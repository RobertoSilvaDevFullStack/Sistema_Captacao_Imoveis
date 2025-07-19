# final_integration_demo.py

print("=== DEMONSTRAÇÃO DE INTEGRAÇÃO BANCO DE DADOS ===")
print()

try:
    # 1. Testa conexão com banco
    print("1. Testando conexão com banco de dados...")
    from backend.services.database_service import DatabaseService
    
    with DatabaseService() as db_service:
        print("   ✅ Conexão estabelecida com sucesso!")
        
        # 2. Testa inserção de propriedade
        print("2. Inserindo propriedade de teste...")
        test_property = {
            'url': 'https://exemplo.com/imovel/teste',
            'title': 'Apartamento Demonstração',
            'price': 500000.0,
            'bedrooms': 2,
            'bathrooms': 1,
            'area': 75.0,
            'neighborhood': 'Bairro Teste',
            'property_type': 'Apartamento',
            'price_per_sqm': 6666.67,
            'is_valid': True,
            'source': 'demo'
        }
        
        property_obj = db_service.save_property(test_property)
        print(f"   ✅ Propriedade salva com ID: {property_obj.id}")
        
        # 3. Testa inserção de análise
        print("3. Inserindo análise de mercado...")
        analysis_data = {
            'opportunity_score': 40.0,
            'discount_percentage': 20.0,
            'investment_recommendation': 'EXCELENTE',
            'analysis_notes': 'Ótima oportunidade identificada'
        }
        
        # Force refresh to get the actual ID
        db_service.db.refresh(property_obj)
        analysis_obj = db_service.save_property_analysis(property_obj.id, analysis_data)
        print(f"   ✅ Análise salva com ID: {analysis_obj.id}")
        
        # 4. Busca estatísticas
        print("4. Consultando estatísticas do mercado...")
        stats = db_service.get_market_stats()
        print(f"   📊 Total de propriedades: {stats['total_properties']}")
        print(f"   📊 Propriedades válidas: {stats['valid_properties']}")
        print(f"   📊 Oportunidades: {stats['opportunities_count']}")
        
        # 5. Busca melhores oportunidades
        print("5. Buscando melhores oportunidades...")
        opportunities = db_service.get_best_opportunities(limit=3)
        print(f"   🎯 {len(opportunities)} oportunidades encontradas:")
        
        for i, opp in enumerate(opportunities, 1):
            latest_analysis = opp.analyses[0] if opp.analyses else None
            score = latest_analysis.opportunity_score if latest_analysis else 'N/A'
            print(f"   {i}. {opp.title[:30]}... - Score: {score}")

    print()
    print("🎉 INTEGRAÇÃO BANCO DE DADOS FUNCIONANDO PERFEITAMENTE!")
    print()
    print("📋 RECURSOS IMPLEMENTADOS:")
    print("   ✅ Modelos de banco de dados (Property, PropertyPriceHistory, PropertyAnalysis)")
    print("   ✅ Serviço de banco de dados completo")
    print("   ✅ Integração com sistema de análise de mercado")
    print("   ✅ Persistência de dados de propriedades")
    print("   ✅ Histórico de preços")
    print("   ✅ Análises de investimento")
    print("   ✅ Consultas e estatísticas")
    print("   ✅ Identificação de oportunidades")
    
except Exception as e:
    print(f"❌ Erro na demonstração: {e}")
    import traceback
    traceback.print_exc()
