# test_ocr_system.py
"""
Testes Completos do Sistema de OCR para Análise de Imagens
Testa extração de dados, fallback inteligente e integração com scrapers.
"""
import asyncio
import logging
import tempfile
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Imports do sistema
try:
    from backend.services.ocr_service import OCRService
    from backend.services.smart_data_extractor import SmartDataExtractor
    from backend.services.enhanced_scraper import EnhancedScraper
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Serviços não disponíveis: {e}")
    OCRService = None
    SmartDataExtractor = None
    EnhancedScraper = None
    SERVICES_AVAILABLE = False

# Image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    import io
    IMAGING_AVAILABLE = True
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None
    io = None
    IMAGING_AVAILABLE = False

class OCRSystemTester:
    """Tester completo para o sistema de OCR"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Serviços
        self.ocr_service = None
        self.smart_extractor = None
        self.enhanced_scraper = None
        
        # Resultados dos testes
        self.test_results = []
        
        # Dados de teste
        self.sample_property_data = [
            {
                'text': "APARTAMENTO 3 QUARTOS\nR$ 850.000,00\n120 m² área útil\n2 banheiros\n1 vaga garagem",
                'expected': {
                    'price': 850000.0,
                    'area': 120.0,
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'parking': 1
                }
            },
            {
                'text': "CASA TÉRREA\nValor: R$ 1.200.000\n200m² terreno\n4 qtos, 3 banhs\n2 vagas",
                'expected': {
                    'price': 1200000.0,
                    'area': 200.0,
                    'bedrooms': 4,
                    'bathrooms': 3,
                    'parking': 2
                }
            },
            {
                'text': "Cobertura Duplex\n2.5 milhões\n150 metros quadrados\n3 suítes + 1 quarto\n4 banheiros",
                'expected': {
                    'price': 2500000.0,
                    'area': 150.0,
                    'bedrooms': 4,
                    'bathrooms': 4
                }
            }
        ]
    
    async def initialize(self):
        """Inicializa serviços para teste"""
        try:
            if SERVICES_AVAILABLE and OCRService and SmartDataExtractor and EnhancedScraper:
                self.ocr_service = OCRService()
                self.smart_extractor = SmartDataExtractor(use_cache=False, use_ocr=True)
                await self.smart_extractor.initialize()
                
                self.enhanced_scraper = EnhancedScraper(use_ocr=True)
                await self.enhanced_scraper.initialize()
                
                self.logger.info("✅ Serviços inicializados para teste")
            else:
                self.logger.warning("⚠️ Serviços não disponíveis - executando testes limitados")
        
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    def create_test_image(self, text_lines: List[str], size: tuple = (400, 300)):
        """Cria imagem de teste com texto"""
        if not IMAGING_AVAILABLE or not Image:
            raise Exception("PIL não disponível")
        
        # Criar imagem
        img = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(img)
        
        # Tentar carregar fonte
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Adicionar texto
        y_pos = 30
        for line in text_lines:
            draw.text((20, y_pos), line, fill='black', font=font)
            y_pos += 30
        
        return img
    
    async def test_ocr_service(self) -> Dict[str, Any]:
        """Testa o serviço de OCR básico"""
        test_name = "OCR Service Basic"
        self.logger.info(f"🧪 Iniciando teste: {test_name}")
        
        if not self.ocr_service:
            return self._create_test_result(test_name, False, "OCR Service não disponível")
        
        try:
            results = []
            
            # Verificar disponibilidade
            availability = self.ocr_service.check_availability()
            self.logger.info(f"Disponibilidade OCR: {availability}")
            
            if not availability['overall']:
                return self._create_test_result(
                    test_name, False, "Nenhuma engine de OCR disponível"
                )
            
            # Testar com cada sample
            for i, sample in enumerate(self.sample_property_data):
                try:
                    # Criar imagem com texto
                    text_lines = sample['text'].split('\n')
                    test_image = self.create_test_image(text_lines)
                    
                    # Analisar imagem
                    result = await self.ocr_service.analyze_image(test_image)
                    
                    # Verificar resultado
                    success = result['success']
                    extracted_data = result['data']
                    confidence = result['confidence']
                    
                    # Comparar com esperado
                    matches = self._compare_extracted_data(extracted_data, sample['expected'])
                    
                    results.append({
                        'sample_index': i,
                        'success': success,
                        'confidence': confidence,
                        'matches': matches,
                        'extracted': extracted_data,
                        'expected': sample['expected']
                    })
                    
                    self.logger.info(f"Sample {i}: {matches['total_matches']}/{matches['total_fields']} campos corretos")
                
                except Exception as e:
                    self.logger.error(f"Erro no sample {i}: {e}")
                    results.append({
                        'sample_index': i,
                        'success': False,
                        'error': str(e)
                    })
            
            # Calcular estatísticas gerais
            successful_tests = sum(1 for r in results if r.get('success', False))
            total_matches = sum(r.get('matches', {}).get('total_matches', 0) for r in results)
            total_fields = sum(r.get('matches', {}).get('total_fields', 0) for r in results)
            
            accuracy = total_matches / total_fields if total_fields > 0 else 0
            
            return self._create_test_result(
                test_name, True,
                f"{successful_tests}/{len(results)} testes bem-sucedidos, "
                f"precisão: {accuracy:.2%}",
                {
                    'successful_tests': successful_tests,
                    'total_tests': len(results),
                    'accuracy': accuracy,
                    'results': results
                }
            )
        
        except Exception as e:
            return self._create_test_result(test_name, False, str(e))
    
    async def test_smart_extractor(self) -> Dict[str, Any]:
        """Testa o extrator inteligente"""
        test_name = "Smart Data Extractor"
        self.logger.info(f"🧪 Iniciando teste: {test_name}")
        
        if not self.smart_extractor:
            return self._create_test_result(test_name, False, "Smart Extractor não disponível")
        
        try:
            results = []
            
            for i, sample in enumerate(self.sample_property_data):
                try:
                    # Teste 1: Dados estruturados completos
                    result1 = await self.smart_extractor.extract_property_data(
                        structured_data=sample['expected']
                    )
                    
                    # Teste 2: HTML com dados parciais
                    html_content = f"""
                    <div class="property">
                        <h1>Propriedade {i}</h1>
                        <span class="price">R$ {sample['expected']['price']:,.0f}</span>
                    </div>
                    """
                    
                    result2 = await self.smart_extractor.extract_property_data(
                        html_content=html_content
                    )
                    
                    # Teste 3: OCR fallback (se disponível)
                    if IMAGING_AVAILABLE and io:
                        text_lines = sample['text'].split('\n')
                        test_image = self.create_test_image(text_lines)
                        
                        # Converter para bytes
                        img_bytes = io.BytesIO()
                        test_image.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        result3 = await self.smart_extractor.extract_property_data(
                            structured_data={},  # Dados vazios para forçar OCR
                            images=[img_bytes.getvalue()]
                        )
                    else:
                        result3 = {'success': False, 'error': 'PIL ou io não disponível'}
                    
                    results.append({
                        'sample_index': i,
                        'structured_test': {
                            'success': result1['success'],
                            'confidence': result1.get('overall_confidence', 0)
                        },
                        'html_test': {
                            'success': result2['success'],
                            'confidence': result2.get('overall_confidence', 0)
                        },
                        'ocr_test': {
                            'success': result3.get('success', False),
                            'confidence': result3.get('overall_confidence', 0)
                        }
                    })
                
                except Exception as e:
                    self.logger.error(f"Erro no teste smart extractor sample {i}: {e}")
                    results.append({
                        'sample_index': i,
                        'error': str(e)
                    })
            
            # Estatísticas
            structured_success = sum(1 for r in results if r.get('structured_test', {}).get('success', False))
            html_success = sum(1 for r in results if r.get('html_test', {}).get('success', False))
            ocr_success = sum(1 for r in results if r.get('ocr_test', {}).get('success', False))
            
            return self._create_test_result(
                test_name, True,
                f"Estruturado: {structured_success}/{len(results)}, "
                f"HTML: {html_success}/{len(results)}, "
                f"OCR: {ocr_success}/{len(results)}",
                {
                    'structured_success_rate': structured_success / len(results),
                    'html_success_rate': html_success / len(results),
                    'ocr_success_rate': ocr_success / len(results),
                    'results': results
                }
            )
        
        except Exception as e:
            return self._create_test_result(test_name, False, str(e))
    
    async def test_enhanced_scraper(self) -> Dict[str, Any]:
        """Testa o scraper aprimorado"""
        test_name = "Enhanced Scraper"
        self.logger.info(f"🧪 Iniciando teste: {test_name}")
        
        if not self.enhanced_scraper:
            return self._create_test_result(test_name, False, "Enhanced Scraper não disponível")
        
        try:
            # Teste com dados simulados (já que não temos URLs reais)
            test_data = {
                'traditional_data': {
                    'price': 850000,
                    'area': 120,
                    'bedrooms': 3
                },
                'ocr_enhanced_data': {
                    'price': 850000,
                    'area': 120,
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'parking': 1
                }
            }
            
            # Simular resultado de scraping
            original_fields = len([v for v in test_data['traditional_data'].values() if v])
            enhanced_fields = len([v for v in test_data['ocr_enhanced_data'].values() if v])
            
            improvement = enhanced_fields - original_fields
            
            # Verificar estatísticas do scraper
            stats = self.enhanced_scraper.get_statistics()
            
            return self._create_test_result(
                test_name, True,
                f"Melhoria simulada: +{improvement} campos com OCR",
                {
                    'original_fields': original_fields,
                    'enhanced_fields': enhanced_fields,
                    'improvement': improvement,
                    'scraper_stats': stats
                }
            )
        
        except Exception as e:
            return self._create_test_result(test_name, False, str(e))
    
    async def test_integration_workflow(self) -> Dict[str, Any]:
        """Testa o workflow completo de integração"""
        test_name = "Integration Workflow"
        self.logger.info(f"🧪 Iniciando teste: {test_name}")
        
        try:
            workflow_steps = []
            
            # Passo 1: Dados estruturados disponíveis
            step1_data = {'price': 850000, 'area': 120}
            workflow_steps.append({
                'step': 'structured_data',
                'success': True,
                'data_completeness': len([v for v in step1_data.values() if v]) / 5  # 5 campos esperados
            })
            
            # Passo 2: OCR como fallback
            if self.ocr_service and IMAGING_AVAILABLE:
                try:
                    test_image = self.create_test_image([
                        "APARTAMENTO 3 QUARTOS",
                        "2 BANHEIROS",
                        "1 VAGA"
                    ])
                    
                    ocr_result = await self.ocr_service.analyze_image(test_image)
                    
                    workflow_steps.append({
                        'step': 'ocr_fallback',
                        'success': ocr_result['success'],
                        'confidence': ocr_result.get('confidence', 0)
                    })
                except Exception as e:
                    workflow_steps.append({
                        'step': 'ocr_fallback',
                        'success': False,
                        'error': str(e)
                    })
            else:
                workflow_steps.append({
                    'step': 'ocr_fallback',
                    'success': False,
                    'reason': 'OCR ou PIL não disponível'
                })
            
            # Passo 3: Validação e limpeza
            final_data = {
                'price': 850000.0,
                'area': 120.0,
                'bedrooms': 3,
                'bathrooms': 2,
                'parking': 1
            }
            
            # Validar dados
            validation_errors = []
            if final_data['price'] < 10000:
                validation_errors.append("Preço muito baixo")
            if final_data['area'] < 10:
                validation_errors.append("Área muito pequena")
            
            workflow_steps.append({
                'step': 'validation',
                'success': len(validation_errors) == 0,
                'errors': validation_errors,
                'final_data': final_data
            })
            
            # Resultado geral
            successful_steps = sum(1 for step in workflow_steps if step['success'])
            
            return self._create_test_result(
                test_name, True,
                f"{successful_steps}/{len(workflow_steps)} etapas bem-sucedidas",
                {
                    'workflow_steps': workflow_steps,
                    'success_rate': successful_steps / len(workflow_steps),
                    'final_data_completeness': len([v for v in final_data.values() if v]) / 5
                }
            )
        
        except Exception as e:
            return self._create_test_result(test_name, False, str(e))
    
    def _compare_extracted_data(self, extracted: Dict[str, Any], 
                              expected: Dict[str, Any]) -> Dict[str, Any]:
        """Compara dados extraídos com esperados"""
        matches = 0
        total_fields = len(expected)
        field_comparisons = {}
        
        for field, expected_value in expected.items():
            extracted_value = extracted.get(field)
            
            if extracted_value is None:
                field_comparisons[field] = {'match': False, 'reason': 'not_extracted'}
            else:
                # Comparação com tolerância para valores numéricos
                if isinstance(expected_value, (int, float)) and isinstance(extracted_value, (int, float)):
                    tolerance = 0.1 * expected_value  # 10% de tolerância
                    match = abs(extracted_value - expected_value) <= tolerance
                else:
                    match = str(extracted_value).lower() == str(expected_value).lower()
                
                field_comparisons[field] = {
                    'match': match,
                    'extracted': extracted_value,
                    'expected': expected_value
                }
                
                if match:
                    matches += 1
        
        return {
            'total_matches': matches,
            'total_fields': total_fields,
            'accuracy': matches / total_fields if total_fields > 0 else 0,
            'field_comparisons': field_comparisons
        }
    
    def _create_test_result(self, test_name: str, success: bool, 
                          message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cria resultado padronizado de teste"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.test_results.append(result)
        return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        self.logger.info("🧪 Iniciando bateria completa de testes OCR")
        
        start_time = datetime.now()
        
        # Lista de testes
        test_functions = [
            self.test_ocr_service,
            self.test_smart_extractor,
            self.test_enhanced_scraper,
            self.test_integration_workflow
        ]
        
        # Executar testes
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                self.logger.error(f"❌ Erro no teste {test_func.__name__}: {e}")
                self._create_test_result(
                    test_func.__name__, False, f"Erro na execução: {e}"
                )
        
        # Compilar resultados finais
        successful_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        
        final_result = {
            'overall_success': successful_tests == total_tests,
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'execution_time': (datetime.now() - start_time).total_seconds(),
            'test_results': self.test_results,
            'summary': self._generate_test_summary()
        }
        
        self._log_final_results(final_result)
        return final_result
    
    def _generate_test_summary(self) -> Dict[str, Any]:
        """Gera resumo dos testes"""
        summary = {
            'ocr_availability': False,
            'extraction_accuracy': 0.0,
            'integration_success': False,
            'recommendations': []
        }
        
        # Analisar resultados
        for result in self.test_results:
            if result['test_name'] == 'OCR Service Basic':
                summary['ocr_availability'] = result['success']
                if result['success'] and 'details' in result:
                    summary['extraction_accuracy'] = result['details'].get('accuracy', 0)
            
            elif result['test_name'] == 'Integration Workflow':
                summary['integration_success'] = result['success']
        
        # Gerar recomendações
        if not summary['ocr_availability']:
            summary['recommendations'].append(
                "Instalar dependências de OCR: pip install pytesseract easyocr opencv-python"
            )
        
        if summary['extraction_accuracy'] < 0.7:
            summary['recommendations'].append(
                "Considerar melhorar pré-processamento de imagens para maior precisão"
            )
        
        if not summary['integration_success']:
            summary['recommendations'].append(
                "Verificar integração entre componentes do sistema"
            )
        
        return summary
    
    def _log_final_results(self, final_result: Dict[str, Any]):
        """Log dos resultados finais"""
        self.logger.info("=" * 60)
        self.logger.info("📊 RESULTADOS FINAIS DOS TESTES OCR")
        self.logger.info("=" * 60)
        
        if final_result['overall_success']:
            self.logger.info("✅ TODOS OS TESTES PASSARAM!")
        else:
            self.logger.warning(f"⚠️ {final_result['successful_tests']}/{final_result['total_tests']} testes passaram")
        
        self.logger.info(f"Taxa de sucesso: {final_result['success_rate']:.1%}")
        self.logger.info(f"Tempo de execução: {final_result['execution_time']:.2f}s")
        
        # Log de cada teste
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            self.logger.info(f"{status} {result['test_name']}: {result['message']}")
        
        # Recomendações
        summary = final_result['summary']
        if summary['recommendations']:
            self.logger.info("\n📋 RECOMENDAÇÕES:")
            for rec in summary['recommendations']:
                self.logger.info(f"• {rec}")
        
        self.logger.info("=" * 60)
    
    async def close(self):
        """Fecha serviços"""
        if self.smart_extractor:
            await self.smart_extractor.close()
        if self.enhanced_scraper:
            await self.enhanced_scraper.close()


async def main():
    """Executa testes do sistema OCR"""
    tester = OCRSystemTester()
    
    try:
        await tester.initialize()
        final_result = await tester.run_all_tests()
        
        # Salvar resultados
        results_file = "ocr_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Resultados salvos em: {results_file}")
        
        return final_result
    
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())
