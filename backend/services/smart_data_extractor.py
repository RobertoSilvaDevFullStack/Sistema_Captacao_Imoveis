# backend/services/smart_data_extractor.py
"""
Extrator Inteligente de Dados com OCR como Fallback
Combina extração estruturada de dados com OCR para máxima precisão na captura de informações de imóveis.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import re
from pathlib import Path

# Importar serviços existentes com fallbacks
OCRService = None
CacheService = None
DatabaseService = None

try:
    from .ocr_service import OCRService as _OCRService
    OCRService = _OCRService
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from .cache_service import CacheService as _CacheService
    CacheService = _CacheService
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from .database_service import DatabaseService as _DatabaseService
    DatabaseService = _DatabaseService
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

class SmartDataExtractor:
    """
    Extrator inteligente que combina múltiplas estratégias:
    1. Extração estruturada de HTML/JSON (preferencial)
    2. OCR de imagens como fallback
    3. Cache para otimização
    4. Validação cruzada de dados
    """
    
    def __init__(self, use_cache: bool = True, use_ocr: bool = True):
        self.logger = logging.getLogger(__name__)
        
        # Inicializar serviços com verificação de disponibilidade
        self.ocr_service = None
        self.cache_service = None
        self.db_service = None
        
        if OCR_AVAILABLE and use_ocr and OCRService:
            try:
                self.ocr_service = OCRService()
            except Exception as e:
                self.logger.warning(f"Falha ao inicializar OCR service: {e}")
        
        if CACHE_AVAILABLE and use_cache and CacheService:
            try:
                self.cache_service = CacheService()
            except Exception as e:
                self.logger.warning(f"Falha ao inicializar Cache service: {e}")
        
        if DB_AVAILABLE and DatabaseService:
            try:
                self.db_service = DatabaseService()
            except Exception as e:
                self.logger.warning(f"Falha ao inicializar Database service: {e}")
        
        # Configurações
        self.use_ocr_fallback = use_ocr and OCR_AVAILABLE and self.ocr_service is not None
        self.use_cache = use_cache and CACHE_AVAILABLE and self.cache_service is not None
        
        # Padrões para validação de dados
        self.validation_patterns = {
            'price': {
                'min': 10000,      # R$ 10.000 mínimo
                'max': 50000000,   # R$ 50 milhões máximo
                'pattern': r'^\d+(\.\d{3})*(\,\d{2})?$'
            },
            'area': {
                'min': 10,         # 10 m² mínimo
                'max': 10000,      # 10.000 m² máximo
                'pattern': r'^\d+(\,\d{1,2})?$'
            },
            'bedrooms': {
                'min': 0,
                'max': 20,
                'pattern': r'^\d{1,2}$'
            },
            'bathrooms': {
                'min': 0,
                'max': 20,
                'pattern': r'^\d{1,2}$'
            }
        }
        
        # Estatísticas
        self.stats: Dict[str, Any] = {
            'total_extractions': 0,
            'structured_success': 0,
            'ocr_fallback_used': 0,
            'ocr_fallback_success': 0,
            'cache_hits': 0,
            'validation_failures': 0
        }
    
    async def initialize(self):
        """Inicializa todos os serviços"""
        try:
            if self.cache_service and hasattr(self.cache_service, 'initialize'):
                await self.cache_service.initialize()  # type: ignore
                self.logger.info("✅ Cache service inicializado")
            
            if self.db_service and hasattr(self.db_service, 'initialize'):
                await self.db_service.initialize()  # type: ignore
                self.logger.info("✅ Database service inicializado")
            
            self.logger.info("✅ SmartDataExtractor inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    async def extract_property_data(self, 
                                  structured_data: Optional[Dict[str, Any]] = None,
                                  html_content: Optional[str] = None,
                                  images: Optional[List[Union[str, bytes]]] = None,
                                  url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrai dados de propriedade usando múltiplas estratégias
        
        Args:
            structured_data: Dados já estruturados (JSON, etc.)
            html_content: Conteúdo HTML para parsing
            images: Lista de imagens para OCR
            url: URL para identificação e cache
        
        Returns:
            Dict com dados extraídos e metadados
        """
        start_time = datetime.now()
        extraction_id = f"ext_{int(start_time.timestamp())}"
        
        self.stats['total_extractions'] += 1
        
        try:
            # Verificar cache primeiro
            cache_key = self._generate_cache_key(structured_data, html_content, url)
            if self.use_cache and cache_key:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    self.stats['cache_hits'] += 1
                    self.logger.info(f"🟢 Cache hit para extração: {extraction_id}")
                    return cached_result
            
            # Resultado combinado
            final_result = {
                'extraction_id': extraction_id,
                'timestamp': start_time.isoformat(),
                'data': {
                    'price': None,
                    'area': None,
                    'bedrooms': None,
                    'bathrooms': None,
                    'parking': None,
                    'address': None,
                    'neighborhood': None,
                    'city': None,
                    'state': None,
                    'property_type': None,
                    'business_type': None
                },
                'sources': [],
                'confidence_scores': {},
                'overall_confidence': 0.0,
                'processing_time': 0.0,
                'success': False,
                'errors': []
            }
            
            # 1. Tentar extração estruturada primeiro
            if structured_data or html_content:
                structured_result = await self._extract_structured_data(
                    structured_data, html_content
                )
                
                if structured_result['success']:
                    final_result = self._merge_results(final_result, structured_result, 'structured')
                    self.stats['structured_success'] += 1
                    self.logger.info(f"✅ Extração estruturada bem-sucedida: {extraction_id}")
            
            # 2. Se dados incompletos e OCR disponível, usar OCR como fallback
            if self._needs_ocr_fallback(final_result) and images and self.use_ocr_fallback:
                self.stats['ocr_fallback_used'] += 1
                
                ocr_result = await self._extract_ocr_data(images)
                
                if ocr_result['success']:
                    final_result = self._merge_results(final_result, ocr_result, 'ocr')
                    self.stats['ocr_fallback_success'] += 1
                    self.logger.info(f"✅ OCR fallback bem-sucedido: {extraction_id}")
            
            # 3. Validar dados extraídos
            validation_result = self._validate_extracted_data(final_result['data'])
            final_result['validation'] = validation_result
            
            if not validation_result['is_valid']:
                self.stats['validation_failures'] += 1
                final_result['errors'].extend(validation_result['errors'])
            
            # 4. Calcular confiança geral
            final_result['overall_confidence'] = self._calculate_overall_confidence(final_result)
            final_result['success'] = final_result['overall_confidence'] > 0.3
            
            # 5. Tempo de processamento
            final_result['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # 6. Cache do resultado se bem-sucedido
            if final_result['success'] and self.use_cache and cache_key:
                await self._save_to_cache(cache_key, final_result)
            
            # 7. Log do resultado
            self._log_extraction_result(final_result)
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração: {e}")
            return {
                'extraction_id': extraction_id,
                'success': False,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    async def _extract_structured_data(self, 
                                     structured_data: Optional[Dict[str, Any]],
                                     html_content: Optional[str]) -> Dict[str, Any]:
        """Extrai dados de fontes estruturadas"""
        result = {
            'success': False,
            'data': {},
            'confidence_scores': {},
            'source': 'structured'
        }
        
        try:
            # Se dados JSON estruturados estão disponíveis
            if structured_data:
                extracted = self._parse_structured_json(structured_data)
                result['data'].update(extracted)
                result['confidence_scores'].update({k: 0.9 for k in extracted.keys() if extracted[k]})
            
            # Se HTML disponível, fazer parsing
            if html_content:
                html_extracted = await self._parse_html_content(html_content)
                result['data'].update(html_extracted)
                result['confidence_scores'].update({k: 0.8 for k in html_extracted.keys() if html_extracted[k]})
            
            # Verificar se algo foi extraído
            extracted_fields = [k for k, v in result['data'].items() if v is not None]
            result['success'] = len(extracted_fields) > 0
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração estruturada: {e}")
            result['error'] = str(e)
            return result
    
    def _parse_structured_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse de dados JSON estruturados"""
        extracted = {}
        
        # Mapeamentos comuns de campos
        field_mappings = {
            'price': ['price', 'valor', 'preco', 'amount', 'cost'],
            'area': ['area', 'size', 'meters', 'sqm', 'area_util', 'area_total'],
            'bedrooms': ['bedrooms', 'quartos', 'rooms', 'bed', 'dormitorios'],
            'bathrooms': ['bathrooms', 'banheiros', 'bath', 'wc'],
            'parking': ['parking', 'vagas', 'garage', 'garagem'],
            'address': ['address', 'endereco', 'location', 'street'],
            'neighborhood': ['neighborhood', 'bairro', 'district'],
            'city': ['city', 'cidade', 'municipio'],
            'state': ['state', 'estado', 'uf'],
            'property_type': ['property_type', 'tipo', 'type', 'category'],
            'business_type': ['business_type', 'negocio', 'transaction']
        }
        
        # Buscar valores usando mapeamentos
        for field, possible_keys in field_mappings.items():
            for key in possible_keys:
                value = self._deep_get(data, key)
                if value is not None:
                    # Limpar e converter valor
                    cleaned_value = self._clean_field_value(field, value)
                    if cleaned_value is not None:
                        extracted[field] = cleaned_value
                        break
        
        return extracted
    
    def _deep_get(self, data: Dict[str, Any], key: str) -> Any:
        """Busca profunda por chave em dicionário aninhado"""
        def _search(obj, target_key):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k.lower() == target_key.lower():
                        return v
                    elif isinstance(v, (dict, list)):
                        result = _search(v, target_key)
                        if result is not None:
                            return result
            elif isinstance(obj, list):
                for item in obj:
                    result = _search(item, target_key)
                    if result is not None:
                        return result
            return None
        
        return _search(data, key)
    
    async def _parse_html_content(self, html_content: str) -> Dict[str, Any]:
        """Parse de conteúdo HTML"""
        extracted = {}
        
        try:
            # Usar regex para extrair dados comuns
            # Preço
            price_patterns = [
                r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
                r'(?:preço|valor|price)[:=]\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    price_str = match.group(1)
                    price_value = self._parse_price_string(price_str)
                    if price_value:
                        extracted['price'] = price_value
                        break
            
            # Área
            area_patterns = [
                r'(\d{1,4}(?:,\d{1,2})?)\s*m[²2]',
                r'(?:área|area|size)[:=]\s*(\d{1,4}(?:,\d{1,2})?)',
            ]
            
            for pattern in area_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    area_str = match.group(1)
                    area_value = self._parse_area_string(area_str)
                    if area_value:
                        extracted['area'] = area_value
                        break
            
            # Quartos e banheiros
            room_patterns = {
                'bedrooms': [r'(\d{1,2})\s*(?:quartos?|rooms?|bed)', r'(?:quartos?|rooms?)[:=]\s*(\d{1,2})'],
                'bathrooms': [r'(\d{1,2})\s*(?:banheiros?|bath)', r'(?:banheiros?|bath)[:=]\s*(\d{1,2})']
            }
            
            for field, patterns in room_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, html_content, re.IGNORECASE)
                    if match:
                        value = int(match.group(1))
                        if 0 <= value <= 20:
                            extracted[field] = value
                            break
            
            return extracted
            
        except Exception as e:
            self.logger.error(f"❌ Erro no parse HTML: {e}")
            return {}
    
    async def _extract_ocr_data(self, images: List[Union[str, bytes]]) -> Dict[str, Any]:
        """Extrai dados usando OCR"""
        if not self.ocr_service:
            return {'success': False, 'error': 'OCR service não disponível'}
        
        try:
            # Verificar se o método existe
            if not hasattr(self.ocr_service, 'batch_analyze'):
                return {'success': False, 'error': 'Método batch_analyze não disponível'}
            
            # Analisar todas as imagens
            ocr_results = await self.ocr_service.batch_analyze(images, max_concurrent=2)  # type: ignore
            
            # Combinar resultados
            combined_data = {}
            confidence_scores = {}
            
            for result in ocr_results:
                if result.get('success'):
                    data = result.get('data', {})
                    confidence = result.get('confidence', 0.0)
                    
                    # Mesclar dados com base na confiança
                    for field, value in data.items():
                        if value is not None and field != 'raw_text':
                            current_confidence = confidence_scores.get(field, 0)
                            if confidence > current_confidence:
                                combined_data[field] = value
                                confidence_scores[field] = confidence
            
            return {
                'success': len(combined_data) > 0,
                'data': combined_data,
                'confidence_scores': confidence_scores,
                'source': 'ocr'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na extração OCR: {e}")
            return {'success': False, 'error': str(e)}
    
    def _needs_ocr_fallback(self, current_result: Dict[str, Any]) -> bool:
        """Verifica se OCR é necessário como fallback"""
        data = current_result['data']
        
        # Campos críticos que justificam OCR se não encontrados
        critical_fields = ['price', 'area']
        missing_critical = any(data.get(field) is None for field in critical_fields)
        
        # Confiança baixa em campos existentes
        low_confidence = current_result.get('overall_confidence', 0) < 0.6
        
        return missing_critical or low_confidence
    
    def _merge_results(self, base_result: Dict[str, Any], 
                      new_result: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Mescla resultados de diferentes fontes"""
        
        # Adicionar fonte
        base_result['sources'].append(source)
        
        # Mesclar dados com base na confiança
        for field, value in new_result['data'].items():
            if value is not None:
                current_confidence = base_result['confidence_scores'].get(field, 0)
                new_confidence = new_result['confidence_scores'].get(field, 0)
                
                # Usar valor com maior confiança
                if new_confidence > current_confidence:
                    base_result['data'][field] = value
                    base_result['confidence_scores'][field] = new_confidence
        
        return base_result
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados extraídos"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        for field, value in data.items():
            if value is None:
                continue
            
            if field in self.validation_patterns:
                pattern_config = self.validation_patterns[field]
                
                # Validar faixa de valores
                if isinstance(value, (int, float)):
                    if value < pattern_config['min'] or value > pattern_config['max']:
                        validation_result['errors'].append(
                            f"{field}: valor {value} fora da faixa válida ({pattern_config['min']}-{pattern_config['max']})"
                        )
                        validation_result['is_valid'] = False
        
        # Validações específicas
        if data.get('price') and data.get('area'):
            price_per_sqm = data['price'] / data['area']
            if price_per_sqm < 500 or price_per_sqm > 50000:  # R$/m²
                validation_result['warnings'].append(
                    f"Preço por m² suspeito: R$ {price_per_sqm:.2f}/m²"
                )
        
        return validation_result
    
    def _calculate_overall_confidence(self, result: Dict[str, Any]) -> float:
        """Calcula confiança geral do resultado"""
        confidence_scores = result['confidence_scores']
        
        if not confidence_scores:
            return 0.0
        
        # Pesos por importância do campo
        field_weights = {
            'price': 0.3,
            'area': 0.25,
            'bedrooms': 0.15,
            'bathrooms': 0.1,
            'address': 0.1,
            'neighborhood': 0.05,
            'city': 0.05
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for field, confidence in confidence_scores.items():
            weight = field_weights.get(field, 0.05)
            weighted_sum += confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _clean_field_value(self, field: str, value: Any) -> Any:
        """Limpa e converte valores de campos"""
        if value is None:
            return None
        
        try:
            if field == 'price':
                return self._parse_price_string(str(value))
            elif field == 'area':
                return self._parse_area_string(str(value))
            elif field in ['bedrooms', 'bathrooms', 'parking']:
                return int(value)
            else:
                return str(value).strip()
        
        except (ValueError, TypeError):
            return None
    
    def _parse_price_string(self, price_str: str) -> Optional[float]:
        """Parse de string de preço"""
        try:
            # Remover símbolos mantendo apenas dígitos, pontos e vírgulas
            clean_price = re.sub(r'[^\d,.]', '', price_str)
            
            if not clean_price:
                return None
            
            # Determinar formato e converter
            if ',' in clean_price and '.' in clean_price:
                # Formato brasileiro: 1.200.000,00
                clean_price = clean_price.replace('.', '').replace(',', '.')
            elif '.' in clean_price:
                # Verificar se é separador de milhares ou decimal
                parts = clean_price.split('.')
                if len(parts) > 2:
                    # Múltiplos pontos = separador de milhares: 1.200.000
                    clean_price = clean_price.replace('.', '')
                elif len(parts) == 2 and len(parts[1]) <= 2 and len(parts[0]) <= 3:
                    # Decimal: 850.50
                    clean_price = clean_price
                else:
                    # Separador de milhares: 1200.000
                    clean_price = clean_price.replace('.', '')
            elif ',' in clean_price:
                # Vírgula como decimal
                if len(clean_price.split(',')[1]) <= 2:
                    clean_price = clean_price.replace(',', '.')
                else:
                    clean_price = clean_price.replace(',', '')
            
            value = float(clean_price)
            return value if 10000 <= value <= 50000000 else None
        
        except (ValueError, AttributeError):
            return None
    
    def _parse_area_string(self, area_str: str) -> Optional[float]:
        """Parse de string de área"""
        try:
            clean_area = re.sub(r'[^\d,.]', '', area_str)
            if ',' in clean_area:
                clean_area = clean_area.replace(',', '.')
            
            value = float(clean_area)
            return value if 10 <= value <= 10000 else None
        
        except (ValueError, AttributeError):
            return None
    
    def _generate_cache_key(self, structured_data: Optional[Dict], 
                          html_content: Optional[str], url: Optional[str]) -> Optional[str]:
        """Gera chave de cache"""
        try:
            import hashlib
            
            key_data = {
                'url': url,
                'structured_hash': hashlib.md5(
                    json.dumps(structured_data, sort_keys=True).encode()
                ).hexdigest() if structured_data else None,
                'html_hash': hashlib.md5(
                    html_content.encode()
                ).hexdigest() if html_content else None
            }
            
            key_string = json.dumps(key_data, sort_keys=True)
            return f"smart_extract:{hashlib.md5(key_string.encode()).hexdigest()}"
        
        except Exception:
            return None
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Obtém resultado do cache"""
        if not self.cache_service:
            return None
        
        try:
            # Tentar usar o método get do cache
            if hasattr(self.cache_service, 'get'):
                # Usar type: ignore para suprimir erros de tipo
                cached_data = await self.cache_service.get(cache_key)  # type: ignore
                return json.loads(cached_data) if cached_data else None
        except Exception:
            pass
        
        return None
    
    async def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Salva resultado no cache"""
        if not self.cache_service:
            return
        
        try:
            # Tentar usar setex primeiro, depois set
            if hasattr(self.cache_service, 'setex'):
                # Cache por 24 horas - usar type: ignore para suprimir erros
                await self.cache_service.setex(cache_key, 86400, json.dumps(result))  # type: ignore
            elif hasattr(self.cache_service, 'set'):
                await self.cache_service.set(cache_key, json.dumps(result))  # type: ignore
        except Exception as e:
            self.logger.warning(f"Erro ao salvar no cache: {e}")
    
    def _log_extraction_result(self, result: Dict[str, Any]):
        """Log detalhado do resultado"""
        data = result['data']
        filled_fields = [k for k, v in data.items() if v is not None]
        
        if result['success']:
            self.logger.info(
                f"✅ Extração bem-sucedida: {len(filled_fields)} campos preenchidos "
                f"(confiança: {result['overall_confidence']:.2f}, "
                f"tempo: {result['processing_time']:.2f}s, "
                f"fontes: {', '.join(result['sources'])})"
            )
        else:
            self.logger.warning(
                f"⚠️ Extração com problemas: {len(filled_fields)} campos preenchidos "
                f"(confiança: {result['overall_confidence']:.2f})"
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas"""
        base_stats: Dict[str, Any] = self.stats.copy()
        
        # Calcular taxas
        if base_stats['total_extractions'] > 0:
            base_stats['structured_success_rate'] = (
                base_stats['structured_success'] / base_stats['total_extractions']
            )
            base_stats['ocr_usage_rate'] = (
                base_stats['ocr_fallback_used'] / base_stats['total_extractions']
            )
            base_stats['cache_hit_rate'] = (
                base_stats['cache_hits'] / base_stats['total_extractions']
            )
        
        # Estatísticas dos serviços
        if self.ocr_service and hasattr(self.ocr_service, 'get_statistics'):
            try:
                base_stats['ocr_stats'] = self.ocr_service.get_statistics()
            except Exception:
                base_stats['ocr_stats'] = {}
        
        return base_stats
    
    async def close(self):
        """Fecha todos os serviços"""
        if self.cache_service and hasattr(self.cache_service, 'close'):
            try:
                await self.cache_service.close()  # type: ignore
            except Exception as e:
                self.logger.warning(f"Erro ao fechar cache service: {e}")
        
        if self.db_service and hasattr(self.db_service, 'close'):
            try:
                await self.db_service.close()  # type: ignore
            except Exception as e:
                self.logger.warning(f"Erro ao fechar database service: {e}")


# Exemplo de uso integrado
async def main():
    """Exemplo de uso do SmartDataExtractor"""
    extractor = SmartDataExtractor(use_cache=True, use_ocr=True)
    await extractor.initialize()
    
    # Exemplo 1: Dados estruturados completos
    structured_data = {
        'price': 850000,
        'area': 120,
        'bedrooms': 3,
        'bathrooms': 2,
        'address': 'Rua das Flores, 123',
        'city': 'São Paulo',
        'state': 'SP'
    }
    
    result1 = await extractor.extract_property_data(structured_data=structured_data)
    print(f"Resultado estruturado: {result1['success']}, confiança: {result1['overall_confidence']:.2f}")
    
    # Exemplo 2: HTML com dados incompletos + imagens (simulado)
    html_content = """
    <div class="property">
        <h1>Apartamento 3 quartos</h1>
        <span class="price">R$ 850.000,00</span>
        <div class="area">120 m²</div>
    </div>
    """
    
    result2 = await extractor.extract_property_data(
        html_content=html_content,
        images=[],  # Lista vazia para exemplo
        url="https://exemplo.com/imovel123"
    )
    print(f"Resultado HTML: {result2['success']}, confiança: {result2['overall_confidence']:.2f}")
    
    # Estatísticas
    stats = extractor.get_statistics()
    print(f"Estatísticas: {stats}")
    
    await extractor.close()

if __name__ == "__main__":
    asyncio.run(main())
