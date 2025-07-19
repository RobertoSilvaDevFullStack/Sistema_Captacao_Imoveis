#!/usr/bin/env python3
# backend/services/multi_scraper_service.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from scrapers.vivareal_scraper import VivaRealScraper
from scrapers.olx_scraper import OLXScraper
from scrapers.zapimoveis_scraper import ZapImoveisScraper

class MultiScraperService:
    """Serviço que coordena todos os scrapers de imóveis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scrapers = {}
        self.results = {}
        
    def initialize_scrapers(self):
        """Inicializa todos os scrapers disponíveis"""
        try:
            self.logger.info("Inicializando scrapers...")
            
            # VivaReal
            try:
                self.scrapers['vivareal'] = VivaRealScraper()
                self.logger.info("✅ VivaReal Scraper inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar VivaReal: {e}")
            
            # OLX
            try:
                self.scrapers['olx'] = OLXScraper()
                self.logger.info("✅ OLX Scraper inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar OLX: {e}")
            
            # ZapImóveis
            try:
                self.scrapers['zapimoveis'] = ZapImoveisScraper()
                self.logger.info("✅ ZapImóveis Scraper inicializado")
            except Exception as e:
                self.logger.error(f"❌ Erro ao inicializar ZapImóveis: {e}")
                
            self.logger.info(f"Total de {len(self.scrapers)} scrapers inicializados")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar scrapers: {e}")

    def get_search_urls(self, location="rio-de-janeiro", property_type="apartamentos"):
        """Retorna URLs de busca para cada portal"""
        urls = {}
        
        # VivaReal URLs
        urls['vivareal'] = [
            f"https://www.vivareal.com.br/venda/{property_type}/rj/{location}/",
            f"https://www.vivareal.com.br/venda/{property_type}/rj/{location}/zona-sul/"
        ]
        
        # OLX URLs  
        urls['olx'] = [
            f"https://www.olx.com.br/imoveis/venda/{property_type}/estado-rj/{location}",
            f"https://www.olx.com.br/imoveis/venda/{property_type}/estado-rj/{location}/zona-sul"
        ]
        
        # ZapImóveis URLs
        urls['zapimoveis'] = [
            f"https://www.zapimoveis.com.br/venda/{property_type}/rj+{location}/",
            f"https://www.zapimoveis.com.br/venda/{property_type}/rj+{location}+zona-sul/"
        ]
        
        return urls

    def scrape_portal(self, portal_name: str, search_urls: List[str], max_properties=10, max_pages=2):
        """Executa scraping em um portal específico"""
        if portal_name not in self.scrapers:
            self.logger.error(f"Scraper {portal_name} não está disponível")
            return []
        
        scraper = self.scrapers[portal_name]
        all_properties = []
        
        for url in search_urls:
            try:
                self.logger.info(f"Scraping {portal_name}: {url}")
                
                # Método unificado para todos os scrapers
                if hasattr(scraper, 'scrape_properties'):
                    properties = scraper.scrape_properties(url, max_properties, max_pages)
                else:
                    # Fallback para scrapers com interface diferente
                    properties = scraper.scrape_properties(url)
                
                if properties:
                    all_properties.extend(properties)
                    self.logger.info(f"✅ {len(properties)} propriedades encontradas em {portal_name}")
                else:
                    self.logger.warning(f"⚠️ Nenhuma propriedade encontrada em {url}")
                    
                # Pausa entre URLs para evitar bloqueios
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Erro ao fazer scraping em {url}: {e}")
                continue
        
        self.logger.info(f"Total {portal_name}: {len(all_properties)} propriedades")
        return all_properties

    def scrape_all_portals(self, location="rio-de-janeiro", max_properties_per_portal=15):
        """Executa scraping em todos os portais disponíveis"""
        try:
            self.logger.info("=== INICIANDO SCRAPING MULTI-PORTAL ===")
            start_time = datetime.now()
            
            # Inicializa scrapers
            self.initialize_scrapers()
            
            if not self.scrapers:
                self.logger.error("Nenhum scraper disponível!")
                return {}
            
            # Obtém URLs de busca
            search_urls = self.get_search_urls(location)
            
            # Executa scraping em cada portal
            for portal_name in self.scrapers.keys():
                try:
                    self.logger.info(f"\n--- SCRAPING {portal_name.upper()} ---")
                    
                    portal_urls = search_urls.get(portal_name, [])
                    properties = self.scrape_portal(
                        portal_name, 
                        portal_urls, 
                        max_properties_per_portal,
                        max_pages=2
                    )
                    
                    self.results[portal_name] = properties
                    
                    # Pausa entre portais
                    time.sleep(10)
                    
                except Exception as e:
                    self.logger.error(f"Erro no portal {portal_name}: {e}")
                    self.results[portal_name] = []
                    continue
            
            # Relatório final
            end_time = datetime.now()
            duration = end_time - start_time
            
            total_properties = sum(len(props) for props in self.results.values())
            
            self.logger.info("\n=== RELATÓRIO FINAL ===")
            for portal, properties in self.results.items():
                self.logger.info(f"{portal.upper()}: {len(properties)} propriedades")
            self.logger.info(f"TOTAL: {total_properties} propriedades")
            self.logger.info(f"DURAÇÃO: {duration}")
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Erro durante scraping multi-portal: {e}")
            return {}

    def save_results(self, filename="multi_portal_properties.json"):
        """Salva todos os resultados em um arquivo JSON"""
        try:
            if not self.results:
                self.logger.warning("Nenhum resultado para salvar")
                return False
            
            # Prepara dados para salvar
            save_data = {
                'scraped_at': datetime.now().isoformat(),
                'total_properties': sum(len(props) for props in self.results.values()),
                'portals': {}
            }
            
            for portal, properties in self.results.items():
                save_data['portals'][portal] = {
                    'count': len(properties),
                    'properties': properties
                }
            
            # Salva no arquivo
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Resultados salvos em {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {e}")
            return False

    def get_consolidated_data(self):
        """Retorna dados consolidados de todos os portais"""
        all_properties = []
        
        for portal, properties in self.results.items():
            for prop in properties:
                # Garante que cada propriedade tenha a fonte identificada
                prop['source'] = portal
                all_properties.append(prop)
        
        return all_properties

    def close_all_scrapers(self):
        """Fecha todos os scrapers"""
        for name, scraper in self.scrapers.items():
            try:
                if hasattr(scraper, 'close'):
                    scraper.close()
                    self.logger.info(f"{name} scraper fechado")
            except Exception as e:
                self.logger.error(f"Erro ao fechar {name}: {e}")

# Função de teste principal
def run_multi_scraper_test():
    """Executa teste completo do multi-scraper"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    service = MultiScraperService()
    
    try:
        # Executa scraping em todos os portais
        results = service.scrape_all_portals(
            location="rio-de-janeiro",
            max_properties_per_portal=5  # Limite baixo para teste
        )
        
        if results:
            # Salva resultados
            service.save_results("test_multi_portal_results.json")
            
            # Mostra resumo
            print("\n=== RESUMO DOS DADOS COLETADOS ===")
            for portal, properties in results.items():
                print(f"\n{portal.upper()}:")
                for i, prop in enumerate(properties[:2], 1):  # Mostra apenas 2 por portal
                    print(f"  {i}. {prop.get('title', 'N/A')[:60]}...")
                    print(f"     Preço: {prop.get('price', 'N/A')}")
                    print(f"     Fonte: {prop.get('source', 'N/A')}")
        
    except Exception as e:
        logging.error(f"Erro no teste multi-scraper: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        service.close_all_scrapers()

if __name__ == "__main__":
    run_multi_scraper_test()
