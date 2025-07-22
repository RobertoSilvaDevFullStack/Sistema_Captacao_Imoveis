#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZapImóveis Scraper Melhorado com Anti-Detecção
Versão otimizada com rotação de headers e rate limiting
"""
import os
import sys
import time
import random
import logging
from datetime import datetime

# Adicionar paths necessários
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(root_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, root_dir)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

# Importar utilitários de anti-detecção
try:
    from utils.header_rotator import header_rotator
    from utils.rate_limiter import rate_manager
    ANTI_DETECTION_AVAILABLE = True
except ImportError:
    ANTI_DETECTION_AVAILABLE = False
    print("⚠️ Utilitários de anti-detecção não disponíveis, usando configuração básica")

class ZapImoveisAdvancedV2:
    """Scraper ZapImóveis com anti-detecção melhorada"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.portal_name = 'zapimoveis'
        
    def _setup_driver_with_anti_detection(self):
        """Configura driver com máxima proteção anti-detecção"""
        chrome_options = Options()
        
        if ANTI_DETECTION_AVAILABLE:
            # Usar opções otimizadas do header_rotator
            selenium_options = header_rotator.get_selenium_options(self.portal_name)
            for option in selenium_options:
                chrome_options.add_argument(option)
        else:
            # Configuração básica se utilitários não estiverem disponíveis
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # User-agent básico
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # Configurações experimentais
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configurações de performance
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Scripts anti-detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']})")
        
        return driver
    
    def _apply_smart_delays(self, min_delay=2, max_delay=5):
        """Aplica delays inteligentes com variação"""
        if ANTI_DETECTION_AVAILABLE:
            # Usar rate manager se disponível
            rate_manager.wait_for_portal(self.portal_name)
        else:
            # Delay básico aleatório
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
    
    def _get_optimized_headers(self):
        """Obtém headers otimizados para ZapImóveis"""
        if ANTI_DETECTION_AVAILABLE:
            return header_rotator.get_random_headers(self.portal_name)
        else:
            # Headers básicos
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.zapimoveis.com.br/',
            }
    
    def scrape_properties(self, url, max_results=20):
        """Scraping principal com anti-detecção melhorada"""
        self.logger.info(f"🚀 Iniciando scraping ZapImóveis V2 (Anti-Detecção): {url}")
        
        driver = None
        properties = []
        
        try:
            # Aplicar rate limiting inteligente
            self._apply_smart_delays()
            
            # Configurar driver com proteção máxima
            driver = self._setup_driver_with_anti_detection()
            
            # Configurar headers se possível
            try:
                headers = self._get_optimized_headers()
                # Tentar aplicar headers via CDP
                driver.execute_cdp_cmd('Network.setRequestHeaders', {'headers': headers})
            except Exception as e:
                self.logger.warning(f"Não foi possível aplicar headers customizados: {e}")
            
            # Navegar para a página
            self.logger.info(f"📄 Navegando para: {url}")
            driver.get(url)
            
            # Aguardar carregamento inicial com delay inteligente
            self._apply_smart_delays(3, 6)
            
            # Verificar se a página carregou corretamente
            page_title = driver.title.lower()
            if 'blocked' in page_title or 'erro' in page_title:
                self.logger.warning(f"⚠️ Possível bloqueio detectado. Título: {driver.title}")
                if ANTI_DETECTION_AVAILABLE:
                    rate_manager.record_failure(self.portal_name)
                return []
            
            # Aguardar elementos aparecerem
            try:
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*="card"], .result-card')))
            except Exception as e:
                self.logger.warning(f"⏰ Timeout aguardando elementos: {e}")
            
            # Simular comportamento humano - scroll suave
            self._simulate_human_behavior(driver)
            
            # Buscar elementos de propriedades com múltiplos seletores
            selectors = [
                '[data-testid*="card"]',
                '[data-testid="result-card-container"]',
                '.result-card',
                '[data-testid="property-card"]',
                '.property-card',
                '.listing-card'
            ]
            
            elements = []
            for selector in selectors:
                try:
                    found = driver.find_elements(By.CSS_SELECTOR, selector)
                    if found:
                        elements = found
                        self.logger.info(f"✅ Encontrados {len(elements)} elementos com seletor: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not elements:
                self.logger.warning("🔍 Nenhum elemento de propriedade encontrado")
                return []
            
            # Processar elementos encontrados
            self.logger.info(f"🏠 Processando {min(len(elements), max_results)} propriedades...")
            
            for i, element in enumerate(elements[:max_results]):
                try:
                    property_data = self._extract_property_data_v2(element)
                    if property_data:
                        properties.append(property_data)
                        self.logger.debug(f"✅ Propriedade {i+1}: {property_data.get('title', 'N/A')[:50]}...")
                    
                    # Delay entre extrações para parecer humano
                    if i < len(elements) - 1:
                        time.sleep(random.uniform(0.3, 1.0))
                        
                except Exception as e:
                    self.logger.error(f"❌ Erro ao extrair propriedade {i+1}: {e}")
                    continue
            
            # Registrar sucesso se encontrou propriedades
            if properties and ANTI_DETECTION_AVAILABLE:
                rate_manager.record_success(self.portal_name)
            
            self.logger.info(f"🎉 Scraping concluído: {len(properties)} propriedades extraídas")
            
        except Exception as e:
            self.logger.error(f"💥 Erro durante scraping: {e}")
            if ANTI_DETECTION_AVAILABLE:
                rate_manager.record_failure(self.portal_name)
            
        finally:
            if driver:
                driver.quit()
        
        return properties
    
    def _simulate_human_behavior(self, driver):
        """Simula comportamento humano na página"""
        try:
            # Scroll suave para baixo
            driver.execute_script("window.scrollTo({top: 300, behavior: 'smooth'});")
            time.sleep(random.uniform(1, 2))
            
            # Scroll um pouco mais
            driver.execute_script("window.scrollTo({top: 600, behavior: 'smooth'});")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Voltar para o topo
            driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            time.sleep(random.uniform(0.5, 1.0))
            
        except Exception as e:
            self.logger.debug(f"Erro ao simular comportamento humano: {e}")
    
    def _extract_property_data_v2(self, element):
        """Extração melhorada de dados da propriedade"""
        try:
            property_data = {
                'title': self._extract_text_safe(element, 'title'),
                'price': self._extract_price_v2(element),
                'url': self._extract_url_v2(element),
                'address': self._extract_text_safe(element, 'address'),
                'area': self._extract_numeric_safe(element, 'area'),
                'bedrooms': self._extract_numeric_safe(element, 'bedrooms'),
                'bathrooms': self._extract_numeric_safe(element, 'bathrooms'),
                'parking_spaces': self._extract_numeric_safe(element, 'parking'),
                'source': 'ZapImoveis',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Filtrar propriedades vazias
            if not property_data['title'] and not property_data['price']:
                return None
                
            return property_data
            
        except Exception as e:
            self.logger.error(f"Erro na extração de dados: {e}")
            return None
    
    def _extract_text_safe(self, element, field_type):
        """Extração segura de texto"""
        try:
            text = element.text.strip()
            if text:
                return text
        except:
            pass
        return None
    
    def _extract_price_v2(self, element):
        """Extração melhorada de preço"""
        try:
            text = element.text
            # Padrões de preço mais robustos
            patterns = [
                r'R\$\s*([\d.,]+)',
                r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    price_str = match.group(1).replace('.', '').replace(',', '.')
                    try:
                        price = float(price_str)
                        if 10000 <= price <= 50000000:  # Validação de faixa
                            return price
                    except:
                        continue
        except:
            pass
        return None
    
    def _extract_url_v2(self, element):
        """Extração melhorada de URL"""
        try:
            link = element.find_element(By.TAG_NAME, 'a')
            url = link.get_attribute('href')
            if url and not url.startswith('http'):
                url = f"https://www.zapimoveis.com.br{url}"
            return url
        except:
            pass
        return None
    
    def _extract_numeric_safe(self, element, field_type):
        """Extração segura de valores numéricos"""
        try:
            text = element.text.lower()
            
            if field_type == 'area':
                match = re.search(r'(\d+)\s*m²', text)
            elif field_type == 'bedrooms':
                match = re.search(r'(\d+)\s*quarto', text)
            elif field_type == 'bathrooms':
                match = re.search(r'(\d+)\s*banho', text)
            elif field_type == 'parking':
                match = re.search(r'(\d+)\s*vaga', text)
            else:
                return None
                
            if match:
                return int(match.group(1))
        except:
            pass
        return None

# Exemplo de uso
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ZapImóveis Scraper V2 com Anti-Detecção')
    parser.add_argument('--city', default='rio-de-janeiro', help='Cidade para busca')
    parser.add_argument('--type', default='apartamento', choices=['apartamento', 'casa'], help='Tipo de imóvel')
    parser.add_argument('--max', type=int, default=5, help='Máximo de resultados')
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Mapeamento de cidades
    city_mapping = {
        'rio-de-janeiro': 'rj+rio-de-janeiro',
        'sao-paulo': 'sp+sao-paulo',
        'belo-horizonte': 'mg+belo-horizonte'
    }
    
    city_code = city_mapping.get(args.city, 'rj+rio-de-janeiro')
    
    if args.type == 'apartamento':
        url = f"https://www.zapimoveis.com.br/venda/apartamentos/{city_code}/"
    else:
        url = f"https://www.zapimoveis.com.br/venda/casas/{city_code}/"
    
    print(f"🏠 ZapImóveis Scraper V2 - Anti-Detecção")
    print(f"🔍 Buscando {args.type} em {args.city}")
    print(f"🌐 URL: {url}")
    print(f"📊 Máximo: {args.max} resultados")
    
    if ANTI_DETECTION_AVAILABLE:
        print("✅ Sistema anti-detecção ativo")
    else:
        print("⚠️ Sistema anti-detecção básico")
    
    print("-" * 50)
    
    scraper = ZapImoveisAdvancedV2()
    results = scraper.scrape_properties(url, max_results=args.max)
    
    print(f"\n🎉 Resultados: {len(results)} propriedades encontradas")
    
    for i, prop in enumerate(results, 1):
        print(f"\n{i}. {prop.get('title', 'N/A')[:60]}...")
        if prop.get('price'):
            print(f"   💰 Preço: R$ {prop['price']:,.2f}")
        if prop.get('area'):
            print(f"   📐 Área: {prop['area']} m²")
        if prop.get('url'):
            print(f"   🔗 URL: {prop['url'][:60]}...")
