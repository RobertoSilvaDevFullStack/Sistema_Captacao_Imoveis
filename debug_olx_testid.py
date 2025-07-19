#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug focado nos data-testid para encontrar os anúncios reais
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

def debug_olx_testid():
    """Debug focado nos data-testid"""
    print("🔍 Debug focado em data-testid...")
    
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
        time.sleep(7)
        
        print(f"\n🎯 Analisando elementos com data-testid...")
        
        # Buscar todos os elementos com data-testid
        elements_with_testid = driver.find_elements(By.CSS_SELECTOR, '[data-testid]')
        print(f"Total de elementos com data-testid: {len(elements_with_testid)}")
        
        # Coletar todos os data-testid únicos
        testids = set()
        for elem in elements_with_testid:
            testid = elem.get_attribute('data-testid')
            if testid:
                testids.add(testid)
        
        print(f"\n📋 data-testid únicos encontrados ({len(testids)}):")
        for testid in sorted(testids):
            count = len(driver.find_elements(By.CSS_SELECTOR, f'[data-testid="{testid}"]'))
            print(f"   '{testid}': {count} elementos")
        
        # Focar nos que parecem ser anúncios
        ad_like_testids = [tid for tid in testids if any(word in tid.lower() for word in ['ad', 'card', 'listing', 'item', 'property'])]
        
        print(f"\n🏠 data-testid que parecem ser anúncios:")
        for testid in ad_like_testids:
            elements = driver.find_elements(By.CSS_SELECTOR, f'[data-testid="{testid}"]')
            print(f"\n   🔍 '{testid}': {len(elements)} elementos")
            
            for i, elem in enumerate(elements[:3]):
                try:
                    # Tentar encontrar link dentro do elemento
                    links = elem.find_elements(By.TAG_NAME, 'a')
                    if links:
                        href = links[0].get_attribute('href')
                        text = elem.text.strip()[:100]
                        print(f"      {i+1}. Href: {href}")
                        print(f"         Texto: '{text}'")
                except Exception as e:
                    print(f"      {i+1}. Erro: {e}")
        
        # Testar seletores específicos para anúncios
        print(f"\n🧪 Testando seletores específicos para anúncios...")
        
        test_selectors = [
            '[data-testid*="ad"] a',
            '[data-testid*="card"] a', 
            '[data-testid="ad-card"] a',
            '[data-testid="ad-tile"] a',
            '[data-testid="listing"] a',
            '[data-testid="listing-card"] a'
        ]
        
        best_selector = None
        best_count = 0
        best_examples = []
        
        for selector in test_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                property_links = []
                
                for elem in elements:
                    href = elem.get_attribute('href')
                    if href and 'olx.com.br' in href:
                        # Verificar se parece um anúncio específico
                        if (len(href.split('/')) > 6 or 
                            any(word in href.lower() for word in ['apartamento', 'casa', 'quarto']) or
                            href.count('-') > 3):
                            property_links.append(href)
                
                print(f"   '{selector}': {len(elements)} elementos, {len(property_links)} links de propriedade")
                
                if len(property_links) > best_count:
                    best_count = len(property_links)
                    best_selector = selector
                    best_examples = property_links[:5]
                    
            except Exception as e:
                print(f"   '{selector}': Erro - {e}")
        
        if best_selector:
            print(f"\n🏆 Melhor seletor: '{best_selector}' com {best_count} links")
            print(f"📋 Exemplos de links encontrados:")
            for i, link in enumerate(best_examples):
                print(f"   {i+1}. {link}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_olx_testid()
