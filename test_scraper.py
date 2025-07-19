# test_scraper.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.scrapers.vivareal_scraper import VivaRealScraper
import logging

logging.basicConfig(level=logging.INFO)

def run_test():
    logging.info("Iniciando teste do VivaRealScraper...")
    scraper = VivaRealScraper()
    
    try:
        search_url = "https://www.vivareal.com.br/venda/sp/sao-paulo/"
        links = scraper.get_property_links(search_url)
        
        if links:
            logging.info(f"SUCESSO! Encontrados {len(links)} links.")
            logging.info("Amostra dos 3 primeiros links:")
            for link in links[:3]:
                print(link)
        else:
            logging.error("FALHA! Nenhum link de imóvel foi encontrado.")
            # Vamos guardar o HTML da página para análise
            page_html = scraper.driver.page_source
            with open("debug_vivareal.html", "w", encoding="utf-8") as f:
                f.write(page_html)
            logging.info("O HTML da página foi guardado em 'debug_vivareal.html'.")
            logging.info("Abra este ficheiro no seu navegador para ver o que o scraper viu e encontrar o seletor CSS correto.")

    except Exception as e:
        logging.error(f"Ocorreu um erro durante o teste: {e}", exc_info=True)
    finally:
        scraper.close()

if __name__ == "__main__":
    run_test()