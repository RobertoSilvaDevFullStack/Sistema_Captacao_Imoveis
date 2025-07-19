#!/usr/bin/env python3
"""
Script de teste para verificar a API de busca
"""

import requests
import json
import time

def test_search_api():
    """Testa a API de busca de propriedades"""
    
    base_url = "http://localhost:5000"
    
    # Teste 1: ZapImóveis Rio de Janeiro
    print("🧪 Testando ZapImóveis Rio de Janeiro...")
    
    params = {
        'city': 'rio-de-janeiro',
        'property_type': 'apartamento', 
        'portal': 'zapimoveis',
        'max_results': 3
    }
    
    try:
        response = requests.get(f"{base_url}/api/properties/search", params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total encontrado: {data.get('total', 0)}")
            print(f"✅ Sucesso: {data.get('success', False)}")
            
            if data.get('data'):
                first_property = data['data'][0]
                print(f"✅ Primeira propriedade: {first_property.get('title', 'N/A')}")
                print(f"✅ Preço: {first_property.get('price', 'N/A')}")
            else:
                print("⚠️ Nenhuma propriedade encontrada")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Status dos scrapers
    print("🧪 Testando status dos scrapers...")
    
    try:
        response = requests.get(f"{base_url}/api/scrapers/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Scrapers disponíveis: {list(data.keys())}")
            
            for scraper, status in data.items():
                print(f"  - {scraper}: {status.get('status', 'N/A')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_search_api()
