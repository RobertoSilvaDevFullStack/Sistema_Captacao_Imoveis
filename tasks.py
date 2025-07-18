# tasks.py

from utils.logging_config import setup_logging
setup_logging()

import logging
from celery import Celery
from celery.schedules import crontab
from functools import wraps

# Importações para as tarefas e métricas
from scrapers.vivareal_scraper import VivaRealScraper
from scrapers.zapimoveis_scraper import ZapImoveisScraper
from scrapers.olx_scraper import OLXScraper
from utils.decorators import track_scraping_metrics # Importando o decorator de métricas
from prometheus_client import Counter, Histogram # Importando as ferramentas do Prometheus

# --- DEFINIÇÃO DAS MÉTRICAS DO PROMETHEUS ---
# Estas métricas são definidas no escopo global para serem compartilhadas entre as tarefas
SCRAPED_PROPERTIES = Counter('scraped_properties_total', 'Total de imóveis coletados', ['source'])
SCRAPING_DURATION = Histogram('scraping_duration_seconds', 'Tempo gasto na coleta (em segundos)', ['source'])
ERRORS = Counter('scraping_errors_total', 'Total de erros na coleta', ['source', 'error_type'])


# --- CONFIGURAÇÃO DO CELERY ---
celery_app = Celery('real_estate_tasks')
celery_app.config_from_object('celery_config')


# --- DEFINIÇÃO DAS TAREFAS ---

@celery_app.task
def run_scraper_task(scraper_class_name, source_name):
    """
    Tarefa que executa o scraper e é monitorada pelo decorator de métricas.
    """
    scraper_map = {
        'VivaRealScraper': VivaRealScraper,
        'ZapImoveisScraper': ZapImoveisScraper,
        'OLXScraper': OLXScraper,
    }
    scraper_class = scraper_map.get(scraper_class_name)
    if not scraper_class:
        logging.error(f"Scraper class '{scraper_class_name}' não encontrada.")
        return []

    scraper = scraper_class()
    all_property_data = []

    # O decorator de métricas precisa ser aplicado dinamicamente aqui
    @track_scraping_metrics(source=source_name, scraped_properties_counter=SCRAPED_PROPERTIES, scraping_duration_histogram=SCRAPING_DURATION, errors_counter=ERRORS)
    def decorated_scraper():
        property_links = scraper.get_property_links(f"{scraper.base_url}/venda/sp/sao-paulo/")
        logging.info(f"Encontrados {len(property_links)} links em {source_name}.")
        
        local_data = []
        for link in property_links:
            data = scraper.extract_property_data(link)
            if data:
                local_data.append(data)
        return local_data

    try:
        all_property_data = decorated_scraper()
        logging.info(f"Tarefa de scraping para {source_name} concluída. Coletados {len(all_property_data)} imóveis.")
        # Aqui viria a lógica para salvar os dados no banco
        # processor.process_properties(all_property_data)
    except Exception as e:
        # O decorator já registrou o erro, mas logamos para ter o contexto completo.
        logging.error(f"A tarefa de scraping para {source_name} falhou: {e}", exc_info=True)
    finally:
        scraper.close()

@celery_app.task
def daily_market_analysis():
    logging.info("Iniciando tarefa de análise diária do mercado.")
    # Lógica da análise...

# --- AGENDAMENTO DAS TAREFAS (CELERY BEAT) ---

celery_app.conf.beat_schedule = {
    'scrape-vivareal-daily': {
        'task': 'tasks.run_scraper_task',
        'schedule': crontab(hour=8, minute=0),
        'args': ('VivaRealScraper', 'VivaReal'),
    },
    'scrape-zapimoveis-daily': {
        'task': 'tasks.run_scraper_task',
        'schedule': crontab(hour=10, minute=0),
        'args': ('ZapImoveisScraper', 'ZapImoveis'),
    },
    'scrape-olx-daily': {
        'task': 'tasks.run_scraper_task',
        'schedule': crontab(hour=12, minute=0),
        'args': ('OLXScraper', 'OLX'),
    },
    'daily-analysis': {
        'task': 'tasks.daily_market_analysis',
        'schedule': crontab(hour=18, minute=0),
    },
}