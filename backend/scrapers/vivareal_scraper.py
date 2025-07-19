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
        self.setup_driver()

    def setup_driver(self):
        """Configura driver com bypass avançado do Cloudflare"""
        options = Options()

        # Configurações anti-detecção avançadas
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Cloudflare bypass específico
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Headers mais realistas
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Experimental options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Perfis e preferências
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        }
        options.add_experimental_option("prefs", prefs)

        # Inicializa driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Scripts anti-detecção avançados
        self._apply_stealth_mode()
        
        # Configurações de timing
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(1920, 1080)
        
        logging.info("VivaReal driver configurado com bypass Cloudflare")

    def _apply_stealth_mode(self):
        """Aplica scripts de stealth mode para bypass do Cloudflare"""
        try:
            # Remove webdriver property
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Modifica navigator properties
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['pt-BR', 'pt', 'en-US', 'en'],
                });
            """)
            
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # Override permissions
            self.driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                return window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Chrome runtime
            self.driver.execute_script("""
                window.chrome = {
                    runtime: {},
                };
            """)
            
        except Exception as e:
            logging.debug(f"Erro ao aplicar stealth mode: {e}")

    def wait_for_cloudflare_bypass(self, max_wait=30):
        """Aguarda bypass do Cloudflare"""
        try:
            wait = WebDriverWait(self.driver, max_wait)
            
            # Aguarda a página carregar completamente
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
            # Verifica se ainda está no Cloudflare
            for _ in range(max_wait):
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                # Indicadores do Cloudflare
                if any(indicator in page_source for indicator in [
                    'checking your browser',
                    'cloudflare',
                    'ddos protection',
                    'please wait',
                    'ray id'
                ]):
                    logging.info("Aguardando bypass do Cloudflare...")
                    time.sleep(1)
                    continue
                else:
                    logging.info("Cloudflare bypass concluído")
                    return True
                    
            return False
            
        except Exception as e:
            logging.error(f"Erro ao aguardar bypass Cloudflare: {e}")
            return False
        
        # Execute script to hide automation indicators
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set realistic window size
        self.driver.set_window_size(1366, 768)

        

    def get_property_data_from_listing(self, search_url):
        """Extrai dados básicos das propriedades diretamente da página de listagem com bypass Cloudflare"""
        try:
            logging.info(f"Acessando VivaReal: {search_url}")
            
            # Navega para a URL de busca
            self.driver.get(search_url)
            
            # Aguarda bypass do Cloudflare
            if not self.wait_for_cloudflare_bypass(30):
                logging.error("Não foi possível contornar o Cloudflare")
                return []
            
            # Aguarda elementos carregarem
            time.sleep(random.uniform(3, 5))
            
            try:
                wait = WebDriverWait(self.driver, 15)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-cy='rp-property-cd'], .property-card, [data-testid='property-card']")))
            except:
                logging.warning("Elementos de propriedades não encontrados, tentando seletores alternativos")
            
            # Busca cards de propriedades com múltiplos seletores
            property_selectors = [
                "li[data-cy='rp-property-cd']",
                ".property-card",
                "[data-testid='property-card']",
                ".js-property-card",
                "[data-position]"
            ]
            
            property_cards = []
            for selector in property_selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        property_cards = cards
                        logging.info(f"Encontrados {len(cards)} cards com seletor: {selector}")
                        break
                except:
                    continue
            
            if not property_cards:
                logging.warning("Nenhum card de propriedade encontrado")
                return []
            
            properties_data = []
            
            for i, card in enumerate(property_cards[:10]):  # Limita a 10 para teste
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
                        'neighborhood': None,
                        'source': 'vivareal'
                    }
                    
                    # Extrai URL com múltiplos seletores
                    url_selectors = [
                        "a[href*='/imovel/']",
                        "a[data-testid='property-card-link']",
                        ".property-card__content a",
                        "a[data-position]"
                    ]
                    
                    for selector in url_selectors:
                        try:
                            link_element = card.find_element(By.CSS_SELECTOR, selector)
                            href = link_element.get_attribute('href')
                            if href and '/imovel/' in href:
                                property_data['url'] = href
                                break
                        except:
                            continue
                    
                    # Extrai preço
                    try:
                        price_selectors = [
                            '[data-testid="price-info-value"]',
                            '.price',
                            '[class*="price"]',
                            '.js-price'
                        ]
                        
                        for selector in price_selectors:
                            try:
                                price_elem = card.find_element(By.CSS_SELECTOR, selector)
                                if price_elem and price_elem.text.strip():
                                    property_data['price'] = price_elem.text.strip()
                                    break
                            except:
                                continue
                        
                        # Fallback: busca qualquer texto com R$
                        if not property_data['price']:
                            price_elements = card.find_elements(By.CSS_SELECTOR, "*")
                            for elem in price_elements:
                                text = elem.text.strip()
                                if text and ('R$' in text or 'RS' in text) and any(char.isdigit() for char in text):
                                    if 'cond' not in text.lower() and 'iptu' not in text.lower():
                                        property_data['price'] = text
                                        break
                    except:
                        pass
                    
                    # Extrai características (quartos, banheiros, área, vagas)
                    try:
                        feature_selectors = [
                            '[data-testid="property-features"] span',
                            '.features span',
                            '[class*="feature"] span'
                        ]
                        
                        for selector in feature_selectors:
                            try:
                                features = card.find_elements(By.CSS_SELECTOR, selector)
                                for elem in features:
                                    text = elem.text.strip().lower()
                                    if text:
                                        if ('quarto' in text or 'dormitório' in text) and any(char.isdigit() for char in text):
                                            property_data['bedrooms'] = elem.text.strip()
                                        elif ('banheiro' in text) and any(char.isdigit() for char in text):
                                            property_data['bathrooms'] = elem.text.strip()
                                        elif 'm²' in text and any(char.isdigit() for char in text):
                                            property_data['area'] = elem.text.strip()
                                        elif ('vaga' in text or 'garagem' in text) and any(char.isdigit() for char in text):
                                            property_data['parking_spaces'] = elem.text.strip()
                                break
                            except:
                                continue
                        
                        # Fallback: busca em todo o card
                        if not any([property_data['bedrooms'], property_data['bathrooms'], property_data['area']]):
                            all_text_elements = card.find_elements(By.CSS_SELECTOR, "*")
                            for elem in all_text_elements:
                                text = elem.text.strip().lower()
                                if text:
                                    if ('quarto' in text or 'quartos' in text) and any(char.isdigit() for char in text):
                                        if not property_data['bedrooms']:
                                            property_data['bedrooms'] = elem.text.strip()
                                    elif ('banheiro' in text or 'banheiros' in text) and any(char.isdigit() for char in text):
                                        if not property_data['bathrooms']:
                                            property_data['bathrooms'] = elem.text.strip()
                                    elif 'm²' in text and any(char.isdigit() for char in text):
                                        if not property_data['area']:
                                            property_data['area'] = elem.text.strip()
                                    elif ('vaga' in text or 'vagas' in text) and any(char.isdigit() for char in text):
                                        if not property_data['parking_spaces']:
                                            property_data['parking_spaces'] = elem.text.strip()
                    except Exception as e:
                        logging.debug(f"Erro ao extrair características: {e}")
                    
                    # Extrai endereço
                    try:
                        address_selectors = [
                            '[data-testid="property-address"]',
                            '.address',
                            '[class*="address"]',
                            '.location'
                        ]
                        
                        for selector in address_selectors:
                            try:
                                address_elem = card.find_element(By.CSS_SELECTOR, selector)
                                if address_elem and address_elem.text.strip():
                                    property_data['address'] = address_elem.text.strip()
                                    break
                            except:
                                continue
                                
                    except Exception as e:
                        logging.debug(f"Erro ao extrair endereço: {e}")
                    
                    # Adiciona à lista se tem dados mínimos
                    if property_data['url'] or property_data['price']:
                        properties_data.append(property_data)
                        logging.info(f"✅ Propriedade {i+1} extraída: {property_data.get('price', 'Sem preço')}")
                
                except Exception as e:
                    logging.debug(f"Erro ao processar card {i}: {e}")
                    continue
            
            logging.info(f"Total de {len(properties_data)} propriedades extraídas da listagem")
            return properties_data
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados da listagem: {e}")
            return []
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

    def get_property_links(self, search_url, max_pages=2):
        """Extrai links de propriedades das páginas de busca"""
        try:
            all_links = set()
            page = 1
            
            while page <= max_pages:
                try:
                    # Monta URL da página
                    if page == 1:
                        page_url = search_url
                    else:
                        # VivaReal usa paginação com parâmetro 'pagina'
                        separator = "&" if "?" in search_url else "?"
                        page_url = f"{search_url}{separator}pagina={page}"
                    
                    logging.info(f"Processando página {page}: {page_url}")
                    self.driver.get(page_url)
                    time.sleep(random.uniform(2, 4))
                    
                    # Seletores para links de propriedades no VivaReal
                    selectors = [
                        'a[data-position]',
                        'a[href*="/imovel/"]',
                        '.property-card__content a',
                        '[data-testid="property-card-link"]'
                    ]
                    
                    page_links = set()
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                href = element.get_attribute('href')
                                if href and '/imovel/' in href and 'vivareal.com.br' in href:
                                    page_links.add(href)
                        except Exception as e:
                            logging.debug(f"Seletor {selector} falhou: {e}")
                            continue
                    
                    if not page_links:
                        logging.warning(f"Nenhum link encontrado na página {page}")
                        break
                    
                    all_links.update(page_links)
                    logging.info(f"Encontrados {len(page_links)} links na página {page}")
                    
                    page += 1
                    
                except Exception as e:
                    logging.error(f"Erro ao processar página {page}: {e}")
                    break
            
            logging.info(f"Total de {len(all_links)} links únicos encontrados")
            return list(all_links)
            
        except Exception as e:
            logging.error(f"Erro ao buscar links de propriedades: {e}")
            return []

    def scrape_properties(self, search_url, max_properties=5, max_pages=2):
        """Scrape completo: extrai dados direto da listagem com bypass Cloudflare"""
        try:
            logging.info(f"Iniciando scraping VivaReal: {search_url}")
            
            # Primeira tentativa: extração direta da listagem
            properties_data = self.get_property_data_from_listing(search_url)
            
            if properties_data:
                # Limita o número se especificado
                if max_properties and len(properties_data) > max_properties:
                    properties_data = properties_data[:max_properties]
                
                logging.info(f"✅ {len(properties_data)} propriedades extraídas da listagem")
                return properties_data
            
            # Fallback: tentativa com busca de links
            logging.info("Tentando abordagem alternativa com busca de links...")
            property_links = self.get_property_links(search_url, max_pages)
            
            if not property_links:
                logging.warning("Nenhum link de propriedade encontrado")
                return []
            
            logging.info(f"Encontrados {len(property_links)} links")
            
            # Limita o número de propriedades se especificado
            if max_properties:
                property_links = property_links[:max_properties]
            
            properties_data = []
            
            for i, link in enumerate(property_links, 1):
                logging.info(f"Processando propriedade {i}/{len(property_links)}")
                
                # Cria dados básicos apenas com o link
                property_data = {
                    'url': link,
                    'title': None,
                    'price': None,
                    'bedrooms': None,
                    'bathrooms': None,
                    'area': None,
                    'parking_spaces': None,
                    'address': None,
                    'neighborhood': None,
                    'source': 'vivareal'
                }
                
                properties_data.append(property_data)
                logging.info(f"✅ Link {i} processado")
                
                # Pausa entre requisições
                time.sleep(random.uniform(1, 2))
            
            logging.info(f"Scraping VivaReal concluído! {len(properties_data)} propriedades extraídas.")
            return properties_data
            
        except Exception as e:
            logging.error(f"Erro durante o scraping: {e}")
            return []

    def close(self):
        """Fecha o driver do navegador"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                logging.info("VivaReal driver fechado")
        except Exception as e:
            logging.debug(f"Erro ao fechar driver: {e}")


