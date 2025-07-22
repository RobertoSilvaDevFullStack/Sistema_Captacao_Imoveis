# config_proxies.py
"""
Script para configurar proxies no sistema
"""
import json
import logging
from src.utils.proxy_rotator import proxy_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_proxies_from_file(file_path: str):
    """Configura proxies a partir de arquivo JSON"""
    try:
        with open(file_path, 'r') as f:
            proxy_list = json.load(f)
        
        proxy_manager.setup_proxies(proxy_list=proxy_list)
        logger.info(f"Proxies configurados a partir de {file_path}")
        
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
    except json.JSONDecodeError:
        logger.error(f"Erro ao ler JSON do arquivo: {file_path}")

def configure_proxies_interactive():
    """Configuração interativa de proxies"""
    print("🔧 CONFIGURAÇÃO INTERATIVA DE PROXIES")
    print("=" * 50)
    
    proxies = []
    
    while True:
        print(f"\nProxy #{len(proxies) + 1}")
        ip = input("IP do proxy (ou 'fim' para terminar): ").strip()
        
        if ip.lower() == 'fim':
            break
            
        try:
            port = int(input("Porta: ").strip())
        except ValueError:
            print("❌ Porta inválida, pulando...")
            continue
        
        protocol = input("Protocolo (http/socks5) [http]: ").strip() or "http"
        
        username = input("Username (opcional): ").strip() or None
        password = input("Password (opcional): ").strip() or None
        
        proxy_data = {
            "ip": ip,
            "port": port,
            "protocol": protocol
        }
        
        if username:
            proxy_data["username"] = username
        if password:
            proxy_data["password"] = password
            
        proxies.append(proxy_data)
        print(f"✅ Proxy {ip}:{port} adicionado")
    
    if proxies:
        proxy_manager.setup_proxies(proxy_list=proxies)
        print(f"\n✅ {len(proxies)} proxies configurados com sucesso!")
        
        # Salvar configuração
        save = input("\nSalvar configuração em arquivo? (s/n): ").strip().lower()
        if save == 's':
            filename = input("Nome do arquivo [proxies.json]: ").strip() or "proxies.json"
            with open(filename, 'w') as f:
                json.dump(proxies, f, indent=2)
            print(f"✅ Configuração salva em {filename}")
    else:
        print("❌ Nenhum proxy configurado")

def create_sample_proxy_config():
    """Cria arquivo de exemplo de configuração de proxies"""
    sample_config = [
        {
            "ip": "192.168.1.100",
            "port": 8080,
            "protocol": "http",
            "country": "BR"
        },
        {
            "ip": "10.0.0.50",
            "port": 3128,
            "protocol": "http",
            "username": "usuario",
            "password": "senha",
            "country": "US"
        },
        {
            "ip": "172.16.0.10",
            "port": 1080,
            "protocol": "socks5",
            "country": "UK"
        }
    ]
    
    filename = "proxies_exemplo.json"
    with open(filename, 'w') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Arquivo de exemplo criado: {filename}")
    print("📝 Edite este arquivo com seus proxies reais")

def validate_proxy_config():
    """Valida configuração atual de proxies"""
    stats = proxy_manager.get_statistics()
    
    print("📊 VALIDAÇÃO DA CONFIGURAÇÃO DE PROXIES")
    print("=" * 50)
    
    if stats['total_proxies'] == 0:
        print("❌ Nenhum proxy configurado")
        return False
    
    print(f"✅ Total de proxies: {stats['total_proxies']}")
    print(f"✅ Proxies funcionando: {stats['working_proxies']}")
    print(f"📊 Taxa de sucesso: {stats['success_rate']:.1%}")
    
    if stats['working_proxies'] > 0:
        print(f"⚡ Tempo médio de resposta: {stats['avg_response_time']:.2f}s")
        print("✅ Sistema de proxies operacional")
        return True
    else:
        print("❌ Nenhum proxy funcionando - verifique configurações")
        return False

def main():
    """Função principal"""
    print("🔧 CONFIGURADOR DE PROXIES - Sistema de Captação de Imóveis")
    print("=" * 70)
    
    options = {
        "1": ("Configuração interativa", configure_proxies_interactive),
        "2": ("Carregar de arquivo JSON", lambda: configure_proxies_from_file(
            input("Caminho do arquivo JSON: ").strip()
        )),
        "3": ("Usar proxies gratuitos (teste)", lambda: proxy_manager.setup_proxies(use_free_proxies=True)),
        "4": ("Criar arquivo de exemplo", create_sample_proxy_config),
        "5": ("Validar configuração atual", validate_proxy_config),
        "6": ("Sair", None)
    }
    
    while True:
        print("\nOpções disponíveis:")
        for key, (description, _) in options.items():
            print(f"  {key}. {description}")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "6":
            print("👋 Até logo!")
            break
        elif choice in options:
            func = options[choice][1]
            if func:
                try:
                    func()
                except Exception as e:
                    logger.error(f"Erro: {e}")
                    print(f"❌ Erro: {e}")
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
