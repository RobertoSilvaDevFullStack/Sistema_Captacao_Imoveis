# backend/services/cache_service.py
"""
Serviço de Cache Redis para APIs e Resultados de Enriquecimento
"""
import redis.asyncio as redis
import json
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pickle
import asyncio
from dataclasses import asdict

class CacheService:
    """Serviço de cache Redis para otimização de APIs"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.logger = logging.getLogger(__name__)
        
        # Configurações de TTL (Time To Live) por tipo de dados
        self.ttl_config = {
            # APIs externas - cache mais longo
            'google_maps': 86400 * 7,     # 7 dias
            'ibge_data': 86400 * 30,      # 30 dias (dados raramente mudam)
            'cep_data': 86400 * 30,       # 30 dias
            
            # Dados municipais - cache médio
            'municipal_data': 86400 * 7,  # 7 dias
            'registry_data': 86400 * 3,   # 3 dias
            
            # Dados de mercado - cache curto (preços mudam)
            'market_data': 86400 * 1,     # 1 dia
            'price_analysis': 3600 * 6,   # 6 horas
            
            # Resultados completos de enriquecimento
            'enrichment_full': 86400 * 1, # 1 dia
            'enrichment_summary': 3600 * 2, # 2 horas
            
            # Cache de fallback para rate limiting
            'rate_limit': 300,            # 5 minutos
            'api_error': 1800             # 30 minutos
        }
        
        # Prefixos para organização no Redis
        self.prefixes = {
            'api': 'api:',
            'enrichment': 'enrich:',
            'geocoding': 'geo:',
            'analysis': 'analysis:',
            'dedup': 'dedup:',
            'stats': 'stats:'
        }
        
        # Conexões Redis
        self.redis_sync = None
        self.redis_async = None
        
    async def initialize(self):
        """Inicializa conexões Redis"""
        try:
            # Conexão síncrona para operações simples
            self.redis_sync = redis.Redis.from_url(self.redis_url, decode_responses=True)
            
            # Conexão assíncrona para operações em paralelo
            self.redis_async = redis.from_url(self.redis_url, decode_responses=True)
            
            # Testar conexões
            await self.redis_async.ping()
            await self.redis_sync.ping()
            
            self.logger.info("✅ Conexões Redis estabelecidas com sucesso")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Redis não disponível: {e}. Cache desabilitado.")
            self.redis_sync = None
            self.redis_async = None
    
    def _generate_cache_key(self, prefix: str, data: Union[str, Dict[str, Any]]) -> str:
        """Gera chave única para cache"""
        if isinstance(data, dict):
            # Ordenar chaves para garantir consistência
            normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        else:
            normalized = str(data)
        
        # Hash para chave compacta
        hash_key = hashlib.md5(normalized.encode('utf-8')).hexdigest()
        return f"{self.prefixes.get(prefix, prefix)}{hash_key}"
    
    async def get_cached_data(self, cache_type: str, key_data: Union[str, Dict[str, Any]]) -> Optional[Any]:
        """Recupera dados do cache"""
        if not self.redis_async:
            return None
        
        try:
            cache_key = self._generate_cache_key(cache_type, key_data)
            
            # Buscar dados
            cached_data = await self.redis_async.get(cache_key)
            
            if cached_data:
                # Deserializar dados
                data = json.loads(cached_data)
                
                # Verificar se não expirou (dupla verificação)
                if 'cached_at' in data:
                    cached_time = datetime.fromisoformat(data['cached_at'])
                    ttl = self.ttl_config.get(cache_type, 3600)
                    
                    if (datetime.now() - cached_time).total_seconds() > ttl:
                        await self.redis_async.delete(cache_key)
                        return None
                
                # Registrar hit do cache
                await self._record_cache_hit(cache_type, True)
                
                self.logger.debug(f"📥 Cache hit: {cache_type}")
                return data.get('result')
            
            # Registrar miss do cache
            await self._record_cache_hit(cache_type, False)
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar cache {cache_type}: {e}")
            return None
    
    async def set_cached_data(self, cache_type: str, key_data: Union[str, Dict[str, Any]], 
                            result: Any, custom_ttl: Optional[int] = None) -> bool:
        """Armazena dados no cache"""
        if not self.redis_async:
            return False
        
        try:
            cache_key = self._generate_cache_key(cache_type, key_data)
            ttl = custom_ttl or self.ttl_config.get(cache_type, 3600)
            
            # Preparar dados para cache
            cache_data = {
                'result': result,
                'cached_at': datetime.now().isoformat(),
                'cache_type': cache_type,
                'ttl': ttl
            }
            
            # Serializar e armazenar
            serialized = json.dumps(cache_data, ensure_ascii=False, default=str)
            
            await self.redis_async.setex(cache_key, ttl, serialized)
            
            # Registrar estatísticas
            await self._record_cache_set(cache_type)
            
            self.logger.debug(f"📤 Cache set: {cache_type} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar cache {cache_type}: {e}")
            return False
    
    async def invalidate_cache(self, cache_type: str, key_data: Optional[Union[str, Dict[str, Any]]] = None) -> bool:
        """Invalida cache específico ou por tipo"""
        if not self.redis_async:
            return False
        
        try:
            if key_data:
                # Invalidar cache específico
                cache_key = self._generate_cache_key(cache_type, key_data)
                deleted = await self.redis_async.delete(cache_key)
                self.logger.info(f"🗑️ Cache invalidado: {cache_key}")
                return deleted > 0
            else:
                # Invalidar todos os caches do tipo
                pattern = f"{self.prefixes.get(cache_type, cache_type)}*"
                keys = await self.redis_async.keys(pattern)
                
                if keys:
                    deleted = await self.redis_async.delete(*keys)
                    self.logger.info(f"🗑️ Invalidados {deleted} caches do tipo: {cache_type}")
                    return deleted > 0
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao invalidar cache {cache_type}: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        if not self.redis_async:
            return {'error': 'Redis não disponível'}
        
        try:
            stats = {}
            
            # Estatísticas gerais do Redis
            info = await self.redis_async.info()
            stats['redis_info'] = {
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
            
            # Calcular hit ratio
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            
            if total > 0:
                stats['redis_info']['hit_ratio'] = f"{(hits/total)*100:.2f}%"
            
            # Contagem de chaves por tipo
            stats['keys_by_type'] = {}
            for cache_type, prefix in self.prefixes.items():
                pattern = f"{prefix}*"
                keys = await self.redis_async.keys(pattern)
                stats['keys_by_type'][cache_type] = len(keys)
            
            # Estatísticas específicas da aplicação
            app_stats = self.redis_async.hgetall('stats:cache_performance')
            stats['app_stats'] = app_stats
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {'error': str(e)}
    
    async def _record_cache_hit(self, cache_type: str, hit: bool):
        """Registra estatísticas de hit/miss"""
        if not self.redis_async:
            return
        
        try:
            key = f"stats:cache_performance"
            field = f"{cache_type}_{'hits' if hit else 'misses'}"
            
            self.redis_async.hincrby(key, field, 1)
            self.redis_async.expire(key, 86400 * 7)  # 7 dias
            
        except Exception as e:
            self.logger.debug(f"Erro ao registrar estatística: {e}")
    
    async def _record_cache_set(self, cache_type: str):
        """Registra operação de set no cache"""
        if not self.redis_async:
            return
        
        try:
            key = f"stats:cache_performance"
            field = f"{cache_type}_sets"
            
            self.redis_async.hincrby(key, field, 1)
            self.redis_async.expire(key, 86400 * 7)  # 7 dias
            
        except Exception as e:
            self.logger.debug(f"Erro ao registrar set: {e}")
    
    async def cleanup_expired_cache(self) -> Dict[str, Any]:
        """Remove caches expirados manualmente"""
        if not self.redis_async:
            return {'error': 'Redis não disponível'}
        
        try:
            cleaned = {}
            
            for cache_type, prefix in self.prefixes.items():
                pattern = f"{prefix}*"
                keys = await self.redis_async.keys(pattern)
                
                expired_count = 0
                for key in keys:
                    # Verificar TTL
                    ttl = await self.redis_async.ttl(key)
                    if ttl == -1:  # Sem expiração definida
                        # Buscar dados para verificar se expirou
                        data = await self.redis_async.get(key)
                        if data:
                            try:
                                cache_data = json.loads(data)
                                if 'cached_at' in cache_data:
                                    cached_time = datetime.fromisoformat(cache_data['cached_at'])
                                    expected_ttl = self.ttl_config.get(cache_type, 3600)
                                    
                                    if (datetime.now() - cached_time).total_seconds() > expected_ttl:
                                        await self.redis_async.delete(key)
                                        expired_count += 1
                            except:
                                # Se não conseguir deserializar, remove
                                await self.redis_async.delete(key)
                                expired_count += 1
                
                cleaned[cache_type] = expired_count
            
            self.logger.info(f"🧹 Limpeza de cache concluída: {cleaned}")
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de cache: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Fecha conexões Redis"""
        try:
            if self.redis_async:
                await self.redis_async.close()
            
            if self.redis_sync:
                await self.redis_sync.close()
            
            self.logger.info("🔌 Conexões Redis fechadas")
            
        except Exception as e:
            self.logger.error(f"Erro ao fechar Redis: {e}")

# Instância global do serviço de cache
cache_service = CacheService()

async def initialize_cache():
    """Inicializa o serviço de cache"""
    await cache_service.initialize()

async def get_cached_result(cache_type: str, key_data: Union[str, Dict[str, Any]]) -> Optional[Any]:
    """Helper para buscar dados do cache"""
    return await cache_service.get_cached_data(cache_type, key_data)

async def set_cached_result(cache_type: str, key_data: Union[str, Dict[str, Any]], 
                          result: Any, ttl: Optional[int] = None) -> bool:
    """Helper para armazenar dados no cache"""
    return await cache_service.set_cached_data(cache_type, key_data, result, ttl)

async def invalidate_cached_result(cache_type: str, key_data: Optional[Union[str, Dict[str, Any]]] = None) -> bool:
    """Helper para invalidar cache"""
    return await cache_service.invalidate_cache(cache_type, key_data)
