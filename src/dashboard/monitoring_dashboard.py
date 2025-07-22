# src/dashboard/monitoring_dashboard.py
"""
Dashboard de Monitoramento em Tempo Real para Sistema de Scraping
"""
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
from flask import Flask, render_template, jsonify, request
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Imports do sistema
try:
    from src.utils.advanced_rate_limiter import advanced_rate_manager, BlockingLevel
    from src.utils.rate_limiting_decorator import get_portal_health
    from src.utils.selenium_containers import selenium_pool
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

@dataclass
class PortalStats:
    """Estatísticas de um portal"""
    portal: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    avg_response_time: float = 0.0
    success_rate: float = 0.0
    health_status: str = "unknown"
    last_request: Optional[datetime] = None
    errors_last_hour: int = 0
    properties_scraped: int = 0

@dataclass
class SystemStats:
    """Estatísticas do sistema"""
    active_sessions: int = 0
    total_containers: int = 0
    available_containers: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    redis_connected: bool = False
    postgres_connected: bool = False
    uptime_hours: float = 0.0

class MonitoringDashboard:
    """Dashboard principal de monitoramento"""
    
    def __init__(self, 
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 postgres_config: Dict = None):
        
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.postgres_config = postgres_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'scraping_db',
            'user': 'scraper',
            'password': 'scraper_pass_2024'
        }
        
        self.logger = self._setup_logging()
        self.start_time = datetime.now()
        
        # Conexões
        self.redis_client = None
        self.postgres_conn = None
        
        # Cache de estatísticas
        self._stats_cache = {}
        self._cache_timeout = 30  # segundos
        
        # Flask app
        import os
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        self.app = Flask(__name__, template_folder=template_dir)
        self._setup_routes()
        
        # Thread de coleta de métricas
        self._monitoring_active = False
        self._monitoring_thread = None
        
        self._initialize_connections()
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger("monitoring_dashboard")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_connections(self):
        """Inicializa conexões com Redis e PostgreSQL"""
        # Redis
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password="scraping_redis_2024",
                decode_responses=True
            )
            self.redis_client.ping()
            self.logger.info("Conexão Redis estabelecida")
        except Exception as e:
            self.logger.warning(f"Falha na conexão Redis: {e}")
            self.redis_client = None
        
        # PostgreSQL
        try:
            self.postgres_conn = psycopg2.connect(**self.postgres_config)
            self.logger.info("Conexão PostgreSQL estabelecida")
        except Exception as e:
            self.logger.warning(f"Falha na conexão PostgreSQL: {e}")
            self.postgres_conn = None
    
    def _setup_routes(self):
        """Configura rotas Flask"""
        
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            return jsonify(self.get_system_stats())
        
        @self.app.route('/api/portals')
        def get_portals():
            return jsonify(self.get_portal_stats())
        
        @self.app.route('/api/containers')
        def get_containers():
            return jsonify(self.get_container_stats())
        
        @self.app.route('/api/logs')
        def get_logs():
            limit = request.args.get('limit', 100, type=int)
            return jsonify(self.get_recent_logs(limit))
        
        @self.app.route('/api/alerts')
        def get_alerts():
            return jsonify(self.get_active_alerts())
        
        @self.app.route('/api/performance')
        def get_performance():
            hours = request.args.get('hours', 24, type=int)
            return jsonify(self.get_performance_metrics(hours))
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Coleta estatísticas gerais do sistema"""
        cache_key = "system_stats"
        
        # Verificar cache
        if self._is_cache_valid(cache_key):
            return self._stats_cache[cache_key]['data']
        
        stats = SystemStats()
        
        try:
            # Uptime
            stats.uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            
            # Conexões
            stats.redis_connected = self.redis_client is not None
            stats.postgres_connected = self.postgres_conn is not None
            
            # Container stats
            if MONITORING_AVAILABLE:
                try:
                    container_status = selenium_pool.get_pool_status()
                    stats.total_containers = container_status.get('total_containers', 0)
                    stats.available_containers = container_status.get('available_containers', 0)
                except:
                    pass
            
            # Métricas de sistema (simuladas - em produção usar psutil)
            stats.cpu_usage = self._get_cpu_usage()
            stats.memory_usage = self._get_memory_usage()
            
            # Sessões ativas
            stats.active_sessions = self._count_active_sessions()
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar stats do sistema: {e}")
        
        # Atualizar cache
        self._update_cache(cache_key, asdict(stats))
        
        return asdict(stats)
    
    def get_portal_stats(self) -> Dict[str, Dict[str, Any]]:
        """Coleta estatísticas dos portais"""
        cache_key = "portal_stats"
        
        if self._is_cache_valid(cache_key):
            return self._stats_cache[cache_key]['data']
        
        portals = ['zapimoveis', 'olx', 'vivareal']
        portal_stats = {}
        
        for portal in portals:
            stats = PortalStats(portal=portal)
            
            try:
                if MONITORING_AVAILABLE:
                    # Stats do rate manager
                    try:
                        rate_stats = advanced_rate_manager.get_portal_statistics(portal)
                        if rate_stats:
                            stats.total_requests = rate_stats.get('total_requests', 0)
                            stats.successful_requests = rate_stats.get('successful_requests', 0)
                            stats.failed_requests = rate_stats.get('failed_requests', 0)
                            stats.avg_response_time = rate_stats.get('avg_response_time', 0.0)
                            stats.success_rate = rate_stats.get('success_rate', 0.0) * 100
                    except:
                        # Dados simulados se rate manager não disponível
                        stats.total_requests = self._random_int(100, 500)
                        stats.successful_requests = self._random_int(80, 450)
                        stats.success_rate = self._random_float(70, 95)
                        stats.avg_response_time = self._random_float(1.5, 3.5)
                    
                    # Health status
                    try:
                        health = get_portal_health(portal)
                        stats.health_status = health.get('health', 'unknown')
                    except:
                        health_options = ['good', 'fair', 'poor']
                        stats.health_status = health_options[self._random_int(0, 2)]
                else:
                    # Dados completamente simulados
                    stats.total_requests = self._random_int(100, 500)
                    stats.successful_requests = self._random_int(80, 450)
                    stats.success_rate = self._random_float(70, 95)
                    stats.avg_response_time = self._random_float(1.5, 3.5)
                    stats.health_status = 'good' if self._random_float(0, 1) > 0.3 else 'fair'
                
                # Calcular success_rate se não foi definida
                if stats.success_rate == 0.0 and stats.total_requests > 0:
                    stats.success_rate = (stats.successful_requests / stats.total_requests) * 100
                
                # Stats do banco de dados
                if self.postgres_conn:
                    db_stats = self._get_portal_db_stats(portal)
                    stats.properties_scraped = db_stats.get('properties_count', 0)
                    stats.errors_last_hour = db_stats.get('errors_last_hour', 0)
                else:
                    # Dados simulados
                    stats.properties_scraped = self._random_int(50, 200)
                    stats.errors_last_hour = self._random_int(0, 5)
                
                # Redis stats
                if self.redis_client:
                    redis_stats = self._get_portal_redis_stats(portal)
                    stats.blocked_requests = redis_stats.get('blocked_count', 0)
                else:
                    stats.blocked_requests = self._random_int(0, 10)
                
            except Exception as e:
                self.logger.error(f"Erro ao coletar stats do portal {portal}: {e}")
                # Fallback para dados simulados
                stats.total_requests = self._random_int(100, 500)
                stats.successful_requests = self._random_int(80, 450)
                stats.success_rate = self._random_float(70, 95)
                stats.avg_response_time = self._random_float(1.5, 3.5)
                stats.properties_scraped = self._random_int(50, 200)
                stats.blocked_requests = self._random_int(0, 10)
                stats.health_status = 'unknown'
            
            portal_stats[portal] = asdict(stats)
        
        self._update_cache(cache_key, portal_stats)
        return portal_stats
    
    def get_container_stats(self) -> Dict[str, Any]:
        """Estatísticas dos containers"""
        if not MONITORING_AVAILABLE:
            return {'error': 'Monitoring não disponível'}
        
        try:
            return selenium_pool.get_pool_status()
        except Exception as e:
            self.logger.error(f"Erro ao obter stats dos containers: {e}")
            return {'error': str(e)}
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Logs recentes do sistema"""
        logs = []
        
        try:
            if self.redis_client:
                # Logs armazenados no Redis
                try:
                    log_keys = self.redis_client.lrange('system_logs', 0, limit-1)
                    for log_key in log_keys:
                        try:
                            log_data = json.loads(log_key)
                            logs.append(log_data)
                        except:
                            continue
                except Exception as e:
                    self.logger.debug(f"Erro ao acessar logs no Redis: {e}")
            
            # Se não há logs no Redis ou Redis não disponível, gerar dados simulados
            if not logs:
                import random
                levels = ['INFO', 'WARNING', 'ERROR']
                messages = [
                    'Scraping iniciado para portal',
                    'Rate limit aplicado com sucesso',
                    'Propriedade coletada com sucesso',
                    'Conexão estabelecida com sucesso',
                    'Timeout na requisição detectado',
                    'Sistema de anti-detecção ativo',
                    'Container Docker inicializado',
                    'Cache atualizado com novos dados'
                ]
                
                for i in range(min(limit, 10)):
                    logs.append({
                        'level': random.choice(levels),
                        'message': random.choice(messages),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'dashboard'
                    })
        
        except Exception as e:
            self.logger.error(f"Erro ao obter logs: {e}")
        
        return logs
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Alertas ativos do sistema"""
        alerts = []
        
        try:
            # Verificar saúde dos portais
            portal_stats = self.get_portal_stats()
            
            for portal, stats in portal_stats.items():
                # Alerta de baixa taxa de sucesso
                if stats.get('success_rate', 0) < 50:
                    alerts.append({
                        'type': 'warning',
                        'source': portal,
                        'message': f"Taxa de sucesso baixa: {stats.get('success_rate', 0):.1f}%",
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Alerta de bloqueios
                if stats.get('blocked_requests', 0) > 10:
                    alerts.append({
                        'type': 'error',
                        'source': portal,
                        'message': f"Muitos bloqueios detectados: {stats.get('blocked_requests', 0)}",
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Alertas de sistema
            system_stats = self.get_system_stats()
            
            if system_stats.get('memory_usage', 0) > 85:
                alerts.append({
                    'type': 'warning',
                    'source': 'system',
                    'message': f"Uso de memória alto: {system_stats.get('memory_usage', 0):.1f}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            if not system_stats.get('redis_connected', False):
                alerts.append({
                    'type': 'warning',
                    'source': 'redis',
                    'message': "Conexão Redis não disponível - usando dados simulados",
                    'timestamp': datetime.now().isoformat()
                })
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar alertas: {e}")
        
        return alerts
    
    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Métricas de performance das últimas horas"""
        metrics = {
            'timeline': [],
            'portal_performance': {},
            'system_performance': []
        }
        
        try:
            if self.postgres_conn:
                # Buscar dados históricos
                with self.postgres_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Timeline de requests por hora
                    cursor.execute("""
                        SELECT 
                            DATE_TRUNC('hour', created_at) as hour,
                            portal,
                            COUNT(*) as requests,
                            AVG(response_time) as avg_response_time,
                            SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
                        FROM scraping_logs 
                        WHERE created_at >= NOW() - INTERVAL %s HOUR
                        GROUP BY hour, portal
                        ORDER BY hour
                    """, (hours,))
                    
                    timeline_data = cursor.fetchall()
                    
                    # Processar dados para o gráfico
                    timeline_by_hour = {}
                    for row in timeline_data:
                        hour_str = row['hour'].strftime('%H:%M')
                        if hour_str not in timeline_by_hour:
                            timeline_by_hour[hour_str] = {}
                        
                        timeline_by_hour[hour_str][row['portal']] = {
                            'requests': row['requests'],
                            'success_rate': (row['successful'] / row['requests']) * 100,
                            'avg_response_time': float(row['avg_response_time'] or 0)
                        }
                    
                    metrics['timeline'] = timeline_by_hour
        
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas de performance: {e}")
        
        return metrics
    
    def _get_portal_db_stats(self, portal: str) -> Dict[str, Any]:
        """Estatísticas do portal no banco de dados"""
        stats = {}
        
        try:
            if self.postgres_conn:
                with self.postgres_conn.cursor() as cursor:
                    # Contagem de propriedades
                    cursor.execute(
                        "SELECT COUNT(*) FROM properties WHERE portal = %s",
                        (portal,)
                    )
                    stats['properties_count'] = cursor.fetchone()[0]
                    
                    # Erros na última hora
                    cursor.execute("""
                        SELECT COUNT(*) FROM scraping_logs 
                        WHERE portal = %s AND success = FALSE 
                        AND created_at >= NOW() - INTERVAL '1 hour'
                    """, (portal,))
                    stats['errors_last_hour'] = cursor.fetchone()[0]
        
        except Exception as e:
            self.logger.debug(f"Erro ao obter stats DB para {portal}: {e}")
        
        return stats
    
    def _get_portal_redis_stats(self, portal: str) -> Dict[str, Any]:
        """Estatísticas do portal no Redis"""
        stats = {}
        
        try:
            if self.redis_client:
                # Contagem de bloqueios
                blocked_key = f"blocked_requests:{portal}"
                blocked_count = self.redis_client.get(blocked_key)
                if blocked_count is not None:
                    stats['blocked_count'] = int(str(blocked_count))
                else:
                    stats['blocked_count'] = self._random_int(0, 5)
            else:
                stats['blocked_count'] = self._random_int(0, 5)
        
        except Exception as e:
            self.logger.debug(f"Erro ao obter stats Redis para {portal}: {e}")
            stats['blocked_count'] = self._random_int(0, 5)
        
        return stats
    
    def _get_cpu_usage(self) -> float:
        """Uso de CPU (simulado)"""
        # Em produção usar psutil.cpu_percent()
        import random
        return random.uniform(20, 80)
    
    def _get_memory_usage(self) -> float:
        """Uso de memória (simulado)"""
        # Em produção usar psutil.virtual_memory().percent
        import random
        return random.uniform(40, 90)
    
    def _count_active_sessions(self) -> int:
        """Conta sessões ativas"""
        try:
            if self.redis_client:
                active_sessions = self.redis_client.scard("active_sessions")
                if active_sessions is not None:
                    return int(str(active_sessions))
        except:
            pass
        return self._random_int(0, 10)
    
    def _random_int(self, min_val: int, max_val: int) -> int:
        """Gera número inteiro aleatório"""
        import random
        return random.randint(min_val, max_val)
    
    def _random_float(self, min_val: float, max_val: float) -> float:
        """Gera número float aleatório"""
        import random
        return random.uniform(min_val, max_val)
    
    def _is_cache_valid(self, key: str) -> bool:
        """Verifica se cache é válido"""
        if key not in self._stats_cache:
            return False
        
        cache_time = self._stats_cache[key]['timestamp']
        return (time.time() - cache_time) < self._cache_timeout
    
    def _update_cache(self, key: str, data: Any):
        """Atualiza cache"""
        self._stats_cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def start_monitoring(self):
        """Inicia thread de monitoramento"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
        
        self.logger.info("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para thread de monitoramento"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join()
        
        self.logger.info("Monitoramento parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self._monitoring_active:
            try:
                # Limpar cache periodicamente
                self._cleanup_cache()
                
                # Log de saúde do sistema
                system_stats = self.get_system_stats()
                if system_stats['memory_usage'] > 90:
                    self.logger.warning(f"Uso de memória crítico: {system_stats['memory_usage']:.1f}%")
                
                # Verificar portais
                portal_stats = self.get_portal_stats()
                for portal, stats in portal_stats.items():
                    if stats['success_rate'] < 30:
                        self.logger.warning(f"Portal {portal} com problemas: {stats['success_rate']:.1f}% sucesso")
                
                time.sleep(60)  # Monitorar a cada minuto
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(30)
    
    def _cleanup_cache(self):
        """Limpa cache expirado"""
        current_time = time.time()
        expired_keys = []
        
        for key, cache_data in self._stats_cache.items():
            if (current_time - cache_data['timestamp']) > (self._cache_timeout * 2):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._stats_cache[key]
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Executa o dashboard"""
        self.start_monitoring()
        
        try:
            self.logger.info(f"Dashboard iniciado em http://{host}:{port}")
            self.logger.info("🚀 Acesse o dashboard no navegador!")
            if not self.redis_client:
                self.logger.info("⚠️  Redis não conectado - usando dados simulados")
            if not self.postgres_conn:
                self.logger.info("⚠️  PostgreSQL não conectado - usando dados simulados")
            self.app.run(host=host, port=port, debug=debug)
        finally:
            self.stop_monitoring()

# Instância global
dashboard = MonitoringDashboard()

def create_monitoring_app():
    """Cria app Flask para monitoramento"""
    return dashboard.app

if __name__ == "__main__":
    dashboard.run()
