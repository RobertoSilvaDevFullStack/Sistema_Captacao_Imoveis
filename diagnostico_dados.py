#!/usr/bin/env python3
"""
Script para testar se os dados estão sendo carregados corretamente
"""

import json
import requests
from datetime import datetime

print("🔍 DIAGNÓSTICO DOS DADOS REAIS")
print("=" * 50)

# 1. Verificar arquivo de dados
try:
    with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📂 Arquivo JSON: {len(data)} registros totais")
    
    # Contar dados válidos
    valid_data = [p for p in data if p.get('is_valid') and p.get('price')]
    print(f"✅ Dados válidos: {len(valid_data)} propriedades")
    
    if valid_data:
        sample = valid_data[0]
        print(f"🏠 Exemplo: {sample.get('neighborhood', 'N/A')} - R$ {sample.get('price', 0):,.2f}")
        print(f"📍 Área: {sample.get('area', 0)}m² - {sample.get('bedrooms', 0)} quartos")
    
except FileNotFoundError:
    print("❌ Arquivo processed_properties_data.json não encontrado!")
except Exception as e:
    print(f"❌ Erro ao ler arquivo: {e}")

print()

# 2. Testar API do backend
try:
    print("🔧 Testando Backend API...")
    
    # Teste health
    response = requests.get('http://localhost:8000/api/health', timeout=5)
    if response.status_code == 200:
        print("✅ Backend respondendo")
    else:
        print(f"❌ Backend erro: {response.status_code}")
    
    # Teste search
    search_data = {
        'city': 'sao-paulo',
        'propertyType': 'apartamento',
        'portal': 'zapimoveis',
        'maxResults': 5
    }
    
    response = requests.post('http://localhost:8000/api/search', 
                           json=search_data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            properties = result.get('data', [])
            print(f"✅ API retornou {len(properties)} propriedades")
            
            if properties:
                prop = properties[0]
                print(f"🏠 Primeira propriedade: {prop.get('title', 'N/A')}")
                print(f"💰 Preço: R$ {prop.get('price', 0):,.2f}")
                print(f"📍 Bairro: {prop.get('neighborhood', 'N/A')}")
            else:
                print("⚠️ API retornou lista vazia")
        else:
            print(f"❌ API erro: {result.get('error', 'Desconhecido')}")
    else:
        print(f"❌ API falhou: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Backend não está rodando ou não está acessível")
except Exception as e:
    print(f"❌ Erro ao testar API: {e}")

print()
print("🎯 DIAGNÓSTICO COMPLETO!")
print("=" * 50)
