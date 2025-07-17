from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    price = Column(Float)
    address = Column(String(500))
    neighborhood = Column(String(100))
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    area = Column(Float)
    parking_spots = Column(Integer)
    description = Column(Text)
    url = Column(String(1000), unique=True)
    source = Column(String(50))
    property_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'address': self.address,
            'neighborhood': self.neighborhood,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area': self.area,
            'url': self.url,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MarketAnalysis(Base):
    __tablename__ = 'market_analysis'
    
    id = Column(Integer, primary_key=True)
    neighborhood = Column(String(100))
    avg_price = Column(Float)
    avg_price_per_sqm = Column(Float)
    total_properties = Column(Integer)
    analysis_date = Column(DateTime, default=datetime.now)
    property_type = Column(String(50))