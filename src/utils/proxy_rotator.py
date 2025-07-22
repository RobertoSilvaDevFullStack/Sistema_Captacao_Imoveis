# src/utils/proxy_rotator.py
"""
Sistema de rotação de proxies para evitar detecção e bloqueios
"""
import random
import time
import requests
import threading
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Configurar logging
logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Informações de um proxy"""
    ip: str
    port: int
    protocol: str = 'http'
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    is_working: bool = True
    last_tested: Optional[datetime] = None
    response_time: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    
    @property
    def proxy_url(self) -> str:
        """Retorna URL do proxy formatada"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"{self.protocol}://{self.ip}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso do proxy"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total
    
    @property
    def reliability_score(self) -> float:
        """Score de confiabilidade baseado em múltiplos fatores"""
        # Score base na taxa de sucesso
        base_score = self.success_rate
        
        # Penalizar tempo de resposta alto
        time_penalty = min(self.response_time / 10.0, 0.5)  # Max 50% penalty
        
        # Bonificar uso recente (proxy testado recentemente)
        if self.last_tested:
            hours_since_test = (datetime.now() - self.last_tested).total_seconds() / 3600
            freshness_bonus = max(0, (24 - hours_since_test) / 24 * 0.2)  # Max 20% bonus
        else:
            freshness_bonus = 0
            
        return max(0, base_score - time_penalty + freshness_bonus)

class ProxyValidator:
    """Validador de proxies"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.test_urls = [
            'http://httpbin.org/ip',
            'https://api.ipify.org?format=json',
            'http://icanhazip.com',
            'https://httpbin.org/headers'
        ]
    
    def validate_proxy(self, proxy: ProxyInfo) -> Tuple[bool, float]:
        """
        Valida um proxy testando conectividade e velocidade
        
        Returns:
            Tuple[bool, float]: (is_working, response_time)
        """
        start_time = time.time()
        
        proxies = {
            'http': proxy.proxy_url,
            'https': proxy.proxy_url
        }
        
        try:
            # Testar com URL aleatória
            test_url = random.choice(self.test_urls)
            
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            
            response_time = time.time() - start_time
            
            # Verificar se a resposta é válida
            if response.status_code == 200:
                # Verificar se realmente está usando o proxy
                if 'ipify' in test_url or 'icanhazip' in test_url:
                    returned_ip = response.text.strip().replace('"', '')
                    if returned_ip != proxy.ip:
                        logger.warning(f"Proxy {proxy.ip} retornou IP diferente: {returned_ip}")
                
                return True, response_time
            else:
                return False, response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            logger.debug(f"Proxy {proxy.ip}:{proxy.port} falhou: {str(e)}")
            return False, response_time
    
    def validate_proxy_list(self, proxies: List[ProxyInfo], max_workers: int = 10) -> List[ProxyInfo]:
        """
        Valida lista de proxies em paralelo
        
        Returns:
            List[ProxyInfo]: Lista de proxies atualizados com status de validação
        """
        logger.info(f"Validando {len(proxies)} proxies...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter tarefas de validação
            future_to_proxy = {
                executor.submit(self.validate_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            # Coletar resultados
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_working, response_time = future.result()
                    
                    # Atualizar informações do proxy
                    proxy.is_working = is_working
                    proxy.response_time = response_time
                    proxy.last_tested = datetime.now()
                    
                    if is_working:
                        proxy.success_count += 1
                        logger.debug(f"✓ Proxy {proxy.ip}:{proxy.port} OK ({response_time:.2f}s)")
                    else:
                        proxy.failure_count += 1
                        logger.debug(f"✗ Proxy {proxy.ip}:{proxy.port} falhou")
                        
                except Exception as e:
                    proxy.is_working = False
                    proxy.failure_count += 1
                    logger.error(f"Erro ao validar proxy {proxy.ip}:{proxy.port}: {str(e)}")
        
        working_proxies = [p for p in proxies if p.is_working]
        logger.info(f"Validação concluída: {len(working_proxies)}/{len(proxies)} proxies funcionando")
        
        return proxies

class ProxyRotator:
    """Sistema de rotação inteligente de proxies"""
    
    def __init__(self, revalidation_interval: int = 3600):
        self.proxies: List[ProxyInfo] = []
        self.validator = ProxyValidator()
        self.revalidation_interval = revalidation_interval  # segundos
        self.last_revalidation = None
        self._lock = threading.RLock()
        self._current_index = 0
        
    def add_proxy(self, ip: str, port: int, protocol: str = 'http', 
                  username: Optional[str] = None, password: Optional[str] = None,
                  country: Optional[str] = None) -> None:
        """Adiciona um proxy à lista"""
        proxy = ProxyInfo(
            ip=ip,
            port=port,
            protocol=protocol,
            username=username,
            password=password,
            country=country
        )
        
        with self._lock:
            self.proxies.append(proxy)
            logger.info(f"Proxy adicionado: {proxy.ip}:{proxy.port}")
    
    def load_proxies_from_list(self, proxy_list: List[Dict]) -> None:
        """
        Carrega proxies de uma lista de dicionários
        
        Formato esperado:
        [
            {"ip": "1.2.3.4", "port": 8080, "protocol": "http"},
            {"ip": "5.6.7.8", "port": 3128, "username": "user", "password": "pass"}
        ]
        """
        for proxy_data in proxy_list:
            self.add_proxy(**proxy_data)
    
    def load_free_proxies(self) -> None:
        """Carrega lista de proxies gratuitos (para demonstração)"""
        # ATENÇÃO: Proxies gratuitos são instáveis e podem não funcionar
        # Para produção, use proxies pagos e confiáveis
        free_proxies = [
            {"ip": "8.210.83.33", "port": 80},
            {"ip": "47.74.152.29", "port": 8888},
            {"ip": "103.149.162.194", "port": 80},
            {"ip": "202.131.159.230", "port": 80},
            {"ip": "103.167.134.31", "port": 80},
            {"ip": "185.32.6.129", "port": 8090},
            {"ip": "154.236.168.179", "port": 1976},
            {"ip": "185.32.6.131", "port": 8090},
            {"ip": "103.149.162.195", "port": 80},
            {"ip": "154.236.168.181", "port": 1976}
        ]
        
        logger.warning("Carregando proxies gratuitos - use apenas para testes!")
        self.load_proxies_from_list(free_proxies)
    
    def validate_all_proxies(self, force: bool = False) -> None:
        """Valida todos os proxies"""
        with self._lock:
            if not force and self.last_revalidation:
                time_since_last = (datetime.now() - self.last_revalidation).total_seconds()
                if time_since_last < self.revalidation_interval:
                    logger.debug("Proxies validados recentemente, pulando revalidação")
                    return
            
            if self.proxies:
                self.proxies = self.validator.validate_proxy_list(self.proxies)
                self.last_revalidation = datetime.now()
    
    def get_working_proxies(self) -> List[ProxyInfo]:
        """Retorna lista de proxies funcionando"""
        with self._lock:
            return [p for p in self.proxies if p.is_working]
    
    def get_best_proxy(self) -> Optional[ProxyInfo]:
        """Retorna o melhor proxy baseado no score de confiabilidade"""
        working_proxies = self.get_working_proxies()
        
        if not working_proxies:
            return None
            
        # Ordenar por score de confiabilidade
        best_proxy = max(working_proxies, key=lambda p: p.reliability_score)
        
        # Atualizar tempo de último uso
        best_proxy.last_used = datetime.now()
        
        return best_proxy
    
    def get_random_proxy(self) -> Optional[ProxyInfo]:
        """Retorna um proxy aleatório dos que estão funcionando"""
        working_proxies = self.get_working_proxies()
        
        if not working_proxies:
            return None
            
        proxy = random.choice(working_proxies)
        proxy.last_used = datetime.now()
        
        return proxy
    
    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """Retorna próximo proxy na rotação (round-robin)"""
        working_proxies = self.get_working_proxies()
        
        if not working_proxies:
            return None
        
        with self._lock:
            proxy = working_proxies[self._current_index % len(working_proxies)]
            self._current_index += 1
            proxy.last_used = datetime.now()
            
        return proxy
    
    def mark_proxy_failed(self, proxy: ProxyInfo) -> None:
        """Marca um proxy como com falha"""
        with self._lock:
            proxy.failure_count += 1
            # Se falhar muito, marcar como não funcionando
            if proxy.failure_count > 5:
                proxy.is_working = False
                logger.warning(f"Proxy {proxy.ip}:{proxy.port} marcado como não funcionando")
    
    def mark_proxy_success(self, proxy: ProxyInfo) -> None:
        """Marca um proxy como bem-sucedido"""
        with self._lock:
            proxy.success_count += 1
            proxy.is_working = True  # Reativar se estava marcado como falho
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas dos proxies"""
        with self._lock:
            total_proxies = len(self.proxies)
            working_proxies = len(self.get_working_proxies())
            
            if working_proxies > 0:
                avg_response_time = sum(p.response_time for p in self.get_working_proxies()) / working_proxies
                avg_success_rate = sum(p.success_rate for p in self.get_working_proxies()) / working_proxies
            else:
                avg_response_time = 0
                avg_success_rate = 0
            
            return {
                'total_proxies': total_proxies,
                'working_proxies': working_proxies,
                'success_rate': working_proxies / total_proxies if total_proxies > 0 else 0,
                'avg_response_time': avg_response_time,
                'avg_success_rate': avg_success_rate,
                'last_revalidation': self.last_revalidation.isoformat() if self.last_revalidation else None
            }

class ProxyManager:
    """Gerenciador principal do sistema de proxies"""
    
    def __init__(self, rotation_strategy: str = 'best'):
        """
        Args:
            rotation_strategy: 'best', 'random', 'round_robin'
        """
        self.rotator = ProxyRotator()
        self.rotation_strategy = rotation_strategy
        self.selenium_proxy_config = None
        
    def setup_proxies(self, proxy_list: Optional[List[Dict]] = None, 
                     use_free_proxies: bool = False) -> None:
        """Configura proxies no sistema"""
        if proxy_list:
            self.rotator.load_proxies_from_list(proxy_list)
        elif use_free_proxies:
            self.rotator.load_free_proxies()
        else:
            logger.warning("Nenhum proxy configurado!")
            return
        
        # Validar proxies após carregar
        self.rotator.validate_all_proxies()
        
        stats = self.rotator.get_statistics()
        logger.info(f"Sistema de proxies configurado: {stats['working_proxies']}/{stats['total_proxies']} proxies funcionando")
    
    def get_proxy_for_request(self) -> Optional[ProxyInfo]:
        """Retorna proxy baseado na estratégia configurada"""
        # Revalidar proxies se necessário
        self.rotator.validate_all_proxies()
        
        if self.rotation_strategy == 'best':
            return self.rotator.get_best_proxy()
        elif self.rotation_strategy == 'random':
            return self.rotator.get_random_proxy()
        elif self.rotation_strategy == 'round_robin':
            return self.rotator.get_next_proxy()
        else:
            return self.rotator.get_best_proxy()
    
    def get_selenium_proxy_config(self) -> Optional[Dict]:
        """Retorna configuração de proxy para Selenium"""
        proxy = self.get_proxy_for_request()
        
        if not proxy:
            return None
        
        config = {
            'proxyType': 'MANUAL',
            'httpProxy': f"{proxy.ip}:{proxy.port}",
            'sslProxy': f"{proxy.ip}:{proxy.port}",
            'noProxy': ''
        }
        
        # Se tem autenticação, precisará de extensão do Chrome
        if proxy.username and proxy.password:
            config['proxy_auth'] = {
                'username': proxy.username,
                'password': proxy.password
            }
        
        self.selenium_proxy_config = config
        return config
    
    def create_proxy_extension(self, proxy: ProxyInfo) -> Optional[str]:
        """
        Cria extensão Chrome para proxy com autenticação
        Retorna caminho para o arquivo .zip da extensão
        """
        if not (proxy.username and proxy.password):
            return None
        
        import zipfile
        import tempfile
        import os
        
        # Código da extensão proxy
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Proxy Auth Extension",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {"scripts": ["background.js"]},
        }
        
        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "{proxy.protocol}",
                    host: "{proxy.ip}",
                    port: {proxy.port}
                }}
            }}
        }};
        
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
        
        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy.username}",
                    password: "{proxy.password}"
                }}
            }};
        }}
        
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.zip', delete=False) as temp_file:
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                zf.writestr('manifest.json', str(manifest).replace("'", '"'))
                zf.writestr('background.js', background_js)
            
            return temp_file.name
    
    def report_proxy_result(self, proxy: ProxyInfo, success: bool) -> None:
        """Reporta resultado de uso do proxy"""
        if success:
            self.rotator.mark_proxy_success(proxy)
        else:
            self.rotator.mark_proxy_failed(proxy)
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do sistema de proxies"""
        return self.rotator.get_statistics()

# Instância global
proxy_manager = ProxyManager()
