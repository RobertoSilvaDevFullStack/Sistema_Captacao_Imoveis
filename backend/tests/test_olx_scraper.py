#!/usr/bin/env python3
# backend/tests/test_olx_scraper.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import json
from scrapers.olx_scraper import OLXScraper

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_olx_scraper():
    """Testa o scraper OLX com uma busca real"""
    scraper = None
    try:
        logging.info("Iniciando teste do OLX Scraper...")
        
        # URLs de teste - Rio de Janeiro, apartamentos para venda
        test_urls = [
            "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro",
            "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro/zona-sul"
        ]
        
        # Inicializa o scraper
        scraper = OLXScraper()
        
        for search_url in test_urls:
            try:
                logging.info(f"Testando URL: {search_url}")
                
                # Executa o scraping (limitado a 3 propriedades para teste)
                properties = scraper.scrape_properties(search_url, max_properties=3, max_pages=1)
                
                if properties:
                    logging.info(f"SUCESSO! Extraídos detalhes de {len(properties)} propriedades.")
                    
                    # Salva os dados em JSON para análise
                    filename = f'olx_test_data_{len(properties)}.json'
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(properties, f, ensure_ascii=False, indent=2)
                    
                    logging.info(f"Dados salvos em '{filename}'")
                    
                    # Mostra uma amostra dos dados
                    for i, prop in enumerate(properties, 1):
                        print(f"\n=== PROPRIEDADE OLX {i} ===")
                        print(f"Título: {prop.get('title', 'N/A')}")
                        print(f"Preço: {prop.get('price', 'N/A')}")
                        print(f"Quartos: {prop.get('bedrooms', 'N/A')}")
                        print(f"Banheiros: {prop.get('bathrooms', 'N/A')}")
                        print(f"Área: {prop.get('area', 'N/A')}")
                        print(f"Vagas: {prop.get('parking_spaces', 'N/A')}")
                        print(f"Endereço: {prop.get('address', 'N/A')}")
                        print(f"URL: {prop.get('url', 'N/A')}")
                    
                    break  # Se conseguir dados de uma URL, para o teste
                    
                else:
                    logging.warning(f"Nenhuma propriedade encontrada em {search_url}")
                    
            except Exception as e:
                logging.error(f"Erro ao testar URL {search_url}: {e}")
                continue
        
        logging.info("Teste OLX concluído!")
        
    except Exception as e:
        logging.error(f"Erro durante o teste OLX: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.close()
            logging.info("OLX Scraper fechado.")

if __name__ == "__main__":
    test_olx_scraper()
