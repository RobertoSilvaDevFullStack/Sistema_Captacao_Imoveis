# backend/services/data_enrichment_service.py
"""
Serviço de Enriquecimento de Dados com APIs Oficiais e Fontes Alternativas
"""
import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import quote
import hashlib
import os

@dataclass
class LocationData:
    """Dados de localização enriquecidos"""
    address: str
    neighborhood: str
    city: str
    state: str
    zipcode: str
    latitude: float
    longitude: float
    google_place_id: Optional[str] = None
    
@dataclass
class PropertyEnrichment:
    """Dados de enriquecimento do imóvel"""
    # Dados básicos
    property_id: str
    original_data: Dict[str, Any]
    
    # Localização enriquecida
    location: LocationData
    
    # Dados de cartório/registro
    registry_data: Optional[Dict[str, Any]] = None
    
    # Dados da prefeitura
    municipal_data: Optional[Dict[str, Any]] = None
    
    # Dados do Google Maps
    google_data: Optional[Dict[str, Any]] = None
    
    # Dados de mercado imobiliário
    market_data: Optional[Dict[str, Any]] = None
    
    # Score de confiabilidade
    confidence_score: float = 0.0
    
    # Timestamp do enriquecimento
    enriched_at: str = ""

class DataEnrichmentService:
    """Serviço principal de enriquecimento de dados"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # APIs Keys (configurar via environment)
        self.google_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.ibge_api_base = "https://servicodados.ibge.gov.br/api/v1"
        self.cep_api_base = "https://viacep.com.br/ws"
        
        # Cache de requisições para evitar duplicatas
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Rate limiting
        self.request_delay = 0.1  # 100ms entre requests
        self.last_request_time = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger("data_enrichment")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def enrich_property(self, property_data: Dict[str, Any]) -> PropertyEnrichment:
        """Enriquece um imóvel com dados de múltiplas fontes"""
        property_id = property_data.get('id', 'unknown')
        
        self.logger.info(f"🔍 Iniciando enriquecimento do imóvel {property_id}")
        
        # 1. Normalizar e extrair localização
        location = await self._extract_location(property_data)
        
        # 2. Buscar dados em paralelo de múltiplas fontes
        tasks = [
            self._get_google_data(location),
            self._get_cep_data(location.zipcode),
            self._get_ibge_data(location.city, location.state),
            self._get_municipal_data(location),
            self._get_registry_data(location),
            self._get_market_data(location)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. Processar resultados com type checking
        google_data: Optional[Dict[str, Any]] = None
        if not isinstance(results[0], Exception) and isinstance(results[0], dict):
            google_data = results[0]
        
        cep_data = results[1] if not isinstance(results[1], Exception) else None
        ibge_data = results[2] if not isinstance(results[2], Exception) else None
        
        municipal_data: Optional[Dict[str, Any]] = None
        if not isinstance(results[3], Exception) and isinstance(results[3], dict):
            municipal_data = results[3]
        
        registry_data: Optional[Dict[str, Any]] = None
        if not isinstance(results[4], Exception) and isinstance(results[4], dict):
            registry_data = results[4]
        
        market_data: Optional[Dict[str, Any]] = None
        if not isinstance(results[5], Exception) and isinstance(results[5], dict):
            market_data = results[5]
        
        # 4. Calcular score de confiabilidade
        confidence_score = self._calculate_confidence_score({
            'google_data': google_data,
            'cep_data': cep_data,
            'ibge_data': ibge_data,
            'municipal_data': municipal_data,
            'registry_data': registry_data,
            'market_data': market_data
        })
        
        # 5. Criar objeto enriquecido
        enrichment = PropertyEnrichment(
            property_id=property_id,
            original_data=property_data,
            location=location,
            google_data=google_data,
            municipal_data=municipal_data,
            registry_data=registry_data,
            market_data=market_data,
            confidence_score=confidence_score,
            enriched_at=time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.logger.info(f"✅ Enriquecimento concluído - Score: {confidence_score:.2f}")
        
        return enrichment
    
    async def _extract_location(self, property_data: Dict[str, Any]) -> LocationData:
        """Extrai e normaliza dados de localização"""
        address = property_data.get('address', '')
        neighborhood = property_data.get('neighborhood', '')
        city = property_data.get('city', '')
        state = property_data.get('state', '')
        zipcode = property_data.get('zipcode', '').replace('-', '').replace(' ', '')
        
        # Tentar extrair coordenadas se disponíveis
        lat = property_data.get('latitude', 0.0)
        lng = property_data.get('longitude', 0.0)
        
        # Se não tem coordenadas, tentar geocodificar
        if not lat or not lng:
            lat, lng = await self._geocode_address(f"{address}, {neighborhood}, {city}, {state}")
        
        return LocationData(
            address=address,
            neighborhood=neighborhood,
            city=city,
            state=state,
            zipcode=zipcode,
            latitude=lat,
            longitude=lng
        )
    
    async def _get_google_data(self, location: LocationData) -> Optional[Dict[str, Any]]:
        """Busca dados do Google Maps/Places API"""
        if not self.google_api_key:
            self.logger.warning("Google API Key não configurada")
            return None
        
        try:
            cache_key = f"google_{location.latitude}_{location.longitude}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached
            
            await self._rate_limit('google')
            
            # 1. Buscar Place ID
            place_id = await self._get_place_id(location)
            if not place_id:
                return None
            
            # 2. Buscar detalhes do lugar
            async with aiohttp.ClientSession() as session:
                url = f"https://maps.googleapis.com/maps/api/place/details/json"
                params = {
                    'place_id': place_id,
                    'fields': 'name,formatted_address,geometry,place_id,types,address_components,rating,user_ratings_total,photos',
                    'key': self.google_api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('result', {})
                        
                        # 3. Buscar lugares próximos (escolas, hospitais, etc.)
                        nearby_places = await self._get_nearby_places(location)
                        result['nearby_places'] = nearby_places
                        
                        self._set_cache(cache_key, result)
                        return result
                        
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados Google: {e}")
        
        return None
    
    async def _get_place_id(self, location: LocationData) -> Optional[str]:
        """Busca Place ID do Google"""
        try:
            async with aiohttp.ClientSession() as session:
                query = f"{location.address}, {location.neighborhood}, {location.city}"
                url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                params = {
                    'input': query,
                    'inputtype': 'textquery',
                    'fields': 'place_id',
                    'key': self.google_api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        candidates = data.get('candidates', [])
                        if candidates:
                            return candidates[0].get('place_id')
        except Exception as e:
            self.logger.debug(f"Erro ao buscar Place ID: {e}")
        
        return None
    
    async def _get_nearby_places(self, location: LocationData) -> Dict[str, List]:
        """Busca lugares próximos importantes"""
        nearby = {
            'schools': [],
            'hospitals': [],
            'shopping': [],
            'transportation': [],
            'banks': []
        }
        
        try:
            types_map = {
                'schools': 'school',
                'hospitals': 'hospital',
                'shopping': 'shopping_mall',
                'transportation': 'subway_station',
                'banks': 'bank'
            }
            
            async with aiohttp.ClientSession() as session:
                for category, place_type in types_map.items():
                    await self._rate_limit('google')
                    
                    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    params = {
                        'location': f"{location.latitude},{location.longitude}",
                        'radius': 2000,  # 2km
                        'type': place_type,
                        'key': self.google_api_key
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = data.get('results', [])[:5]  # Top 5
                            
                            for place in results:
                                nearby[category].append({
                                    'name': place.get('name'),
                                    'rating': place.get('rating'),
                                    'distance': self._calculate_distance(
                                        location.latitude, location.longitude,
                                        place['geometry']['location']['lat'],
                                        place['geometry']['location']['lng']
                                    )
                                })
        
        except Exception as e:
            self.logger.debug(f"Erro ao buscar lugares próximos: {e}")
        
        return nearby
    
    async def _get_cep_data(self, zipcode: str) -> Optional[Dict[str, Any]]:
        """Busca dados do CEP via ViaCEP"""
        if not zipcode or len(zipcode) != 8:
            return None
        
        try:
            cache_key = f"cep_{zipcode}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached
            
            await self._rate_limit('viacep')
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.cep_api_base}/{zipcode}/json/"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if not data.get('erro'):
                            self._set_cache(cache_key, data)
                            return data
                            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados CEP: {e}")
        
        return None
    
    async def _get_ibge_data(self, city: str, state: str) -> Optional[Dict[str, Any]]:
        """Busca dados do IBGE"""
        try:
            cache_key = f"ibge_{city}_{state}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached
            
            await self._rate_limit('ibge')
            
            async with aiohttp.ClientSession() as session:
                # 1. Buscar código do município
                city_url = f"{self.ibge_api_base}/localidades/municipios"
                async with session.get(city_url) as response:
                    if response.status == 200:
                        municipalities = await response.json()
                        city_code = None
                        muni = None
                        
                        for municipality in municipalities:
                            if (municipality['nome'].lower() == city.lower() and 
                                municipality['microrregiao']['mesorregiao']['UF']['sigla'].lower() == state.lower()):
                                city_code = municipality['id']
                                muni = municipality
                                break
                        
                        if not city_code or not muni:
                            return None
                        
                        # 2. Buscar dados demográficos e econômicos
                        ibge_data = {
                            'municipality_code': city_code,
                            'municipality_info': muni
                        }
                        
                        self._set_cache(cache_key, ibge_data)
                        return ibge_data
                        
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados IBGE: {e}")
        
        return None
    
    async def _get_municipal_data(self, location: LocationData) -> Optional[Dict[str, Any]]:
        """Busca dados da prefeitura (simulado - implementar APIs específicas)"""
        # Aqui implementaríamos integrações com APIs de prefeituras específicas
        # Como São Paulo, Rio de Janeiro, etc.
        
        try:
            # Exemplo de estrutura de dados municipais
            municipal_data = {
                'zoning': self._get_zoning_info(location),
                'iptu_reference': self._get_iptu_reference(location),
                'urban_planning': self._get_urban_planning(location),
                'public_services': self._get_public_services(location)
            }
            
            return municipal_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados municipais: {e}")
        
        return None
    
    async def _get_registry_data(self, location: LocationData) -> Optional[Dict[str, Any]]:
        """Busca dados de cartório/registro (simulado)"""
        # Implementar integração com cartórios quando APIs estiverem disponíveis
        
        try:
            # Estrutura simulada de dados de registro
            registry_data = {
                'registry_office': f"Cartório de {location.city}",
                'property_documentation': {
                    'status': 'regular',
                    'last_transaction': '2023-15-03',
                    'ownership_history': []
                },
                'liens_and_encumbrances': [],
                'legal_status': 'clear'
            }
            
            return registry_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados de registro: {e}")
        
        return None
    
    async def _get_market_data(self, location: LocationData) -> Optional[Dict[str, Any]]:
        """Busca dados de mercado imobiliário"""
        try:
            # Aqui implementaríamos integração com APIs de mercado imobiliário
            # Como FipeZap, Imovelweb, etc.
            
            market_data = {
                'average_price_per_sqm': self._estimate_price_per_sqm(location),
                'market_trend': 'stable',
                'comparable_properties': [],
                'investment_potential': self._calculate_investment_potential(location)
            }
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados de mercado: {e}")
        
        return None
    
    def _get_zoning_info(self, location: LocationData) -> Dict[str, Any]:
        """Informações de zoneamento"""
        # Simulado - implementar com APIs municipais
        return {
            'zone_type': 'residential',
            'building_restrictions': {
                'max_height': '15 floors',
                'occupation_rate': '50%',
                'building_rate': '4x'
            }
        }
    
    def _get_iptu_reference(self, location: LocationData) -> Dict[str, Any]:
        """Valor de referência do IPTU"""
        # Simulado - implementar com APIs da Receita Municipal
        return {
            'reference_value': 450000.00,
            'iptu_rate': 0.008,
            'estimated_iptu': 3600.00
        }
    
    def _get_urban_planning(self, location: LocationData) -> Dict[str, Any]:
        """Informações de planejamento urbano"""
        return {
            'planned_developments': [],
            'infrastructure_projects': [],
            'zoning_changes': []
        }
    
    def _get_public_services(self, location: LocationData) -> Dict[str, Any]:
        """Serviços públicos disponíveis"""
        return {
            'water_supply': 'municipal',
            'sewage_system': 'municipal',
            'electricity': 'available',
            'gas': 'available',
            'internet_coverage': 'fiber_available'
        }
    
    def _estimate_price_per_sqm(self, location: LocationData) -> float:
        """Estima preço por m² baseado na localização"""
        # Implementar lógica baseada em dados históricos
        base_price = 8000.0  # Preço base por m²
        
        # Ajustar baseado na cidade
        city_multipliers = {
            'são paulo': 1.5,
            'rio de janeiro': 1.3,
            'belo horizonte': 1.0,
            'brasília': 1.2
        }
        
        multiplier = city_multipliers.get(location.city.lower(), 1.0)
        return base_price * multiplier
    
    def _calculate_investment_potential(self, location: LocationData) -> Dict[str, Any]:
        """Calcula potencial de investimento"""
        return {
            'score': 7.5,
            'factors': {
                'location': 8.0,
                'infrastructure': 7.0,
                'growth_potential': 8.0,
                'liquidity': 7.0
            },
            'recommendation': 'buy'
        }
    
    async def _geocode_address(self, address: str) -> Tuple[float, float]:
        """Geocodifica endereço"""
        if not self.google_api_key:
            return 0.0, 0.0
        
        try:
            await self._rate_limit('google')
            
            async with aiohttp.ClientSession() as session:
                url = f"https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    'address': address,
                    'key': self.google_api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', [])
                        if results:
                            location = results[0]['geometry']['location']
                            return location['lat'], location['lng']
                            
        except Exception as e:
            self.logger.debug(f"Erro na geocodificação: {e}")
        
        return 0.0, 0.0
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcula distância entre duas coordenadas (km)"""
        import math
        
        R = 6371  # Raio da Terra em km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)
    
    def _calculate_confidence_score(self, enrichment_data: Dict[str, Any]) -> float:
        """Calcula score de confiabilidade dos dados"""
        score = 0.0
        max_score = 100.0
        
        # Google Data (30 pontos)
        if enrichment_data.get('google_data'):
            score += 30.0
        
        # CEP Data (20 pontos)
        if enrichment_data.get('cep_data'):
            score += 20.0
        
        # IBGE Data (15 pontos)
        if enrichment_data.get('ibge_data'):
            score += 15.0
        
        # Municipal Data (15 pontos)
        if enrichment_data.get('municipal_data'):
            score += 15.0
        
        # Registry Data (10 pontos)
        if enrichment_data.get('registry_data'):
            score += 10.0
        
        # Market Data (10 pontos)
        if enrichment_data.get('market_data'):
            score += 10.0
        
        return round(score / max_score, 2)
    
    async def _rate_limit(self, api_name: str):
        """Aplica rate limiting por API"""
        now = time.time()
        last_request = self.last_request_time.get(api_name, 0)
        
        if now - last_request < self.request_delay:
            await asyncio.sleep(self.request_delay - (now - last_request))
        
        self.last_request_time[api_name] = time.time()
    
    def _get_cache_key(self, key: str) -> str:
        """Gera chave de cache"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Recupera item do cache"""
        cache_key = self._get_cache_key(key)
        
        if cache_key in self.cache:
            item = self.cache[cache_key]
            if time.time() - item['timestamp'] < self.cache_ttl:
                return item['data']
            else:
                del self.cache[cache_key]
        
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Armazena item no cache"""
        cache_key = self._get_cache_key(key)
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

# Instância global do serviço
data_enrichment_service = DataEnrichmentService()

async def enrich_property_data(property_data: Dict[str, Any]) -> PropertyEnrichment:
    """Função helper para enriquecer dados de um imóvel"""
    return await data_enrichment_service.enrich_property(property_data)

async def enrich_property_batch(properties: List[Dict[str, Any]], max_concurrent: int = 5) -> List[PropertyEnrichment]:
    """Enriquece múltiplos imóveis em lote com controle de concorrência"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def enrich_with_limit(property_data):
        async with semaphore:
            return await enrich_property_data(property_data)
    
    tasks = [enrich_with_limit(prop) for prop in properties]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filtrar apenas resultados válidos
    valid_results = []
    for result in results:
        if not isinstance(result, Exception):
            valid_results.append(result)
    
    return valid_results
