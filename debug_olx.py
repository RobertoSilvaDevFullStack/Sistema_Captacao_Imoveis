#!/usr/bin/env python3
"""
Teste específico para depuração do OLX - Identifica seletores corretos
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from utils.windows_logging import setup_windows_logging, log_info, log_error, log_warning

# Configura logging
setup_windows_logging()

from backend.scrapers.olx_scraper import OLXScraper

def debug_olx():
    """Debug específico do OLX"""
    log_info("=== DEBUG OLX SELETORES ===")
    
    try:
        scraper = OLXScraper()
        url = "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro"
        
        log_info(f"Acessando: {url}")
        scraper.driver.get(url)
        
        import time
        time.sleep(5)
        
        # Analisa a estrutura da página
        log_info("Analisando estrutura da página...")
        
        # Busca todos os links
        from selenium.webdriver.common.by import By
        all_links = scraper.driver.find_elements(By.TAG_NAME, 'a')
        log_info(f"Total de links na página: {len(all_links)}")
        
        # Filtra links que podem ser de anúncios
        potential_ad_links = []
        for link in all_links:
            href = link.get_attribute('href')
            if href and 'olx.com.br' in href:
                if '/ad/' in href or '/imovel/' in href or any(word in href.lower() for word in ['apartamento', 'casa', 'quarto']):
                    potential_ad_links.append(href)
        
        log_info(f"Links potenciais de anúncios: {len(potential_ad_links)}")
        
        # Mostra alguns exemplos
        for i, link in enumerate(potential_ad_links[:5]):
            log_info(f"Link {i+1}: {link}")
        
        # Testa diferentes seletores
        test_selectors = [
            'a[href*="/ad/"]',
            'a[data-lurker*="list_ad"]',
            '[data-testid*="ad"] a',
            '.sc-bxivhb a',
            'a[data-ds-component="DS-Link"]'
        ]
        
        for selector in test_selectors:
            try:
                elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                log_info(f"Seletor '{selector}': {len(elements)} elementos")
                
                if elements:
                    # Mostra exemplo do primeiro elemento
                    first_elem = elements[0]
                    href = first_elem.get_attribute('href')
                    text = first_elem.text.strip()[:50]
                    log_info(f"  Exemplo: {href} | Texto: {text}")
                    
            except Exception as e:
                log_error(f"Erro com seletor '{selector}': {e}")
        
        # Salva HTML para análise
        try:
            with open('olx_debug_page.html', 'w', encoding='utf-8') as f:
                f.write(scraper.driver.page_source)
            log_info("HTML da página salvo em 'olx_debug_page.html'")
        except:
            pass
        
        return len(potential_ad_links)
        
    except Exception as e:
        log_error(f"Erro no debug OLX: {e}")
        return 0
    finally:
        try:
            scraper.close()
        except:
            pass

def main():
    start_time = datetime.now()
    log_info("INICIANDO DEBUG DO OLX")
    log_info("=" * 50)
    
    result = debug_olx()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    log_info("=" * 50)
    log_info(f"DEBUG CONCLUÍDO - {result} links encontrados")
    log_info(f"DURAÇÃO: {duration}")

if __name__ == "__main__":
    main()
