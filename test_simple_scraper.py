#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.abspath('.'))

from backend.scrapers.zapimoveis_simple import ZapImoveisSimple

def test_simple_scraper():
    print("Testando ZapImóveis Simple Scraper...")
    
    scraper = ZapImoveisSimple()
    url = 'https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/'
    
    properties = scraper.scrape_properties(url, max_results=5)
    
    print(f"\nPropriedades encontradas: {len(properties)}")
    
    for i, prop in enumerate(properties):
        print(f"\n{i+1}. {prop.get('title', 'N/A')}")
        print(f"   Preço: {prop.get('price', 'N/A')}")
        print(f"   Local: {prop.get('location', 'N/A')}")
        print(f"   Quartos: {prop.get('rooms', 'N/A')}")
        print(f"   Área: {prop.get('area', 'N/A')}")

if __name__ == "__main__":
    test_simple_scraper()
