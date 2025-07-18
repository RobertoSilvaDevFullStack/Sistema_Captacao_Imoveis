# Em scrapers/zapimoveis_scraper.py

import time
import re
import logging
from datetime import datetime
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from utils.decorators import rate_limit

class ZapImoveisScraper(BaseScraper):
    def __init__(self):
        # O construtor chama a classe base com a URL principal do ZapImóveis
        super().__init__("https://www.zapimoveis.com.br")

    @rate_limit(calls_per_second=1) # Limitador de 1 chamada por segundo
    def get_property_links(self, search_url):
        """Busca a URL de pesquisa e retorna uma lista de links para os imóveis."""
        print(f"Buscando links em: {search_url}")
        self.driver.get(search_url)
        time.sleep(3) # Pausa para carregamento da página

        # TODO: Se o ZapImóveis usar "infinite scroll", a lógica de rolagem pode ser necessária aqui.
        
        # TODO: Encontre o seletor CSS correto para o link de cada imóvel na página de resultados
        # Dica: Inspecione a página de busca do ZapImóveis e encontre a tag `<a>` que leva ao imóvel.
        property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.property-card__content-link") # <--- EXEMPLO, PODE PRECISAR DE AJUSTE
        
        links = [elem.get_attribute('href') for elem in property_elements]
        print(f"Encontrados {len(links)} links de imóveis no ZapImóveis.")
        return links

    @rate_limit(calls_per_second=0.5) # Limitador de 1 chamada a cada 2 segundos
    def extract_property_data(self, property_url):
        """Acessa a página de um imóvel e extrai seus dados."""
        try:
            print(f"Extraindo dados de: {property_url}")
            self.driver.get(property_url)
            time.sleep(2)

            # TODO: Adapte os seletores abaixo para os elementos corretos na página de um imóvel do ZapImóveis.
            # Inspecione a página para encontrar os seletores para título, preço, endereço, etc.
            
            title = self.driver.find_element(By.CSS_SELECTOR, "h1.title__title").text # <--- EXEMPLO
            price = self.driver.find_element(By.CSS_SELECTOR, "span.price__value").text # <--- EXEMPLO
            address = self.driver.find_element(By.CSS_SELECTOR, "span.text.address").text # <--- EXEMPLO

            # Use regex para limpar o preço, mantendo apenas os números
            price_cleaned = re.sub(r'[^\d]', '', price)

            area = int(self.driver.find_element(By.CSS_SELECTOR, "span[itemprop='floorSize']").text.replace('m²', '').strip()) # <--- EXEMPLO
            bedrooms = int(self.driver.find_element(By.CSS_SELECTOR, "span[itemprop='numberOfRooms']").text.strip()) # <--- EXEMPLO
            bathrooms = int(self.driver.find_element(By.CSS_SELECTOR, "span[itemprop='numberOfBathroomsTotal']").text.strip()) # <--- EXEMPLO

            return {
                'title': title,
                'price': int(price_cleaned) if price_cleaned else None,
                'address': address,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'url': property_url,
                'source': 'ZapImoveis',
                'scraped_at': datetime.now()
            }

        except Exception as e:
            logging.error(f"Erro ao extrair dados de {property_url}: {e}")
            return None