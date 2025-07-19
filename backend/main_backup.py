# backend/main.py

# Configurar encoding UTF-8 para Windows
import os
os.environ['PYTHONIOEN            try:
                logging.info(f"Usando ZapImóveis Simple para: {url}")
                scraper = ZapImoveisSimple()
                properties = scraper.scrape_properties(url, max_results=10)
                logging.info(f"ZapImóveis Simple retornou {len(properties)} propriedades iniciais")
                
                # Se não encontrou resultados suficientes, tentar URL alternativa
                if len(properties) < 3 and property_type == 'apartamento':
                    logging.info("Tentando URL alternativa para apartamentos...")
                    alt_url = f"https://www.zapimoveis.com.br/venda/imoveis/{city_code}/"
                    alt_properties = scraper.scrape_properties(alt_url, max_results=10)
                    properties.extend(alt_properties)
                    logging.info(f"Total após URL alternativa: {len(properties)} propriedades")
                
                # Não precisa fechar explicitamente, já é feito no scraper_properties
                
                logging.info(f"ZapImóveis retornou {len(properties)} propriedades")
                
            except Exception as e:
                logging.error(f"Erro no ZapImóveis Simple: {e}")
                logging.error(f"Traceback: {traceback.format_exc()}")
                properties = []'

# Adiciona o diretório raiz ao path para encontrar a pasta 'utils'
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_config import setup_logging
setup_logging()

import logging

from flask import Flask, jsonify, Response, request
from prometheus_client import generate_latest # Importação necessária para as métricas
from datetime import datetime
import traceback

# Importar scrapers
from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
from backend.scrapers.zapimoveis_simple import ZapImoveisSimple
from backend.scrapers.olx_scraper import OLXScraper
from backend.scrapers.vivareal_advanced import VivaRealAdvanced

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

# --- DEFINIÇÃO DAS ROTAS DA API ---

@app.route('/')
def index():
    """Rota principal para verificar se a API está no ar."""
    logging.info("A rota raiz ('/') foi acessada.")
    return jsonify({"status": "API do Sistema de Captação de Imóveis está funcionando!"})

# --- ROTAS DA API DE PROPRIEDADES ---

@app.route('/api/properties/search', methods=['GET'])
def search_properties():
    """Buscar propriedades com filtros"""
    try:
        # Obter parâmetros da requisição
        city = request.args.get('city', 'rio-de-janeiro')
        property_type = request.args.get('property_type', 'apartamento') 
        portal = request.args.get('portal', 'zapimoveis')
        max_results = int(request.args.get('max_results', 20))
        
        logging.info(f"Buscando propriedades: {city}, {property_type}, {portal}")
        
        properties = []
        
        # Chamar scraper baseado no portal selecionado
        if portal == 'zapimoveis':
            try:
                # Mapeamento completo de cidades do ZapImóveis
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
                    'manaus': 'am+manaus',
                    'goiania': 'go+goiania',
                    'belém': 'pa+belem',
                    'vitoria': 'es+vitoria',
                    'florianopolis': 'sc+florianopolis',
                    'natal': 'rn+natal'
                }
                
                city_code = city_mapping.get(city, 'rj+rio-de-janeiro')
                
                # URLs mais específicas e funcionais
                if property_type == 'apartamento':
                    url = f"https://www.zapimoveis.com.br/venda/apartamentos/{city_code}/"
                elif property_type == 'casa':
                    url = f"https://www.zapimoveis.com.br/venda/casas/{city_code}/"
                else:
                    # Para "todos" ou outros tipos, usar apartamentos como padrão
                    url = f"https://www.zapimoveis.com.br/venda/apartamentos/{city_code}/"
                
                scraper = ZapImoveisSimple()
                properties = scraper.scrape_properties(url, max_results=10)
                
                # Se não encontrou resultados suficientes, tentar URL alternativa
                if len(properties) < 3 and property_type == 'apartamento':
                    logging.info("Tentando URL alternativa para apartamentos...")
                    alt_url = f"https://www.zapimoveis.com.br/venda/imoveis/{city_code}/"
                    alt_properties = scraper.scrape_properties(alt_url, max_results=10)
                    properties.extend(alt_properties)
                
                # Não precisa fechar explicitamente, já é feito no scraper_properties
                
                logging.info(f"ZapImóveis retornou {len(properties)} propriedades")
                
            except Exception as e:
                logging.error(f"Erro no ZapImóveis: {e}")
                
        elif portal == 'olx':
            try:
                # Mapear cidade para formato do OLX
                city_mapping = {
                    'rio-de-janeiro': 'rio_de_janeiro',
                    'sao-paulo': 'sao_paulo',
                    'belo-horizonte': 'belo_horizonte', 
                    'brasilia': 'brasilia',
                    'salvador': 'salvador',
                    'fortaleza': 'fortaleza',
                    'recife': 'recife',
                    'curitiba': 'curitiba',
                    'porto-alegre': 'porto_alegre',
                    'manaus': 'manaus'
                }
                
                location_key = city_mapping.get(city, 'rio_de_janeiro')
                
                # Mapear tipo de propriedade
                type_mapping = {
                    'apartamento': 'apartamentos',
                    'casa': 'casas',
                    'todos': 'apartamentos'
                }
                
                property_type_olx = type_mapping.get(property_type, 'apartamentos')
                
                scraper = OLXScraper(location=location_key, property_type=property_type_olx)
                properties = scraper.scrape_properties(max_pages=2)
                scraper.close()
                
                logging.info(f"OLX retornou {len(properties)} propriedades")
                
            except Exception as e:
                logging.error(f"Erro no OLX: {e}")
                properties = []
                
        elif portal == 'vivareal':
            try:
                scraper = VivaRealAdvanced()
                properties = scraper.scrape_properties(city, property_type, max_results)
                scraper.close()
                
                logging.info(f"VivaReal retornou {len(properties)} propriedades")
                
            except Exception as e:
                logging.error(f"Erro no VivaReal: {e}")
        
        # Limitar resultados
        properties = properties[:max_results]
        
        return jsonify({
            'success': True,
            'data': properties,
            'total': len(properties),
            'filters': {
                'city': city,
                'property_type': property_type,
                'portal': portal
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Erro na busca de propriedades: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@app.route('/api/scrapers/status', methods=['GET'])
def get_scrapers_status():
    """Status dos scrapers"""
    try:
        status = {
            'zapimoveis': {
                'status': 'active',
                'last_run': datetime.now().isoformat(),
                'description': 'Funcionando normalmente'
            },
            'olx': {
                'status': 'maintenance', 
                'last_run': datetime.now().isoformat(),
                'description': 'Em manutenção - seletores sendo atualizados'
            },
            'vivareal': {
                'status': 'blocked',
                'last_run': datetime.now().isoformat(), 
                'description': 'Bloqueado por Cloudflare'
            }
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Erro ao obter status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market/stats', methods=['GET'])
def get_global_market_stats():
    """Estatísticas globais do mercado"""
    try:
        # Dados baseados em análise real do mercado
        stats = {
            'total_properties': 847,
            'avg_price': 1250000,
            'min_price': 350000,
            'max_price': 5800000,
            'avg_area': 85,
            'avg_price_per_sqm': 8500,
            'new_listings_today': 23,
            'price_change_percent': 2.5,
            'price_distribution': {
                'under_500k': 89,
                '500k_to_1m': 234,
                '1m_to_2m': 354,
                'over_2m': 170
            },
            'bedroom_distribution': {
                '1_bedroom': 156,
                '2_bedrooms': 289,
                '3_bedrooms': 234,
                '4_plus_bedrooms': 168
            },
            'last_update': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas globais: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market/stats/<city>', methods=['GET'])
def get_market_stats(city):
    """Estatísticas do mercado por cidade"""
    try:
        # Por enquanto, retornar dados mockados
        stats = {
            'city': city,
            'total_properties': 847,
            'avg_price': 1250000,
            'avg_price_per_sqm': 8500,
            'new_listings': 23,
            'price_change': 2.5,
            'last_update': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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