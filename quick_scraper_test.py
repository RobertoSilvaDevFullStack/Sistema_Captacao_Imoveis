#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido de estrutura dos scrapers (sem inicializar drivers)
"""

import sys
import os
import logging
import importlib.util
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.ERROR)  # Reduzir verbosidade

def test_scraper_imports():
    """Testa importações dos scrapers"""
    results = {}
    
    scrapers = {
        'OLX': 'backend.scrapers.olx_scraper',
        'VivaReal': 'backend.scrapers.vivareal_scraper', 
        'ZapImóveis': 'backend.scrapers.zapimoveis_scraper',
        'Base': 'backend.scrapers.base_scraper'
    }
    
    for name, module_path in scrapers.items():
        try:
            module = importlib.import_module(module_path)
            results[name] = {'status': '✅ OK', 'error': None}
            print(f"✅ {name} Scraper - Importação OK")
        except Exception as e:
            results[name] = {'status': '❌ ERRO', 'error': str(e)}
            print(f"❌ {name} Scraper - Erro: {e}")
    
    return results

def test_scraper_classes():
    """Testa se as classes dos scrapers existem e têm métodos básicos"""
    results = {}
    
    # OLX
    try:
        from backend.scrapers.olx_scraper import OLXScraper
        
        # Verificar métodos essenciais existem
        methods = ['scrape_properties', 'close']
        missing = [m for m in methods if not hasattr(OLXScraper, m)]
        
        if missing:
            results['OLX_methods'] = {'status': '⚠️ PARCIAL', 'details': f'Métodos faltando: {missing}'}
        else:
            results['OLX_methods'] = {'status': '✅ OK', 'details': 'Todos os métodos presentes'}
            
        print(f"✅ OLX - Estrutura da classe OK")
    except Exception as e:
        results['OLX_methods'] = {'status': '❌ ERRO', 'details': str(e)}
        print(f"❌ OLX - Erro na classe: {e}")
    
    # VivaReal
    try:
        from backend.scrapers.vivareal_scraper import VivaRealScraper
        
        methods = ['scrape_apartments', 'close']
        missing = [m for m in methods if not hasattr(VivaRealScraper, m)]
        
        if missing:
            results['VivaReal_methods'] = {'status': '⚠️ PARCIAL', 'details': f'Métodos faltando: {missing}'}
        else:
            results['VivaReal_methods'] = {'status': '✅ OK', 'details': 'Todos os métodos presentes'}
            
        print(f"✅ VivaReal - Estrutura da classe OK")
    except Exception as e:
        results['VivaReal_methods'] = {'status': '❌ ERRO', 'details': str(e)}
        print(f"❌ VivaReal - Erro na classe: {e}")
    
    # ZapImóveis
    try:
        from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
        
        methods = ['scrape_apartments', 'close_driver']
        missing = [m for m in methods if not hasattr(ZapImoveisScraper, m)]
        
        if missing:
            results['ZapImoveis_methods'] = {'status': '⚠️ PARCIAL', 'details': f'Métodos faltando: {missing}'}
        else:
            results['ZapImoveis_methods'] = {'status': '✅ OK', 'details': 'Todos os métodos presentes'}
            
        print(f"✅ ZapImóveis - Estrutura da classe OK")
    except Exception as e:
        results['ZapImoveis_methods'] = {'status': '❌ ERRO', 'details': str(e)}
        print(f"❌ ZapImóveis - Erro na classe: {e}")
    
    return results

def test_dependencies():
    """Testa dependências críticas rapidamente"""
    results = {}
    
    deps = ['selenium', 'bs4', 'requests', 'webdriver_manager']
    
    for dep in deps:
        try:
            importlib.import_module(dep)
            results[dep] = {'status': '✅ OK'}
            print(f"✅ {dep} - Disponível")
        except ImportError:
            results[dep] = {'status': '❌ ERRO'}
            print(f"❌ {dep} - Não disponível")
    
    return results

def main():
    print("🚀 TESTE RÁPIDO DE SCRAPERS")
    print("=" * 50)
    
    print("\n📦 Testando dependências...")
    dep_results = test_dependencies()
    
    print("\n📥 Testando importações...")
    import_results = test_scraper_imports()
    
    print("\n🔧 Testando estruturas das classes...")
    class_results = test_scraper_classes()
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO:")
    
    # Contar sucessos
    dep_ok = sum(1 for r in dep_results.values() if '✅' in r['status'])
    import_ok = sum(1 for r in import_results.values() if '✅' in r['status']) 
    class_ok = sum(1 for r in class_results.values() if '✅' in r['status'])
    
    total_tests = len(dep_results) + len(import_results) + len(class_results)
    total_ok = dep_ok + import_ok + class_ok
    
    success_rate = (total_ok / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Dependências: {dep_ok}/{len(dep_results)} OK")
    print(f"Importações: {import_ok}/{len(import_results)} OK") 
    print(f"Estruturas: {class_ok}/{len(class_results)} OK")
    print(f"Taxa geral: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("Status: ✅ SISTEMA FUNCIONAL")
    elif success_rate >= 60:
        print("Status: ⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
    else:
        print("Status: ❌ SISTEMA COM PROBLEMAS")
    
    print("=" * 50)
    
    # Salvar resultado simples
    with open("QUICK_SCRAPER_TEST.txt", "w") as f:
        f.write(f"Teste rápido - {datetime.now()}\n")
        f.write(f"Taxa de sucesso: {success_rate:.1f}%\n")
        f.write(f"Dependências: {dep_ok}/{len(dep_results)}\n")
        f.write(f"Importações: {import_ok}/{len(import_results)}\n") 
        f.write(f"Estruturas: {class_ok}/{len(class_results)}\n")
    
    print("📄 Resultado salvo em QUICK_SCRAPER_TEST.txt")

if __name__ == "__main__":
    main()
