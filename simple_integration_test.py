# simple_integration_test.py

import logging
import json
from utils.logging_config import setup_logging
from backend.services.database_service import DatabaseService

# Configura logging
setup_logging()

def test_database_integration():
    """Teste simples da integração com banco de dados"""
    logging.info("🚀 Testando integração simplificada com banco de dados...")
    
    try:
        # 1. Testa serviço de banco
        with DatabaseService() as db_service:
            logging.info("✅ Conexão com DatabaseService OK")
            
            # 2. Testa inserção de propriedade
            test_property_data = {
                'url': 'https://test.com/property/1',
                'title': 'Apartamento Teste',
                'price': 300000.0,
                'bedrooms': 2,
                'bathrooms': 1,
                'area': 65.0,
                'parking_spaces': 1,
                'address': 'Rua Teste, 123',
                'neighborhood': 'Bairro Teste',
                'property_type': 'Apartamento',
                'price_per_sqm': 4615.38,
                'is_valid': True,
                'description': 'Apartamento para teste',
                'source': 'vivareal'
            }
            
            logging.info("🔄 Salvando propriedade de teste...")
            property_obj = db_service.save_property(test_property_data)
            logging.info(f"✅ Propriedade salva com ID: {property_obj.id}")
            
            # 3. Testa inserção de análise
            test_analysis_data = {
                'opportunity_score': 35.5,
                'discount_percentage': 15.2,
                'estimated_rental_yield': 7.5,
                'payback_years': 13.3,
                'efficiency_score': 85.0,
                'investment_recommendation': 'BOM',
                'analysis_notes': 'Boa oportunidade no bairro teste',
                'market_avg_price_per_sqm': 5400.0,
                'savings_amount': 50000.0,
                'analysis_version': '1.0'
            }
            
            logging.info("🔄 Salvando análise de teste...")
            # Refresca o objeto para garantir que o ID esteja disponível
            db_service.db.refresh(property_obj)
            analysis_obj = db_service.save_property_analysis(property_obj.id, test_analysis_data)
            logging.info(f"✅ Análise salva com ID: {analysis_obj.id}")
            
            # 4. Testa busca de estatísticas
            logging.info("🔄 Buscando estatísticas...")
            stats = db_service.get_market_stats()
            logging.info("✅ Estatísticas obtidas:")
            logging.info(f"   • Total de propriedades: {stats['total_properties']}")
            logging.info(f"   • Propriedades válidas: {stats['valid_properties']}")
            logging.info(f"   • Oportunidades: {stats['opportunities_count']}")
            
            # 5. Testa busca de oportunidades
            logging.info("🔄 Buscando melhores oportunidades...")
            opportunities = db_service.get_best_opportunities(limit=5)
            logging.info(f"✅ {len(opportunities)} oportunidades encontradas")
            
            for opp in opportunities:
                logging.info(f"   • {opp.title} - Score: {opp.analyses[0].opportunity_score if opp.analyses else 'N/A'}")
            
            logging.info("🎉 TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
            return True
            
    except Exception as e:
        logging.error(f"❌ Erro no teste de integração: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_processed_data():
    """Testa integração com dados processados reais se disponíveis"""
    try:
        logging.info("🔄 Verificando dados processados...")
        
        with open('processed_properties.json', 'r', encoding='utf-8') as f:
            properties_data = json.load(f)
        
        logging.info(f"✅ {len(properties_data)} propriedades encontradas nos dados processados")
        
        with DatabaseService() as db_service:
            # Salva algumas propriedades dos dados reais
            saved_count = 0
            for prop_data in properties_data[:5]:  # Apenas 5 para teste
                try:
                    db_property_data = {
                        'url': prop_data.get('url', f'test-{saved_count}'),
                        'title': prop_data.get('titulo', 'Sem título'),
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
                        'source': 'vivareal'
                    }
                    
                    property_obj = db_service.save_property(db_property_data)
                    saved_count += 1
                    
                except Exception as e:
                    logging.warning(f"Erro ao salvar propriedade: {e}")
            
            logging.info(f"✅ {saved_count} propriedades dos dados reais salvas")
            
            # Atualiza estatísticas
            stats = db_service.get_market_stats()
            logging.info(f"📊 Total no banco após inserção: {stats['total_properties']} propriedades")
        
    except FileNotFoundError:
        logging.warning("⚠️ Arquivo processed_properties.json não encontrado. Pulando teste com dados reais.")
    except Exception as e:
        logging.error(f"❌ Erro no teste com dados reais: {e}")

if __name__ == "__main__":
    # Executa testes
    success = test_database_integration()
    
    if success:
        test_with_processed_data()
        logging.info("🎯 TESTES CONCLUÍDOS!")
    else:
        logging.error("💥 Falha nos testes!")
        exit(1)
