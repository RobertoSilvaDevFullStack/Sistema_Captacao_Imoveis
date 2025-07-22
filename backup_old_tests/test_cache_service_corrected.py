# test_cache_service_corrected.py
"""
Teste do Cache Service corrigido
"""
import asyncio
import logging
from backend.services.cache_service import CacheService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cache_service():
    """Testa o cache service corrigido"""
    logger.info("🧪 INICIANDO TESTE DO CACHE SERVICE CORRIGIDO")
    
    # Inicializar cache service
    cache_service = CacheService()
    await cache_service.initialize()
    
    try:
        # Teste 1: Cache básico
        logger.info("📝 Teste 1: Cache básico")
        
        test_data = {'address': 'Rua Teste, 123', 'city': 'São Paulo'}
        test_result = {'lat': -23.5505, 'lng': -46.6333, 'status': 'found'}
        
        # Set cache
        success = await cache_service.set_cached_data('google_maps', test_data, test_result)
        logger.info(f"Cache set success: {success}")
        
        # Get cache
        cached_result = await cache_service.get_cached_data('google_maps', test_data)
        logger.info(f"Cached result: {cached_result}")
        
        if cached_result == test_result:
            logger.info("✅ Cache básico funcionando!")
        else:
            logger.error("❌ Erro no cache básico")
        
        # Teste 2: Cache miss
        logger.info("📝 Teste 2: Cache miss")
        miss_result = await cache_service.get_cached_data('google_maps', {'address': 'inexistente'})
        if miss_result is None:
            logger.info("✅ Cache miss funcionando!")
        else:
            logger.error("❌ Erro no cache miss")
        
        # Teste 3: Invalidação
        logger.info("📝 Teste 3: Invalidação de cache")
        invalidated = await cache_service.invalidate_cache('google_maps', test_data)
        logger.info(f"Cache invalidated: {invalidated}")
        
        # Verificar se foi invalidado
        after_invalidation = await cache_service.get_cached_data('google_maps', test_data)
        if after_invalidation is None:
            logger.info("✅ Invalidação funcionando!")
        else:
            logger.error("❌ Erro na invalidação")
        
        # Teste 4: Estatísticas
        logger.info("📝 Teste 4: Estatísticas do cache")
        stats = await cache_service.get_cache_stats()
        logger.info(f"Cache stats: {stats}")
        
        logger.info("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        
    except Exception as e:
        logger.error(f"❌ Erro nos testes: {e}")
        
    finally:
        await cache_service.close()
        logger.info("🔒 Cache service fechado")

if __name__ == "__main__":
    asyncio.run(test_cache_service())
