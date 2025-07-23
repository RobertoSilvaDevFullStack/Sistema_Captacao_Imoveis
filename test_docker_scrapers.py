#!/usr/bin/env python3
"""
Teste rápido dos scrapers com Docker/Selenium Grid
"""

import asyncio
import time
from backend.scrapers.vivareal_scraper import VivaRealScraper
from backend.scrapers.olx_scraper import OLXScraper
from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper

async def test_docker_scrapers():
    """Testa scrapers com Docker/Selenium Grid"""
    
    print("🧪 Testando scrapers com Docker/Selenium Grid...")
    
    # Configuração para usar Selenium Grid
    selenium_config = {
        'use_remote': True,
        'remote_url': 'http://localhost:4444/wd/hub',
        'headless': True
    }
    
    scrapers = [
        ('VivaReal', VivaRealScraper),
        ('OLX', OLXScraper),
        ('ZapImóveis', ZapImoveisScraper)
    ]
    
    results = {}
    
    for name, scraper_class in scrapers:
        print(f"\n📊 Testando {name}...")
        try:
            # Criar instância do scraper
            scraper = scraper_class()
            
            # Configurar para usar Selenium Grid
            if hasattr(scraper, 'selenium_config'):
                scraper.selenium_config.update(selenium_config)
            
            # Testar busca simples
            start_time = time.time()
            
            # URLs de teste simplificadas
            if name == 'VivaReal':
                test_url = "https://www.vivareal.com.br/venda/sp/sao-paulo/"
            elif name == 'OLX':
                test_url = "https://sp.olx.com.br/imoveis/venda"  
            else:  # ZapImóveis
                test_url = "https://www.zapimoveis.com.br/venda/imoveis/sp+sao-paulo/"
            
            print(f"   🌐 URL: {test_url}")
            
            # Fazer uma busca simples
            properties = []
            async for prop in scraper.search_properties(
                city="São Paulo",
                max_results=5,
                property_type="apartamento"
            ):
                properties.append(prop)
                if len(properties) >= 3:  # Limitar para teste rápido
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            
            results[name] = {
                'success': True,
                'count': len(properties),
                'duration': duration,
                'sample': properties[0] if properties else None
            }
            
            print(f"   ✅ Encontrados: {len(properties)} imóveis")
            print(f"   ⏱️  Tempo: {duration:.2f}s")
            
            if properties:
                sample = properties[0]
                print(f"   🏠 Exemplo: {sample.get('title', 'N/A')[:50]}...")
                print(f"   💰 Preço: {sample.get('price', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            results[name] = {
                'success': False,
                'error': str(e),
                'count': 0,
                'duration': 0
            }
    
    # Relatório final
    print("\n" + "="*60)
    print("📋 RELATÓRIO FINAL - Docker/Selenium Grid")
    print("="*60)
    
    total_success = sum(1 for r in results.values() if r['success'])
    total_properties = sum(r['count'] for r in results.values())
    avg_duration = sum(r['duration'] for r in results.values()) / len(results)
    
    print(f"✅ Scrapers funcionais: {total_success}/{len(scrapers)} ({total_success/len(scrapers)*100:.1f}%)")
    print(f"🏠 Total de imóveis coletados: {total_properties}")
    print(f"⏱️  Tempo médio por scraper: {avg_duration:.2f}s")
    
    for name, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"\n{status} {name}:")
        if result['success']:
            print(f"   📊 Imóveis: {result['count']}")
            print(f"   ⏱️  Tempo: {result['duration']:.2f}s")
        else:
            print(f"   🚨 Erro: {result['error']}")
    
    print("\n🔧 Configuração Docker:")
    print(f"   🐳 Selenium Grid: http://localhost:4444")
    print(f"   🔴 Redis: localhost:6379")
    print(f"   🐘 PostgreSQL: localhost:5432")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_docker_scrapers())
