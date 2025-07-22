#!/usr/bin/env python3
"""
Verificador de Docker para Sistema de Captação de Imóveis
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, capture_output=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_docker_installation():
    """Verifica se Docker está instalado"""
    print("🔍 Verificando instalação do Docker...")
    
    # Verifica Docker
    success, stdout, stderr = run_command("docker --version")
    if success:
        print(f"✅ Docker encontrado: {stdout.strip()}")
        docker_version = stdout.strip()
    else:
        print("❌ Docker não está instalado ou não está no PATH")
        return False, None, None
    
    # Verifica Docker Compose
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        print(f"✅ Docker Compose encontrado: {stdout.strip()}")
        compose_version = stdout.strip()
    else:
        print("❌ Docker Compose não está instalado")
        return False, docker_version, None
    
    return True, docker_version, compose_version

def check_docker_daemon():
    """Verifica se o daemon Docker está rodando"""
    print("\n🐳 Verificando daemon Docker...")
    
    success, stdout, stderr = run_command("docker ps")
    if success:
        print("✅ Docker daemon está rodando")
        containers = stdout.strip().split('\n')
        if len(containers) > 1:
            print(f"📦 {len(containers)-1} container(s) em execução")
        else:
            print("📦 Nenhum container em execução")
        return True
    else:
        print("❌ Docker daemon não está rodando")
        print(f"Erro: {stderr}")
        return False

def check_docker_compose_files():
    """Verifica arquivos Docker Compose do projeto"""
    print("\n📄 Verificando arquivos Docker do projeto...")
    
    project_root = Path.cwd()
    docker_files = [
        "docker-compose.yml",
        "docker-compose-production.yml",
        "docker-compose-selenium.yml",
        "Dockerfile"
    ]
    
    found_files = []
    for file in docker_files:
        file_path = project_root / file
        if file_path.exists():
            print(f"✅ {file} encontrado")
            found_files.append(file)
        else:
            print(f"❌ {file} não encontrado")
    
    return found_files

def test_docker_compose():
    """Testa se docker-compose funciona"""
    print("\n🧪 Testando Docker Compose...")
    
    if not Path("docker-compose.yml").exists():
        print("❌ docker-compose.yml não encontrado")
        return False
    
    success, stdout, stderr = run_command("docker-compose config")
    if success:
        print("✅ docker-compose.yml está válido")
        return True
    else:
        print("❌ Erro na configuração do docker-compose.yml")
        print(f"Erro: {stderr}")
        return False

def get_docker_recommendations():
    """Fornece recomendações baseadas no status"""
    print("\n💡 RECOMENDAÇÕES:")
    print("=" * 50)
    
    # Verifica instalação
    installed, docker_ver, compose_ver = check_docker_installation()
    
    if not installed:
        print("1. Instale o Docker Desktop:")
        print("   - Windows: https://docs.docker.com/desktop/install/windows-install/")
        print("   - Baixe e execute o instalador")
        print("   - Reinicie o computador após a instalação")
        return
    
    # Verifica daemon
    daemon_running = check_docker_daemon()
    
    if not daemon_running:
        print("1. Inicie o Docker Desktop:")
        print("   - Procure 'Docker Desktop' no menu Iniciar")
        print("   - Execute como administrador se necessário")
        print("   - Aguarde o ícone ficar verde na bandeja do sistema")
        return
    
    # Verifica arquivos do projeto
    docker_files = check_docker_compose_files()
    
    if "docker-compose.yml" in docker_files:
        compose_valid = test_docker_compose()
        
        if compose_valid:
            print("🎉 DOCKER ESTÁ PRONTO PARA USO!")
            print("\n🚀 Para iniciar o sistema com Docker:")
            print("   docker-compose up -d")
            print("\n📊 Para ver logs:")
            print("   docker-compose logs -f")
            print("\n🛑 Para parar:")
            print("   docker-compose down")
        else:
            print("❌ Arquivo docker-compose.yml tem problemas")
            print("   Verifique a sintaxe e dependências")

def create_docker_start_script():
    """Cria script para iniciar sistema com Docker"""
    script_content = '''@echo off
echo ========================================
echo   INICIANDO SISTEMA COM DOCKER
echo ========================================

echo Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está instalado ou não está rodando
    echo Instale o Docker Desktop e tente novamente
    pause
    exit /b 1
)

echo ✅ Docker encontrado
echo.

echo Construindo e iniciando containers...
docker-compose up -d --build

echo.
echo Aguardando serviços iniciarem...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   SISTEMA DOCKER INICIADO!
echo ========================================
echo.
echo  Backend API:     http://localhost:5000
echo  PostgreSQL:      localhost:5432
echo  Redis:          localhost:6379
echo.
echo Para ver logs: docker-compose logs -f
echo Para parar:    docker-compose down
echo.
pause
'''
    
    with open("start_docker_system.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("\n📝 Script criado: start_docker_system.bat")

def main():
    """Função principal"""
    print("🐳 VERIFICADOR DE DOCKER")
    print("Sistema de Captação de Imóveis")
    print("=" * 50)
    
    get_docker_recommendations()
    create_docker_start_script()
    
    print(f"\n📍 Diretório atual: {Path.cwd()}")
    print("\n🔧 Use 'python check_docker.py' para executar esta verificação novamente")

if __name__ == "__main__":
    main()
