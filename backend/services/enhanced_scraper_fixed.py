# backend/services/enhanced_scraper_fixed.py
"""
Scraper Aprimorado com OCR Integrado - Versão Corrigida
Combina scraping tradicional com análise de imagens para máxima extração de dados.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import base64
import io
from urllib.parse import urljoin

# Imports com fallback
try:
    from .smart_data_extractor import SmartDataExtractor
    SMART_EXTRACTOR_AVAILABLE = True
except ImportError:
    SMART_EXTRACTOR_AVAILABLE = False
    SmartDataExtractor = None

# Web scraping
try:
    import requests
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    requests = None
    webdriver = None
    By = None
    WebDriverWait = None
    EC = None
    BeautifulSoup = None

class EnhancedScraper:
    """
    Scraper aprimorado que combina:
    1. Scraping estruturado tradicional
    2. Análise de imagens com OCR
    3. Validação cruzada de dados
    4. Cache inteligente
    """
    
    def __init__(self, use_ocr: bool = True, max_images_per_property: int = 3):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.use_ocr = use_ocr and SMART_EXTRACTOR_AVAILABLE
        self.max_images_per_property = max_images_per_property
        
        # Inicializar extrator inteligente
        if SMART_EXTRACTOR_AVAILABLE and SmartDataExtractor:
            self.smart_extractor = SmartDataExtractor(
                use_cache=True, 
                use_ocr=self.use_ocr
            )
        else:
            self.smart_extractor = None
        
        # Scrapers tradicionais - simplificado
        self.traditional_scrapers = {}
        
        # Configuração do navegador para captura de imagens
        self.driver_options = {
            'headless': True,
            'disable_images': False,  # Precisamos das imagens para OCR
            'window_size': (1920, 1080)
        }
        
        # Estatísticas
        self.stats: Dict[str, Any] = {
            'total_properties_scraped': 0,
            'ocr_enhanced_extractions': 0,
            'image_downloads': 0,
            'ocr_fallback_successes': 0,
            'validation_improvements': 0
        }
    
    async def initialize(self):
        """Inicializa todos os componentes"""
        try:
            if self.smart_extractor:
                await self.smart_extractor.initialize()
                self.logger.info("✅ Smart extractor inicializado")
            
            self.logger.info("✅ Enhanced scraper inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    async def scrape_property_enhanced(self, url: str, source: str = 'auto') -> Dict[str, Any]:
        """
        Scraping aprimorado de propriedade individual
        
        Args:
            url: URL da propriedade
            source: Fonte ('vivareal', 'olx', 'zapimoveis' ou 'auto')
        
        Returns:
            Dict com dados extraídos e metadados
        """
        start_time = datetime.now()
        self.stats['total_properties_scraped'] += 1
        
        # Resultado final - inicializar sempre
        result = {
            'url': url,
            'source': source,
            'timestamp': start_time.isoformat(),
            'success': False,
            'data': {},
            'extraction_methods': [],
            'images_analyzed': 0,
            'processing_time': 0.0,
            'errors': []
        }
        
        try:
            # Detectar fonte automaticamente se necessário
            if source == 'auto':
                source = self._detect_source(url)
                result['source'] = source
            
            # 1. Scraping tradicional primeiro
            traditional_data = await self._traditional_scraping(url, source)
            if traditional_data['success']:
                result['data'].update(traditional_data['data'])
                result['extraction_methods'].append('traditional_scraping')
                result['success'] = True
            
            # 2. Se OCR habilitado e dados incompletos, usar análise de imagens
            if self.use_ocr and self.smart_extractor and self._needs_image_analysis(result['data']):
                image_analysis_result = await self._analyze_property_images(url)
                
                if image_analysis_result['success']:
                    # Combinar dados usando smart extractor
                    enhanced_result = await self.smart_extractor.extract_property_data(
                        structured_data=result['data'],
                        images=image_analysis_result['images'],
                        url=url
                    )
                    
                    if enhanced_result['success']:
                        result['data'] = enhanced_result['data']
                        result['extraction_methods'].append('ocr_enhancement')
                        result['images_analyzed'] = len(image_analysis_result['images'])
                        result['success'] = True
                        self.stats['ocr_enhanced_extractions'] += 1
                        
                        # Verificar se OCR melhorou os dados
                        if self._ocr_improved_data(traditional_data['data'], enhanced_result['data']):
                            self.stats['ocr_fallback_successes'] += 1
            
            # 3. Validação final e limpeza
            result['data'] = self._clean_and_validate_data(result['data'])
            
            # 4. Metadados finais
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Log do resultado
            self._log_scraping_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro no scraping aprimorado: {e}")
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            return result
    
    async def _traditional_scraping(self, url: str, source: str) -> Dict[str, Any]:
        """Executa scraping tradicional"""
        try:
            # Scraping genérico usando BeautifulSoup
            data = await self._generic_scraping(url)
            return {
                'success': bool(data and any(v for v in data.values() if v)),
                'data': data or {}
            }
        
        except Exception as e:
            self.logger.error(f"❌ Erro no scraping tradicional: {e}")
            return {'success': False, 'data': {}, 'error': str(e)}
    
    async def _generic_scraping(self, url: str) -> Dict[str, Any]:
        """Scraping genérico usando BeautifulSoup"""
        try:
            # Verificar se requests e BeautifulSoup estão disponíveis
            if not requests or not BeautifulSoup:
                self.logger.warning("Requests ou BeautifulSoup não disponíveis")
                return {}
            
            # Fazer request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados usando padrões comuns
            extracted_data = {}
            
            # Preço
            price_selectors = [
                '[data-testid*="price"]',
                '.price', '.valor', '.preco',
                '[class*="price"]', '[class*="valor"]'
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text(strip=True)
                    price_value = self._extract_price_from_text(price_text)
                    if price_value:
                        extracted_data['price'] = price_value
                        break
            
            # Área
            area_selectors = [
                '[data-testid*="area"]',
                '.area', '.metros', '.m2',
                '[class*="area"]', '[class*="size"]'
            ]
            
            for selector in area_selectors:
                element = soup.select_one(selector)
                if element:
                    area_text = element.get_text(strip=True)
                    area_value = self._extract_area_from_text(area_text)
                    if area_value:
                        extracted_data['area'] = area_value
                        break
            
            # Quartos e banheiros
            room_selectors = {
                'bedrooms': ['.quartos', '.bedrooms', '[data-testid*="bedroom"]'],
                'bathrooms': ['.banheiros', '.bathrooms', '[data-testid*="bathroom"]']
            }
            
            for field, selectors in room_selectors.items():
                for selector in selectors:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        number = self._extract_number_from_text(text)
                        if number and 0 <= number <= 20:
                            extracted_data[field] = number
                            break
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"❌ Erro no scraping genérico: {e}")
            return {}
    
    async def _analyze_property_images(self, url: str) -> Dict[str, Any]:
        """Analisa imagens da propriedade usando OCR"""
        if not WEB_SCRAPING_AVAILABLE or not webdriver or not By or not requests:
            return {'success': False, 'error': 'Selenium ou requests não disponível'}
        
        driver = None
        try:
            # Configurar driver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Aguardar carregamento
            await asyncio.sleep(3)
            
            # Encontrar imagens
            image_elements = driver.find_elements(By.TAG_NAME, 'img')
            
            # Filtrar e baixar imagens relevantes
            relevant_images = []
            downloaded_count = 0
            
            for img in image_elements[:self.max_images_per_property]:
                try:
                    src = img.get_attribute('src')
                    if not src or 'data:image' in src:
                        continue
                    
                    # Converter para URL absoluta
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(url, src)
                    
                    # Baixar imagem
                    img_response = requests.get(src, timeout=5)
                    if img_response.status_code == 200:
                        relevant_images.append(img_response.content)
                        downloaded_count += 1
                        self.stats['image_downloads'] += 1
                    
                except Exception as e:
                    self.logger.debug(f"Erro ao baixar imagem: {e}")
                    continue
            
            return {
                'success': len(relevant_images) > 0,
                'images': relevant_images,
                'total_downloaded': downloaded_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise de imagens: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            if driver:
                driver.quit()
    
    def _detect_source(self, url: str) -> str:
        """Detecta a fonte com base na URL"""
        url_lower = url.lower()
        
        if 'vivareal.com' in url_lower:
            return 'vivareal'
        elif 'olx.com' in url_lower:
            return 'olx'
        elif 'zapimoveis.com' in url_lower:
            return 'zapimoveis'
        else:
            return 'generic'
    
    def _needs_image_analysis(self, data: Dict[str, Any]) -> bool:
        """Verifica se análise de imagem é necessária"""
        # Campos críticos que se beneficiam de OCR
        critical_fields = ['price', 'area', 'bedrooms', 'bathrooms']
        
        missing_fields = sum(1 for field in critical_fields if not data.get(field))
        
        # Se mais de 1 campo crítico está faltando, usar OCR
        return missing_fields > 1
    
    def _ocr_improved_data(self, original_data: Dict[str, Any], 
                          enhanced_data: Dict[str, Any]) -> bool:
        """Verifica se OCR melhorou os dados"""
        original_fields = sum(1 for v in original_data.values() if v)
        enhanced_fields = sum(1 for v in enhanced_data.values() if v)
        
        return enhanced_fields > original_fields
    
    def _clean_and_validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Limpa e valida dados finais"""
        cleaned_data = {}
        
        # Validar e limpar cada campo
        if data.get('price'):
            try:
                price = float(data['price'])
                if 10000 <= price <= 50000000:
                    cleaned_data['price'] = price
            except (ValueError, TypeError):
                pass
        
        if data.get('area'):
            try:
                area = float(data['area'])
                if 10 <= area <= 10000:
                    cleaned_data['area'] = area
            except (ValueError, TypeError):
                pass
        
        for field in ['bedrooms', 'bathrooms', 'parking']:
            if data.get(field):
                try:
                    value = int(data[field])
                    if 0 <= value <= 20:
                        cleaned_data[field] = value
                except (ValueError, TypeError):
                    pass
        
        # Campos de texto
        for field in ['address', 'neighborhood', 'city', 'state', 'property_type']:
            if data.get(field):
                cleaned_data[field] = str(data[field]).strip()
        
        return cleaned_data
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extrai preço de texto"""
        import re
        
        # Padrões de preço
        patterns = [
            r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*reais?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    price_str = match.group(1)
                    # Converter para float
                    if ',' in price_str and '.' in price_str:
                        price_str = price_str.replace('.', '').replace(',', '.')
                    elif ',' in price_str:
                        if len(price_str.split(',')[1]) <= 2:
                            price_str = price_str.replace(',', '.')
                        else:
                            price_str = price_str.replace(',', '')
                    
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_area_from_text(self, text: str) -> Optional[float]:
        """Extrai área de texto"""
        import re
        
        pattern = r'(\d{1,4}(?:,\d{1,2})?)\s*m[²2]?'
        match = re.search(pattern, text)
        
        if match:
            try:
                area_str = match.group(1).replace(',', '.')
                return float(area_str)
            except ValueError:
                pass
        
        return None
    
    def _extract_number_from_text(self, text: str) -> Optional[int]:
        """Extrai número de texto"""
        import re
        
        match = re.search(r'(\d{1,2})', text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _log_scraping_result(self, result: Dict[str, Any]):
        """Log detalhado do resultado"""
        data = result['data']
        fields_count = len([v for v in data.values() if v])
        
        if result['success']:
            methods = ', '.join(result['extraction_methods'])
            self.logger.info(
                f"✅ Scraping bem-sucedido: {fields_count} campos extraídos "
                f"({methods}, {result['images_analyzed']} imagens analisadas, "
                f"{result['processing_time']:.2f}s)"
            )
        else:
            self.logger.warning(
                f"⚠️ Scraping parcial: {fields_count} campos extraídos "
                f"({result['processing_time']:.2f}s)"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas"""
        base_stats = self.stats.copy()
        
        # Calcular taxas
        if base_stats['total_properties_scraped'] > 0:
            base_stats['ocr_enhancement_rate'] = float(
                base_stats['ocr_enhanced_extractions'] / 
                base_stats['total_properties_scraped']
            )
            base_stats['ocr_success_rate'] = float(
                base_stats['ocr_fallback_successes'] / 
                max(1, base_stats['ocr_enhanced_extractions'])
            )
        
        # Estatísticas do smart extractor
        if self.smart_extractor:
            try:
                base_stats['smart_extractor_stats'] = self.smart_extractor.get_statistics()
            except Exception as e:
                self.logger.warning(f"Erro ao obter estatísticas do smart extractor: {e}")
        
        return base_stats
    
    async def batch_scrape_enhanced(self, urls: List[str], 
                                  max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Scraping em lote com análise de imagens"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single(url):
            async with semaphore:
                return await self.scrape_property_enhanced(url)
        
        tasks = [scrape_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'url': urls[i],
                    'success': False,
                    'error': str(result),
                    'index': i
                })
            else:
                # result é um Dict[str, Any], podemos adicionar o index
                if isinstance(result, dict):
                    result['index'] = i
                processed_results.append(result)
        
        return processed_results
    
    async def close(self):
        """Fecha todos os serviços"""
        if self.smart_extractor:
            try:
                await self.smart_extractor.close()
            except Exception as e:
                self.logger.warning(f"Erro ao fechar smart extractor: {e}")


# Exemplo de uso
async def main():
    """Exemplo de uso do Enhanced Scraper"""
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    scraper = EnhancedScraper(use_ocr=False, max_images_per_property=1)
    await scraper.initialize()
    
    # URLs de exemplo
    test_urls = [
        "https://www.vivareal.com.br/imovel/apartamento-3-quartos-...",
        "https://www.olx.com.br/imoveis/apartamento-...",
    ]
    
    try:
        # Teste básico sem URLs reais
        print("✅ Enhanced Scraper inicializado com sucesso")
        
        # Testar estatísticas
        stats = scraper.get_statistics()
        print(f"✅ Estatísticas obtidas: {list(stats.keys())}")
        
        # Testar detecção de fonte
        source = scraper._detect_source("https://www.vivareal.com.br/teste")
        print(f"✅ Detecção de fonte: {source}")
        
        print("✅ Todos os testes básicos passaram!")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
