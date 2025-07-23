#!/usr/bin/env python3
"""
Sistema de Captação Ativa Multi-Cidade
Teste em tempo real de captação de imóveis
"""

import json
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.append('backend')
sys.path.append('.')

def test_multi_city_scraping():
    """Testa captação em múltiplas cidades"""
    print("🌍 TESTE DE CAPTAÇÃO MULTI-CIDADE")
    print("=" * 60)
    
    # Listar cidades disponíveis
    try:
        from backend.config.location_config import LocationConfig
        config = LocationConfig()
        locations = config.list_locations()
        
        print(f"📍 Cidades configuradas: {len(locations)}")
        for loc in locations[:10]:  # Mostrar primeiras 10
            display_name = config.get_display_name(loc)
            print(f"   • {loc} ({display_name})")
        
        return locations
        
    except ImportError as e:
        print(f"❌ Erro ao importar LocationConfig: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return []

def test_olx_scraper_simple(city='rio_de_janeiro', max_properties=5):
    """Teste simples do scraper OLX para uma cidade"""
    print(f"\n🏠 TESTE OLX - {city.upper()}")
    print("-" * 40)
    
    try:
        from backend.scrapers.olx_scraper import OLXScraper
        
        print(f"⚡ Iniciando scraper para {city}...")
        scraper = OLXScraper(location=city, property_type='apartamentos')
        
        # Verificar se cidade está disponível
        available_locations = scraper.get_available_locations()
        if city not in scraper.location_config.list_locations():
            print(f"❌ Cidade {city} não está nas configurações")
            print(f"📍 Cidades disponíveis: {list(available_locations.keys())[:5]}...")
            return False
        
        print(f"✅ Configuração OK para {city}")
        
        # Tentar captar alguns imóveis
        print(f"🔄 Captando até {max_properties} imóveis...")
        
        start_time = time.time()
        properties = scraper.scrape_properties(max_properties)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if properties and len(properties) > 0:
            print(f"✅ Sucesso! Captados {len(properties)} imóveis em {duration:.1f}s")
            
            # Mostrar sample
            for i, prop in enumerate(properties[:3]):
                price = prop.get('price', 'N/A')
                neighborhood = prop.get('neighborhood', 'N/A')
                print(f"   {i+1}. {neighborhood} - R$ {price}")
            
            return properties
        else:
            print(f"⚠️ Nenhum imóvel encontrado (em {duration:.1f}s)")
            return []
        
    except ImportError as e:
        print(f"❌ Erro ao importar OLXScraper: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante scraping: {e}")
        return False

def test_existing_data_cities():
    """Analisa cidades nos dados existentes"""
    print(f"\n📊 ANÁLISE DOS DADOS ATUAIS")
    print("-" * 40)
    
    try:
        with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
            properties = json.load(f)
        
        print(f"📋 Total: {len(properties)} propriedades")
        
        # Análise de cidades nas URLs
        cities_found = {}
        sources = {}
        
        for prop in properties:
            url = prop.get('url', '')
            
            # Identificar cidade pela URL
            if 'sao-paulo' in url:
                city = 'São Paulo'
            elif 'rio-de-janeiro' in url:
                city = 'Rio de Janeiro'
            elif 'belo-horizonte' in url:
                city = 'Belo Horizonte'
            else:
                city = 'Outra'
            
            cities_found[city] = cities_found.get(city, 0) + 1
            
            # Identificar fonte
            if 'vivareal.com.br' in url:
                source = 'VivaReal'
            elif 'zapimoveis.com.br' in url:
                source = 'ZapImóveis'
            elif 'olx.com.br' in url:
                source = 'OLX'
            else:
                source = 'Outra'
            
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n📍 Distribuição por cidades:")
        for city, count in sorted(cities_found.items(), key=lambda x: x[1], reverse=True):
            print(f"   {city}: {count} imóveis")
        
        print(f"\n🌐 Distribuição por fonte:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"   {source}: {count} imóveis")
        
        return cities_found, sources
        
    except FileNotFoundError:
        print("❌ Arquivo processed_properties_data.json não encontrado")
        return {}, {}
    except Exception as e:
        print(f"❌ Erro ao analisar dados: {e}")
        return {}, {}

def create_active_scraping_demo():
    """Demonstração de captação ativa"""
    print(f"\n🚀 DEMONSTRAÇÃO DE CAPTAÇÃO ATIVA")
    print("-" * 60)
    
    # Testar cidades prioritárias
    priority_cities = [
        'rio_de_janeiro',
        'sao_paulo', 
        'belo_horizonte'
    ]
    
    results = {}
    
    for city in priority_cities:
        print(f"\n🎯 Testando {city}...")
        
        try:
            properties = test_olx_scraper_simple(city, max_properties=3)
            
            if properties and len(properties) > 0:
                results[city] = {
                    'status': 'sucesso',
                    'count': len(properties),
                    'sample': properties[0] if properties else None
                }
                print(f"✅ {city}: {len(properties)} imóveis captados")
            else:
                results[city] = {
                    'status': 'sem_dados',
                    'count': 0,
                    'sample': None
                }
                print(f"⚠️ {city}: Nenhum imóvel captado")
                
        except Exception as e:
            results[city] = {
                'status': 'erro',
                'count': 0,
                'error': str(e)
            }
            print(f"❌ {city}: Erro - {e}")
        
        # Pausa entre cidades para não sobrecarregar
        time.sleep(2)
    
    return results

if __name__ == "__main__":
    print("🏠 SISTEMA DE CAPTAÇÃO ATIVA - TESTE MULTI-CIDADE")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Analisar dados atuais
    current_cities, current_sources = test_existing_data_cities()
    
    # 2. Testar configuração multi-cidade
    available_locations = test_multi_city_scraping()
    
    # 3. Se disponível, testar captação ativa
    if available_locations:
        print(f"\n🎯 INICIANDO TESTES DE CAPTAÇÃO ATIVA...")
        active_results = create_active_scraping_demo()
        
        # Resumo dos resultados
        print(f"\n📋 RESUMO DOS TESTES ATIVOS:")
        print("-" * 40)
        for city, result in active_results.items():
            status = result['status']
            count = result['count']
            
            if status == 'sucesso':
                print(f"   ✅ {city}: {count} imóveis captados")
            elif status == 'sem_dados':
                print(f"   ⚠️ {city}: Scraper OK, mas sem dados")
            else:
                print(f"   ❌ {city}: Erro técnico")
    
    print(f"\n" + "=" * 70)
    print("🎯 CONCLUSÃO:")
    print(f"   • Dados atuais: {sum(current_cities.values())} imóveis")
    print(f"   • Cidades nos dados: {len([c for c in current_cities if current_cities[c] > 0])}")
    print(f"   • Cidades configuradas: {len(available_locations) if available_locations else 'N/A'}")
    print(f"   • Captação ativa: {'TESTADA' if available_locations else 'PRECISA CONFIGURAÇÃO'}")
    print("=" * 70)
