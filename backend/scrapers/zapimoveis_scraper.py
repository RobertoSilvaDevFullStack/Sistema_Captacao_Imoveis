# backend/scrapers/zapimoveis_scraper.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
import re
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.decorators import rate_limit

class ZapImoveisScraper:
    def __init__(self):
        """Inicializa o scraper ZapImóveis com configurações anti-detecção"""
        self.base_url = "https://www.zapimoveis.com.br"
        self.session_counter = 0
        self.max_operations_per_session = 15  # Reinicia sessão após N operações
        self.setup_driver()
        
    def setup_driver(self):
        """Configura o WebDriver com opções anti-detecção"""
        # Fecha driver anterior se existir
        self.close_driver()
        
        options = Options()
        
        # Configurações básicas
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--user-data-dir=/tmp/chrome_user_data_zap')
        options.add_argument('--remote-debugging-port=9224')
        
        # User-Agent rotation para parecer mais humano
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Opções anti-detecção
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-default-apps')

        # Inicializa o driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Remove indicadores de automação
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception:
            logging.debug("Webdriver property já foi definida ou não pode ser redefinida")
            
        self.driver.set_window_size(1366, 768)
        self.session_counter = 0
        
    def ensure_driver(self):
        """Garante que o driver está funcionando"""
        if not hasattr(self, 'driver') or self.driver is None or self.session_counter >= self.max_operations_per_session:
            self.setup_driver()
        
        # Testa se o driver ainda está responsivo
        try:
            self.driver.current_url
        except Exception:
            logging.info("Driver não responsivo, reiniciando...")
            self.setup_driver()
            
    def close_driver(self):
        """Fecha o driver atual"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    @rate_limit(calls_per_second=1)
    def get_property_links(self, search_url, max_pages=3):
        """Busca links de propriedades nas páginas de resultados"""
        try:
            self.ensure_driver()
            logging.info(f"Buscando links em: {search_url}")
            self.driver.get(search_url)
            time.sleep(random.uniform(4, 6))
            
            all_links = []
            
            for page in range(1, max_pages + 1):
                try:
                    logging.info(f"Processando página {page}")
                    
                    # Incrementa contador de sessão
                    self.session_counter += 1
                    
                    # Aguarda os elementos carregarem
                    wait = WebDriverWait(self.driver, 15)
                    
                    # Scroll para ativar lazy loading
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                    time.sleep(2)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(2)
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    
                    # Seletores possíveis para links de imóveis no ZapImóveis
                    possible_selectors = [
                        'a[href*="/imovel/"]',
                        'a.result-card__link',
                        'a.listing-wrapper__link',
                        'a[data-position]',
                        'div[data-position] a',
                        '.result-card a',
                        '.listing-wrapper a'
                    ]
                    
                    property_elements = []
                    for selector in possible_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                # Filtra links que realmente são de imóveis
                                valid_elements = []
                                for elem in elements:
                                    href = elem.get_attribute('href')
                                    if href and '/imovel/' in href and 'zapimoveis.com.br' in href:
                                        valid_elements.append(elem)
                                
                                if valid_elements:
                                    property_elements = valid_elements
                                    logging.info(f"Encontrados {len(valid_elements)} elementos com seletor: {selector}")
                                    break
                        except:
                            continue
                    
                    if not property_elements:
                        # Fallback: busca por qualquer link que contenha /imovel/
                        all_links_on_page = self.driver.find_elements(By.TAG_NAME, 'a')
                        for link in all_links_on_page:
                            href = link.get_attribute('href')
                            if href and '/imovel/' in href and 'zapimoveis.com.br' in href:
                                property_elements.append(link)
                    
                    page_links = []
                    for elem in property_elements:
                        href = elem.get_attribute('href')
                        if href and href not in all_links:
                            page_links.append(href)
                            all_links.append(href)
                    
                    logging.info(f"Encontrados {len(page_links)} links únicos na página {page}")
                    
                    # Tenta ir para próxima página
                    if page < max_pages:
                        try:
                            next_selectors = [
                                'button[title="Próxima página"]',
                                'a[title="Próxima página"]',
                                'button[aria-label="Próxima página"]',
                                '.pagination__item--next a',
                                'a.pagination-forward'
                            ]
                            
                            next_clicked = False
                            for selector in next_selectors:
                                try:
                                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    if next_button.is_enabled() and next_button.is_displayed():
                                        self.driver.execute_script("arguments[0].click();", next_button)
                                        time.sleep(random.uniform(4, 6))
                                        next_clicked = True
                                        break
                                except:
                                    continue
                            
                            if not next_clicked:
                                logging.warning(f"Não foi possível ir para página {page + 1}")
                                break
                                
                        except Exception as e:
                            logging.warning(f"Erro ao navegar para próxima página: {e}")
                            break
                    
                except Exception as e:
                    logging.error(f"Erro ao processar página {page}: {e}")
                    continue
            
            logging.info(f"Total de {len(all_links)} links únicos encontrados")
            return all_links
            
        except Exception as e:
            logging.error(f"Erro ao buscar links de propriedades: {e}")
            return []

    def extract_property_data(self, property_url):
        """Extrai dados de uma propriedade específica"""
        try:
            self.ensure_driver()
            logging.info(f"Extraindo dados de: {property_url}")
            
            # Aguarda tempo aleatório para simular comportamento humano
            time.sleep(random.uniform(3, 5))
            
            self.driver.get(property_url)
            time.sleep(random.uniform(4, 6))
            
            # Incrementa contador de sessão
            self.session_counter += 1
            
            # Verifica se a página carregou corretamente
            if "página não encontrada" in self.driver.page_source.lower() or "404" in self.driver.title.lower():
                logging.warning(f"Página não encontrada: {property_url}")
                return None
            
            property_data = {
                'url': property_url,
                'title': None,
                'price': None,
                'bedrooms': None,
                'bathrooms': None,
                'area': None,
                'parking_spaces': None,
                'address': None,
                'neighborhood': None,
                'description': None,
                'amenities': [],
                'source': 'ZapImoveis',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Simula scroll para ativar lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Extrai título
            title_selectors = [
                'h1.header__title',
                'h1[class*="title"]',
                'h1.l-page__title',
                'h1',
                '.header__title',
                '[data-testid="header-title"]'
            ]
            
            for selector in title_selectors:
                try:
                    title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if title_element.text.strip():
                        property_data['title'] = title_element.text.strip()
                        break
                except:
                    continue
            
            # Extrai preço
            price_selectors = [
                '.header__price',
                'p[class*="price"]',
                '.price__value',
                'span[class*="price"]',
                'div[class*="price"]',
                '[data-testid="price"]'
            ]
            
            for selector in price_selectors:
                try:
                    price_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in price_elements:
                        text = elem.text.strip()
                        if text and ('R$' in text or 'RS' in text) and any(char.isdigit() for char in text):
                            # Verifica se não é taxa de condomínio ou IPTU
                            if 'cond' not in text.lower() and 'iptu' not in text.lower():
                                property_data['price'] = text
                                break
                    if property_data['price']:
                        break
                except:
                    continue
            
            # Extrai características (quartos, banheiros, área, vagas)
            # Busca em diferentes seções da página
            details_selectors = [
                '.amenities__item',
                '.features__item', 
                '.feature__item',
                '.card__amenity',
                '.summary__item',
                'li',
                'span',
                'div[class*="feature"]',
                'div[class*="amenity"]'
            ]
            
            all_text_elements = []
            for selector in details_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    all_text_elements.extend(elements)
                except:
                    continue
            
            for element in all_text_elements:
                try:
                    text = element.text.strip().lower()
                    if text:
                        # Quartos
                        if any(keyword in text for keyword in ['quarto', 'dormitório', 'dorm']) and not property_data['bedrooms']:
                            if any(char.isdigit() for char in text):
                                property_data['bedrooms'] = element.text.strip()
                        
                        # Banheiros
                        elif any(keyword in text for keyword in ['banheiro', 'lavabo', 'wc']) and not property_data['bathrooms']:
                            if any(char.isdigit() for char in text):
                                property_data['bathrooms'] = element.text.strip()
                        
                        # Área
                        elif 'm²' in text and not property_data['area']:
                            property_data['area'] = element.text.strip()
                        
                        # Vagas
                        elif any(keyword in text for keyword in ['vaga', 'garagem', 'estacionamento']) and not property_data['parking_spaces']:
                            if any(char.isdigit() for char in text):
                                property_data['parking_spaces'] = element.text.strip()
                except:
                    continue
            
            # Extrai endereço/localização
            address_selectors = [
                '.header__address',
                '.address',
                '.location',
                '.neighborhood',
                '[class*="address"]',
                '[class*="location"]',
                '[data-testid="address"]'
            ]
            
            for selector in address_selectors:
                try:
                    address_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if address_element.text.strip():
                        property_data['address'] = address_element.text.strip()
                        break
                except:
                    continue
            
            # Extrai descrição
            description_selectors = [
                '.description__content',
                '.about__content',
                'div[class*="description"]',
                '.text-content',
                '[data-testid="description"]'
            ]
            
            for selector in description_selectors:
                try:
                    desc_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in desc_elements:
                        text = elem.text.strip()
                        if text and len(text) > 50:  # Descrição deve ter pelo menos 50 caracteres
                            property_data['description'] = text
                            break
                    if property_data['description']:
                        break
                except:
                    continue
            
            # Extrai comodidades/amenidades
            amenities_selectors = [
                '.amenities__item',
                '.amenity__item',
                '.features__item',
                '.feature__item'
            ]
            
            amenities = []
            for selector in amenities_selectors:
                try:
                    amenity_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in amenity_elements:
                        text = elem.text.strip()
                        if text and len(text) < 50:  # Comodidades são geralmente textos curtos
                            amenities.append(text)
                except:
                    continue
            
            if amenities:
                property_data['amenities'] = list(set(amenities))  # Remove duplicatas
            
            # Log do resultado
            if property_data['title'] and property_data['price']:
                logging.info(f"OK - Dados extraídos com sucesso: {property_data['title'][:50]}...")
            else:
                logging.warning(f"AVISO - Dados incompletos extraídos de {property_url}")
            
            return property_data
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados de {property_url}: {e}")
            return None

    def scrape_properties(self, search_url, max_properties=10, max_pages=3):
        """Método principal para scraping completo"""
        try:
            logging.info(f"Iniciando scraping ZapImóveis: {search_url}")
            
            # Busca os links das propriedades
            property_links = self.get_property_links(search_url, max_pages)
            
            if not property_links:
                logging.warning("Nenhum link de propriedade encontrado")
                return []
            
            # Limita o número de propriedades
            if max_properties:
                property_links = property_links[:max_properties]
            
            logging.info(f"Extraindo detalhes de {len(property_links)} propriedades...")
            
            properties_data = []
            
            for i, link in enumerate(property_links, 1):
                logging.info(f"Processando propriedade {i}/{len(property_links)}")
                
                property_details = self.extract_property_data(link)
                if property_details:
                    properties_data.append(property_details)
                    logging.info(f"OK - Propriedade {i} processada com sucesso")
                else:
                    logging.warning(f"ERRO - Falha ao processar propriedade {i}")
                
                # Pausa entre requisições
                time.sleep(random.uniform(3, 6))
            
            logging.info(f"Scraping ZapImóveis concluído! {len(properties_data)} propriedades extraídas.")
            return properties_data
            
        except Exception as e:
            logging.error(f"Erro durante o scraping ZapImóveis: {e}")
            return []

    def close(self):
        """Fecha o WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("ZapImóveis Scraper fechado.")
        except Exception as e:
            logging.error(f"Erro ao fechar ZapImóveis Scraper: {e}")