#!/usr/bin/env python3
"""
Dashboard Simplificado para Monitoramento
Versão que funciona com os containers atuais
"""

from flask import Flask, render_template, jsonify
import redis
import json
import time
import docker
from datetime import datetime
import subprocess

app = Flask(__name__)

class SimpleDashboard:
    """Dashboard simplificado"""
    
    def __init__(self):
        self.redis_client = None
        self.docker_client = None
        self.start_time = datetime.now()
        
        # Tentar conectar Redis
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
            print("✅ Redis conectado")
        except Exception as e:
            print(f"⚠️  Redis não conectado: {e}")
        
        # Tentar conectar Docker
        try:
            self.docker_client = docker.from_env()
            print("✅ Docker conectado")
        except Exception as e:
            print(f"⚠️  Docker não conectado: {e}")
    
    def get_system_stats(self):
        """Estatísticas básicas do sistema"""
        uptime = datetime.now() - self.start_time
        uptime_hours = uptime.total_seconds() / 3600
        
        stats = {
            'uptime_hours': round(uptime_hours, 1),
            'redis_connected': self.redis_client is not None,
            'postgres_connected': False,  # Simplificado por enquanto
            'containers_running': 0,
            'total_containers': 0
        }
        
        # Verificar containers Docker
        if self.docker_client:
            try:
                containers = self.docker_client.containers.list()
                stats['containers_running'] = len([c for c in containers if c.status == 'running'])
                stats['total_containers'] = len(containers)
            except:
                pass
        
        return stats
    
    def get_portal_stats(self):
        """Estatísticas dos portais"""
        portals = ['zapimoveis', 'vivareal', 'olx']
        portal_stats = {}
        
        for portal in portals:
            stats = {
                'portal': portal,
                'total_requests': 0,
                'successful_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'properties_scraped': 0,
                'blocked_requests': 0,
                'health_status': 'unknown'
            }
            
            # Tentar buscar do Redis
            if self.redis_client:
                try:
                    key = f"{portal}:stats"
                    data = self.redis_client.hgetall(key)
                    if data:
                        stats.update({
                            'total_requests': int(data.get('total_requests', 0)),
                            'successful_requests': int(data.get('successful_requests', 0)),
                            'properties_scraped': int(data.get('properties_scraped', 0)),
                            'blocked_requests': int(data.get('blocked_requests', 0))
                        })
                        
                        if stats['total_requests'] > 0:
                            stats['success_rate'] = (stats['successful_requests'] / stats['total_requests']) * 100
                            stats['health_status'] = 'good' if stats['success_rate'] > 80 else 'warning'
                except:
                    pass
            
            portal_stats[portal] = stats
        
        return portal_stats
    
    def get_container_status(self):
        """Status dos containers"""
        containers = []
        
        if self.docker_client:
            try:
                for container in self.docker_client.containers.list():
                    containers.append({
                        'name': container.name,
                        'image': container.image.tags[0] if container.image.tags else 'unknown',
                        'status': container.status,
                        'ports': container.ports
                    })
            except Exception as e:
                print(f"Erro ao buscar containers: {e}")
        
        return containers
    
    def check_selenium_grid(self):
        """Verifica status do Selenium Grid"""
        try:
            import requests
            response = requests.get('http://localhost:4444/status', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'online',
                    'ready': data.get('value', {}).get('ready', False),
                    'nodes': len(data.get('value', {}).get('nodes', []))
                }
        except:
            pass
        
        return {'status': 'offline', 'ready': False, 'nodes': 0}

# Instância global
dashboard = SimpleDashboard()

@app.route('/')
def index():
    """Página principal"""
    return render_template('simple_dashboard.html')

@app.route('/api/stats')
def api_stats():
    """API - Estatísticas gerais"""
    try:
        return jsonify({
            'system': dashboard.get_system_stats(),
            'selenium_grid': dashboard.check_selenium_grid(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portals')
def api_portals():
    """API - Estatísticas dos portais"""
    try:
        return jsonify(dashboard.get_portal_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/containers')
def api_containers():
    """API - Status dos containers"""
    try:
        return jsonify(dashboard.get_container_status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """API - Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'uptime': (datetime.now() - dashboard.start_time).total_seconds()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard Simplificado...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 APIs:")
    print("   - /api/stats - Estatísticas do sistema")
    print("   - /api/portals - Status dos portais")
    print("   - /api/containers - Status dos containers")
    print("   - /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
