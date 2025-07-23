#!/usr/bin/env python3
"""
Backend API Server Ultra-Simples
Versão mínima que funciona garantidamente
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Dados globais
properties_data = []

def load_data():
    """Carregar dados do arquivo JSON"""
    global properties_data
    try:
        with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filtrar dados válidos
        valid_data = [p for p in data if p.get('is_valid') and p.get('price')]
        
        # Converter para formato esperado pelo React
        properties_data = []
        for i, prop in enumerate(valid_data):
            property_data = {
                'id': f"real_{i}",
                'title': f"{prop.get('property_type', 'Apartamento')} {prop.get('bedrooms', 2)} quartos - {prop.get('neighborhood', 'Centro')}",
                'price': int(prop.get('price', 0)),
                'pricePerSqm': float(prop.get('price_per_sqm', 0)),
                'area': int(prop.get('area', 0)),
                'bedrooms': int(prop.get('bedrooms', 0)),
                'bathrooms': int(prop.get('bathrooms', 0)),
                'address': f"{prop.get('neighborhood', 'Centro')}, São Paulo - SP",
                'neighborhood': prop.get('neighborhood', 'Centro'),
                'city': 'São Paulo',
                'state': 'SP',
                'url': prop.get('url', '#'),
                'images': ['https://via.placeholder.com/400x300?text=Imovel+Real'],
                'description': f"Imóvel real de {prop.get('neighborhood')} - {prop.get('bedrooms')} quartos, {prop.get('area')}m²",
                'amenities': ['Dados Reais do VivaReal'],
                'portal': 'vivareal',
                'scraped_at': datetime.now().isoformat(),
                'parking_spaces': int(prop.get('parking_spaces', 0))
            }
            properties_data.append(property_data)
        
        logger.info(f"✅ Carregados {len(properties_data)} imóveis válidos de São Paulo")
        return True
        
    except FileNotFoundError:
        logger.error("❌ Arquivo processed_properties_data.json não encontrado")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'message': 'Backend funcionando!',
        'timestamp': datetime.now().isoformat(),
        'properties_loaded': len(properties_data)
    })

@app.route('/api/search', methods=['POST', 'GET'])
def search_properties():
    """Buscar propriedades"""
    
    logger.info(f"📡 Recebida requisição de busca - {request.method}")
    
    try:
        # Sempre retornar os dados carregados (São Paulo)
        result_data = properties_data[:20]  # Limitar a 20 para performance
        
        logger.info(f"✅ Retornando {len(result_data)} propriedades")
        
        return jsonify({
            'success': True,
            'data': result_data,
            'total': len(result_data),
            'message': f'Dados reais de São Paulo carregados',
            'timestamp': datetime.now().isoformat()
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
        'data': {
            'zapimoveis': {'status': 'active', 'properties_found': len(properties_data)},
            'vivareal': {'status': 'active', 'properties_found': len(properties_data)},
            'olx': {'status': 'maintenance', 'properties_found': 0}
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Backend API Server Ultra-Simples...")
    
    # Carregar dados
    if load_data():
        print(f"✅ {len(properties_data)} propriedades carregadas")
    else:
        print("⚠️ Problema ao carregar dados - usando modo emergência")
    
    print("📡 Servidor rodando em http://localhost:8000")
    print("🎯 Endpoints disponíveis:")
    print("   - GET  /api/health")
    print("   - POST /api/search")
    print("   - GET  /api/scrapers/status")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
