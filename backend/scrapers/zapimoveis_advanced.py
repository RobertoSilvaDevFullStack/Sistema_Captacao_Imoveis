#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ZapImóveis Scraper Melhorado
Foca em lançamentos, oportunidades e imóveis recém-adicionados
"""

import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

class ZapImoveisAdvanced:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def _setup_driver(self):
        """Configura o driver Chrome com opções anti-detecção"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-automation')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agents mais realísticos
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove propriedades que indicam automação
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _extract_price(self, text):
        """Extrai preço do texto com melhor precisão"""
        if not text:
            return None
        
        # Remove espaços e caracteres especiais
        clean_text = text.replace(' ', '').replace('\n', '')
        
        # Padrões específicos do ZapImóveis
        price_patterns = [
            r'R\$\s*([\d,.]+)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d+\.?\d*\.?\d*)',
            r'Valor\s*R\$\s*([\d,.]+)',
            r'Preço\s*R\$\s*([\d,.]+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, clean_text)
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    price = float(price_str)
                    # Validação básica (preços muito baixos ou altos são suspeitos)
                    if 10000 <= price <= 50000000:
                        return price
                except:
                    continue
        return None
    
    def _extract_area(self, text):
        """Extrai área com padrões específicos do ZapImóveis"""
        if not text:
            return None
            
        area_patterns = [
            r'(\d+)\s*m²',
            r'(\d+)\s*m2',
            r'(\d+),(\d+)\s*m²',  # Para áreas com decimal
            r'Área:\s*(\d+)',
            r'(\d+)\s*metros'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    if len(match.groups()) > 1:  # Área com decimal
                        return int(match.group(1))
                    return int(match.group(1))
                except:
                    continue
        return None
    
    def _extract_rooms_and_bathrooms(self, text):
        """Extrai quartos e banheiros do texto"""
        if not text:
            return None, None
        
        bedrooms = None
        bathrooms = None
        
        # Padrões para quartos
        bedroom_patterns = [
            r'(\d+)\s*quarto',
            r'(\d+)\s*dormitório',
            r'(\d+)\s*qto',
            r'(\d+)\s*dorm'
        ]
        
        for pattern in bedroom_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    bedrooms = int(match.group(1))
                    break
                except:
                    continue
        
        # Padrões para banheiros
        bathroom_patterns = [
            r'(\d+)\s*banheiro',
            r'(\d+)\s*wc',
            r'(\d+)\s*lavabo'
        ]
        
        for pattern in bathroom_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    bathrooms = int(match.group(1))
                    break
                except:
                    continue
        
        return bedrooms, bathrooms
    
    def _extract_badges(self, card):
        """Extrai badges como 'OPORTUNIDADE', 'LANÇAMENTO', etc."""
        badges = []
        badge_selectors = [
            '.listing-badge',
            '.badge',
            '.tag',
            '[class*="badge"]',
            '[class*="tag"]',
            '.highlight',
            '.promotional'
        ]
        
        for selector in badge_selectors:
            try:
                badge_elements = card.find_elements(By.CSS_SELECTOR, selector)
                for badge in badge_elements:
                    badge_text = badge.text.strip()
                    if badge_text and badge_text not in badges:
                        badges.append(badge_text)
            except:
                continue
        
        return badges
    
    def scrape_properties(self, url, max_results=20):
        """Scraping principal do ZapImóveis focado em lançamentos e oportunidades"""
        self.logger.info(f"Iniciando scraping ZapImóveis Advanced: {url}")
        
        driver = None
        properties = []
        
        try:
            driver = self._setup_driver()
            
            # Navega para a página
            driver.get(url)
            
            # Aguarda carregar
            time.sleep(random.uniform(4, 7))
            
            # Tenta aceitar cookies se aparecer
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="cookie-accept"], .cookie-accept, .lgpd-accept'))
                )
                cookie_button.click()
                time.sleep(1)
            except:
                pass
            
            # Seletores para os cards de imóveis do ZapImóveis
            property_selectors = [
                '[data-testid="listing-card"]',
                '.listing-card',
                '.property-card',
                '.card-container',
                '[class*="listing"]',
                '.result-card'
            ]
            
            property_cards = []
            for selector in property_selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        property_cards = cards[:max_results * 2]  # Pega mais para filtrar
                        self.logger.info(f"Encontrados {len(cards)} cards com seletor: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Seletor {selector} não funcionou: {e}")
                    continue
            
            if not property_cards:
                # Fallback: tenta extrair qualquer elemento que pareça um card
                self.logger.warning("Tentando fallback para encontrar cards...")
                try:
                    all_divs = driver.find_elements(By.TAG_NAME, 'div')
                    property_cards = [div for div in all_divs if 
                                    len(div.text) > 50 and 
                                    ('R$' in div.text or 'm²' in div.text)][:max_results]
                    self.logger.info(f"Fallback encontrou {len(property_cards)} possíveis cards")
                except:
                    pass
            
            if not property_cards:
                self.logger.warning("Nenhum card de propriedade encontrado")
                return []
            
            for i, card in enumerate(property_cards[:max_results]):
                try:
                    # Scroll para o elemento
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    property_data = {
                        'title': None,
                        'price': None,
                        'area': None,
                        'bedrooms': None,
                        'bathrooms': None,
                        'address': None,
                        'neighborhood': None,
                        'url': None,
                        'description': None,
                        'amenities': [],
                        'parking_spaces': None,
                        'source': 'ZapImoveis',
                        'scraped_at': datetime.now().isoformat(),
                        'badges': []
                    }
                    
                    # Texto completo do card para análise
                    full_text = card.text
                    
                    # Extrair badges (OPORTUNIDADE, LANÇAMENTO, etc.)
                    property_data['badges'] = self._extract_badges(card)
                    
                    # Extrair título
                    title_selectors = [
                        'h2', 'h3', 'h4',
                        '[data-testid="listing-title"]',
                        '.listing-title',
                        '.property-title',
                        '.card-title'
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, selector)
                            if title_elem and title_elem.text.strip():
                                property_data['title'] = title_elem.text.strip()
                                break
                        except:
                            continue
                    
                    # Se não achou título, pega a primeira linha relevante
                    if not property_data['title'] and full_text:
                        lines = full_text.split('\n')
                        for line in lines:
                            if len(line.strip()) > 10 and 'R$' not in line:
                                property_data['title'] = line.strip()
                                break
                    
                    # Extrair preço
                    price_selectors = [
                        '[data-testid="listing-price"]',
                        '.listing-price',
                        '.price',
                        '.valor',
                        '[class*="price"]'
                    ]
                    
                    for selector in price_selectors:
                        try:
                            price_elem = card.find_element(By.CSS_SELECTOR, selector)
                            if price_elem and price_elem.text.strip():
                                price = self._extract_price(price_elem.text)
                                if price:
                                    property_data['price'] = price
                                    break
                        except:
                            continue
                    
                    # Se não achou preço, procura no texto completo
                    if not property_data['price']:
                        property_data['price'] = self._extract_price(full_text)
                    
                    # Extrair URL
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                        href = link_elem.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                property_data['url'] = f"https://www.zapimoveis.com.br{href}"
                            else:
                                property_data['url'] = href
                    except:
                        pass
                    
                    # Extrair área, quartos e banheiros do texto completo
                    if full_text:
                        property_data['area'] = self._extract_area(full_text)
                        bedrooms, bathrooms = self._extract_rooms_and_bathrooms(full_text)
                        property_data['bedrooms'] = bedrooms
                        property_data['bathrooms'] = bathrooms
                        
                        # Busca por vagas de garagem
                        garage_patterns = [
                            r'(\d+)\s*vaga',
                            r'(\d+)\s*garagem',
                            r'garage.*?(\d+)'
                        ]
                        
                        for pattern in garage_patterns:
                            match = re.search(pattern, full_text.lower())
                            if match:
                                try:
                                    property_data['parking_spaces'] = int(match.group(1))
                                    break
                                except:
                                    continue
                        
                        # Amenidades do ZapImóveis
                        amenities = []
                        amenities_keywords = {
                            'piscina': 'Piscina',
                            'academia': 'Academia',
                            'elevador': 'Elevador',
                            'portaria': 'Portaria 24h',
                            'playground': 'Playground',
                            'churrasqueira': 'Churrasqueira',
                            'salão de festas': 'Salão de Festas',
                            'quadra': 'Quadra Esportiva'
                        }
                        
                        for keyword, amenity in amenities_keywords.items():
                            if keyword in full_text.lower():
                                amenities.append(amenity)
                        
                        property_data['amenities'] = amenities
                    
                    # Extrair endereço/localização
                    location_selectors = [
                        '[data-testid="listing-address"]',
                        '.listing-address',
                        '.property-address',
                        '.address',
                        '.location'
                    ]
                    
                    for selector in location_selectors:
                        try:
                            location_elem = card.find_element(By.CSS_SELECTOR, selector)
                            if location_elem and location_elem.text.strip():
                                location_text = location_elem.text.strip()
                                property_data['address'] = location_text
                                
                                # Tenta extrair bairro
                                parts = location_text.split(',')
                                if len(parts) >= 2:
                                    property_data['neighborhood'] = parts[0].strip()
                                break
                        except:
                            continue
                    
                    # Prioriza propriedades com badges especiais (OPORTUNIDADE, LANÇAMENTO)
                    priority_badges = ['OPORTUNIDADE', 'LANÇAMENTO', 'DESTAQUE', 'NOVIDADE']
                    has_priority = any(badge.upper() in priority_badges for badge in property_data['badges'])
                    
                    # Só adiciona se tiver dados mínimos válidos
                    if (property_data['title'] or property_data['price']) and property_data['price'] != 0:
                        if has_priority:
                            properties.insert(0, property_data)  # Coloca no início
                        else:
                            properties.append(property_data)
                        
                        self.logger.info(f"Propriedade {i+1} extraída: {property_data['title'][:50] if property_data['title'] else 'Sem título'} - R$ {property_data['price']}")
                
                except Exception as e:
                    self.logger.error(f"Erro ao extrair propriedade {i+1}: {e}")
                    continue
            
            # Remove duplicatas baseado na URL
            seen_urls = set()
            unique_properties = []
            for prop in properties:
                url = prop.get('url', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_properties.append(prop)
            
            self.logger.info(f"Scraping ZapImóveis concluído: {len(unique_properties)} propriedades únicas extraídas")
            
        except Exception as e:
            self.logger.error(f"Erro no scraping ZapImóveis: {e}")
            
        finally:
            if driver:
                driver.quit()
        
        return unique_properties[:max_results]
