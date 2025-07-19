#!/usr/bin/env python3
"""
Demo Simplificado dos Scrapers - Versão Windows Otimizada
Testa todos os scrapers individualmente com logging otimizado
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

# Importa configuração de logging otimizada
from utils.windows_logging import setup_windows_logging, log_info, log_error, log_warning

# Configura logging antes de importar outros módulos
setup_windows_logging()

# Importa scrapers
from backend.scrapers.vivareal_scraper import VivaRealScraper
from backend.scrapers.olx_scraper import OLXScraper
from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper

def test_vivareal():
    """Testa o scraper VivaReal"""
    log_info("=== TESTANDO VIVAREAL ===")
    
    try:
        scraper = VivaRealScraper()
        url = "https://www.vivareal.com.br/venda/sp/sao-paulo/"
        
        log_info(f"Buscando em: {url}")
        properties = scraper.scrape_properties(url, max_properties=2, max_pages=1)
        
        if properties:
            log_info(f"VivaReal: {len(properties)} propriedades encontradas")
            return len(properties)
        else:
            log_warning("VivaReal: Nenhuma propriedade encontrada")
            return 0
            
    except Exception as e:
        log_error(f"Erro no VivaReal: {e}")
        return 0
    finally:
        try:
            scraper.close()
        except:
            pass

def test_olx():
    """Testa o scraper OLX"""
    log_info("=== TESTANDO OLX ===")
    
    try:
        scraper = OLXScraper()
        url = "https://www.olx.com.br/imoveis/venda/apartamentos/estado-rj/rio-de-janeiro"
        
        log_info(f"Buscando em: {url}")
        properties = scraper.scrape_properties(url, max_properties=2, max_pages=1)
        
        if properties:
            log_info(f"OLX: {len(properties)} propriedades encontradas")
            return len(properties)
        else:
            log_warning("OLX: Nenhuma propriedade encontrada")
            return 0
            
    except Exception as e:
        log_error(f"Erro no OLX: {e}")
        return 0
    finally:
        try:
            scraper.close()
        except:
            pass

def test_zapimoveis():
    """Testa o scraper ZapImóveis"""
    log_info("=== TESTANDO ZAPIMOVEIS ===")
    
    try:
        scraper = ZapImoveisScraper()
        url = "https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/"
        
        log_info(f"Buscando em: {url}")
        properties = scraper.scrape_properties(url, max_properties=2, max_pages=1)
        
        if properties:
            log_info(f"ZapImoveis: {len(properties)} propriedades encontradas")
            return len(properties)
        else:
            log_warning("ZapImoveis: Nenhuma propriedade encontrada")
            return 0
            
    except Exception as e:
        log_error(f"Erro no ZapImoveis: {e}")
        return 0
    finally:
        try:
            scraper.close()
        except:
            pass

def main():
    """Função principal do demo"""
    start_time = datetime.now()
    log_info("INICIANDO DEMO SIMPLIFICADO DOS SCRAPERS")
    log_info(f"Horario de inicio: {start_time.strftime('%H:%M:%S')}")
    log_info("=" * 60)
    
    results = {
        'vivareal': 0,
        'olx': 0,
        'zapimoveis': 0
    }
    
    # Testa cada scraper individualmente
    try:
        results['vivareal'] = test_vivareal()
        time.sleep(2)  # Pausa entre testes
        
        results['olx'] = test_olx()
        time.sleep(2)
        
        results['zapimoveis'] = test_zapimoveis()
        
    except KeyboardInterrupt:
        log_warning("Demo interrompido pelo usuario")
    except Exception as e:
        log_error(f"Erro geral no demo: {e}")
    
    # Relatório final
    end_time = datetime.now()
    duration = end_time - start_time
    
    log_info("=" * 60)
    log_info("RELATORIO FINAL DO DEMO")
    log_info("=" * 60)
    
    total_properties = sum(results.values())
    working_scrapers = sum(1 for count in results.values() if count > 0)
    
    for portal, count in results.items():
        status = "FUNCIONANDO" if count > 0 else "SEM DADOS"
        log_info(f"{portal.upper()}: {count} propriedades - {status}")
    
    log_info(f"SCRAPERS FUNCIONAIS: {working_scrapers}/3")
    log_info(f"TOTAL DE PROPRIEDADES: {total_properties}")
    log_info(f"DURACAO: {duration}")
    
    if working_scrapers == 3:
        log_info("TODOS OS SCRAPERS FUNCIONANDO!")
    elif working_scrapers > 0:
        log_info("ALGUNS SCRAPERS FUNCIONANDO")
    else:
        log_warning("NENHUM SCRAPER FUNCIONANDO")
    
    log_info("FIM DO DEMO")

if __name__ == "__main__":
    main()
