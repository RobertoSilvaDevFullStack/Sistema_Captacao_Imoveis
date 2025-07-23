#!/usr/bin/env python3
"""
Servidor Flask Mínimo para Teste
"""

from flask import Flask, jsonify
import json
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Test</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .good { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>🏠 Sistema Captação Imóveis - Dashboard Teste</h1>
        
        <div class="card">
            <h3>Status dos Containers</h3>
            <div id="containers">Carregando...</div>
        </div>
        
        <div class="card">
            <h3>APIs de Teste</h3>
            <ul>
                <li><a href="/api/test">Teste Básico</a></li>
                <li><a href="/api/containers">Status Containers</a></li>
                <li><a href="/api/redis">Teste Redis</a></li>
                <li><a href="/api/selenium">Teste Selenium</a></li>
            </ul>
        </div>

        <script>
            // Testar containers
            fetch('/api/containers')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('containers').innerHTML = 
                        '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                })
                .catch(e => {
                    document.getElementById('containers').innerHTML = 
                        '<span class="error">Erro: ' + e.message + '</span>';
                });
        </script>
    </body>
    </html>
    '''

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat(),
        'message': 'API funcionando!'
    })

@app.route('/api/containers')
def api_containers():
    try:
        import docker
        client = docker.from_env()
        containers = []
        
        for container in client.containers.list():
            containers.append({
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else 'unknown'
            })
        
        return jsonify({
            'status': 'success',
            'containers': containers,
            'total': len(containers)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/redis')
def api_redis():
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        
        return jsonify({
            'status': 'success',
            'message': 'Redis conectado com sucesso!'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/selenium')
def api_selenium():
    try:
        import requests
        response = requests.get('http://localhost:4444/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'status': 'success',
                'selenium_data': data,
                'ready': data.get('value', {}).get('ready', False)
            })
        else:
            return jsonify({
                'status': 'error',
                'error': f'HTTP {response.status_code}'
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 Servidor de Teste iniciado!")
    print("🌐 Acesse: http://localhost:5000")
    print("🔍 APIs disponíveis:")
    print("   - /api/test")
    print("   - /api/containers") 
    print("   - /api/redis")
    print("   - /api/selenium")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
