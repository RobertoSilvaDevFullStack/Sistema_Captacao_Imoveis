# backend/api_integrations/ibge_integration.py
"""
Integração com APIs do IBGE (Instituto Brasileiro de Geografia e Estatística)
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
import time

class IBGEIntegration:
    """Cliente para APIs do IBGE"""
    
    def __init__(self):
        self.base_url = "https://servicodados.ibge.gov.br/api/v1"
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting - IBGE geralmente não tem limites rigorosos
        self.request_delay = 0.1  # 100ms entre requests
        self.last_request_time = 0
    
    async def get_states(self) -> List[Dict[str, Any]]:
        """Lista todos os estados"""
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/localidades/estados"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Erro ao buscar estados: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Erro na API IBGE (estados): {e}")
        
        return []
    
    async def get_municipalities(self, state_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lista municípios (opcionalmente filtrado por estado)"""
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                if state_id:
                    url = f"{self.base_url}/localidades/estados/{state_id}/municipios"
                else:
                    url = f"{self.base_url}/localidades/municipios"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Erro ao buscar municípios: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Erro na API IBGE (municípios): {e}")
        
        return []
    
    async def get_municipality_by_name(self, municipality_name: str, state_abbreviation: str) -> Optional[Dict[str, Any]]:
        """Busca município específico por nome e estado"""
        try:
            municipalities = await self.get_municipalities()
            
            for municipality in municipalities:
                if (municipality['nome'].lower() == municipality_name.lower() and
                    municipality['microrregiao']['mesorregiao']['UF']['sigla'].lower() == state_abbreviation.lower()):
                    return municipality
                    
        except Exception as e:
            self.logger.error(f"Erro ao buscar município por nome: {e}")
        
        return None
    
    async def get_districts(self, municipality_id: int) -> List[Dict[str, Any]]:
        """Lista distritos de um município"""
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/localidades/municipios/{municipality_id}/distritos"
                
                async with session.get(url, params={'orderBy': 'nome'}) as response:
                    if response.status == 200:
                        return await response.json()
                        
        except Exception as e:
            self.logger.error(f"Erro ao buscar distritos: {e}")
        
        return []
    
    async def get_census_data(self, municipality_id: int) -> Optional[Dict[str, Any]]:
        """Busca dados do censo para um município"""
        # O IBGE não tem uma API direta para dados do censo, mas podemos simular
        # com informações estruturadas baseadas no ID do município
        
        try:
            # Buscar informações básicas do município
            municipality = await self._get_municipality_details(municipality_id)
            if not municipality:
                return None
            
            # Simular dados censitários estruturados
            census_data = {
                'municipality_id': municipality_id,
                'municipality_name': municipality['nome'],
                'state': municipality['microrregiao']['mesorregiao']['UF']['nome'],
                'microregion': municipality['microrregiao']['nome'],
                'mesoregion': municipality['microrregiao']['mesorregiao']['nome'],
                'demographic_data': {
                    'estimated_population': self._estimate_population(municipality_id),
                    'population_density': self._estimate_density(municipality_id),
                    'urban_population_percent': self._estimate_urban_percent(municipality_id)
                },
                'economic_data': {
                    'gdp_per_capita': self._estimate_gdp_per_capita(municipality_id),
                    'main_economic_activities': self._get_main_activities(municipality_id),
                    'employment_rate': self._estimate_employment_rate(municipality_id)
                },
                'infrastructure_data': {
                    'water_supply_coverage': self._estimate_water_coverage(municipality_id),
                    'sewage_coverage': self._estimate_sewage_coverage(municipality_id),
                    'electricity_coverage': self._estimate_electricity_coverage(municipality_id)
                }
            }
            
            return census_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados censitários: {e}")
        
        return None
    
    async def _get_municipality_details(self, municipality_id: int) -> Optional[Dict[str, Any]]:
        """Busca detalhes de um município específico"""
        try:
            await self._rate_limit()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/localidades/municipios/{municipality_id}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                        
        except Exception as e:
            self.logger.error(f"Erro ao buscar detalhes do município: {e}")
        
        return None
    
    def _estimate_population(self, municipality_id: int) -> int:
        """Estima população baseada no ID (simulado)"""
        # Em implementação real, usar dados reais do IBGE
        base_population = 50000
        return base_population + (municipality_id % 1000000)
    
    def _estimate_density(self, municipality_id: int) -> float:
        """Estima densidade populacional"""
        return round(100 + (municipality_id % 500), 2)
    
    def _estimate_urban_percent(self, municipality_id: int) -> float:
        """Estima percentual urbano"""
        return round(60 + (municipality_id % 40), 1)
    
    def _estimate_gdp_per_capita(self, municipality_id: int) -> float:
        """Estima PIB per capita"""
        return round(15000 + (municipality_id % 20000), 2)
    
    def _get_main_activities(self, municipality_id: int) -> List[str]:
        """Retorna principais atividades econômicas"""
        activities_map = {
            0: ['Agropecuária', 'Serviços'],
            1: ['Indústria', 'Comércio'],
            2: ['Serviços', 'Turismo'],
            3: ['Agropecuária', 'Indústria'],
            4: ['Comércio', 'Serviços']
        }
        return activities_map[municipality_id % 5]
    
    def _estimate_employment_rate(self, municipality_id: int) -> float:
        """Estima taxa de emprego"""
        return round(70 + (municipality_id % 20), 1)
    
    def _estimate_water_coverage(self, municipality_id: int) -> float:
        """Estima cobertura de água"""
        return round(80 + (municipality_id % 20), 1)
    
    def _estimate_sewage_coverage(self, municipality_id: int) -> float:
        """Estima cobertura de esgoto"""
        return round(60 + (municipality_id % 35), 1)
    
    def _estimate_electricity_coverage(self, municipality_id: int) -> float:
        """Estima cobertura elétrica"""
        return round(95 + (municipality_id % 5), 1)
    
    async def get_geographic_info(self, municipality_id: int) -> Optional[Dict[str, Any]]:
        """Busca informações geográficas"""
        try:
            municipality = await self._get_municipality_details(municipality_id)
            if not municipality:
                return None
            
            geographic_info = {
                'municipality_id': municipality_id,
                'region': municipality['microrregiao']['mesorregiao']['UF']['regiao']['nome'],
                'state_code': municipality['microrregiao']['mesorregiao']['UF']['sigla'],
                'state_name': municipality['microrregiao']['mesorregiao']['UF']['nome'],
                'microregion': municipality['microrregiao']['nome'],
                'mesoregion': municipality['microrregiao']['mesorregiao']['nome'],
                'climate_info': self._get_climate_info(municipality_id),
                'biome': self._get_biome(municipality_id),
                'area_km2': self._estimate_area(municipality_id)
            }
            
            return geographic_info
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar informações geográficas: {e}")
        
        return None
    
    def _get_climate_info(self, municipality_id: int) -> Dict[str, Any]:
        """Informações climáticas estimadas"""
        climate_types = [
            {'type': 'Tropical', 'temperature_avg': 25, 'humidity_avg': 75},
            {'type': 'Subtropical', 'temperature_avg': 20, 'humidity_avg': 70},
            {'type': 'Semiárido', 'temperature_avg': 28, 'humidity_avg': 50},
            {'type': 'Temperado', 'temperature_avg': 18, 'humidity_avg': 65}
        ]
        return climate_types[municipality_id % 4]
    
    def _get_biome(self, municipality_id: int) -> str:
        """Bioma estimado"""
        biomes = ['Mata Atlântica', 'Cerrado', 'Caatinga', 'Amazônia', 'Pampa', 'Pantanal']
        return biomes[municipality_id % 6]
    
    def _estimate_area(self, municipality_id: int) -> float:
        """Estima área do município"""
        return round(100 + (municipality_id % 2000), 2)
    
    async def get_postal_codes(self, municipality_id: int) -> List[str]:
        """Busca CEPs de um município (simulado)"""
        # Em implementação real, integrar com Correios
        try:
            municipality = await self._get_municipality_details(municipality_id)
            if not municipality:
                return []
            
            # Gerar CEPs simulados baseados no município
            base_cep = 10000 + (municipality_id % 90000)
            postal_codes = []
            
            for i in range(5):  # 5 CEPs exemplo
                cep = f"{base_cep + i:05d}-{(municipality_id % 899) + 100:03d}"
                postal_codes.append(cep)
            
            return postal_codes
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar CEPs: {e}")
        
        return []
    
    async def get_complete_location_data(self, city_name: str, state_abbreviation: str) -> Optional[Dict[str, Any]]:
        """Busca dados completos de uma localização"""
        try:
            # 1. Buscar município
            municipality = await self.get_municipality_by_name(city_name, state_abbreviation)
            if not municipality:
                return None
            
            municipality_id = municipality['id']
            
            # 2. Buscar dados em paralelo
            tasks = [
                self.get_districts(municipality_id),
                self.get_census_data(municipality_id),
                self.get_geographic_info(municipality_id),
                self.get_postal_codes(municipality_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 3. Compilar resultado
            complete_data = {
                'municipality': municipality,
                'districts': results[0] if not isinstance(results[0], Exception) else [],
                'census_data': results[1] if not isinstance(results[1], Exception) else None,
                'geographic_info': results[2] if not isinstance(results[2], Exception) else None,
                'postal_codes': results[3] if not isinstance(results[3], Exception) else []
            }
            
            return complete_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados completos: {e}")
        
        return None
    
    async def _rate_limit(self):
        """Aplica rate limiting"""
        now = time.time()
        
        if now - self.last_request_time < self.request_delay:
            await asyncio.sleep(self.request_delay - (now - self.last_request_time))
        
        self.last_request_time = time.time()
