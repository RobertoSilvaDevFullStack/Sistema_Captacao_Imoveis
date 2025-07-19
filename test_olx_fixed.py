#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do scraper OLX corrigido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.olx_scraper_fixed import OLXScraperFixed
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_olx_fixed():
    """Teste final do OLX corrigido"""
    print("🚀 Testando OLX Scraper Corrigido...")
    
    scraper = OLXScraperFixed()
    
    try:
        print("\n📝 Iniciando scraping de 1 página...")
        properties = scraper.scrape_properties(max_pages=1)
        
        print(f"\n✅ Resultado: {len(properties)} propriedades encontradas")
        
        if properties:
            print("\n📋 Primeira propriedade encontrada:")
            first_prop = properties[0]
            for key, value in first_prop.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} itens")
                else:
                    print(f"   {key}: {str(value)[:100]}...")
                    
            print(f"\n🎯 Todas as propriedades:")
            for i, prop in enumerate(properties):
                print(f"   {i+1}. {prop.get('title', 'Sem título')[:60]}...")
                print(f"      Preço: {prop.get('price', 'N/A')}")
                print(f"      Local: {prop.get('location', 'N/A')}")
        else:
            print("\n❌ Nenhuma propriedade encontrada")
            
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    test_olx_fixed()
