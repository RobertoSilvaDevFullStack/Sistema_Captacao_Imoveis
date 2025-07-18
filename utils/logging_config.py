import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            RotatingFileHandler('logs/scraper.log', maxBytes=10000000, backupCount=5),
            logging.StreamHandler()
        ]
    )