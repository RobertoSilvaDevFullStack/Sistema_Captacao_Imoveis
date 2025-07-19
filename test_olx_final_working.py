#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do scraper OLX com extração de dados das listagens
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.olx_scraper_final import OLXScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_olx_final_working():
    """Teste final do OLX com extração das listagens"""
    print("🚀 Testando OLX Scraper Final (extração de listagens)...")
    
    scraper = OLXScraper()
    
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
                    print(f"   {key}: {str(value)[:100]}")
                    
            print(f"\n🎯 Resumo de todas as propriedades:")
            for i, prop in enumerate(properties[:10]):
                title = prop.get('title', 'Sem título')[:60]
                price = prop.get('price', 'N/A')[:30]
                location = prop.get('location', 'N/A')[:40]
                print(f"   {i+1}. {title}...")
                print(f"      💰 {price} | 📍 {location}")
                
            print(f"\n📊 Estatísticas:")
            with_price = sum(1 for p in properties if p.get('price'))
            with_location = sum(1 for p in properties if p.get('location'))
            with_area = sum(1 for p in properties if p.get('area'))
            
            print(f"   Propriedades com preço: {with_price}/{len(properties)}")
            print(f"   Propriedades com localização: {with_location}/{len(properties)}")
            print(f"   Propriedades com área: {with_area}/{len(properties)}")
            
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
    test_olx_final_working()
