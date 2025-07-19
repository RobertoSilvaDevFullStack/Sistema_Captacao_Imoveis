# src/models/property.py
"""
Modelos de dados para propriedades imobiliárias
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class PropertyType(Enum):
    """Tipos de propriedades"""
    APARTAMENTO = "apartamento"
    CASA = "casa"
    SOBRADO = "sobrado"
    KITNET = "kitnet"
    LOFT = "loft"
    COBERTURA = "cobertura"

class PropertySource(Enum):
    """Fontes de dados"""
    ZAPIMOVEIS = "zapimoveis"
    OLX = "olx"
    VIVAREAL = "vivareal"

class InvestmentRecommendation(Enum):
    """Recomendações de investimento"""
    EXCELENTE = "excelente"
    BOM = "bom"
    MODERADO = "moderado"
    BAIXO = "baixo"

@dataclass
class Property:
    """Modelo principal de propriedade"""
    
    # Identificação
    id: Optional[int] = None
    url: str = ""
    title: str = ""
    
    # Dados básicos
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    parking_spaces: Optional[int] = None
    
    # Localização
    address: str = ""
    neighborhood: str = ""
    city: str = ""
    state: str = ""
    
    # Classificação
    property_type: PropertyType = PropertyType.APARTAMENTO
    source: PropertySource = PropertySource.ZAPIMOVEIS
    
    # Métricas calculadas
    price_per_sqm: Optional[float] = None
    
    # Dados adicionais
    description: str = ""
    amenities: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)  # OPORTUNIDADE, LANÇAMENTO, etc.
    
    # Status
    is_valid: bool = False
    is_active: bool = True
    is_opportunity: bool = False
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Processamento pós-inicialização"""
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
            
        # Calcular preço por m²
        if self.price and self.area and self.area > 0:
            self.price_per_sqm = self.price / self.area
            
        # Verificar se é oportunidade baseado nos badges
        if any(badge.upper() in ['OPORTUNIDADE', 'LANÇAMENTO', 'PROMOÇÃO'] for badge in self.badges):
            self.is_opportunity = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
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
            'city': self.city,
            'state': self.state,
            'property_type': self.property_type.value if self.property_type else None,
            'source': self.source.value if self.source else None,
            'price_per_sqm': self.price_per_sqm,
            'description': self.description,
            'amenities': self.amenities,
            'images': self.images,
            'badges': self.badges,
            'is_valid': self.is_valid,
            'is_active': self.is_active,
            'is_opportunity': self.is_opportunity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Property':
        """Cria instância a partir de dicionário"""
        # Converter strings de volta para enums
        if 'property_type' in data and isinstance(data['property_type'], str):
            data['property_type'] = PropertyType(data['property_type'])
        
        if 'source' in data and isinstance(data['source'], str):
            data['source'] = PropertySource(data['source'])
            
        # Converter timestamps
        for field_name in ['created_at', 'updated_at', 'scraped_at']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
                
        return cls(**data)

@dataclass
class PropertySearch:
    """Parâmetros de busca de propriedades"""
    city: str = "rio-de-janeiro"
    property_type: PropertyType = PropertyType.APARTAMENTO
    portal: PropertySource = PropertySource.ZAPIMOVEIS
    max_results: int = 20
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    bedrooms: Optional[int] = None
    neighborhoods: List[str] = field(default_factory=list)
    only_opportunities: bool = False

@dataclass
class ScrapingResult:
    """Resultado de uma operação de scraping"""
    properties: List[Property] = field(default_factory=list)
    total_found: int = 0
    success: bool = False
    error_message: str = ""
    execution_time: float = 0.0
    source: PropertySource = PropertySource.ZAPIMOVEIS
