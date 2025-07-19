#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Test main.py simplificado
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from flask import Flask, jsonify, request
from datetime import datetime

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configurar CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Configurar logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    """Rota principal para verificar se a API está no ar."""
    logging.info("A rota raiz ('/') foi acessada.")
    return jsonify({"status": "API do Sistema de Captação de Imóveis está funcionando!"})

@app.route('/test')
def test():
    return jsonify({"message": "Test route working!"})

if __name__ == '__main__':
    try:
        logging.info("Iniciando servidor Flask...")
        app.run(host='0.0.0.0', port=5001, debug=True)  # Porta 5001 para não conflitar
    except Exception as e:
        logging.error(f"Erro ao inicializar o servidor: {e}")
