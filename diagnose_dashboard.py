#!/usr/bin/env python3
"""
Teste e diagnóstico do ambiente antes de iniciar dashboard
"""

import sys
import os
import subprocess
import importlib.util

def test_dependencies():
    """Testa dependências necessárias"""
    
    print("🔍 Testando dependências...")
    
    dependencies = {
        'flask': 'Flask',
        'redis': 'Redis',
        'docker': 'Docker',
        'requests': 'Requests'
    }
    
    missing = []
    
    for package, name in dependencies.items():
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing.append(package)
                print(f"❌ {name} não encontrado")
            else:
                print(f"✅ {name} OK")
        except ImportError:
            missing.append(package)
            print(f"❌ {name} não encontrado")
    
    return missing

def test_containers():
    """Testa containers Docker"""
    
    print("\n🐳 Testando containers...")
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        if 'selenium-hub' in result.stdout:
            print("✅ Selenium Hub rodando")
        else:
            print("❌ Selenium Hub não encontrado")
            
        if 'redis' in result.stdout:
            print("✅ Redis rodando")
        else:
            print("❌ Redis não encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar containers: {e}")
        return False

def test_connections():
    """Testa conexões"""
    
    print("\n🔌 Testando conexões...")
    
    # Teste Redis
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis conectado")
    except Exception as e:
        print(f"❌ Redis falhou: {e}")
    
    # Teste Selenium Grid
    try:
        import requests
        response = requests.get('http://localhost:4444/status', timeout=5)
        if response.status_code == 200:
            print("✅ Selenium Grid conectado")
        else:
            print(f"❌ Selenium Grid retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Selenium Grid falhou: {e}")

def fix_issues():
    """Tentar corrigir problemas comuns"""
    
    print("\n🔧 Verificando correções...")
    
    # Verificar se diretório templates existe
    templates_dir = os.path.join('src', 'dashboard', 'templates')
    if not os.path.exists(templates_dir):
        print(f"⚠️  Criando diretório: {templates_dir}")
        os.makedirs(templates_dir, exist_ok=True)
    else:
        print("✅ Diretório templates OK")
    
    # Verificar arquivo template
    template_file = os.path.join(templates_dir, 'simple_dashboard.html')
    if os.path.exists(template_file):
        print("✅ Template HTML encontrado")
    else:
        print("❌ Template HTML não encontrado")

def main():
    print("🚀 Diagnóstico do Dashboard\n")
    
    # Verificar diretório atual
    if not os.path.exists('src'):
        print("❌ Execute este script na raiz do projeto!")
        return False
    
    # Testar dependências
    missing = test_dependencies()
    if missing:
        print(f"\n⚠️  Instalar dependências: pip install {' '.join(missing)}")
    
    # Testar containers
    containers_ok = test_containers()
    
    # Testar conexões
    test_connections()
    
    # Corrigir problemas
    fix_issues()
    
    print("\n📋 Resumo:")
    if not missing and containers_ok:
        print("✅ Sistema pronto para dashboard!")
        print("\n🚀 Para iniciar:")
        print("cd src/dashboard")
        print("python simple_dashboard_server.py")
        print("\n🌐 Acesse: http://localhost:5000")
        return True
    else:
        print("❌ Problemas encontrados - revisar acima")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Tudo OK! Iniciando dashboard...")
        try:
            os.chdir(os.path.join('src', 'dashboard'))
            os.system('python simple_dashboard_server.py')
        except KeyboardInterrupt:
            print("\n👋 Dashboard parado pelo usuário")
    else:
        print("\n❌ Corrija os problemas antes de continuar")
