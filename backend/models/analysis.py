# Em backend/models/analysis.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base  # <-- Importando a mesma Base central

class MarketAnalysis(Base):
    __tablename__ = 'market_analysis'
    
    id = Column(Integer, primary_key=True, index=True)
    neighborhood = Column(String(100), index=True)
    avg_price = Column(Float)
    avg_price_per_sqm = Column(Float)
    total_properties = Column(Integer)
    analysis_date = Column(DateTime, default=datetime.now)
    property_type = Column(String(50))