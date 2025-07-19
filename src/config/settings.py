# src/config/settings.py
"""
Configurações centralizadas do sistema
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ScraperConfig:
    """Configurações para scrapers"""
    max_results: int = 20
    timeout: int = 30
    retry_attempts: int = 3
    delay_between_requests: float = 1.0
    user_agents: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]

@dataclass
class APIConfig:
    """Configurações da API"""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = False
    cors_enabled: bool = True

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    database_url: str = 'sqlite:///properties.db'
    echo: bool = False

class Settings:
    """Configurações principais do sistema"""
    
    # Configurações de ambiente
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Configurações dos componentes
    SCRAPER = ScraperConfig()
    API = APIConfig()
    DATABASE = DatabaseConfig()
    
    # Mapeamento de cidades
    CITY_MAPPING = {
        'zapimoveis': {
            'rio-de-janeiro': 'rj+rio-de-janeiro',
            'sao-paulo': 'sp+sao-paulo',
            'belo-horizonte': 'mg+belo-horizonte',
            'brasilia': 'df+brasilia',
            'salvador': 'ba+salvador',
            'fortaleza': 'ce+fortaleza',
            'recife': 'pe+recife',
            'curitiba': 'pr+curitiba',
            'porto-alegre': 'rs+porto-alegre',
            'manaus': 'am+manaus'
        },
        'olx': {
            'rio-de-janeiro': 'estado-rj/rio-de-janeiro',
            'sao-paulo': 'estado-sp/sao-paulo',
            'belo-horizonte': 'estado-mg/belo-horizonte',
            'brasilia': 'estado-df',
            'salvador': 'estado-ba/salvador',
            'fortaleza': 'estado-ce/fortaleza',
            'recife': 'estado-pe/recife',
            'curitiba': 'estado-pr/curitiba',
            'porto-alegre': 'estado-rs/porto-alegre',
            'manaus': 'estado-am/manaus'
        }
    }
    
    # URLs base dos portais
    PORTAL_URLS = {
        'zapimoveis': 'https://www.zapimoveis.com.br',
        'olx': 'https://www.olx.com.br'
    }

# Instância global das configurações
settings = Settings()
