#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# backend/main.py - Sistema de Captação de Imóveis

# Configurar encoding UTF-8 para Windows
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Adiciona o diretório raiz ao path
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

# Importações básicas
import logging
from flask import Flask, jsonify, request
from datetime import datetime
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar logging avançado
try:
    from utils.logging_config import setup_logging
    setup_logging()
    logger.info("Logging avançado configurado")
except Exception as e:
    logger.warning(f"Erro ao configurar logging avançado: {e}")

# Importar scrapers
try:
    from backend.scrapers.zapimoveis_simple import ZapImoveisSimple
    logger.info("ZapImoveisSimple importado com sucesso")
except Exception as e:
    logger.error(f"Erro ao importar ZapImoveisSimple: {e}")
    ZapImoveisSimple = None

# Inicializa a aplicação Flask
app = Flask(__name__)
logger.info("Aplicação Flask inicializada")

# Configurar CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/')
def index():
    """Rota principal para verificar se a API está no ar."""
    logger.info("A rota raiz ('/') foi acessada.")
    return jsonify({"status": "API do Sistema de Captação de Imóveis está funcionando!"})

@app.route('/api/properties/search', methods=['GET'])
def search_properties():
    """Buscar propriedades com filtros"""
    try:
        # Obter parâmetros da requisição
        city = request.args.get('city', 'rio-de-janeiro')
        property_type = request.args.get('property_type', 'apartamento') 
        portal = request.args.get('portal', 'zapimoveis')
        max_results = int(request.args.get('max_results', 20))
        
        logger.info(f"Buscando propriedades: {city}, {property_type}, {portal}")
        
        properties = []
        
        # Por enquanto, apenas ZapImóveis funcional
        if portal == 'zapimoveis' and ZapImoveisSimple:
            try:
                # Mapeamento de cidades do ZapImóveis
                city_mapping = {
                    'rio-de-janeiro': 'rj+rio-de-janeiro',
                    'sao-paulo': 'sp+sao-paulo', 
                    'belo-horizonte': 'mg+belo-horizonte',
                    'brasilia': 'df+brasilia',
                    'salvador': 'ba+salvador',
                    'fortaleza': 'ce+fortaleza',
                    'recife': 'pe+recife',
                    'curitiba': 'pr+curitiba',
                    'porto-alegre': 'rs+porto-alegre',
                    'manaus': 'am+manaus'
                }
                
                city_code = city_mapping.get(city, 'rj+rio-de-janeiro')
                
                # URL baseada no tipo de propriedade
                if property_type == 'apartamento':
                    url = f"https://www.zapimoveis.com.br/venda/apartamentos/{city_code}/"
                elif property_type == 'casa':
                    url = f"https://www.zapimoveis.com.br/venda/casas/{city_code}/"
                else:
                    url = f"https://www.zapimoveis.com.br/venda/apartamentos/{city_code}/"
                
                logger.info(f"Usando ZapImóveis Simple para: {url}")
                scraper = ZapImoveisSimple()
                properties = scraper.scrape_properties(url, max_results=min(max_results, 10))
                
                logger.info(f"ZapImóveis retornou {len(properties)} propriedades")
                
            except Exception as e:
                logger.error(f"Erro no ZapImóveis Simple: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                properties = []
        else:
            # Outros portais temporariamente desabilitados
            logger.info(f"Portal {portal} temporariamente indisponível")
            properties = []
        
        return jsonify({
            'success': True,
            'properties': properties,
            'total': len(properties),
            'filters': {
                'city': city,
                'property_type': property_type,
                'portal': portal
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na busca de propriedades: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'properties': []
        }), 500

@app.route('/api/scrapers/status', methods=['GET'])
def get_scrapers_status():
    """Status dos scrapers"""
    try:
        status = {
            'zapimoveis': {
                'status': 'active' if ZapImoveisSimple else 'error',
                'last_run': datetime.now().isoformat(),
                'description': 'Funcionando com scraper simplificado' if ZapImoveisSimple else 'Erro na importação'
            },
            'olx': {
                'status': 'maintenance', 
                'last_run': datetime.now().isoformat(),
                'description': 'Temporariamente desabilitado'
            },
            'vivareal': {
                'status': 'maintenance',
                'last_run': datetime.now().isoformat(), 
                'description': 'Temporariamente desabilitado'
            }
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status dos scrapers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    try:
        logger.info("Iniciando servidor Flask...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Erro ao inicializar o servidor: {e}")
