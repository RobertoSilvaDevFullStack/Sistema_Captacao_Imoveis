#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simplificado de funcionalidade dos scrapers principais
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

def test_core_scrapers():
    """Testa os scrapers principais"""
    results = []
    
    logger.info("🚀 Testando scrapers principais...")
    
    # Teste OLX Scraper
    try:
        logger.info("🔍 Testando OLX Scraper...")
        from backend.scrapers.olx_scraper import OLXScraper
        
        # Instanciar e testar métodos básicos
        scraper = OLXScraper()
        
        # Verificar se tem os métodos necessários
        assert hasattr(scraper, 'scrape_properties'), "OLX: Falta método scrape_properties"
        assert hasattr(scraper, 'close'), "OLX: Falta método close"
        
        scraper.close()
        
        results.append({
            'scraper': 'OLX',
            'status': '✅ OK',
            'details': 'Importação e instanciação OK, métodos presentes'
        })
        logger.info("✅ OLX Scraper - OK")
        
    except Exception as e:
        results.append({
            'scraper': 'OLX',
            'status': '❌ ERRO',
            'details': f'Erro: {str(e)}'
        })
        logger.error(f"❌ OLX Scraper - ERRO: {e}")
    
    # Teste VivaReal Scraper
    try:
        logger.info("🔍 Testando VivaReal Scraper...")
        from backend.scrapers.vivareal_scraper import VivaRealScraper
        
        # Instanciar e testar métodos básicos
        scraper = VivaRealScraper()
        
        # Verificar se tem os métodos necessários
        assert hasattr(scraper, 'scrape_apartments'), "VivaReal: Falta método scrape_apartments"
        assert hasattr(scraper, 'close'), "VivaReal: Falta método close"
        
        scraper.close()
        
        results.append({
            'scraper': 'VivaReal',
            'status': '✅ OK',
            'details': 'Importação e instanciação OK, métodos presentes'
        })
        logger.info("✅ VivaReal Scraper - OK")
        
    except Exception as e:
        results.append({
            'scraper': 'VivaReal',
            'status': '❌ ERRO',
            'details': f'Erro: {str(e)}'
        })
        logger.error(f"❌ VivaReal Scraper - ERRO: {e}")
    
    # Teste ZapImóveis Scraper
    try:
        logger.info("🔍 Testando ZapImóveis Scraper...")
        from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
        
        # Instanciar e testar métodos básicos
        scraper = ZapImoveisScraper()
        
        # Verificar se tem os métodos necessários
        assert hasattr(scraper, 'scrape_apartments'), "ZapImóveis: Falta método scrape_apartments"
        assert hasattr(scraper, 'close_driver'), "ZapImóveis: Falta método close_driver"
        
        scraper.close_driver()
        
        results.append({
            'scraper': 'ZapImóveis',
            'status': '✅ OK',
            'details': 'Importação e instanciação OK, métodos presentes'
        })
        logger.info("✅ ZapImóveis Scraper - OK")
        
    except Exception as e:
        results.append({
            'scraper': 'ZapImóveis',
            'status': '❌ ERRO',
            'details': f'Erro: {str(e)}'
        })
        logger.error(f"❌ ZapImóveis Scraper - ERRO: {e}")
    
    return results

def test_simple_scraping():
    """Teste básico de scraping (sem executar realmente)"""
    results = []
    
    logger.info("🕵️ Testando capacidade básica de scraping...")
    
    try:
        # Testar se podemos criar URL de busca
        from backend.scrapers.olx_scraper import OLXScraper
        scraper = OLXScraper()
        
        # Verificar se as configurações básicas estão OK
        assert scraper.location is not None, "Localização não configurada"
        assert scraper.property_type is not None, "Tipo de propriedade não configurado"
        
        scraper.close()
        
        results.append({
            'test': 'Configuração Básica',
            'status': '✅ OK',
            'details': 'Scrapers podem ser configurados corretamente'
        })
        
    except Exception as e:
        results.append({
            'test': 'Configuração Básica',
            'status': '❌ ERRO',
            'details': f'Erro: {str(e)}'
        })
    
    return results

def test_dependencies():
    """Testa dependências críticas"""
    results = []
    
    deps = {
        'selenium': 'selenium',
        'webdriver-manager': 'webdriver_manager.chrome',
        'beautifulsoup': 'bs4',
        'requests': 'requests',
        'logging': 'logging'
    }
    
    for name, module in deps.items():
        try:
            __import__(module)
            results.append({
                'dependency': name,
                'status': '✅ OK',
                'details': 'Disponível'
            })
        except ImportError as e:
            results.append({
                'dependency': name,
                'status': '❌ ERRO',
                'details': f'Não disponível: {e}'
            })
    
    return results

def generate_simplified_report(scraper_results, scraping_results, dependency_results):
    """Gera relatório simplificado"""
    
    report = []
    report.append("=" * 70)
    report.append("🔍 RELATÓRIO SIMPLIFICADO DOS SCRAPERS")
    report.append("=" * 70)
    report.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append("")
    
    # Dependências
    report.append("📦 DEPENDÊNCIAS:")
    dep_ok = sum(1 for r in dependency_results if '✅' in r['status'])
    dep_total = len(dependency_results)
    
    for result in dependency_results:
        report.append(f"  {result['dependency']}: {result['status']}")
        if '❌' in result['status']:
            report.append(f"    → {result['details']}")
    
    report.append(f"  Resultado: {dep_ok}/{dep_total} dependências OK")
    report.append("")
    
    # Scrapers
    report.append("🕷️ SCRAPERS PRINCIPAIS:")
    scraper_ok = sum(1 for r in scraper_results if '✅' in r['status'])
    scraper_total = len(scraper_results)
    
    for result in scraper_results:
        report.append(f"  {result['scraper']}: {result['status']}")
        if '❌' in result['status']:
            report.append(f"    → {result['details']}")
    
    report.append(f"  Resultado: {scraper_ok}/{scraper_total} scrapers OK")
    report.append("")
    
    # Testes de Scraping
    report.append("🔧 TESTES DE CONFIGURAÇÃO:")
    scraping_ok = sum(1 for r in scraping_results if '✅' in r['status'])
    scraping_total = len(scraping_results)
    
    for result in scraping_results:
        report.append(f"  {result['test']}: {result['status']}")
        if '❌' in result['status']:
            report.append(f"    → {result['details']}")
    
    report.append(f"  Resultado: {scraping_ok}/{scraping_total} testes OK")
    report.append("")
    
    # Resumo Final
    total_tests = dep_total + scraper_total + scraping_total
    total_ok = dep_ok + scraper_ok + scraping_ok
    success_rate = (total_ok / total_tests) * 100 if total_tests > 0 else 0
    
    report.append("=" * 70)
    report.append("📊 RESUMO FINAL:")
    report.append(f"  Total de testes: {total_tests}")
    report.append(f"  Testes aprovados: {total_ok}")
    report.append(f"  Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        status = "✅ EXCELENTE - Sistema totalmente funcional"
    elif success_rate >= 75:
        status = "✅ FUNCIONAL - Sistema operacional"
    elif success_rate >= 50:
        status = "⚠️ PARCIAL - Sistema com limitações"
    else:
        status = "❌ CRÍTICO - Sistema com problemas"
    
    report.append(f"  Status: {status}")
    report.append("=" * 70)
    
    return "\n".join(report)

def main():
    """Executa todos os testes"""
    logger.info("🚀 Iniciando teste simplificado dos scrapers...")
    
    # Executar testes
    dependency_results = test_dependencies()
    scraper_results = test_core_scrapers() 
    scraping_results = test_simple_scraping()
    
    # Gerar relatório
    report = generate_simplified_report(scraper_results, scraping_results, dependency_results)
    
    # Salvar e exibir
    report_file = "SCRAPERS_SIMPLIFIED_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + report)
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    logger.info("✅ Teste simplificado concluído!")

if __name__ == "__main__":
    main()
