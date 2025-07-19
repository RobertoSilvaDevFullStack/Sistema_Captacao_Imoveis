#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do scraper OLX com novos filtros aprimorados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.olx_scraper import OLXScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_olx_final():
    """Teste final do OLX com os novos filtros"""
    print("🚀 Testando OLX com filtros aprimorados...")
    
    scraper = OLXScraper()
    
    try:
        # URL do OLX Rio de Janeiro - Imóveis
        search_url = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/imoveis"
        
        # Testar apenas uma página para verificar os novos filtros
        print(f"\n📝 Iniciando scraping de 1 página: {search_url}")
        properties = scraper.scrape_properties(search_url, max_pages=1)
        
        print(f"\n✅ Resultado: {len(properties)} propriedades encontradas")
        
        if properties:
            print("\n📋 Primeira propriedade encontrada:")
            first_prop = properties[0]
            for key, value in first_prop.items():
                print(f"   {key}: {value}")
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
    test_olx_final()
