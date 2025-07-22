#!/usr/bin/env python3
"""
Dashboard de Monitoramento Simplificado para Sistema de Scraping
Versão independente que funciona sem dependências externas complexas
"""
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
from flask import Flask, render_template_string, jsonify, request
import os
import psutil

@dataclass
class SystemStats:
    """Estatísticas básicas do sistema"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    uptime_hours: float = 0.0
    active_processes: int = 0
    timestamp: str = ""

class SimpleMonitoringDashboard:
    """Dashboard simplificado de monitoramento"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.start_time = datetime.now()
        self.logger = self._setup_logging()
        
        # Flask app
        self.app = Flask(__name__)
        self._setup_routes()
        
        self.logger.info("Dashboard de monitoramento simplificado inicializado")
    
    def _setup_logging(self) -> logging.Logger:
        """Configura logging"""
        logger = logging.getLogger("simple_monitoring")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def get_system_stats(self) -> SystemStats:
        """Coleta estatísticas básicas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600
            
            # Conta processos Python ativos
            python_processes = 0
            for proc in psutil.process_iter(['name']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes += 1
                except:
                    pass
            
            return SystemStats(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                uptime_hours=uptime,
                active_processes=python_processes,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas: {e}")
            return SystemStats(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def _setup_routes(self):
        """Configura rotas Flask"""
        
        @self.app.route('/')
        def dashboard():
            """Página principal do dashboard"""
            html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoring Dashboard - Sistema de Captação</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #4a90e2, #7b68ee);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .content { padding: 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            border-left: 5px solid #4a90e2;
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #4a90e2;
            margin: 10px 0;
        }
        .stat-label {
            font-size: 1.1em;
            color: #666;
            font-weight: 500;
        }
        .status-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
        }
        .status-title {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
        }
        .service-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }
        .service-name { font-weight: 600; }
        .service-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #28a745;
        }
        .refresh-btn {
            background: #4a90e2;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s;
        }
        .refresh-btn:hover { background: #357abd; }
        .timestamp {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Monitoring Dashboard</h1>
            <p>Sistema de Captação de Imóveis - Monitoramento em Tempo Real</p>
        </div>
        
        <div class="content">
            <div class="stats-grid" id="statsGrid">
                <!-- Estatísticas serão carregadas aqui -->
            </div>
            
            <div class="status-section">
                <h2 class="status-title">📊 Status dos Serviços</h2>
                <div class="service-status">
                    <span class="service-name">Backend Flask API</span>
                    <div class="service-indicator"></div>
                </div>
                <div class="service-status">
                    <span class="service-name">Frontend React</span>
                    <div class="service-indicator"></div>
                </div>
                <div class="service-status">
                    <span class="service-name">Monitoring Dashboard</span>
                    <div class="service-indicator"></div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button class="refresh-btn" onclick="refreshStats()">🔄 Atualizar Estatísticas</button>
            </div>
            
            <div class="timestamp" id="timestamp">
                <!-- Timestamp será atualizado aqui -->
            </div>
        </div>
    </div>

    <script>
        function refreshStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    updateStatsGrid(data);
                    document.getElementById('timestamp').textContent = 
                        `Última atualização: ${data.timestamp}`;
                })
                .catch(error => {
                    console.error('Erro ao buscar estatísticas:', error);
                });
        }
        
        function updateStatsGrid(stats) {
            const grid = document.getElementById('statsGrid');
            grid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${stats.cpu_usage.toFixed(1)}%</div>
                    <div class="stat-label">💻 Uso de CPU</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.memory_usage.toFixed(1)}%</div>
                    <div class="stat-label">🧠 Uso de Memória</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.disk_usage.toFixed(1)}%</div>
                    <div class="stat-label">💾 Uso de Disco</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.uptime_hours.toFixed(1)}h</div>
                    <div class="stat-label">⏱️ Tempo Ativo</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.active_processes}</div>
                    <div class="stat-label">🐍 Processos Python</div>
                </div>
            `;
        }
        
        // Atualizar automaticamente a cada 30 segundos
        setInterval(refreshStats, 30000);
        
        // Carregar estatísticas iniciais
        refreshStats();
    </script>
</body>
</html>
            """
            return html_template
        
        @self.app.route('/api/stats')
        def api_stats():
            """API para estatísticas do sistema"""
            stats = self.get_system_stats()
            return jsonify(asdict(stats))
        
        @self.app.route('/api/health')
        def health_check():
            """Health check da API"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            })
    
    def run(self, debug: bool = False):
        """Executa o dashboard"""
        self.logger.info(f"Iniciando dashboard na porta {self.port}")
        self.logger.info(f"Acesse: http://localhost:{self.port}")
        
        try:
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=debug,
                use_reloader=False
            )
        except Exception as e:
            self.logger.error(f"Erro ao iniciar dashboard: {e}")

def main():
    """Função principal"""
    dashboard = SimpleMonitoringDashboard(port=8080)
    dashboard.run()

if __name__ == "__main__":
    main()
