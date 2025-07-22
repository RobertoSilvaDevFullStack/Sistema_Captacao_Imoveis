#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise detalhada dos métodos dos scrapers
"""

def analyze_scraper_methods():
    """Analisa métodos disponíveis em cada scraper"""
    
    print("🔍 ANÁLISE DETALHADA DOS SCRAPERS")
    print("=" * 60)
    
    # OLX Scraper
    try:
        from backend.scrapers.olx_scraper import OLXScraper
        print("\n📋 OLX SCRAPER:")
        print("  Classe importada: ✅")
        
        methods = [m for m in dir(OLXScraper) if not m.startswith('_')]
        print(f"  Métodos públicos: {len(methods)}")
        
        expected_methods = ['scrape_properties', 'close', 'get_property_links', 'extract_property_data']
        present = []
        missing = []
        
        for method in expected_methods:
            if hasattr(OLXScraper, method):
                present.append(method)
            else:
                missing.append(method)
        
        print(f"  Métodos presentes: {present}")
        if missing:
            print(f"  Métodos faltando: {missing}")
        
        # Verificar alguns métodos específicos encontrados
        actual_methods = [m for m in methods if 'scrape' in m.lower() or 'close' in m.lower() or 'extract' in m.lower()]
        print(f"  Métodos relacionados a scraping: {actual_methods}")
        
    except Exception as e:
        print(f"❌ OLX Scraper - Erro: {e}")
    
    # VivaReal Scraper
    try:
        from backend.scrapers.vivareal_scraper import VivaRealScraper
        print("\n📋 VIVAREAL SCRAPER:")
        print("  Classe importada: ✅")
        
        methods = [m for m in dir(VivaRealScraper) if not m.startswith('_')]
        print(f"  Métodos públicos: {len(methods)}")
        
        expected_methods = ['scrape_apartments', 'close', 'setup_driver', 'scrape_property_details']
        present = []
        missing = []
        
        for method in expected_methods:
            if hasattr(VivaRealScraper, method):
                present.append(method)
            else:
                missing.append(method)
        
        print(f"  Métodos presentes: {present}")
        if missing:
            print(f"  Métodos faltando: {missing}")
        
        # Verificar alguns métodos específicos encontrados
        actual_methods = [m for m in methods if 'scrape' in m.lower() or 'close' in m.lower() or 'extract' in m.lower()]
        print(f"  Métodos relacionados a scraping: {actual_methods}")
        
    except Exception as e:
        print(f"❌ VivaReal Scraper - Erro: {e}")
    
    # ZapImóveis Scraper
    try:
        from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
        print("\n📋 ZAPIMOVEIS SCRAPER:")
        print("  Classe importada: ✅")
        
        methods = [m for m in dir(ZapImoveisScraper) if not m.startswith('_')]
        print(f"  Métodos públicos: {len(methods)}")
        
        expected_methods = ['scrape_apartments', 'close_driver', 'setup_driver', 'extract_property_info']
        present = []
        missing = []
        
        for method in expected_methods:
            if hasattr(ZapImoveisScraper, method):
                present.append(method)
            else:
                missing.append(method)
        
        print(f"  Métodos presentes: {present}")
        if missing:
            print(f"  Métodos faltando: {missing}")
        
        # Verificar alguns métodos específicos encontrados
        actual_methods = [m for m in methods if 'scrape' in m.lower() or 'close' in m.lower() or 'extract' in m.lower()]
        print(f"  Métodos relacionados a scraping: {actual_methods}")
        
    except Exception as e:
        print(f"❌ ZapImóveis Scraper - Erro: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Análise concluída!")

if __name__ == "__main__":
    analyze_scraper_methods()
