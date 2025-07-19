#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper para OLX - versão final 2025 otimizada para listagens
"""

import time
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class OLXScraper:
    """Scraper otimizado para extrair dados de imóveis do OLX sem bloqueio"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self._setup_driver()
        
    def _setup_driver(self):
        """Configura o driver Chrome com configurações otimizadas"""
        chrome_options = Options()
        
        # Configurações anti-detecção aprimoradas
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logging.info("OLX Scraper inicializado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao inicializar driver: {e}")
            raise
    
    def scrape_properties(self, search_url: Optional[str] = None, max_pages: int = 3) -> List[Dict]:
        """Scraping principal - extrai propriedades do OLX das listagens"""
        if not search_url:
            search_url = "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj"
        
        logging.info(f"Iniciando scraping OLX: {search_url}")
        
        try:
            properties = []
            
            for page in range(1, max_pages + 1):
                try:
                    page_url = f"{search_url}?o={page}" if page > 1 else search_url
                    logging.info(f"Processando página {page}: {page_url}")
                    
                    if self.driver:
                        self.driver.get(page_url)
                    time.sleep(random.uniform(4, 7))
                    
                    page_properties = self._extract_properties_from_listing()
                    properties.extend(page_properties)
                    
                    logging.info(f"Extraídas {len(page_properties)} propriedades da página {page}")
                    
                    if not page_properties:
                        logging.warning(f"Nenhuma propriedade encontrada na página {page}, parando")
                        break
                    
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logging.error(f"Erro ao processar página {page}: {e}")
                    continue
            
            logging.info(f"Scraping concluído. {len(properties)} propriedades extraídas")
            return properties
            
        except Exception as e:
            logging.error(f"Erro no scraping: {e}")
            return []
    
    def _extract_properties_from_listing(self) -> List[Dict]:
        """Extrai dados das propriedades diretamente da listagem"""
        properties = []
        
        try:
            # Aguarda carregamento
            time.sleep(3)
            
            # Buscar todos os cards de anúncios
            if not self.driver:
                logging.error("Driver não inicializado")
                return []
                
            ad_cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="adcard-link"]')
            logging.info(f"Encontrados {len(ad_cards)} cards de anúncios")
            
            for i, card in enumerate(ad_cards):
                try:
                    property_data = self._extract_data_from_card(card)
                    if property_data:
                        properties.append(property_data)
                        logging.debug(f"Propriedade {i+1} extraída: {property_data.get('title', 'Sem título')[:50]}")
                except Exception as e:
                    logging.debug(f"Erro ao extrair card {i+1}: {e}")
                    continue
            
            return properties
            
        except Exception as e:
            logging.error(f"Erro na extração de propriedades: {e}")
            return []
    
    def _extract_data_from_card(self, card_element) -> Optional[Dict]:
        """Extrai dados de um card de anúncio na listagem"""
        try:
            property_data = {
                'title': '',
                'price': '',
                'location': '',
                'url': '',
                'area': '',
                'bedrooms': '',
                'bathrooms': '',
                'description': '',
                'features': [],
                'scraped_at': datetime.now().isoformat(),
                'source': 'OLX'
            }
            
            # URL do anúncio
            try:
                property_data['url'] = card_element.get_attribute('href') or ''
            except:
                pass
            
            # Título do anúncio
            try:
                title = card_element.get_attribute('title') or ''
                if not title:
                    # Buscar em elementos filhos
                    title_elements = card_element.find_elements(By.CSS_SELECTOR, 'h3, h2, .ad-title, [data-testid*="title"]')
                    if title_elements:
                        title = title_elements[0].text.strip()
                property_data['title'] = title
            except Exception as e:
                logging.debug(f"Erro ao extrair título: {e}")
            
            # Buscar informações dentro do card usando o contexto do elemento
            try:
                # Tentar encontrar o container pai do card
                parent = card_element
                for _ in range(3):  # Subir até 3 níveis para encontrar o container completo
                    try:
                        parent = parent.find_element(By.XPATH, '..')
                        # Verificar se tem informações de preço
                        price_elements = parent.find_elements(By.CSS_SELECTOR, '[data-testid*="price"], .price, .ad-price')
                        if price_elements:
                            break
                    except:
                        break
                
                # Extrair preço
                try:
                    price_selectors = [
                        '[data-testid*="price"]',
                        '.price',
                        '.ad-price',
                        'span[class*="price"]',
                        'div[class*="price"]'
                    ]
                    for selector in price_selectors:
                        price_elements = parent.find_elements(By.CSS_SELECTOR, selector)
                        for price_elem in price_elements:
                            price_text = price_elem.text.strip()
                            if price_text and ('R$' in price_text or 'mil' in price_text.lower()):
                                property_data['price'] = price_text
                                break
                        if property_data['price']:
                            break
                except Exception as e:
                    logging.debug(f"Erro ao extrair preço: {e}")
                
                # Extrair localização
                try:
                    location_selectors = [
                        '[data-testid*="location"]',
                        '.location',
                        '.ad-location',
                        'span[class*="location"]',
                        'div[class*="location"]'
                    ]
                    for selector in location_selectors:
                        location_elements = parent.find_elements(By.CSS_SELECTOR, selector)
                        for loc_elem in location_elements:
                            loc_text = loc_elem.text.strip()
                            if loc_text and len(loc_text) > 3:
                                property_data['location'] = loc_text
                                break
                        if property_data['location']:
                            break
                except Exception as e:
                    logging.debug(f"Erro ao extrair localização: {e}")
                
                # Extrair características (área, quartos, etc.) do texto visível
                try:
                    all_text = parent.text.lower()
                    
                    # Procurar por área
                    import re
                    area_match = re.search(r'(\d+)\s*m²', all_text)
                    if area_match:
                        property_data['area'] = f"{area_match.group(1)} m²"
                    
                    # Procurar por quartos
                    bedroom_patterns = [
                        r'(\d+)\s*quarto[s]?',
                        r'(\d+)\s*dormitório[s]?',
                        r'(\d+)\s*qto[s]?'
                    ]
                    for pattern in bedroom_patterns:
                        bedroom_match = re.search(pattern, all_text)
                        if bedroom_match:
                            property_data['bedrooms'] = f"{bedroom_match.group(1)} quartos"
                            break
                    
                    # Procurar por banheiros
                    bathroom_patterns = [
                        r'(\d+)\s*banheiro[s]?',
                        r'(\d+)\s*wc[s]?'
                    ]
                    for pattern in bathroom_patterns:
                        bathroom_match = re.search(pattern, all_text)
                        if bathroom_match:
                            property_data['bathrooms'] = f"{bathroom_match.group(1)} banheiros"
                            break
                    
                except Exception as e:
                    logging.debug(f"Erro ao extrair características: {e}")
                
            except Exception as e:
                logging.debug(f"Erro ao processar container do card: {e}")
            
            # Validar se tem dados mínimos
            if property_data['title'] or property_data['url']:
                # Filtrar apenas imóveis reais
                title_lower = property_data['title'].lower()
                url_lower = property_data['url'].lower()
                
                is_real_estate = any(keyword in title_lower + url_lower for keyword in [
                    'apartamento', 'casa', 'kitnet', 'quarto', 'imovel', 'cobertura',
                    'loft', 'studio', 'sobrado', 'chácara'
                ])
                
                if is_real_estate:
                    return property_data
            
            return None
            
        except Exception as e:
            logging.debug(f"Erro ao extrair dados do card: {e}")
            return None
    
    def close(self):
        """Fecha o driver"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("OLX Scraper fechado.")
        except Exception as e:
            logging.error(f"Erro ao fechar scraper: {e}")
