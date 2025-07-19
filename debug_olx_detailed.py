#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug detalhado dos links encontrados no OLX
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_olx_links():
    """Debug detalhado dos links OLX"""
    print("🔍 Debug detalhado - OLX Links...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://rj.olx.com.br/rio-de-janeiro-e-regiao/imoveis"
        print(f"\n📡 Acessando: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        print("\n🔍 Analisando seletores...")
        
        # Seletor principal
        elements_main = driver.find_elements(By.CSS_SELECTOR, 'a[data-ds-component="DS-Link"]')
        print(f"Seletor principal 'a[data-ds-component=\"DS-Link\"]': {len(elements_main)} elementos")
        
        # Listar alguns hrefs
        print("\n📋 Primeiros 10 hrefs encontrados:")
        for i, elem in enumerate(elements_main[:10]):
            try:
                href = elem.get_attribute('href')
                text = elem.text.strip()[:50]
                print(f"   {i+1}. {href} | Texto: '{text}'")
            except:
                print(f"   {i+1}. [Erro ao obter href]")
        
        # Análise de padrões
        print(f"\n🧪 Analisando padrões nos {len(elements_main)} links...")
        
        imoveis_count = 0
        ad_count = 0  
        apartamento_count = 0
        casa_count = 0
        valid_pattern_count = 0
        rj_imoveis_count = 0
        
        for elem in elements_main:
            try:
                href = elem.get_attribute('href')
                if not href:
                    continue
                    
                if '/imoveis/' in href:
                    imoveis_count += 1
                if '/ad/' in href:
                    ad_count += 1
                if 'apartamento' in href.lower():
                    apartamento_count += 1
                if 'casa' in href.lower():
                    casa_count += 1
                if 'rj.olx.com.br' in href and '/imoveis/' in href:
                    rj_imoveis_count += 1
                    
                # Testa padrões válidos
                valid_patterns = [
                    'olx.com.br' in href and '/imoveis/' in href,
                    'olx.com.br' in href and '/ad/' in href,
                    'olx.com.br' in href and 'apartamento' in href.lower(),
                    'olx.com.br' in href and 'casa' in href.lower(),
                    'rj.olx.com.br' in href and '/imoveis/' in href,
                    'sp.olx.com.br' in href and '/imoveis/' in href,
                ]
                
                if any(valid_patterns):
                    valid_pattern_count += 1
                    
            except:
                continue
        
        print(f"   📊 Contadores:")
        print(f"      '/imoveis/' no href: {imoveis_count}")
        print(f"      '/ad/' no href: {ad_count}")
        print(f"      'apartamento' no href: {apartamento_count}")
        print(f"      'casa' no href: {casa_count}")
        print(f"      'rj.olx.com.br' + '/imoveis/': {rj_imoveis_count}")
        print(f"      Links com padrão válido: {valid_pattern_count}")
        
        # Teste de todos os links A da página
        print(f"\n🌐 Testando todos os links <a> da página...")
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"Total de links <a> na página: {len(all_links)}")
        
        potential_property_links = 0
        for link in all_links:
            try:
                href = link.get_attribute('href')
                if href and 'olx.com.br' in href and '/imoveis/' in href:
                    potential_property_links += 1
            except:
                continue
                
        print(f"Links potenciais de imóveis (olx.com.br + /imoveis/): {potential_property_links}")
        
        # Mostrar exemplos de links potenciais
        print(f"\n🎯 Exemplos de links potenciais de imóveis:")
        count = 0
        for link in all_links:
            if count >= 5:
                break
            try:
                href = link.get_attribute('href')
                if href and 'olx.com.br' in href and '/imoveis/' in href:
                    count += 1
                    print(f"   {count}. {href}")
            except:
                continue
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_olx_links()
