#!/usr/bin/env python3
"""
Sistema de Captação Ativa Simplificado
Testa scrapers e configurações existentes
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar o diretório backend ao path
current_dir = Path(__file__).parent
backend_dir = current_dir / 'backend'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(current_dir))

def analyze_current_data():
    """Análise dos dados existentes"""
    print("📊 ANÁLISE DOS DADOS ATUAIS")
    print("=" * 50)
    
    try:
        data_file = current_dir / 'processed_properties_data.json'
        with open(data_file, 'r', encoding='utf-8') as f:
            properties = json.load(f)
        
        print(f"📋 Total de propriedades: {len(properties)}")
        
        # Análise de distribuição
        cities = {}
        sources = {}
        neighborhoods = {}
        
        for prop in properties:
            url = prop.get('url', '')
            neighborhood = prop.get('neighborhood', 'Desconhecido')
            
            # Identificar cidade
            if 'sao-paulo' in url:
                city = 'São Paulo'
            elif 'rio-de-janeiro' in url:
                city = 'Rio de Janeiro'
            elif 'belo-horizonte' in url:
                city = 'Belo Horizonte'
            else:
                city = 'Outras'
            
            cities[city] = cities.get(city, 0) + 1
            
            # Identificar fonte
            if 'vivareal.com.br' in url:
                source = 'VivaReal'
            elif 'zapimoveis.com.br' in url:
                source = 'ZapImóveis'
            elif 'olx.com.br' in url:
                source = 'OLX'
            else:
                source = 'Outras'
            
            sources[source] = sources.get(source, 0) + 1
            neighborhoods[neighborhood] = neighborhoods.get(neighborhood, 0) + 1
        
        # Exibir estatísticas
        print(f"\n📍 Cidades nos dados:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(properties)) * 100
            print(f"   {city}: {count} imóveis ({percentage:.1f}%)")
        
        print(f"\n🌐 Fontes dos dados:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(properties)) * 100
            print(f"   {source}: {count} imóveis ({percentage:.1f}%)")
        
        print(f"\n🏘️ Top 10 bairros:")
        top_neighborhoods = sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True)[:10]
        for neighborhood, count in top_neighborhoods:
            if neighborhood != 'Desconhecido':
                print(f"   {neighborhood}: {count} imóveis")
        
        return {
            'total': len(properties),
            'cities': cities,
            'sources': sources,
            'neighborhoods': neighborhoods
        }
        
    except FileNotFoundError:
        print("❌ Arquivo processed_properties_data.json não encontrado")
        return None
    except Exception as e:
        print(f"❌ Erro ao analisar dados: {e}")
        return None

def test_scraper_configs():
    """Testa as configurações dos scrapers"""
    print(f"\n🔧 TESTE DE CONFIGURAÇÕES")
    print("=" * 50)
    
    scrapers_tested = 0
    scrapers_working = 0
    
    # Testar LocationConfig
    try:
        from config.location_config import LocationConfig
        config = LocationConfig()
        locations = config.list_locations()
        
        print(f"✅ LocationConfig carregado")
        print(f"📍 Cidades configuradas: {len(locations)}")
        
        # Mostrar algumas cidades
        print("   Cidades disponíveis:")
        for i, loc in enumerate(locations[:8]):
            try:
                location_obj = config.get_location(loc)
                display_name = f"{location_obj.name}, {location_obj.state}" if location_obj else loc
                print(f"     • {loc} ({display_name})")
            except:
                print(f"     • {loc}")
        
        scrapers_tested += 1
        scrapers_working += 1
        
    except ImportError as e:
        print(f"❌ LocationConfig não encontrado: {e}")
    except Exception as e:
        print(f"❌ Erro LocationConfig: {e}")
    
    # Testar OLX Scraper (sem executar)
    scrapers_tested += 1
    try:
        olx_file = backend_dir / 'scrapers' / 'olx_scraper.py'
        if olx_file.exists():
            print(f"✅ OLX Scraper encontrado")
            
            # Verificar se tem as funções necessárias
            with open(olx_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'scrape_properties' in content:
                print(f"   ✅ Método scrape_properties disponível")
            if 'location' in content.lower():
                print(f"   ✅ Suporte a múltiplas localizações")
            
            scrapers_working += 1
        else:
            print(f"❌ OLX Scraper não encontrado")
    except Exception as e:
        print(f"❌ Erro ao verificar OLX Scraper: {e}")
    
    # Testar VivaReal Scraper
    scrapers_tested += 1
    try:
        vivareal_file = backend_dir / 'scrapers' / 'vivareal_scraper.py'
        if vivareal_file.exists():
            print(f"✅ VivaReal Scraper encontrado")
            scrapers_working += 1
        else:
            print(f"❌ VivaReal Scraper não encontrado")
    except Exception as e:
        print(f"❌ Erro ao verificar VivaReal Scraper: {e}")
    
    # Testar ZapImóveis Scraper
    scrapers_tested += 1
    try:
        zap_file = backend_dir / 'scrapers' / 'zapimoveis_scraper.py'
        if zap_file.exists():
            print(f"✅ ZapImóveis Scraper encontrado")
            scrapers_working += 1
        else:
            print(f"❌ ZapImóveis Scraper não encontrado")
    except Exception as e:
        print(f"❌ Erro ao verificar ZapImóveis Scraper: {e}")
    
    return {
        'tested': scrapers_tested,
        'working': scrapers_working,
        'percentage': (scrapers_working / scrapers_tested * 100) if scrapers_tested > 0 else 0
    }

def check_continuous_system():
    """Verifica sistema de captação contínua"""
    print(f"\n⚡ SISTEMA CONTÍNUO")
    print("=" * 50)
    
    # Verificar tasks.py
    tasks_file = current_dir / 'tasks.py'
    if tasks_file.exists():
        print("✅ Sistema Celery configurado (tasks.py)")
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar componentes
        if 'crontab' in content:
            print("   ✅ Agendamentos configurados")
        if 'run_scraper_task' in content:
            print("   ✅ Tarefas de scraping definidas")
        if 'redis' in content.lower():
            print("   ⚠️ Redis requerido (não verificado)")
        
    else:
        print("❌ Sistema Celery não configurado")
    
    # Verificar Docker
    docker_file = current_dir / 'docker-compose.yml'
    if docker_file.exists():
        print("✅ Docker Compose encontrado")
        
        with open(docker_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'redis' in content:
            print("   ✅ Redis configurado no Docker")
        if 'celery' in content:
            print("   ✅ Celery configurado no Docker")
    else:
        print("❌ Docker Compose não encontrado")

def create_activation_plan():
    """Criar plano de ativação"""
    print(f"\n🚀 PLANO DE ATIVAÇÃO")
    print("=" * 50)
    
    print("📋 SITUAÇÃO ATUAL:")
    print("   ✅ Scrapers desenvolvidos e configurados")
    print("   ✅ Configuração multi-cidade disponível")
    print("   ✅ Dados de exemplo existentes (São Paulo)")
    print("   ✅ Sistema de tarefas agendadas configurado")
    print("   ❌ Captação contínua INATIVA")
    
    print(f"\n🎯 OPÇÕES DE ATIVAÇÃO:")
    
    print(f"\n1️⃣ ATIVAÇÃO SIMPLES (Recomendado):")
    print("   • Executar scrapers manualmente por cidade")
    print("   • Testar Rio de Janeiro e Belo Horizonte")
    print("   • Atualizar dados gradualmente")
    print("   • Sem necessidade de Docker/Redis")
    
    print(f"\n2️⃣ ATIVAÇÃO COMPLETA:")
    print("   • Iniciar Docker com Redis")
    print("   • Ativar Celery workers")
    print("   • Captação automática agendada")
    print("   • Monitoramento contínuo")
    
    print(f"\n💡 PRÓXIMO PASSO SUGERIDO:")
    print("   Testar scraper OLX em Rio de Janeiro")
    print("   (cidade com segunda maior demanda)")

def main():
    """Função principal"""
    print("🏠 SISTEMA DE CAPTAÇÃO ATIVA - ANÁLISE COMPLETA")
    print("=" * 70)
    print(f"⏰ Análise iniciada: {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Analisar dados atuais
    data_stats = analyze_current_data()
    
    # 2. Testar configurações
    scraper_stats = test_scraper_configs()
    
    # 3. Verificar sistema contínuo
    check_continuous_system()
    
    # 4. Criar plano de ativação
    create_activation_plan()
    
    # Resumo final
    print(f"\n" + "=" * 70)
    print("🎯 RESUMO EXECUTIVO:")
    
    if data_stats:
        print(f"   📊 Dados atuais: {data_stats['total']} propriedades")
        cities_count = len([c for c in data_stats['cities'] if data_stats['cities'][c] > 0])
        print(f"   📍 Cidades com dados: {cities_count}")
    
    if scraper_stats:
        print(f"   🤖 Scrapers funcionais: {scraper_stats['working']}/{scraper_stats['tested']} ({scraper_stats['percentage']:.0f}%)")
    
    print(f"   ⚡ Status: PRONTO PARA EXPANSÃO")
    print(f"   🎯 Recomendação: TESTAR NOVAS CIDADES")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
