#!/usr/bin/env python3
"""
Launcher Principal do Sistema
Inicia todos os serviços na ordem correta
"""

import subprocess
import time
import sys
import threading
import webbrowser
from datetime import datetime

def run_command_in_thread(command, name, cwd=None):
    """Executar comando em thread separada"""
    
    def target():
        try:
            print(f"🚀 Iniciando {name}...")
            process = subprocess.Popen(
                command,
                cwd=cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Ler output em tempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"[{name}] {output.strip()}")
            
        except Exception as e:
            print(f"❌ Erro ao iniciar {name}: {e}")
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread

def check_port_available(port):
    """Verificar se porta está disponível"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def wait_for_server(port, name, max_attempts=30):
    """Aguardar servidor ficar disponível"""
    import requests
    
    for i in range(max_attempts):
        try:
            response = requests.get(f'http://localhost:{port}/api/health', timeout=2)
            if response.status_code == 200:
                print(f"✅ {name} está online na porta {port}")
                return True
        except:
            pass
        
        print(f"⏳ Aguardando {name} ({i+1}/{max_attempts})...")
        time.sleep(2)
    
    print(f"❌ {name} não respondeu na porta {port}")
    return False

def main():
    """Função principal"""
    
    print("=" * 60)
    print("🏠 SISTEMA DE CAPTAÇÃO DE IMÓVEIS")
    print("🚀 Iniciando todos os serviços...")
    print("=" * 60)
    
    # Verificar se as portas estão disponíveis
    ports_to_check = [3000, 5000, 8000]
    for port in ports_to_check:
        if not check_port_available(port):
            print(f"❌ Porta {port} já está em uso!")
            print("   Feche outros serviços ou mude as portas")
            return
    
    print("✅ Todas as portas estão disponíveis")
    
    # 1. Iniciar Backend API (porta 8000)
    print("\n🔧 1/3 - Iniciando Backend API Server...")
    backend_thread = run_command_in_thread(
        "python backend_api_server.py",
        "Backend-API",
        cwd="."
    )
    
    # Aguardar backend ficar online
    if not wait_for_server(8000, "Backend API"):
        print("❌ Backend API falhou ao iniciar")
        return
    
    # 2. Iniciar Dashboard de Monitoramento (porta 5000)
    print("\n📊 2/3 - Iniciando Dashboard de Monitoramento...")
    monitoring_thread = run_command_in_thread(
        "python test_server.py",
        "Dashboard-Monitoramento", 
        cwd="."
    )
    
    # Aguardar dashboard de monitoramento
    time.sleep(5)  # Dar tempo para iniciar
    
    # 3. Iniciar React Frontend (porta 3000)
    print("\n⚛️  3/3 - Iniciando React Frontend...")
    frontend_thread = run_command_in_thread(
        "npm start",
        "React-Frontend",
        cwd="frontend"
    )
    
    # Aguardar um pouco para o React iniciar
    print("⏳ Aguardando React inicializar...")
    time.sleep(10)
    
    # Mostrar URLs
    print("\n" + "=" * 60)
    print("🎉 SISTEMA INICIADO COM SUCESSO!")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("\n🌐 URLs Disponíveis:")
    print("   🎯 PRINCIPAL - Dashboard React:")
    print("      http://localhost:3000")
    print("\n   📊 MONITORAMENTO - Dashboard Python:")
    print("      http://localhost:5000")
    print("\n   📡 API Backend:")
    print("      http://localhost:8000/api/health")
    
    # Abrir navegador automaticamente na página principal
    print("\n🌍 Abrindo navegador na página principal...")
    time.sleep(2)
    webbrowser.open('http://localhost:3000')
    
    print("\n💡 COMO USAR:")
    print("   1. Use o Dashboard React (porta 3000) como PRINCIPAL")
    print("   2. Acesse o Dashboard de Monitoramento via botão no React")
    print("   3. Para parar: Ctrl+C neste terminal")
    
    # Manter vivo
    try:
        print("\n⚡ Sistema em execução... (Ctrl+C para parar)")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Parando sistema...")
        print("✅ Sistema parado com sucesso!")

if __name__ == "__main__":
    main()
