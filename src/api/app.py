# src/api/app.py
"""
Aplicação Flask principal
"""
import os
import sys
import logging
from flask import Flask
from flask_cors import CORS

# Configurar encoding UTF-8 para Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from api.routes import api_bp

def create_app() -> Flask:
    """Factory para criar aplicação Flask"""
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Criar aplicação
    app = Flask(__name__)
    
    # Configurar CORS
    if settings.API.cors_enabled:
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Rota raiz
    @app.route('/')
    def index():
        return {
            "status": "API do Sistema de Captação de Imóveis está funcionando!",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=settings.API.host,
        port=settings.API.port,
        debug=settings.API.debug
    )
