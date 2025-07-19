#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste com URLs mais específicas do OLX para imóveis
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

def test_specific_urls():
    """Teste com URLs específicas"""
    print("🔍 Testando URLs específicas do OLX...")
    
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # URLs mais específicas para testar
        test_urls = [
            "https://rj.olx.com.br/rio-de-janeiro-e-regiao/imoveis/venda",
            "https://rj.olx.com.br/rio-de-janeiro-e-regiao/imoveis/venda/apartamentos",
            "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj",
            "https://www.olx.com.br/imoveis/venda/estado-rj",
            "https://rj.olx.com.br/imoveis"
        ]
        
        for url in test_urls:
            print(f"\n📡 Testando: {url}")
            driver.get(url)
            time.sleep(5)
            
            # Verificar se chegou na página correta
            title = driver.title
            print(f"   Título da página: {title}")
            
            # Buscar elementos adcard-link
            adcard_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="adcard-link"]')
            print(f"   Elementos adcard-link: {len(adcard_elements)}")
            
            if adcard_elements:
                # Verificar os primeiros 3 anúncios
                property_count = 0
                for i, elem in enumerate(adcard_elements[:5]):
                    try:
                        href = elem.get_attribute('href')
                        title_attr = elem.get_attribute('title') or ''
                        
                        # Verificar se é imóvel
                        if any(word in title_attr.lower() for word in ['apartamento', 'casa', 'kitnet', 'quarto', 'imóvel', 'cobertura']):
                            property_count += 1
                            print(f"   ✅ Imóvel {property_count}: {title_attr}")
                            print(f"      URL: {href}")
                    except:
                        continue
                
                print(f"   🏠 Total de imóveis encontrados: {property_count}")
                
                if property_count > 0:
                    print(f"   🎯 URL funcionando para imóveis!")
                    break
            else:
                print(f"   ❌ Nenhum elemento adcard-link encontrado")
        
        # Se nenhuma URL funcionou, mostrar o que está na página atual
        print(f"\n🔍 Analisando conteúdo da página atual...")
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        
        real_estate_links = []
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.text.lower()
                title = (link.get_attribute('title') or '').lower()
                
                if (href and 'olx.com.br' in href and 
                    any(word in href.lower() + text + title for word in ['apartamento', 'casa', 'kitnet', 'quarto', 'imovel', 'cobertura'])):
                    real_estate_links.append((href, text[:50]))
            except:
                continue
        
        print(f"📋 Links relacionados a imóveis encontrados: {len(real_estate_links)}")
        for i, (href, text) in enumerate(real_estate_links[:5]):
            print(f"   {i+1}. {href} | {text}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_specific_urls()
