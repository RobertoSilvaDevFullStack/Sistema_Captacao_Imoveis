# backend/api_integrations/__init__.py
"""
Módulo de Integrações com APIs Oficiais e Alternativas
"""

from .google_maps_integration import GoogleMapsIntegration
from .ibge_integration import IBGEIntegration
from .municipal_apis import MunicipalAPIs
from .registry_apis import RegistryAPIs
from .market_data_apis import MarketDataAPIs

__all__ = [
    'GoogleMapsIntegration',
    'IBGEIntegration', 
    'MunicipalAPIs',
    'RegistryAPIs',
    'MarketDataAPIs'
]
