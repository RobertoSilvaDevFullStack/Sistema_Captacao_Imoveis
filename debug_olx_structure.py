#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug da estrutura HTML do OLX para encontrar os seletores corretos dos anúncios
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

def debug_olx_structure():
    """Debug da estrutura HTML para encontrar os anúncios"""
    print("🔍 Debug da estrutura HTML do OLX...")
    
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
        time.sleep(7)  # Mais tempo para carregar
        
        print("\n🔍 Testando seletores comuns para anúncios...")
        
        # Lista de seletores para testar
        selectors = [
            'a[data-testid]',
            'a[href*="/ad/"]', 
            'a[href*="/anuncio"]',
            'a[href*="apartamento"]',
            'a[href*="casa"]',
            'div[data-testid] a',
            '.listing a',
            '.ad-tile a',
            '.item a',
            'section a',
            'article a',
            'li a',
            'div[class*="ad"] a',
            'div[class*="listing"] a',
            'div[class*="item"] a',
            '[data-ds-component] a',
            '[data-lurker-detail] a'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ '{selector}': {len(elements)} elementos")
                    
                    # Mostrar exemplo de href se tiver
                    for i, elem in enumerate(elements[:3]):
                        try:
                            href = elem.get_attribute('href')
                            if href and ('apartamento' in href.lower() or 'casa' in href.lower() or '/ad/' in href):
                                print(f"   Exemplo {i+1}: {href}")
                        except:
                            continue
                else:
                    print(f"❌ '{selector}': 0 elementos")
            except Exception as e:
                print(f"⚠️  '{selector}': Erro - {e}")
        
        print(f"\n🌐 Procurando padrões nos hrefs...")
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        
        property_patterns = []
        for link in all_links:
            try:
                href = link.get_attribute('href')
                if href and 'olx.com.br' in href:
                    # Procurar por links que parecem ser de anúncios específicos
                    if any(word in href.lower() for word in ['apartamento', 'casa', 'quarto', 'kitnet']):
                        property_patterns.append(href)
                    elif '/imoveis/' in href and len(href.split('/')) > 6:  # Links mais específicos
                        property_patterns.append(href)
                    elif href.count('-') > 3:  # Links com muitos hífens (típico de anúncios)
                        property_patterns.append(href)
            except:
                continue
        
        print(f"🎯 Encontrados {len(property_patterns)} links que parecem ser anúncios:")
        for i, link in enumerate(property_patterns[:10]):
            print(f"   {i+1}. {link}")
        
        # Testar scroll para carregar mais conteúdo
        print(f"\n📜 Testando scroll para carregar mais conteúdo...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        all_links_after = driver.find_elements(By.TAG_NAME, 'a')
        print(f"Links após scroll: {len(all_links_after)} (antes: {len(all_links)})")
        
        # Buscar por data attributes específicos
        print(f"\n🏷️  Buscando por data attributes...")
        data_attrs = [
            '[data-testid*="ad"]',
            '[data-testid*="listing"]', 
            '[data-testid*="item"]',
            '[data-testid*="card"]',
            '[data-lurker-detail]',
            '[data-position]'
        ]
        
        for attr in data_attrs:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, attr)
                if elements:
                    print(f"✅ '{attr}': {len(elements)} elementos")
                    for elem in elements[:2]:
                        links_inside = elem.find_elements(By.TAG_NAME, 'a')
                        if links_inside:
                            href = links_inside[0].get_attribute('href')
                            print(f"   Link dentro: {href}")
            except Exception as e:
                print(f"⚠️  '{attr}': Erro - {e}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_olx_structure()
