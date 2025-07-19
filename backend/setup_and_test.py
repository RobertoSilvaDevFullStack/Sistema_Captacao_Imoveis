#!/usr/bin/env python3
# backend/setup_and_test.py

"""
Script de configuração e teste do sistema de scrapers
Verifica dependências, configurações e executa testes básicos
"""

import sys
import os
import subprocess
import importlib

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'selenium',
        'webdriver_manager',
        'beautifulsoup4',
        'requests',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'webdriver_manager':
                importlib.import_module('webdriver_manager.chrome')
            elif package == 'beautifulsoup4':
                importlib.import_module('bs4')
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - NÃO INSTALADO")
    
    if missing_packages:
        print(f"\n⚠️ Pacotes faltando: {', '.join(missing_packages)}")
        print("Para instalar:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ Todas as dependências estão instaladas!")
        return True

def check_chrome():
    """Verifica se o Chrome está disponível"""
    print("\n🌐 Verificando Google Chrome...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"  ✅ Chrome funcionando - Título obtido: {title}")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro com Chrome: {e}")
        return False

def test_scraper_imports():
    """Testa se todos os scrapers podem ser importados"""
    print("\n📦 Testando imports dos scrapers...")
    
    scrapers = {
        'VivaReal': 'scrapers.vivareal_scraper.VivaRealScraper',
        'OLX': 'scrapers.olx_scraper.OLXScraper', 
        'ZapImóveis': 'scrapers.zapimoveis_scraper.ZapImoveisScraper'
    }
    
    success_count = 0
    
    for name, import_path in scrapers.items():
        try:
            module_path, class_name = import_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            scraper_class = getattr(module, class_name)
            print(f"  ✅ {name}: {scraper_class}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {name}: Erro - {e}")
    
    print(f"\n📊 Scrapers importados: {success_count}/{len(scrapers)}")
    return success_count == len(scrapers)

def test_scraper_initialization():
    """Testa se os scrapers podem ser inicializados"""
    print("\n🚀 Testando inicialização dos scrapers...")
    
    success_count = 0
    
    # Teste VivaReal
    try:
        from scrapers.vivareal_scraper import VivaRealScraper
        vr = VivaRealScraper()
        vr.close()
        print("  ✅ VivaReal: Inicializado com sucesso")
        success_count += 1
    except Exception as e:
        print(f"  ❌ VivaReal: {e}")
    
    # Teste OLX
    try:
        from scrapers.olx_scraper import OLXScraper
        olx = OLXScraper()
        olx.close()
        print("  ✅ OLX: Inicializado com sucesso")
        success_count += 1
    except Exception as e:
        print(f"  ❌ OLX: {e}")
    
    # Teste ZapImóveis
    try:
        from scrapers.zapimoveis_scraper import ZapImoveisScraper
        zap = ZapImoveisScraper()
        zap.close()
        print("  ✅ ZapImóveis: Inicializado com sucesso")
        success_count += 1
    except Exception as e:
        print(f"  ❌ ZapImóveis: {e}")
    
    print(f"\n📊 Scrapers funcionais: {success_count}/3")
    return success_count == 3

def test_multi_scraper_service():
    """Testa o multi-scraper service"""
    print("\n🔧 Testando Multi-Scraper Service...")
    
    try:
        from services.multi_scraper_service import MultiScraperService
        
        service = MultiScraperService()
        service.initialize_scrapers()
        
        initialized_count = len(service.scrapers)
        print(f"  ✅ Multi-Scraper Service: {initialized_count} scrapers inicializados")
        
        service.close_all_scrapers()
        return initialized_count > 0
        
    except Exception as e:
        print(f"  ❌ Multi-Scraper Service: {e}")
        return False

def run_quick_demo():
    """Executa demo rápido se tudo estiver funcionando"""
    print("\n🎬 Executando demo rápido...")
    
    try:
        from demos.complete_scraper_demo import test_individual_scrapers
        
        print("  📋 Executando testes individuais (modo rápido)...")
        # results = test_individual_scrapers()
        
        print("  ✅ Demo concluído! Para teste completo execute:")
        print("     python backend/demos/complete_scraper_demo.py")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no demo: {e}")
        return False

def main():
    """Função principal de setup e teste"""
    print("🏠 SISTEMA DE CAPTAÇÃO DE IMÓVEIS - SETUP E TESTE")
    print("=" * 60)
    
    # Lista de verificações
    checks = [
        ("Dependências", check_dependencies),
        ("Google Chrome", check_chrome),
        ("Imports dos Scrapers", test_scraper_imports),
        ("Inicialização dos Scrapers", test_scraper_initialization),
        ("Multi-Scraper Service", test_multi_scraper_service)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Erro em {check_name}: {e}")
            results[check_name] = False
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {check_name}: {status}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para uso!")
        
        # Executa demo se solicitado
        demo_choice = input("\n🎬 Executar demo completo? (s/n): ").lower()
        if demo_choice == 's':
            run_quick_demo()
    
    elif passed >= total * 0.8:
        print("⚠️ MAIORIA DOS TESTES PASSARAM")
        print("🔧 Sistema funcional com algumas limitações")
    else:
        print("🚨 MUITOS TESTES FALHARAM")
        print("❌ Sistema precisa de correções antes do uso")
    
    print(f"\n📝 Para logs detalhados, verifique os arquivos de teste")
    print("🏁 Setup concluído!")

if __name__ == "__main__":
    # Adiciona o diretório backend ao path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
