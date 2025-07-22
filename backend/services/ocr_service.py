# backend/services/ocr_service.py
"""
Serviço de OCR para Análise de Imagens de Anúncios de Imóveis
Extrai dados como preço, área, quartos e banheiros de imagens quando dados estruturados não estão disponíveis.
"""
import asyncio
import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import base64
import io
from pathlib import Path

# OCR Libraries with robust fallbacks
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    Image = None
    ImageEnhance = None
    ImageFilter = None
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    easyocr = None
    EASYOCR_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None
    OPENCV_AVAILABLE = False

# Type hints fallback - create comprehensive dummy classes
if not TESSERACT_AVAILABLE:
    # Create comprehensive dummy classes for type hints and graceful degradation
    class DummyImage:
        """Dummy Image class for when PIL is not available"""
        def __init__(self, *args, **kwargs):
            self.mode = 'RGB'
            self.size = (100, 100)
        
        def convert(self, mode):
            return DummyImage()
        
        def resize(self, size):
            return DummyImage()
        
        def filter(self, filter_type):
            return DummyImage()
        
        def save(self, fp, format=None):
            pass
        
        def __array__(self):
            if np:
                return np.zeros((100, 100, 3), dtype=np.uint8)
            return []
    
    class DummyImageEnhance:
        """Dummy ImageEnhance class"""
        def __init__(self, image):
            self.image = image
        
        def enhance(self, factor):
            return DummyImage()
        
        @staticmethod
        def Contrast(image):
            return DummyImageEnhance(image)
    
    class DummyImageFilter:
        """Dummy ImageFilter class"""
        SHARPEN = "sharpen"
    
    class DummyImageDraw:
        """Dummy ImageDraw class"""
        def __init__(self, image):
            pass
        
        def text(self, position, text, fill=None):
            pass
        
        @staticmethod
        def Draw(image):
            return DummyImageDraw(image)
    
    class DummyImageModule:
        """Dummy PIL Image module"""
        Image = DummyImage
        
        @staticmethod
        def open(*args, **kwargs):
            return DummyImage()
        
        @staticmethod
        def fromarray(*args, **kwargs):
            return DummyImage()
        
        @staticmethod
        def new(mode, size, color=None):
            return DummyImage()
    
    # Override the None values with dummy classes
    Image = DummyImageModule()
    ImageEnhance = DummyImageEnhance
    ImageFilter = DummyImageFilter

class OCRService:
    """Serviço de OCR para extração de dados de imagens de anúncios"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurações de OCR
        self.ocr_engines = {
            'tesseract': TESSERACT_AVAILABLE,
            'easyocr': EASYOCR_AVAILABLE
        }
        
        # Inicializar EasyOCR se disponível
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE and easyocr:
            try:
                self.easyocr_reader = easyocr.Reader(['pt', 'en'], gpu=False)
                self.logger.info("✅ EasyOCR inicializado")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao inicializar EasyOCR: {e}")
                self.ocr_engines['easyocr'] = False
        
        # Padrões regex para extração de dados
        self.patterns = {
            'price': [
                r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # R$ 850.000,00
                r'R\$?\s*(\d{1,3}(?:\.\d{3})*)',  # R$ 1.200.000
                r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*reais?',  # 850.000,00 reais
                r'Preço:?\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # Preço: R$ 850.000
                r'Valor:?\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # Valor: 850.000
                r'(\d{1,3}(?:\.\d{3})*)\s*mil',  # 850 mil
                r'(\d{3,})',  # Fallback para números grandes
            ],
            'area': [
                r'(\d{1,4}(?:,\d{1,2})?)\s*m[²2]',  # 120 m² ou 120,5 m2
                r'(\d{1,4}(?:,\d{1,2})?)\s*metros?[\s\-]?quadrados?',  # 120 metros quadrados
                r'Área:?\s*(\d{1,4}(?:,\d{1,2})?)\s*m[²2]?',  # Área: 120 m²
                r'(\d{1,4}(?:,\d{1,2})?)\s*m[²2]\s*(?:útil|total|privativa)?',  # 120 m² útil
            ],
            'bedrooms': [
                r'(\d{1,2})\s*(?:quartos?|dorms?|suítes?)',  # 3 quartos
                r'(\d{1,2})\s*qto?s?',  # 3 qtos
                r'Quartos?:?\s*(\d{1,2})',  # Quartos: 3
                r'(\d{1,2})\s*(?:bedroom|bed)',  # 3 bedroom
            ],
            'bathrooms': [
                r'(\d{1,2})\s*(?:banheiros?|wcs?)',  # 2 banheiros
                r'(\d{1,2})\s*banh?s?',  # 2 banhs
                r'Banheiros?:?\s*(\d{1,2})',  # Banheiros: 2
                r'(\d{1,2})\s*(?:bathroom|bath)',  # 2 bathroom
            ],
            'parking': [
                r'(\d{1,2})\s*(?:vagas?|garagens?)',  # 2 vagas
                r'(\d{1,2})\s*vg?s?',  # 2 vgs
                r'Vagas?:?\s*(\d{1,2})',  # Vagas: 2
                r'(\d{1,2})\s*(?:parking|garage)',  # 2 parking
            ]
        }
        
        # Cache de resultados
        self.cache = {}
        
    def check_availability(self) -> Dict[str, bool]:
        """Verifica disponibilidade das engines de OCR"""
        return {
            'tesseract': TESSERACT_AVAILABLE,
            'easyocr': EASYOCR_AVAILABLE,
            'opencv': OPENCV_AVAILABLE,
            'overall': any(self.ocr_engines.values())
        }
    
    def preprocess_image(self, image) -> List:
        """Pré-processa imagem para melhorar OCR"""
        processed_images = []
        
        try:
            if not TESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
                return [image]
            
            # Imagem original
            processed_images.append(image)
            
            # Converter para escala de cinza se PIL disponível
            if TESSERACT_AVAILABLE and hasattr(image, 'mode') and image.mode != 'L':
                gray_image = image.convert('L')
                processed_images.append(gray_image)
            
            # Aumentar contraste se PIL disponível
            if TESSERACT_AVAILABLE and ImageEnhance:
                enhancer = ImageEnhance.Contrast(image)
                high_contrast = enhancer.enhance(2.0)
                processed_images.append(high_contrast)
                
                # Aplicar filtro de nitidez
                if ImageFilter:
                    sharp_image = image.filter(ImageFilter.SHARPEN)
                    processed_images.append(sharp_image)
            
            # Se OpenCV disponível, aplicar processamentos avançados
            if OPENCV_AVAILABLE:
                processed_images.extend(self._opencv_preprocessing(image))
            
            return processed_images
            
        except Exception as e:
            self.logger.error(f"❌ Erro no pré-processamento: {e}")
            return [image]  # Retorna pelo menos a imagem original
    
    def _opencv_preprocessing(self, image: Any) -> List[Any]:
        """Pré-processamento avançado com OpenCV"""
        processed = []
        
        try:
            if not OPENCV_AVAILABLE or not cv2 or not np:
                return []
                
            # Converter PIL para OpenCV
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Binarização adaptativa
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            if TESSERACT_AVAILABLE and Image and hasattr(Image, 'fromarray'):
                processed.append(Image.fromarray(adaptive_thresh))
            
            # Denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            if TESSERACT_AVAILABLE and Image and hasattr(Image, 'fromarray'):
                processed.append(Image.fromarray(denoised))
            
            # Morphological operations
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            if TESSERACT_AVAILABLE and Image and hasattr(Image, 'fromarray'):
                processed.append(Image.fromarray(opening))
            
            return processed
            
        except Exception as e:
            self.logger.debug(f"Erro no processamento OpenCV: {e}")
            return []
    
    async def extract_text_tesseract(self, image: Any) -> str:
        """Extrai texto usando Tesseract OCR"""
        if not TESSERACT_AVAILABLE or not pytesseract:
            raise Exception("Tesseract não está disponível")
        
        try:
            # Configurações do Tesseract para português
            custom_config = r'--oem 3 --psm 6 -l por'
            
            # Extrair texto
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Erro no Tesseract OCR: {e}")
            return ""
    
    async def extract_text_easyocr(self, image: Any) -> str:
        """Extrai texto usando EasyOCR"""
        if not self.easyocr_reader:
            raise Exception("EasyOCR não está disponível")
        
        try:
            # Converter PIL para numpy array
            if not np:
                raise Exception("NumPy não está disponível")
                
            image_array = np.array(image)
            
            # Executar OCR
            results = self.easyocr_reader.readtext(image_array)
            
            # Combinar textos extraídos
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filtrar por confiança
                    extracted_texts.append(text)
            
            return ' '.join(extracted_texts)
            
        except Exception as e:
            self.logger.error(f"❌ Erro no EasyOCR: {e}")
            return ""
    
    def extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto usando regex"""
        extracted_data = {
            'price': None,
            'area': None,
            'bedrooms': None,
            'bathrooms': None,
            'parking': None,
            'raw_text': text,
            'confidence': 0.0
        }
        
        confidence_scores = []
        
        # Normalizar texto
        normalized_text = text.lower().replace('\n', ' ').replace('\t', ' ')
        
        # Extrair cada tipo de dado
        for data_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, normalized_text, re.IGNORECASE)
                if matches:
                    try:
                        # Pegar a primeira correspondência válida
                        value = matches[0]
                        
                        if data_type == 'price':
                            # Processar preço
                            price_value = self._parse_price(value)
                            if price_value and price_value > 10000:  # Filtro mínimo
                                extracted_data['price'] = price_value
                                confidence_scores.append(0.9)
                                break
                        
                        elif data_type == 'area':
                            # Processar área
                            area_value = self._parse_area(value)
                            if area_value and 10 <= area_value <= 10000:  # Faixa válida
                                extracted_data['area'] = area_value
                                confidence_scores.append(0.8)
                                break
                        
                        elif data_type in ['bedrooms', 'bathrooms', 'parking']:
                            # Processar números inteiros
                            int_value = int(value)
                            if 0 <= int_value <= 20:  # Faixa válida
                                extracted_data[data_type] = int_value
                                confidence_scores.append(0.7)
                                break
                    
                    except (ValueError, TypeError):
                        continue
        
        # Calcular confiança geral
        if confidence_scores:
            extracted_data['confidence'] = sum(confidence_scores) / len(confidence_scores)
        
        return extracted_data
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Converte string de preço para float"""
        try:
            # Normalizar string
            price_str = price_str.strip()
            
            # Lidar com formato "mil"
            if 'mil' in price_str.lower():
                # Extrair número antes de "mil"
                match = re.search(r'(\d+(?:[.,]\d+)?)', price_str)
                if match:
                    base_value = float(match.group(1).replace(',', '.'))
                    return base_value * 1000
            
            # Remover símbolos mantendo apenas dígitos, pontos e vírgulas
            clean_str = re.sub(r'[^\d.,]', '', price_str)
            
            if not clean_str:
                return None
            
            # Processar diferentes formatos
            if '.' in clean_str and ',' in clean_str:
                # Formato brasileiro: 1.200.000,00
                clean_price = clean_str.replace('.', '').replace(',', '.')
            elif '.' in clean_str:
                # Verificar se é separador de milhares ou decimal
                parts = clean_str.split('.')
                if len(parts) > 2:
                    # Múltiplos pontos = separador de milhares
                    clean_price = clean_str.replace('.', '')
                elif len(parts) == 2 and len(parts[1]) <= 2 and len(parts[0]) <= 3:
                    # Decimal: 850.50
                    clean_price = clean_str
                else:
                    # Separador de milhares: 1.200 ou 1000.000
                    clean_price = clean_str.replace('.', '')
            elif ',' in clean_str:
                # Vírgula decimal ou separador
                parts = clean_str.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Decimal: 850,50
                    clean_price = clean_str.replace(',', '.')
                else:
                    # Separador: 1,200,000
                    clean_price = clean_str.replace(',', '')
            else:
                # Apenas dígitos
                clean_price = clean_str
            
            return float(clean_price)
        
        except (ValueError, AttributeError):
            return None
    
    def _parse_area(self, area_str: str) -> Optional[float]:
        """Converte string de área para float"""
        try:
            # Remover símbolos e manter apenas números e vírgula
            clean_area = re.sub(r'[^\d,.]', '', area_str)
            
            # Converter vírgula para ponto decimal
            if ',' in clean_area:
                clean_area = clean_area.replace(',', '.')
            
            return float(clean_area)
        
        except (ValueError, AttributeError):
            return None
    
    async def analyze_image(self, image_input: Union[str, bytes, Any], 
                          use_fallback: bool = True) -> Dict[str, Any]:
        """
        Analisa imagem e extrai dados de imóvel
        
        Args:
            image_input: Caminho do arquivo, bytes da imagem ou objeto PIL Image
            use_fallback: Se deve usar OCR como fallback
        
        Returns:
            Dict com dados extraídos
        """
        start_time = datetime.now()
        
        try:
            # Carregar imagem
            if isinstance(image_input, str):
                if not Image or not hasattr(Image, 'open'):
                    raise ValueError("PIL não está disponível para carregar imagem")
                image = Image.open(image_input)
            elif isinstance(image_input, bytes):
                if not Image or not hasattr(Image, 'open'):
                    raise ValueError("PIL não está disponível para carregar imagem")
                image = Image.open(io.BytesIO(image_input))
            elif TESSERACT_AVAILABLE and Image and hasattr(image_input, 'mode'):
                image = image_input
            else:
                raise ValueError("Tipo de imagem não suportado ou PIL não disponível")
            
            # Verificar cache
            image_hash = self._generate_image_hash(image)
            if image_hash in self.cache:
                self.logger.info("🟢 Cache hit para análise de imagem")
                return self.cache[image_hash]
            
            # Pré-processar imagem
            processed_images = self.preprocess_image(image)
            
            best_result = {
                'success': False,
                'data': {},
                'confidence': 0.0,
                'processing_time': 0.0,
                'ocr_engine': None,
                'error': None
            }
            
            # Tentar diferentes engines de OCR
            for engine in ['easyocr', 'tesseract']:
                if not self.ocr_engines.get(engine, False):
                    continue
                
                try:
                    # Tentar cada imagem processada
                    for proc_image in processed_images:
                        
                        # Extrair texto
                        if engine == 'easyocr':
                            extracted_text = await self.extract_text_easyocr(proc_image)
                        else:
                            extracted_text = await self.extract_text_tesseract(proc_image)
                        
                        if not extracted_text.strip():
                            continue
                        
                        # Extrair dados estruturados
                        extracted_data = self.extract_data_from_text(extracted_text)
                        
                        # Verificar se é melhor resultado
                        if extracted_data['confidence'] > best_result['confidence']:
                            best_result = {
                                'success': True,
                                'data': extracted_data,
                                'confidence': extracted_data['confidence'],
                                'ocr_engine': engine,
                                'processing_time': (datetime.now() - start_time).total_seconds(),
                                'error': None
                            }
                        
                        # Se confiança alta, parar
                        if extracted_data['confidence'] > 0.8:
                            break
                    
                    # Se resultado bom encontrado, parar
                    if best_result['confidence'] > 0.7:
                        break
                
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro com engine {engine}: {e}")
                    continue
            
            # Finalizar resultado
            if not best_result['success']:
                best_result['error'] = 'Nenhum dado estruturado extraído'
                best_result['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Cache do resultado
            self.cache[image_hash] = best_result
            
            # Log do resultado
            if best_result['success']:
                data = best_result['data']
                found_fields = [k for k, v in data.items() if v is not None and k != 'raw_text']
                self.logger.info(f"✅ OCR extraiu: {found_fields} (confiança: {best_result['confidence']:.2f})")
            else:
                self.logger.warning(f"⚠️ OCR falhou: {best_result['error']}")
            
            return best_result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise de imagem: {e}")
            return {
                'success': False,
                'data': {},
                'confidence': 0.0,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'ocr_engine': None,
                'error': str(e)
            }
    
    def _generate_image_hash(self, image: Any) -> str:
        """Gera hash para cache da imagem"""
        try:
            if not TESSERACT_AVAILABLE or not Image or not hasattr(image, 'resize'):
                return f"img_{datetime.now().timestamp()}"
                
            # Redimensionar para hash consistente
            thumb = image.resize((64, 64))
            
            # Converter para bytes
            img_bytes = io.BytesIO()
            thumb.save(img_bytes, format='PNG')
            
            # Gerar hash
            import hashlib
            return hashlib.md5(img_bytes.getvalue()).hexdigest()
        
        except Exception:
            return f"img_{datetime.now().timestamp()}"
    
    async def batch_analyze(self, image_list: List[Union[str, bytes]], 
                          max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Analisa múltiplas imagens em paralelo"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_single(image_input):
            async with semaphore:
                return await self.analyze_image(image_input)
        
        tasks = [analyze_single(img) for img in image_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'image_index': i
                })
            else:
                # result é um Dict[str, Any], podemos adicionar o index
                if isinstance(result, dict):
                    result['image_index'] = i
                processed_results.append(result)
        
        return processed_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do serviço OCR"""
        total_cached = len(self.cache)
        successful = sum(1 for result in self.cache.values() if result['success'])
        
        confidence_scores = [r['confidence'] for r in self.cache.values() if r['success']]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        engines_used = {}
        for result in self.cache.values():
            if result['ocr_engine']:
                engines_used[result['ocr_engine']] = engines_used.get(result['ocr_engine'], 0) + 1
        
        return {
            'total_processed': total_cached,
            'success_rate': successful / total_cached if total_cached > 0 else 0,
            'average_confidence': avg_confidence,
            'engines_used': engines_used,
            'available_engines': self.check_availability()
        }
    
    def clear_cache(self):
        """Limpa cache de resultados"""
        self.cache.clear()
        self.logger.info("🧹 Cache de OCR limpo")


# Exemplo de uso
async def main():
    """Exemplo de uso do OCR Service"""
    ocr_service = OCRService()
    
    # Verificar disponibilidade
    availability = ocr_service.check_availability()
    print(f"Disponibilidade OCR: {availability}")
    
    if not availability['overall']:
        print("❌ Nenhuma engine de OCR disponível")
        return
    
    # Exemplo com imagem fictícia (seria uma imagem real de anúncio)
    try:
        # Verificar se PIL está disponível para o exemplo
        if not TESSERACT_AVAILABLE:
            print("⚠️ PIL não disponível, pulando exemplo de imagem")
            return
            
        # Criar imagem de exemplo com texto
        if not TESSERACT_AVAILABLE:
            print("⚠️ PIL não disponível, pulando exemplo de imagem")
            return
            
        try:
            from PIL import Image as PILImage, ImageDraw, ImageFont  # type: ignore
            
            # Criar imagem de exemplo
            img = PILImage.new('RGB', (400, 300), color='white')
            draw = ImageDraw.Draw(img)
        except ImportError:
            print("⚠️ PIL não disponível para exemplo")
            return
        
        # Adicionar texto de exemplo
        sample_text = [
            "APARTAMENTO 3 QUARTOS",
            "R$ 850.000,00",
            "120 m² área útil",
            "2 banheiros",
            "1 vaga de garagem"
        ]
        
        y_pos = 50
        for text in sample_text:
            draw.text((50, y_pos), text, fill='black')
            y_pos += 40
        
        # Analisar imagem
        result = await ocr_service.analyze_image(img)
        print(f"Resultado OCR: {result}")
        
        # Estatísticas
        stats = ocr_service.get_statistics()
        print(f"Estatísticas: {stats}")
        
    except Exception as e:
        print(f"Erro no exemplo: {e}")

if __name__ == "__main__":
    asyncio.run(main())
