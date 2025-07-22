# src/utils/selenium_containers.py
"""
Sistema de Selenium com Docker para paralelização e isolamento
"""
import os
import json
import time
import logging
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import docker
from docker.errors import DockerException

@dataclass
class ContainerConfig:
    """Configuração do container Selenium"""
    image: str = "selenium/standalone-chrome:latest"
    shm_size: str = "2g"
    memory_limit: str = "1g"
    cpu_limit: float = 1.0
    ports: Dict[str, int] = None
    environment: Dict[str, str] = None
    volumes: Dict[str, str] = None
    network_mode: str = "bridge"

class SeleniumContainer:
    """Wrapper para container Selenium individual"""
    
    def __init__(self, container_id: str, config: ContainerConfig):
        self.container_id = container_id
        self.config = config
        self.container = None
        self.selenium_url = None
        self.logger = logging.getLogger(__name__)
        
        try:
            self.docker_client = docker.from_env()
        except DockerException as e:
            self.logger.error(f"Erro ao conectar com Docker: {e}")
            raise
    
    def start(self) -> bool:
        """Inicia o container"""
        try:
            # Configurar portas
            port_bindings = {}
            if self.config.ports:
                for container_port, host_port in self.config.ports.items():
                    port_bindings[container_port] = host_port
            else:
                # Porta padrão do Selenium
                port_bindings['4444/tcp'] = None  # Docker escolhe porta automaticamente
            
            # Configurar volumes
            volumes = self.config.volumes or {}
            
            # Configurar variáveis de ambiente
            environment = self.config.environment or {}
            environment.update({
                'SE_SCREEN_WIDTH': '1920',
                'SE_SCREEN_HEIGHT': '1080',
                'SE_SCREEN_DEPTH': '24',
                'SE_START_XVFB': 'true'
            })
            
            # Criar container
            self.container = self.docker_client.containers.run(
                image=self.config.image,
                name=f"selenium-{self.container_id}",
                ports=port_bindings,
                environment=environment,
                volumes=volumes,
                shm_size=self.config.shm_size,
                mem_limit=self.config.memory_limit,
                cpu_count=self.config.cpu_limit,
                network_mode=self.config.network_mode,
                detach=True,
                remove=True  # Remove automaticamente quando parar
            )
            
            # Aguardar container estar pronto
            if self._wait_for_ready():
                # Descobrir porta atribuída
                self._discover_selenium_url()
                self.logger.info(f"Container {self.container_id} iniciado: {self.selenium_url}")
                return True
            else:
                self.logger.error(f"Container {self.container_id} não ficou pronto")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao iniciar container {self.container_id}: {e}")
            return False
    
    def stop(self):
        """Para o container"""
        try:
            if self.container:
                self.container.stop()
                self.logger.info(f"Container {self.container_id} parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar container {self.container_id}: {e}")
    
    def _wait_for_ready(self, timeout: int = 60) -> bool:
        """Aguarda container estar pronto para receber conexões"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # Verificar se container está rodando
                self.container.reload()
                if self.container.status != 'running':
                    time.sleep(1)
                    continue
                
                # Verificar logs para indicação de prontidão
                logs = self.container.logs().decode('utf-8')
                if 'Selenium Grid ready' in logs or 'Started Selenium Standalone' in logs:
                    return True
                    
                time.sleep(2)
                
            except Exception as e:
                self.logger.debug(f"Aguardando container {self.container_id}: {e}")
                time.sleep(2)
        
        return False
    
    def _discover_selenium_url(self):
        """Descobre a URL do Selenium no container"""
        try:
            self.container.reload()
            port_info = self.container.attrs['NetworkSettings']['Ports']
            
            # Procurar porta 4444 (Selenium)
            if '4444/tcp' in port_info and port_info['4444/tcp']:
                host_port = port_info['4444/tcp'][0]['HostPort']
                self.selenium_url = f"http://localhost:{host_port}/wd/hub"
            else:
                # Fallback para IP do container
                ip_address = self.container.attrs['NetworkSettings']['IPAddress']
                self.selenium_url = f"http://{ip_address}:4444/wd/hub"
                
        except Exception as e:
            self.logger.error(f"Erro ao descobrir URL do Selenium: {e}")
            self.selenium_url = None
    
    def get_selenium_url(self) -> Optional[str]:
        """Retorna URL do Selenium"""
        return self.selenium_url
    
    def is_healthy(self) -> bool:
        """Verifica se container está saudável"""
        try:
            if not self.container:
                return False
                
            self.container.reload()
            return self.container.status == 'running'
            
        except Exception:
            return False

class SeleniumContainerPool:
    """Pool de containers Selenium para paralelização"""
    
    def __init__(self, pool_size: int = 3):
        self.pool_size = pool_size
        self.containers: List[SeleniumContainer] = []
        self.available_containers: List[SeleniumContainer] = []
        self.busy_containers: List[SeleniumContainer] = []
        self.logger = logging.getLogger(__name__)
        
        # Verificar se Docker está disponível
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
        except DockerException as e:
            self.logger.error(f"Docker não está disponível: {e}")
            raise
    
    def start_pool(self, configs: List[ContainerConfig] = None) -> bool:
        """Inicia pool de containers"""
        if configs is None:
            configs = self._get_default_configs()
        
        self.logger.info(f"Iniciando pool com {self.pool_size} containers...")
        
        # Criar containers
        for i in range(self.pool_size):
            config = configs[i % len(configs)]  # Rotacionar configurações
            container = SeleniumContainer(f"pool-{i}", config)
            self.containers.append(container)
        
        # Iniciar containers em paralelo
        with ThreadPoolExecutor(max_workers=self.pool_size) as executor:
            futures = {executor.submit(container.start): container 
                      for container in self.containers}
            
            for future in as_completed(futures):
                container = futures[future]
                try:
                    success = future.result()
                    if success:
                        self.available_containers.append(container)
                        self.logger.info(f"Container {container.container_id} pronto")
                    else:
                        self.logger.error(f"Falha ao iniciar {container.container_id}")
                except Exception as e:
                    self.logger.error(f"Erro no container {container.container_id}: {e}")
        
        ready_count = len(self.available_containers)
        self.logger.info(f"Pool iniciado: {ready_count}/{self.pool_size} containers prontos")
        
        return ready_count > 0
    
    def get_container(self, timeout: int = 30) -> Optional[SeleniumContainer]:
        """Obtém container disponível do pool"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            if self.available_containers:
                container = self.available_containers.pop(0)
                
                # Verificar se ainda está saudável
                if container.is_healthy():
                    self.busy_containers.append(container)
                    return container
                else:
                    # Container não está saudável, tentar reiniciar
                    self.logger.warning(f"Container {container.container_id} não está saudável")
                    self._restart_container(container)
            
            time.sleep(1)
        
        self.logger.warning("Timeout ao aguardar container disponível")
        return None
    
    def release_container(self, container: SeleniumContainer):
        """Libera container de volta para o pool"""
        if container in self.busy_containers:
            self.busy_containers.remove(container)
            
            # Verificar se ainda está saudável
            if container.is_healthy():
                self.available_containers.append(container)
            else:
                # Reiniciar container problemático
                self._restart_container(container)
    
    def _restart_container(self, container: SeleniumContainer):
        """Reinicia container problemático"""
        try:
            self.logger.info(f"Reiniciando container {container.container_id}")
            container.stop()
            time.sleep(2)
            
            if container.start():
                self.available_containers.append(container)
                self.logger.info(f"Container {container.container_id} reiniciado com sucesso")
            else:
                self.logger.error(f"Falha ao reiniciar container {container.container_id}")
                
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar container: {e}")
    
    def stop_pool(self):
        """Para todos os containers do pool"""
        self.logger.info("Parando pool de containers...")
        
        all_containers = self.available_containers + self.busy_containers
        
        with ThreadPoolExecutor(max_workers=self.pool_size) as executor:
            futures = [executor.submit(container.stop) for container in all_containers]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Erro ao parar container: {e}")
        
        self.containers.clear()
        self.available_containers.clear()
        self.busy_containers.clear()
        
        self.logger.info("Pool de containers parado")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Retorna status do pool"""
        return {
            'total_containers': len(self.containers),
            'available_containers': len(self.available_containers),
            'busy_containers': len(self.busy_containers),
            'healthy_containers': sum(1 for c in self.containers if c.is_healthy()),
            'container_urls': [c.get_selenium_url() for c in self.containers if c.get_selenium_url()]
        }
    
    def _get_default_configs(self) -> List[ContainerConfig]:
        """Configurações padrão para containers"""
        return [
            ContainerConfig(
                image="selenium/standalone-chrome:latest",
                memory_limit="1g",
                environment={
                    'SE_SCREEN_WIDTH': '1366',
                    'SE_SCREEN_HEIGHT': '768'
                }
            ),
            ContainerConfig(
                image="selenium/standalone-chrome:latest",
                memory_limit="1g",
                environment={
                    'SE_SCREEN_WIDTH': '1920',
                    'SE_SCREEN_HEIGHT': '1080'
                }
            ),
            ContainerConfig(
                image="selenium/standalone-firefox:latest",
                memory_limit="1g",
                environment={
                    'SE_SCREEN_WIDTH': '1440',
                    'SE_SCREEN_HEIGHT': '900'
                }
            )
        ]

class ContainerizedSeleniumTask:
    """Wrapper para executar tarefas Selenium em containers"""
    
    def __init__(self, pool: SeleniumContainerPool):
        self.pool = pool
        self.logger = logging.getLogger(__name__)
    
    def execute_task(self, task_func, *args, **kwargs):
        """Executa tarefa usando container do pool"""
        container = None
        
        try:
            # Obter container
            container = self.pool.get_container()
            if not container:
                raise RuntimeError("Nenhum container disponível")
            
            # Executar tarefa
            selenium_url = container.get_selenium_url()
            result = task_func(selenium_url, *args, **kwargs)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na execução da tarefa: {e}")
            raise
            
        finally:
            # Liberar container
            if container:
                self.pool.release_container(container)

# Instância global do pool
selenium_pool = SeleniumContainerPool()

def execute_parallel_selenium_tasks(tasks: List[Dict], pool_size: int = 3) -> List[Any]:
    """
    Executa tarefas Selenium em paralelo usando containers
    
    Args:
        tasks: Lista de dicionários com 'func' e 'args'
        pool_size: Tamanho do pool de containers
    
    Returns:
        Lista com resultados das tarefas
    """
    logger = logging.getLogger(__name__)
    
    # Iniciar pool
    pool = SeleniumContainerPool(pool_size)
    if not pool.start_pool():
        raise RuntimeError("Falha ao iniciar pool de containers")
    
    try:
        # Executar tarefas em paralelo
        results = []
        
        with ThreadPoolExecutor(max_workers=pool_size) as executor:
            # Criar tasks
            task_wrapper = ContainerizedSeleniumTask(pool)
            futures = []
            
            for task in tasks:
                func = task['func']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})
                
                future = executor.submit(task_wrapper.execute_task, func, *args, **kwargs)
                futures.append(future)
            
            # Coletar resultados
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Erro na tarefa: {e}")
                    results.append(None)
        
        return results
        
    finally:
        # Parar pool
        pool.stop_pool()

def create_docker_compose_config(services: int = 3) -> str:
    """Cria configuração docker-compose para Selenium Grid"""
    
    config = {
        'version': '3.8',
        'services': {
            'selenium-hub': {
                'image': 'selenium/hub:latest',
                'container_name': 'selenium-hub',
                'ports': ['4444:4444'],
                'environment': {
                    'GRID_MAX_SESSION': str(services * 2),
                    'GRID_BROWSER_TIMEOUT': '30',
                    'GRID_TIMEOUT': '30'
                }
            }
        }
    }
    
    # Adicionar nodes Chrome
    for i in range(services):
        service_name = f'chrome-{i+1}'
        config['services'][service_name] = {
            'image': 'selenium/node-chrome:latest',
            'shm_size': '2gb',
            'depends_on': ['selenium-hub'],
            'environment': {
                'HUB_HOST': 'selenium-hub',
                'HUB_PORT': '4444',
                'NODE_MAX_INSTANCES': '2',
                'NODE_MAX_SESSION': '2'
            },
            'volumes': ['/dev/shm:/dev/shm']
        }
    
    return json.dumps(config, indent=2)
