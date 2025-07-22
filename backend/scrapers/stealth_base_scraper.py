# backend/scrapers/stealth_base_scraper.py
"""
Base Scraper com integração completa do sistema Selenium Stealth e Anti-Detecção
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Imports do sistema anti-detecção
try:
    from src.utils.selenium_stealth import create_stealth_driver, StealthWebDriver
    from src.utils.advanced_rate_limiter import advanced_rate_manager, BlockingLevel
    from src.utils.rate_limiting_decorator import intelligent_rate_limit
    from src.utils.header_rotator import header_rotator
    STEALTH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Sistema stealth não disponível: {e}")
    STEALTH_AVAILABLE = False

@dataclass
class ScrapingConfig:
    """Configuração para scraping"""
    portal: str
    headless: bool = True
    max_retries: int = 3
    timeout: int = 30
    simulate_human: bool = True
    use_stealth: bool = True

class StealthBaseScraper(ABC):
    """
    Base Scraper com sistema completo de anti-detecção
    
    Recursos:
    - Selenium Stealth com undetected-chromedriver
    - Rate limiting inteligente
    - Comportamento humano simulado
    - Monitoramento de bloqueios
    - Retry automático
    """
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.portal = config.portal
        self.logger = self._setup_logging()
        self.driver_wrapper: Optional[StealthWebDriver] = None
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'blocked_requests': 0,
            'start_time': datetime.now()
        }
        
        if not STEALTH_AVAILABLE:
            self.logger.warning("Sistema stealth não disponível - usando Selenium básico")
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging específico para o scraper"""
        logger = logging.getLogger(f"scraper.{self.portal}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @intelligent_rate_limit(action_type='navigation', max_retries=3)
    def navigate_to_url(self, url: str, simulate_reading: bool = True) -> bool:
        """
        Navega para URL com proteção anti-detecção
        
        Args:
            url: URL de destino
            simulate_reading: Se deve simular leitura humana
            
        Returns:
            bool: Sucesso da navegação
        """
        try:
            if not self.driver_wrapper:
                raise RuntimeError("Driver não foi inicializado")
            
            self.logger.info(f"Navegando para: {url}")
            self.driver_wrapper.get(url, simulate_reading=simulate_reading)
            
            # Aguardar carregamento completo
            self.driver_wrapper.wait_and_think(1, 3)
            
            self.stats['total_requests'] += 1
            self.stats['successful_requests'] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na navegação para {url}: {e}")
            self.stats['total_requests'] += 1
            self.stats['failed_requests'] += 1
            
            # Registrar falha no rate manager
            if STEALTH_AVAILABLE:
                advanced_rate_manager.record_request_result(
                    portal=self.portal,
                    success=False,
                    response_time=5.0,
                    status_code=500,
                    blocking_level=BlockingLevel.SOFT_BLOCK,
                    error_type=str(type(e).__name__)
                )
            
            return False
    
    def start_session(self) -> bool:
        """Inicia sessão de scraping com driver stealth"""
        try:
            self.logger.info(f"Iniciando sessão de scraping para {self.portal}")
            
            if STEALTH_AVAILABLE and self.config.use_stealth:
                # Criar driver stealth
                self.driver_wrapper = create_stealth_driver(
                    portal=self.portal,
                    headless=self.config.headless
                )
                self.driver_wrapper.driver = self.driver_wrapper.create_driver()
                self.logger.info("Driver stealth criado com sucesso")
                
            else:
                # Fallback para Selenium básico
                self.driver_wrapper = self._create_basic_driver()
                self.logger.warning("Usando Selenium básico (stealth não disponível)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sessão: {e}")
            return False
    
    def _create_basic_driver(self) -> Any:
        """Cria driver Selenium básico como fallback"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if self.config.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Usar headers do sistema
        if STEALTH_AVAILABLE:
            headers = header_rotator.get_random_headers(self.portal)
            options.add_argument(f'--user-agent={headers["User-Agent"]}')
        
        driver = webdriver.Chrome(options=options)
        
        # Wrapper básico
        class BasicDriverWrapper:
            def __init__(self, driver):
                self.driver = driver
                
            def get(self, url, simulate_reading=True):
                self.driver.get(url)
                if simulate_reading:
                    time.sleep(2)  # Pausa básica
                    
            def wait_and_think(self, min_sec, max_sec):
                import random
                time.sleep(random.uniform(min_sec, max_sec))
                
            def scroll_page(self, direction='down', distance=300):
                if direction == 'down':
                    self.driver.execute_script(f"window.scrollBy(0, {distance});")
                else:
                    self.driver.execute_script(f"window.scrollBy(0, -{distance});")
                time.sleep(1)
                
            def find_and_click(self, by, value, simulate_human=True):
                element = self.driver.find_element(by, value)
                if simulate_human:
                    time.sleep(0.5)
                element.click()
                return element
                
            def quit(self):
                self.driver.quit()
        
        return BasicDriverWrapper(driver)
    
    def end_session(self):
        """Encerra sessão de scraping"""
        if self.driver_wrapper:
            try:
                if hasattr(self.driver_wrapper, 'quit'):
                    self.driver_wrapper.quit()
                elif hasattr(self.driver_wrapper, 'driver') and self.driver_wrapper.driver:
                    self.driver_wrapper.driver.quit()
                self.logger.info("Sessão encerrada com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao encerrar sessão: {e}")
            finally:
                self.driver_wrapper = None
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da sessão atual"""
        duration = datetime.now() - self.stats['start_time']
        success_rate = (
            self.stats['successful_requests'] / max(1, self.stats['total_requests'])
        ) * 100
        
        return {
            'portal': self.portal,
            'duration_minutes': duration.total_seconds() / 60,
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'blocked_requests': self.stats['blocked_requests'],
            'success_rate': success_rate,
            'requests_per_minute': self.stats['total_requests'] / max(1, duration.total_seconds() / 60)
        }
    
    @abstractmethod
    def extract_property_data(self, property_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um imóvel específico
        
        Args:
            property_url: URL do imóvel
            
        Returns:
            Dados do imóvel ou None se erro
        """
        pass
    
    @abstractmethod
    def get_property_links(self, search_url: str) -> List[str]:
        """
        Obtém links de imóveis de uma página de busca
        
        Args:
            search_url: URL da página de busca
            
        Returns:
            Lista de URLs de imóveis
        """
        pass
    
    @abstractmethod
    def build_search_url(self, **kwargs) -> str:
        """
        Constrói URL de busca baseada nos parâmetros
        
        Returns:
            URL de busca formatada
        """
        pass
    
    def scrape_properties(self, **search_params) -> List[Dict[str, Any]]:
        """
        Método principal de scraping com proteção completa
        
        Args:
            **search_params: Parâmetros de busca específicos do portal
            
        Returns:
            Lista de imóveis encontrados
        """
        properties = []
        
        try:
            # Iniciar sessão
            if not self.start_session():
                self.logger.error("Falha ao iniciar sessão")
                return properties
            
            # Construir URL de busca
            search_url = self.build_search_url(**search_params)
            self.logger.info(f"URL de busca: {search_url}")
            
            # Navegar para página de busca
            if not self.navigate_to_url(search_url, simulate_reading=True):
                self.logger.error("Falha ao navegar para página de busca")
                return properties
            
            # Simular comportamento humano na página de busca
            if self.config.simulate_human and self.driver_wrapper:
                self.logger.info("Simulando análise da página de busca...")
                self.driver_wrapper.scroll_page('down', 400)
                self.driver_wrapper.wait_and_think(2, 5)
                self.driver_wrapper.scroll_page('down', 300)
                self.driver_wrapper.wait_and_think(1, 3)
            
            # Obter links de propriedades
            property_links = self.get_property_links(search_url)
            self.logger.info(f"Encontrados {len(property_links)} links de imóveis")
            
            # Processar cada imóvel
            for i, link in enumerate(property_links, 1):
                try:
                    self.logger.info(f"Processando imóvel {i}/{len(property_links)}")
                    
                    # Rate limiting automático aplicado pelo decorator
                    property_data = self.extract_property_data(link)
                    
                    if property_data:
                        properties.append(property_data)
                        self.logger.info(f"Imóvel {i} extraído com sucesso")
                    else:
                        self.logger.warning(f"Falha ao extrair dados do imóvel {i}")
                    
                    # Pausa entre imóveis para simular comportamento humano
                    if self.config.simulate_human:
                        self.driver_wrapper.wait_and_think(3, 8)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao processar imóvel {i}: {e}")
                    self.stats['failed_requests'] += 1
                    continue
            
            self.logger.info(f"Scraping concluído: {len(properties)} imóveis extraídos")
            
        except Exception as e:
            self.logger.error(f"Erro geral no scraping: {e}")
            
        finally:
            # Encerrar sessão
            self.end_session()
            
            # Log das estatísticas finais
            stats = self.get_session_stats()
            self.logger.info(f"Estatísticas da sessão: {stats}")
        
        return properties
    
    def __enter__(self):
        """Context manager entry"""
        if self.start_session():
            return self
        else:
            raise RuntimeError("Falha ao iniciar sessão")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.end_session()

class StealthScrapingSession:
    """
    Context manager para sessões de scraping com múltiplos portais
    """
    
    def __init__(self, scrapers: List[StealthBaseScraper]):
        self.scrapers = scrapers
        self.results = {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        for scraper in self.scrapers:
            scraper.end_session()
    
    def run_parallel_scraping(self, search_params_list: List[Dict]) -> Dict[str, List]:
        """
        Executa scraping em paralelo para múltiplos portais
        
        Args:
            search_params_list: Lista de parâmetros para cada scraper
            
        Returns:
            Dicionário com resultados por portal
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def scrape_portal(scraper, params):
            try:
                portal_name = scraper.portal
                results = scraper.scrape_properties(**params)
                return portal_name, results
            except Exception as e:
                logging.error(f"Erro no scraping paralelo para {scraper.portal}: {e}")
                return scraper.portal, []
        
        # Executar scrapers em paralelo
        with ThreadPoolExecutor(max_workers=min(3, len(self.scrapers))) as executor:
            futures = []
            
            for scraper, params in zip(self.scrapers, search_params_list):
                future = executor.submit(scrape_portal, scraper, params)
                futures.append(future)
            
            # Coletar resultados
            for future in as_completed(futures):
                try:
                    portal_name, results = future.result()
                    self.results[portal_name] = results
                except Exception as e:
                    logging.error(f"Erro ao coletar resultado: {e}")
        
        return self.results
