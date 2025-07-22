# src/utils/__init__.py
"""
Utilitários para o sistema de captação de imóveis
"""

from .header_rotator import header_rotator, HeaderRotator
from .rate_limiter import rate_manager, PortalRateManager, SmartRateLimit
from .proxy_rotator import proxy_manager, ProxyManager, ProxyRotator, ProxyInfo
from .selenium_proxy_config import selenium_proxy_config, SeleniumProxyConfig
from .advanced_rate_limiter import advanced_rate_manager, AdvancedRateManager, BlockingLevel
from .rate_limiting_decorator import (
    intelligent_rate_limit, 
    zapimoveis_rate_limit, 
    olx_rate_limit, 
    vivareal_rate_limit,
    RateLimitedContext,
    get_portal_health,
    suggest_optimal_timing
)

# Selenium Stealth (opcional)
try:
    from .selenium_stealth import (
        StealthWebDriver,
        StealthConfig,
        HumanBehaviorConfig,
        HumanBehaviorSimulator,
        StealthDriverManager,
        stealth_manager,
        create_stealth_driver
    )
    SELENIUM_STEALTH_AVAILABLE = True
except ImportError:
    SELENIUM_STEALTH_AVAILABLE = False

# Selenium Containers (opcional)
try:
    from .selenium_containers import (
        SeleniumContainer,
        SeleniumContainerPool,
        ContainerConfig,
        ContainerizedSeleniumTask,
        selenium_pool,
        execute_parallel_selenium_tasks,
        create_docker_compose_config
    )
    SELENIUM_CONTAINERS_AVAILABLE = True
except ImportError:
    SELENIUM_CONTAINERS_AVAILABLE = False

__all__ = [
    'header_rotator',
    'HeaderRotator', 
    'rate_manager',
    'PortalRateManager',
    'SmartRateLimit',
    'proxy_manager',
    'ProxyManager',
    'ProxyRotator',
    'ProxyInfo',
    'selenium_proxy_config',
    'SeleniumProxyConfig',
    'advanced_rate_manager',
    'AdvancedRateManager',
    'BlockingLevel',
    'intelligent_rate_limit',
    'zapimoveis_rate_limit',
    'olx_rate_limit', 
    'vivareal_rate_limit',
    'RateLimitedContext',
    'get_portal_health',
    'suggest_optimal_timing'
]

# Adicionar módulos Selenium se disponíveis
if SELENIUM_STEALTH_AVAILABLE:
    __all__.extend([
        'StealthWebDriver',
        'StealthConfig', 
        'HumanBehaviorConfig',
        'HumanBehaviorSimulator',
        'StealthDriverManager',
        'stealth_manager',
        'create_stealth_driver'
    ])

if SELENIUM_CONTAINERS_AVAILABLE:
    __all__.extend([
        'SeleniumContainer',
        'SeleniumContainerPool',
        'ContainerConfig', 
        'ContainerizedSeleniumTask',
        'selenium_pool',
        'execute_parallel_selenium_tasks',
        'create_docker_compose_config'
    ])
