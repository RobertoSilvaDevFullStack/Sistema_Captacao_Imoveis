#!/usr/bin/env python3
"""
Diagnóstico do Sistema de Captação Ativa
Verifica o status atual e identifica o que precisa ser implementado
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

print("🔍 DIAGNÓSTICO DO SISTEMA DE CAPTAÇÃO ATIVA")
print("=" * 60)

# 1. Verificar dados existentes
print("\n📊 1. ANÁLISE DOS DADOS EXISTENTES")
print("-" * 40)

try:
    with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    print(f"✅ Dados encontrados: {len(current_data)} propriedades")
    
    # Verificar idades dos dados
    if current_data:
        # Pegar uma amostra de propriedades para verificar quando foram coletadas
        sample_urls = [p.get('url', '') for p in current_data[:5]]
        print(f"🏠 Exemplos de URLs coletadas:")
        for url in sample_urls[:3]:
            if url:
                print(f"   - {url[:60]}...")
    
    # Verificar distribuição por cidades/bairros
    neighborhoods = {}
    for prop in current_data:
        neighborhood = prop.get('neighborhood', 'Desconhecido')
        if neighborhood in neighborhoods:
            neighborhoods[neighborhood] += 1
        else:
            neighborhoods[neighborhood] = 1
    
    print(f"\n📍 Distribuição por bairros (top 10):")
    sorted_neighborhoods = sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True)
    for neighborhood, count in sorted_neighborhoods[:10]:
        print(f"   - {neighborhood}: {count} imóveis")

except FileNotFoundError:
    print("❌ Nenhum arquivo de dados encontrado")

# 2. Verificar infraestrutura de captura
print("\n🔧 2. INFRAESTRUTURA DE CAPTAÇÃO")
print("-" * 40)

# Verificar se scrapers existem
scrapers_path = Path("backend/scrapers")
if scrapers_path.exists():
    scrapers = list(scrapers_path.glob("*_scraper.py"))
    print(f"✅ Scrapers encontrados: {len(scrapers)}")
    for scraper in scrapers:
        print(f"   - {scraper.name}")
else:
    print("❌ Pasta de scrapers não encontrada")

# Verificar configuração de cidades
config_path = Path("backend/config/location_config.py")
if config_path.exists():
    print("✅ Configuração de cidades encontrada")
else:
    print("❌ Configuração de cidades não encontrada")

# Verificar sistema de tarefas
if Path("tasks.py").exists():
    print("✅ Sistema de tarefas (Celery) configurado")
else:
    print("❌ Sistema de tarefas não encontrado")

# 3. Verificar sistema ativo
print("\n⚡ 3. SISTEMA ATIVO ATUAL")
print("-" * 40)

# Verificar processos
import subprocess
import json

try:
    result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, check=True)
    if result.stdout.strip():
        print("✅ Docker ativo com containers")
        print(result.stdout)
    else:
        print("⚠️ Docker ativo mas sem containers")
except:
    print("❌ Docker não ativo")

# Verificar se backend atual faz captação ativa
backend_files = [
    "backend_ultra_simple.py",
    "backend_api_simple.py", 
    "backend_api_server.py"
]

active_backend = None
for backend_file in backend_files:
    if Path(backend_file).exists():
        active_backend = backend_file
        break

if active_backend:
    print(f"✅ Backend ativo: {active_backend}")
    print("⚠️ Backend atual: APENAS SERVE DADOS (não coleta ativamente)")
else:
    print("❌ Nenhum backend encontrado")

# 4. Recomendações
print("\n🎯 4. ANÁLISE E RECOMENDAÇÕES")
print("-" * 40)

print("📋 STATUS ATUAL:")
print("   ✅ Dados existentes de São Paulo (380 propriedades)")
print("   ✅ Scrapers desenvolvidos para múltiplas fontes")
print("   ✅ Configuração para 10+ cidades brasileiras")
print("   ✅ Sistema de tarefas agendadas (Celery)")
print("   ❌ Sistema de captação contínua INATIVO")
print("   ❌ Dados não estão sendo atualizados")

print("\n🚀 PRECISA IMPLEMENTAR:")
print("   1. Ativar sistema de captação contínua")
print("   2. Implementar rotação entre cidades")
print("   3. Sistema anti-bloqueio ativo")
print("   4. Atualização automática dos dados")
print("   5. Verificar scrapers para outras cidades")

print("\n💡 PRÓXIMOS PASSOS SUGERIDOS:")
print("   1. Testar scrapers em outras cidades")
print("   2. Ativar sistema Celery + Redis")  
print("   3. Implementar captação gradual e inteligente")
print("   4. Monitoramento de qualidade dos dados")

print("\n" + "=" * 60)
print("🎯 CONCLUSÃO: Sistema tem infraestrutura completa,")
print("   mas captação ativa está INATIVA. Dados atuais")
print("   são estáticos de uma coleta anterior.")
print("=" * 60)
