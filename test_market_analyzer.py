#!/usr/bin/env python3
# test_market_analyzer.py

import logging
import json
from backend.services.market_analyzer import MarketAnalyzer

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_market_analysis():
    """Testa o sistema completo de análise de mercado"""
    try:
        print("🏠 INICIANDO ANÁLISE DE MERCADO IMOBILIÁRIO")
        print("=" * 80)
        
        # Inicializa o analisador
        analyzer = MarketAnalyzer()
        
        # Carrega dados processados
        if not analyzer.load_properties_data():
            print("❌ ERRO: Não foi possível carregar os dados das propriedades")
            print("💡 Execute primeiro o test_data_processor.py para gerar os dados")
            return
        
        print(f"✅ Dados carregados: {len(analyzer.properties)} propriedades válidas")
        print("-" * 80)
        
        # ANÁLISE POR BAIRRO
        print("\n📍 ANÁLISE POR BAIRRO")
        print("=" * 50)
        
        neighborhood_analysis = analyzer.analyze_by_neighborhood()
        
        if neighborhood_analysis:
            print(f"Bairros analisados: {len(neighborhood_analysis)}")
            print("\n🏆 TOP 5 BAIRROS MAIS CAROS:")
            
            for i, (neighborhood, data) in enumerate(list(neighborhood_analysis.items())[:5], 1):
                print(f"{i}. {neighborhood}")
                print(f"   • Preço médio: R$ {data['avg_price']:,.0f}")
                print(f"   • Preço/m²: R$ {data.get('avg_price_per_sqm', 0):,.0f}")
                print(f"   • Propriedades: {data['total_properties']}")
                print(f"   • Tipos: {', '.join([f'{k}({v})' for k, v in data['property_types'].most_common(2)])}")
        else:
            print("⚠️  Dados insuficientes para análise por bairro")
        
        # DETECÇÃO DE OPORTUNIDADES
        print("\n\n💰 OPORTUNIDADES DE INVESTIMENTO")
        print("=" * 50)
        
        opportunities = analyzer.detect_opportunities(discount_threshold=0.10)  # 10% desconto
        
        if opportunities:
            print(f"Oportunidades encontradas: {len(opportunities)}")
            print("\n🎯 TOP 5 MELHORES OPORTUNIDADES:")
            
            for i, opp in enumerate(opportunities[:5], 1):
                prop = opp['property']
                print(f"\n{i}. {prop.get('property_type', 'Propriedade')} - {prop.get('neighborhood', 'N/A')}")
                print(f"   💵 Preço: R$ {prop.get('price', 0):,.0f}")
                print(f"   📏 Área: {prop.get('area', 0)} m²")
                print(f"   💸 Desconto: {opp['discount_percentage']}%")
                print(f"   💰 Economia: R$ {opp['savings_amount']:,.0f}")
                print(f"   ⭐ Score: {opp['opportunity_score']}/50")
                print(f"   📊 Preço/m²: R$ {opp['property_price_per_sqm']:,.0f} (vs R$ {opp['market_avg_price_per_sqm']:,.0f} média)")
        else:
            print("⚠️  Nenhuma oportunidade significativa detectada")
        
        # ANÁLISE DE ROI
        print("\n\n📈 ANÁLISE DE ROI E RENTABILIDADE")
        print("=" * 50)
        
        roi_metrics = analyzer.calculate_roi_metrics()
        
        if roi_metrics and roi_metrics['rent_yield_analysis']:
            print("🏅 TOP 5 MELHORES INVESTIMENTOS PARA RENDA:")
            
            for i, roi_data in enumerate(roi_metrics['rent_yield_analysis'][:5], 1):
                prop = roi_data['property']
                print(f"\n{i}. {prop.get('property_type', 'Propriedade')} - {prop.get('neighborhood', 'N/A')}")
                print(f"   💵 Investimento: R$ {prop.get('price', 0):,.0f}")
                print(f"   🏠 Aluguel estimado: R$ {roi_data['estimated_monthly_rent']:,.0f}/mês")
                print(f"   📊 Yield anual: {roi_data['rental_yield_percent']}%")
                print(f"   ⏱️  Payback: {roi_data['payback_years']} anos" if roi_data['payback_years'] else "   ⏱️  Payback: N/A")
                print(f"   ⭐ Score eficiência: {roi_data['efficiency_score']}/100")
                print(f"   💡 Recomendação: {roi_data['recommendation']}")
        
        # TENDÊNCIAS DE MERCADO
        print("\n\n📊 TENDÊNCIAS DE MERCADO")
        print("=" * 50)
        
        market_trends = analyzer.generate_market_trends()
        
        if market_trends:
            # Distribuição de preços
            price_dist = market_trends.get('price_distribution', {})
            if price_dist:
                print("💰 DISTRIBUIÇÃO DE PREÇOS:")
                print(f"   • Preço médio: R$ {price_dist.get('average_price', 0):,.0f}")
                print(f"   • Preço mediano: R$ {price_dist.get('median_price', 0):,.0f}")
                print(f"   • Faixa: R$ {price_dist.get('price_range', {}).get('min', 0):,.0f} - R$ {price_dist.get('price_range', {}).get('max', 0):,.0f}")
                
                brackets = price_dist.get('price_brackets', {})
                print(f"   • Econômicas (até 400k): {brackets.get('budget', 0)} propriedades")
                print(f"   • Médio padrão (400k-800k): {brackets.get('mid_range', 0)} propriedades")
                print(f"   • Premium (800k-1.5M): {brackets.get('premium', 0)} propriedades")
                print(f"   • Luxo (>1.5M): {brackets.get('luxury', 0)} propriedades")
            
            # Análise de área
            area_analysis = market_trends.get('area_analysis', {})
            if area_analysis:
                print(f"\n📏 ANÁLISE DE ÁREA:")
                print(f"   • Área média: {area_analysis.get('average_area', 0)} m²")
                print(f"   • Área mediana: {area_analysis.get('median_area', 0)} m²")
            
            # Tipos de propriedade
            prop_trends = market_trends.get('property_type_trends', {})
            if prop_trends:
                print(f"\n🏠 TENDÊNCIAS POR TIPO:")
                for prop_type, data in prop_trends.items():
                    if prop_type != 'N/A':
                        print(f"   • {prop_type}: {data['count']} unidades, R$ {data['price_per_sqm']:,.0f}/m²")
        
        # RELATÓRIO COMPLETO
        print("\n\n📋 GERANDO RELATÓRIO COMPLETO...")
        print("=" * 50)
        
        comprehensive_report = analyzer.generate_comprehensive_report()
        
        # Salva relatório
        if analyzer.save_report(comprehensive_report):
            print("✅ Relatório completo salvo em 'market_analysis_report.json'")
        
        # Mostra resumo executivo
        exec_summary = comprehensive_report.get('executive_summary', {})
        if exec_summary:
            print(f"\n📊 RESUMO EXECUTIVO:")
            print(f"   • {exec_summary.get('market_overview', 'N/A')}")
            print(f"   • Faixa de preços: {exec_summary.get('price_range', 'N/A')}")
            print(f"   • Preço médio: {exec_summary.get('average_price', 'N/A')}")
            print(f"   • Área média: {exec_summary.get('average_area', 'N/A')}")
            print(f"   • Oportunidades: {exec_summary.get('total_opportunities', 0)}")
            print(f"   • Atividade do mercado: {exec_summary.get('market_activity', 'N/A')}")
        
        # Mostra recomendações
        recommendations = comprehensive_report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMENDAÇÕES ESTRATÉGICAS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "=" * 80)
        print("🎉 ANÁLISE DE MERCADO CONCLUÍDA COM SUCESSO!")
        print("📄 Relatório detalhado disponível em 'market_analysis_report.json'")
        print("=" * 80)
        
    except Exception as e:
        logging.error(f"Erro durante análise de mercado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_market_analysis()
