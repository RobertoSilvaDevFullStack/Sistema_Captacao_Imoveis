# init_database.py
import logging
from database import init_db
from utils.logging_config import setup_logging

# Configura o sistema de logging para ver as mensagens
setup_logging()

if __name__ == "__main__":
    logging.info("Iniciando o script de criação do banco de dados...")
    init_db()
    logging.info("Script de criação do banco de dados finalizado.")