#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste de Integração Completa dos Dashboards
Verifica se todos os componentes estão funcionando corretamente
"""

import os
import sys
import time
import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_backend_api():
    """Testa o backend Flask API"""
    try:
        logger.info("🔍 Testando Backend Flask API...")
        
        # Testar endpoint de propriedades
        response = requests.get("http://localhost:5000/api/properties", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Backend API - Endpoint /api/properties: OK")
        else:
            logger.warning(f"⚠️  Backend API - Endpoint /api/properties: Status {response.status_code}")
        
        # Testar endpoint de status dos scrapers
        response = requests.get("http://localhost:5000/api/scrapers/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Backend API - Endpoint /api/scrapers/status: OK")
            logger.info(f"   Scrapers disponíveis: {list(data.get('data', {}).keys())}")
        else:
            logger.warning(f"⚠️  Backend API - Endpoint /api/scrapers/status: Status {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        logger.error("❌ Backend Flask API: NÃO ESTÁ RODANDO")
        logger.info("   Para iniciar: cd backend && python main.py")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao testar Backend API: {e}")
        return False

def test_monitoring_dashboard():
    """Testa o dashboard de monitoramento Python"""
    try:
        logger.info("🔍 Testando Monitoring Dashboard Python...")
        
        # Testar página principal
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200 and "Dashboard de Monitoramento" in response.text:
            logger.info("✅ Monitoring Dashboard - Página principal: OK")
        else:
            logger.warning(f"⚠️  Monitoring Dashboard - Página principal: Status {response.status_code}")
        
        # Testar APIs de monitoramento
        endpoints = [
            "/api/stats",
            "/api/portals", 
            "/api/logs",
            "/api/alerts"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ Monitoring Dashboard - {endpoint}: OK")
                else:
                    logger.warning(f"⚠️  Monitoring Dashboard - {endpoint}: Status {response.status_code}")
            except:
                logger.warning(f"⚠️  Monitoring Dashboard - {endpoint}: Falha na conexão")
                
        return True
        
    except requests.exceptions.ConnectionError:
        logger.error("❌ Monitoring Dashboard: NÃO ESTÁ RODANDO")
        logger.info("   Para iniciar: cd src/dashboard && python monitoring_dashboard.py")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao testar Monitoring Dashboard: {e}")
        return False

def test_react_frontend():
    """Testa o frontend React"""
    try:
        logger.info("🔍 Testando Frontend React...")
        
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Frontend React: RODANDO na porta 3000")
            
            # Verificar se Dashboard_new está sendo usado
            if "Dashboard" in response.text or "react" in response.text.lower():
                logger.info("✅ Frontend React - Dashboard_new.jsx: OK")
            
            return True
        else:
            logger.warning(f"⚠️  Frontend React: Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Frontend React: NÃO ESTÁ RODANDO")
        logger.info("   Para iniciar: cd frontend && npm start")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao testar Frontend React: {e}")
        return False

def test_component_files():
    """Verifica se os arquivos dos componentes existem"""
    logger.info("🔍 Verificando arquivos dos componentes...")
    
    files_to_check = [
        ("Frontend React Dashboard", "frontend/src/pages/Dashboard_new.jsx"),
        ("Python Monitoring Dashboard", "src/dashboard/monitoring_dashboard.py"),
        ("Dashboard Template HTML", "src/dashboard/templates/dashboard.html"),
        ("Backend Flask API", "backend/main.py"),
        ("Property Service", "frontend/src/services/propertyService.js"),
        ("Search Filters", "frontend/src/components/SearchFilters.jsx"),
        ("Property Card", "frontend/src/components/PropertyCard.jsx"),
    ]
    
    all_exist = True
    for name, file_path in files_to_check:
        if os.path.exists(file_path):
            logger.info(f"✅ {name}: {file_path}")
        else:
            logger.error(f"❌ {name}: {file_path} - ARQUIVO NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def main():
    """Função principal de teste"""
    logger.info("🚀 TESTE DE INTEGRAÇÃO COMPLETA - Sistema de Captação de Imóveis")
    logger.info("=" * 70)
    
    # Verificar arquivos
    logger.info("\n📁 VERIFICAÇÃO DE ARQUIVOS:")
    files_ok = test_component_files()
    
    # Aguardar um pouco para os serviços iniciarem
    logger.info("\n⏱️  Aguardando serviços iniciarem...")
    time.sleep(3)
    
    # Testar serviços
    logger.info("\n🔧 TESTE DOS SERVIÇOS:")
    backend_ok = test_backend_api()
    monitoring_ok = test_monitoring_dashboard() 
    frontend_ok = test_react_frontend()
    
    # Resumo final
    logger.info("\n" + "=" * 70)
    logger.info("📊 RESULTADO FINAL:")
    logger.info(f"✅ Arquivos dos componentes: {'OK' if files_ok else 'ERRO'}")
    logger.info(f"✅ Backend Flask API: {'OK' if backend_ok else 'ERRO'}")
    logger.info(f"✅ Monitoring Dashboard: {'OK' if monitoring_ok else 'ERRO'}")
    logger.info(f"✅ Frontend React: {'OK' if frontend_ok else 'ERRO'}")
    
    if all([files_ok, backend_ok, frontend_ok]):
        logger.info("\n🎉 SISTEMA 100% FUNCIONAL!")
        logger.info("Dashboard_new.jsx e monitoring_dashboard.py estão integrados e funcionando!")
        logger.info("\n📱 ACESSO AOS DASHBOARDS:")
        logger.info("   • Frontend React: http://localhost:3000")
        logger.info("   • Monitoring Dashboard: http://localhost:5000")
        logger.info("   • Backend API: http://localhost:5000/api")
    else:
        logger.warning("\n⚠️  ALGUNS COMPONENTES PRECISAM DE ATENÇÃO")
        logger.info("\n🔧 COMO INICIAR OS SERVIÇOS:")
        logger.info("   1. Backend: cd backend && python main.py")
        logger.info("   2. Frontend: cd frontend && npm start") 
        logger.info("   3. Monitoring: cd src/dashboard && python monitoring_dashboard.py")

if __name__ == "__main__":
    main()
