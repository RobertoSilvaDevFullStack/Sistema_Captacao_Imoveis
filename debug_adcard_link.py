#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug dos elementos adcard-link encontrados
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

def debug_adcard_link():
    """Debug dos elementos adcard-link"""
    print("🔍 Debug dos elementos adcard-link...")
    
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
        
        # Buscar elementos adcard-link
        adcard_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="adcard-link"]')
        print(f"\n🎯 Encontrados {len(adcard_elements)} elementos adcard-link")
        
        property_links = []
        
        print(f"\n📋 Analisando os primeiros 10 elementos adcard-link:")
        for i, elem in enumerate(adcard_elements[:10]):
            try:
                href = elem.get_attribute('href')
                title = elem.get_attribute('title') or 'Sem título'
                text = elem.text.strip()[:100] or 'Sem texto'
                
                print(f"\n   {i+1}. Href: {href}")
                print(f"       Título: {title}")
                print(f"       Texto: {text}")
                
                if href and 'olx.com.br' in href:
                    property_links.append(href)
                    
            except Exception as e:
                print(f"   {i+1}. Erro: {e}")
        
        print(f"\n✅ Total de links válidos encontrados: {len(property_links)}")
        
        if property_links:
            print(f"\n🏆 Primeiros 5 links de propriedades:")
            for i, link in enumerate(property_links[:5]):
                print(f"   {i+1}. {link}")
        
        # Testar se são anúncios reais verificando a estrutura da URL
        real_ads = []
        for link in property_links:
            # URLs de anúncios do OLX têm um padrão específico
            if ('rj.olx.com.br' in link and 
                len(link.split('/')) > 5 and 
                not any(exclude in link for exclude in ['categoria', 'estado', 'buscar'])):
                real_ads.append(link)
        
        print(f"\n🎯 Links que parecem ser anúncios reais: {len(real_ads)}")
        for i, link in enumerate(real_ads[:5]):
            print(f"   {i+1}. {link}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_adcard_link()
