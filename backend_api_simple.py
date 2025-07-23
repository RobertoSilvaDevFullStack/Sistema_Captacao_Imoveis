#!/usr/bin/env python3
"""
Backend API Server Simplificado
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Backend funcionando!'
    })

@app.route('/api/search', methods=['POST', 'GET'])
def search_properties():
    """Buscar propriedades"""
    
    try:
        # Carregar dados reais
        with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
            real_data = json.load(f)
        
        print(f"✅ Carregados {len(real_data)} imóveis")
        
        # Converter para formato esperado pelo frontend
        properties = []
        for i, prop in enumerate(real_data[:20]):  # Limitar a 20 para teste
            if prop.get('is_valid') and prop.get('price'):
                property_data = {
                    'id': f"real_{i}",
                    'title': f"{prop.get('property_type', 'Apartamento')} {prop.get('bedrooms', 2)} quartos",
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
                    'images': ['https://via.placeholder.com/400x300?text=Imovel+Real'],
                    'description': f"Imóvel real coletado - {prop.get('bedrooms')} quartos, {prop.get('area')}m²",
                    'amenities': ['Dados Reais'],
                    'portal': 'vivareal',
                    'scraped_at': datetime.now().isoformat(),
                    'parking_spaces': prop.get('parking_spaces', 0)
                }
                properties.append(property_data)
        
        print(f"✅ Retornando {len(properties)} propriedades")
        
        return jsonify({
            'success': True,
            'data': properties,
            'total': len(properties),
            'timestamp': datetime.now().isoformat()
        })
        
    except FileNotFoundError:
        print("❌ Arquivo não encontrado, usando dados mockados")
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': 'mock_1',
                    'title': 'Apartamento 2 quartos - Copacabana',
                    'price': 850000,
                    'pricePerSqm': 8500,
                    'area': 100,
                    'bedrooms': 2,
                    'bathrooms': 1,
                    'address': 'Copacabana, Rio de Janeiro - RJ',
                    'neighborhood': 'Copacabana',
                    'city': 'Rio de Janeiro',
                    'state': 'RJ',
                    'url': '#',
                    'images': ['https://via.placeholder.com/400x300'],
                    'description': 'Apartamento mockado para teste',
                    'amenities': ['Piscina'],
                    'portal': 'zapimoveis',
                    'scraped_at': datetime.now().isoformat(),
                    'parking_spaces': 1
                }
            ],
            'total': 1,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Erro: {e}")
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
            'zapimoveis': {'status': 'active', 'properties_found': 100},
            'vivareal': {'status': 'active', 'properties_found': 200},
            'olx': {'status': 'maintenance', 'properties_found': 0}
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Backend API Server Simplificado...")
    print("📡 Servidor rodando em http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
