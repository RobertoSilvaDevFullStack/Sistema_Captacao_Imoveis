# backend/api_integrations/market_data_apis.py
"""
Integração com APIs de Dados de Mercado Imobiliário
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import time
import statistics

class MarketDataAPIs:
    """Cliente para APIs de dados de mercado imobiliário"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # URLs de APIs de mercado (algumas são fictícias para demonstração)
        self.market_apis = {
            'fipe_zap': {
                'url': 'https://www.zapimoveis.com.br/fipe-zap',
                'description': 'Índice FipeZAP'
            },
            'imovelweb': {
                'url': 'https://www.imovelweb.com.br/api',
                'description': 'Dados ImovelWeb'
            },
            'loft': {
                'url': 'https://loft.com.br/api',
                'description': 'Dados Loft'
            },
            'quintoandar': {
                'url': 'https://quintoandar.com.br/api',
                'description': 'Dados QuintoAndar'
            },
            'vivareal': {
                'url': 'https://vivareal.com.br/api',
                'description': 'Dados VivaReal'
            }
        }
        
        self.request_delay = 0.5  # 500ms entre requests
        self.last_request_time = {}
    
    async def get_market_price_analysis(self, address: str, city: str, property_type: str, 
                                      area_m2: float, bedrooms: int) -> Dict[str, Any]:
        """Análise de preços de mercado"""
        try:
            await self._rate_limit('market_analysis')
            
            # Buscar dados de diferentes fontes em paralelo
            tasks = [
                self._get_fipe_zap_data(city, property_type),
                self._get_comparable_properties(address, city, property_type, area_m2, bedrooms),
                self._get_price_trends(city, property_type),
                self._get_rental_yields(city, property_type),
                self._get_market_indicators(city)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Processar resultados com type checking adequado
            fipe_data_raw = results[0] if not isinstance(results[0], Exception) else None
            comparables = results[1] if not isinstance(results[1], Exception) else []
            trends = results[2] if not isinstance(results[2], Exception) else None
            yields = results[3] if not isinstance(results[3], Exception) else None
            indicators = results[4] if not isinstance(results[4], Exception) else None
            
            # Garantir que comparables é uma lista
            if not isinstance(comparables, list):
                comparables = []
            
            # Garantir que fipe_data é dict ou None
            fipe_data: Optional[Dict[str, Any]] = None
            if fipe_data_raw is not None and isinstance(fipe_data_raw, dict):
                fipe_data = fipe_data_raw
            
            # Calcular estimativa de preço
            price_estimate = self._calculate_price_estimate(
                area_m2, bedrooms, city, property_type, comparables, fipe_data
            )
            
            # Compilar análise
            market_analysis = {
                'price_estimate': price_estimate,
                'fipe_zap_index': fipe_data,
                'comparable_properties': comparables[:10],  # Top 10
                'price_trends': trends,
                'rental_analysis': yields,
                'market_indicators': indicators,
                'confidence_level': self._calculate_confidence_level(len(comparables), fipe_data),
                'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return market_analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise de mercado: {e}")
        
        return {}
    
    async def _get_fipe_zap_data(self, city: str, property_type: str) -> Optional[Dict[str, Any]]:
        """Busca dados do índice FipeZAP"""
        try:
            await self._rate_limit('fipe_zap')
            
            # Simular dados do FipeZAP baseados na cidade
            city_multipliers = {
                'são paulo': 1.5,
                'rio de janeiro': 1.3,
                'belo horizonte': 0.8,
                'brasília': 1.1,
                'salvador': 0.7,
                'fortaleza': 0.6,
                'recife': 0.7,
                'porto alegre': 0.9,
                'curitiba': 1.0,
                'goiânia': 0.6
            }
            
            base_price_sqm = 8000.0  # Preço base por m²
            multiplier = city_multipliers.get(city.lower(), 0.8)
            
            # Ajustar por tipo de imóvel
            type_multipliers = {
                'apartamento': 1.0,
                'casa': 0.9,
                'cobertura': 1.3,
                'studio': 1.1,
                'loft': 1.2
            }
            
            type_mult = type_multipliers.get(property_type.lower(), 1.0)
            current_price = base_price_sqm * multiplier * type_mult
            
            fipe_data = {
                'city': city,
                'property_type': property_type,
                'price_per_sqm': round(current_price, 2),
                'index_value': round(100 * multiplier * type_mult, 2),
                'monthly_variation': round(-0.5 + (hash(city) % 20) / 10, 2),  # -0.5% a +1.5%
                'yearly_variation': round(2 + (hash(city) % 80) / 10, 2),  # 2% a 10%
                'reference_period': time.strftime('%Y-%m'),
                'data_source': 'FipeZAP'
            }
            
            return fipe_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados FipeZAP: {e}")
        
        return None
    
    async def _get_comparable_properties(self, address: str, city: str, property_type: str,
                                       area_m2: float, bedrooms: int) -> List[Dict[str, Any]]:
        """Busca imóveis comparáveis"""
        try:
            await self._rate_limit('comparables')
            
            comparables = []
            
            # Gerar 15-25 imóveis comparáveis simulados
            num_comparables = 15 + (hash(address) % 11)
            
            for i in range(num_comparables):
                comparable = self._generate_comparable_property(
                    address, city, property_type, area_m2, bedrooms, i
                )
                comparables.append(comparable)
            
            # Ordenar por similaridade (baseado na diferença de área e quartos)
            comparables.sort(key=lambda x: (
                abs(x['area_m2'] - area_m2) + 
                abs(x['bedrooms'] - bedrooms) * 10
            ))
            
            return comparables
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar comparáveis: {e}")
        
        return []
    
    def _generate_comparable_property(self, address: str, city: str, property_type: str,
                                    area_m2: float, bedrooms: int, index: int) -> Dict[str, Any]:
        """Gera imóvel comparável simulado"""
        prop_hash = hash(address + str(index))
        
        # Variar área em ±30%
        area_variation = 0.7 + (prop_hash % 60) / 100  # 0.7 a 1.3
        comp_area = round(area_m2 * area_variation, 1)
        
        # Variar quartos em ±2
        bedrooms_variation = -2 + (prop_hash % 5)
        comp_bedrooms = max(1, bedrooms + bedrooms_variation)
        
        # Calcular preço baseado na cidade e características
        base_price_sqm = self._get_base_price_sqm(city, property_type)
        price_variation = 0.8 + (prop_hash % 40) / 100  # ±20%
        price_per_sqm = base_price_sqm * price_variation
        total_price = comp_area * price_per_sqm
        
        comparable = {
            'id': f"COMP{prop_hash % 1000000:06d}",
            'address': self._generate_comparable_address(city, index),
            'property_type': property_type,
            'area_m2': comp_area,
            'bedrooms': comp_bedrooms,
            'bathrooms': max(1, comp_bedrooms - 1 + (prop_hash % 3)),
            'parking_spaces': (prop_hash % 3),
            'floor': 1 + (prop_hash % 20) if property_type == 'apartamento' else 0,
            'age_years': prop_hash % 30,
            'price': round(total_price, 2),
            'price_per_sqm': round(price_per_sqm, 2),
            'listing_date': f"2024-{(prop_hash % 12) + 1:02d}-{(prop_hash % 28) + 1:02d}",
            'source': self._get_random_source(index),
            'status': self._get_listing_status(prop_hash),
            'distance_km': round(0.1 + (prop_hash % 50) / 10, 1),  # 0.1 a 5.0 km
            'similarity_score': round(0.7 + (prop_hash % 30) / 100, 2)  # 0.7 a 1.0
        }
        
        return comparable
    
    async def _get_price_trends(self, city: str, property_type: str) -> Optional[Dict[str, Any]]:
        """Busca tendências de preços"""
        try:
            await self._rate_limit('price_trends')
            
            # Simular tendências baseadas na cidade
            city_hash = hash(city)
            
            # Gerar dados históricos dos últimos 24 meses
            monthly_data = []
            base_index = 100.0
            
            for i in range(24):
                # Simular flutuação mensal
                month_variation = -2 + (city_hash + i) % 5  # -2% a +3%
                base_index *= (1 + month_variation / 100)
                
                month_data = {
                    'period': f"2022-{((i % 12) + 1):02d}" if i < 12 else f"2023-{((i % 12) + 1):02d}",
                    'index': round(base_index, 2),
                    'variation_percent': round(month_variation, 2)
                }
                monthly_data.append(month_data)
            
            trends = {
                'city': city,
                'property_type': property_type,
                'monthly_data': monthly_data,
                'trend_direction': 'up' if base_index > 100 else 'down',
                'total_variation_24m': round(((base_index - 100) / 100) * 100, 2),
                'average_monthly_variation': round(sum(d['variation_percent'] for d in monthly_data) / 24, 2),
                'volatility': round(statistics.stdev([d['variation_percent'] for d in monthly_data]), 2)
            }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar tendências: {e}")
        
        return None
    
    async def _get_rental_yields(self, city: str, property_type: str) -> Optional[Dict[str, Any]]:
        """Busca dados de rentabilidade de aluguel"""
        try:
            await self._rate_limit('rental_yields')
            
            # Simular dados de aluguel baseados na cidade
            city_yields = {
                'são paulo': {'min': 0.3, 'max': 0.6},
                'rio de janeiro': {'min': 0.4, 'max': 0.7},
                'belo horizonte': {'min': 0.5, 'max': 0.8},
                'brasília': {'min': 0.4, 'max': 0.7},
                'salvador': {'min': 0.6, 'max': 0.9},
                'fortaleza': {'min': 0.7, 'max': 1.0}
            }
            
            yield_range = city_yields.get(city.lower(), {'min': 0.5, 'max': 0.8})
            city_hash = hash(city + property_type)
            
            # Calcular yield médio
            avg_yield = yield_range['min'] + (city_hash % 100) / 100 * (yield_range['max'] - yield_range['min'])
            
            rental_data = {
                'city': city,
                'property_type': property_type,
                'average_yield_percent': round(avg_yield, 2),
                'min_yield_percent': yield_range['min'],
                'max_yield_percent': yield_range['max'],
                'rental_price_growth_12m': round(5 + (city_hash % 60) / 10, 1),  # 5% a 11%
                'vacancy_rate_percent': round(3 + (city_hash % 70) / 10, 1),  # 3% a 10%
                'average_rental_period_months': 12 + (city_hash % 24),  # 12 a 36 meses
                'rental_market_status': self._get_rental_market_status(avg_yield)
            }
            
            return rental_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados de aluguel: {e}")
        
        return None
    
    async def _get_market_indicators(self, city: str) -> Optional[Dict[str, Any]]:
        """Busca indicadores gerais de mercado"""
        try:
            await self._rate_limit('market_indicators')
            
            city_hash = hash(city)
            
            indicators = {
                'city': city,
                'market_temperature': self._get_market_temperature(city_hash),
                'supply_demand_ratio': round(0.8 + (city_hash % 40) / 100, 2),  # 0.8 a 1.2
                'average_time_to_sell_days': 60 + (city_hash % 120),  # 60 a 180 dias
                'price_per_sqm_growth_12m': round(-5 + (city_hash % 200) / 10, 1),  # -5% a +15%
                'new_launches_last_quarter': 50 + (city_hash % 200),  # 50 a 250
                'financing_conditions': {
                    'average_interest_rate': round(8 + (city_hash % 40) / 10, 2),  # 8% a 12%
                    'max_financing_percent': 80 if city_hash % 2 else 90,
                    'average_approval_time_days': 15 + (city_hash % 30)
                },
                'economic_indicators': {
                    'unemployment_rate': round(8 + (city_hash % 60) / 10, 1),  # 8% a 14%
                    'average_income': 3000 + (city_hash % 5000),  # R$ 3000 a R$ 8000
                    'cost_of_living_index': round(100 + (city_hash % 500) / 10, 1)  # 100 a 150
                }
            }
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar indicadores: {e}")
        
        return None
    
    def _calculate_price_estimate(self, area_m2: float, bedrooms: int, city: str, 
                                property_type: str, comparables: List[Dict[str, Any]], 
                                fipe_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estimativa de preço"""
        
        # Método 1: Média dos comparáveis (peso 60%)
        if comparables:
            comparable_prices = [comp['price_per_sqm'] for comp in comparables[:5]]
            avg_comp_price_sqm = statistics.mean(comparable_prices)
            comp_estimate = avg_comp_price_sqm * area_m2
        else:
            comp_estimate = None
        
        # Método 2: FipeZAP (peso 30%)
        if fipe_data:
            fipe_estimate = fipe_data['price_per_sqm'] * area_m2
        else:
            fipe_estimate = None
        
        # Método 3: Modelo interno (peso 10%)
        base_price_sqm = self._get_base_price_sqm(city, property_type)
        internal_estimate = base_price_sqm * area_m2
        
        # Calcular estimativa final
        estimates = []
        weights = []
        
        if comp_estimate:
            estimates.append(comp_estimate)
            weights.append(0.6)
        
        if fipe_estimate:
            estimates.append(fipe_estimate)
            weights.append(0.3)
        
        estimates.append(internal_estimate)
        weights.append(0.1)
        
        # Normalizar pesos
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Calcular média ponderada
        final_estimate = sum(est * weight for est, weight in zip(estimates, weights))
        
        # Calcular faixas
        margin = 0.15  # ±15%
        min_estimate = final_estimate * (1 - margin)
        max_estimate = final_estimate * (1 + margin)
        
        price_estimate = {
            'estimated_price': round(final_estimate, 2),
            'price_per_sqm': round(final_estimate / area_m2, 2),
            'confidence_range': {
                'min': round(min_estimate, 2),
                'max': round(max_estimate, 2)
            },
            'methodology': {
                'comparable_properties': len(comparables),
                'fipe_zap_used': fipe_data is not None,
                'internal_model_used': True
            },
            'price_breakdown': {
                'comparable_estimate': comp_estimate,
                'fipe_estimate': fipe_estimate,
                'internal_estimate': internal_estimate,
                'final_estimate': final_estimate
            }
        }
        
        return price_estimate
    
    def _calculate_confidence_level(self, num_comparables: int, fipe_data: Optional[Dict[str, Any]]) -> float:
        """Calcula nível de confiança da análise"""
        confidence = 0.5  # Base 50%
        
        # Adicionar confiança baseado no número de comparáveis
        if num_comparables >= 10:
            confidence += 0.3
        elif num_comparables >= 5:
            confidence += 0.2
        elif num_comparables >= 3:
            confidence += 0.1
        
        # Adicionar confiança se tem dados FipeZAP
        if fipe_data:
            confidence += 0.2
        
        return min(confidence, 0.95)  # Máximo 95%
    
    def _get_base_price_sqm(self, city: str, property_type: str) -> float:
        """Preço base por m² por cidade e tipo"""
        city_prices = {
            'são paulo': 12000,
            'rio de janeiro': 10000,
            'belo horizonte': 6500,
            'brasília': 8500,
            'salvador': 5500,
            'fortaleza': 4500,
            'recife': 5000,
            'porto alegre': 7000,
            'curitiba': 8000,
            'goiânia': 4800
        }
        
        base_price = city_prices.get(city.lower(), 6000)
        
        # Ajustar por tipo
        type_multipliers = {
            'apartamento': 1.0,
            'casa': 0.85,
            'cobertura': 1.4,
            'studio': 1.1,
            'loft': 1.2
        }
        
        multiplier = type_multipliers.get(property_type.lower(), 1.0)
        return base_price * multiplier
    
    def _generate_comparable_address(self, city: str, index: int) -> str:
        """Gera endereço para imóvel comparável"""
        streets = [
            'Rua das Flores', 'Av. Principal', 'Rua do Comércio', 'Av. Central',
            'Rua São João', 'Av. Paulista', 'Rua Augusta', 'Rua da Consolação'
        ]
        
        street = streets[index % len(streets)]
        number = 100 + (index * 50)
        
        return f"{street}, {number} - {city}"
    
    def _get_random_source(self, index: int) -> str:
        """Fonte aleatória do anúncio"""
        sources = ['ZapImóveis', 'VivaReal', 'OLX', 'QuintoAndar', 'Loft', 'ImovelWeb']
        return sources[index % len(sources)]
    
    def _get_listing_status(self, prop_hash: int) -> str:
        """Status do anúncio"""
        statuses = ['active', 'sold', 'rented', 'suspended']
        weights = [70, 20, 5, 5]  # 70% ativo, 20% vendido, etc.
        
        hash_mod = prop_hash % 100
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if hash_mod < cumulative:
                return statuses[i]
        
        return 'active'
    
    def _get_market_temperature(self, city_hash: int) -> str:
        """Temperatura do mercado"""
        temperatures = ['frio', 'morno', 'aquecido', 'muito_aquecido']
        return temperatures[city_hash % len(temperatures)]
    
    def _get_rental_market_status(self, avg_yield: float) -> str:
        """Status do mercado de aluguel"""
        if avg_yield >= 0.7:
            return 'excelente'
        elif avg_yield >= 0.5:
            return 'bom'
        elif avg_yield >= 0.3:
            return 'regular'
        else:
            return 'baixo'
    
    async def _rate_limit(self, operation: str):
        """Aplica rate limiting por operação"""
        now = time.time()
        last_request = self.last_request_time.get(operation, 0)
        
        if now - last_request < self.request_delay:
            await asyncio.sleep(self.request_delay - (now - last_request))
        
        self.last_request_time[operation] = time.time()
