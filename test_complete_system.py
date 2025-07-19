#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do sistema completo com os 3 scrapers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.vivareal_scraper import VivaRealScraper
from backend.scrapers.olx_scraper import OLXScraper
from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_complete_system():
    """Teste final do sistema completo"""
    print("🚀 TESTE FINAL DO SISTEMA COMPLETO DE SCRAPERS")
    print("=" * 60)
    
    results = {}
    
    # Teste VivaReal
    print("\n1️⃣ Testando VivaReal...")
    try:
        scraper = VivaRealScraper()
        properties = scraper.scrape_properties(
            "https://www.vivareal.com.br/venda/rio-de-janeiro/apartamento/", 
            max_pages=1
        )
        results['VivaReal'] = len(properties)
        print(f"   ✅ VivaReal: {len(properties)} propriedades")
        scraper.close()
    except Exception as e:
        results['VivaReal'] = 0
        print(f"   ❌ VivaReal: Erro - {e}")
    
    time.sleep(2)
    
    # Teste OLX
    print("\n2️⃣ Testando OLX...")
    try:
        scraper = OLXScraper()
        properties = scraper.scrape_properties(max_pages=1)
        results['OLX'] = len(properties)
        print(f"   ✅ OLX: {len(properties)} propriedades")
        scraper.close()
    except Exception as e:
        results['OLX'] = 0
        print(f"   ❌ OLX: Erro - {e}")
    
    time.sleep(2)
    
    # Teste ZapImóveis
    print("\n3️⃣ Testando ZapImóveis...")
    try:
        scraper = ZapImoveisScraper()
        properties = scraper.scrape_properties(
            "https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/", 
            max_pages=1
        )
        results['ZapImoveis'] = len(properties)
        print(f"   ✅ ZapImóveis: {len(properties)} propriedades")
        scraper.close()
    except Exception as e:
        results['ZapImoveis'] = 0
        print(f"   ❌ ZapImóveis: Erro - {e}")
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL DO SISTEMA:")
    print("=" * 60)
    
    total_properties = sum(results.values())
    working_scrapers = sum(1 for count in results.values() if count > 0)
    
    for portal, count in results.items():
        status = "✅ FUNCIONANDO" if count > 0 else "❌ FALHOU"
        print(f"   {portal:12} | {count:3} propriedades | {status}")
    
    print("=" * 60)
    print(f"🎯 TOTAL: {total_properties} propriedades de {working_scrapers}/3 portais")
    print(f"📈 Taxa de sucesso: {working_scrapers*100//3}%")
    
    if working_scrapers >= 2:
        print("🏆 SISTEMA APROVADO! Pelo menos 2 scrapers funcionando.")
    else:
        print("⚠️  SISTEMA NECESSITA AJUSTES.")

if __name__ == "__main__":
    test_complete_system()
