import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# 1. Pega a URL do banco de dados a partir das variáveis de ambiente
# O valor padrão é para um banco SQLite local, útil para testes rápidos fora do Docker.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_database.db")

try:
    # 2. Cria o "motor" (engine) do SQLAlchemy
    # Este é o ponto de partida para qualquer aplicação SQLAlchemy.
    # Ele gerencia as conexões com o banco de dados.
    # O 'pool_pre_ping=True' verifica se as conexões estão ativas antes de usá-las.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    # 3. Cria uma classe de sessão configurada
    # Cada instância de SessionLocal será uma nova sessão com o banco de dados.
    # Uma sessão é a principal interface para persistir e consultar objetos no banco.
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 4. Cria uma classe Base para os modelos
    # Todos os seus modelos de tabela (como Property, Analysis) irão herdar desta classe.
    # É assim que o SQLAlchemy sabe quais classes correspondem a quais tabelas.
    Base = declarative_base()

    logging.info("Conexão com o banco de dados e sessão SQLAlchemy configuradas com sucesso.")

except Exception as e:
    logging.error(f"Erro ao configurar a conexão com o banco de dados: {e}", exc_info=True)
    # Em caso de falha, definimos como None para evitar erros em cascata
    engine = None
    SessionLocal = None
    Base = None

def get_db():
    """
    Função para ser usada como dependência para obter uma sessão do banco de dados.
    Garante que a sessão seja sempre fechada após o uso.
    """
    if SessionLocal is None:
        logging.error("A sessão do banco de dados não está disponível.")
        return
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Função para criar todas as tabelas no banco de dados.
    Ela importa todos os modelos antes de chamar create_all para garantir que
    eles sejam registrados no metadata do SQLAlchemy.
    """
    if Base is None or engine is None:
        logging.error("Não foi possível inicializar o banco de dados pois a configuração falhou.")
        return
        
    try:
        logging.info("Inicializando o banco de dados e criando tabelas...")
        # Importe seus modelos aqui para que eles sejam registrados
        import backend.models.property
        import backend.models.analysis
        
        Base.metadata.create_all(bind=engine)
        logging.info("Tabelas criadas com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao criar as tabelas do banco de dados: {e}", exc_info=True)