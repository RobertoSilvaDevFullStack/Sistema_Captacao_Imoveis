# backend/services/database_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.models.property import Property, PropertyPriceHistory, PropertyAnalysis
from database import SessionLocal

class DatabaseService:
    """Serviço para operações de banco de dados"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    # OPERAÇÕES COM PROPRIEDADES
    
    def save_property(self, property_data: dict) -> Property:
        """Salva uma nova propriedade ou atualiza existente"""
        try:
            # Verifica se já existe pela URL
            existing = self.db.query(Property).filter(Property.url == property_data.get('url')).first()
            
            if existing:
                # Atualiza propriedade existente
                for key, value in property_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.last_scraped_at = datetime.now()
                
                # Registra mudança de preço se houver
                if 'price' in property_data and existing.price != property_data['price']:
                    self._record_price_change(existing, property_data['price'])
                
                property_obj = existing
            else:
                # Cria nova propriedade
                property_obj = Property(**property_data)
                self.db.add(property_obj)
                self.db.flush()  # Para obter o ID
                
                # Registra preço inicial
                if property_obj.price:
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
