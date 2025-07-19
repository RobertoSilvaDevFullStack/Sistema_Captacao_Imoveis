#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VivaReal com Playwright - Solução moderna para Cloudflare
"""

import asyncio
import logging
import random
import time
from typing import List, Dict, Optional
from datetime import datetime
import re
import json

# Importações condicionais
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright não instalado. Para instalar: pip install playwright && playwright install")

class VivaRealPlaywright:
    """Scraper VivaReal usando Playwright para contornar Cloudflare"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def init_browser(self):
        """Inicializa browser com configurações anti-detecção"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright não está disponível")
            
        playwright = await async_playwright().start()
        
        # Configurações para evitar detecção
        self.browser = await playwright.chromium.launch(
            headless=True,  # Pode mudar para False para debug
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Criar contexto com user agent realista
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='pt-BR',
            timezone_id='America/Sao_Paulo'
        )
        
        # Configurações adicionais para evitar detecção
        await self.context.add_init_script("""
            // Remove navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en'],
            });
        """)
        
        self.page = await self.context.new_page()
        
    async def scrape_properties(self, location: str = 'rio-de-janeiro', property_type: str = 'apartamento', max_results: int = 20) -> List[Dict]:
        """
        Scraping principal usando Playwright
        
        Args:
            location: cidade (ex: 'rio-de-janeiro', 'sao-paulo')
            property_type: tipo ('apartamento', 'casa', 'cobertura')
            max_results: máximo de resultados
        """
        if not self.browser:
            await self.init_browser()
            
        logging.info(f"Iniciando scraping VivaReal Playwright: {location} - {property_type}")
        
        try:
            # Construir URL de busca
            base_url = "https://www.vivareal.com.br"
            
            # Mapear tipos de propriedade
            type_mapping = {
                'apartamento': 'apartamento',
                'casa': 'casa',
                'cobertura': 'cobertura',
                'todos': ''
            }
            
            prop_type = type_mapping.get(property_type, 'apartamento')
            
            # URL de busca
            if prop_type:
                search_url = f"{base_url}/venda/{prop_type}/{location}/"
            else:
                search_url = f"{base_url}/venda/imoveis/{location}/"
            
            logging.info(f"Acessando: {search_url}")
            
            # Navegar para a página com delays aleatórios
            await self.page.goto(search_url, wait_until='networkidle', timeout=30000)
            
            # Aguardar um pouco após carregar
            await asyncio.sleep(random.uniform(2, 4))
            
            # Verificar se há Cloudflare challenge
            if await self._handle_cloudflare():
                logging.info("Cloudflare detectado e possivelmente contornado")
                await asyncio.sleep(5)  # Aguardar processamento
            
            # Tentar aguardar lista de propriedades
            try:
                await self.page.wait_for_selector('[data-testid="property-card"], .property-card, .listing-item', timeout=15000)
                logging.info("Propriedades carregadas")
            except:
                logging.warning("Timeout aguardando propriedades - tentando continuar")
            
            # Extrair propriedades usando múltiplos seletores
            properties = await self._extract_properties(max_results)
            
            logging.info(f"Total extraído: {len(properties)} propriedades")
            return properties
            
        except Exception as e:
            logging.error(f"Erro no scraping: {e}")
            return []
    
    async def _handle_cloudflare(self) -> bool:
        """Detecta e tenta contornar Cloudflare"""
        try:
            page_content = await self.page.content()
            
            # Verificar indicadores de Cloudflare
            cloudflare_indicators = [
                'checking your browser',
                'cloudflare',
                'ddos protection',
                'cf-browser-verification',
                'just a moment'
            ]
            
            content_lower = page_content.lower()
            
            if any(indicator in content_lower for indicator in cloudflare_indicators):
                logging.info("🛡️ Cloudflare detectado - aguardando...")
                
                # Aguardar até 30 segundos para o challenge passar
                for i in range(30):
                    await asyncio.sleep(1)
                    
                    # Verificar se saiu do challenge
                    current_content = await self.page.content()
                    if not any(indicator in current_content.lower() for indicator in cloudflare_indicators):
                        logging.info("✅ Cloudflare contornado")
                        return True
                
                # Se ainda estiver no challenge, tentar algumas ações
                try:
                    # Tentar clicar em botão de verificação se existir
                    verify_button = await self.page.query_selector('input[type="button"], button[type="submit"], #challenge-form button')
                    if verify_button:
                        await verify_button.click()
                        await asyncio.sleep(5)
                        return True
                except:
                    pass
                
                logging.warning("❌ Não foi possível contornar Cloudflare automaticamente")
                return False
            
            return False
            
        except Exception as e:
            logging.debug(f"Erro ao verificar Cloudflare: {e}")
            return False
    
    async def _extract_properties(self, max_results: int) -> List[Dict]:
        """Extrai propriedades da página"""
        properties = []
        
        try:
            # Múltiplos seletores para diferentes layouts
            selectors = [
                '[data-testid="property-card"]',
                '.property-card',
                '.listing-item',
                '.js-card-selector',
                '.results-item',
                'article[data-position]'
            ]
            
            property_elements = []
            
            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    property_elements = elements
                    logging.info(f"Usando seletor: {selector} - {len(elements)} elementos")
                    break
            
            if not property_elements:
                logging.warning("❌ Nenhum elemento de propriedade encontrado")
                return []
            
            # Extrair dados de cada propriedade
            for i, element in enumerate(property_elements[:max_results]):
                try:
                    property_data = await self._extract_single_property(element)
                    if property_data:
                        properties.append(property_data)
                        
                except Exception as e:
                    logging.debug(f"Erro ao extrair propriedade {i}: {e}")
                    continue
            
        except Exception as e:
            logging.error(f"Erro na extração: {e}")
        
        return properties
    
    async def _extract_single_property(self, element) -> Optional[Dict]:
        """Extrai dados de uma única propriedade"""
        try:
            # Título
            title_selectors = [
                '[data-testid="property-card-title"]',
                '.property-card__title',
                '.listing-title',
                'h2 a',
                '.js-card-title'
            ]
            title = await self._get_text_from_selectors(element, title_selectors)
            
            # Preço
            price_selectors = [
                '[data-testid="price-info"]',
                '.property-card__price',
                '.listing-price',
                '.js-price',
                '.price'
            ]
            price = await self._get_text_from_selectors(element, price_selectors)
            
            # Localização
            location_selectors = [
                '[data-testid="property-card-location"]',
                '.property-card__address',
                '.listing-location',
                '.js-card-address',
                '.address'
            ]
            location = await self._get_text_from_selectors(element, location_selectors)
            
            # Área
            area_selectors = [
                '[data-testid="property-card-area"]',
                '.property-card__area',
                '.listing-area',
                '.js-area',
                '.area'
            ]
            area = await self._get_text_from_selectors(element, area_selectors)
            
            # Quartos
            bedroom_selectors = [
                '[data-testid="property-card-bedrooms"]',
                '.property-card__bedrooms',
                '.listing-bedrooms',
                '.js-bedrooms',
                '.bedrooms'
            ]
            bedrooms = await self._get_text_from_selectors(element, bedroom_selectors)
            
            # Banheiros
            bathroom_selectors = [
                '[data-testid="property-card-bathrooms"]',
                '.property-card__bathrooms',
                '.listing-bathrooms',
                '.js-bathrooms',
                '.bathrooms'
            ]
            bathrooms = await self._get_text_from_selectors(element, bathroom_selectors)
            
            # URL
            url_selectors = [
                'a[href*="/imovel/"]',
                'a[href*="/apartamento/"]',
                'a[href*="/casa/"]',
                'a'
            ]
            url = await self._get_href_from_selectors(element, url_selectors)
            
            # Montar dados da propriedade
            property_data = {
                'title': title or 'Sem título',
                'price': self._clean_price(price) if price else 'N/A',
                'location': location or 'N/A',
                'area': self._clean_area(area) if area else 'N/A',
                'bedrooms': self._extract_number(bedrooms) if bedrooms else 'N/A',
                'bathrooms': self._extract_number(bathrooms) if bathrooms else 'N/A',
                'url': self._clean_url(url) if url else 'N/A',
                'source': 'VivaReal (Playwright)',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Só retornar se tiver pelo menos título ou preço
            if property_data['title'] != 'Sem título' or property_data['price'] != 'N/A':
                return property_data
            
        except Exception as e:
            logging.debug(f"Erro ao extrair propriedade individual: {e}")
        
        return None
    
    async def _get_text_from_selectors(self, element, selectors: List[str]) -> Optional[str]:
        """Tenta obter texto usando múltiplos seletores"""
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    text = await sub_element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    async def _get_href_from_selectors(self, element, selectors: List[str]) -> Optional[str]:
        """Tenta obter href usando múltiplos seletores"""
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    href = await sub_element.get_attribute('href')
                    if href:
                        return href
            except:
                continue
        return None
    
    def _clean_price(self, price: str) -> str:
        """Limpa e formata preço"""
        if not price:
            return 'N/A'
        
        # Extrair apenas números e pontos/vírgulas
        price_clean = re.sub(r'[^\d.,]', '', price)
        if price_clean:
            return f"R$ {price_clean}"
        return price
    
    def _clean_area(self, area: str) -> str:
        """Limpa e formata área"""
        if not area:
            return 'N/A'
        
        # Extrair número e adicionar m² se não tiver
        area_match = re.search(r'(\d+)', area)
        if area_match:
            num = area_match.group(1)
            return f"{num} m²"
        return area
    
    def _extract_number(self, text: str) -> str:
        """Extrai número do texto"""
        if not text:
            return 'N/A'
        
        number_match = re.search(r'(\d+)', text)
        if number_match:
            return number_match.group(1)
        return text
    
    def _clean_url(self, url: str) -> str:
        """Limpa e completa URL"""
        if not url:
            return 'N/A'
        
        if url.startswith('/'):
            return f"https://www.vivareal.com.br{url}"
        elif not url.startswith('http'):
            return f"https://www.vivareal.com.br/{url}"
        return url
    
    async def close(self):
        """Fecha browser"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except:
            pass

# Classe wrapper para uso síncrono
class VivaRealPlaywrightSync:
    """Wrapper síncrono para o scraper Playwright"""
    
    def __init__(self):
        self.scraper = VivaRealPlaywright()
    
    def scrape_properties(self, location: str = 'rio-de-janeiro', property_type: str = 'apartamento', max_results: int = 20) -> List[Dict]:
        """Método síncrono para scraping"""
        return asyncio.run(self._scrape_async(location, property_type, max_results))
    
    async def _scrape_async(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Método assíncrono interno"""
        try:
            return await self.scraper.scrape_properties(location, property_type, max_results)
        finally:
            await self.scraper.close()
    
    def close(self):
        """Método de compatibilidade"""
        pass
