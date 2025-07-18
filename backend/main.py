# backend/main.py

# Adiciona o diretório raiz ao path para encontrar a pasta 'utils'
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_config import setup_logging
setup_logging()

import logging
from flask import Flask, jsonify, Response
from prometheus_client import generate_latest # Importação necessária para as métricas

# Inicializa a aplicação Flask
app = Flask(__name__)

# --- DEFINIÇÃO DAS ROTAS DA API ---

@app.route('/')
def index():
    """Rota principal para verificar se a API está no ar."""
    logging.info("A rota raiz ('/') foi acessada.")
    return jsonify({"status": "API do Sistema de Captação de Imóveis está funcionando!"})

# --- ROTA PARA MÉTRICAS DO PROMETHEUS ---
@app.route('/metrics')
def metrics():
    """Esta rota expõe as métricas coletadas para o Prometheus."""
    logging.info("A rota /metrics foi acessada para coletar métricas.")
    # Gera a resposta no formato de texto plano que o Prometheus espera
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')


@app.route('/api/market-overview', methods=['GET'])
def get_market_overview():
    """Rota para obter uma visão geral do mercado."""
    logging.info("Requisição recebida em /api/market-overview")
    try:
        return jsonify({"message": "Endpoint de visão geral do mercado."}) # Placeholder
    except Exception as e:
        logging.error(f"Erro ao processar /api/market-overview: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro interno."}), 500

@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    """Rota para listar oportunidades de investimento."""
    logging.info("Requisição recebida em /api/opportunities")
    try:
        return jsonify({"message": "Endpoint de oportunidades."}) # Placeholder
    except Exception as e:
        logging.error(f"Erro ao processar /api/opportunities: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro interno."}), 500

# Garante que o servidor Flask rode apenas quando o script é executado diretamente
if __name__ == '__main__':
    # O host '0.0.0.0' torna a aplicação acessível de fora do contêiner
    app.run(host='0.0.0.0', port=5000, debug=False)