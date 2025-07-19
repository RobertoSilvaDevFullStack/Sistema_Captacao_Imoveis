#!/usr/bin/env python3
# test_data_processor.py

import logging
import json
from backend.scrapers.vivareal_scraper import VivaRealScraper
from backend.services.data_processor_clean import PropertyDataProcessor

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_data_processing():
    """Testa o processamento de dados extraídos"""
    scraper = None
    try:
        logging.info("Iniciando teste de processamento de dados...")
        
        # URL de teste - São Paulo, apartamentos
        search_url = "https://www.vivareal.com.br/venda/sp/sao-paulo/"
        
        # Inicializa o scraper
        scraper = VivaRealScraper()
        
        # Executa o scraping para obter dados brutos
        raw_properties = scraper.get_property_data_from_listing(search_url)
        
        if raw_properties:
            logging.info(f"Obtidos {len(raw_properties)} propriedades brutas")
            
            # Inicializa o processador de dados
            processor = PropertyDataProcessor()
            
            # Processa os dados
            processed_properties = processor.process_properties_list(raw_properties)
            
            if processed_properties:
                logging.info(f"SUCESSO! Processadas {len(processed_properties)} propriedades válidas")
                
                # Salva os dados processados
                with open('processed_properties_data.json', 'w', encoding='utf-8') as f:
                    json.dump(processed_properties, f, ensure_ascii=False, indent=2)
                
                logging.info("Dados processados salvos em 'processed_properties_data.json'")
                
                # Mostra comparação antes/depois
                print("\n" + "="*80)
                print("COMPARAÇÃO DADOS BRUTOS vs PROCESSADOS")
                print("="*80)
                
                for i, (raw, processed) in enumerate(zip(raw_properties[:3], processed_properties[:3]), 1):
                    print(f"\n--- PROPRIEDADE {i} ---")
                    print(f"BRUTO - Preço: {raw.get('price', 'N/A')[:50]}...")
                    print(f"PROCESSADO - Preço: R$ {processed.get('price', 'N/A'):,}")
                    print(f"BRUTO - Quartos: {raw.get('bedrooms', 'N/A')[:50]}...")
                    print(f"PROCESSADO - Quartos: {processed.get('bedrooms', 'N/A')}")
                    print(f"BRUTO - Área: {raw.get('area', 'N/A')[:50]}...")
                    print(f"PROCESSADO - Área: {processed.get('area', 'N/A')} m²")
                    print(f"PROCESSADO - Bairro: {processed.get('neighborhood', 'N/A')}")
                    print(f"PROCESSADO - Tipo: {processed.get('property_type', 'N/A')}")
                    print(f"PROCESSADO - Preço/m²: R$ {processed.get('price_per_sqm', 'N/A')}")
                    print(f"PROCESSADO - Válido: {processed.get('is_valid', False)}")
                
                # Estatísticas gerais
                print(f"\n" + "="*50)
                print("ESTATÍSTICAS")
                print("="*50)
                
                valid_count = len(processed_properties)
                total_price = sum(p['price'] for p in processed_properties if p['price'])
                avg_price = total_price / valid_count if valid_count > 0 else 0
                
                total_area = sum(p['area'] for p in processed_properties if p['area'])
                avg_area = total_area / valid_count if valid_count > 0 else 0
                
                avg_price_per_sqm = sum(p['price_per_sqm'] for p in processed_properties if p['price_per_sqm']) / valid_count if valid_count > 0 else 0
                
                print(f"Total de propriedades válidas: {valid_count}")
                print(f"Preço médio: R$ {avg_price:,.2f}")
                print(f"Área média: {avg_area:.1f} m²")
                print(f"Preço médio por m²: R$ {avg_price_per_sqm:,.2f}")
                
                # Tipos de propriedades
                property_types = {}
                neighborhoods = {}
                
                for prop in processed_properties:
                    prop_type = prop.get('property_type', 'Não identificado')
                    neighborhood = prop.get('neighborhood', 'Não identificado')
                    
                    property_types[prop_type] = property_types.get(prop_type, 0) + 1
                    neighborhoods[neighborhood] = neighborhoods.get(neighborhood, 0) + 1
                
                print(f"\nTipos de propriedades:")
                for prop_type, count in sorted(property_types.items()):
                    print(f"  {prop_type}: {count}")
                
                print(f"\nBairros mais frequentes:")
                sorted_neighborhoods = sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True)
                for neighborhood, count in sorted_neighborhoods[:5]:
                    print(f"  {neighborhood}: {count}")
                
            else:
                logging.error("FALHA! Nenhuma propriedade válida após processamento.")
        else:
            logging.error("FALHA! Nenhuma propriedade bruta foi extraída.")
            
    except Exception as e:
        logging.error(f"Ocorreu um erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.close()
            logging.info("Scraper fechado.")

if __name__ == "__main__":
    test_data_processing()
