# backend/api_integrations/google_maps_integration.py
"""
Integração com Google Maps API e Google Places API
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Tuple
import os
import time

class GoogleMapsIntegration:
    """Cliente para Google Maps e Places APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.requests_per_second = 50  # Limite da API
        self.last_request_time = 0
        
        if not self.api_key:
            self.logger.warning("Google Maps API Key não configurada")
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocodifica um endereço"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/geocode/json"
                params = {
                    'address': address,
                    'key': self.api_key,
                    'language': 'pt-BR',
                    'region': 'br'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK' and data['results']:
                            result = data['results'][0]
                            
                            return {
                                'latitude': result['geometry']['location']['lat'],
                                'longitude': result['geometry']['location']['lng'],
                                'formatted_address': result['formatted_address'],
                                'place_id': result['place_id'],
                                'address_components': result['address_components'],
                                'geometry': result['geometry']
                            }
                        else:
                            self.logger.warning(f"Geocoding failed: {data['status']}")
                    else:
                        self.logger.error(f"Google API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Erro na geocodificação: {e}")
        
        return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Geocodificação reversa"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/geocode/json"
                params = {
                    'latlng': f"{latitude},{longitude}",
                    'key': self.api_key,
                    'language': 'pt-BR',
                    'result_type': 'street_address'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK' and data['results']:
                            return data['results'][0]
                            
        except Exception as e:
            self.logger.error(f"Erro na geocodificação reversa: {e}")
        
        return None
    
    async def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes de um lugar pelo Place ID"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            fields = [
                'place_id', 'name', 'formatted_address', 'geometry',
                'address_components', 'types', 'rating', 'user_ratings_total',
                'photos', 'website', 'formatted_phone_number', 'reviews'
            ]
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/place/details/json"
                params = {
                    'place_id': place_id,
                    'fields': ','.join(fields),
                    'key': self.api_key,
                    'language': 'pt-BR'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK':
                            return data['result']
                        else:
                            self.logger.warning(f"Place details failed: {data['status']}")
                            
        except Exception as e:
            self.logger.error(f"Erro ao buscar detalhes do lugar: {e}")
        
        return None
    
    async def find_nearby_places(self, latitude: float, longitude: float, 
                                place_type: str, radius: int = 1000) -> List[Dict[str, Any]]:
        """Busca lugares próximos"""
        if not self.api_key:
            return []
        
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/place/nearbysearch/json"
                params = {
                    'location': f"{latitude},{longitude}",
                    'radius': radius,
                    'type': place_type,
                    'key': self.api_key,
                    'language': 'pt-BR'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK':
                            return data['results']
                        else:
                            self.logger.warning(f"Nearby search failed: {data['status']}")
                            
        except Exception as e:
            self.logger.error(f"Erro na busca de lugares próximos: {e}")
        
        return []
    
    async def get_elevation(self, latitude: float, longitude: float) -> Optional[float]:
        """Busca elevação de um ponto"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/elevation/json"
                params = {
                    'locations': f"{latitude},{longitude}",
                    'key': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK' and data['results']:
                            return data['results'][0]['elevation']
                            
        except Exception as e:
            self.logger.error(f"Erro ao buscar elevação: {e}")
        
        return None
    
    async def calculate_distance_matrix(self, origins: List[Tuple[float, float]], 
                                      destinations: List[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
        """Calcula matriz de distâncias"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            origins_str = '|'.join([f"{lat},{lng}" for lat, lng in origins])
            destinations_str = '|'.join([f"{lat},{lng}" for lat, lng in destinations])
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/distancematrix/json"
                params = {
                    'origins': origins_str,
                    'destinations': destinations_str,
                    'units': 'metric',
                    'mode': 'driving',
                    'key': self.api_key,
                    'language': 'pt-BR'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK':
                            return data
                            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de distâncias: {e}")
        
        return None
    
    async def get_street_view_metadata(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Verifica disponibilidade do Street View"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/streetview/metadata"
                params = {
                    'location': f"{latitude},{longitude}",
                    'key': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                        
        except Exception as e:
            self.logger.error(f"Erro no Street View metadata: {e}")
        
        return None
    
    async def search_text(self, query: str, location: Optional[Tuple[float, float]] = None,
                         radius: Optional[int] = None) -> List[Dict[str, Any]]:
        """Busca por texto"""
        if not self.api_key:
            return []
        
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/place/textsearch/json"
                params = {
                    'query': query,
                    'key': self.api_key,
                    'language': 'pt-BR'
                }
                
                if location:
                    params['location'] = f"{location[0]},{location[1]}"
                    if radius:
                        params['radius'] = str(radius)
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK':
                            return data['results']
                        else:
                            self.logger.warning(f"Text search failed: {data['status']}")
                            
        except Exception as e:
            self.logger.error(f"Erro na busca por texto: {e}")
        
        return []
    
    async def get_timezone(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Busca fuso horário"""
        if not self.api_key:
            return None
        
        try:
            await self._rate_limit()
            
            timestamp = int(time.time())
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/timezone/json"
                params = {
                    'location': f"{latitude},{longitude}",
                    'timestamp': timestamp,
                    'key': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data['status'] == 'OK':
                            return data
                            
        except Exception as e:
            self.logger.error(f"Erro ao buscar fuso horário: {e}")
        
        return None
    
    async def _rate_limit(self):
        """Aplica rate limiting"""
        now = time.time()
        min_interval = 1.0 / self.requests_per_second
        
        if now - self.last_request_time < min_interval:
            await asyncio.sleep(min_interval - (now - self.last_request_time))
        
        self.last_request_time = time.time()
    
    async def get_comprehensive_location_data(self, address: str) -> Dict[str, Any]:
        """Busca dados completos de localização"""
        result = {
            'geocoding': None,
            'place_details': None,
            'nearby_schools': [],
            'nearby_hospitals': [],
            'nearby_shopping': [],
            'nearby_transport': [],
            'elevation': None,
            'timezone': None,
            'street_view_available': False
        }
        
        # 1. Geocodificar endereço
        geocoding = await self.geocode_address(address)
        if not geocoding:
            return result
        
        result['geocoding'] = geocoding
        lat, lng = geocoding['latitude'], geocoding['longitude']
        
        # 2. Buscar dados em paralelo
        tasks = [
            self.get_place_details(geocoding['place_id']),
            self.find_nearby_places(lat, lng, 'school', 2000),
            self.find_nearby_places(lat, lng, 'hospital', 3000),
            self.find_nearby_places(lat, lng, 'shopping_mall', 5000),
            self.find_nearby_places(lat, lng, 'subway_station', 2000),
            self.get_elevation(lat, lng),
            self.get_timezone(lat, lng),
            self.get_street_view_metadata(lat, lng)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. Processar resultados com type checking
        if not isinstance(results[0], Exception):
            result['place_details'] = results[0]
        
        if not isinstance(results[1], Exception) and isinstance(results[1], list):
            result['nearby_schools'] = results[1][:5]  # Top 5
        
        if not isinstance(results[2], Exception) and isinstance(results[2], list):
            result['nearby_hospitals'] = results[2][:5]
        
        if not isinstance(results[3], Exception) and isinstance(results[3], list):
            result['nearby_shopping'] = results[3][:3]
        
        if not isinstance(results[4], Exception) and isinstance(results[4], list):
            result['nearby_transport'] = results[4][:5]
        
        if not isinstance(results[5], Exception):
            result['elevation'] = results[5]
        
        if not isinstance(results[6], Exception):
            result['timezone'] = results[6]
        
        if not isinstance(results[7], Exception) and isinstance(results[7], dict):
            street_view = results[7]
            result['street_view_available'] = street_view and street_view.get('status') == 'OK'
        
        return result
