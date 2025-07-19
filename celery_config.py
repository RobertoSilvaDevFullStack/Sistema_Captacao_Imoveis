# celery_config.py

import os

# URL do Broker (Redis)
# Pega a URL do Redis a partir das variáveis de ambiente definidas no docker-compose.yml
broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# URL do Backend de Resultados (Opcional, mas recomendado)
# Vamos usar o banco de dados PostgreSQL para guardar os resultados das tarefas.
# Isso é útil para consultar o status ou o resultado de uma tarefa que já foi executada.
result_backend = os.getenv("DATABASE_URL", "sqlite:///./local_database.db").replace("postgresql://", "db+postgresql://")

# Configurações de serialização
# Define como os dados das tarefas são serializados (convertidos) para serem enviados
# através da rede. 'json' é uma escolha segura e padrão.
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# Fuso horário
# Importante para que o agendamento do Celery Beat funcione corretamente.
timezone = 'America/Sao_Paulo'
enable_utc = True