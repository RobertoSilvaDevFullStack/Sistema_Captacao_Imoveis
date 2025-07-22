#!/usr/bin/env python3
"""
Exemplo Completo de Integração do Sistema de Enriquecimento de Dados
Demonstra o pipeline completo desde scraping até enriquecimento com APIs oficiais
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar serviços necessários
from backend.services.data_enrichment_service import DataEnrichmentService, PropertyEnrichment

class ComprehensiveIntegrationDemo:
    """Demonstração completa do sistema de enriquecimento de dados"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inicializar serviço de enriquecimento
        self.enrichment_service = DataEnrichmentService()
    
    async def demonstrate_full_pipeline(self, max_properties: int = 5):
        """Demonstra o pipeline completo de scraping + enriquecimento"""
        
        self.logger.info("🚀 Iniciando demonstração completa do sistema")
        start_time = time.time()
        
        try:
            # Etapa 1: Simular dados básicos de propriedades
            self.logger.info("📡 Etapa 1: Carregando dados básicos...")
            raw_properties = self._generate_sample_properties(max_properties)
            
            # Etapa 2: Enriquecimento com APIs oficiais
            self.logger.info("🔍 Etapa 2: Enriquecimento com APIs oficiais...")
            enriched_properties = await self._enrich_properties(raw_properties)
            
            # Etapa 3: Análise comparativa
            self.logger.info("📊 Etapa 3: Análise comparativa dos dados...")
            analysis_report = self._analyze_enrichment_results(raw_properties, enriched_properties)
            
            # Etapa 4: Relatório final
            self.logger.info("📋 Etapa 4: Gerando relatório final...")
            final_report = self._generate_final_report(
                raw_properties, enriched_properties, analysis_report, start_time
            )
            
            # Salvar resultados
            await self._save_results(raw_properties, enriched_properties, final_report)
            
            self.logger.info("✅ Demonstração completa finalizada com sucesso!")
            return final_report
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração: {str(e)}")
            raise
    
    def _generate_sample_properties(self, max_properties: int) -> List[Dict[str, Any]]:
        """Gera dados de exemplo de propriedades"""
        
        sample_properties = [
            {
                'id': '1',
                'title': 'Apartamento 3 quartos em Copacabana',
                'address': 'Rua Barata Ribeiro, 500, Copacabana',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'neighborhood': 'Copacabana',
                'price': 1200000,
                'area': 120,
                'bedrooms': 3,
                'bathrooms': 2,
                'property_type': 'APARTMENT',
                'business_type': 'SALE'
            },
            {
                'id': '2',
                'title': 'Casa 4 quartos em Vila Madalena',
                'address': 'Rua Aspicuelta, 200, Vila Madalena',
                'city': 'São Paulo',
                'state': 'SP',
                'neighborhood': 'Vila Madalena',
                'price': 2500000,
                'area': 250,
                'bedrooms': 4,
                'bathrooms': 3,
                'property_type': 'HOUSE',
                'business_type': 'SALE'
            },
            {
                'id': '3',
                'title': 'Apartamento 2 quartos em Ipanema',
                'address': 'Rua Garcia D\'Ávila, 100, Ipanema',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'neighborhood': 'Ipanema',
                'price': 1800000,
                'area': 90,
                'bedrooms': 2,
                'bathrooms': 2,
                'property_type': 'APARTMENT',
                'business_type': 'SALE'
            },
            {
                'id': '4',
                'title': 'Cobertura 3 quartos em Leblon',
                'address': 'Avenida Ataulfo de Paiva, 300, Leblon',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'neighborhood': 'Leblon',
                'price': 4500000,
                'area': 180,
                'bedrooms': 3,
                'bathrooms': 3,
                'property_type': 'PENTHOUSE',
                'business_type': 'SALE'
            },
            {
                'id': '5',
                'title': 'Apartamento 1 quarto em Pinheiros',
                'address': 'Rua dos Pinheiros, 800, Pinheiros',
                'city': 'São Paulo',
                'state': 'SP',
                'neighborhood': 'Pinheiros',
                'price': 650000,
                'area': 45,
                'bedrooms': 1,
                'bathrooms': 1,
                'property_type': 'APARTMENT',
                'business_type': 'SALE'
            }
        ]
        
        # Retornar apenas o número solicitado
        limited_properties = sample_properties[:max_properties]
        
        self.logger.info(f"📡 Gerados {len(limited_properties)} propriedades de exemplo")
        
        return limited_properties
    
    async def _enrich_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enriquece propriedades com dados de APIs oficiais"""
        
        enriched_properties = []
        
        for i, property_data in enumerate(properties, 1):
            self.logger.info(f"🔍 Enriquecendo propriedade {i}/{len(properties)}")
            
            try:
                # Executar enriquecimento
                enriched_data = await self.enrichment_service.enrich_property(property_data)
                
                # Combinar dados originais com enriquecidos
                combined_data = {
                    'original_data': property_data,
                    'enriched_data': enriched_data.__dict__ if hasattr(enriched_data, '__dict__') else enriched_data,
                    'enrichment_timestamp': datetime.now().isoformat()
                }
                
                enriched_properties.append(combined_data)
                
                # Delay para evitar rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Erro ao enriquecer propriedade {i}: {str(e)}")
                # Adicionar dados originais mesmo com erro
                enriched_properties.append({
                    'original_data': property_data,
                    'enriched_data': None,
                    'enrichment_error': str(e),
                    'enrichment_timestamp': datetime.now().isoformat()
                })
        
        return enriched_properties
    
    def _analyze_enrichment_results(self, raw_properties: List[Dict], enriched_properties: List[Dict]) -> Dict[str, Any]:
        """Analisa resultados do enriquecimento"""
        
        total_properties = len(raw_properties)
        successfully_enriched = sum(1 for prop in enriched_properties if prop.get('enriched_data'))
        
        # Análise de dados enriquecidos
        enrichment_stats = {
            'total_properties': total_properties,
            'successfully_enriched': successfully_enriched,
            'enrichment_rate': (successfully_enriched / total_properties) * 100 if total_properties > 0 else 0,
            'failed_enrichments': total_properties - successfully_enriched
        }
        
        # Análise de qualidade dos dados
        data_quality = self._analyze_data_quality(enriched_properties)
        
        # Análise de cobertura de APIs
        api_coverage = self._analyze_api_coverage(enriched_properties)
        
        return {
            'enrichment_statistics': enrichment_stats,
            'data_quality_analysis': data_quality,
            'api_coverage_analysis': api_coverage,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _analyze_data_quality(self, enriched_properties: List[Dict]) -> Dict[str, Any]:
        """Analisa qualidade dos dados enriquecidos"""
        
        quality_metrics = {
            'complete_geocoding': 0,
            'complete_demographics': 0,
            'complete_market_data': 0,
            'complete_municipal_data': 0,
            'complete_registry_data': 0,
            'high_confidence_enrichment': 0
        }
        
        for prop in enriched_properties:
            enriched_data = prop.get('enriched_data')
            if not enriched_data:
                continue
            
            # Verificar qualidade dos dados
            if enriched_data.get('location_data', {}).get('coordinates'):
                quality_metrics['complete_geocoding'] += 1
            
            if enriched_data.get('demographic_data', {}).get('population'):
                quality_metrics['complete_demographics'] += 1
            
            if enriched_data.get('market_data', {}).get('price_estimate'):
                quality_metrics['complete_market_data'] += 1
            
            if enriched_data.get('municipal_data', {}).get('iptu_info'):
                quality_metrics['complete_municipal_data'] += 1
            
            if enriched_data.get('registry_data', {}).get('ownership_info'):
                quality_metrics['complete_registry_data'] += 1
            
            if enriched_data.get('confidence_score', 0) > 0.7:
                quality_metrics['high_confidence_enrichment'] += 1
        
        return quality_metrics
    
    def _analyze_api_coverage(self, enriched_properties: List[Dict]) -> Dict[str, Any]:
        """Analisa cobertura das diferentes APIs"""
        
        api_usage = {
            'google_maps_api': 0,
            'ibge_api': 0,
            'municipal_apis': 0,
            'registry_apis': 0,
            'market_data_apis': 0
        }
        
        for prop in enriched_properties:
            enriched_data = prop.get('enriched_data')
            if not enriched_data:
                continue
            
            # Contar uso de cada API
            if enriched_data.get('location_data'):
                api_usage['google_maps_api'] += 1
            
            if enriched_data.get('demographic_data'):
                api_usage['ibge_api'] += 1
            
            if enriched_data.get('municipal_data'):
                api_usage['municipal_apis'] += 1
            
            if enriched_data.get('registry_data'):
                api_usage['registry_apis'] += 1
            
            if enriched_data.get('market_data'):
                api_usage['market_data_apis'] += 1
        
        return api_usage
    
    def _generate_final_report(self, raw_properties: List[Dict], enriched_properties: List[Dict], 
                             analysis: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Gera relatório final da demonstração"""
        
        execution_time = time.time() - start_time
        
        report = {
            'execution_summary': {
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_execution_time_seconds': execution_time,
                'total_properties_processed': len(raw_properties),
                'successful_enrichments': analysis['enrichment_statistics']['successfully_enriched']
            },
            'data_enhancement': {
                'original_data_fields': self._count_data_fields(raw_properties),
                'enriched_data_fields': self._count_enriched_fields(enriched_properties),
                'enhancement_factor': self._calculate_enhancement_factor(raw_properties, enriched_properties)
            },
            'quality_metrics': analysis['data_quality_analysis'],
            'api_performance': analysis['api_coverage_analysis'],
            'sample_enriched_property': enriched_properties[0] if enriched_properties else None,
            'recommendations': self._generate_recommendations(analysis)
        }
        
        return report
    
    def _count_data_fields(self, properties: List[Dict]) -> int:
        """Conta campos únicos nos dados originais"""
        if not properties:
            return 0
        
        all_fields = set()
        for prop in properties:
            all_fields.update(prop.keys())
        
        return len(all_fields)
    
    def _count_enriched_fields(self, enriched_properties: List[Dict]) -> int:
        """Conta campos únicos nos dados enriquecidos"""
        if not enriched_properties:
            return 0
        
        all_fields = set()
        for prop in enriched_properties:
            enriched_data = prop.get('enriched_data')
            if enriched_data:
                all_fields.update(self._flatten_dict_keys(enriched_data))
        
        return len(all_fields)
    
    def _flatten_dict_keys(self, d: Dict, prefix: str = '') -> List[str]:
        """Aplana chaves de dicionário aninhado"""
        keys = []
        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(self._flatten_dict_keys(v, new_key))
            else:
                keys.append(new_key)
        return keys
    
    def _calculate_enhancement_factor(self, raw_properties: List[Dict], enriched_properties: List[Dict]) -> float:
        """Calcula fator de enriquecimento dos dados"""
        original_fields = self._count_data_fields(raw_properties)
        enriched_fields = self._count_enriched_fields(enriched_properties)
        
        if original_fields == 0:
            return 0.0
        
        return enriched_fields / original_fields
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        enrichment_rate = analysis['enrichment_statistics']['enrichment_rate']
        
        if enrichment_rate < 80:
            recommendations.append("Considere otimizar tratamento de endereços para melhorar taxa de enriquecimento")
        
        if enrichment_rate > 90:
            recommendations.append("Excelente taxa de enriquecimento! Sistema pronto para produção")
        
        quality_metrics = analysis['data_quality_analysis']
        
        if quality_metrics['complete_geocoding'] < quality_metrics.get('total_properties', 0) * 0.8:
            recommendations.append("Melhorar geocodificação de endereços")
        
        if quality_metrics['high_confidence_enrichment'] > quality_metrics.get('total_properties', 0) * 0.7:
            recommendations.append("Alta confiança nos dados - considere expandir uso do sistema")
        
        return recommendations
    
    async def _save_results(self, raw_properties: List[Dict], enriched_properties: List[Dict], 
                           final_report: Dict[str, Any]):
        """Salva resultados da demonstração"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar dados brutos
        with open(f'demo_raw_properties_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(raw_properties, f, indent=2, ensure_ascii=False)
        
        # Salvar dados enriquecidos
        with open(f'demo_enriched_properties_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(enriched_properties, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório final
        with open(f'demo_final_report_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Resultados salvos com timestamp {timestamp}")

async def main():
    """Função principal para executar a demonstração"""
    
    print("🏠 Sistema Completo de Captação e Enriquecimento de Imóveis")
    print("=" * 60)
    print("Esta demonstração mostra o pipeline completo:")
    print("1. Scraping básico de propriedades")
    print("2. Enriquecimento com APIs oficiais (Google Maps, IBGE, Prefeituras, etc.)")
    print("3. Análise de qualidade e cobertura dos dados")
    print("4. Geração de relatório final")
    print("=" * 60)
    
    demo = ComprehensiveIntegrationDemo()
    
    try:
        # Executar demonstração completa
        final_report = await demo.demonstrate_full_pipeline(max_properties=3)
        
        # Exibir sumário dos resultados
        print("\n📊 SUMÁRIO DOS RESULTADOS:")
        print(f"Propriedades processadas: {final_report['execution_summary']['total_properties_processed']}")
        print(f"Enriquecimentos bem-sucedidos: {final_report['execution_summary']['successful_enrichments']}")
        print(f"Tempo de execução: {final_report['execution_summary']['total_execution_time_seconds']:.2f}s")
        print(f"Fator de enriquecimento: {final_report['data_enhancement']['enhancement_factor']:.2f}x")
        
        print("\n✅ Demonstração concluída com sucesso!")
        print("📁 Arquivos de resultado salvos com timestamp")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
