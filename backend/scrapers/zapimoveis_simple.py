# backend/scrapers/zapimoveis_simple.py

import time
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class ZapImoveisSimple:
    def __init__(self):
        self.driver = None
        self.base_url = "https://www.zapimoveis.com.br"
        
    def setup_driver(self):
        """Configura o WebDriver com configurações básicas"""
        try:
            options = Options()
            
            # Configurações mínimas necessárias
            options.add_argument('--headless')  # Modo headless para performance
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Desabilitar recursos desnecessários (mas manter JavaScript)
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Para performance
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logging.info("Driver ZapImóveis inicializado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao inicializar driver: {e}")
            return False
    
    def scrape_properties(self, search_url, max_results=10):
        """Busca propriedades de forma simplificada e robusta"""
        properties = []
        
        try:
            if not self.setup_driver():
                return []
            
            logging.info(f"Iniciando busca: {search_url}")
            
            # Navegar para a página
            self.driver.get(search_url)
            time.sleep(8)  # Mais tempo para carregamento
            
            # Múltiplas estratégias de busca
            try:
                # Estratégia 1: Buscar cards de propriedades
                property_cards = self.find_property_cards()
                
                if property_cards:
                    logging.info(f"Encontrados {len(property_cards)} cards de propriedades")
                    
                    for i, card in enumerate(property_cards[:max_results]):
                        try:
                            property_data = self.extract_property_data(card, i + 1)
                            if property_data:
                                properties.append(property_data)
                                
                        except Exception as e:
                            logging.warning(f"Erro ao extrair dados do card {i+1}: {e}")
                            continue
                
                # Estratégia 2: Fallback - buscar por texto com preços
                if len(properties) < 3:
                    logging.info("Usando estratégia fallback...")
                    fallback_properties = self.extract_fallback_data(max_results)
                    properties.extend(fallback_properties)
                
            except Exception as e:
                logging.error(f"Erro nas estratégias de busca: {e}")
                
        except Exception as e:
            logging.error(f"Erro no scraping ZapImóveis: {e}")
            
        finally:
            self.close()
            
        logging.info(f"Scraping concluído: {len(properties)} propriedades extraídas")
        return properties
    
    def find_property_cards(self):
        """Busca cards de propriedades com múltiplos seletores"""
        if not self.driver:
            return []
            
        selectors = [
            # Seletores específicos do ZapImóveis
            'div[data-testid*="listing"]',
            'div[data-testid*="property"]',
            'article[data-testid]',
            'div[class*="listing"]',
            'div[class*="result"]',
            'div[class*="card"]',
            # Seletores genéricos
            'article',
            'div[role="listitem"]',
            '.listing-wrapper',
            '.result-item'
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                # Filtra elementos que contêm preços
                valid_elements = []
                for elem in elements:
                    if 'R$' in elem.text or 'reais' in elem.text.lower():
                        valid_elements.append(elem)
                
                if valid_elements:
                    logging.info(f"Seletor '{selector}' encontrou {len(valid_elements)} elementos válidos")
                    return valid_elements
                    
            except Exception as e:
                continue
        
        return []
    
    def extract_property_data(self, element, index):
        """Extrai dados de uma propriedade específica"""
        try:
            text = element.text
            
            # Busca URL
            url = None
            try:
                link_elem = element.find_element(By.TAG_NAME, 'a')
                url = link_elem.get_attribute('href')
            except:
                url = f"{self.base_url}/imovel/id-{index}"
            
            # Extração de dados via regex/texto
            import re
            
            # Preço
            price_match = re.search(r'R\$\s*([\d.,]+)', text)
            price = price_match.group(0) if price_match else 'Consulte'
            
            # Quartos
            rooms_match = re.search(r'(\d+)\s*quarto', text, re.IGNORECASE)
            rooms = rooms_match.group(1) if rooms_match else 'N/A'
            
            # Banheiros
            bath_match = re.search(r'(\d+)\s*banheiro', text, re.IGNORECASE)
            bathrooms = bath_match.group(1) if bath_match else 'N/A'
            
            # Área
            area_match = re.search(r'(\d+)\s*m²', text)
            area = f"{area_match.group(1)}m²" if area_match else 'N/A'
            
            # Localização (primeiras palavras após quebra de linha)
            lines = text.split('\n')
            location = 'N/A'
            for line in lines:
                line = line.strip()
                if len(line) > 5 and not any(x in line.lower() for x in ['r$', 'quarto', 'banheiro', 'm²']):
                    location = line[:50]  # Primeiros 50 caracteres
                    break
            
            property_data = {
                'url': url,
                'title': f"Imóvel em {location}",
                'price': price,
                'location': location,
                'area': area,
                'rooms': rooms,
                'bathrooms': bathrooms,
                'portal': 'zapimoveis',
                'scraped_at': datetime.now().isoformat(),
                'raw_text': text[:200]  # Para debug
            }
            
            # Valida se tem dados mínimos
            if price != 'Consulte' or any(x != 'N/A' for x in [rooms, bathrooms, area]):
                return property_data
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados: {e}")
        
        return None
    
    def extract_fallback_data(self, max_results):
        """Estratégia fallback: busca elementos com preços"""
        properties = []
        
        if not self.driver:
            return properties
        
        try:
            # Busca todos os elementos que contêm "R$"
            price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'R$')]")
            
            processed_texts = set()
            
            for elem in price_elements[:max_results * 2]:
                try:
                    # Busca o container pai
                    parent = elem.find_element(By.XPATH, "./ancestor::div[@class] | ./ancestor::article")
                    text = parent.text
                    
                    # Evita duplicatas
                    if text in processed_texts or len(text) < 20:
                        continue
                    
                    processed_texts.add(text)
                    
                    # Extrai dados básicos
                    import re
                    price_match = re.search(r'R\$\s*([\d.,]+)', text)
                    
                    if price_match:
                        property_data = {
                            'url': f"{self.base_url}/imovel/fallback-{len(properties)+1}",
                            'title': f"Propriedade Fallback {len(properties)+1}",
                            'price': price_match.group(0),
                            'location': 'Localização não identificada',
                            'area': 'N/A',
                            'rooms': 'N/A',
                            'bathrooms': 'N/A',
                            'portal': 'zapimoveis',
                            'scraped_at': datetime.now().isoformat(),
                            'extraction_method': 'fallback'
                        }
                        
                        properties.append(property_data)
                        
                        if len(properties) >= max_results:
                            break
                    
                except Exception:
                    continue
            
            logging.info(f"Fallback extraiu {len(properties)} propriedades")
            
        except Exception as e:
            logging.error(f"Erro no fallback: {e}")
        
        return properties
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
