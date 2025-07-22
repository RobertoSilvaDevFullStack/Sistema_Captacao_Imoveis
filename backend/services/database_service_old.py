# backend/services/database_service.py
"""
Serviço de Banco de Dados para Deduplicação e Análise Histórica de Propriedades
Implementa Redis caching e SQLite para deduplicação e análise histórica.
"""
import sqlite3
import asyncio
import aiosqlite
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict
import os
from contextlib import asynccontextmanager

class DatabaseService:
    """Serviço de banco de dados para armazenamento, deduplicação e análise histórica"""
    
    def __init__(self, db_path: str = "properties_enrichment.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Schema do banco de dados
        self.schema = {
            'properties': '''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_hash TEXT UNIQUE NOT NULL,
                    address TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    neighborhood TEXT,
                    zipcode TEXT,
                    latitude REAL,
                    longitude REAL,
                    price REAL,
                    area REAL,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    property_type TEXT,
                    business_type TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    times_seen INTEGER DEFAULT 1,
                    source TEXT
                )
            ''',
            
            'enrichment_results': '''
                CREATE TABLE IF NOT EXISTS enrichment_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_id INTEGER NOT NULL,
                    enrichment_hash TEXT UNIQUE NOT NULL,
                    google_data JSON,
                    municipal_data JSON,
                    registry_data JSON,
                    market_data JSON,
                    ibge_data JSON,
                    confidence_score REAL,
                    enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    api_sources TEXT,
                    processing_time REAL,
                    FOREIGN KEY (property_id) REFERENCES properties (id)
                )
            ''',
            
            'api_usage_stats': '''
                CREATE TABLE IF NOT EXISTS api_usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT NOT NULL,
                    endpoint TEXT,
                    request_data JSON,
                    response_size INTEGER,
                    response_time REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cache_hit BOOLEAN DEFAULT FALSE
                )
            ''',
            
            'property_history': '''
                CREATE TABLE IF NOT EXISTS property_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    change_source TEXT,
                    FOREIGN KEY (property_id) REFERENCES properties (id)
                )
            ''',
            
            'market_trends': '''
                CREATE TABLE IF NOT EXISTS market_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    neighborhood TEXT,
                    property_type TEXT,
                    avg_price REAL,
                    avg_price_per_sqm REAL,
                    property_count INTEGER,
                    date_calculated DATE,
                    data_source TEXT
                )
            ''',
            
            'deduplication_log': '''
                CREATE TABLE IF NOT EXISTS deduplication_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_property_id INTEGER,
                    duplicate_property_id INTEGER,
                    similarity_score REAL,
                    merge_action TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (original_property_id) REFERENCES properties (id),
                    FOREIGN KEY (duplicate_property_id) REFERENCES properties (id)
                )
            '''
        }
        
        # Índices para performance
        self.indexes = [
            'CREATE INDEX IF NOT EXISTS idx_property_hash ON properties (property_hash)',
            'CREATE INDEX IF NOT EXISTS idx_property_location ON properties (city, state, neighborhood)',
            'CREATE INDEX IF NOT EXISTS idx_property_coordinates ON properties (latitude, longitude)',
            'CREATE INDEX IF NOT EXISTS idx_enrichment_hash ON enrichment_results (enrichment_hash)',
            'CREATE INDEX IF NOT EXISTS idx_enrichment_property ON enrichment_results (property_id)',
            'CREATE INDEX IF NOT EXISTS idx_api_stats_name ON api_usage_stats (api_name, timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_history_property ON property_history (property_id, changed_at)',
            'CREATE INDEX IF NOT EXISTS idx_market_trends_location ON market_trends (city, state, date_calculated)'
        ]
    
    async def initialize(self):
        """Inicializa o banco de dados"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Criar tabelas
                for table_name, schema in self.schema.items():
                    await db.execute(schema)
                
                # Criar índices
                for index in self.indexes:
                    await db.execute(index)
                
                await db.commit()
            
            self.logger.info(f"✅ Banco de dados inicializado: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar banco: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager para conexões de banco"""
        conn = None
        try:
            conn = await aiosqlite.connect(self.db_path)
            yield conn
        except Exception as e:
            self.logger.error(f"❌ Erro na conexão: {e}")
            raise
        finally:
            if conn:
                await conn.close()
    
    def generate_property_hash(self, property_data: Dict[str, Any]) -> str:
        """Gera hash único para propriedade baseado em localização e características"""
        # Normalizar dados para hash consistente
        normalized_data = {
            'address': str(property_data.get('address', '')).lower().strip(),
            'city': str(property_data.get('city', '')).lower().strip(),
            'state': str(property_data.get('state', '')).lower().strip(),
            'neighborhood': str(property_data.get('neighborhood', '')).lower().strip(),
            'area': property_data.get('area'),
            'bedrooms': property_data.get('bedrooms'),
            'bathrooms': property_data.get('bathrooms'),
            'property_type': str(property_data.get('property_type', '')).lower().strip()
        }
        
        # Gerar hash MD5
        hash_string = json.dumps(normalized_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def generate_enrichment_hash(self, property_id: int, enrichment_data: Dict[str, Any]) -> str:
        """Gera hash único para dados de enriquecimento"""
        hash_data = {
            'property_id': property_id,
            'apis_used': sorted(enrichment_data.keys()),
            'timestamp': datetime.now().strftime('%Y-%m-%d')  # Para invalidar cache diário
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    async def save_property(self, property_data: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Salva propriedade com deduplicação
        Returns: (property_id, is_new)
        """
        try:
            property_hash = self.generate_property_hash(property_data)
            
            async with self.get_connection() as conn:
                # Verificar se propriedade já existe
                cursor = await conn.execute(
                    "SELECT id, times_seen FROM properties WHERE property_hash = ?",
                    (property_hash,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    # Propriedade existente - atualizar contador e timestamp
                    property_id, times_seen = existing
                    await conn.execute(
                        """UPDATE properties 
                           SET times_seen = ?, last_updated = CURRENT_TIMESTAMP 
                           WHERE id = ?""",
                        (times_seen + 1, property_id)
                    )
                    
                    self.logger.info(f"🔄 Propriedade duplicada encontrada: {property_id} (vista {times_seen + 1}x)")
                    
                    # Log de deduplicação
                    await self._log_duplicate_detection(conn, property_id, property_hash)
                    
                    await conn.commit()
                    return property_id, False
                
                else:
                    # Nova propriedade
                    cursor = await conn.execute(
                        """INSERT INTO properties 
                           (property_hash, address, city, state, neighborhood, zipcode,
                            latitude, longitude, price, area, bedrooms, bathrooms,
                            property_type, business_type, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            property_hash,
                            property_data.get('address'),
                            property_data.get('city'),
                            property_data.get('state'),
                            property_data.get('neighborhood'),
                            property_data.get('zipcode'),
                            property_data.get('latitude'),
                            property_data.get('longitude'),
                            property_data.get('price'),
                            property_data.get('area'),
                            property_data.get('bedrooms'),
                            property_data.get('bathrooms'),
                            property_data.get('property_type'),
                            property_data.get('business_type'),
                            property_data.get('source')
                        )
                    )
                    
                    property_id = cursor.lastrowid
                    await conn.commit()
                    
                    self.logger.info(f"✅ Nova propriedade salva: {property_id}")
                    return property_id, True
    async def _log_duplicate_detection(self, conn, property_id: int, property_hash: str):
        """Log de detecção de duplicatas"""
        await conn.execute(
            """INSERT INTO deduplication_log 
               (original_property_id, duplicate_property_id, similarity_score, merge_action)
               VALUES (?, ?, ?, ?)""",
            (property_id, property_id, 1.0, 'duplicate_detected')
        )
    
    async def save_enrichment_result(self, property_id: int, enrichment_data: Dict[str, Any], 
                                   confidence_score: float, processing_time: float) -> int:
        """Salva resultado de enriquecimento"""
        try:
            enrichment_hash = self.generate_enrichment_hash(property_id, enrichment_data)
            
            async with self.get_connection() as conn:
                # Verificar se já existe
                cursor = await conn.execute(
                    "SELECT id FROM enrichment_results WHERE enrichment_hash = ?",
                    (enrichment_hash,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    self.logger.info(f"🔄 Resultado de enriquecimento já existe: {existing[0]}")
                    return existing[0]
                
                # Salvar novo resultado
                cursor = await conn.execute(
                    """INSERT INTO enrichment_results 
                       (property_id, enrichment_hash, google_data, municipal_data, 
                        registry_data, market_data, ibge_data, confidence_score, 
                        api_sources, processing_time)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        property_id,
                        enrichment_hash,
                        json.dumps(enrichment_data.get('google_data')),
                        json.dumps(enrichment_data.get('municipal_data')),
                        json.dumps(enrichment_data.get('registry_data')),
                        json.dumps(enrichment_data.get('market_data')),
                        json.dumps(enrichment_data.get('ibge_data')),
                        confidence_score,
                        ','.join(enrichment_data.keys()),
                        processing_time
                    )
                )
                
                result_id = cursor.lastrowid
                await conn.commit()
                
                self.logger.info(f"✅ Resultado de enriquecimento salvo: {result_id}")
                return result_id
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar enriquecimento: {e}")
            raise
    
    async def log_api_usage(self, api_name: str, endpoint: str, request_data: Dict[str, Any],
                          response_size: int, response_time: float, success: bool,
                          error_message: Optional[str] = None, cache_hit: bool = False):
        """Log de uso das APIs"""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """INSERT INTO api_usage_stats 
                       (api_name, endpoint, request_data, response_size, response_time, 
                        success, error_message, cache_hit)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        api_name,
                        endpoint,
                        json.dumps(request_data),
                        response_size,
                        response_time,
                        success,
                        error_message,
                        cache_hit
                    )
                )
                await conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao log API usage: {e}")
    
    async def find_duplicates(self, similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Encontra propriedades potencialmente duplicadas"""
        try:
            async with self.get_connection() as conn:
                # Buscar propriedades com localizações similares
                cursor = await conn.execute(
                    """SELECT p1.id, p1.property_hash, p1.address, p1.city, p1.state,
                              p2.id, p2.property_hash, p2.address, p2.city, p2.state
                       FROM properties p1
                       JOIN properties p2 ON p1.id < p2.id
                       WHERE p1.city = p2.city 
                         AND p1.state = p2.state
                         AND p1.neighborhood = p2.neighborhood
                         AND ABS(p1.latitude - p2.latitude) < 0.001
                         AND ABS(p1.longitude - p2.longitude) < 0.001
                         AND p1.property_hash != p2.property_hash"""
                )
                
                duplicates = []
                async for row in cursor:
                    similarity_score = self._calculate_similarity(row)
                    if similarity_score >= similarity_threshold:
                        duplicates.append({
                            'property1_id': row[0],
                            'property1_hash': row[1],
                            'property1_address': row[2],
                            'property2_id': row[5],
                            'property2_hash': row[6],
                            'property2_address': row[7],
                            'similarity_score': similarity_score
                        })
                
                return duplicates
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar duplicatas: {e}")
            return []
    
    def _calculate_similarity(self, row) -> float:
        """Calcula similaridade entre duas propriedades"""
        # Implementação simplificada - pode ser expandida
        # Considera proximidade geográfica e dados similares
        return 0.85  # Placeholder
    
    async def get_market_trends(self, city: str, state: str, 
                              days_back: int = 30) -> Dict[str, Any]:
        """Obtém tendências de mercado"""
        try:
            async with self.get_connection() as conn:
                # Calcular estatísticas de mercado
                cursor = await conn.execute(
                    """SELECT property_type, AVG(price) as avg_price, 
                              AVG(price/area) as avg_price_per_sqm, COUNT(*) as count
                       FROM properties 
                       WHERE city = ? AND state = ? 
                         AND last_updated >= date('now', '-{} days')
                         AND price IS NOT NULL AND area IS NOT NULL
                       GROUP BY property_type""".format(days_back),
                    (city, state)
                )
                
                trends = {}
                async for row in cursor:
                    property_type, avg_price, avg_price_per_sqm, count = row
                    trends[property_type] = {
                        'avg_price': avg_price,
                        'avg_price_per_sqm': avg_price_per_sqm,
                        'property_count': count
                    }
                
                # Salvar tendências calculadas
                for prop_type, data in trends.items():
                    await conn.execute(
                        """INSERT OR REPLACE INTO market_trends 
                           (city, state, property_type, avg_price, avg_price_per_sqm, 
                            property_count, date_calculated, data_source)
                           VALUES (?, ?, ?, ?, ?, ?, date('now'), 'calculated')""",
                        (city, state, prop_type, data['avg_price'], 
                         data['avg_price_per_sqm'], data['property_count'])
                    )
                
                await conn.commit()
                return trends
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular tendências: {e}")
            return {}
    
    async def get_property_history(self, property_id: int) -> List[Dict[str, Any]]:
        """Obtém histórico de mudanças de uma propriedade"""
        try:
            async with self.get_connection() as conn:
                cursor = await conn.execute(
                    """SELECT field_name, old_value, new_value, changed_at, change_source
                       FROM property_history 
                       WHERE property_id = ? 
                       ORDER BY changed_at DESC""",
                    (property_id,)
                )
                
                history = []
                async for row in cursor:
                    history.append({
                        'field_name': row[0],
                        'old_value': row[1],
                        'new_value': row[2],
                        'changed_at': row[3],
                        'change_source': row[4]
                    })
                
                return history
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    async def get_api_usage_stats(self, days_back: int = 7) -> Dict[str, Any]:
        """Obtém estatísticas de uso das APIs"""
        try:
            async with self.get_connection() as conn:
                cursor = await conn.execute(
                    """SELECT api_name, COUNT(*) as total_requests,
                              AVG(response_time) as avg_response_time,
                              SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                              SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits
                       FROM api_usage_stats 
                       WHERE timestamp >= datetime('now', '-{} days')
                       GROUP BY api_name""".format(days_back),
                )
                
                stats = {}
                async for row in cursor:
                    api_name, total, avg_time, successful, cache_hits = row
                    stats[api_name] = {
                        'total_requests': total,
                        'avg_response_time': avg_time,
                        'success_rate': successful / total if total > 0 else 0,
                        'cache_hit_rate': cache_hits / total if total > 0 else 0
                    }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar estatísticas: {e}")
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Remove dados antigos para manter performance"""
        try:
            async with self.get_connection() as conn:
                # Remover logs de API antigos
                await conn.execute(
                    "DELETE FROM api_usage_stats WHERE timestamp < datetime('now', '-{} days')".format(days_to_keep)
                )
                
                # Remover logs de deduplicação antigos
                await conn.execute(
                    "DELETE FROM deduplication_log WHERE processed_at < datetime('now', '-{} days')".format(days_to_keep)
                )
                
                # Remover tendências de mercado antigas
                await conn.execute(
                    "DELETE FROM market_trends WHERE date_calculated < date('now', '-{} days')".format(days_to_keep)
                )
                
                await conn.commit()
                self.logger.info(f"✅ Limpeza de dados concluída (mantidos últimos {days_to_keep} dias)")
                
        except Exception as e:
            self.logger.error(f"❌ Erro na limpeza de dados: {e}")
    
    async def close(self):
        """Fechar conexões (se necessário)"""
        # Para aiosqlite, não há conexões persistentes para fechar
        pass
                    self._record_price_change(property_obj, property_obj.price, is_initial=True)
            
            self.db.commit()
            return property_obj
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_properties(self, limit: int = 100, offset: int = 0, 
                      filters: Optional[Dict] = None) -> List[Property]:
        """Busca propriedades com filtros opcionais"""
        query = self.db.query(Property).filter(Property.is_active == True)
        
        if filters:
            if filters.get('neighborhood'):
                query = query.filter(Property.neighborhood.ilike(f"%{filters['neighborhood']}%"))
            if filters.get('property_type'):
                query = query.filter(Property.property_type == filters['property_type'])
            if filters.get('min_price'):
                query = query.filter(Property.price >= filters['min_price'])
            if filters.get('max_price'):
                query = query.filter(Property.price <= filters['max_price'])
            if filters.get('min_bedrooms'):
                query = query.filter(Property.bedrooms >= filters['min_bedrooms'])
            if filters.get('max_bedrooms'):
                query = query.filter(Property.bedrooms <= filters['max_bedrooms'])
            if filters.get('min_area'):
                query = query.filter(Property.area >= filters['min_area'])
            if filters.get('is_valid_only', True):
                query = query.filter(Property.is_valid == True)
        
        return query.order_by(desc(Property.created_at)).offset(offset).limit(limit).all()
    
    def get_property_by_id(self, property_id: int) -> Optional[Property]:
        """Busca propriedade por ID"""
        return self.db.query(Property).filter(Property.id == property_id).first()
    
    def get_property_by_url(self, url: str) -> Optional[Property]:
        """Busca propriedade por URL"""
        return self.db.query(Property).filter(Property.url == url).first()
    
    def search_properties(self, search_term: str, limit: int = 50) -> List[Property]:
        """Busca propriedades por termo de pesquisa"""
        search_pattern = f"%{search_term}%"
        return self.db.query(Property).filter(
            and_(
                Property.is_active == True,
                Property.is_valid == True,
                or_(
                    Property.title.ilike(search_pattern),
                    Property.address.ilike(search_pattern),
                    Property.neighborhood.ilike(search_pattern),
                    Property.description.ilike(search_pattern)
                )
            )
        ).order_by(desc(Property.created_at)).limit(limit).all()
    
    # OPERAÇÕES COM HISTÓRICO DE PREÇOS
    
    def _record_price_change(self, property_obj: Property, new_price: float, is_initial: bool = False):
        """Registra mudança de preço"""
        previous_price = None
        change_percentage = None
        
        if not is_initial:
            # Busca último preço registrado
            last_record = self.db.query(PropertyPriceHistory).filter(
                PropertyPriceHistory.property_id == property_obj.id
            ).order_by(desc(PropertyPriceHistory.recorded_at)).first()
            
            if last_record:
                previous_price = last_record.price
                change_percentage = ((new_price - previous_price) / previous_price) * 100
        
        # Cria registro de histórico
        price_history = PropertyPriceHistory(
            property_id=property_obj.id,
            price=new_price,
            price_per_sqm=new_price / property_obj.area if property_obj.area else None,
            source=property_obj.source,
            change_percentage=change_percentage
        )
        
        self.db.add(price_history)
    
    def get_price_history(self, property_id: int, days: int = 30) -> List[PropertyPriceHistory]:
        """Busca histórico de preços de uma propriedade"""
        since_date = datetime.now() - timedelta(days=days)
        return self.db.query(PropertyPriceHistory).filter(
            and_(
                PropertyPriceHistory.property_id == property_id,
                PropertyPriceHistory.recorded_at >= since_date
            )
        ).order_by(PropertyPriceHistory.recorded_at).all()
    
    # OPERAÇÕES COM ANÁLISES
    
    def save_property_analysis(self, property_id, analysis_data: dict) -> PropertyAnalysis:
        """Salva análise de uma propriedade"""
        try:
            # Converte property_id para int se necessário
            if hasattr(property_id, '__int__'):
                property_id = int(property_id)
            elif hasattr(property_id, 'value'):
                property_id = property_id.value
            
            analysis = PropertyAnalysis(
                property_id=property_id,
                **analysis_data
            )
            
            self.db.add(analysis)
            self.db.commit()
            return analysis
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_property_analyses(self, property_id: int, limit: int = 10) -> List[PropertyAnalysis]:
        """Busca análises de uma propriedade"""
        return self.db.query(PropertyAnalysis).filter(
            PropertyAnalysis.property_id == property_id
        ).order_by(desc(PropertyAnalysis.analysis_date)).limit(limit).all()
    
    def get_best_opportunities(self, limit: int = 20) -> List[Property]:
        """Busca melhores oportunidades baseadas nas análises"""
        return self.db.query(Property).join(PropertyAnalysis).filter(
            and_(
                Property.is_active == True,
                Property.is_valid == True,
                PropertyAnalysis.opportunity_score >= 30
            )
        ).order_by(desc(PropertyAnalysis.opportunity_score)).limit(limit).all()
    
    # ESTATÍSTICAS E MÉTRICAS
    
    def get_market_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do mercado"""
        stats = {}
        
        # Total de propriedades
        stats['total_properties'] = self.db.query(Property).filter(Property.is_active == True).count()
        stats['valid_properties'] = self.db.query(Property).filter(
            and_(Property.is_active == True, Property.is_valid == True)
        ).count()
        
        # Preços médios
        avg_price = self.db.query(func.avg(Property.price)).filter(
            and_(Property.is_active == True, Property.is_valid == True)
        ).scalar()
        stats['avg_price'] = float(avg_price) if avg_price else 0
        
        # Preço por m²
        avg_price_per_sqm = self.db.query(func.avg(Property.price_per_sqm)).filter(
            and_(Property.is_active == True, Property.is_valid == True, Property.price_per_sqm.isnot(None))
        ).scalar()
        stats['avg_price_per_sqm'] = float(avg_price_per_sqm) if avg_price_per_sqm else 0
        
        # Distribuição por bairros
        neighborhood_stats = self.db.query(
            Property.neighborhood,
            func.count(Property.id).label('count'),
            func.avg(Property.price).label('avg_price')
        ).filter(
            and_(Property.is_active == True, Property.is_valid == True)
        ).group_by(Property.neighborhood).order_by(desc('count')).limit(10).all()
        
        stats['top_neighborhoods'] = [
            {
                'neighborhood': row.neighborhood,
                'count': row.count,
                'avg_price': float(row.avg_price) if row.avg_price else 0
            }
            for row in neighborhood_stats
        ]
        
        # Oportunidades identificadas
        opportunities_count = self.db.query(PropertyAnalysis).filter(
            PropertyAnalysis.opportunity_score >= 30
        ).count()
        stats['opportunities_count'] = opportunities_count
        
        return stats
    
    def get_neighborhood_stats(self, neighborhood: str) -> Dict[str, Any]:
        """Retorna estatísticas específicas de um bairro"""
        properties = self.db.query(Property).filter(
            and_(
                Property.neighborhood.ilike(f"%{neighborhood}%"),
                Property.is_active == True,
                Property.is_valid == True
            )
        ).all()
        
        if not properties:
            return {}
        
        prices = [p.price for p in properties if p.price]
        areas = [p.area for p in properties if p.area]
        price_per_sqm = [p.price_per_sqm for p in properties if p.price_per_sqm]
        
        stats = {
            'neighborhood': neighborhood,
            'total_properties': len(properties),
            'avg_price': sum(prices) / len(prices) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'avg_area': sum(areas) / len(areas) if areas else 0,
            'avg_price_per_sqm': sum(price_per_sqm) / len(price_per_sqm) if price_per_sqm else 0,
            'property_types': {}
        }
        
        # Distribuição por tipo
        for prop in properties:
            prop_type = prop.property_type or 'Não informado'
            if prop_type not in stats['property_types']:
                stats['property_types'][prop_type] = 0
            stats['property_types'][prop_type] += 1
        
        return stats
    
    # OPERAÇÕES DE LIMPEZA
    
    def mark_inactive_properties(self, cutoff_days: int = 30):
        """Marca propriedades como inativas se não foram atualizadas recentemente"""
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)
        
        updated_count = self.db.query(Property).filter(
            Property.last_scraped_at < cutoff_date
        ).update({'is_active': False})
        
        self.db.commit()
        return updated_count
    
    def cleanup_invalid_properties(self):
        """Remove propriedades inválidas antigas"""
        cutoff_date = datetime.now() - timedelta(days=7)
        
        deleted_count = self.db.query(Property).filter(
            and_(
                Property.is_valid == False,
                Property.created_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        return deleted_count
