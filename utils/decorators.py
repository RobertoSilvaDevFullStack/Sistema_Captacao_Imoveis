# em utils/decorators.py

import time
import logging
from functools import wraps

# --- DECORATOR 1: RATE LIMITER (Atualizado para aceitar float) ---
def rate_limit(calls_per_second=1.0):
    """
    Decorator que limita a frequência de chamadas de uma função
    
    Args:
        calls_per_second (float): Número de chamadas permitidas por segundo
    """
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# --- DECORATOR 2: METRICS TRACKER (Este está faltando) ---
def track_scraping_metrics(source, scraped_properties_counter, scraping_duration_histogram, errors_counter):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with scraping_duration_histogram.labels(source=source).time():
                try:
                    result = func(*args, **kwargs)
                    if isinstance(result, list):
                        scraped_properties_counter.labels(source=source).inc(len(result))
                    return result
                except Exception as e:
                    errors_counter.labels(source=source, error_type=type(e).__name__).inc()
                    logging.error(f"Métrica de erro capturada para {source}: {type(e).__name__}")
                    raise
        return wrapper
    return decorator