# backend/scrapers/zapimoveis_stealth.py
"""
Scraper ZapImóveis com sistema completo de anti-detecção
"""
import time
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .stealth_base_scraper import StealthBaseScraper, ScrapingConfig

class ZapImoveisStealthScraper(StealthBaseScraper):
    """
    Scraper ZapImóveis com proteção anti-detecção completa
    
    Recursos:
    - Selenium Stealth integrado
    - Rate limiting inteligente específico para ZAP
    - Comportamento humano simulado
    - Tratamento de bloqueios e captchas
    """
    
    def __init__(self, headless: bool = True, simulate_human: bool = True):
        config = ScrapingConfig(
            portal='zapimoveis',
            headless=headless,
            max_retries=3,
            timeout=30,
            simulate_human=simulate_human,
            use_stealth=True
        )
        super().__init__(config)
        
        self.base_url = "https://www.zapimoveis.com.br"
        self.selectors = {
            'property_cards': '[data-testid="property-card-content"]',
            'property_links': 'a[data-testid="property-card-link"]',
            'price': '[data-testid="price-info-value"]',
            'address': '[data-testid="property-card-subtitle"]',
            'title': '[data-testid="property-card-title"]',
            'details': '[data-testid="property-card-details"]',
            'area': '[data-testid="property-card-area"]',
            'rooms': '[data-testid="property-card-rooms"]',
            'bathrooms': '[data-testid="property-card-bathrooms"]',
            'parking': '[data-testid="property-card-parking"]',
            'next_page': '[data-testid="pagination-next"]'
        }
    
    def build_search_url(self, 
                        tipo: str = 'apartamento', 
                        transacao: str = 'venda',
                        cidade: str = 'sao-paulo',
                        bairro: str = None,
                        preco_min: int = None,
                        preco_max: int = None,
                        quartos_min: int = None,
                        **kwargs) -> str:
        """
        Constrói URL de busca para ZapImóveis
        
        Args:
            tipo: Tipo do imóvel (apartamento, casa, etc.)
            transacao: Tipo de transação (venda, aluguel)
            cidade: Cidade da busca
            bairro: Bairro específico (opcional)
            preco_min: Preço mínimo
            preco_max: Preço máximo
            quartos_min: Número mínimo de quartos
            
        Returns:
            URL formatada para busca
        """
        # URL base
        url_parts = [self.base_url, transacao, tipo, cidade]
        
        if bairro:
            url_parts.append(bairro)
        
        base_url = '/'.join(url_parts) + '/'
        
        # Parâmetros de filtro
        params = []
        if preco_min:
            params.append(f"preco-minimo={preco_min}")
        if preco_max:
            params.append(f"preco-maximo={preco_max}")
        if quartos_min:
            params.append(f"quartos-minimo={quartos_min}")
        
        if params:
            base_url += '?' + '&'.join(params)
        
        return base_url
    
    def get_property_links(self, search_url: str) -> List[str]:
        """
        Extrai links de imóveis da página de busca
        
        Args:
            search_url: URL da página de busca
            
        Returns:
            Lista de URLs de imóveis
        """
        property_links = []
        
        try:
            if not self.driver_wrapper:
                raise RuntimeError("Driver não inicializado")
            
            driver = self.driver_wrapper.driver
            
            # Aguardar carregamento dos cards
            wait = WebDriverWait(driver, self.config.timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['property_cards'])))
            
            # Simular scroll para carregar mais imóveis
            if self.config.simulate_human:
                self.logger.info("Simulando scroll para carregar mais imóveis...")
                for _ in range(3):
                    self.driver_wrapper.scroll_page('down', 800)
                    self.driver_wrapper.wait_and_think(2, 4)
            
            # Encontrar todos os links de imóveis
            link_elements = driver.find_elements(By.CSS_SELECTOR, self.selectors['property_links'])
            
            for element in link_elements:
                try:
                    href = element.get_attribute('href')
                    if href and '/imovel/' in href:
                        # Garantir URL absoluta
                        full_url = urljoin(self.base_url, href)
                        property_links.append(full_url)
                except Exception as e:
                    self.logger.debug(f"Erro ao extrair link: {e}")
                    continue
            
            # Remover duplicatas mantendo ordem
            property_links = list(dict.fromkeys(property_links))
            
            self.logger.info(f"Encontrados {len(property_links)} links únicos de imóveis")
            
        except TimeoutException:
            self.logger.error("Timeout ao aguardar carregamento dos imóveis")
        except Exception as e:
            self.logger.error(f"Erro ao extrair links de imóveis: {e}")
        
        return property_links
    
    def extract_property_data(self, property_url: str) -> Optional[Dict[str, Any]]:
        """
        Extrai dados detalhados de um imóvel específico
        
        Args:
            property_url: URL do imóvel
            
        Returns:
            Dicionário com dados do imóvel ou None se erro
        """
        try:
            if not self.driver_wrapper:
                raise RuntimeError("Driver não inicializado")
            
            # Navegar para página do imóvel
            if not self.navigate_to_url(property_url, simulate_reading=True):
                return None
            
            driver = self.driver_wrapper.driver
            wait = WebDriverWait(driver, self.config.timeout)
            
            # Simular leitura da página
            if self.config.simulate_human:
                self.driver_wrapper.scroll_page('down', 600)
                self.driver_wrapper.wait_and_think(3, 6)
                self.driver_wrapper.scroll_page('down', 400)
                self.driver_wrapper.wait_and_think(2, 4)
            
            # Extrair dados básicos
            property_data = {
                'url': property_url,
                'portal': 'zapimoveis',
                'scraped_at': time.time()
            }
            
            # Preço
            try:
                price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['price'])))
                price_text = price_element.text.strip()
                property_data['preco_texto'] = price_text
                property_data['preco'] = self._extract_price(price_text)
            except:
                property_data['preco_texto'] = None
                property_data['preco'] = None
            
            # Título
            try:
                title_element = driver.find_element(By.CSS_SELECTOR, self.selectors['title'])
                property_data['titulo'] = title_element.text.strip()
            except:
                property_data['titulo'] = None
            
            # Endereço
            try:
                address_element = driver.find_element(By.CSS_SELECTOR, self.selectors['address'])
                property_data['endereco'] = address_element.text.strip()
            except:
                property_data['endereco'] = None
            
            # Detalhes (quartos, banheiros, área, etc.)
            try:
                details = self._extract_property_details(driver)
                property_data.update(details)
            except Exception as e:
                self.logger.debug(f"Erro ao extrair detalhes: {e}")
            
            # Características adicionais
            try:
                features = self._extract_property_features(driver)
                property_data['caracteristicas'] = features
            except Exception as e:
                self.logger.debug(f"Erro ao extrair características: {e}")
            
            # Informações do anunciante
            try:
                advertiser = self._extract_advertiser_info(driver)
                property_data['anunciante'] = advertiser
            except Exception as e:
                self.logger.debug(f"Erro ao extrair info do anunciante: {e}")
            
            # Coordenadas (se disponível)
            try:
                coordinates = self._extract_coordinates(driver)
                property_data.update(coordinates)
            except Exception as e:
                self.logger.debug(f"Erro ao extrair coordenadas: {e}")
            
            self.logger.info(f"Dados extraídos com sucesso para: {property_url}")
            return property_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados do imóvel {property_url}: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extrai valor numérico do preço"""
        if not price_text:
            return None
        
        # Remover caracteres não numéricos exceto pontos e vírgulas
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        
        # Converter para float
        try:
            if ',' in price_clean and '.' in price_clean:
                # Formato brasileiro: 1.234.567,89
                price_clean = price_clean.replace('.', '').replace(',', '.')
            elif ',' in price_clean:
                # Formato: 1234567,89
                price_clean = price_clean.replace(',', '.')
            
            return float(price_clean)
        except:
            return None
    
    def _extract_property_details(self, driver) -> Dict[str, Any]:
        """Extrai detalhes como quartos, banheiros, área"""
        details = {}
        
        # Quartos
        try:
            rooms_element = driver.find_element(By.CSS_SELECTOR, self.selectors['rooms'])
            rooms_text = rooms_element.text.strip()
            details['quartos'] = self._extract_number(rooms_text)
        except:
            details['quartos'] = None
        
        # Banheiros
        try:
            bath_element = driver.find_element(By.CSS_SELECTOR, self.selectors['bathrooms'])
            bath_text = bath_element.text.strip()
            details['banheiros'] = self._extract_number(bath_text)
        except:
            details['banheiros'] = None
        
        # Área
        try:
            area_element = driver.find_element(By.CSS_SELECTOR, self.selectors['area'])
            area_text = area_element.text.strip()
            details['area_texto'] = area_text
            details['area_m2'] = self._extract_area(area_text)
        except:
            details['area_texto'] = None
            details['area_m2'] = None
        
        # Vagas de garagem
        try:
            parking_element = driver.find_element(By.CSS_SELECTOR, self.selectors['parking'])
            parking_text = parking_element.text.strip()
            details['vagas_garagem'] = self._extract_number(parking_text)
        except:
            details['vagas_garagem'] = None
        
        return details
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extrai número de um texto"""
        if not text:
            return None
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _extract_area(self, area_text: str) -> Optional[float]:
        """Extrai área em m²"""
        if not area_text:
            return None
        
        # Procurar por números seguidos de m² ou m2
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*m[²2]', area_text.lower())
        if match:
            area_str = match.group(1).replace(',', '.')
            try:
                return float(area_str)
            except:
                return None
        return None
    
    def _extract_property_features(self, driver) -> List[str]:
        """Extrai características do imóvel"""
        features = []
        
        try:
            # Procurar por seção de características
            feature_selectors = [
                '[data-testid="amenities-list"] li',
                '.amenities li',
                '.features li',
                '.property-features li'
            ]
            
            for selector in feature_selectors:
                try:
                    feature_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in feature_elements:
                        feature_text = element.text.strip()
                        if feature_text and feature_text not in features:
                            features.append(feature_text)
                    if features:
                        break
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Erro ao extrair características: {e}")
        
        return features
    
    def _extract_advertiser_info(self, driver) -> Dict[str, str]:
        """Extrai informações do anunciante"""
        advertiser = {}
        
        try:
            # Procurar por informações do anunciante
            name_selectors = [
                '[data-testid="advertiser-name"]',
                '.advertiser-name',
                '.broker-name'
            ]
            
            for selector in name_selectors:
                try:
                    name_element = driver.find_element(By.CSS_SELECTOR, selector)
                    advertiser['nome'] = name_element.text.strip()
                    break
                except:
                    continue
            
            # Tipo de anunciante
            type_selectors = [
                '[data-testid="advertiser-type"]',
                '.advertiser-type'
            ]
            
            for selector in type_selectors:
                try:
                    type_element = driver.find_element(By.CSS_SELECTOR, selector)
                    advertiser['tipo'] = type_element.text.strip()
                    break
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Erro ao extrair info do anunciante: {e}")
        
        return advertiser
    
    def _extract_coordinates(self, driver) -> Dict[str, float]:
        """Extrai coordenadas geográficas"""
        coordinates = {}
        
        try:
            # Procurar por dados de mapa no HTML
            scripts = driver.find_elements(By.TAG_NAME, 'script')
            
            for script in scripts:
                script_content = script.get_attribute('innerHTML')
                if script_content and ('latitude' in script_content or 'lat' in script_content):
                    # Procurar por padrões de coordenadas
                    lat_match = re.search(r'"lat(?:itude)?":\s*(-?\d+(?:\.\d+)?)', script_content)
                    lng_match = re.search(r'"lng|lon(?:gitude)?":\s*(-?\d+(?:\.\d+)?)', script_content)
                    
                    if lat_match and lng_match:
                        coordinates['latitude'] = float(lat_match.group(1))
                        coordinates['longitude'] = float(lng_match.group(1))
                        break
        except Exception as e:
            self.logger.debug(f"Erro ao extrair coordenadas: {e}")
        
        return coordinates
    
    def scrape_multiple_pages(self, 
                            max_pages: int = 5,
                            **search_params) -> List[Dict[str, Any]]:
        """
        Scraping de múltiplas páginas de resultados
        
        Args:
            max_pages: Número máximo de páginas a processar
            **search_params: Parâmetros de busca
            
        Returns:
            Lista consolidada de imóveis
        """
        all_properties = []
        
        try:
            if not self.start_session():
                return all_properties
            
            for page in range(1, max_pages + 1):
                self.logger.info(f"Processando página {page}/{max_pages}")
                
                # Adicionar parâmetro de página
                search_params['pagina'] = page
                search_url = self.build_search_url(**search_params)
                
                # Navegar para página
                if not self.navigate_to_url(search_url):
                    self.logger.warning(f"Falha ao carregar página {page}")
                    continue
                
                # Obter links da página atual
                page_links = self.get_property_links(search_url)
                
                if not page_links:
                    self.logger.info(f"Nenhum imóvel encontrado na página {page}")
                    break
                
                # Processar imóveis da página
                for link in page_links:
                    property_data = self.extract_property_data(link)
                    if property_data:
                        all_properties.append(property_data)
                    
                    # Pausa entre imóveis
                    if self.config.simulate_human:
                        self.driver_wrapper.wait_and_think(2, 5)
                
                # Pausa entre páginas
                if self.config.simulate_human and page < max_pages:
                    self.logger.info("Pausando entre páginas...")
                    self.driver_wrapper.wait_and_think(5, 10)
            
            self.logger.info(f"Scraping de múltiplas páginas concluído: {len(all_properties)} imóveis")
            
        except Exception as e:
            self.logger.error(f"Erro no scraping de múltiplas páginas: {e}")
        finally:
            self.end_session()
        
        return all_properties

# Função de conveniência para uso rápido
def scrape_zapimoveis(cidade: str = 'sao-paulo',
                     tipo: str = 'apartamento',
                     preco_max: int = None,
                     quartos_min: int = None,
                     max_imoveis: int = 50,
                     headless: bool = True) -> List[Dict[str, Any]]:
    """
    Função de conveniência para scraping rápido do ZapImóveis
    
    Args:
        cidade: Cidade para busca
        tipo: Tipo do imóvel
        preco_max: Preço máximo
        quartos_min: Número mínimo de quartos
        max_imoveis: Número máximo de imóveis
        headless: Se deve rodar em modo headless
        
    Returns:
        Lista de imóveis encontrados
    """
    scraper = ZapImoveisStealthScraper(headless=headless)
    
    try:
        properties = scraper.scrape_properties(
            cidade=cidade,
            tipo=tipo,
            preco_max=preco_max,
            quartos_min=quartos_min
        )
        
        # Limitar número de resultados
        return properties[:max_imoveis]
        
    except Exception as e:
        logging.error(f"Erro no scraping rápido: {e}")
        return []
