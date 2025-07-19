#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper VivaReal - versão 2025 com bypass Cloudflare avançado
"""

import time
import random
import logging
import undetected_chromedriver as uc
from typing import List, Dict, Optional
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
from bs4 import BeautifulSoup

class VivaRealScraperAdvanced:
    """Scraper VivaReal com bypass Cloudflare avançado"""
    
    def __init__(self):
        self.driver = None
        self.session = None
        self._setup_session()
        
    def _setup_session(self):
        """Configura sessão HTTP com headers realistas"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def _setup_undetected_driver(self):
        """Configura driver com undetected-chromedriver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            self.driver = uc.Chrome(options=options, version_main=None)
            logging.info("VivaReal undetected driver configurado")
            return True
        except Exception as e:
            logging.error(f"Erro ao configurar undetected driver: {e}")
            return False
    
    def scrape_properties(self, search_url: str, max_pages: int = 3) -> List[Dict]:
        """Scraping usando múltiplas estratégias"""
        logging.info(f"Iniciando scraping VivaReal: {search_url}")
        
        # Estratégia 1: Requests + BeautifulSoup
        properties = self._try_requests_scraping(search_url)
        if properties:
            logging.info(f"Sucesso com requests: {len(properties)} propriedades")
            return properties
        
        # Estratégia 2: Undetected ChromeDriver
        if self._setup_undetected_driver():
            properties = self._try_selenium_scraping(search_url, max_pages)
            if properties:
                logging.info(f"Sucesso com undetected chrome: {len(properties)} propriedades")
                return properties
        
        # Estratégia 3: API direta (se disponível)
        properties = self._try_api_scraping(search_url)
        if properties:
            logging.info(f"Sucesso com API: {len(properties)} propriedades")
            return properties
        
        logging.warning("Todas as estratégias falharam")
        return []
    
    def _try_requests_scraping(self, search_url: str) -> List[Dict]:
        """Tenta scraping com requests puro"""
        try:
            logging.info("Tentando scraping com requests...")
            
            # Fazer request inicial
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Procurar por dados JSON embutidos
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('property' in script.string.lower() or 'listing' in script.string.lower()):
                        # Tentar extrair dados JSON
                        try:
                            import json
                            import re
                            
                            # Procurar por padrões JSON
                            json_pattern = r'(\{.*?"listings".*?\})'
                            matches = re.findall(json_pattern, script.string, re.DOTALL)
                            
                            for match in matches:
                                data = json.loads(match)
                                return self._parse_json_data(data)
                        except:
                            continue
                
                # Fallback: parsing HTML tradicional
                return self._parse_html_listings(soup)
            
        except Exception as e:
            logging.debug(f"Requests scraping falhou: {e}")
        
        return []
    
    def _try_selenium_scraping(self, search_url: str, max_pages: int) -> List[Dict]:
        """Scraping com Selenium undetected"""
        try:
            logging.info("Tentando scraping com undetected selenium...")
            
            self.driver.get(search_url)
            time.sleep(10)  # Aguarda carregamento
            
            # Verificar se passou do Cloudflare
            if "vivareal.com.br" in self.driver.current_url.lower():
                logging.info("Bypass Cloudflare bem-sucedido!")
                
                properties = []
                for page in range(1, max_pages + 1):
                    page_properties = self._extract_selenium_properties()
                    properties.extend(page_properties)
                    
                    if not page_properties:
                        break
                    
                    # Navegar para próxima página
                    if page < max_pages:
                        self._navigate_next_page()
                
                return properties
            
        except Exception as e:
            logging.debug(f"Selenium scraping falhou: {e}")
        
        return []
    
    def _try_api_scraping(self, search_url: str) -> List[Dict]:
        """Tenta usar API direta do VivaReal"""
        try:
            logging.info("Tentando API direta...")
            
            # URLs de API conhecidas do VivaReal
            api_endpoints = [
                "https://glue-api.vivareal.com/v2/listings",
                "https://api.vivareal.com/v1/listings"
            ]
            
            for endpoint in api_endpoints:
                try:
                    params = {
                        'addressCity': 'Rio de Janeiro',
                        'addressState': 'Rio de Janeiro',
                        'businessType': 'SALE',
                        'propertyType': 'APARTMENT',
                        'size': 20
                    }
                    
                    response = self.session.get(endpoint, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_api_data(data)
                        
                except Exception as e:
                    logging.debug(f"API endpoint {endpoint} falhou: {e}")
                    continue
            
        except Exception as e:
            logging.debug(f"API scraping falhou: {e}")
        
        return []
    
    def _parse_json_data(self, data: dict) -> List[Dict]:
        """Parse dados JSON extraídos"""
        properties = []
        try:
            listings = data.get('listings', [])
            for listing in listings[:20]:  # Limitar a 20
                property_data = {
                    'title': listing.get('title', ''),
                    'price': listing.get('price', ''),
                    'location': listing.get('address', {}).get('city', ''),
                    'area': listing.get('area', ''),
                    'bedrooms': listing.get('bedrooms', ''),
                    'bathrooms': listing.get('bathrooms', ''),
                    'url': listing.get('url', ''),
                    'source': 'VivaReal',
                    'scraped_at': datetime.now().isoformat()
                }
                properties.append(property_data)
        except Exception as e:
            logging.debug(f"Erro ao parse JSON: {e}")
        
        return properties
    
    def _parse_html_listings(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML tradicional"""
        properties = []
        try:
            # Seletores conhecidos do VivaReal
            listings = soup.find_all(['div', 'article'], class_=lambda x: x and ('listing' in x.lower() or 'property' in x.lower()))
            
            for listing in listings[:20]:
                property_data = {
                    'title': '',
                    'price': '',
                    'location': '',
                    'area': '',
                    'bedrooms': '',
                    'bathrooms': '',
                    'url': '',
                    'source': 'VivaReal',
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Extrair título
                title_elem = listing.find(['h1', 'h2', 'h3'], class_=lambda x: x and 'title' in x.lower())
                if title_elem:
                    property_data['title'] = title_elem.get_text(strip=True)
                
                # Extrair preço
                price_elem = listing.find(class_=lambda x: x and 'price' in x.lower())
                if price_elem:
                    property_data['price'] = price_elem.get_text(strip=True)
                
                # Extrair localização
                location_elem = listing.find(class_=lambda x: x and ('location' in x.lower() or 'address' in x.lower()))
                if location_elem:
                    property_data['location'] = location_elem.get_text(strip=True)
                
                if property_data['title'] or property_data['price']:
                    properties.append(property_data)
                    
        except Exception as e:
            logging.debug(f"Erro ao parse HTML: {e}")
        
        return properties
    
    def _extract_selenium_properties(self) -> List[Dict]:
        """Extrai propriedades usando Selenium"""
        properties = []
        try:
            # Aguardar carregamento
            wait = WebDriverWait(self.driver, 10)
            
            # Seletores do VivaReal
            property_selectors = [
                '[data-testid="property-card"]',
                '.property-card',
                '.listing-card',
                '[class*="listing"]'
            ]
            
            for selector in property_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        for elem in elements[:20]:
                            property_data = self._extract_property_from_element(elem)
                            if property_data:
                                properties.append(property_data)
                        break
                except:
                    continue
                    
        except Exception as e:
            logging.debug(f"Erro na extração Selenium: {e}")
        
        return properties
    
    def _extract_property_from_element(self, element) -> Optional[Dict]:
        """Extrai dados de um elemento de propriedade"""
        try:
            property_data = {
                'title': '',
                'price': '',
                'location': '',
                'area': '',
                'bedrooms': '',
                'bathrooms': '',
                'url': '',
                'source': 'VivaReal',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Título
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, 'h2, h3, [data-testid*="title"]')
                property_data['title'] = title_elem.text.strip()
            except:
                pass
            
            # Preço
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, '[data-testid*="price"], .price')
                property_data['price'] = price_elem.text.strip()
            except:
                pass
            
            # URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                property_data['url'] = link_elem.get_attribute('href')
            except:
                pass
            
            if property_data['title'] or property_data['price']:
                return property_data
            
        except Exception as e:
            logging.debug(f"Erro ao extrair elemento: {e}")
        
        return None
    
    def _navigate_next_page(self):
        """Navega para próxima página"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="next-page"], .next-page, [aria-label*="próxima"]')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(5)
        except:
            pass
    
    def close(self):
        """Fecha recursos"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("VivaReal driver fechado")
        except Exception as e:
            logging.error(f"Erro ao fechar driver: {e}")
        
        try:
            if self.session:
                self.session.close()
        except:
            pass
