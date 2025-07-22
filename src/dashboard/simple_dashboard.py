"""
Dashboard Simplificado para Teste
"""
import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, jsonify

# Configurar o caminho do template
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Estatísticas do sistema (dados simulados)"""
    return jsonify({
        'uptime_hours': 2.5,
        'total_containers': 6,
        'available_containers': 4,
        'cpu_usage': random.uniform(30, 70),
        'memory_usage': random.uniform(40, 80),
        'redis_connected': False,
        'postgres_connected': False
    })

@app.route('/api/portals')
def get_portals():
    """Status dos portais (dados simulados)"""
    portals = {
        'zapimoveis': {
            'total_requests': random.randint(100, 500),
            'successful_requests': random.randint(80, 450),
            'success_rate': random.uniform(70, 95),
            'avg_response_time': random.uniform(1.5, 3.5),
            'properties_scraped': random.randint(50, 200),
            'blocked_requests': random.randint(0, 10),
            'health_status': 'good'
        },
        'olx': {
            'total_requests': random.randint(100, 500),
            'successful_requests': random.randint(80, 450),
            'success_rate': random.uniform(70, 95),
            'avg_response_time': random.uniform(1.5, 3.5),
            'properties_scraped': random.randint(50, 200),
            'blocked_requests': random.randint(0, 10),
            'health_status': 'fair'
        },
        'vivareal': {
            'total_requests': random.randint(100, 500),
            'successful_requests': random.randint(80, 450),
            'success_rate': random.uniform(70, 95),
            'avg_response_time': random.uniform(1.5, 3.5),
            'properties_scraped': random.randint(50, 200),
            'blocked_requests': random.randint(0, 10),
            'health_status': 'good'
        }
    }
    return jsonify(portals)

@app.route('/api/containers')
def get_containers():
    """Status dos containers"""
    return jsonify({
        'total_containers': 6,
        'available_containers': 4,
        'busy_containers': 2,
        'healthy_containers': 5
    })

@app.route('/api/logs')
def get_logs():
    """Logs recentes do sistema"""
    logs = []
    levels = ['INFO', 'WARNING', 'ERROR']
    messages = [
        'Scraping iniciado para ZapImóveis',
        'Rate limit aplicado para OLX',
        'Propriedade coletada com sucesso',
        'Conexão estabelecida com sucesso',
        'Timeout na requisição',
        'Captcha detectado no portal'
    ]
    
    for i in range(10):
        logs.append({
            'level': random.choice(levels),
            'message': random.choice(messages),
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify(logs)

@app.route('/api/alerts')
def get_alerts():
    """Alertas ativos"""
    alerts = []
    
    # Simular alguns alertas
    if random.random() > 0.7:
        alerts.append({
            'type': 'warning',
            'source': 'zapimoveis',
            'message': 'Taxa de sucesso abaixo do esperado',
            'timestamp': datetime.now().isoformat()
        })
    
    if random.random() > 0.8:
        alerts.append({
            'type': 'error',
            'source': 'system',
            'message': 'Alto uso de memória detectado',
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify(alerts)

@app.route('/api/performance')
def get_performance():
    """Dados de performance"""
    return jsonify({
        'timeline': {},
        'portal_performance': {},
        'system_performance': []
    })

if __name__ == '__main__':
    print("🚀 Dashboard Simplificado iniciado!")
    print("📊 Acesse: http://localhost:5001")
    print("⚠️  Usando dados simulados para demonstração")
    app.run(host='0.0.0.0', port=5001, debug=True)
