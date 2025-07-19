# init_database.py
import logging
from database import init_db
from utils.logging_config import setup_logging

# Configura o sistema de logging para ver as mensagens
setup_logging()

def create_database_tables():
    """Cria todas as tabelas do banco de dados"""
    try:
        logging.info("Iniciando criação das tabelas do banco de dados...")
        
        # Importa os modelos para garantir que estejam registrados
        from backend.models.property import Property, PropertyPriceHistory, PropertyAnalysis
        logging.info("Modelos importados: Property, PropertyPriceHistory, PropertyAnalysis")
        
        # Cria as tabelas
        init_db()
        logging.info("✅ Tabelas criadas com sucesso!")
        
        # Verifica as tabelas criadas
        from database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logging.info(f"📊 Tabelas no banco: {tables}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    success = create_database_tables()
    if success:
        logging.info("🎉 Banco de dados inicializado com sucesso!")
    else:
        logging.error("💥 Falha na inicialização do banco de dados!")