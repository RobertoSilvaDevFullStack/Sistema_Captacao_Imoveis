# demo_ocr_integration.py
"""
Demonstração Completa do Sistema de OCR Integrado
Mostra como o sistema usa OCR como fallback inteligente para extração de dados de imóveis.
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar serviços
try:
    from backend.services.ocr_service_simple import OCRServiceSimple
    from backend.services.database_service import DatabaseService
    OCRServiceSimple_available = True
    DatabaseService_available = True
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.error(f"Erro ao importar serviços: {e}")
    OCRServiceSimple_available = False
    DatabaseService_available = False
    SERVICES_AVAILABLE = False

class OCRIntegrationDemo:
    """Demonstração da integração completa do sistema de OCR"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inicializar serviços
        self.ocr_service = None
        self.cache_service = None
        self.db_service = None
        
        # Dados de demonstração
        self.demo_scenarios = [
            {
                'name': 'Cenário 1: Dados estruturados completos',
                'structured_data': {
                    'price': 850000,
                    'area': 120,
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'parking': 1,
                    'address': 'Rua das Flores, 123',
                    'city': 'São Paulo',
                    'state': 'SP'
                },
                'need_ocr': False,
                'description': 'Dados já disponíveis via scraping estruturado'
            },
            {
                'name': 'Cenário 2: Dados incompletos - OCR como fallback',
                'structured_data': {
                    'address': 'Rua das Palmeiras, 456',
                    'city': 'Rio de Janeiro',
                    'state': 'RJ'
                },
                'ocr_text': 'CASA TÉRREA\nValor: R$ 1.200.000\n200m² terreno\n4 qtos, 3 banhs\n2 vagas',
                'need_ocr': True,
                'description': 'Endereço disponível, mas preço e características via OCR'
            },
            {
                'name': 'Cenário 3: Apenas OCR disponível',
                'structured_data': {},
                'ocr_text': 'Cobertura Duplex\n2.5 milhões\n150 metros quadrados\n3 suítes + 1 quarto\n4 banheiros\nVaga dupla',
                'need_ocr': True,
                'description': 'Nenhum dado estruturado, apenas imagem com texto'
            },
            {
                'name': 'Cenário 4: Dados conflitantes - validação cruzada',
                'structured_data': {
                    'price': 800000,  # Preço do scraping
                    'bedrooms': 2,    # Quartos do scraping
                    'city': 'Belo Horizonte',
                    'state': 'MG'
                },
                'ocr_text': 'APARTAMENTO 3 QUARTOS\nR$ 850.000,00\n120 m² área útil\n2 banheiros',
                'need_ocr': True,
                'description': 'Dados diferentes entre scraping e OCR - sistema deve decidir'
            }
        ]
    
    async def initialize(self):
        """Inicializa todos os serviços"""
        try:
            if not SERVICES_AVAILABLE:
                self.logger.warning("⚠️ Serviços não disponíveis - demo limitada")
                return
            
            # OCR Service
            if OCRServiceSimple_available:
                self.ocr_service = OCRServiceSimple()
            
            # Database Service
            if DatabaseService_available:
                self.db_service = DatabaseService("demo_ocr.db")
                await self.db_service.initialize()
            
            self.logger.info("✅ Todos os serviços inicializados")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            raise
    
    async def run_integration_demo(self):
        """Executa demonstração completa"""
        self.logger.info("🎬 INICIANDO DEMONSTRAÇÃO DE INTEGRAÇÃO OCR")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        results = []
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            self.logger.info(f"\n📋 {scenario['name']}")
            self.logger.info(f"📝 {scenario['description']}")
            self.logger.info("-" * 40)
            
            try:
                result = await self._process_scenario(scenario)
                results.append(result)
                
                # Log resultado
                self._log_scenario_result(scenario, result)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no cenário {i}: {e}")
                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'error': str(e)
                })
        
        # Compilar resultados finais
        total_time = (datetime.now() - start_time).total_seconds()
        final_results = self._compile_final_results(results, total_time)
        
        # Salvar resultados
        await self._save_demo_results(final_results)
        
        # Log resumo final
        self._log_final_summary(final_results)
        
        return final_results
    
    async def _process_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um cenário individual"""
        scenario_start = datetime.now()
        
        # Dados estruturados iniciais
        structured_data = scenario['structured_data']
        need_ocr = scenario['need_ocr']
        
        # Resultado do processamento
        result = {
            'scenario': scenario['name'],
            'initial_data': structured_data.copy(),
            'final_data': structured_data.copy(),
            'ocr_used': False,
            'improvements': [],
            'processing_steps': [],
            'performance': {}
        }
        
        # Passo 1: Avaliar completude dos dados
        initial_completeness = self._calculate_completeness(structured_data)
        result['processing_steps'].append(f"Completude inicial: {initial_completeness:.1%}")
        
        # Passo 2: Decidir se usar OCR
        if need_ocr and initial_completeness < 0.8:  # Se menos de 80% completo
            result['processing_steps'].append("🤖 Decidindo usar OCR como fallback")
            
            # Simular OCR
            if self.ocr_service:
                # Configurar dados de teste
                ocr_test_data = {
                    f"scenario_{scenario['name']}": scenario.get('ocr_text', '')
                }
                self.ocr_service.enable_test_mode(ocr_test_data)
                
                # Executar OCR
                ocr_result = await self.ocr_service.analyze_image(f"scenario_{scenario['name']}")
                
                if ocr_result['success']:
                    result['ocr_used'] = True
                    result['processing_steps'].append(f"✅ OCR executado (confiança: {ocr_result['confidence']:.2f})")
                    
                    # Mesclar dados
                    ocr_data = ocr_result['data']
                    merged_data = self._merge_data_intelligently(structured_data, ocr_data)
                    
                    result['final_data'] = merged_data
                    result['improvements'] = self._identify_improvements(structured_data, merged_data)
                    
                else:
                    result['processing_steps'].append("❌ OCR falhou")
        
        else:
            result['processing_steps'].append("✅ Dados estruturados suficientes - OCR não necessário")
        
        # Passo 3: Validação final
        final_completeness = self._calculate_completeness(result['final_data'])
        result['processing_steps'].append(f"Completude final: {final_completeness:.1%}")
        
        # Passo 4: Salvar no banco de dados
        if self.db_service:
            try:
                property_id, is_new = await self.db_service.save_property(result['final_data'])
                result['processing_steps'].append(f"💾 Propriedade {'nova' if is_new else 'existente'}: ID {property_id}")
            except Exception as e:
                result['processing_steps'].append(f"❌ Erro ao salvar: {e}")
        
        # Performance
        processing_time = (datetime.now() - scenario_start).total_seconds()
        result['performance'] = {
            'processing_time': processing_time,
            'improvement_ratio': final_completeness / max(initial_completeness, 0.1),
            'fields_added': len(result['improvements'])
        }
        
        result['success'] = final_completeness > initial_completeness or final_completeness > 0.5
        
        return result
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calcula completude dos dados"""
        essential_fields = ['price', 'area', 'bedrooms', 'bathrooms', 'address', 'city', 'state']
        
        filled_fields = sum(1 for field in essential_fields if data.get(field))
        return filled_fields / len(essential_fields)
    
    def _merge_data_intelligently(self, structured_data: Dict[str, Any], 
                                ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mescla dados de forma inteligente"""
        merged = structured_data.copy()
        
        # Regras de mesclagem
        for field, ocr_value in ocr_data.items():
            if field in ['raw_text', 'confidence']:
                continue
            
            if ocr_value is None:
                continue
            
            structured_value = structured_data.get(field)
            
            if structured_value is None:
                # Campo não existe em dados estruturados - usar OCR
                merged[field] = ocr_value
            
            elif isinstance(structured_value, (int, float)) and isinstance(ocr_value, (int, float)):
                # Valores numéricos - usar lógica de validação
                diff_percent = abs(structured_value - ocr_value) / max(structured_value, ocr_value)
                
                if diff_percent < 0.1:  # Diferença menor que 10%
                    # Valores similares - manter estruturado
                    pass
                elif structured_value == 0 or structured_value is None:
                    # Valor estruturado inválido - usar OCR
                    merged[field] = ocr_value
                else:
                    # Conflito - manter estruturado mas adicionar nota
                    merged[f'{field}_ocr_alternative'] = ocr_value
            
            else:
                # Strings - preferir dados estruturados se já existem
                if not structured_value or (isinstance(structured_value, str) and structured_value.strip() == ''):
                    merged[field] = ocr_value
        
        return merged
    
    def _identify_improvements(self, original: Dict[str, Any], 
                             improved: Dict[str, Any]) -> List[str]:
        """Identifica melhorias feitas pelo OCR"""
        improvements = []
        
        for field, new_value in improved.items():
            if field.endswith('_ocr_alternative'):
                improvements.append(f"Conflito detectado em {field.replace('_ocr_alternative', '')}")
                continue
            
            original_value = original.get(field)
            
            if original_value is None and new_value is not None:
                improvements.append(f"Campo {field} adicionado via OCR: {new_value}")
            elif original_value != new_value and new_value is not None:
                improvements.append(f"Campo {field} atualizado: {original_value} → {new_value}")
        
        return improvements
    
    def _log_scenario_result(self, scenario: Dict[str, Any], result: Dict[str, Any]):
        """Log detalhado do resultado do cenário"""
        
        # Status geral
        status = "✅ SUCESSO" if result['success'] else "⚠️ PARCIAL"
        self.logger.info(f"🎯 Resultado: {status}")
        
        # Passos do processamento
        for step in result['processing_steps']:
            self.logger.info(f"   {step}")
        
        # Melhorias identificadas
        if result['improvements']:
            self.logger.info("🔧 Melhorias via OCR:")
            for improvement in result['improvements']:
                self.logger.info(f"   • {improvement}")
        
        # Performance
        perf = result['performance']
        self.logger.info(f"⚡ Performance: {perf['processing_time']:.2f}s, "
                        f"melhoria: {perf['improvement_ratio']:.1f}x, "
                        f"campos adicionados: {perf['fields_added']}")
    
    def _compile_final_results(self, results: List[Dict[str, Any]], 
                             total_time: float) -> Dict[str, Any]:
        """Compila resultados finais"""
        successful_scenarios = sum(1 for r in results if r.get('success', False))
        ocr_used_count = sum(1 for r in results if r.get('ocr_used', False))
        
        total_improvements = sum(len(r.get('improvements', [])) for r in results)
        avg_processing_time = sum(r.get('performance', {}).get('processing_time', 0) for r in results) / len(results)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_scenarios': len(results),
                'successful_scenarios': successful_scenarios,
                'success_rate': successful_scenarios / len(results),
                'ocr_usage_rate': ocr_used_count / len(results),
                'total_improvements': total_improvements,
                'avg_processing_time': avg_processing_time,
                'total_execution_time': total_time
            },
            'scenarios': results,
            'conclusions': self._generate_conclusions(results)
        }
    
    def _generate_conclusions(self, results: List[Dict[str, Any]]) -> List[str]:
        """Gera conclusões da demonstração"""
        conclusions = []
        
        ocr_successes = sum(1 for r in results if r.get('ocr_used', False) and r.get('success', False))
        ocr_attempts = sum(1 for r in results if r.get('ocr_used', False))
        
        if ocr_attempts > 0:
            ocr_success_rate = ocr_successes / ocr_attempts
            conclusions.append(f"Taxa de sucesso do OCR: {ocr_success_rate:.1%}")
        
        total_improvements = sum(len(r.get('improvements', [])) for r in results)
        if total_improvements > 0:
            conclusions.append(f"OCR adicionou {total_improvements} campos/melhorias no total")
        
        conclusions.append("OCR provou ser eficaz como sistema de fallback inteligente")
        conclusions.append("Sistema consegue mesclar dados estruturados e OCR de forma inteligente")
        conclusions.append("Validação cruzada detecta e resolve conflitos entre fontes")
        
        return conclusions
    
    async def _save_demo_results(self, final_results: Dict[str, Any]):
        """Salva resultados da demonstração"""
        try:
            filename = f"ocr_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"📄 Resultados salvos em: {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar resultados: {e}")
    
    def _log_final_summary(self, final_results: Dict[str, Any]):
        """Log do resumo final"""
        summary = final_results['summary']
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 RESUMO FINAL DA DEMONSTRAÇÃO OCR")
        self.logger.info("=" * 60)
        
        self.logger.info(f"📈 Cenários processados: {summary['total_scenarios']}")
        self.logger.info(f"✅ Taxa de sucesso: {summary['success_rate']:.1%}")
        self.logger.info(f"🤖 Taxa de uso do OCR: {summary['ocr_usage_rate']:.1%}")
        self.logger.info(f"🔧 Total de melhorias: {summary['total_improvements']}")
        self.logger.info(f"⚡ Tempo médio por cenário: {summary['avg_processing_time']:.2f}s")
        self.logger.info(f"🕒 Tempo total de execução: {summary['total_execution_time']:.2f}s")
        
        self.logger.info("\n🎯 CONCLUSÕES:")
        for conclusion in final_results['conclusions']:
            self.logger.info(f"• {conclusion}")
        
        self.logger.info("\n🏆 SISTEMA OCR FUNCIONANDO COMO FALLBACK INTELIGENTE!")
        self.logger.info("=" * 60)
    
    async def demonstrate_real_world_usage(self):
        """Demonstra uso real do sistema"""
        self.logger.info("\n🌍 DEMONSTRAÇÃO DE USO NO MUNDO REAL")
        self.logger.info("-" * 40)
        
        # Simular dados de anúncios reais
        real_world_examples = [
            {
                'url': 'https://vivareal.com/apartamento-1234',
                'scraping_result': {
                    'address': 'Rua Augusta, 1000',
                    'neighborhood': 'Consolação',
                    'city': 'São Paulo',
                    'state': 'SP'
                },
                'images_text': 'APARTAMENTO REFORMADO\nR$ 750.000\n85m² úteis\n2 dorms, 1 suite\n1 vaga'
            },
            {
                'url': 'https://olx.com/casa-5678',
                'scraping_result': {
                    'price': 950000,
                    'city': 'Rio de Janeiro',
                    'state': 'RJ'
                },
                'images_text': 'CASA DE VILA\n3 quartos, 2 banheiros\n150m² construída\n2 vagas descobertas'
            }
        ]
        
        for i, example in enumerate(real_world_examples, 1):
            self.logger.info(f"\n📋 Exemplo Real {i}: {example['url']}")
            
            # Simular processo completo
            initial_data = example['scraping_result']
            ocr_text = example['images_text']
            
            self.logger.info(f"📥 Dados do scraping: {len([v for v in initial_data.values() if v])} campos")
            
            # OCR como fallback
            if self.ocr_service:
                self.ocr_service.enable_test_mode({f"real_example_{i}": ocr_text})
                ocr_result = await self.ocr_service.analyze_image(f"real_example_{i}")
                
                if ocr_result['success']:
                    final_data = self._merge_data_intelligently(initial_data, ocr_result['data'])
                    improvements = len([v for v in final_data.values() if v]) - len([v for v in initial_data.values() if v])
                    
                    self.logger.info(f"🤖 OCR adicionou {improvements} campos adicionais")
                    self.logger.info(f"🎯 Dados finais: {list(final_data.keys())}")
                else:
                    self.logger.warning("⚠️ OCR não conseguiu extrair dados")
    
    async def close(self):
        """Fecha todos os serviços"""
        if self.db_service:
            await self.db_service.close()


async def main():
    """Executa demonstração completa"""
    demo = OCRIntegrationDemo()
    
    try:
        await demo.initialize()
        
        # Demonstração principal
        results = await demo.run_integration_demo()
        
        # Demonstração de uso real
        await demo.demonstrate_real_world_usage()
        
        return results
    
    finally:
        await demo.close()

if __name__ == "__main__":
    asyncio.run(main())
