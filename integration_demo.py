# integration_demo.py

import logging
import json
from datetime import datetime
from typing import List, Dict

from utils.logging_config import setup_logging
from backend.services.database_service import DatabaseService
from backend.services.market_analyzer import MarketAnalyzer
from backend.services.advanced_market_insights import AdvancedMarketInsights

# Configura logging
setup_logging()

class MarketDatabaseIntegration:
    """Integração entre análise de mercado e banco de dados"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.advanced_insights = None  # Será inicializado após análise
    
    def save_analysis_to_database(self, properties_data: List[Dict]):
        """Salva dados de propriedades e análises no banco"""
        logging.info("🔄 Iniciando integração com banco de dados...")
        
        with DatabaseService() as db_service:
            saved_properties = []
            saved_analyses = []
            
            # 1. Salva propriedades no banco
            logging.info(f"📊 Salvando {len(properties_data)} propriedades...")
            for prop_data in properties_data:
                try:
                    # Converte dados para formato do banco
                    db_property_data = self._convert_to_db_format(prop_data)
                    
                    # Salva propriedade
                    property_obj = db_service.save_property(db_property_data)
                    saved_properties.append(property_obj)
                    
                    logging.info(f"✅ Propriedade salva: {property_obj.title[:50]}... (ID: {property_obj.id})")
                    
                except Exception as e:
                    logging.error(f"❌ Erro ao salvar propriedade {prop_data.get('titulo', 'N/A')}: {e}")
            
            # 2. Carrega dados no market analyzer e executa análise
            logging.info("🔍 Carregando dados no analisador...")
            self.market_analyzer.properties = saved_properties
            
            logging.info("🔍 Executando análise de mercado...")
            analysis_result = self.market_analyzer.analyze_by_neighborhood()
            
            # 3. Salva análises individuais no banco
            logging.info("💾 Salvando análises individuais...")
            for opportunity in analysis_result.get('opportunities', []):
                try:
                    # Busca propriedade no banco pela URL
                    property_obj = db_service.get_property_by_url(opportunity['url'])
                    
                    if property_obj:
                        # Prepara dados da análise
                        analysis_data = {
                            'opportunity_score': opportunity['opportunity_score'],
                            'discount_percentage': opportunity['discount_percentage'],
                            'estimated_rental_yield': opportunity.get('estimated_rental_yield', 0),
                            'payback_years': opportunity.get('payback_years', 0),
                            'efficiency_score': opportunity.get('efficiency_score', 0),
                            'investment_recommendation': self._get_recommendation_level(opportunity['opportunity_score']),
                            'analysis_notes': f"Desconto de {opportunity['discount_percentage']:.1f}% identificado",
                            'market_avg_price_per_sqm': opportunity.get('market_avg_price_sqm', 0),
                            'savings_amount': opportunity.get('savings_amount', 0),
                            'analysis_version': '1.0'
                        }
                        
                        # Salva análise
                        analysis_obj = db_service.save_property_analysis(property_obj.id, analysis_data)
                        saved_analyses.append(analysis_obj)
                        
                        logging.info(f"✅ Análise salva para propriedade ID {property_obj.id}: Score {opportunity['opportunity_score']}")
                    
                except Exception as e:
                    logging.error(f"❌ Erro ao salvar análise: {e}")
            
            # 4. Gera estatísticas finais
            stats = db_service.get_market_stats()
            
            logging.info("📈 Integração concluída!")
            logging.info(f"   • Propriedades salvas: {len(saved_properties)}")
            logging.info(f"   • Análises salvas: {len(saved_analyses)}")
            logging.info(f"   • Total no banco: {stats['total_properties']} propriedades")
            logging.info(f"   • Oportunidades: {stats['opportunities_count']}")
            
            return {
                'saved_properties': len(saved_properties),
                'saved_analyses': len(saved_analyses),
                'market_stats': stats,
                'analysis_result': analysis_result
            }
    
    def _convert_to_db_format(self, prop_data: Dict) -> Dict:
        """Converte dados de propriedade para formato do banco"""
        return {
            'url': prop_data.get('url', ''),
            'title': prop_data.get('titulo', ''),
            'raw_price': prop_data.get('preco_original', ''),
            'raw_bedrooms': prop_data.get('quartos_original', ''),
            'raw_bathrooms': prop_data.get('banheiros_original', ''),
            'raw_area': prop_data.get('area_original', ''),
            'raw_parking_spaces': prop_data.get('vagas_original', ''),
            'raw_address': prop_data.get('endereco', ''),
            'price': prop_data.get('preco', 0),
            'bedrooms': prop_data.get('quartos', 0),
            'bathrooms': prop_data.get('banheiros', 0),
            'area': prop_data.get('area', 0),
            'parking_spaces': prop_data.get('vagas', 0),
            'address': prop_data.get('endereco', ''),
            'neighborhood': prop_data.get('bairro', ''),
            'property_type': prop_data.get('tipo', 'Apartamento'),
            'price_per_sqm': prop_data.get('preco_por_m2', 0),
            'is_valid': prop_data.get('dados_validos', False),
            'description': prop_data.get('descricao', ''),
            'amenities': prop_data.get('comodidades', []),
            'source': 'vivareal'
        }
    
    def _get_recommendation_level(self, opportunity_score: float) -> str:
        """Determina nível de recomendação baseado no score"""
        if opportunity_score >= 40:
            return 'EXCELENTE'
        elif opportunity_score >= 30:
            return 'BOM'
        elif opportunity_score >= 20:
            return 'MODERADO'
        else:
            return 'BAIXO'
    
    def generate_database_report(self):
        """Gera relatório do banco de dados"""
        logging.info("📊 Gerando relatório do banco de dados...")
        
        with DatabaseService() as db_service:
            # Estatísticas gerais
            stats = db_service.get_market_stats()
            
            # Melhores oportunidades
            opportunities = db_service.get_best_opportunities(limit=10)
            
            # Estatísticas por bairros principais
            neighborhood_details = []
            for neighborhood_info in stats.get('top_neighborhoods', [])[:5]:
                neighborhood_stats = db_service.get_neighborhood_stats(neighborhood_info['neighborhood'])
                neighborhood_details.append(neighborhood_stats)
            
            report = {
                'report_date': datetime.now().isoformat(),
                'market_overview': stats,
                'top_opportunities': [
                    {
                        'id': prop.id,
                        'title': prop.title,
                        'neighborhood': prop.neighborhood,
                        'price': prop.price,
                        'price_per_sqm': prop.price_per_sqm,
                        'latest_analysis': prop.analyses[0].to_dict() if prop.analyses else None
                    }
                    for prop in opportunities
                ],
                'neighborhood_analysis': neighborhood_details
            }
            
            # Salva relatório
            with open('database_market_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logging.info("✅ Relatório salvo em 'database_market_report.json'")
            
            # Mostra resumo
            logging.info("📈 RESUMO DO RELATÓRIO:")
            logging.info(f"   • Total de propriedades: {stats['total_properties']}")
            logging.info(f"   • Propriedades válidas: {stats['valid_properties']}")
            logging.info(f"   • Preço médio: R$ {stats['avg_price']:,.2f}")
            logging.info(f"   • Preço médio por m²: R$ {stats['avg_price_per_sqm']:,.2f}")
            logging.info(f"   • Oportunidades identificadas: {stats['opportunities_count']}")
            logging.info(f"   • Melhores oportunidades: {len(opportunities)}")
            
            return report

def main():
    """Demonstração da integração completa"""
    logging.info("🚀 DEMONSTRAÇÃO: Integração Market Analyzer + Banco de Dados")
    
    try:
        # 1. Carrega dados processados
        logging.info("📂 Carregando dados processados...")
        with open('processed_properties.json', 'r', encoding='utf-8') as f:
            properties_data = json.load(f)
        
        logging.info(f"✅ {len(properties_data)} propriedades carregadas")
        
        # 2. Executa integração
        integration = MarketDatabaseIntegration()
        result = integration.save_analysis_to_database(properties_data)
        
        # 3. Gera relatório final
        report = integration.generate_database_report()
        
        logging.info("🎉 INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
        logging.info("📄 Arquivos gerados:")
        logging.info("   • database_market_report.json - Relatório do banco de dados")
        
        return True
        
    except FileNotFoundError:
        logging.error("❌ Arquivo 'processed_properties.json' não encontrado!")
        logging.info("💡 Execute primeiro o data_processor.py para gerar os dados processados")
        return False
        
    except Exception as e:
        logging.error(f"❌ Erro na integração: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
