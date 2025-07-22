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
from utils.header_rotator import header_rotator
from utils.rate_limiter import rate_manager
from utils.proxy_rotator import proxy_manager
from utils.selenium_proxy_config import selenium_proxy_config

class BaseScraper(ABC):
    """Classe base para scrapers"""
    
    def __init__(self, source: PropertySource):
        self.source = source
        self.logger = logging.getLogger(f'scraper.{source.value}')
        self.driver: Optional[webdriver.Chrome] = None
        self.config = settings.SCRAPER
        self.current_proxy = None  # Proxy em uso atualmente
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Configura o driver do Selenium com opções otimizadas e proxy"""
        chrome_options = Options()
        
        # Usar opções do header_rotator para anti-detecção
        portal_name = self.source.value.lower()
        selenium_options = header_rotator.get_selenium_options(portal_name)
        
        for option in selenium_options:
            chrome_options.add_argument(option)
        
        # Configurar proxy se disponível
        try:
            self.current_proxy = proxy_manager.get_proxy_for_request()
            if self.current_proxy:
                self.logger.info(f"Usando proxy: {self.current_proxy.ip}:{self.current_proxy.port}")
                
                # Usar configuração de proxy do selenium_proxy_config
                proxy_options = selenium_proxy_config.configure_chrome_with_proxy(self.current_proxy)
                
                # Merge das opções
                for arg in proxy_options.arguments:
                    if arg not in chrome_options.arguments:
                        chrome_options.add_argument(arg)
                        
                # Adicionar extensões de proxy se necessário
                for extension in proxy_options.extensions:
                    chrome_options.add_extension(extension)
                    
            else:
                self.logger.warning("Nenhum proxy disponível - usando conexão direta")
                
        except Exception as e:
            self.logger.warning(f"Erro ao configurar proxy: {e} - usando conexão direta")
            self.current_proxy = None
        
        # Configurações extras anti-detecção
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configurações de performance
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configurações extras anti-detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
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
        portal_name = self.source.value.lower()
        
        try:
            self.logger.info(f"Iniciando scraping: {search.city}, {search.property_type.value}")
            
            # Aplicar rate limiting antes de começar
            rate_manager.wait_for_portal(portal_name)
            
            # Configurar driver
            self.driver = self._setup_driver()
            
            # Construir URL e navegar
            url = self._build_search_url(search)
            self.logger.info(f"Navegando para: {url}")
            
            # Aplicar headers customizados se possível
            try:
                headers = header_rotator.get_random_headers(portal_name)
                self.driver.execute_cdp_cmd('Network.setRequestHeaders', {'headers': headers})
            except Exception as e:
                self.logger.warning(f"Não foi possível definir headers customizados: {e}")
            
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
            
            # Registrar sucesso no rate manager
            rate_manager.record_success(portal_name)
            
            # Registrar sucesso do proxy se estiver sendo usado
            if self.current_proxy:
                proxy_manager.report_proxy_result(self.current_proxy, True)
                self.logger.debug(f"Proxy {self.current_proxy.ip}:{self.current_proxy.port} - sucesso")
            
            self.logger.info(f"Scraping concluído: {len(properties)} propriedades válidas")
            
        except Exception as e:
            self.logger.error(f"Erro durante scraping: {e}")
            result.error_message = str(e)
            result.success = False
            
            # Registrar falha no rate manager
            rate_manager.record_failure(portal_name)
            
            # Registrar falha do proxy se estiver sendo usado
            if self.current_proxy:
                proxy_manager.report_proxy_result(self.current_proxy, False)
                self.logger.debug(f"Proxy {self.current_proxy.ip}:{self.current_proxy.port} - falha")
            
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
