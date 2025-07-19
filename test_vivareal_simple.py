#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do VivaReal Simples - APIs diretas sem Cloudflare
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scrapers.vivareal_simple import VivaRealSimple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

def test_vivareal_simple():
    """Testa o scraper VivaReal simplificado"""
    
    print("🔍 Testando VivaReal Simple (APIs diretas)")
    print("=" * 50)
    
    scraper = VivaRealSimple()
    
    try:
        # Teste 1: Rio de Janeiro - Apartamentos
        print("\n📍 Testando Rio de Janeiro - Apartamentos")
        properties = scraper.scrape_properties(
            location='rio-de-janeiro',
            property_type='apartamento',
            max_results=10
        )
        
        print(f"✅ Encontradas {len(properties)} propriedades")
        
        # Mostrar algumas propriedades
        for i, prop in enumerate(properties[:3], 1):
            print(f"\n{i}. {prop.get('title', 'Sem título')}")
            print(f"   💰 Preço: {prop.get('price', 'N/A')}")
            print(f"   📍 Local: {prop.get('location', 'N/A')}")
            print(f"   📐 Área: {prop.get('area', 'N/A')}")
            print(f"   🔗 URL: {prop.get('url', 'N/A')[:80]}...")
        
        # Teste 2: São Paulo - Casas
        print("\n\n📍 Testando São Paulo - Casas")
        sp_properties = scraper.scrape_properties(
            location='sao-paulo',
            property_type='casa',
            max_results=5
        )
        
        print(f"✅ Encontradas {len(sp_properties)} propriedades em SP")
        
        if sp_properties:
            prop = sp_properties[0]
            print(f"\n📋 Exemplo de São Paulo:")
            print(f"   Título: {prop.get('title', 'N/A')}")
            print(f"   Preço: {prop.get('price', 'N/A')}")
        
        # Estatísticas finais
        total_properties = len(properties) + len(sp_properties)
        print(f"\n📊 Total geral: {total_properties} propriedades")
        
        if total_properties > 0:
            print("✅ VivaReal Simple funcionando!")
            return True
        else:
            print("❌ Nenhuma propriedade encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        scraper.close()

def test_location_variations():
    """Testa variações de localização"""
    
    print("\n🌍 Testando variações de localização")
    print("=" * 40)
    
    scraper = VivaRealSimple()
    
    locations = [
        'rio-de-janeiro',
        'sao-paulo', 
        'belo-horizonte',
        'brasilia',
        'salvador'
    ]
    
    results = {}
    
    for location in locations:
        try:
            print(f"\n🔍 Testando {location}...")
            props = scraper.scrape_properties(
                location=location,
                property_type='apartamento',
                max_results=3
            )
            results[location] = len(props)
            print(f"   ✅ {len(props)} propriedades")
            
        except Exception as e:
            print(f"   ❌ Erro em {location}: {e}")
            results[location] = 0
    
    print(f"\n📊 Resultados por cidade:")
    for city, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {city}: {count} propriedades")
    
    scraper.close()
    
    working_cities = sum(1 for count in results.values() if count > 0)
    print(f"\n🏆 Cidades funcionando: {working_cities}/{len(locations)}")
    
    return working_cities > 0

if __name__ == "__main__":
    print("🚀 Iniciando testes VivaReal Simple")
    
    # Teste principal
    success1 = test_vivareal_simple()
    
    # Teste de localização
    success2 = test_location_variations()
    
    if success1 or success2:
        print("\n🎉 Pelo menos um teste passou - VivaReal Simple viável!")
    else:
        print("\n😞 Todos os testes falharam - APIs podem estar indisponíveis")
