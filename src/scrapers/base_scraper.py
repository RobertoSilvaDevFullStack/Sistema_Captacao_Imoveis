# src/scrapers/base_scraper.py
"""
Classe base para todos os scrapers
"""
import logging
import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Import direto sem relative imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.property import Property, PropertySearch, ScrapingResult, PropertySource, PropertyType
from config.settings import settings

class BaseScraper(ABC):
    """Classe base para scrapers"""
    
    def __init__(self, source: PropertySource):
        self.source = source
        self.logger = logging.getLogger(f'scraper.{source.value}')
        self.driver: Optional[webdriver.Chrome] = None
        self.config = settings.SCRAPER
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Configura o driver do Selenium com opções otimizadas"""
        chrome_options = Options()
        
        # Configurações anti-detecção
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configurações de performance
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        
        # User agent aleatório
        user_agents = self.config.user_agents or []
        user_agent = None
        if user_agents:
            user_agent = random.choice(user_agents)
            chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configurações extras anti-detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        if user_agent:
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
        
        return driver
    
    def _wait_for_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> Optional[Any]:
        """Aguarda elemento aparecer na página"""
        if timeout is None:
            timeout = self.config.timeout
            
        if not self.driver:
            return None
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Timeout aguardando elemento: {locator}")
            return None
    
    def _wait_for_elements(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> List[Any]:
        """Aguarda elementos aparecerem na página"""
        if timeout is None:
            timeout = self.config.timeout
            
        if not self.driver:
            return []
            
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            self.logger.warning(f"Timeout aguardando elementos: {locator}")
            return []
    
    def _random_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Adiciona delay aleatório entre ações"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _extract_text_safe(self, element: Any, default: str = "") -> str:
        """Extrai texto de elemento de forma segura"""
        try:
            return element.text.strip() if element else default
        except Exception as e:
            self.logger.warning(f"Erro ao extrair texto: {e}")
            return default
    
    def _extract_attribute_safe(self, element: Any, attribute: str, default: str = "") -> str:
        """Extrai atributo de elemento de forma segura"""
        try:
            return element.get_attribute(attribute) if element else default
        except Exception as e:
            self.logger.warning(f"Erro ao extrair atributo {attribute}: {e}")
            return default
    
    @abstractmethod
    def _build_search_url(self, search: PropertySearch) -> str:
        """Constrói URL de busca específica do portal"""
        pass
    
    @abstractmethod
    def _extract_property_data(self, element: Any) -> Optional[Property]:
        """Extrai dados de uma propriedade do elemento"""
        pass
    
    @abstractmethod
    def _get_property_elements(self) -> List[Any]:
        """Obtém elementos de propriedades da página"""
        pass
    
    def scrape_properties(self, search: PropertySearch) -> ScrapingResult:
        """Executa scraping de propriedades"""
        start_time = time.time()
        result = ScrapingResult(source=self.source)
        
        try:
            self.logger.info(f"Iniciando scraping: {search.city}, {search.property_type.value}")
            
            # Configurar driver
            self.driver = self._setup_driver()
            
            # Construir URL e navegar
            url = self._build_search_url(search)
            self.logger.info(f"Navegando para: {url}")
            self.driver.get(url)
            
            # Aguardar carregamento
            self._random_delay(2, 4)
            
            # Extrair propriedades
            property_elements = self._get_property_elements()
            self.logger.info(f"Encontrados {len(property_elements)} elementos de propriedades")
            
            properties = []
            for i, element in enumerate(property_elements[:search.max_results]):
                try:
                    property_data = self._extract_property_data(element)
                    if property_data and self._validate_property(property_data):
                        properties.append(property_data)
                        self.logger.debug(f"Propriedade {i+1} extraída: {property_data.title[:50]}...")
                    
                    # Delay entre extrações
                    if i < len(property_elements) - 1:
                        self._random_delay(0.5, 1.5)
                        
                except Exception as e:
                    self.logger.error(f"Erro ao extrair propriedade {i+1}: {e}")
                    continue
            
            result.properties = properties
            result.total_found = len(properties)
            result.success = True
            
            self.logger.info(f"Scraping concluído: {len(properties)} propriedades válidas")
            
        except Exception as e:
            self.logger.error(f"Erro durante scraping: {e}")
            result.error_message = str(e)
            result.success = False
            
        finally:
            # Limpar recursos
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            result.execution_time = time.time() - start_time
            
        return result
    
    def _validate_property(self, property_data: Property) -> bool:
        """Valida dados básicos da propriedade"""
        if not property_data.title or not property_data.url:
            return False
            
        if not property_data.price or property_data.price < 10000 or property_data.price > 50000000:
            return False
            
        property_data.is_valid = True
        return True
