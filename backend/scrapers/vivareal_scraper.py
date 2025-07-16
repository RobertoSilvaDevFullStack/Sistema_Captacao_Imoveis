from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
import re

class VivaRealScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.vivareal.com.br")
        
    def get_property_links(self, search_url):
        self.driver.get(search_url)
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
        
        return links
        
    def extract_property_data(self, property_url):
        try:
            self.driver.get(property_url)
            time.sleep(2)
            
            # Extrair dados específicos
            title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
            
            price_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='price-info']")
            price = re.sub(r'[^\d]', '', price_element.text)
            
            address = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='address']").text
            
            # Características do imóvel
            features = {}
            feature_elements = self.driver.find_elements(By.CSS_SELECTOR, ".feature-item")
            for feature in feature_elements:
                key = feature.find_element(By.CSS_SELECTOR, ".feature-label").text
                value = feature.find_element(By.CSS_SELECTOR, ".feature-value").text
                features[key] = value
                
            return {
                'title': title,
                'price': int(price) if price else None,
                'address': address,
                'bedrooms': features.get('Quartos', 0),
                'bathrooms': features.get('Banheiros', 0),
                'area': features.get('Área', 0),
                'url': property_url,
                'source': 'VivaReal',
                'scraped_at': datetime.now()
            }
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados de {property_url}: {e}")
            return None