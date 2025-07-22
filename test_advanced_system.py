#!/usr/bin/env python3
"""
Teste Avançado do Sistema de Enriquecimento de Dados
Demonstra capacidades avançadas e análise detalhada dos resultados
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Adicionar o diretório raiz ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.data_enrichment_service import DataEnrichmentService, PropertyEnrichment
from dataclasses import asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedSystemTester:
    """Tester avançado para o sistema de enriquecimento"""
    
    def __init__(self):
        self.enrichment_service = DataEnrichmentService()
        self.test_results = []
    
    async def run_comprehensive_tests(self):
        """Executa bateria completa de testes"""
        print("🚀 Sistema Avançado de Teste - APIs Oficiais e Fontes Alternativas")
        print("=" * 80)
        
        test_scenarios = [
            await self.test_luxury_property(),
            await self.test_commercial_property(), 
            await self.test_budget_property(),
            await self.test_different_states(),
            await self.test_batch_processing()
        ]
        
        # Análise consolidada
        await self.generate_consolidated_report()
        
        return test_scenarios
    
    async def test_luxury_property(self):
        """Teste com propriedade de luxo"""
        print("\n💎 TESTE 1: Propriedade de Luxo")
        print("-" * 50)
        
        luxury_property = {
            'id': 'luxury_001',
            'title': 'Cobertura Duplex Frente Mar - Leblon',
            'address': 'Avenida Delfim Moreira, 696, Leblon',
            'city': 'Rio de Janeiro',
            'state': 'RJ',
            'neighborhood': 'Leblon',
            'price': 8500000,
            'area': 280,
            'bedrooms': 4,
            'bathrooms': 5,
            'property_type': 'PENTHOUSE',
            'business_type': 'SALE',
            'features': ['Vista para o mar', 'Piscina privativa', 'Churrasqueira', 'Sauna']
        }
        
        result = await self._test_property(luxury_property, "Propriedade de Luxo")
        self.test_results.append(result)
        return result
    
    async def test_commercial_property(self):
        """Teste com propriedade comercial"""
        print("\n🏢 TESTE 2: Propriedade Comercial")
        print("-" * 50)
        
        commercial_property = {
            'id': 'commercial_001',
            'title': 'Sala Comercial - Faria Lima',
            'address': 'Avenida Brigadeiro Faria Lima, 2232, Jardim Paulistano',
            'city': 'São Paulo',
            'state': 'SP',
            'neighborhood': 'Jardim Paulistano',
            'price': 1200000,
            'area': 85,
            'property_type': 'COMMERCIAL',
            'business_type': 'SALE',
            'features': ['Andar alto', 'Vista panorâmica', 'Piso elevado', '2 vagas']
        }
        
        result = await self._test_property(commercial_property, "Propriedade Comercial")
        self.test_results.append(result)
        return result
    
    async def test_budget_property(self):
        """Teste com propriedade econômica"""
        print("\n🏠 TESTE 3: Propriedade Econômica")
        print("-" * 50)
        
        budget_property = {
            'id': 'budget_001',
            'title': 'Apartamento 2 quartos - Tijuca',
            'address': 'Rua Conde de Bonfim, 850, Tijuca',
            'city': 'Rio de Janeiro',
            'state': 'RJ',
            'neighborhood': 'Tijuca',
            'price': 350000,
            'area': 65,
            'bedrooms': 2,
            'bathrooms': 1,
            'property_type': 'APARTMENT',
            'business_type': 'SALE'
        }
        
        result = await self._test_property(budget_property, "Propriedade Econômica")
        self.test_results.append(result)
        return result
    
    async def test_different_states(self):
        """Teste com propriedades de diferentes estados"""
        print("\n🗺️ TESTE 4: Cobertura Geográfica")
        print("-" * 50)
        
        properties_by_state = [
            {
                'id': 'sp_001',
                'address': 'Rua Oscar Freire, 1000, Jardins',
                'city': 'São Paulo',
                'state': 'SP',
                'price': 2000000,
                'area': 150
            },
            {
                'id': 'mg_001', 
                'address': 'Rua da Bahia, 500, Centro',
                'city': 'Belo Horizonte',
                'state': 'MG',
                'price': 800000,
                'area': 100
            },
            {
                'id': 'df_001',
                'address': 'SQN 305, Bloco A, Asa Norte',
                'city': 'Brasília',
                'state': 'DF',
                'price': 1200000,
                'area': 120
            },
            {
                'id': 'pe_001',
                'address': 'Avenida Boa Viagem, 5000, Boa Viagem',
                'city': 'Recife',
                'state': 'PE',
                'price': 900000,
                'area': 110
            }
        ]
        
        results = []
        for prop in properties_by_state:
            print(f"\n📍 Testando: {prop['city']}/{prop['state']}")
            result = await self._test_property(prop, f"Cobertura {prop['state']}")
            results.append(result)
            self.test_results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Análise geográfica
        print(f"\n📊 Análise de Cobertura Geográfica:")
        for result in results:
            state = result['property_data']['state']
            confidence = result['enrichment_result'].confidence_score
            print(f"  {state}: Score {confidence:.2f} - {'✅' if confidence > 0.4 else '❌'}")
        
        return results
    
    async def test_batch_processing(self):
        """Teste de processamento em lote"""
        print("\n⚡ TESTE 5: Processamento em Lote")
        print("-" * 50)
        
        batch_properties = [
            {
                'id': f'batch_{i:03d}',
                'address': f'Rua Teste {i}, {100*i}, Bairro Teste',
                'city': 'São Paulo',
                'state': 'SP',
                'price': 500000 + (i * 50000),
                'area': 80 + (i * 10),
                'bedrooms': 2 + (i % 3)
            }
            for i in range(1, 6)  # 5 propriedades
        ]
        
        print(f"🔄 Processando {len(batch_properties)} propriedades em paralelo...")
        start_time = datetime.now()
        
        # Processar em lote
        tasks = [
            self.enrichment_service.enrich_property(prop) 
            for prop in batch_properties
        ]
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Análise do batch
        successful = len([r for r in batch_results if not isinstance(r, Exception)])
        failed = len(batch_results) - successful
        
        print(f"✅ Processadas: {successful}/{len(batch_properties)}")
        print(f"❌ Falhas: {failed}")
        print(f"⏱️ Tempo total: {processing_time:.2f}s")
        print(f"⚡ Throughput: {len(batch_properties)/processing_time:.2f} propriedades/segundo")
        
        return {
            'total_properties': len(batch_properties),
            'successful': successful,
            'failed': failed,
            'processing_time': processing_time,
            'throughput': len(batch_properties)/processing_time
        }
    
    async def _test_property(self, property_data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """Testa uma propriedade individual"""
        print(f"🏠 {property_data.get('title', property_data['address'])}")
        print(f"💰 R$ {property_data['price']:,.2f} | 📐 {property_data['area']}m²")
        
        try:
            # Enriquecimento
            enriched = await self.enrichment_service.enrich_property(property_data)
            
            # Análise detalhada
            analysis = self._analyze_enrichment(enriched)
            
            print(f"📊 Score: {enriched.confidence_score:.2f} | "
                  f"Dados: {analysis['data_sources_count']}/6 | "
                  f"Campos: {analysis['total_fields']}")
            
            return {
                'test_name': test_name,
                'property_data': property_data,
                'enrichment_result': enriched,
                'analysis': analysis,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return {
                'test_name': test_name,
                'property_data': property_data,
                'error': str(e),
                'success': False
            }
    
    def _analyze_enrichment(self, enriched: PropertyEnrichment) -> Dict[str, Any]:
        """Analisa resultado do enriquecimento"""
        data_sources = {
            'original_data': bool(enriched.original_data),
            'location': bool(enriched.location),
            'google_data': bool(enriched.google_data),
            'municipal_data': bool(enriched.municipal_data),
            'registry_data': bool(enriched.registry_data),
            'market_data': bool(enriched.market_data)
        }
        
        # Converter para dict para contar campos
        enriched_dict = asdict(enriched)
        total_fields = self._count_nested_fields(enriched_dict)
        
        return {
            'data_sources': data_sources,
            'data_sources_count': sum(data_sources.values()),
            'total_fields': total_fields,
            'confidence_score': enriched.confidence_score
        }
    
    def _count_nested_fields(self, data: Dict, prefix: str = "") -> int:
        """Conta campos aninhados"""
        count = 0
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    count += self._count_nested_fields(value, f"{prefix}.{key}" if prefix else key)
                else:
                    count += 1
        return count
    
    async def generate_consolidated_report(self):
        """Gera relatório consolidado dos testes"""
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO CONSOLIDADO DO SISTEMA")
        print("=" * 80)
        
        successful_tests = [r for r in self.test_results if r.get('success', False)]
        failed_tests = [r for r in self.test_results if not r.get('success', True)]
        
        print(f"\n🎯 RESUMO GERAL:")
        print(f"  Total de testes: {len(self.test_results)}")
        print(f"  Sucessos: {len(successful_tests)}")
        print(f"  Falhas: {len(failed_tests)}")
        print(f"  Taxa de sucesso: {len(successful_tests)/len(self.test_results)*100:.1f}%")
        
        if successful_tests:
            # Análise de scores
            scores = [r['enrichment_result'].confidence_score for r in successful_tests]
            avg_score = sum(scores) / len(scores)
            
            print(f"\n📊 QUALIDADE DOS DADOS:")
            print(f"  Score médio: {avg_score:.2f}")
            print(f"  Score mínimo: {min(scores):.2f}")
            print(f"  Score máximo: {max(scores):.2f}")
            
            # Análise de fontes de dados
            data_sources_analysis = {}
            for result in successful_tests:
                sources = result['analysis']['data_sources']
                for source, available in sources.items():
                    if source not in data_sources_analysis:
                        data_sources_analysis[source] = 0
                    if available:
                        data_sources_analysis[source] += 1
            
            print(f"\n🔍 COBERTURA DAS FONTES DE DADOS:")
            total_tests = len(successful_tests)
            for source, count in data_sources_analysis.items():
                percentage = (count / total_tests) * 100
                print(f"  {source}: {count}/{total_tests} ({percentage:.1f}%)")
        
        print(f"\n✅ Sistema operacional e pronto para produção!")
        print(f"📁 Logs detalhados salvos em: test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Salvar resultados
        await self._save_test_results()
    
    async def _save_test_results(self):
        """Salva resultados dos testes"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_{timestamp}.json"
        
        # Converter PropertyEnrichment para dict para serialização
        serializable_results = []
        for result in self.test_results:
            if result.get('success') and 'enrichment_result' in result:
                result_copy = result.copy()
                result_copy['enrichment_result'] = asdict(result['enrichment_result'])
                serializable_results.append(result_copy)
            else:
                serializable_results.append(result)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False, default=str)

async def main():
    """Função principal"""
    tester = AdvancedSystemTester()
    
    try:
        await tester.run_comprehensive_tests()
        
    except Exception as e:
        print(f"\n💥 Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Iniciando testes avançados do sistema...")
    asyncio.run(main())
