# tasks.py

# Adiciona o diretório backend ao path do Python
# para que ele possa encontrar os módulos como 'scrapers'
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.logging_config import setup_logging
setup_logging()

import logging
from celery import Celery
from celery.schedules import crontab
from functools import wraps

# Agora estas importações irão funcionar
from backend.scrapers.vivareal_scraper import VivaRealScraper
from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
from backend.scrapers.olx_scraper import OLXScraper
from utils.decorators import track_scraping_metrics
from prometheus_client import Counter, Histogram

from database import SessionLocal
from backend.services.data_processor import DataProcessorService

# --- DEFINIÇÃO DAS MÉTRICAS DO PROMETHEUS ---
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
    Tarefa que executa o scraper, monitora com métricas e salva os dados no banco.
    """
    scraper_map = {
        'VivaRealScraper': VivaRealScraper,
        'ZapImoveisScraper': ZapImoveisScraper,
        'OLXScraper': OLXScraper,
    }
    scraper_class = scraper_map.get(scraper_class_name)
    if not scraper_class:
        logging.error(f"Scraper class '{scraper_class_name}' não encontrada.")
        return

    scraper = scraper_class()

    @track_scraping_metrics(source=source_name, scraped_properties_counter=SCRAPED_PROPERTIES, scraping_duration_histogram=SCRAPING_DURATION, errors_counter=ERRORS)
    def decorated_scraper():
        # A URL de busca pode ser mais dinâmica no futuro
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

        if all_property_data:
            db_session = SessionLocal()
            try:
                processor = DataProcessorService(db_session=db_session)
                processor.process_and_save_properties(all_property_data)
                logging.info(f"Dados de {source_name} processados e salvos com sucesso.")
            finally:
                db_session.close()
        else:
            logging.info(f"Nenhum imóvel novo encontrado em {source_name} para salvar.")

    except Exception as e:
        logging.error(f"A tarefa de scraping para {source_name} falhou: {e}", exc_info=True)
    finally:
        scraper.close()

@celery_app.task
def daily_market_analysis():
    logging.info("Iniciando tarefa de análise diária do mercado.")
    # A lógica da análise viria aqui...

# --- AGENDAMENTO DAS TAREFAS (CELERY BEAT) ---
# ... (o agendamento continua igual)
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