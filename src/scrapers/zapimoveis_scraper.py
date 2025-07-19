# src/scrapers/zapimoveis_scraper.py
"""
Scraper otimizado para ZapImóveis com foco em oportunidades
"""
import re
import time
from typing import List, Optional, Any
from selenium.webdriver.common.by import By

# Import direto sem relative imports  
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scrapers.base_scraper import BaseScraper
from models.property import Property, PropertySearch, PropertySource, PropertyType
from config.settings import settings

class ZapImoveisScraper(BaseScraper):
    """Scraper especializado para ZapImóveis"""
    
    def __init__(self):
        super().__init__(PropertySource.ZAPIMOVEIS)
    
    def _build_search_url(self, search: PropertySearch) -> str:
        """Constrói URL de busca do ZapImóveis"""
        base_url = settings.PORTAL_URLS['zapimoveis']
        city_mapping = settings.CITY_MAPPING['zapimoveis']
        
        city_code = city_mapping.get(search.city, 'rj+rio-de-janeiro')
        
        if search.property_type == PropertyType.APARTAMENTO:
            return f"{base_url}/venda/apartamentos/{city_code}/"
        elif search.property_type == PropertyType.CASA:
            return f"{base_url}/venda/casas/{city_code}/"
        else:
            return f"{base_url}/venda/apartamentos/{city_code}/"
    
    def _get_property_elements(self) -> List[Any]:
        """Obtém elementos de propriedades da página"""
        # Aguardar carregamento dos elementos
        time.sleep(5)  # Aumentar tempo de espera
        
        # Múltiplos seletores para diferentes layouts (atualizados)
        selectors = [
            '[data-testid*="card"]',  # Seletor atual do ZapImóveis
            '[data-testid="result-card-container"]',
            '.result-card',
            '[data-testid="property-card"]',
            '.property-card',
            '.listing-item'
        ]
        
        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector) if self.driver else []
            if elements:
                self.logger.info(f"Encontrados {len(elements)} elementos usando seletor: {selector}")
                # Filtrar elementos de propriedades (menos restritivo)
                property_elements = []
                for elem in elements:
                    try:
                        # Verificar se tem características de propriedade
                        text = self._extract_text_safe(elem).lower()
                        if any(word in text for word in ['r$', 'quarto', 'banho', 'm²', 'apartamento', 'casa', 'venda']) or len(text) > 50:
                            property_elements.append(elem)
                    except:
                        # Se der erro, incluir mesmo assim
                        property_elements.append(elem)
                
                if property_elements:
                    self.logger.info(f"Filtrados {len(property_elements)} elementos de propriedades válidas")
                    return property_elements[:20]  # Limitar para evitar muitos elementos
        
        self.logger.warning("Nenhum elemento de propriedade encontrado")
        return []
    
    def _extract_property_data(self, element: Any) -> Optional[Property]:
        """Extrai dados completos da propriedade"""
        try:
            # Título
            title = self._extract_title(element)
            if not title:
                return None
            
            # URL
            url = self._extract_url(element)
            if not url:
                return None
            
            # Preço
            price = self._extract_price_from_element(element)
            
            # Características
            bedrooms = self._extract_bedrooms(element)
            bathrooms = self._extract_bathrooms(element)
            area = self._extract_area_from_element(element)
            parking = self._extract_parking(element)
            
            # Localização
            address = self._extract_address(element)
            neighborhood = self._extract_neighborhood(element)
            
            # Badges especiais (OPORTUNIDADE, LANÇAMENTO)
            badges = self._extract_badges(element)
            
            # Criar objeto Property
            property_data = Property(
                url=url,
                title=title,
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                area=area,
                parking_spaces=parking,
                address=address,
                neighborhood=neighborhood,
                property_type=PropertyType.APARTAMENTO,
                source=PropertySource.ZAPIMOVEIS,
                badges=badges
            )
            
            return property_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da propriedade: {e}")
            return None
    
    def _extract_title(self, element: Any) -> str:
        """Extrai título da propriedade"""
        selectors = [
            'h2[data-testid="property-card-title"]',
            '.property-card__title',
            'h2.listing-card__title',
            'h3.result-card__title',
            '.listing-item__title'
        ]
        
        for selector in selectors:
            try:
                title_element = element.find_element(By.CSS_SELECTOR, selector)
                title = self._extract_text_safe(title_element)
                if title:
                    return title
            except:
                continue
        
        return ""
    
    def _extract_url(self, element: Any) -> str:
        """Extrai URL da propriedade"""
        try:
            link_element = element.find_element(By.CSS_SELECTOR, 'a')
            url = self._extract_attribute_safe(link_element, 'href')
            
            if url and not url.startswith('http'):
                url = f"https://www.zapimoveis.com.br{url}"
            
            return url
        except:
            return ""
    
    def _extract_price_from_element(self, element: Any) -> Optional[float]:
        """Extrai preço com múltiplas estratégias"""
        price_selectors = [
            '[data-testid="property-card-price"]',
            '.property-card__price',
            '.listing-card__price',
            '.result-card__price',
            '.price'
        ]
        
        for selector in price_selectors:
            try:
                price_element = element.find_element(By.CSS_SELECTOR, selector)
                price_text = self._extract_text_safe(price_element)
                if price_text:
                    price = self._parse_price(price_text)
                    if price:
                        return price
            except:
                continue
        
        return None
    
    def _parse_price(self, text: str) -> Optional[float]:
        """Converte texto de preço para float"""
        if not text:
            return None
        
        # Remove espaços e caracteres especiais
        clean_text = text.replace(' ', '').replace('\n', '')
        
        # Padrões específicos do ZapImóveis
        price_patterns = [
            r'R\$\s*([\d,.]+)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d+\.?\d*\.?\d*)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, clean_text)
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    price = float(price_str)
                    # Validação de faixa de preços
                    if 10000 <= price <= 50000000:
                        return price
                except:
                    continue
        
        return None
    
    def _extract_bedrooms(self, element: Any) -> Optional[int]:
        """Extrai número de quartos"""
        return self._extract_numeric_feature(element, ['quarto', 'dorm', 'bedroom'])
    
    def _extract_bathrooms(self, element: Any) -> Optional[int]:
        """Extrai número de banheiros"""
        return self._extract_numeric_feature(element, ['banho', 'bath', 'wc'])
    
    def _extract_parking(self, element: Any) -> Optional[int]:
        """Extrai número de vagas"""
        return self._extract_numeric_feature(element, ['vaga', 'garage', 'parking'])
    
    def _extract_numeric_feature(self, element: Any, keywords: List[str]) -> Optional[int]:
        """Extrai características numéricas (quartos, banheiros, vagas)"""
        try:
            text = self._extract_text_safe(element)
            
            for keyword in keywords:
                pattern = rf'(\d+)\s*{keyword}'
                match = re.search(pattern, text.lower())
                if match:
                    return int(match.group(1))
        except:
            pass
        
        return None
    
    def _extract_area_from_element(self, element: Any) -> Optional[float]:
        """Extrai área da propriedade"""
        try:
            text = self._extract_text_safe(element)
            return self._parse_area(text)
        except:
            return None
    
    def _parse_area(self, text: str) -> Optional[float]:
        """Converte texto de área para float"""
        if not text:
            return None
            
        area_patterns = [
            r'(\d+)\s*m²',
            r'(\d+)\s*m2',
            r'(\d+),(\d+)\s*m²',
            r'Área:\s*(\d+)'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    if len(match.groups()) > 1:
                        # Área com decimal (ex: 85,5 m²)
                        return float(f"{match.group(1)}.{match.group(2)}")
                    else:
                        return float(match.group(1))
                except:
                    continue
        
        return None
    
    def _extract_address(self, element: Any) -> str:
        """Extrai endereço"""
        address_selectors = [
            '[data-testid="property-card-address"]',
            '.property-card__address',
            '.listing-card__address',
            '.result-card__address'
        ]
        
        for selector in address_selectors:
            try:
                address_element = element.find_element(By.CSS_SELECTOR, selector)
                address = self._extract_text_safe(address_element)
                if address:
                    return address
            except:
                continue
        
        return ""
    
    def _extract_neighborhood(self, element: Any) -> str:
        """Extrai bairro do endereço"""
        address = self._extract_address(element)
        if address:
            # Extrair bairro (geralmente após a primeira vírgula)
            parts = address.split(',')
            if len(parts) >= 2:
                return parts[1].strip()
        
        return ""
    
    def _extract_badges(self, element: Any) -> List[str]:
        """Extrai badges especiais (OPORTUNIDADE, LANÇAMENTO, etc.)"""
        badges = []
        
        badge_selectors = [
            '.property-card__badge',
            '.listing-card__badge',
            '.result-card__badge',
            '.badge',
            '[data-testid="property-badge"]'
        ]
        
        for selector in badge_selectors:
            try:
                badge_elements = element.find_elements(By.CSS_SELECTOR, selector)
                for badge_element in badge_elements:
                    badge_text = self._extract_text_safe(badge_element).upper()
                    if badge_text and badge_text not in badges:
                        badges.append(badge_text)
            except:
                continue
        
        # Buscar por badges no texto geral também
        text = self._extract_text_safe(element).upper()
        special_badges = ['OPORTUNIDADE', 'LANÇAMENTO', 'PROMOÇÃO', 'DESTAQUE']
        
        for badge in special_badges:
            if badge in text and badge not in badges:
                badges.append(badge)
        
        return badges
