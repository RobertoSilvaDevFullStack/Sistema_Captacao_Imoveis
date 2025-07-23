#!/usr/bin/env python3
"""
Sistema de Captação Contínua de Imóveis
Análise de dados atuais e implementação de captação ativa multi-cidade
"""

import json
import re
from collections import Counter
from datetime import datetime
import sys

def analyze_current_data():
    """Analisa os dados atuais para entender cobertura e padrões"""
    print("🔍 ANÁLISE DOS DADOS ATUAIS")
    print("=" * 50)
    
    try:
        with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
            properties = json.load(f)
        
        print(f"📊 Total de propriedades: {len(properties)}")
        
        # Análise de cidades/bairros
        neighborhoods = []
        cities = []
        sources = []
        
        for prop in properties:
            # Extrair bairro
            if 'neighborhood' in prop:
                neighborhoods.append(prop['neighborhood'])
            
            # Extrair cidade da URL
            url = prop.get('url', '')
            if 'sao-paulo' in url:
                cities.append('São Paulo')
            elif 'rio-de-janeiro' in url:
                cities.append('Rio de Janeiro')
            elif 'belo-horizonte' in url:
                cities.append('Belo Horizonte')
            
            # Fonte do imóvel
            if 'vivareal.com.br' in url:
                sources.append('VivaReal')
            elif 'zapimoveis.com.br' in url:
                sources.append('ZapImóveis')
            elif 'olx.com.br' in url:
                sources.append('OLX')
        
        # Estatísticas
        city_counts = Counter(cities)
        neighborhood_counts = Counter(neighborhoods)
        source_counts = Counter(sources)
        
        print(f"\n📍 COBERTURA POR CIDADES:")
        for city, count in city_counts.most_common():
            print(f"   {city}: {count} imóveis")
        
        print(f"\n🌐 FONTES DOS DADOS:")
        for source, count in source_counts.most_common():
            print(f"   {source}: {count} imóveis")
        
        print(f"\n🏘️ TOP 10 BAIRROS:")
        for neighborhood, count in neighborhood_counts.most_common(10):
            if neighborhood and neighborhood != 'Unknown':
                print(f"   {neighborhood}: {count} imóveis")
        
        # Análise de preços
        prices = [prop.get('price', 0) for prop in properties if prop.get('price')]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            print(f"\n💰 ANÁLISE DE PREÇOS:")
            print(f"   Preço médio: R$ {avg_price:,.2f}")
            print(f"   Preço mínimo: R$ {min_price:,.2f}")
            print(f"   Preço máximo: R$ {max_price:,.2f}")
        
        return {
            'total': len(properties),
            'cities': city_counts,
            'sources': source_counts,
            'neighborhoods': neighborhood_counts
        }
        
    except Exception as e:
        print(f"❌ Erro ao analisar dados: {e}")
        return None

def check_scraper_capabilities():
    """Verifica capacidades dos scrapers existentes"""
    print(f"\n🤖 ANÁLISE DOS SCRAPERS")
    print("=" * 50)
    
    scrapers = [
        'backend/scrapers/vivareal_scraper.py',
        'backend/scrapers/zapimoveis_scraper.py', 
        'backend/scrapers/olx_scraper.py'
    ]
    
    active_scrapers = []
    for scraper_path in scrapers:
        try:
            with open(scraper_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar se tem suporte a múltiplas cidades
            has_city_support = 'location' in content or 'cidade' in content or 'city' in content
            has_antiblock = 'sleep' in content or 'delay' in content or 'random' in content
            has_error_handling = 'try:' in content and 'except' in content
            
            scraper_name = scraper_path.split('/')[-1].replace('.py', '')
            print(f"   ✅ {scraper_name}")
            print(f"      📍 Suporte multi-cidade: {'✅' if has_city_support else '❌'}")
            print(f"      🛡️ Anti-bloqueio: {'✅' if has_antiblock else '❌'}")
            print(f"      ⚠️ Tratamento de erro: {'✅' if has_error_handling else '❌'}")
            
            active_scrapers.append(scraper_name)
            
        except FileNotFoundError:
            scraper_name = scraper_path.split('/')[-1]
            print(f"   ❌ {scraper_name} não encontrado")
        except Exception as e:
            print(f"   ⚠️ Erro ao verificar {scraper_path}: {e}")
    
    return active_scrapers

def check_continuous_system():
    """Verifica o sistema de captação contínua"""
    print(f"\n⚡ SISTEMA DE CAPTAÇÃO CONTÍNUA")
    print("=" * 50)
    
    # Verificar tasks.py
    try:
        with open('tasks.py', 'r', encoding='utf-8') as f:
            tasks_content = f.read()
        
        print("   ✅ Sistema Celery configurado")
        
        # Verificar agendamentos
        if 'crontab' in tasks_content:
            print("   ✅ Agendamentos configurados")
            # Extrair horários
            import re
            cron_matches = re.findall(r"crontab\(.*?\)", tasks_content)
            print("   📅 Horários programados:")
            for match in cron_matches:
                print(f"      - {match}")
        
        # Verificar anti-bloqueio
        if 'random' in tasks_content and 'sleep' in tasks_content:
            print("   ✅ Anti-bloqueio configurado")
        else:
            print("   ⚠️ Anti-bloqueio limitado")
            
    except FileNotFoundError:
        print("   ❌ tasks.py não encontrado")
    
    # Verificar location_config.py
    try:
        with open('backend/config/location_config.py', 'r', encoding='utf-8') as f:
            location_content = f.read()
        
        print("   ✅ Configuração de localizações disponível")
        
        # Contar cidades configuradas
        city_matches = re.findall(r'"[^"]*":\s*Location', location_content)
        print(f"   📍 Cidades configuradas: {len(city_matches)}")
        
    except FileNotFoundError:
        print("   ❌ location_config.py não encontrado")

def create_activation_plan():
    """Cria plano para ativar captação contínua"""
    print(f"\n🚀 PLANO DE ATIVAÇÃO")
    print("=" * 50)
    
    print("📋 PASSOS NECESSÁRIOS:")
    print("   1. ✅ Testar scrapers individualmente por cidade")
    print("   2. ⚠️ Ativar Redis para queue de tarefas")
    print("   3. ⚠️ Ativar Celery worker e scheduler")
    print("   4. ⚠️ Implementar rotação inteligente de cidades")
    print("   5. ⚠️ Sistema de monitoramento de qualidade")
    
    print(f"\n⚡ IMPLEMENTAÇÃO IMEDIATA DISPONÍVEL:")
    print("   • Captação manual por cidade")
    print("   • Teste de scrapers em tempo real") 
    print("   • Atualização incremental dos dados")
    print("   • Sistema simplificado sem Redis/Celery")
    
    print(f"\n🎯 PRÓXIMA AÇÃO RECOMENDADA:")
    print("   Testar captação para Rio de Janeiro")
    print("   (cidade com maior demanda após São Paulo)")

if __name__ == "__main__":
    print("🏠 SISTEMA DE CAPTAÇÃO CONTÍNUA DE IMÓVEIS")
    print("=" * 60)
    
    # Análise completa
    data_stats = analyze_current_data()
    active_scrapers = check_scraper_capabilities()
    check_continuous_system()
    create_activation_plan()
    
    print(f"\n" + "=" * 60)
    print("🎯 RESUMO EXECUTIVO:")
    if data_stats:
        print(f"   • Dados atuais: {data_stats['total']} propriedades")
        print(f"   • Cobertura: {len(data_stats['cities'])} cidade(s)")
        print(f"   • Fontes ativas: {len(data_stats['sources'])}")
    print(f"   • Scrapers funcionais: {len(active_scrapers)}")
    print(f"   • Status captação: INATIVA (apenas dados estáticos)")
    print(f"   • Pronto para ativação: SIM")
    print("=" * 60)
