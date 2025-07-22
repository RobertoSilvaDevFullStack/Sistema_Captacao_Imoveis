# backend/services/cache_service_simple.py
"""
Serviço de Cache Simples (In-Memory) para demonstração
Substitui Redis por cache em memória para testes.
"""
import asyncio
import logging
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import asdict

class CacheService:
    """Serviço de cache em memória para demonstração"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'total_requests': 0
        }
        self.logger = logging.getLogger(__name__)
        
        # TTL configurations (em horas)
        self.default_ttl = {
            'google_maps': 24,      # Google Maps: 24h
            'municipal': 72,        # Municipal: 72h  
            'registry': 168,        # Registry: 1 semana
            'market_data': 6,       # Market data: 6h
            'ibge': 720,           # IBGE: 30 dias
            'enrichment': 24,      # Enriquecimento: 24h
            'default': 12          # Padrão: 12h
        }
    
    async def initialize(self):
        """Inicializar cache (para compatibilidade com Redis)"""
        self.logger.info("✅ Cache service inicializado (in-memory)")
    
    def _is_expired(self, cached_item: Dict[str, Any]) -> bool:
        """Verifica se item do cache expirou"""
        if 'expires_at' not in cached_item:
            return True
        
        return datetime.now() > datetime.fromisoformat(cached_item['expires_at'])
    
    def _generate_cache_key(self, api_name: str, request_data: Dict[str, Any]) -> str:
        """Gera chave de cache baseada na API e dados da requisição"""
        # Normalizar dados para chave consistente
        normalized_data = {
            'api': api_name,
            'params': {k: v for k, v in sorted(request_data.items()) if v is not None}
        }
        
        # Gerar hash MD5
        key_string = json.dumps(normalized_data, sort_keys=True, default=str)
        hash_value = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"api_cache:{api_name}:{hash_value}"
    
    async def get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Recupera dados do cache"""
        self.stats['total_requests'] += 1
        
        try:
            if cache_key in self.cache:
                cached_item = self.cache[cache_key]
                
                # Verificar se expirou
                if self._is_expired(cached_item):
                    del self.cache[cache_key]
                    self.stats['misses'] += 1
                    self.logger.debug(f"🔴 Cache MISS (expirado): {cache_key}")
                    return None
                
                self.stats['hits'] += 1
                self.logger.debug(f"🟢 Cache HIT: {cache_key}")
                return cached_item['data']
            
            self.stats['misses'] += 1
            self.logger.debug(f"🔴 Cache MISS: {cache_key}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao recuperar cache: {e}")
            self.stats['misses'] += 1
            return None
    
    async def set_cached_data(self, cache_key: str, data: Any, ttl_hours: Optional[int] = None) -> bool:
        """Armazena dados no cache"""
        try:
            # Determinar TTL
            if ttl_hours is None:
                ttl_hours = self.default_ttl.get('default', 12)
            
            # Calcular expiração
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            # Armazenar no cache
            self.cache[cache_key] = {
                'data': data,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'ttl_hours': ttl_hours
            }
            
            self.stats['sets'] += 1
            self.logger.debug(f"✅ Cache SET: {cache_key} (TTL: {ttl_hours}h)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao armazenar cache: {e}")
            return False
    
    async def cache_api_result(self, api_name: str, request_data: Dict[str, Any], 
                             response_data: Any, force_update: bool = False) -> str:
        """Cache específico para resultados de API"""
        cache_key = self._generate_cache_key(api_name, request_data)
        
        # Verificar se já existe (a menos que force_update)
        if not force_update:
            existing = await self.get_cached_data(cache_key)
            if existing:
                self.logger.debug(f"🔄 Cache já existe para API {api_name}")
                return cache_key
        
        # Armazenar com TTL específico da API
        ttl_hours = self.default_ttl.get(api_name, self.default_ttl['default'])
        
        success = await self.set_cached_data(cache_key, response_data, ttl_hours)
        
        if success:
            self.logger.info(f"💾 API result cached: {api_name} (TTL: {ttl_hours}h)")
        
        return cache_key
    
    async def get_api_cached_result(self, api_name: str, request_data: Dict[str, Any]) -> Optional[Any]:
        """Recupera resultado cachado de API"""
        cache_key = self._generate_cache_key(api_name, request_data)
        result = await self.get_cached_data(cache_key)
        
        if result:
            self.logger.info(f"🟢 Cache HIT para API: {api_name}")
        else:
            self.logger.info(f"🔴 Cache MISS para API: {api_name}")
        
        return result
    
    async def invalidate_cache(self, pattern: Optional[str] = None, 
                             api_name: Optional[str] = None) -> int:
        """Invalida cache por padrão ou API"""
        deleted_count = 0
        
        try:
            keys_to_delete = []
            
            if api_name:
                # Invalidar por API específica
                pattern = f"api_cache:{api_name}:*"
            
            if pattern:
                # Filtrar chaves por padrão
                for key in self.cache.keys():
                    if self._matches_pattern(key, pattern):
                        keys_to_delete.append(key)
            else:
                # Invalidar tudo
                keys_to_delete = list(self.cache.keys())
            
            # Deletar chaves
            for key in keys_to_delete:
                del self.cache[key]
                deleted_count += 1
            
            self.stats['deletes'] += deleted_count
            self.logger.info(f"🗑️ Cache invalidado: {deleted_count} itens removidos")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao invalidar cache: {e}")
        
        return deleted_count
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Verifica se chave corresponde ao padrão (implementação simples)"""
        if '*' in pattern:
            pattern_prefix = pattern.replace('*', '')
            return key.startswith(pattern_prefix)
        return key == pattern
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_items = len(self.cache)
        expired_items = 0
        
        # Contar itens expirados
        for cached_item in self.cache.values():
            if self._is_expired(cached_item):
                expired_items += 1
        
        # Calcular hit rate
        total_requests = self.stats['total_requests']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Estatísticas por API
        api_breakdown = {}
        for key in self.cache.keys():
            if key.startswith('api_cache:'):
                api_name = key.split(':')[1]
                api_breakdown[api_name] = api_breakdown.get(api_name, 0) + 1
        
        return {
            'total_items': total_items,
            'expired_items': expired_items,
            'active_items': total_items - expired_items,
            'hit_rate': round(hit_rate, 2),
            'statistics': self.stats.copy(),
            'api_breakdown': api_breakdown,
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estima uso de memória do cache"""
        try:
            import sys
            total_size = 0
            for key, value in self.cache.items():
                total_size += sys.getsizeof(key) + sys.getsizeof(str(value))
            return round(total_size / (1024 * 1024), 2)  # MB
        except:
            return 0.0
    
    async def cleanup_expired(self) -> int:
        """Remove itens expirados do cache"""
        deleted_count = 0
        
        keys_to_delete = []
        for key, cached_item in self.cache.items():
            if self._is_expired(cached_item):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.cache[key]
            deleted_count += 1
        
        if deleted_count > 0:
            self.logger.info(f"🧹 Limpeza automática: {deleted_count} itens expirados removidos")
        
        return deleted_count
    
    async def close(self):
        """Fechar conexões (para compatibilidade)"""
        self.logger.info("🔒 Cache service fechado")
        
    # Métodos de monitoramento
    async def monitor_performance(self):
        """Monitor de performance em background"""
        while True:
            try:
                await asyncio.sleep(300)  # A cada 5 minutos
                
                # Limpeza automática
                await self.cleanup_expired()
                
                # Log de estatísticas
                stats = await self.get_cache_statistics()
                self.logger.info(f"📊 Cache stats: {stats['hit_rate']}% hit rate, {stats['active_items']} items")
                
            except Exception as e:
                self.logger.error(f"❌ Erro no monitor de performance: {e}")
                break


# Exemplo de uso
async def demo_cache_usage():
    """Demonstração do cache service"""
    cache = CacheService()
    await cache.initialize()
    
    # Teste básico
    test_data = {'address': 'Rua A, 123', 'city': 'São Paulo'}
    
    # Cache miss
    result1 = await cache.get_api_cached_result('google_maps', test_data)
    print(f"Primeiro acesso: {result1}")
    
    # Armazenar resultado
    api_result = {'lat': -23.5505, 'lng': -46.6333, 'formatted_address': 'Rua A, 123, São Paulo'}
    await cache.cache_api_result('google_maps', test_data, api_result)
    
    # Cache hit
    result2 = await cache.get_api_cached_result('google_maps', test_data)
    print(f"Segundo acesso: {result2}")
    
    # Estatísticas
    stats = await cache.get_cache_statistics()
    print(f"Estatísticas: {stats}")

if __name__ == "__main__":
    asyncio.run(demo_cache_usage())
