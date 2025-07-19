#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print("Paths configurados:")
print(f"Current dir: {current_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    from backend.scrapers.zapimoveis_simple import ZapImoveisSimple
    print("✅ Import ZapImoveisSimple OK")
    
    # Teste do scraper
    scraper = ZapImoveisSimple()
    url = 'https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/'
    properties = scraper.scrape_properties(url, max_results=2)
    print(f"✅ Scraper funcionou: {len(properties)} propriedades")
    
except Exception as e:
    print(f"❌ Erro no import/teste: {e}")
    import traceback
    traceback.print_exc()

# Agora testar Flask
try:
    from flask import Flask, jsonify, request
    print("✅ Flask importado")
    
    app = Flask(__name__)
    
    @app.route('/test')
    def test():
        return jsonify({"status": "OK", "message": "Teste funcionando"})
    
    @app.route('/api/properties/search', methods=['GET'])
    def search_properties():
        try:
            scraper = ZapImoveisSimple()
            url = 'https://www.zapimoveis.com.br/venda/apartamentos/rj+rio-de-janeiro/'
            properties = scraper.scrape_properties(url, max_results=3)
            
            return jsonify({
                'success': True,
                'properties': properties,
                'total': len(properties)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'properties': []
            }), 500
    
    print("✅ Flask app criado")
    print("🚀 Iniciando servidor de teste na porta 5002...")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
    
except Exception as e:
    print(f"❌ Erro no Flask: {e}")
    import traceback
    traceback.print_exc()
