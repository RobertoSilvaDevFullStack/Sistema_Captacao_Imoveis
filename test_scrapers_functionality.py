#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de funcionalidade dos scrapers após mudanças
"""

import sys
import os
import logging
import time
from datetime import datetime

# Adicionar paths necessários
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todos os scrapers podem ser importados"""
    test_results = {}
    
    logger.info("🔍 Testando importação dos scrapers...")
    
    # Testar Base Scraper
    try:
        from backend.scrapers.base_scraper import BaseScraper
        test_results['base_scraper'] = {'import': True, 'error': None}
        logger.info("✅ BaseScraper importado com sucesso")
    except Exception as e:
        test_results['base_scraper'] = {'import': False, 'error': str(e)}
        logger.error(f"❌ BaseScraper falhou: {e}")
    
    # Testar OLX Scraper
    try:
        from backend.scrapers.olx_scraper import OLXScraper
        test_results['olx_scraper'] = {'import': True, 'error': None}
        logger.info("✅ OLXScraper importado com sucesso")
    except Exception as e:
        test_results['olx_scraper'] = {'import': False, 'error': str(e)}
        logger.error(f"❌ OLXScraper falhou: {e}")
    
    # Testar VivaReal Scraper
    try:
        from backend.scrapers.vivareal_scraper import VivaRealScraper
        test_results['vivareal_scraper'] = {'import': True, 'error': None}
        logger.info("✅ VivaRealScraper importado com sucesso")
    except Exception as e:
        test_results['vivareal_scraper'] = {'import': False, 'error': str(e)}
        logger.error(f"❌ VivaRealScraper falhou: {e}")
    
    # Testar ZapImóveis Scraper
    try:
        from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
        test_results['zapimoveis_scraper'] = {'import': True, 'error': None}
        logger.info("✅ ZapImoveisScraper importado com sucesso")
    except Exception as e:
        test_results['zapimoveis_scraper'] = {'import': False, 'error': str(e)}
        logger.error(f"❌ ZapImoveisScraper falhou: {e}")
    
    # Testar Stealth Base Scraper
    try:
        from backend.scrapers.stealth_base_scraper import StealthBaseScraper, ScrapingConfig
        test_results['stealth_base_scraper'] = {'import': True, 'error': None}
        logger.info("✅ StealthBaseScraper importado com sucesso")
    except Exception as e:
        test_results['stealth_base_scraper'] = {'import': False, 'error': str(e)}
        logger.error(f"❌ StealthBaseScraper falhou: {e}")
    
    return test_results

def test_scraper_instantiation():
    """Testa se os scrapers podem ser instanciados"""
    test_results = {}
    
    logger.info("🔧 Testando instanciação dos scrapers...")
    
    # Testar OLX Scraper
    try:
        from backend.scrapers.olx_scraper import OLXScraper
        scraper = OLXScraper()
        # Fechar imediatamente
        if hasattr(scraper, 'close'):
            scraper.close()
        elif hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()
        test_results['olx_instantiation'] = {'success': True, 'error': None}
        logger.info("✅ OLXScraper instanciado com sucesso")
    except Exception as e:
        test_results['olx_instantiation'] = {'success': False, 'error': str(e)}
        logger.error(f"❌ OLXScraper instanciação falhou: {e}")
    
    # Testar VivaReal Scraper
    try:
        from backend.scrapers.vivareal_scraper import VivaRealScraper
        scraper = VivaRealScraper()
        # Fechar imediatamente
        if hasattr(scraper, 'close'):
            scraper.close()
        elif hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()
        test_results['vivareal_instantiation'] = {'success': True, 'error': None}
        logger.info("✅ VivaRealScraper instanciado com sucesso")
    except Exception as e:
        test_results['vivareal_instantiation'] = {'success': False, 'error': str(e)}
        logger.error(f"❌ VivaRealScraper instanciação falhou: {e}")
    
    # Testar ZapImóveis Scraper
    try:
        from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
        scraper = ZapImoveisScraper()
        # Fechar imediatamente
        if hasattr(scraper, 'close_driver'):
            scraper.close_driver()
        elif hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()
        test_results['zapimoveis_instantiation'] = {'success': True, 'error': None}
        logger.info("✅ ZapImoveisScraper instanciado com sucesso")
    except Exception as e:
        test_results['zapimoveis_instantiation'] = {'success': False, 'error': str(e)}
        logger.error(f"❌ ZapImoveisScraper instanciação falhou: {e}")
    
    return test_results

def test_stealth_system():
    """Testa se o sistema stealth está funcionando"""
    test_results = {}
    
    logger.info("🥷 Testando sistema stealth...")
    
    try:
        from src.utils.selenium_stealth import create_stealth_driver
        from src.utils.advanced_rate_limiter import advanced_rate_manager
        from src.utils.header_rotator import header_rotator
        
        test_results['stealth_imports'] = {'success': True, 'error': None}
        logger.info("✅ Componentes stealth importados com sucesso")
        
        # Testar rate manager
        try:
            rate_manager = advanced_rate_manager
            test_results['rate_manager'] = {'success': True, 'error': None}
            logger.info("✅ Rate manager funcionando")
        except Exception as e:
            test_results['rate_manager'] = {'success': False, 'error': str(e)}
            logger.error(f"❌ Rate manager falhou: {e}")
        
        # Testar header rotator
        try:
            headers = header_rotator.get_headers()
            test_results['header_rotator'] = {'success': True, 'error': None}
            logger.info("✅ Header rotator funcionando")
        except Exception as e:
            test_results['header_rotator'] = {'success': False, 'error': str(e)}
            logger.error(f"❌ Header rotator falhou: {e}")
            
    except Exception as e:
        test_results['stealth_imports'] = {'success': False, 'error': str(e)}
        logger.error(f"❌ Sistema stealth não disponível: {e}")
    
    return test_results

def test_dependencies():
    """Testa dependências necessárias"""
    test_results = {}
    
    logger.info("📦 Testando dependências...")
    
    # Testar Selenium
    try:
        from selenium import webdriver
        test_results['selenium'] = {'available': True, 'error': None}
        logger.info("✅ Selenium disponível")
    except Exception as e:
        test_results['selenium'] = {'available': False, 'error': str(e)}
        logger.error(f"❌ Selenium não disponível: {e}")
    
    # Testar WebDriver Manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        test_results['webdriver_manager'] = {'available': True, 'error': None}
        logger.info("✅ WebDriver Manager disponível")
    except Exception as e:
        test_results['webdriver_manager'] = {'available': False, 'error': str(e)}
        logger.error(f"❌ WebDriver Manager não disponível: {e}")
    
    # Testar BeautifulSoup
    try:
        from bs4 import BeautifulSoup
        test_results['beautifulsoup'] = {'available': True, 'error': None}
        logger.info("✅ BeautifulSoup disponível")
    except Exception as e:
        test_results['beautifulsoup'] = {'available': False, 'error': str(e)}
        logger.error(f"❌ BeautifulSoup não disponível: {e}")
    
    # Testar Requests
    try:
        import requests
        test_results['requests'] = {'available': True, 'error': None}
        logger.info("✅ Requests disponível")
    except Exception as e:
        test_results['requests'] = {'available': False, 'error': str(e)}
        logger.error(f"❌ Requests não disponível: {e}")
    
    return test_results

def generate_test_report(import_results, instantiation_results, stealth_results, dependency_results):
    """Gera relatório final dos testes"""
    
    report = []
    report.append("=" * 80)
    report.append("🔍 RELATÓRIO DE TESTE DOS SCRAPERS")
    report.append("=" * 80)
    report.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append("")
    
    # Resumo geral
    total_tests = 0
    passed_tests = 0
    
    # Dependências
    report.append("📦 DEPENDÊNCIAS:")
    for dep, result in dependency_results.items():
        status = "✅ OK" if result['available'] else "❌ FALHOU"
        report.append(f"  {dep}: {status}")
        if result['error']:
            report.append(f"    Erro: {result['error']}")
        total_tests += 1
        if result['available']:
            passed_tests += 1
    report.append("")
    
    # Importações
    report.append("📥 IMPORTAÇÕES DOS SCRAPERS:")
    for scraper, result in import_results.items():
        status = "✅ OK" if result['import'] else "❌ FALHOU"
        report.append(f"  {scraper}: {status}")
        if result['error']:
            report.append(f"    Erro: {result['error']}")
        total_tests += 1
        if result['import']:
            passed_tests += 1
    report.append("")
    
    # Instanciações
    report.append("🔧 INSTANCIAÇÃO DOS SCRAPERS:")
    for test, result in instantiation_results.items():
        status = "✅ OK" if result['success'] else "❌ FALHOU"
        report.append(f"  {test}: {status}")
        if result['error']:
            report.append(f"    Erro: {result['error']}")
        total_tests += 1
        if result['success']:
            passed_tests += 1
    report.append("")
    
    # Sistema Stealth
    report.append("🥷 SISTEMA STEALTH:")
    for test, result in stealth_results.items():
        status = "✅ OK" if result['success'] else "❌ FALHOU"
        report.append(f"  {test}: {status}")
        if result['error']:
            report.append(f"    Erro: {result['error']}")
        total_tests += 1
        if result['success']:
            passed_tests += 1
    report.append("")
    
    # Resumo final
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    report.append("=" * 80)
    report.append("📊 RESUMO FINAL:")
    report.append(f"  Total de testes: {total_tests}")
    report.append(f"  Testes aprovados: {passed_tests}")
    report.append(f"  Testes falharam: {total_tests - passed_tests}")
    report.append(f"  Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        report.append("  Status: ✅ SISTEMA FUNCIONAL")
    elif success_rate >= 60:
        report.append("  Status: ⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
    else:
        report.append("  Status: ❌ SISTEMA COM PROBLEMAS")
    
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes de funcionalidade dos scrapers...")
    
    # Executar todos os testes
    dependency_results = test_dependencies()
    import_results = test_imports()
    instantiation_results = test_scraper_instantiation()
    stealth_results = test_stealth_system()
    
    # Gerar relatório
    report = generate_test_report(import_results, instantiation_results, stealth_results, dependency_results)
    
    # Salvar relatório em arquivo
    report_file = "SCRAPER_TEST_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Exibir resultado
    print("\n" + report)
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    logger.info("✅ Testes concluídos!")

if __name__ == "__main__":
    main()
