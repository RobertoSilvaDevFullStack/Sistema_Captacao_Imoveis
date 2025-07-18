import time
import re
import logging
from datetime import datetime
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from utils.decorators import rate_limit # <-- 1. Importamos o decorator

class VivaRealScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.vivareal.com.br")
        
    @rate_limit(calls_per_second=1) # <-- 2. Adicionado limitador (1 chamada/seg)
    def get_property_links(self, search_url):
        """Busca a URL de pesquisa e retorna uma lista de links para os imóveis."""
        print(f"Buscando links em: {search_url}")
        self.driver.get(search_url)
        # O time.sleep original foi mantido para garantir que a página carregue o JS
        time.sleep(3) 
        
        # Scroll para carregar mais imóveis
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        # Extrair links dos imóveis
        property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[data-testid='property-card-link']")
        links = [elem.get_attribute('href') for elem in property_elements]
        print(f"Encontrados {len(links)} links de imóveis.")
        return links
        
    @rate_limit(calls_per_second=0.5) # <-- 3. Adicionado limitador (1 chamada a cada 2 seg)
    def extract_property_data(self, property_url):
        """Acessa a página de um imóvel e extrai seus dados."""
        try:
            print(f"Extraindo dados de: {property_url}")
            self.driver.get(property_url)
            # O time.sleep foi mantido para garantir o carregamento
            time.sleep(2)
            
            # Extrair dados específicos
            title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
            
            price_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='price-info']")
            price = re.sub(r'[^\d]', '', price_element.text)
            
            address = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='address']").text
            
            # Características do imóvel (Exemplo de como poderia ser implementado)
            # Nota: A extração de features pode precisar de ajuste conforme o HTML do site
            area = 0
            bedrooms = 0
            bathrooms = 0

            try:
                area_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='property-card-value-area']")
                area_text = area_element.text.strip()
                area_match = re.search(r'\d+', area_text)
                if area_match:
                    area = int(area_match.group(0))

                bedrooms_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='property-card-value-bedrooms']")
                bedrooms_text = bedrooms_element.text.strip()
                bedrooms_match = re.search(r'\d+', bedrooms_text)
                if bedrooms_match:
                    bedrooms = int(bedrooms_match.group(0))

                bathrooms_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='property-card-value-bathrooms']")
                bathrooms_text = bathrooms_element.text.strip()
                bathrooms_match = re.search(r'\d+', bathrooms_text)
                if bathrooms_match:
                    bathrooms = int(bathrooms_match.group(0))
            except Exception:
                logging.warning(f"Não foi possível extrair todas as features de {property_url}")
                
            return {
                'title': title,
                'price': int(price) if price else None,
                'address': address,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'url': property_url,
                'source': 'VivaReal',
                'scraped_at': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados de {property_url}: {e}")
            return None