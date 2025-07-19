# vivareal_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import random



class VivaRealScraper:

    def __init__(self):

        options = Options()

        # Temporarily disable headless mode to see if it helps with Cloudflare
        # options.add_argument('--headless')

        options.add_argument('--no-sandbox')

        options.add_argument('--disable-dev-shm-usage')

        options.add_argument('--disable-gpu')
        
        options.add_argument('--disable-web-security')
        
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Fix for the user data directory error
        options.add_argument('--user-data-dir=/tmp/chrome_user_data')
        
        options.add_argument('--remote-debugging-port=9222')
        
        # Randomize User-Agent para parecer mais humano
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Additional options to avoid detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add more realistic browser behavior
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-default-apps')

        # Use ChromeDriverManager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute script to hide automation indicators
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set realistic window size
        self.driver.set_window_size(1366, 768)

        

    def get_property_data_from_listing(self, search_url):
        """Extrai dados básicos das propriedades diretamente da página de listagem"""
        try:
            # Navega para a URL de busca
            self.driver.get(search_url)
            
            # Aguarda um pouco para a página carregar
            time.sleep(5)
            
            # Aguarda os elementos carregarem
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-cy='rp-property-cd']")))
            
            # Busca todos os cards de propriedades
            property_cards = self.driver.find_elements(By.CSS_SELECTOR, "li[data-cy='rp-property-cd']")
            
            properties_data = []
            
            for card in property_cards:
                try:
                    property_data = {
                        'url': None,
                        'title': None,
                        'price': None,
                        'bedrooms': None,
                        'bathrooms': None,
                        'area': None,
                        'parking_spaces': None,
                        'address': None,
                        'neighborhood': None
                    }
                    
                    # Extrai URL
                    try:
                        link_element = card.find_element(By.CSS_SELECTOR, "a[href*='/imovel/']")
                        property_data['url'] = link_element.get_attribute('href')
                    except:
                        pass
                    
                    # Extrai preço
                    try:
                        price_elements = card.find_elements(By.CSS_SELECTOR, "*")
                        for elem in price_elements:
                            text = elem.text.strip()
                            if text and ('R$' in text or 'RS' in text) and any(char.isdigit() for char in text):
                                # Pega o primeiro preço encontrado que não seja condomínio/IPTU
                                if 'cond' not in text.lower() and 'iptu' not in text.lower():
                                    property_data['price'] = text
                                    break
                    except:
                        pass
                    
                    # Extrai características (quartos, banheiros, área, vagas)
                    try:
                        all_text_elements = card.find_elements(By.CSS_SELECTOR, "*")
                        for elem in all_text_elements:
                            text = elem.text.strip().lower()
                            if text:
                                # Quartos
                                if ('quarto' in text or 'quartos' in text) and any(char.isdigit() for char in text):
                                    if not property_data['bedrooms']:
                                        property_data['bedrooms'] = elem.text.strip()
                                
                                # Banheiros  
                                elif ('banheiro' in text or 'banheiros' in text) and any(char.isdigit() for char in text):
                                    if not property_data['bathrooms']:
                                        property_data['bathrooms'] = elem.text.strip()
                                
                                # Área
                                elif 'm²' in text and any(char.isdigit() for char in text):
                                    if not property_data['area']:
                                        property_data['area'] = elem.text.strip()
                                
                                # Vagas
                                elif ('vaga' in text or 'vagas' in text) and any(char.isdigit() for char in text):
                                    if not property_data['parking_spaces']:
                                        property_data['parking_spaces'] = elem.text.strip()
                    except:
                        pass
                    
                    # Extrai título/endereço da URL se disponível
                    try:
                        if property_data['url']:
                            url_parts = property_data['url'].split('/')
                            for part in url_parts:
                                if 'quartos' in part or 'sao-paulo' in part:
                                    # Constrói um título básico a partir da URL
                                    title_parts = part.replace('-', ' ').title()
                                    if 'Sao Paulo' in title_parts:
                                        property_data['address'] = title_parts
                                    break
                    except:
                        pass
                    
                    # Só adiciona se encontrou pelo menos URL e preço
                    if property_data['url'] and property_data['price']:
                        properties_data.append(property_data)
                        
                except Exception as e:
                    logging.warning(f"Erro ao processar card de propriedade: {e}")
                    continue
            
            return properties_data
            
        except Exception as e:
            logging.error(f"Erro ao buscar dados de propriedades: {e}")
            return []

    def scrape_property_details(self, property_url):
        """Extrai os detalhes de uma propriedade específica"""
        try:
            # Aguarda um tempo aleatório antes de acessar para parecer mais humano
            time.sleep(random.uniform(3, 7))
            
            self.driver.get(property_url)
            
            # Aguarda a página carregar completamente
            time.sleep(random.uniform(5, 8))
            
            # Verifica se foi bloqueado pelo Cloudflare
            if "sorry, you have been blocked" in self.driver.page_source.lower():
                logging.warning(f"Bloqueado pelo Cloudflare ao acessar: {property_url}")
                return None
            
            # Salva HTML para debug se necessário
            with open('debug_property.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
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
                'amenities': []
            }
            
            # Simula comportamento humano - scroll da página
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Extrai o título (mais genérico)
            try:
                title_selectors = ['h1', '[data-cy*="title"]', '.property-title', 'h1[class*="title"]']
                for selector in title_selectors:
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if title_element.text.strip():
                            property_data['title'] = title_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass
            
            # Extrai o preço (mais genérico)
            try:
                price_selectors = [
                    '[data-cy*="price"]', 
                    '.price', 
                    '[class*="price"]',
                    'span[class*="price"]',
                    'div[class*="price"]'
                ]
                for selector in price_selectors:
                    try:
                        price_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if price_element.text.strip() and ('R$' in price_element.text or 'RS' in price_element.text):
                            property_data['price'] = price_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass
            
            # Busca características gerais (quartos, banheiros, área, vagas)
            try:
                # Busca por elementos que contenham números seguidos de quartos, banheiros, etc.
                feature_elements = self.driver.find_elements(By.CSS_SELECTOR, 'span, div, p')
                for element in feature_elements:
                    text = element.text.strip().lower()
                    if text:
                        # Quartos
                        if 'quarto' in text and not property_data['bedrooms']:
                            if any(char.isdigit() for char in text):
                                property_data['bedrooms'] = text
                        
                        # Banheiros
                        if 'banheiro' in text and not property_data['bathrooms']:
                            if any(char.isdigit() for char in text):
                                property_data['bathrooms'] = text
                        
                        # Área
                        if 'm²' in text and not property_data['area']:
                            property_data['area'] = text
                        
                        # Vagas
                        if 'vaga' in text and not property_data['parking_spaces']:
                            if any(char.isdigit() for char in text):
                                property_data['parking_spaces'] = text
            except:
                pass
            
            # Busca endereço/localização em vários seletores possíveis
            try:
                address_selectors = [
                    '[data-cy*="address"]',
                    '.address',
                    '[class*="address"]',
                    'span[class*="location"]',
                    'div[class*="location"]'
                ]
                for selector in address_selectors:
                    try:
                        address_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if address_element.text.strip():
                            property_data['address'] = address_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass
            
            return property_data
            
        except Exception as e:
            logging.error(f"Erro ao extrair detalhes da propriedade {property_url}: {e}")
            return None

    def scrape_properties(self, search_url, max_properties=5):
        """Scrape completo: busca links e extrai detalhes de cada propriedade"""
        try:
            # Busca os links das propriedades
            logging.info(f"Buscando links de propriedades em: {search_url}")
            property_links = self.get_property_links(search_url)
            
            if not property_links:
                logging.warning("Nenhum link de propriedade encontrado")
                return []
            
            logging.info(f"Encontrados {len(property_links)} links. Extraindo detalhes...")
            
            # Limita o número de propriedades se especificado
            if max_properties:
                property_links = property_links[:max_properties]
            
            properties_data = []
            
            for i, link in enumerate(property_links, 1):
                logging.info(f"Processando propriedade {i}/{len(property_links)}: {link}")
                
                property_details = self.scrape_property_details(link)
                if property_details:
                    properties_data.append(property_details)
                    logging.info(f"✅ Propriedade {i} processada com sucesso")
                else:
                    logging.warning(f"❌ Falha ao processar propriedade {i}")
                
                # Pausa entre requisições para evitar bloqueios (mais longa e aleatória)
                time.sleep(random.uniform(5, 10))
            
            logging.info(f"Scraping concluído! {len(properties_data)} propriedades extraídas com sucesso.")
            return properties_data
            
        except Exception as e:
            logging.error(f"Erro durante o scraping: {e}")
            return []

    def close(self):

        if self.driver:

            self.driver.quit()


