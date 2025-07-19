#!/usr/bin/env python3
# backend/demos/complete_scraper_demo.py

"""
Demo completo dos scrapers OLX, ZapImóveis e VivaReal
Este script demonstra que todos os scrapers estão funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import json
import time
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_demo.log'),
        logging.StreamHandler()
    ]
)

def test_individual_scrapers():
    """Testa cada scraper individualmente"""
    print("="*60)
    print("🏠 DEMO COMPLETO DOS SCRAPERS DE IMÓVEIS")
    print("="*60)
    
    # Configurações de teste
    test_config = {
        'max_properties': 2,  # Limitado para demo
        'max_pages': 1,
        'location': 'rio-de-janeiro'
    }
    
    scrapers_results = {}
    
    # 1. TESTE VIVAREAL SCRAPER
    print("\n1️⃣ TESTANDO VIVAREAL SCRAPER")
    print("-" * 40)
    
    try:
        from scrapers.vivareal_scraper import VivaRealScraper
        
        vr_scraper = VivaRealScraper()
        vr_url = "https://www.vivareal.com.br/venda/sp/sao-paulo/"
        
        print(f"🔍 Buscando em: {vr_url}")
        vr_properties = vr_scraper.scrape_properties(
            vr_url, 
            max_properties=test_config['max_properties']
        )
        
        if vr_properties:
            print(f"✅ VivaReal: {len(vr_properties)} propriedades encontradas")
            scrapers_results['vivareal'] = vr_properties
            
            # Mostra primeira propriedade
            prop = vr_properties[0]
            print(f"   📍 Exemplo: {prop.get('title', 'N/A')[:50]}...")
            print(f"   💰 Preço: {prop.get('price', 'N/A')}")
        else:
            print("❌ VivaReal: Nenhuma propriedade encontrada")
            scrapers_results['vivareal'] = []
        
        vr_scraper.close()
        
    except Exception as e:
        print(f"❌ Erro no VivaReal: {e}")
        scrapers_results['vivareal'] = []
    
    # 2. TESTE OLX SCRAPER
    print("\n2️⃣ TESTANDO OLX SCRAPER")
    print("-" * 40)
    
    try:
        from scrapers.olx_scraper import OLXScraper
        
        olx_scraper = OLXScraper()
        olx_url = "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro"
        
        print(f"🔍 Buscando em: {olx_url}")
        olx_properties = olx_scraper.scrape_properties(
            olx_url,
            max_properties=test_config['max_properties'],
            max_pages=test_config['max_pages']
        )
        
        if olx_properties:
            print(f"✅ OLX: {len(olx_properties)} propriedades encontradas")
            scrapers_results['olx'] = olx_properties
            
            # Mostra primeira propriedade
            prop = olx_properties[0]
            print(f"   📍 Exemplo: {prop.get('title', 'N/A')[:50]}...")
            print(f"   💰 Preço: {prop.get('price', 'N/A')}")
        else:
            print("❌ OLX: Nenhuma propriedade encontrada")
            scrapers_results['olx'] = []
        
        olx_scraper.close()
        
    except Exception as e:
        print(f"❌ Erro no OLX: {e}")
        scrapers_results['olx'] = []
    
    # 3. TESTE ZAPIMOVEIS SCRAPER
    print("\n3️⃣ TESTANDO ZAPIMOVEIS SCRAPER")
    print("-" * 40)
    
    try:
        from scrapers.zapimoveis_scraper import ZapImoveisScraper
        
        zap_scraper = ZapImoveisScraper()
        zap_url = "https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/"
        
        print(f"🔍 Buscando em: {zap_url}")
        zap_properties = zap_scraper.scrape_properties(
            zap_url,
            max_properties=test_config['max_properties'],
            max_pages=test_config['max_pages']
        )
        
        if zap_properties:
            print(f"✅ ZapImóveis: {len(zap_properties)} propriedades encontradas")
            scrapers_results['zapimoveis'] = zap_properties
            
            # Mostra primeira propriedade
            prop = zap_properties[0]
            print(f"   📍 Exemplo: {prop.get('title', 'N/A')[:50]}...")
            print(f"   💰 Preço: {prop.get('price', 'N/A')}")
        else:
            print("❌ ZapImóveis: Nenhuma propriedade encontrada")
            scrapers_results['zapimoveis'] = []
        
        zap_scraper.close()
        
    except Exception as e:
        print(f"❌ Erro no ZapImóveis: {e}")
        scrapers_results['zapimoveis'] = []
    
    return scrapers_results

def test_multi_scraper_service():
    """Testa o serviço multi-scraper"""
    print("\n4️⃣ TESTANDO MULTI-SCRAPER SERVICE")
    print("-" * 40)
    
    try:
        from services.multi_scraper_service import MultiScraperService
        
        service = MultiScraperService()
        results = {}  # Inicializa results
        
        print("🔧 Inicializando scrapers...")
        service.initialize_scrapers()
        
        if service.scrapers:
            print(f"✅ {len(service.scrapers)} scrapers inicializados: {list(service.scrapers.keys())}")
            
            # Teste rápido
            print("🔍 Executando scraping multi-portal (modo demo)...")
            results = service.scrape_all_portals(
                location="rio-de-janeiro",
                max_properties_per_portal=1  # Muito limitado para demo
            )
            
            if results:
                total = sum(len(props) for props in results.values())
                print(f"✅ Multi-scraper: {total} propriedades coletadas no total")
                
                for portal, props in results.items():
                    print(f"   📊 {portal}: {len(props)} propriedades")
            else:
                print("❌ Multi-scraper: Nenhum resultado")
        else:
            print("❌ Nenhum scraper foi inicializado")
        
        service.close_all_scrapers()
        return results
        
    except Exception as e:
        print(f"❌ Erro no Multi-scraper: {e}")
        return {}

def generate_report(individual_results, multi_results):
    """Gera relatório final do demo"""
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DO DEMO")
    print("="*60)
    
    # Relatório individual
    print("\n🔍 TESTES INDIVIDUAIS:")
    total_individual = 0
    for scraper, properties in individual_results.items():
        count = len(properties)
        total_individual += count
        status = "✅ FUNCIONANDO" if count > 0 else "❌ SEM DADOS"
        print(f"   {scraper.upper()}: {count} propriedades - {status}")
    
    # Relatório multi-scraper
    print(f"\n🔧 MULTI-SCRAPER SERVICE:")
    if multi_results:
        total_multi = sum(len(props) for props in multi_results.values())
        print(f"   Total coletado: {total_multi} propriedades")
        print("   Status: ✅ FUNCIONANDO")
    else:
        print("   Status: ❌ NÃO TESTADO/ERRO")
    
    # Status geral
    print(f"\n🎯 STATUS GERAL:")
    working_scrapers = len([s for s, p in individual_results.items() if len(p) > 0])
    total_scrapers = len(individual_results)
    
    print(f"   Scrapers funcionais: {working_scrapers}/{total_scrapers}")
    print(f"   Total de propriedades coletadas: {total_individual}")
    
    if working_scrapers == total_scrapers:
        print("   🎉 TODOS OS SCRAPERS ESTÃO FUNCIONANDO!")
    elif working_scrapers > 0:
        print("   ⚠️ ALGUNS SCRAPERS PRECISAM DE AJUSTES")
    else:
        print("   🚨 NENHUM SCRAPER ESTÁ FUNCIONANDO")
    
    # Salva relatório
    report_data = {
        'demo_timestamp': datetime.now().isoformat(),
        'individual_tests': {
            scraper: {
                'properties_count': len(properties),
                'working': len(properties) > 0,
                'sample_data': properties[0] if properties else None
            }
            for scraper, properties in individual_results.items()
        },
        'multi_scraper_test': {
            'working': bool(multi_results),
            'total_properties': sum(len(props) for props in multi_results.values()) if multi_results else 0,
            'portals_tested': list(multi_results.keys()) if multi_results else []
        },
        'summary': {
            'working_scrapers': working_scrapers,
            'total_scrapers': total_scrapers,
            'total_properties_collected': total_individual
        }
    }
    
    with open('scraper_demo_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Relatório detalhado salvo em 'scraper_demo_report.json'")

def main():
    """Função principal do demo"""
    start_time = datetime.now()
    
    print("🚀 Iniciando demo completo dos scrapers...")
    print(f"⏰ Horário de início: {start_time.strftime('%H:%M:%S')}")
    
    try:
        # Testa scrapers individualmente
        individual_results = test_individual_scrapers()
        
        # Testa multi-scraper service
        multi_results = test_multi_scraper_service()
        
        # Gera relatório final
        generate_report(individual_results, multi_results)
        
    except Exception as e:
        print(f"❌ Erro durante o demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n⏱️ Demo concluído em {duration}")
        print("🏁 Fim do demo!")

if __name__ == "__main__":
    main()
