#!/usr/bin/env python3
# test_advanced_insights.py

import logging
import json
from backend.services.market_analyzer import MarketAnalyzer
from backend.services.advanced_market_insights import AdvancedMarketInsights

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_advanced_insights():
    """Testa as análises avançadas de mercado"""
    try:
        print("🚀 INICIANDO ANÁLISES AVANÇADAS DE MERCADO")
        print("=" * 80)
        
        # Carrega dados do analisador básico
        analyzer = MarketAnalyzer()
        if not analyzer.load_properties_data():
            print("❌ ERRO: Dados não encontrados. Execute primeiro test_market_analyzer.py")
            return
        
        # Executa análise básica para ter os dados
        analyzer.analyze_by_neighborhood()
        analyzer.detect_opportunities()
        analyzer.calculate_roi_metrics()
        analyzer.generate_market_trends()
        
        # Prepara dados para análise avançada
        advanced_data = {
            'properties': analyzer.properties,
            'neighborhood_analysis': analyzer.analysis_results.get('neighborhood_analysis', {}),
            'opportunities': analyzer.analysis_results.get('opportunities', []),
            'roi_metrics': analyzer.analysis_results.get('roi_metrics', {}),
            'market_trends': analyzer.analysis_results.get('market_trends', {})
        }
        
        # Inicializa análise avançada
        advanced_insights = AdvancedMarketInsights(advanced_data)
        
        # ÍNDICE DE AQUECIMENTO DO MERCADO
        print("\n🔥 ÍNDICE DE AQUECIMENTO DO MERCADO")
        print("=" * 60)
        
        heat_index = advanced_insights.calculate_market_heat_index()
        
        if heat_index:
            print("🌡️  TEMPERATURA DO MERCADO POR REGIÃO:")
            for i, (neighborhood, data) in enumerate(list(heat_index.items())[:5], 1):
                print(f"\n{i}. {neighborhood}")
                print(f"   🔥 Índice de Aquecimento: {data['heat_index']}/100")
                print(f"   📊 Classificação: {data['classification']}")
                print(f"   📈 Score Volume: {data['volume_score']}/100")
                print(f"   ⚖️  Score Estabilidade: {data['stability_score']}/100")
                print(f"   💰 Score Valor: {data['value_score']}/100")
                print(f"   🏠 Propriedades: {data['property_count']}")
        
        # ANÁLISE DE DIVERSIFICAÇÃO
        print("\n\n📊 ANÁLISE DE DIVERSIFICAÇÃO DE PORTFÓLIO")
        print("=" * 60)
        
        diversification = advanced_insights.analyze_investment_diversification()
        
        # Por tipo de propriedade
        if diversification.get('by_property_type'):
            print("🏠 DIVERSIFICAÇÃO POR TIPO DE PROPRIEDADE:")
            for prop_type, data in diversification['by_property_type'].items():
                print(f"\n• {prop_type}:")
                print(f"   💰 Investimento médio: R$ {data['avg_investment']:,.0f}")
                print(f"   📊 Faixa: R$ {data['min_investment']:,.0f} - R$ {data['max_investment']:,.0f}")
                print(f"   🏷️  Preço/m² médio: R$ {data['avg_price_per_sqm']:,.0f}")
                print(f"   ⚠️  Nível de risco: {data['risk_level']}")
                print(f"   💧 Score liquidez: {data['liquidity_score']}/100")
        
        # Por faixa de preço
        if diversification.get('by_price_range'):
            print(f"\n💰 DIVERSIFICAÇÃO POR FAIXA DE PREÇO:")
            range_labels = {
                'entry_level': 'ENTRADA (até R$ 400k)',
                'mid_range': 'MÉDIO (R$ 400k-800k)',
                'premium': 'PREMIUM (R$ 800k-1.5M)',
                'luxury': 'LUXO (acima R$ 1.5M)'
            }
            
            for range_name, data in diversification['by_price_range'].items():
                if data['count'] > 0:
                    print(f"\n• {range_labels.get(range_name, range_name)}:")
                    print(f"   🏠 Propriedades disponíveis: {data['count']}")
                    print(f"   📏 Área média: {data['avg_area']} m²")
                    print(f"   🗺️  Bairros disponíveis: {data['neighborhoods_available']}")
                    print(f"   🔄 Score diversidade: {data['diversity_score']}")
        
        # Recomendações de portfólio
        if diversification.get('portfolio_recommendations'):
            print(f"\n💼 ESTRATÉGIAS DE PORTFÓLIO RECOMENDADAS:")
            for strategy in diversification['portfolio_recommendations']:
                print(f"\n🎯 ESTRATÉGIA {strategy['strategy']}:")
                print(f"   📊 Alocação sugerida:")
                for asset, percentage in strategy['allocation'].items():
                    print(f"      - {asset}: {percentage}")
                print(f"   🎯 Foco: {strategy['price_range_focus']}")
                print(f"   📈 Yield esperado: {strategy['expected_yield']}")
                print(f"   ⚠️  Risco: {strategy['risk_level']}")
        
        # ANÁLISE COMPARATIVA
        print("\n\n🔍 ANÁLISE COMPARATIVA DETALHADA")
        print("=" * 60)
        
        comparative = advanced_insights.generate_comparative_analysis()
        
        # Melhores valores
        if comparative.get('best_value_properties'):
            print("💎 TOP 3 MELHORES VALORES (PREÇO vs QUALIDADE):")
            for i, prop_data in enumerate(comparative['best_value_properties'][:3], 1):
                prop = prop_data['property']
                print(f"\n{i}. {prop.get('property_type', 'N/A')} - {prop.get('neighborhood', 'N/A')}")
                print(f"   💵 Preço: R$ {prop.get('price', 0):,.0f}")
                print(f"   📏 Área: {prop.get('area', 0)} m² | 🛏️  Quartos: {prop.get('bedrooms', 0)}")
                print(f"   ⭐ Score Valor: {prop_data['value_score']}/100")
                print(f"   💰 Score Preço: {prop_data['price_score']}/100")
                print(f"   📐 Score Área: {prop_data['area_score']}/100")
        
        # Áreas com potencial de crescimento
        if comparative.get('growth_potential_areas'):
            print(f"\n📈 ÁREAS COM POTENCIAL DE CRESCIMENTO:")
            for i, area_data in enumerate(comparative['growth_potential_areas'][:3], 1):
                print(f"\n{i}. {area_data['neighborhood']}")
                print(f"   💰 Preço atual/m²: R$ {area_data['current_price_per_sqm']:,.0f}")
                print(f"   📊 Média do mercado: R$ {area_data['market_avg_price_per_sqm']:,.0f}")
                print(f"   🚀 Potencial de crescimento: {area_data['growth_potential_percentage']}%")
                print(f"   🏠 Propriedades disponíveis: {area_data['property_count']}")
        
        # Lacunas do mercado
        if comparative.get('market_gaps'):
            print(f"\n🔍 LACUNAS DE MERCADO IDENTIFICADAS:")
            for gap in comparative['market_gaps']:
                print(f"• {gap['description']}")
                print(f"   📊 Participação atual: {gap['market_share_percentage']}%")
                print(f"   💡 {gap['opportunity']}")
        
        # CENÁRIOS DE INVESTIMENTO
        print("\n\n💼 CENÁRIOS DE INVESTIMENTO")
        print("=" * 60)
        
        # Cenário de R$ 500k
        scenarios_500k = advanced_insights.calculate_investment_scenarios(500000)
        print("💰 ORÇAMENTO: R$ 500.000")
        
        if scenarios_500k.get('single_property_scenarios'):
            print("\n🎯 CENÁRIOS PROPRIEDADE ÚNICA:")
            for scenario in scenarios_500k['single_property_scenarios']:
                print(f"\n• {scenario['strategy']}:")
                print(f"   💡 {scenario['rationale']}")
                if scenario['properties']:
                    best_prop = scenario['properties'][0]
                    print(f"   🏆 Melhor opção: {best_prop.get('property_type', 'N/A')} - {best_prop.get('neighborhood', 'N/A')}")
                    print(f"   💵 Preço: R$ {best_prop.get('price', 0):,.0f}")
                    print(f"   📏 Área: {best_prop.get('area', 0)} m²")
        
        if scenarios_500k.get('portfolio_scenarios'):
            print(f"\n📊 CENÁRIOS PORTFÓLIO (R$ 500k):")
            for scenario in scenarios_500k['portfolio_scenarios']:
                print(f"\n• Foco em {scenario['range_label']}:")
                print(f"   💰 Faixa de preços: {scenario['price_range']}")
                print(f"   🏠 Propriedades possíveis: {scenario['possible_property_count']}")
                print(f"   💵 Investimento total: R$ {scenario['total_investment']:,.0f}")
                print(f"   💰 Sobra: R$ {scenario['remaining_budget']:,.0f}")
                print(f"   🔄 Diversificação: {scenario['diversification_benefit']}")
        
        # Cenário de R$ 1M
        scenarios_1m = advanced_insights.calculate_investment_scenarios(1000000)
        print(f"\n💰 ORÇAMENTO: R$ 1.000.000")
        if scenarios_1m.get('portfolio_scenarios'):
            for scenario in scenarios_1m['portfolio_scenarios']:
                if scenario['possible_property_count'] > 1:
                    print(f"\n• {scenario['range_label']}: {scenario['possible_property_count']} propriedades")
                    print(f"   💵 Investimento: R$ {scenario['total_investment']:,.0f}")
                    print(f"   🔄 Diversificação: {scenario['diversification_benefit']}")
        
        # EXPORTA RELATÓRIO AVANÇADO
        print("\n\n📄 EXPORTANDO INSIGHTS AVANÇADOS...")
        print("=" * 60)
        
        summary = advanced_insights.export_insights_summary()
        if summary:
            print("✅ Insights avançados exportados para 'advanced_market_insights.json'")
            
            # Estatísticas finais
            print(f"\n📊 ESTATÍSTICAS FINAIS:")
            print(f"• Regiões analisadas: {len(heat_index)}")
            print(f"• Oportunidades identificadas: {len(comparative.get('best_value_properties', []))}")
            print(f"• Áreas com potencial: {len(comparative.get('growth_potential_areas', []))}")
            print(f"• Lacunas de mercado: {len(comparative.get('market_gaps', []))}")
        
        print("\n" + "=" * 80)
        print("🎉 ANÁLISES AVANÇADAS CONCLUÍDAS COM SUCESSO!")
        print("📊 Relatórios disponíveis:")
        print("   • market_analysis_report.json (Análise básica)")
        print("   • advanced_market_insights.json (Insights avançados)")
        print("=" * 80)
        
    except Exception as e:
        logging.error(f"Erro durante análises avançadas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advanced_insights()
