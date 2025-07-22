# src/utils/advanced_rate_limiter.py
"""
Sistema Avançado de Rate Limiting Inteligente
- Delays aleatórios mais sofisticados
- Backoff exponencial com jitter
- Lógica de retry inteligente
- Detecção de padrões de bloqueio
- Análise comportamental
"""
import time
import random
import threading
import math
import logging
from typing import Dict, Optional, List, Tuple, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics

# Configurar logging
logger = logging.getLogger(__name__)

class BlockingLevel(Enum):
    """Níveis de bloqueio detectados"""
    NORMAL = "normal"
    SOFT_BLOCK = "soft_block"
    HARD_BLOCK = "hard_block"
    CAPTCHA = "captcha"
    IP_BAN = "ip_ban"

@dataclass
class RequestMetrics:
    """Métricas de uma requisição"""
    timestamp: datetime
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_type: Optional[str] = None
    blocking_level: BlockingLevel = BlockingLevel.NORMAL

@dataclass
class PortalBehavior:
    """Comportamento observado de um portal"""
    avg_response_time: float
    success_rate: float
    peak_hours: List[int]  # Horas do dia com mais atividade
    blocking_threshold: int  # Número de requests que causam bloqueio
    recovery_time: float  # Tempo para se recuperar de bloqueio
    last_analysis: datetime

class IntelligentDelayCalculator:
    """Calculadora inteligente de delays baseada em múltiplos fatores"""
    
    def __init__(self):
        self.human_patterns = {
            'reading_time': (2.0, 15.0),  # Tempo lendo uma página
            'navigation_time': (0.5, 3.0),  # Tempo navegando
            'search_time': (5.0, 30.0),  # Tempo fazendo busca
            'idle_time': (10.0, 300.0)  # Tempo inativo
        }
        
    def calculate_delay(self, 
                       base_delay: float,
                       failure_count: int,
                       time_of_day: int,
                       portal_load: float,
                       last_action: str = 'navigation') -> float:
        """
        Calcula delay inteligente baseado em múltiplos fatores
        
        Args:
            base_delay: Delay base em segundos
            failure_count: Número de falhas consecutivas
            time_of_day: Hora do dia (0-23)
            portal_load: Carga do portal (0.0-1.0)
            last_action: Tipo da última ação
            
        Returns:
            float: Delay calculado em segundos
        """
        # 1. Delay base com variação humana
        human_delay = self._get_human_delay(last_action)
        
        # 2. Backoff exponencial com jitter
        backoff_delay = self._exponential_backoff_with_jitter(failure_count)
        
        # 3. Ajuste por horário (evitar horários de pico)
        time_multiplier = self._get_time_multiplier(time_of_day)
        
        # 4. Ajuste por carga do portal
        load_multiplier = 1.0 + (portal_load * 0.5)
        
        # 5. Combinar todos os fatores
        total_delay = max(
            human_delay,
            base_delay * backoff_delay * time_multiplier * load_multiplier
        )
        
        # 6. Adicionar ruído para evitar padrões
        noise = random.uniform(0.8, 1.2)
        
        return total_delay * noise
    
    def _get_human_delay(self, action: str) -> float:
        """Simula delays humanos realísticos"""
        # Mapear ações para padrões disponíveis
        action_mapping = {
            'search': 'search_time',
            'navigation': 'navigation_time',
            'reading': 'reading_time',
            'idle': 'idle_time'
        }
        
        # Usar mapeamento ou padrão padrão
        pattern_key = action_mapping.get(action, 'navigation_time')
        pattern = self.human_patterns[pattern_key]
        
        # Usar distribuição log-normal para simular comportamento humano
        mu = math.log(pattern[0])
        sigma = 0.5
        delay = random.lognormvariate(mu, sigma)
        
        # Limitar ao range máximo
        return min(delay, pattern[1])
    
    def _exponential_backoff_with_jitter(self, failure_count: int) -> float:
        """Backoff exponencial com jitter para evitar thundering herd"""
        if failure_count == 0:
            return 1.0
            
        # Backoff exponencial com cap
        base_backoff = min(2 ** failure_count, 64)
        
        # Adicionar jitter (decorrelated jitter)
        jitter = random.uniform(0, base_backoff)
        
        return base_backoff + jitter
    
    def _get_time_multiplier(self, hour: int) -> float:
        """Multiplier baseado no horário para evitar horários de pico"""
        # Horários de pico (9-11h, 14-16h, 19-21h) = mais delay
        # Horários noturnos (22-6h) = menos delay
        
        if 9 <= hour <= 11 or 14 <= hour <= 16 or 19 <= hour <= 21:
            return random.uniform(1.5, 2.0)  # Horário comercial
        elif 22 <= hour or hour <= 6:
            return random.uniform(0.5, 0.8)  # Horário noturno
        else:
            return random.uniform(0.8, 1.2)  # Horário normal

class SmartRetryManager:
    """Gerenciador inteligente de retries"""
    
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
        self.retry_strategies = {
            BlockingLevel.NORMAL: self._normal_retry,
            BlockingLevel.SOFT_BLOCK: self._soft_block_retry,
            BlockingLevel.HARD_BLOCK: self._hard_block_retry,
            BlockingLevel.CAPTCHA: self._captcha_retry,
            BlockingLevel.IP_BAN: self._ip_ban_retry
        }
    
    def should_retry(self, 
                    attempt: int,
                    blocking_level: BlockingLevel,
                    portal: str,
                    error_history: List[RequestMetrics]) -> bool:
        """
        Decide se deve tentar novamente baseado no contexto
        
        Args:
            attempt: Número da tentativa atual
            blocking_level: Nível de bloqueio detectado
            portal: Portal sendo acessado
            error_history: Histórico de erros
            
        Returns:
            bool: True se deve tentar novamente
        """
        if attempt >= self.max_retries:
            return False
            
        # Analisar padrão de erros recentes
        recent_errors = error_history[-5:] if len(error_history) >= 5 else error_history
        
        if len(recent_errors) >= 3:
            # Se todos os erros recentes são do mesmo tipo, pode ser bloqueio sistemático
            error_types = [e.error_type for e in recent_errors]
            if len(set(error_types)) == 1:
                logger.warning(f"Padrão de erro sistemático detectado: {error_types[0]}")
                return blocking_level not in [BlockingLevel.IP_BAN, BlockingLevel.HARD_BLOCK]
        
        return self.retry_strategies[blocking_level](attempt, portal, recent_errors)
    
    def _normal_retry(self, attempt: int, portal: str, error_history: List[RequestMetrics]) -> bool:
        """Retry normal para erros temporários"""
        return attempt < 3
    
    def _soft_block_retry(self, attempt: int, portal: str, error_history: List[RequestMetrics]) -> bool:
        """Retry para bloqueio leve com delay maior"""
        return attempt < 2
    
    def _hard_block_retry(self, attempt: int, portal: str, error_history: List[RequestMetrics]) -> bool:
        """Retry limitado para bloqueio severo"""
        return attempt < 1
    
    def _captcha_retry(self, attempt: int, portal: str, error_history: List[RequestMetrics]) -> bool:
        """Retry para CAPTCHA (geralmente não vale a pena)"""
        return False
    
    def _ip_ban_retry(self, attempt: int, portal: str, error_history: List[RequestMetrics]) -> bool:
        """Não retry para banimento de IP"""
        return False
    
    def get_retry_delay(self, 
                       attempt: int,
                       blocking_level: BlockingLevel,
                       base_delay: float = 1.0) -> float:
        """
        Calcula delay antes do retry
        
        Args:
            attempt: Número da tentativa
            blocking_level: Nível de bloqueio
            base_delay: Delay base
            
        Returns:
            float: Delay em segundos
        """
        multipliers = {
            BlockingLevel.NORMAL: 2.0,
            BlockingLevel.SOFT_BLOCK: 5.0,
            BlockingLevel.HARD_BLOCK: 15.0,
            BlockingLevel.CAPTCHA: 60.0,
            BlockingLevel.IP_BAN: 300.0
        }
        
        multiplier = multipliers.get(blocking_level, 2.0)
        exponential_delay = base_delay * (multiplier ** attempt)
        
        # Adicionar jitter
        jitter = random.uniform(0.5, 1.5)
        
        # Cap máximo
        max_delay = {
            BlockingLevel.NORMAL: 60.0,
            BlockingLevel.SOFT_BLOCK: 300.0,
            BlockingLevel.HARD_BLOCK: 900.0,
            BlockingLevel.CAPTCHA: 1800.0,
            BlockingLevel.IP_BAN: 3600.0
        }
        
        final_delay = min(exponential_delay * jitter, max_delay.get(blocking_level, 60.0))
        
        logger.info(f"Retry delay calculado: {final_delay:.2f}s para {blocking_level.value} (tentativa {attempt})")
        
        return final_delay

class BehaviorAnalyzer:
    """Analisador de comportamento do portal"""
    
    def __init__(self, analysis_window: timedelta = timedelta(hours=24)):
        self.analysis_window = analysis_window
        self.portal_behaviors: Dict[str, PortalBehavior] = {}
    
    def analyze_portal(self, portal: str, metrics: List[RequestMetrics]) -> PortalBehavior:
        """
        Analisa comportamento do portal baseado em métricas históricas
        
        Args:
            portal: Nome do portal
            metrics: Métricas de requisições
            
        Returns:
            PortalBehavior: Comportamento analisado
        """
        if not metrics:
            return self._default_behavior()
        
        # Filtrar métricas recentes
        cutoff = datetime.now() - self.analysis_window
        recent_metrics = [m for m in metrics if m.timestamp > cutoff]
        
        if not recent_metrics:
            return self._default_behavior()
        
        # Calcular métricas
        response_times = [m.response_time for m in recent_metrics if m.success]
        avg_response_time = statistics.mean(response_times) if response_times else 5.0
        
        success_count = sum(1 for m in recent_metrics if m.success)
        success_rate = success_count / len(recent_metrics)
        
        # Analisar horários de pico
        hours = [m.timestamp.hour for m in recent_metrics]
        peak_hours = self._find_peak_hours(hours)
        
        # Detectar threshold de bloqueio
        blocking_threshold = self._detect_blocking_threshold(recent_metrics)
        
        # Calcular tempo de recuperação
        recovery_time = self._calculate_recovery_time(recent_metrics)
        
        behavior = PortalBehavior(
            avg_response_time=avg_response_time,
            success_rate=success_rate,
            peak_hours=peak_hours,
            blocking_threshold=blocking_threshold,
            recovery_time=recovery_time,
            last_analysis=datetime.now()
        )
        
        self.portal_behaviors[portal] = behavior
        
        logger.info(f"Comportamento analisado para {portal}: "
                   f"response_time={avg_response_time:.2f}s, "
                   f"success_rate={success_rate:.1%}, "
                   f"blocking_threshold={blocking_threshold}")
        
        return behavior
    
    def _default_behavior(self) -> PortalBehavior:
        """Comportamento padrão quando não há dados suficientes"""
        return PortalBehavior(
            avg_response_time=3.0,
            success_rate=0.9,
            peak_hours=[9, 10, 14, 15, 19, 20],
            blocking_threshold=20,
            recovery_time=300.0,
            last_analysis=datetime.now()
        )
    
    def _find_peak_hours(self, hours: List[int]) -> List[int]:
        """Encontra horários de pico baseado na frequência"""
        if not hours:
            return [9, 10, 14, 15, 19, 20]  # Default comercial
            
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Retornar horários com mais de 10% das requisições
        total_requests = len(hours)
        threshold = total_requests * 0.1
        
        peak_hours = [hour for hour, count in hour_counts.items() if count > threshold]
        
        return sorted(peak_hours)
    
    def _detect_blocking_threshold(self, metrics: List[RequestMetrics]) -> int:
        """Detecta quantas requisições causam bloqueio"""
        # Analisar sequências de falhas
        failure_sequences = []
        current_sequence = 0
        
        for metric in metrics:
            if not metric.success:
                current_sequence += 1
            else:
                if current_sequence > 0:
                    failure_sequences.append(current_sequence)
                current_sequence = 0
        
        if current_sequence > 0:
            failure_sequences.append(current_sequence)
        
        # Threshold é a mediana das sequências de falha
        if failure_sequences:
            return int(statistics.median(failure_sequences))
        
        return 15  # Default
    
    def _calculate_recovery_time(self, metrics: List[RequestMetrics]) -> float:
        """Calcula tempo médio de recuperação após bloqueio"""
        recovery_times = []
        last_failure_time = None
        
        for metric in metrics:
            if not metric.success:
                last_failure_time = metric.timestamp
            elif last_failure_time:
                # Primeira requisição bem-sucedida após falha
                recovery_time = (metric.timestamp - last_failure_time).total_seconds()
                recovery_times.append(recovery_time)
                last_failure_time = None
        
        if recovery_times:
            return statistics.mean(recovery_times)
        
        return 180.0  # Default: 3 minutos

class AdvancedRateManager:
    """Gerenciador avançado de rate limiting"""
    
    def __init__(self):
        self.delay_calculator = IntelligentDelayCalculator()
        self.retry_manager = SmartRetryManager()
        self.behavior_analyzer = BehaviorAnalyzer()
        
        # Métricas por portal
        self.metrics: Dict[str, List[RequestMetrics]] = {}
        self.lock = threading.RLock()
        
        # Configurações por portal
        self.portal_configs = {
            'zapimoveis': {
                'base_delay': (3.0, 8.0),
                'max_requests_per_minute': 12,
                'burst_protection': True,
                'requires_session': True,
                'preferred_hours': list(range(22, 24)) + list(range(0, 7))  # Noite/madrugada
            },
            'olx': {
                'base_delay': (2.0, 6.0),
                'max_requests_per_minute': 18,
                'burst_protection': True,
                'requires_session': False,
                'preferred_hours': list(range(1, 8))  # Madrugada
            },
            'vivareal': {
                'base_delay': (4.0, 10.0),
                'max_requests_per_minute': 8,
                'burst_protection': True,
                'requires_session': True,
                'preferred_hours': list(range(23, 24)) + list(range(0, 6))  # Noite
            }
        }
        
        # Estado atual dos portais
        self.portal_states: Dict[str, Dict] = {}
    
    def wait_for_request(self, 
                        portal: str,
                        action_type: str = 'navigation') -> None:
        """
        Aplica delay inteligente antes de uma requisição
        
        Args:
            portal: Portal sendo acessado
            action_type: Tipo de ação ('navigation', 'search', 'reading', 'idle')
        """
        with self.lock:
            # Obter configuração do portal
            config = self.portal_configs.get(portal, self.portal_configs['zapimoveis'])
            
            # Analisar comportamento atual
            metrics = self.metrics.get(portal, [])
            behavior = self.behavior_analyzer.analyze_portal(portal, metrics)
            
            # Calcular delay inteligente
            current_hour = datetime.now().hour
            failure_count = self._get_recent_failure_count(portal)
            portal_load = self._estimate_portal_load(portal, current_hour)
            
            base_delay = random.uniform(*config['base_delay'])
            
            delay = self.delay_calculator.calculate_delay(
                base_delay=base_delay,
                failure_count=failure_count,
                time_of_day=current_hour,
                portal_load=portal_load,
                last_action=action_type
            )
            
            # Verificar rate limiting
            if self._check_rate_limit(portal):
                additional_delay = self._calculate_rate_limit_delay(portal)
                delay += additional_delay
                logger.warning(f"Rate limit ativo para {portal}, delay adicional: {additional_delay:.2f}s")
            
            logger.info(f"Aguardando {delay:.2f}s antes de acessar {portal} ({action_type})")
            
            # Aplicar delay
            time.sleep(delay)
            
            # Registrar início da requisição
            self._record_request_start(portal)
    
    def record_request_result(self,
                             portal: str,
                             success: bool,
                             response_time: float,
                             status_code: Optional[int] = None,
                             error_type: Optional[str] = None,
                             blocking_level: BlockingLevel = BlockingLevel.NORMAL) -> None:
        """
        Registra resultado de uma requisição
        
        Args:
            portal: Portal acessado
            success: Se a requisição foi bem-sucedida
            response_time: Tempo de resposta
            status_code: Código de status HTTP
            error_type: Tipo de erro se houve falha
            blocking_level: Nível de bloqueio detectado
        """
        with self.lock:
            metric = RequestMetrics(
                timestamp=datetime.now(),
                success=success,
                response_time=response_time,
                status_code=status_code,
                error_type=error_type,
                blocking_level=blocking_level
            )
            
            if portal not in self.metrics:
                self.metrics[portal] = []
            
            self.metrics[portal].append(metric)
            
            # Manter apenas últimas 1000 métricas por portal
            if len(self.metrics[portal]) > 1000:
                self.metrics[portal] = self.metrics[portal][-1000:]
            
            # Log do resultado
            status = "✅" if success else "❌"
            logger.info(f"{status} {portal}: {response_time:.2f}s, "
                       f"status={status_code}, "
                       f"blocking={blocking_level.value}")
    
    def should_retry_request(self,
                           portal: str,
                           attempt: int,
                           last_error: Optional[str] = None) -> Tuple[bool, float]:
        """
        Decide se deve tentar novamente uma requisição
        
        Args:
            portal: Portal sendo acessado
            attempt: Número da tentativa atual
            last_error: Último erro ocorrido
            
        Returns:
            Tuple[bool, float]: (should_retry, delay_seconds)
        """
        with self.lock:
            metrics = self.metrics.get(portal, [])
            recent_metrics = metrics[-10:] if len(metrics) >= 10 else metrics
            
            # Detectar nível de bloqueio baseado no erro
            blocking_level = self._detect_blocking_level(last_error)
            
            # Verificar se deve tentar novamente
            should_retry = self.retry_manager.should_retry(
                attempt=attempt,
                blocking_level=blocking_level,
                portal=portal,
                error_history=recent_metrics
            )
            
            # Calcular delay do retry
            retry_delay = 0.0
            if should_retry:
                retry_delay = self.retry_manager.get_retry_delay(
                    attempt=attempt,
                    blocking_level=blocking_level
                )
            
            return should_retry, retry_delay
    
    def get_portal_statistics(self, portal: str) -> Dict:
        """Retorna estatísticas detalhadas do portal"""
        with self.lock:
            metrics = self.metrics.get(portal, [])
            
            if not metrics:
                return {'status': 'no_data'}
            
            # Métricas recentes (últimas 24h)
            cutoff = datetime.now() - timedelta(hours=24)
            recent_metrics = [m for m in metrics if m.timestamp > cutoff]
            
            if not recent_metrics:
                return {'status': 'no_recent_data'}
            
            # Calcular estatísticas
            success_count = sum(1 for m in recent_metrics if m.success)
            success_rate = success_count / len(recent_metrics)
            
            response_times = [m.response_time for m in recent_metrics if m.success]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            failure_count = self._get_recent_failure_count(portal)
            
            # Detecção de bloqueio
            blocking_indicators = {level.value: sum(1 for m in recent_metrics if m.blocking_level == level) 
                                 for level in BlockingLevel}
            
            return {
                'status': 'active',
                'total_requests': len(recent_metrics),
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'recent_failures': failure_count,
                'blocking_indicators': blocking_indicators,
                'last_request': recent_metrics[-1].timestamp.isoformat() if recent_metrics else None
            }
    
    # Métodos auxiliares privados
    
    def _get_recent_failure_count(self, portal: str) -> int:
        """Conta falhas recentes consecutivas"""
        metrics = self.metrics.get(portal, [])
        
        failure_count = 0
        for metric in reversed(metrics):
            if not metric.success:
                failure_count += 1
            else:
                break
                
        return failure_count
    
    def _estimate_portal_load(self, portal: str, current_hour: int) -> float:
        """Estima carga atual do portal (0.0-1.0)"""
        config = self.portal_configs.get(portal, {})
        preferred_hours = config.get('preferred_hours', [])
        
        # Se estamos em horário preferido, carga menor
        if current_hour in preferred_hours:
            return random.uniform(0.1, 0.3)
        
        # Horários comerciais = carga alta
        if 9 <= current_hour <= 18:
            return random.uniform(0.7, 1.0)
        
        # Outros horários = carga média
        return random.uniform(0.3, 0.7)
    
    def _check_rate_limit(self, portal: str) -> bool:
        """Verifica se rate limit foi excedido"""
        config = self.portal_configs.get(portal, {})
        max_requests = config.get('max_requests_per_minute', 15)
        
        metrics = self.metrics.get(portal, [])
        cutoff = datetime.now() - timedelta(minutes=1)
        recent_requests = [m for m in metrics if m.timestamp > cutoff]
        
        return len(recent_requests) >= max_requests
    
    def _calculate_rate_limit_delay(self, portal: str) -> float:
        """Calcula delay adicional por rate limiting"""
        metrics = self.metrics.get(portal, [])
        if not metrics:
            return 30.0
            
        # Encontrar requisição mais antiga no último minuto
        cutoff = datetime.now() - timedelta(minutes=1)
        recent_requests = [m for m in metrics if m.timestamp > cutoff]
        
        if recent_requests:
            oldest_request = min(m.timestamp for m in recent_requests)
            # Aguardar até que saia da janela de 1 minuto + margem
            wait_until = oldest_request + timedelta(minutes=1, seconds=10)
            now = datetime.now()
            
            if wait_until > now:
                return (wait_until - now).total_seconds()
        
        return 30.0  # Default
    
    def _record_request_start(self, portal: str) -> None:
        """Registra início de uma requisição"""
        # Atualizar estado do portal
        if portal not in self.portal_states:
            self.portal_states[portal] = {}
            
        self.portal_states[portal]['last_request_start'] = datetime.now()
    
    def _detect_blocking_level(self, error: Optional[str]) -> BlockingLevel:
        """Detecta nível de bloqueio baseado no erro"""
        if not error:
            return BlockingLevel.NORMAL
            
        error_lower = error.lower()
        
        if 'captcha' in error_lower or 'recaptcha' in error_lower:
            return BlockingLevel.CAPTCHA
        elif 'banned' in error_lower or 'blocked' in error_lower:
            return BlockingLevel.IP_BAN
        elif 'rate limit' in error_lower or 'too many' in error_lower:
            return BlockingLevel.HARD_BLOCK
        elif 'timeout' in error_lower or '503' in error_lower:
            return BlockingLevel.SOFT_BLOCK
        else:
            return BlockingLevel.NORMAL

# Instância global
advanced_rate_manager = AdvancedRateManager()
