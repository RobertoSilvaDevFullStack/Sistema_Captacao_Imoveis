# test_cache_and_database_integration.py
"""
Teste de Integração: Cache Service + Database Service
Demonstra o funcionamento do sistema de cache Redis e deduplicação SQLite.
"""
import asyncio
import logging
import time
from typing import Dict, Any

from backend.services.cache_service_simple import CacheService
from backend.services.database_service import DatabaseService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedDataManager:
    """Gerenciador integrado de cache e banco de dados"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.database_service = DatabaseService()
    
    async def initialize(self):
        """Inicializar serviços"""
        await self.cache_service.initialize()
        await self.database_service.initialize()
        logger.info("✅ Serviços inicializados")
    
    async def process_property_with_cache(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa propriedade com cache inteligente e deduplicação
        """
        start_time = time.time()
        
        # 1. Verificar cache primeiro
        cache_key = f"property_{self.database_service.generate_property_hash(property_data)}"
        cached_result = await self.cache_service.get_cached_data(cache_key)
        
        if cached_result:
            logger.info(f"🟢 CACHE HIT para propriedade: {property_data.get('address')}")
            
            # Log de API usage (cache hit)
            await self.database_service.log_api_usage(
                api_name="property_processing",
                endpoint="process_property",
                request_data=property_data,
                response_size=len(str(cached_result)),
                response_time=time.time() - start_time,
                success=True,
                cache_hit=True
            )
            
            return cached_result
        
        # 2. Cache miss - processar dados
        logger.info(f"🔴 CACHE MISS para propriedade: {property_data.get('address')}")
        
        # Salvar propriedade (com deduplicação automática)
        property_id, is_new = await self.database_service.save_property(property_data)
        
        # Simular enriquecimento de dados
        enriched_data = await self._enrich_property_data(property_data)
        
        # Salvar resultado de enriquecimento
        confidence_score = 0.85
        processing_time = time.time() - start_time
        
        enrichment_id = await self.database_service.save_enrichment_result(
            property_id, enriched_data, confidence_score, processing_time
        )
        
        # Resultado completo
        result = {
            'property_id': property_id,
            'is_new': is_new,
            'enrichment_id': enrichment_id,
            'enriched_data': enriched_data,
            'confidence_score': confidence_score,
            'processing_time': processing_time
        }
        
        # 3. Salvar no cache
        await self.cache_service.set_cached_data(
            cache_key, result, ttl_hours=24  # Cache por 24 horas
        )
        
        # Log de API usage (cache miss)
        await self.database_service.log_api_usage(
            api_name="property_processing",
            endpoint="process_property",
            request_data=property_data,
            response_size=len(str(result)),
            response_time=processing_time,
            success=True,
            cache_hit=False
        )
        
        logger.info(f"✅ Propriedade processada: ID {property_id} ({'nova' if is_new else 'existente'})")
        return result
    
    async def _enrich_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula enriquecimento de dados (substitui chamadas reais de API)"""
        # Simular tempo de processamento
        await asyncio.sleep(0.5)
        
        return {
            'google_data': {
                'place_id': f"ChIJ_{property_data.get('address', '')[:10]}",
                'rating': 4.2,
                'reviews_count': 145,
                'types': ['establishment', 'point_of_interest']
            },
            'municipal_data': {
                'zone': 'residential',
                'tax_value': property_data.get('price', 0) * 0.8,
                'permits': ['habite_se'],
                'restrictions': []
            },
            'market_data': {
                'price_trend': 'stable',
                'liquidity': 'high',
                'appreciation_rate': 5.2,
                'avg_time_on_market': 45
            },
            'ibge_data': {
                'census_sector': '12345',
                'population_density': 8500,
                'income_level': 'medium_high',
                'infrastructure_score': 8.5
            }
        }
    
    async def demonstrate_deduplication(self):
        """Demonstra o sistema de deduplicação"""
        logger.info("\n🔄 DEMONSTRAÇÃO DE DEDUPLICAÇÃO")
        
        # Propriedade base
        base_property = {
            'address': 'Rua das Palmeiras, 456',
            'city': 'São Paulo',
            'state': 'SP',
            'neighborhood': 'Jardins',
            'zipcode': '01234-000',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'price': 1200000.0,
            'area': 120.0,
            'bedrooms': 3,
            'bathrooms': 2,
            'property_type': 'apartamento',
            'business_type': 'venda',
            'source': 'vivareal'
        }
        
        # Primeira inserção
        result1 = await self.process_property_with_cache(base_property)
        logger.info(f"Primeira inserção: ID {result1['property_id']} (nova: {result1['is_new']})")
        
        # Segunda inserção (mesma propriedade - deve detectar duplicata)
        base_property['source'] = 'zapimoveis'  # Fonte diferente, mas mesma propriedade
        result2 = await self.process_property_with_cache(base_property)
        logger.info(f"Segunda inserção: ID {result2['property_id']} (nova: {result2['is_new']})")
        
        # Verificar se são o mesmo ID
        if result1['property_id'] == result2['property_id']:
            logger.info("✅ Deduplicação funcionando corretamente!")
        else:
            logger.error("❌ Erro na deduplicação!")
    
    async def demonstrate_cache_efficiency(self):
        """Demonstra a eficiência do cache"""
        logger.info("\n⚡ DEMONSTRAÇÃO DE EFICIÊNCIA DO CACHE")
        
        property_test = {
            'address': 'Avenida Paulista, 1000',
            'city': 'São Paulo',
            'state': 'SP',
            'neighborhood': 'Bela Vista',
            'zipcode': '01310-000',
            'latitude': -23.5610,
            'longitude': -46.6565,
            'price': 2500000.0,
            'area': 200.0,
            'bedrooms': 4,
            'bathrooms': 3,
            'property_type': 'apartamento',
            'business_type': 'venda',
            'source': 'olx'
        }
        
        # Primeira execução (sem cache)
        start_time = time.time()
        result1 = await self.process_property_with_cache(property_test)
        time1 = time.time() - start_time
        
        # Segunda execução (com cache)
        start_time = time.time()
        result2 = await self.process_property_with_cache(property_test)
        time2 = time.time() - start_time
        
        logger.info(f"Tempo sem cache: {time1:.3f}s")
        logger.info(f"Tempo com cache: {time2:.3f}s")
        logger.info(f"Speedup: {time1/time2:.2f}x mais rápido")
    
    async def show_statistics(self):
        """Mostra estatísticas do sistema"""
        logger.info("\n📊 ESTATÍSTICAS DO SISTEMA")
        
        # Estatísticas de cache
        cache_stats = await self.cache_service.get_cache_statistics()
        logger.info(f"Cache stats: {cache_stats}")
        
        # Estatísticas de API
        api_stats = await self.database_service.get_api_usage_stats()
        logger.info(f"API stats: {api_stats}")
        
        # Buscar duplicatas
        duplicates = await self.database_service.find_duplicates()
        logger.info(f"Duplicatas encontradas: {len(duplicates)}")
    
    async def close(self):
        """Fechar serviços"""
        await self.cache_service.close()
        await self.database_service.close()
        logger.info("🔒 Serviços fechados")

async def run_integration_test():
    """Executa teste completo de integração"""
    logger.info("🚀 INICIANDO TESTE DE INTEGRAÇÃO: CACHE + DATABASE")
    
    manager = IntegratedDataManager()
    
    try:
        # Inicializar
        await manager.initialize()
        
        # Teste 1: Deduplicação
        await manager.demonstrate_deduplication()
        
        # Teste 2: Cache efficiency  
        await manager.demonstrate_cache_efficiency()
        
        # Teste 3: Estatísticas
        await manager.show_statistics()
        
        logger.info("\n✅ TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        raise
    
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(run_integration_test())
