#!/usr/bin/env python3
"""
Backend API Server para o Dashboard React
Servidor principal que irá servir as APIs para o frontend React
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import time
from datetime import datetime
import threading
import json
import logging
from typing import Dict, List, Any

# Imports dos scrapers
try:
    from backend.scrapers.vivareal_scraper import VivaRealScraper
    from backend.scrapers.olx_scraper import OLXScraper
    from backend.scrapers.zapimoveis_scraper import ZapImoveisScraper
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Scrapers não disponíveis: {e}")
    SCRAPERS_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Permitir CORS para o React

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache global para resultados
cache = {
    'properties': [],
    'scrapers_status': {},
    'last_search': None,
    'search_filters': {}
}

# Status dos scrapers
scrapers_status = {
    'zapimoveis': {
        'status': 'active',
        'description': 'Operacional',
        'last_check': None,
        'properties_found': 0
    },
    'vivareal': {
        'status': 'active', 
        'description': 'Operacional',
        'last_check': None,
        'properties_found': 0
    },
    'olx': {
        'status': 'active',
        'description': 'Operacional', 
        'last_check': None,
        'properties_found': 0
    }
}

class PropertySearchService:
    """Serviço de busca de propriedades"""
    
    def __init__(self):
        self.scrapers = {}
        if SCRAPERS_AVAILABLE:
            self.initialize_scrapers()
    
    def initialize_scrapers(self):
        """Inicializar scrapers"""
        try:
            self.scrapers = {
                'zapimoveis': ZapImoveisScraper(),
                'vivareal': VivaRealScraper(),
                'olx': OLXScraper()
            }
            logger.info("✅ Scrapers inicializados")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar scrapers: {e}")
    
    async def search_properties(self, filters: Dict) -> List[Dict]:
        """Buscar propriedades com os filtros"""
        
        portal = filters.get('portal', 'zapimoveis')
        city = filters.get('city', 'rio-de-janeiro')
        property_type = filters.get('propertyType', 'apartamento')
        max_results = int(filters.get('maxResults', 20))
        
        logger.info(f"🔍 Buscando {max_results} {property_type} em {city} via {portal}")
        
        properties = []
        
        if not SCRAPERS_AVAILABLE:
            # Retornar dados mockados se scrapers não disponíveis
            properties = self.get_mock_properties(max_results)
        else:
            try:
                scraper = self.scrapers.get(portal)
                if scraper:
                    # Executar busca assíncrona
                    async for prop in scraper.search_properties(
                        city=city,
                        property_type=property_type,
                        max_results=max_results
                    ):
                        properties.append(prop)
                        if len(properties) >= max_results:
                            break
                
                # Atualizar status
                scrapers_status[portal]['last_check'] = datetime.now().isoformat()
                scrapers_status[portal]['properties_found'] = len(properties)
                
            except Exception as e:
                logger.error(f"❌ Erro na busca {portal}: {e}")
                # Fallback para dados mockados
                properties = self.get_mock_properties(max_results)
        
        # Atualizar cache
        cache['properties'] = properties
        cache['last_search'] = datetime.now().isoformat()
        cache['search_filters'] = filters
        
        logger.info(f"✅ Busca concluída: {len(properties)} propriedades")
        return properties
    
    def get_mock_properties(self, max_results: int) -> List[Dict]:
        """Carregar propriedades dos dados já coletados ou gerar mockadas"""
        
        # Tentar carregar dados reais primeiro
        try:
            with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
                real_data = json.load(f)
            
            logger.info(f"📂 Carregados {len(real_data)} imóveis de dados reais")
            
            # Filtrar e limitar resultados
            filtered_data = []
            for prop in real_data[:max_results]:
                if prop.get('is_valid') and prop.get('price'):
                    filtered_data.append({
                        'id': f"real_{len(filtered_data)}",
                        'title': f"{prop.get('property_type', 'Imóvel')} {prop.get('bedrooms', 'N/A')} quartos - {prop.get('neighborhood', 'Centro')}",
                        'price': prop.get('price', 0),
                        'pricePerSqm': prop.get('price_per_sqm', 0),
                        'area': prop.get('area', 0),
                        'bedrooms': prop.get('bedrooms', 0),
                        'bathrooms': prop.get('bathrooms', 0),
                        'address': f"{prop.get('neighborhood', 'Centro')}, São Paulo - SP",
                        'neighborhood': prop.get('neighborhood', 'Centro'),
                        'city': 'São Paulo',
                        'state': 'SP',
                        'url': prop.get('url', '#'),
                        'images': ['https://via.placeholder.com/400x300?text=Imóvel+Real'],
                        'description': f"Imóvel coletado do VivaReal com {prop.get('bedrooms')} quartos e {prop.get('area')}m²",
                        'amenities': ['Dados Reais', 'Coletado via Scraper'],
                        'portal': 'vivareal',
                        'scraped_at': datetime.now().isoformat(),
                        'parking_spaces': prop.get('parking_spaces', 0)
                    })
            
            if filtered_data:
                logger.info(f"✅ Retornando {len(filtered_data)} imóveis reais")
                return filtered_data
                
        except FileNotFoundError:
            logger.info("📂 Arquivo de dados reais não encontrado, usando dados mockados")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados reais: {e}")
        
        # Fallback para dados mockados
        mock_properties = []
        
        for i in range(min(max_results, 10)):  # Máximo 10 mockados
            prop = {
                'id': f'mock_{i+1}',
                'title': f'Apartamento {i+1} Quartos - Excelente Localização',
                'price': 850000 + (i * 150000),
                'pricePerSqm': 8500 + (i * 500),
                'area': 100 + (i * 20),
                'bedrooms': (i % 4) + 1,
                'bathrooms': (i % 3) + 1,
                'address': f'Rua Example {i+1}, Copacabana - Rio de Janeiro/RJ',
                'neighborhood': 'Copacabana',
                'city': 'Rio de Janeiro',
                'state': 'RJ',
                'url': f'https://example.com/imovel/{i+1}',
                'images': [f'https://via.placeholder.com/400x300?text=Imóvel+{i+1}'],
                'description': f'Apartamento com {(i % 4) + 1} quartos em excelente localização. Vista mar, próximo ao metrô.',
                'amenities': ['Piscina', 'Academia', 'Portaria 24h', 'Salão de Festas'],
                'portal': 'zapimoveis',
                'scraped_at': datetime.now().isoformat(),
                'parking_spaces': (i % 3) + 1 if i % 2 == 0 else 0
            }
            mock_properties.append(prop)
        
        return mock_properties

# Instância do serviço
search_service = PropertySearchService()

# === ROUTES DA API ===

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'scrapers_available': SCRAPERS_AVAILABLE
    })

@app.route('/api/search', methods=['POST', 'GET'])
def search_properties():
    """Endpoint para buscar propriedades"""
    
    try:
        if request.method == 'POST':
            filters = request.get_json() or {}
        else:  # GET
            filters = {
                'city': request.args.get('city', 'rio-de-janeiro'),
                'propertyType': request.args.get('property_type', 'apartamento'),
                'portal': request.args.get('portal', 'zapimoveis'),
                'maxResults': int(request.args.get('max_results', 20))
            }
        
        # Executar busca assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        properties = loop.run_until_complete(
            search_service.search_properties(filters)
        )
        loop.close()
        
        return jsonify({
            'success': True,
            'data': properties,
            'filters': filters,
            'timestamp': datetime.now().isoformat(),
            'total': len(properties)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na busca: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/scrapers/status', methods=['GET'])
def get_scrapers_status():
    """Status dos scrapers"""
    
    return jsonify({
        'success': True,
        'data': scrapers_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Lista de cidades disponíveis"""
    
    cities = [
        {'code': 'rio-de-janeiro', 'name': 'Rio de Janeiro', 'state': 'RJ'},
        {'code': 'sao-paulo', 'name': 'São Paulo', 'state': 'SP'},
        {'code': 'belo-horizonte', 'name': 'Belo Horizonte', 'state': 'MG'},
        {'code': 'brasilia', 'name': 'Brasília', 'state': 'DF'},
        {'code': 'salvador', 'name': 'Salvador', 'state': 'BA'},
        {'code': 'fortaleza', 'name': 'Fortaleza', 'state': 'CE'},
        {'code': 'recife', 'name': 'Recife', 'state': 'PE'},
        {'code': 'porto-alegre', 'name': 'Porto Alegre', 'state': 'RS'},
        {'code': 'curitiba', 'name': 'Curitiba', 'state': 'PR'},
        {'code': 'florianopolis', 'name': 'Florianópolis', 'state': 'SC'}
    ]
    
    return jsonify({
        'success': True,
        'data': cities
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Estatísticas gerais"""
    
    stats = {
        'total_properties': len(cache['properties']),
        'last_search': cache['last_search'],
        'scrapers_active': sum(1 for s in scrapers_status.values() if s['status'] == 'active'),
        'total_scrapers': len(scrapers_status),
        'cache_size': len(cache['properties'])
    }
    
    return jsonify({
        'success': True,
        'data': stats,
        'timestamp': datetime.now().isoformat()
    })

# === INICIALIZAÇÃO ===

def run_background_tasks():
    """Tarefas em background"""
    while True:
        try:
            # Atualizar status dos scrapers periodicamente
            for portal in scrapers_status:
                scrapers_status[portal]['last_check'] = datetime.now().isoformat()
            
            time.sleep(60)  # A cada minuto
        except Exception as e:
            logger.error(f"Erro em background task: {e}")
            time.sleep(60)

if __name__ == '__main__':
    print("🚀 Iniciando Backend API Server...")
    print("📡 APIs disponíveis:")
    print("   - POST /api/search - Buscar propriedades")
    print("   - GET /api/scrapers/status - Status dos scrapers")
    print("   - GET /api/cities - Lista de cidades")
    print("   - GET /api/stats - Estatísticas")
    print("   - GET /api/health - Health check")
    print("\n🌐 Backend API: http://localhost:8000")
    print("🎯 Dashboard React: http://localhost:3000")
    print("📊 Dashboard Monitoramento: http://localhost:5000")
    
    # Iniciar tarefas em background
    background_thread = threading.Thread(target=run_background_tasks, daemon=True)
    background_thread.start()
    
    # Iniciar servidor Flask
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
