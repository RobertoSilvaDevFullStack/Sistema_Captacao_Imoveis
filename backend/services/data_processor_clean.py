#!/usr/bin/env python3
# data_processor.py

import re
import logging
from typing import Dict, Any, Optional, List

class PropertyDataProcessor:
    """Classe para processar e limpar dados de propriedades extraídos do VivaReal"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clean_price(self, price_text: str) -> Optional[int]:
        """
        Extrai e limpa o preço, convertendo para valor numérico
        
        Args:
            price_text: Texto do preço (ex: "R$ 360.000", "Casa para comprar...")
            
        Returns:
            Preço como inteiro ou None se não encontrado
        """
        if not price_text:
            return None
            
        try:
            # Procura por padrões de preço
            price_patterns = [
                r'R\$\s*([\d.,]+)',  # R$ 360.000
                r'RS\s*([\d.,]+)',   # RS 360000
                r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*(?=\n|$|Cond)'  # 360.000 antes de quebra ou "Cond"
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, price_text)
                if matches:
                    price_str = matches[0]
                    # Remove pontos de milhares e converte vírgula para ponto
                    price_str = price_str.replace('.', '').replace(',', '.')
                    
                    # Converte para float e depois para int
                    price_value = int(float(price_str))
                    
                    # Valida se é um preço razoável (entre 10k e 50M)
                    if 10000 <= price_value <= 50000000:
                        return price_value
                        
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Erro ao processar preço '{price_text}': {e}")
            
        return None
    
    def clean_bedrooms(self, bedrooms_text: str) -> Optional[int]:
        """
        Extrai número de quartos
        
        Args:
            bedrooms_text: Texto contendo informação de quartos
            
        Returns:
            Número de quartos como inteiro ou None
        """
        if not bedrooms_text:
            return None
            
        try:
            # Procura por padrões como "3 quartos", "Quantidade de quartos\n3"
            patterns = [
                r'(\d+)\s*quartos?',
                r'quartos?\s*(\d+)',
                r'Quantidade de quartos\s*\n?\s*(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, bedrooms_text, re.IGNORECASE)
                if match:
                    bedrooms = int(match.group(1))
                    # Valida número razoável de quartos (0-20)
                    if 0 <= bedrooms <= 20:
                        return bedrooms
                        
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Erro ao processar quartos '{bedrooms_text}': {e}")
            
        return None
    
    def clean_bathrooms(self, bathrooms_text: str) -> Optional[int]:
        """
        Extrai número de banheiros
        
        Args:
            bathrooms_text: Texto contendo informação de banheiros
            
        Returns:
            Número de banheiros como inteiro ou None
        """
        if not bathrooms_text:
            return None
            
        try:
            # Procura por padrões como "2 banheiros", "Quantidade de banheiros\n2"
            patterns = [
                r'(\d+)\s*banheiros?',
                r'banheiros?\s*(\d+)',
                r'Quantidade de banheiros\s*\n?\s*(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, bathrooms_text, re.IGNORECASE)
                if match:
                    bathrooms = int(match.group(1))
                    # Valida número razoável de banheiros (0-20)
                    if 0 <= bathrooms <= 20:
                        return bathrooms
                        
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Erro ao processar banheiros '{bathrooms_text}': {e}")
            
        return None
    
    def clean_area(self, area_text: str) -> Optional[int]:
        """
        Extrai área em metros quadrados
        
        Args:
            area_text: Texto contendo informação de área
            
        Returns:
            Área como inteiro ou None
        """
        if not area_text:
            return None
            
        try:
            # Procura por padrões como "64 m²", "Tamanho do imóvel\n64 m²"
            patterns = [
                r'(\d+)\s*m²',
                r'(\d+)\s*metros?',
                r'Tamanho do imóvel\s*\n?\s*(\d+)\s*m²'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, area_text, re.IGNORECASE)
                if match:
                    area = int(match.group(1))
                    # Valida área razoável (10-10000 m²)
                    if 10 <= area <= 10000:
                        return area
                        
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Erro ao processar área '{area_text}': {e}")
            
        return None
    
    def clean_parking_spaces(self, parking_text: str) -> Optional[int]:
        """
        Extrai número de vagas de garagem
        
        Args:
            parking_text: Texto contendo informação de vagas
            
        Returns:
            Número de vagas como inteiro ou None
        """
        if not parking_text:
            return None
            
        try:
            # Procura por padrões como "1 vaga", "Quantidade de vagas de garagem\n1"
            patterns = [
                r'(\d+)\s*vagas?',
                r'vagas?\s*(\d+)',
                r'Quantidade de vagas de garagem\s*\n?\s*(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, parking_text, re.IGNORECASE)
                if match:
                    parking = int(match.group(1))
                    # Valida número razoável de vagas (0-20)
                    if 0 <= parking <= 20:
                        return parking
                        
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Erro ao processar vagas '{parking_text}': {e}")
            
        return None
    
    def extract_neighborhood(self, address_text: str) -> Optional[str]:
        """
        Extrai o bairro do endereço
        
        Args:
            address_text: Texto do endereço
            
        Returns:
            Nome do bairro ou None
        """
        if not address_text:
            return None
            
        try:
            # Remove prefixos comuns e extrai o bairro
            address_clean = address_text.replace('Apartamento', '').replace('Casa', '')
            
            # Procura por padrões como "Vila Costa Melo", "Jardim America Da Penha"
            parts = address_clean.split()
            
            # Procura por indicadores de bairro
            neighborhood_indicators = ['Vila', 'Jardim', 'Parque', 'Centro', 'Bairro']
            
            for i, part in enumerate(parts):
                if part.title() in neighborhood_indicators and i + 1 < len(parts):
                    # Pega o indicador + próximas 2-3 palavras
                    neighborhood_parts = parts[i:i+4]
                    neighborhood = ' '.join(neighborhood_parts).title()
                    # Remove números e caracteres especiais
                    neighborhood = re.sub(r'[0-9]+|[^a-zA-ZÀ-ÿ\s]', ' ', neighborhood)
                    neighborhood = ' '.join(neighborhood.split())  # Remove espaços extras
                    if len(neighborhood) > 3:
                        return neighborhood
                        
        except Exception as e:
            self.logger.warning(f"Erro ao extrair bairro '{address_text}': {e}")
            
        return None
    
    def extract_property_type(self, address_text: str) -> Optional[str]:
        """
        Extrai o tipo de propriedade (apartamento, casa, etc.)
        
        Args:
            address_text: Texto do endereço/título
            
        Returns:
            Tipo da propriedade ou None
        """
        if not address_text:
            return None
            
        address_lower = address_text.lower()
        
        property_types = {
            'apartamento': 'Apartamento',
            'casa': 'Casa',
            'sobrado': 'Sobrado',
            'cobertura': 'Cobertura',
            'kitnet': 'Kitnet',
            'loft': 'Loft',
            'terreno': 'Terreno',
            'lote': 'Lote'
        }
        
        for key, value in property_types.items():
            if key in address_lower:
                return value
                
        return None
    
    def process_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados brutos de uma propriedade, limpando e estruturando
        
        Args:
            raw_data: Dados brutos extraídos do scraper
            
        Returns:
            Dados processados e limpos
        """
        processed_data = {
            # Dados originais preservados
            'url': raw_data.get('url'),
            'raw_price': raw_data.get('price'),
            'raw_bedrooms': raw_data.get('bedrooms'),
            'raw_bathrooms': raw_data.get('bathrooms'),
            'raw_area': raw_data.get('area'),
            'raw_parking_spaces': raw_data.get('parking_spaces'),
            'raw_address': raw_data.get('address'),
            
            # Dados processados
            'price': self.clean_price(raw_data.get('price', '')),
            'bedrooms': self.clean_bedrooms(raw_data.get('bedrooms', '')),
            'bathrooms': self.clean_bathrooms(raw_data.get('bathrooms', '')),
            'area': self.clean_area(raw_data.get('area', '')),
            'parking_spaces': self.clean_parking_spaces(raw_data.get('parking_spaces', '')),
            'neighborhood': self.extract_neighborhood(raw_data.get('address', '')),
            'property_type': self.extract_property_type(raw_data.get('address', '')),
            
            # Métricas calculadas
            'price_per_sqm': None,
            'is_valid': False
        }
        
        # Calcula preço por m² se tiver preço e área
        if processed_data['price'] and processed_data['area']:
            processed_data['price_per_sqm'] = round(processed_data['price'] / processed_data['area'], 2)
        
        # Marca como válido se tiver dados essenciais
        processed_data['is_valid'] = all([
            processed_data['url'],
            processed_data['price'],
            processed_data['bedrooms'] is not None,
            processed_data['area']
        ])
        
        return processed_data
    
    def process_properties_list(self, raw_properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa uma lista de propriedades
        
        Args:
            raw_properties: Lista de dados brutos de propriedades
            
        Returns:
            Lista de propriedades processadas
        """
        processed_properties = []
        
        for raw_property in raw_properties:
            try:
                processed_property = self.process_property_data(raw_property)
                processed_properties.append(processed_property)
            except Exception as e:
                self.logger.error(f"Erro ao processar propriedade: {e}")
                continue
        
        # Filtra apenas propriedades válidas
        valid_properties = [p for p in processed_properties if p['is_valid']]
        
        self.logger.info(f"Processadas {len(processed_properties)} propriedades, {len(valid_properties)} válidas")
        
        return valid_properties
