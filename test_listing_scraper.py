#!/usr/bin/env python3
# test_listing_scraper.py

import logging
import json
from backend.scrapers.vivareal_scraper import VivaRealScraper

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def run_listing_test():
    """Testa o scraping direto da página de listagem"""
    scraper = None
    try:
        logging.info("Iniciando teste do scraping da página de listagem...")
        
        # URL de teste - São Paulo, apartamentos
        search_url = "https://www.vivareal.com.br/venda/sp/sao-paulo/"
        
        # Inicializa o scraper
        scraper = VivaRealScraper()
        
        # Executa o scraping direto da listagem
        properties = scraper.get_property_data_from_listing(search_url)
        
        if properties:
            logging.info(f"SUCESSO! Extraídos dados de {len(properties)} propriedades da listagem.")
            
            # Salva os dados em JSON para análise
            with open('properties_listing_data.json', 'w', encoding='utf-8') as f:
                json.dump(properties, f, ensure_ascii=False, indent=2)
            
            logging.info("Dados salvos em 'properties_listing_data.json'")
            
            # Mostra uma amostra dos dados
            for i, prop in enumerate(properties[:5], 1):  # Mostra apenas os primeiros 5
                print(f"\n=== PROPRIEDADE {i} ===")
                print(f"Preço: {prop.get('price', 'N/A')}")
                print(f"Quartos: {prop.get('bedrooms', 'N/A')}")
                print(f"Banheiros: {prop.get('bathrooms', 'N/A')}")
                print(f"Área: {prop.get('area', 'N/A')}")
                print(f"Vagas: {prop.get('parking_spaces', 'N/A')}")
                print(f"Endereço: {prop.get('address', 'N/A')}")
                print(f"URL: {prop.get('url', 'N/A')[:100]}...")
        else:
            logging.error("FALHA! Nenhuma propriedade foi extraída.")
            
    except Exception as e:
        logging.error(f"Ocorreu um erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.close()
            logging.info("Scraper fechado.")

if __name__ == "__main__":
    run_listing_test()
