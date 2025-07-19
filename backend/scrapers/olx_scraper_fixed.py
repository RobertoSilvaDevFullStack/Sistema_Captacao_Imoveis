#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper atualizado para OLX - versão 2025 com seletores corretos
"""

import time
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

class OLXScraperFixed:
    """Scraper para extrair dados de imóveis do OLX - versão corrigida 2025"""
    
    def __init__(self):
        self.driver = None
        self.session = None
        self._setup_driver()
        self._setup_session()
        
    def _setup_driver(self):
        """Configura o driver Chrome com configurações otimizadas"""
        chrome_options = Options()
        
        # Configurações anti-detecção
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent realista
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        
        # Configurações de performance
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Remove propriedades que identificam automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logging.info("OLX Scraper inicializado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao inicializar driver: {e}")
            raise
    
    def _setup_session(self):
        """Configura sessão HTTP para requests adicionais"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_properties(self, search_url: str = None, max_pages: int = 3) -> List[Dict]:
        """Scraping principal - extrai propriedades do OLX"""
        if not search_url:
            # URL específica que funciona para imóveis
            search_url = "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj"
        
        logging.info(f"Iniciando scraping OLX: {search_url}")
        
        try:
            # Obter links de propriedades
            property_links = self.get_property_links(search_url, max_pages)
            
            if not property_links:
                logging.warning("Nenhum link de propriedade encontrado")
                return []
            
            # Extrair dados de cada propriedade
            properties = []
            for i, link in enumerate(property_links[:20]):  # Limitar para teste
                try:
                    logging.info(f"Extraindo dados da propriedade {i+1}/{len(property_links[:20])}: {link}")
                    property_data = self.extract_property_data(link)
                    if property_data:
                        properties.append(property_data)
                    
                    # Rate limiting
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logging.error(f"Erro ao extrair propriedade {link}: {e}")
                    continue
            
            logging.info(f"Scraping concluído. {len(properties)} propriedades extraídas")
            return properties
            
        except Exception as e:
            logging.error(f"Erro no scraping: {e}")
            return []
    
    def get_property_links(self, search_url: str, max_pages: int = 3) -> List[str]:
        """Extrai links de propriedades das páginas de resultado"""
        all_links = []
        
        for page in range(1, max_pages + 1):
            try:
                # URL da página específica
                page_url = f"{search_url}?o={page}" if page > 1 else search_url
                logging.info(f"Buscando links em: {page_url}")
                
                self.driver.get(page_url)
                time.sleep(random.uniform(4, 7))
                
                page_links = self._extract_links_from_page(all_links)
                logging.info(f"Encontrados {len(page_links)} links únicos na página {page}")
                
                if not page_links:
                    logging.warning(f"Nenhum link encontrado na página {page}, parando busca")
                    break
                    
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logging.error(f"Erro ao processar página {page}: {e}")
                continue
        
        logging.info(f"Total de {len(all_links)} links únicos encontrados")
        return all_links
    
    def _extract_links_from_page(self, all_links: List[str]) -> List[str]:
        """Extrai links de propriedades de uma página usando seletores 2025"""
        property_elements = []
        
        try:
            # Aguarda carregamento
            time.sleep(3)
            
            # Seletor correto para OLX 2025
            elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="adcard-link"]')
            logging.info(f"✅ Encontrados {len(elements)} elementos com data-testid='adcard-link'")
            
            page_links = []
            for elem in elements:
                try:
                    href = elem.get_attribute('href')
                    title = elem.get_attribute('title') or ''
                    
                    if not href or not href.startswith('http'):
                        continue
                    
                    # Verificar se é um anúncio de imóvel real
                    if 'olx.com.br' in href:
                        # Filtrar apenas imóveis (apartamentos, casas, etc.)
                        is_real_estate = any(keyword in title.lower() for keyword in [
                            'apartamento', 'casa', 'kitnet', 'quarto', 'imovel', 'cobertura',
                            'loft', 'studio', 'sobrado', 'chácara', 'terreno'
                        ])
                        
                        # Ou verificar pela estrutura da URL (links específicos de anúncios)
                        is_specific_ad = (
                            '/imoveis/' in href and 
                            len(href.split('/')) > 6 and
                            '-' in href.split('/')[-1] and
                            not any(exclude in href for exclude in [
                                'estado-', 'categoria', 'buscar', 'filtro', 
                                'conta.olx', 'ajuda.olx', 'planoprofissional'
                            ])
                        )
                        
                        if is_real_estate or is_specific_ad:
                            clean_href = href.split('?')[0].split('#')[0]
                            
                            if clean_href not in all_links:
                                page_links.append(clean_href)
                                all_links.append(clean_href)
                                logging.debug(f"✅ Link de imóvel: {title[:50]}... | {clean_href}")
                        
                except Exception as e:
                    logging.debug(f"Erro ao processar elemento: {e}")
                    continue
            
            return page_links
            
        except Exception as e:
            logging.error(f"Erro na extração de links: {e}")
            return []
    
    def extract_property_data(self, url: str) -> Optional[Dict]:
        """Extrai dados detalhados de uma propriedade"""
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            # Aguarda carregamento da página
            wait = WebDriverWait(self.driver, 10)
            
            property_data = {
                'url': url,
                'title': '',
                'price': '',
                'location': '',
                'area': '',
                'bedrooms': '',
                'bathrooms': '',
                'description': '',
                'contact': '',
                'images': [],
                'features': [],
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extrair título
            try:
                title_selectors = [
                    'h1[data-testid="ad-title"]',
                    'h1',
                    '.ad-title h1',
                    '[data-testid="title"] h1'
                ]
                for selector in title_selectors:
                    try:
                        title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        property_data['title'] = title_elem.text.strip()
                        break
                    except:
                        continue
            except Exception as e:
                logging.debug(f"Erro ao extrair título: {e}")
            
            # Extrair preço
            try:
                price_selectors = [
                    '[data-testid="price-value"]',
                    '.price-value',
                    '.ad-price',
                    '[data-testid="ad-price"]'
                ]
                for selector in price_selectors:
                    try:
                        price_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        property_data['price'] = price_elem.text.strip()
                        break
                    except:
                        continue
            except Exception as e:
                logging.debug(f"Erro ao extrair preço: {e}")
            
            # Extrair localização
            try:
                location_selectors = [
                    '[data-testid="ad-location"]',
                    '.ad-location',
                    '.location-info',
                    '[data-testid="location"]'
                ]
                for selector in location_selectors:
                    try:
                        location_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        property_data['location'] = location_elem.text.strip()
                        break
                    except:
                        continue
            except Exception as e:
                logging.debug(f"Erro ao extrair localização: {e}")
            
            # Extrair descrição
            try:
                desc_selectors = [
                    '[data-testid="ad-description"]',
                    '.ad-description',
                    '.description-content',
                    '[data-testid="description"]'
                ]
                for selector in desc_selectors:
                    try:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        property_data['description'] = desc_elem.text.strip()
                        break
                    except:
                        continue
            except Exception as e:
                logging.debug(f"Erro ao extrair descrição: {e}")
            
            # Extrair características (área, quartos, etc.)
            try:
                features = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-feature"], .property-feature, .ad-details li')
                for feature in features:
                    text = feature.text.strip().lower()
                    if 'm²' in text or 'metros' in text:
                        property_data['area'] = feature.text.strip()
                    elif 'quarto' in text or 'dormitório' in text:
                        property_data['bedrooms'] = feature.text.strip()
                    elif 'banheiro' in text:
                        property_data['bathrooms'] = feature.text.strip()
                    
                    property_data['features'].append(feature.text.strip())
            except Exception as e:
                logging.debug(f"Erro ao extrair características: {e}")
            
            # Validar se extraiu dados mínimos
            if property_data['title'] or property_data['price']:
                return property_data
            else:
                logging.warning(f"Dados insuficientes extraídos de {url}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao extrair dados de {url}: {e}")
            return None
    
    def close(self):
        """Fecha o driver e sessão"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("OLX Scraper fechado.")
        except Exception as e:
            logging.error(f"Erro ao fechar scraper: {e}")
        
        try:
            if self.session:
                self.session.close()
        except Exception as e:
            logging.error(f"Erro ao fechar sessão: {e}")

# Alias para compatibilidade
OLXScraper = OLXScraperFixed
