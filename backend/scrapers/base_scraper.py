import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.setup_driver()
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
        
    @abstractmethod
    def extract_property_data(self, property_element):
        pass
        
    @abstractmethod
    def get_property_links(self, search_url):
        pass
        
    def scrape_properties(self, location="zona-sul-rio-de-janeiro"):
        properties = []
        search_url = f"{self.base_url}/venda/apartamento/{location}"
        
        try:
            property_links = self.get_property_links(search_url)
            
            for link in property_links:
                property_data = self.extract_property_data(link)
                if property_data:
                    properties.append(property_data)
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logging.error(f"Erro no scraping: {e}")
            
        return properties
        
    def close(self):
        self.driver.quit()