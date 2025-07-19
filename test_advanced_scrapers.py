#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste dos Scrapers Avançados
Testa ZapImóveis e OLX com foco em oportunidades e lançamentos
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import logging
from backend.scrapers.zapimoveis_advanced import ZapImoveisAdvanced
from backend.scrapers.olx_advanced import OLXScraperAdvanced

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_zapimoveis_advanced():
    """Testa o scraper avançado do ZapImóveis"""
    print("\n" + "="*60)
    print("🏠 TESTANDO ZAPIMOVEIS ADVANCED")
    print("="*60)
    
    try:
        scraper = ZapImoveisAdvanced()
        
        # URLs para teste
        test_urls = [
            "https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/",
            "https://www.zapimoveis.com.br/venda/casas/sp+sao-paulo/"
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔍 Teste {i}: {url}")
            properties = scraper.scrape_properties(url, max_results=3)
            
            print(f"✅ Encontradas {len(properties)} propriedades")
            
            for j, prop in enumerate(properties, 1):
                print(f"\n  📋 Propriedade {j}:")
                print(f"     Título: {prop.get('title', 'N/A')[:80]}...")
                print(f"     Preço: R$ {prop.get('price', 'N/A'):,.2f}" if prop.get('price') else "     Preço: N/A")
                print(f"     Área: {prop.get('area', 'N/A')} m²")
                print(f"     Quartos: {prop.get('bedrooms', 'N/A')}")
                print(f"     Banheiros: {prop.get('bathrooms', 'N/A')}")
                print(f"     Endereço: {prop.get('address', 'N/A')}")
                print(f"     Badges: {', '.join(prop.get('badges', []))}")
                print(f"     URL: {prop.get('url', 'N/A')[:80]}...")
                
            if not properties:
                print("   ⚠️  Nenhuma propriedade extraída")
            
    except Exception as e:
        print(f"❌ Erro no teste ZapImóveis: {e}")

def test_olx_advanced():
    """Testa o scraper avançado do OLX"""
    print("\n" + "="*60)
    print("🏘️  TESTANDO OLX ADVANCED")
    print("="*60)
    
    try:
        scraper = OLXScraperAdvanced()
        
        # URLs para teste
        test_urls = [
            "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro",
            "https://www.olx.com.br/imoveis/venda/casas/estado-sp/sao-paulo"
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔍 Teste {i}: {url}")
            properties = scraper.scrape_properties(url, max_results=3)
            
            print(f"✅ Encontradas {len(properties)} propriedades")
            
            for j, prop in enumerate(properties, 1):
                print(f"\n  📋 Propriedade {j}:")
                print(f"     Título: {prop.get('title', 'N/A')[:80]}...")
                print(f"     Preço: R$ {prop.get('price', 'N/A'):,.2f}" if prop.get('price') else "     Preço: N/A")
                print(f"     Área: {prop.get('area', 'N/A')} m²")
                print(f"     Quartos: {prop.get('bedrooms', 'N/A')}")
                print(f"     Endereço: {prop.get('address', 'N/A')}")
                print(f"     Amenidades: {', '.join(prop.get('amenities', []))}")
                print(f"     URL: {prop.get('url', 'N/A')[:80]}...")
                
            if not properties:
                print("   ⚠️  Nenhuma propriedade extraída")
            
    except Exception as e:
        print(f"❌ Erro no teste OLX: {e}")

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DOS SCRAPERS AVANÇADOS")
    print("Foco: Imóveis recém-adicionados, lançamentos e oportunidades")
    
    # Teste ZapImóveis
    test_zapimoveis_advanced()
    
    # Teste OLX
    test_olx_advanced()
    
    print("\n" + "="*60)
    print("✨ TESTES CONCLUÍDOS")
    print("="*60)
    print("\n💡 Os scrapers avançados foram projetados para:")
    print("   • Extrair dados mais precisos (preço, área, quartos)")
    print("   • Identificar badges especiais (OPORTUNIDADE, LANÇAMENTO)")
    print("   • Priorizar imóveis com destaques")
    print("   • Melhor resistência a bloqueios")
    print("   • Extração de amenidades e características")

if __name__ == "__main__":
    main()
