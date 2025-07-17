import pandas as pd
from sqlalchemy import func
from .models.property import Property, MarketAnalysis
from collections import defaultdict
import numpy as np

class AnalysisService:
    def __init__(self, db_session):
        self.db_session = db_session
        
    def get_market_overview(self, days_back=30):
        """Análise geral do mercado dos últimos X dias"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        properties = self.db_session.query(Property).filter(
            Property.created_at >= cutoff_date,
            Property.is_active == True
        ).all()
        
        df = pd.DataFrame([prop.to_dict() for prop in properties])
        
        if df.empty:
            return self._empty_analysis()
            
        analysis = {
            'total_properties': len(df),
            'avg_price': df['price'].mean(),
            'median_price': df['price'].median(),
            'price_range': {
                'min': df['price'].min(),
                'max': df['price'].max(),
                'q1': df['price'].quantile(0.25),
                'q3': df['price'].quantile(0.75)
            },
            'by_neighborhood': self._analyze_by_neighborhood(df),
            'by_bedrooms': self._analyze_by_bedrooms(df),
            'price_distribution': self._get_price_distribution(df),
            'new_listings_trend': self._get_daily_trend(df)
        }
        
        return analysis
        
    def _analyze_by_neighborhood(self, df):
        """Análise por bairro"""
        neighborhood_analysis = df.groupby('neighborhood').agg({
            'price': ['mean', 'median', 'count'],
            'area': 'mean'
        }).round(2)
        
        # Calcular preço por m²
        neighborhood_analysis['price_per_sqm'] = (
            neighborhood_analysis['price']['mean'] / 
            neighborhood_analysis['area']['mean']
        ).round(2)
        
        return neighborhood_analysis.to_dict('index')
        
    def _analyze_by_bedrooms(self, df):
        """Análise por número de quartos"""
        return df.groupby('bedrooms').agg({
            'price': ['mean', 'median', 'count']
        }).round(2).to_dict('index')
        
    def _get_price_distribution(self, df):
        """Distribuição de preços em faixas"""
        bins = [0, 500000, 1000000, 1500000, 2000000, 3000000, float('inf')]
        labels = ['Até R$ 500k', 'R$ 500k - R$ 1M', 'R$ 1M - R$ 1.5M', 
                 'R$ 1.5M - R$ 2M', 'R$ 2M - R$ 3M', 'Acima de R$ 3M']
        
        df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels)
        distribution = df['price_range'].value_counts().to_dict()
        
        return distribution
        
    def _get_daily_trend(self, df):
        """Tendência diária de novos imóveis"""
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        daily_count = df.groupby('date').size().to_dict()
        
        # Converter dates para strings para JSON serialization
        return {str(date): count for date, count in daily_count.items()}
        
    def get_top_opportunities(self, limit=10):
        """Identificar oportunidades baseadas em preço abaixo da média"""
        # Lógica para identificar imóveis com preço abaixo da média do bairro
        subquery = self.db_session.query(
            func.avg(Property.price).label('avg_price'),
            Property.neighborhood
        ).group_by(Property.neighborhood).subquery()
        
        opportunities = self.db_session.query(Property).join(
            subquery, Property.neighborhood == subquery.c.neighborhood
        ).filter(
            Property.price < subquery.c.avg_price * 0.9,  # 10% abaixo da média
            Property.is_active == True
        ).limit(limit).all()
        
        return [prop.to_dict() for prop in opportunities]