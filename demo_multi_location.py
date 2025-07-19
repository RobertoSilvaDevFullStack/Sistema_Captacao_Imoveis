#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração do Sistema Multi-Localização
Mostra como usar os scrapers em diferentes cidades e estados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.olx_scraper import OLXScraper
from backend.config.location_config import LocationConfig
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_multi_location():
    """Demonstração de busca em múltiplas localizações"""
    print("🌍 DEMONSTRAÇÃO - SISTEMA MULTI-LOCALIZAÇÃO")
    print("=" * 60)
    
    # Mostrar localizações disponíveis
    config = LocationConfig()
    locations = config.get_location_display_names()
    
    print("📍 Localizações disponíveis:")
    for key, name in locations.items():
        location_info = config.get_location(key)
        if location_info:
            print(f"   {key:15} | {name}, {location_info.state}")
    
    print("\n" + "=" * 60)
    
    # Demonstrar URLs para diferentes localizações
    print("🔗 Exemplos de URLs geradas:")
    test_locations = ['rio_de_janeiro', 'sao_paulo', 'belo_horizonte', 'salvador']
    
    for location in test_locations:
        try:
            urls = config.build_urls(location, 'apartamentos')
            location_info = config.get_location(location)
            if location_info:
                print(f"\n📍 {location_info.name}:")
                print(f"   OLX: {urls['olx']}")
                print(f"   VivaReal: {urls['vivareal']}")
                print(f"   ZapImóveis: {urls['zapimoveis']}")
        except Exception as e:
            print(f"   Erro para {location}: {e}")
    
    print("\n" + "=" * 60)
    
    # Teste prático com OLX
    print("🚀 TESTE PRÁTICO - OLX em São Paulo")
    print("=" * 60)
    
    try:
        # Criar scraper para São Paulo
        scraper = OLXScraper(location='sao_paulo', property_type='apartamentos')
        
        # Mostrar configuração
        available = scraper.get_available_locations()
        print(f"✅ Scraper configurado para: {available.get('sao_paulo', 'São Paulo')}")
        
        # Executar busca limitada
        print("\n📝 Executando busca de teste (limitado a 5 propriedades)...")
        properties = scraper.scrape_properties(max_pages=1)
        
        print(f"\n✅ Resultado: {len(properties)} propriedades encontradas")
        
        if properties:
            print("\n📋 Primeiras 3 propriedades:")
            for i, prop in enumerate(properties[:3]):
                print(f"\n   {i+1}. {prop.get('title', 'Sem título')[:60]}...")
                print(f"      💰 {prop.get('price', 'N/A')[:30]}")
                print(f"      📍 {prop.get('location', 'N/A')[:40]}")
                print(f"      🔍 Busca: {prop.get('search_location', 'N/A')} - {prop.get('property_type_searched', 'N/A')}")
        
        scraper.close()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("💡 COMO USAR:")
    print("1. Escolha uma localização da lista disponível")
    print("2. Crie o scraper: scraper = OLXScraper(location='sao_paulo', property_type='apartamentos')")
    print("3. Execute: properties = scraper.scrape_properties()")
    print("4. Tipos disponíveis: 'apartamentos', 'casas', 'todos'")
    print("=" * 60)

def demo_property_types():
    """Demonstração de diferentes tipos de propriedades"""
    print("\n🏠 DEMONSTRAÇÃO - TIPOS DE PROPRIEDADES")
    print("=" * 60)
    
    config = LocationConfig()
    property_types = ['apartamentos', 'casas', 'todos']
    
    print("🔗 URLs para Rio de Janeiro com diferentes tipos:")
    for prop_type in property_types:
        try:
            urls = config.build_urls('rio_de_janeiro', prop_type)
            print(f"\n📝 {prop_type.upper()}:")
            print(f"   OLX: {urls['olx']}")
            print(f"   VivaReal: {urls['vivareal']}")
            print(f"   ZapImóveis: {urls['zapimoveis']}")
        except Exception as e:
            print(f"   Erro para {prop_type}: {e}")

def demo_add_custom_location():
    """Demonstração de como adicionar localização customizada"""
    print("\n🛠️ DEMONSTRAÇÃO - LOCALIZAÇÃO CUSTOMIZADA")
    print("=" * 60)
    
    from backend.config.location_config import Location
    
    config = LocationConfig()
    
    # Adicionar Vitória/ES como exemplo
    vitoria = Location(
        name='Vitória',
        state='Espírito Santo',
        state_code='es',
        olx_path='es/vitoria-e-regiao',
        vivareal_path='espirito-santo/vitoria',
        zapimoveis_path='es+vitoria'
    )
    
    config.add_custom_location('vitoria', vitoria)
    
    print("✅ Localização customizada adicionada: Vitória/ES")
    
    # Gerar URLs
    try:
        urls = config.build_urls('vitoria', 'apartamentos')
        print("\n🔗 URLs geradas para Vitória:")
        print(f"   OLX: {urls['olx']}")
        print(f"   VivaReal: {urls['vivareal']}")
        print(f"   ZapImóveis: {urls['zapimoveis']}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    demo_multi_location()
    demo_property_types()
    demo_add_custom_location()
