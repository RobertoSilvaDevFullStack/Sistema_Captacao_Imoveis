# Em scrapers/olx_scraper.py

import time
import re
import logging
from datetime import datetime
from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from utils.decorators import rate_limit

class OLXScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.olx.com.br")

    @rate_limit(calls_per_second=1)
    def get_property_links(self, search_url):
        """Busca a URL de pesquisa e retorna uma lista de links para os imóveis."""
        print(f"Buscando links em: {search_url}")
        self.driver.get(search_url)
        time.sleep(3)
        
        # TODO: Encontre o seletor CSS correto para o link de cada anúncio na OLX.
        property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.olx-ad-card__link") # <--- EXEMPLO, PODE PRECISAR DE AJUSTE
        
        links = [elem.get_attribute('href') for elem in property_elements]
        print(f"Encontrados {len(links)} links de imóveis na OLX.")
        return links

    @rate_limit(calls_per_second=0.5)
    def extract_property_data(self, property_url):
        """Acessa a página de um imóvel e extrai seus dados."""
        try:
            print(f"Extraindo dados de: {property_url}")
            self.driver.get(property_url)
            time.sleep(2)

            # TODO: Adapte os seletores abaixo para os elementos corretos na página de um anúncio da OLX.
            
            title = self.driver.find_element(By.CSS_SELECTOR, "h1[data-testid='ad-title']").text # <--- EXEMPLO
            price = self.driver.find_element(By.CSS_SELECTOR, "h2[data-testid='ad-price-value']").text # <--- EXEMPLO
            price_cleaned = re.sub(r'[^\d]', '', price)

            # A OLX organiza os detalhes de forma diferente, geralmente em uma lista.
            # Você precisará de uma lógica para iterar sobre os detalhes e encontrar os que precisa.
            address = "Não informado" # Exemplo, pois o endereço pode estar em locais diferentes.
            area, bedrooms, bathrooms = 0, 0, 0
            
            details = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ad-properties'] div.duv3c-0") # <--- EXEMPLO
            for detail in details:
                text = detail.text.lower()
                if 'área' in text:
                    area_match = re.search(r'\d+', text)
                    if area_match:
                        area = int(area_match.group(0))
                elif 'quartos' in text:
                    bedrooms_match = re.search(r'\d+', text)
                    if bedrooms_match:
                        bedrooms = int(bedrooms_match.group(0))
                elif 'banheiros' in text:
                    bathrooms_match = re.search(r'\d+', text)
                    if bathrooms_match:
                        bathrooms = int(bathrooms_match.group(0))

            return {
                'title': title,
                'price': int(price_cleaned) if price_cleaned else None,
                'address': address, # Pode ser necessário extrair de outra forma.
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'area': area,
                'url': property_url,
                'source': 'OLX',
                'scraped_at': datetime.now()
            }

        except Exception as e:
            logging.error(f"Erro ao extrair dados de {property_url}: {e}")
            return None