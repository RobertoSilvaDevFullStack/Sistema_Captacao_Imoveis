# src/utils/rate_limiter.py
"""
Sistema de rate limiting inteligente para evitar bloqueios
"""
import time
import random
import threading
from typing import Dict, Optional
from datetime import datetime, timedelta

class SmartRateLimit:
    """Rate limiter inteligente com backoff exponencial"""
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 8.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: Dict[str, float] = {}
        self.failure_count: Dict[str, int] = {}
        self.lock = threading.Lock()
        
    def wait(self, portal: Optional[str] = None) -> None:
        """Aplica delay baseado no portal e histórico de falhas"""
        portal = portal or 'default'
        
        with self.lock:
            current_time = time.time()
            last_time = self.last_request_time.get(portal, 0)
            failures = self.failure_count.get(portal, 0)
            
            # Calcular delay baseado em falhas anteriores
            base_delay = random.uniform(self.min_delay, self.max_delay)
            failure_multiplier = min(2.0 ** failures, 10.0)  # Máximo 10x
            total_delay = base_delay * failure_multiplier
            
            # Garantir que passou tempo suficiente desde a última requisição
            time_since_last = current_time - last_time
            if time_since_last < total_delay:
                sleep_time = total_delay - time_since_last
                time.sleep(sleep_time)
                
            self.last_request_time[portal] = time.time()
    
    def record_success(self, portal: Optional[str] = None) -> None:
        """Registra sucesso e reseta contador de falhas"""
        portal = portal or 'default'
        with self.lock:
            if portal in self.failure_count:
                del self.failure_count[portal]
    
    def record_failure(self, portal: Optional[str] = None) -> None:
        """Registra falha e incrementa contador"""
        portal = portal or 'default'
        with self.lock:
            self.failure_count[portal] = self.failure_count.get(portal, 0) + 1
    
    def exponential_backoff(self, attempt: int, max_delay: float = 300.0) -> None:
        """Aplica backoff exponencial para tentativas de retry"""
        delay = min(max_delay, (2 ** attempt) + random.uniform(0, 1))
        time.sleep(delay)
    
    def get_current_delay(self, portal: Optional[str] = None) -> float:
        """Retorna o delay atual para um portal"""
        portal = portal or 'default'
        failures = self.failure_count.get(portal, 0)
        base_delay = (self.min_delay + self.max_delay) / 2
        return base_delay * min(2.0 ** failures, 10.0)

class PortalRateManager:
    """Gerenciador de rate limiting específico para cada portal"""
    
    def __init__(self):
        self.limiters = {
            'zapimoveis': SmartRateLimit(min_delay=3.0, max_delay=8.0),
            'olx': SmartRateLimit(min_delay=2.0, max_delay=6.0),
            'vivareal': SmartRateLimit(min_delay=4.0, max_delay=10.0),
            'default': SmartRateLimit(min_delay=2.0, max_delay=5.0)
        }
        
        # Configurações específicas por portal
        self.portal_configs = {
            'zapimoveis': {
                'max_requests_per_minute': 15,
                'burst_protection': True,
                'requires_session': True
            },
            'olx': {
                'max_requests_per_minute': 20,
                'burst_protection': True,
                'requires_session': False
            },
            'vivareal': {
                'max_requests_per_minute': 10,
                'burst_protection': True,
                'requires_session': True
            }
        }
        
        self.request_history: Dict[str, list] = {}
        self.lock = threading.Lock()
    
    def wait_for_portal(self, portal: str) -> None:
        """Aplica rate limiting específico para o portal"""
        limiter = self.limiters.get(portal, self.limiters['default'])
        
        # Verificar se estamos fazendo muitas requisições por minuto
        if self._check_rate_limit(portal):
            self._wait_for_rate_window(portal)
        
        # Aplicar delay normal
        limiter.wait(portal)
        
        # Registrar a requisição
        self._record_request(portal)
    
    def _check_rate_limit(self, portal: str) -> bool:
        """Verifica se excedeu o limite de requisições por minuto"""
        config = self.portal_configs.get(portal, {})
        max_requests = config.get('max_requests_per_minute', 30)
        
        with self.lock:
            now = datetime.now()
            history = self.request_history.get(portal, [])
            
            # Filtrar requisições do último minuto
            recent_requests = [
                req_time for req_time in history 
                if now - req_time < timedelta(minutes=1)
            ]
            
            return len(recent_requests) >= max_requests
    
    def _wait_for_rate_window(self, portal: str) -> None:
        """Aguarda até que a janela de rate limiting seja liberada"""
        with self.lock:
            history = self.request_history.get(portal, [])
            if history:
                # Aguardar até que a requisição mais antiga saia da janela de 1 minuto
                oldest_request = min(history)
                wait_until = oldest_request + timedelta(minutes=1, seconds=5)  # 5s de margem
                now = datetime.now()
                
                if wait_until > now:
                    wait_seconds = (wait_until - now).total_seconds()
                    time.sleep(wait_seconds)
    
    def _record_request(self, portal: str) -> None:
        """Registra uma nova requisição no histórico"""
        with self.lock:
            now = datetime.now()
            if portal not in self.request_history:
                self.request_history[portal] = []
            
            self.request_history[portal].append(now)
            
            # Limpar histórico antigo (mais de 2 minutos)
            cutoff = now - timedelta(minutes=2)
            self.request_history[portal] = [
                req_time for req_time in self.request_history[portal]
                if req_time > cutoff
            ]
    
    def record_success(self, portal: str) -> None:
        """Registra sucesso no portal"""
        limiter = self.limiters.get(portal, self.limiters['default'])
        limiter.record_success(portal)
    
    def record_failure(self, portal: str) -> None:
        """Registra falha no portal"""
        limiter = self.limiters.get(portal, self.limiters['default'])
        limiter.record_failure(portal)
    
    def get_portal_status(self, portal: str) -> Dict:
        """Retorna status atual do portal"""
        limiter = self.limiters.get(portal, self.limiters['default'])
        
        with self.lock:
            recent_requests = len([
                req_time for req_time in self.request_history.get(portal, [])
                if datetime.now() - req_time < timedelta(minutes=1)
            ])
            
            return {
                'current_delay': limiter.get_current_delay(portal),
                'failure_count': limiter.failure_count.get(portal, 0),
                'requests_last_minute': recent_requests,
                'max_requests_per_minute': self.portal_configs.get(portal, {}).get('max_requests_per_minute', 30)
            }

# Instância global
rate_manager = PortalRateManager()
