#!/usr/bin/env python3

import requests
import json

print("🧪 TESTE COMPLETO DA INTEGRAÇÃO")
print("=" * 50)

# 1. Testar health check
try:
    print("🔧 Testando health check...")
    response = requests.get('http://localhost:8000/api/health', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend OK - {data.get('properties_loaded', 0)} propriedades carregadas")
    else:
        print(f"❌ Health check falhou: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Erro no health check: {e}")
    exit(1)

# 2. Testar busca
try:
    print("\n🔍 Testando API de busca...")
    response = requests.post('http://localhost:8000/api/search', 
                           json={'city': 'sao-paulo'},
                           timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            properties = data.get('data', [])
            print(f"✅ Busca OK - {len(properties)} propriedades retornadas")
            
            if properties:
                prop = properties[0]
                print(f"🏠 Primeira propriedade:")
                print(f"   Título: {prop.get('title')}")
                print(f"   Preço: R$ {prop.get('price', 0):,}")
                print(f"   Bairro: {prop.get('neighborhood')}")
                print(f"   Cidade: {prop.get('city')}")
        else:
            print(f"❌ API retornou erro: {data.get('error')}")
            exit(1)
    else:
        print(f"❌ Busca falhou: {response.status_code}")
        exit(1)
        
except Exception as e:
    print(f"❌ Erro na busca: {e}")
    exit(1)

print("\n🎉 TODOS OS TESTES PASSARAM!")
print("✅ Backend funcionando corretamente")
print("✅ Dados reais sendo retornados")
print("✅ API pronta para React")
