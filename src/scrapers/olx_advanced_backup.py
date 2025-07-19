#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OLX Scraper Melhorado
Extrai imóveis recém-adicionados e mais relevantes
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

class OLXScraperAdvanced:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def _setup_driver(self):
        """Configura o driver Chrome com opções otimizadas"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Acelera carregamento
        chrome_options.add_argument('--disable-javascript')  # Para alguns casos
        
        # User agents rotativos
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def _extract_price(self, text):
        """Extrai preço do texto"""
        if not text:
            return None
        
        # Busca padrões de preço brasileiro
        price_patterns = [
            r'R\$\s*([\d,.]+)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d+\.?\d*\.?\d*)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text.replace(' ', ''))
            if match:
                price_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    return float(price_str)
                except:
                    continue
        return None
    
    def _extract_area(self, text):
        """Extrai área do texto"""
        if not text:
            return None
            
        area_patterns = [
            r'(\d+)\s*m²',
            r'(\d+)\s*m2',
            r'(\d+)\s*metros'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        return None
    
    def _extract_rooms(self, text):
        """Extrai número de quartos do texto"""
        if not text:
            return None
            
        room_patterns = [
            r'(\d+)\s*quarto',
            r'(\d+)\s*dormitório',
            r'(\d+)\s*qto'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        return None
    
    def scrape_properties(self, url, max_results=20):
        """Scraping principal do OLX"""
        self.logger.info(f"Iniciando scraping OLX: {url}")
        
        driver = None
        properties = []
        
        try:
            driver = self._setup_driver()
            driver.get(url)
            
            # Aguarda carregar a página
            time.sleep(random.uniform(3, 5))
            
            # Seletores para os cards de imóveis do OLX
            property_selectors = [
                '[data-ds-component="DS-NewAdTile"]',
                '.olx-ad-card',
                '[data-testid="ad-card"]',
                '.sc-bwzfXH'
            ]
            
            property_cards = []
            for selector in property_selectors:
                try:
                    cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        property_cards = cards[:max_results]
                        self.logger.info(f"Encontrados {len(cards)} cards com seletor: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"Seletor {selector} não funcionou: {e}")
                    continue
            
            if not property_cards:
                self.logger.warning("Nenhum card de propriedade encontrado")
                return []
            
            for i, card in enumerate(property_cards[:max_results]):
                try:
                    # Scroll para o elemento
                    driver.execute_script("arguments[0].scrollIntoView();", card)
                    time.sleep(random.uniform(0.5, 1))
                    
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
                        'source': 'OLX',
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Extrair título
                    title_selectors = [
                        'h2', 'h3', '.olx-text', 
                        '[data-testid="ad-title"]',
                        '.sc-bwzfXH h2', '.sc-bwzfXH h3'
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = card.find_element(By.CSS_SELECTOR, selector)
                            if title_elem and title_elem.text.strip():
                                property_data['title'] = title_elem.text.strip()
                                break
                        except:
                            continue
                    
                    # Extrair preço
                    price_selectors = [
                        '[data-testid="ad-price"]',
                        '.olx-text--title',
                        '.price', '.valor',
                        'span[class*="price"]',
                        'div[class*="price"]'
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
                    
                    # Extrair URL
                    try:
                        link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                        href = link_elem.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                property_data['url'] = f"https://www.olx.com.br{href}"
                            else:
                                property_data['url'] = href
                    except:
                        pass
                    
                    # Extrair localização
                    location_selectors = [
                        '[data-testid="ad-location"]',
                        '.olx-text--caption',
                        '.location', '.endereco'
                    ]
                    
                    for selector in location_selectors:
                        try:
                            location_elem = card.find_element(By.CSS_SELECTOR, selector)
                            if location_elem and location_elem.text.strip():
                                location_text = location_elem.text.strip()
                                property_data['address'] = location_text
                                
                                # Tenta extrair bairro (última parte antes da cidade)
                                parts = location_text.split(',')
                                if len(parts) >= 2:
                                    property_data['neighborhood'] = parts[-2].strip()
                                break
                        except:
                            continue
                    
                    # Extrair características do texto completo
                    full_text = card.text
                    if full_text:
                        property_data['area'] = self._extract_area(full_text)
                        property_data['bedrooms'] = self._extract_rooms(full_text)
                        
                        # Busca por características especiais
                        if 'garagem' in full_text.lower() or 'vaga' in full_text.lower():
                            property_data['parking_spaces'] = 1
                        
                        # Amenidades básicas
                        amenities = []
                        if 'piscina' in full_text.lower():
                            amenities.append('Piscina')
                        if 'elevador' in full_text.lower():
                            amenities.append('Elevador')
                        if 'portaria' in full_text.lower():
                            amenities.append('Portaria 24h')
                        
                        property_data['amenities'] = amenities
                    
                    # Só adiciona se tiver dados mínimos
                    if property_data['title'] or property_data['price']:
                        properties.append(property_data)
                        self.logger.info(f"Propriedade {i+1} extraída: {property_data['title'][:50] if property_data['title'] else 'Sem título'}")
                
                except Exception as e:
                    self.logger.error(f"Erro ao extrair propriedade {i+1}: {e}")
                    continue
            
            self.logger.info(f"Scraping OLX concluído: {len(properties)} propriedades extraídas")
            
        except Exception as e:
            self.logger.error(f"Erro no scraping OLX: {e}")
            
        finally:
            if driver:
                driver.quit()
        
        return properties
