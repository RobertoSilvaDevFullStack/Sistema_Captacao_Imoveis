# src/utils/rate_limiting_decorator.py
"""
Decorators para aplicar rate limiting inteligente automaticamente
"""
import functools
import time
import logging
from typing import Callable, Any, Optional, Dict
from .advanced_rate_limiter import advanced_rate_manager, BlockingLevel

logger = logging.getLogger(__name__)

def intelligent_rate_limit(portal: str, 
                         action_type: str = 'navigation',
                         max_retries: int = 3,
                         enable_retry: bool = True):
    """
    Decorator para aplicar rate limiting inteligente a funções
    
    Args:
        portal: Portal sendo acessado
        action_type: Tipo de ação ('navigation', 'search', 'reading', 'idle')
        max_retries: Número máximo de tentativas
        enable_retry: Se deve tentar novamente em caso de falha
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            last_error = None
            start_time = 0.0  # Inicializar start_time
            
            while attempt <= max_retries:
                try:
                    # Aplicar rate limiting antes da requisição
                    if attempt == 0:  # Apenas na primeira tentativa
                        advanced_rate_manager.wait_for_request(portal, action_type)
                    
                    # Medir tempo de execução
                    start_time = time.time()
                    
                    # Executar função
                    result = func(*args, **kwargs)
                    
                    # Calcular tempo de resposta
                    response_time = time.time() - start_time
                    
                    # Registrar sucesso
                    advanced_rate_manager.record_request_result(
                        portal=portal,
                        success=True,
                        response_time=response_time,
                        status_code=200,  # Assumir sucesso
                        blocking_level=BlockingLevel.NORMAL
                    )
                    
                    logger.info(f"✅ {func.__name__} executado com sucesso para {portal} "
                               f"(tentativa {attempt + 1}, {response_time:.2f}s)")
                    
                    return result
                    
                except Exception as e:
                    attempt += 1
                    end_time = time.time()
                    response_time = end_time - start_time if 'start_time' in locals() else 0.0
                    last_error = str(e)
                    
                    # Determinar código de status baseado na exceção
                    status_code = _get_status_code_from_exception(e)
                    blocking_level = _get_blocking_level_from_exception(e)
                    
                    # Registrar falha
                    advanced_rate_manager.record_request_result(
                        portal=portal,
                        success=False,
                        response_time=response_time,
                        status_code=status_code,
                        error_type=type(e).__name__,
                        blocking_level=blocking_level
                    )
                    
                    logger.warning(f"❌ {func.__name__} falhou para {portal} "
                                  f"(tentativa {attempt}/{max_retries + 1}): {last_error}")
                    
                    # Verificar se deve tentar novamente
                    if enable_retry and attempt <= max_retries:
                        should_retry, retry_delay = advanced_rate_manager.should_retry_request(
                            portal=portal,
                            attempt=attempt,
                            last_error=last_error
                        )
                        
                        if should_retry:
                            logger.info(f"🔄 Tentando novamente em {retry_delay:.2f}s...")
                            time.sleep(retry_delay)
                            continue
                    
                    # Se chegou aqui, não vai tentar novamente
                    logger.error(f"💥 {func.__name__} falhou definitivamente para {portal} "
                                f"após {attempt} tentativa(s)")
                    raise
            
            # Se saiu do loop, todas as tentativas falharam
            raise Exception(f"Função {func.__name__} falhou após {max_retries + 1} tentativas. "
                          f"Último erro: {last_error}")
        
        return wrapper
    return decorator

def _get_status_code_from_exception(exception: Exception) -> Optional[int]:
    """Extrai código de status da exceção se disponível"""
    # Para requests.HTTPError
    if hasattr(exception, 'response'):
        response = getattr(exception, 'response')
        if hasattr(response, 'status_code'):
            return getattr(response, 'status_code')
    
    # Para erros HTTP comuns
    error_str = str(exception).lower()
    if '404' in error_str:
        return 404
    elif '403' in error_str:
        return 403
    elif '429' in error_str:
        return 429
    elif '503' in error_str:
        return 503
    elif '500' in error_str:
        return 500
    
    return None

def _get_blocking_level_from_exception(exception: Exception) -> BlockingLevel:
    """Determina nível de bloqueio baseado na exceção"""
    error_str = str(exception).lower()
    
    if 'captcha' in error_str or 'recaptcha' in error_str:
        return BlockingLevel.CAPTCHA
    elif 'banned' in error_str or 'blocked' in error_str:
        return BlockingLevel.IP_BAN
    elif 'rate limit' in error_str or 'too many' in error_str or '429' in error_str:
        return BlockingLevel.HARD_BLOCK
    elif 'timeout' in error_str or '503' in error_str:
        return BlockingLevel.SOFT_BLOCK
    else:
        return BlockingLevel.NORMAL

# Decorators específicos por portal para facilitar o uso

def zapimoveis_rate_limit(action_type: str = 'navigation', max_retries: int = 3):
    """Decorator específico para ZapImóveis"""
    return intelligent_rate_limit('zapimoveis', action_type, max_retries)

def olx_rate_limit(action_type: str = 'navigation', max_retries: int = 3):
    """Decorator específico para OLX"""
    return intelligent_rate_limit('olx', action_type, max_retries)

def vivareal_rate_limit(action_type: str = 'navigation', max_retries: int = 3):
    """Decorator específico para VivaReal"""
    return intelligent_rate_limit('vivareal', action_type, max_retries)

# Context manager para rate limiting manual

class RateLimitedContext:
    """Context manager para aplicar rate limiting manualmente"""
    
    def __init__(self, portal: str, action_type: str = 'navigation'):
        self.portal = portal
        self.action_type = action_type
        self.start_time = None
    
    def __enter__(self):
        # Aplicar rate limiting
        advanced_rate_manager.wait_for_request(self.portal, self.action_type)
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        response_time = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            # Sucesso
            advanced_rate_manager.record_request_result(
                portal=self.portal,
                success=True,
                response_time=response_time,
                status_code=200,
                blocking_level=BlockingLevel.NORMAL
            )
        else:
            # Falha
            status_code = _get_status_code_from_exception(exc_val) if exc_val else None
            blocking_level = _get_blocking_level_from_exception(exc_val) if exc_val else BlockingLevel.NORMAL
            
            advanced_rate_manager.record_request_result(
                portal=self.portal,
                success=False,
                response_time=response_time,
                status_code=status_code,
                error_type=exc_type.__name__ if exc_type else None,
                blocking_level=blocking_level
            )

# Funções utilitárias

def get_portal_health(portal: str) -> Dict[str, Any]:
    """
    Retorna saúde atual do portal
    
    Args:
        portal: Portal para verificar
        
    Returns:
        Dict com informações de saúde
    """
    stats = advanced_rate_manager.get_portal_statistics(portal)
    
    if stats.get('status') != 'active':
        return {
            'health': 'unknown',
            'recommendation': 'Sem dados suficientes',
            'stats': stats
        }
    
    success_rate = stats.get('success_rate', 0)
    recent_failures = stats.get('recent_failures', 0)
    
    # Determinar saúde
    if success_rate >= 0.9 and recent_failures <= 2:
        health = 'excellent'
        recommendation = 'Portal funcionando perfeitamente'
    elif success_rate >= 0.7 and recent_failures <= 5:
        health = 'good'
        recommendation = 'Portal funcionando bem'
    elif success_rate >= 0.5 and recent_failures <= 10:
        health = 'fair'
        recommendation = 'Portal com problemas intermitentes'
    else:
        health = 'poor'
        recommendation = 'Portal com problemas sérios - reduzir frequência'
    
    return {
        'health': health,
        'recommendation': recommendation,
        'stats': stats
    }

def suggest_optimal_timing(portal: str) -> Dict[str, Any]:
    """
    Sugere melhor timing para acessar portal
    
    Args:
        portal: Portal para analisar
        
    Returns:
        Dict com sugestões de timing
    """
    from datetime import datetime
    
    config = advanced_rate_manager.portal_configs.get(portal, {})
    preferred_hours = config.get('preferred_hours', [])
    current_hour = datetime.now().hour
    
    # Verificar se estamos em horário preferido
    is_optimal_time = current_hour in preferred_hours
    
    # Sugerir próximo horário bom
    if not is_optimal_time and preferred_hours:
        next_good_hours = [h for h in preferred_hours if h > current_hour]
        if not next_good_hours:
            next_good_hours = preferred_hours  # Próximo dia
        
        next_optimal = min(next_good_hours)
        hours_to_wait = next_optimal - current_hour
        if hours_to_wait <= 0:
            hours_to_wait += 24
    else:
        hours_to_wait = 0
    
    return {
        'is_optimal_time': is_optimal_time,
        'current_hour': current_hour,
        'preferred_hours': preferred_hours,
        'hours_to_optimal': hours_to_wait,
        'recommendation': 'Horário ideal para scraping' if is_optimal_time 
                         else f'Aguardar {hours_to_wait}h para horário ideal'
    }
