# backend/models/property.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String)
    
    # Dados brutos (originais do scraper)
    raw_price = Column(String)
    raw_bedrooms = Column(String)
    raw_bathrooms = Column(String)
    raw_area = Column(String)
    raw_parking_spaces = Column(String)
    raw_address = Column(String)
    
    # Dados processados e limpos
    price = Column(Float, index=True)
    bedrooms = Column(Integer, index=True)
    bathrooms = Column(Integer)
    area = Column(Float, index=True)
    parking_spaces = Column(Integer)
    address = Column(String)
    neighborhood = Column(String, index=True)
    property_type = Column(String, index=True)  # Apartamento, Casa, Sobrado, etc.
    
    # Métricas calculadas
    price_per_sqm = Column(Float, index=True)
    
    # Status e validação
    is_valid = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Dados adicionais
    description = Column(Text)
    amenities = Column(JSON)  # Lista de comodidades
    source = Column(String, default='vivareal')  # Fonte dos dados
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    price_history = relationship("PropertyPriceHistory", back_populates="property", cascade="all, delete-orphan")
    analyses = relationship("PropertyAnalysis", back_populates="property", cascade="all, delete-orphan")

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'price': self.price,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area': self.area,
            'parking_spaces': self.parking_spaces,
            'address': self.address,
            'neighborhood': self.neighborhood,
            'property_type': self.property_type,
            'price_per_sqm': self.price_per_sqm,
            'is_valid': self.is_valid,
            'is_active': self.is_active,
            'description': self.description,
            'amenities': self.amenities,
            'source': self.source,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'last_scraped_at': self.last_scraped_at
        }

# Índices compostos para consultas otimizadas
Index('idx_property_location_price', Property.neighborhood, Property.property_type, Property.price)
Index('idx_property_metrics', Property.price_per_sqm, Property.area, Property.bedrooms)
Index('idx_property_search', Property.is_valid, Property.is_active, Property.created_at)


class PropertyPriceHistory(Base):
    __tablename__ = "property_price_history"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Dados de preço
    price = Column(Float, nullable=False)
    price_per_sqm = Column(Float)
    
    # Fonte e contexto
    source = Column(String, default='vivareal')
    change_percentage = Column(Float)  # % de mudança em relação ao preço anterior
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relacionamento
    property = relationship("Property", back_populates="price_history")

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'price': self.price,
            'price_per_sqm': self.price_per_sqm,
            'source': self.source,
            'change_percentage': self.change_percentage,
            'recorded_at': self.recorded_at
        }

# Índice para consultas de histórico
Index('idx_price_history_timeline', PropertyPriceHistory.property_id, PropertyPriceHistory.recorded_at)


class PropertyAnalysis(Base):
    __tablename__ = "property_analyses"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Métricas de análise
    opportunity_score = Column(Float)  # Score de oportunidade (0-50)
    discount_percentage = Column(Float)  # % de desconto em relação à média
    estimated_rental_yield = Column(Float)  # Yield de aluguel estimado
    payback_years = Column(Float)  # Anos para recuperar investimento
    efficiency_score = Column(Float)  # Score de eficiência (0-100)
    
    # Recomendações
    investment_recommendation = Column(String)  # EXCELENTE, BOM, MODERADO, BAIXO
    analysis_notes = Column(Text)  # Observações da análise
    
    # Comparações de mercado
    market_avg_price_per_sqm = Column(Float)  # Preço médio de mercado para comparação
    savings_amount = Column(Float)  # Valor economizado em relação à média
    
    # Contexto da análise
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    analysis_version = Column(String, default='1.0')  # Versão do algoritmo de análise
    
    # Relacionamento
    property = relationship("Property", back_populates="analyses")

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'opportunity_score': self.opportunity_score,
            'discount_percentage': self.discount_percentage,
            'estimated_rental_yield': self.estimated_rental_yield,
            'payback_years': self.payback_years,
            'efficiency_score': self.efficiency_score,
            'investment_recommendation': self.investment_recommendation,
            'analysis_notes': self.analysis_notes,
            'market_avg_price_per_sqm': self.market_avg_price_per_sqm,
            'savings_amount': self.savings_amount,
            'analysis_date': self.analysis_date,
            'analysis_version': self.analysis_version
        }

# Índice para consultas de análise
Index('idx_analysis_scores', PropertyAnalysis.opportunity_score, PropertyAnalysis.efficiency_score)
Index('idx_analysis_recommendations', PropertyAnalysis.investment_recommendation, PropertyAnalysis.analysis_date)
