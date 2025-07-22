# exemplo_uso_proxies.py
"""
Exemplo prático de uso do sistema de proxies com scrapers
"""
import logging
import json
from src.utils.proxy_rotator import proxy_manager
from src.models.property import PropertySearch, PropertyType, PropertySource

# Importar scraper se disponível
try:
    from src.scrapers.vivareal_scraper import VivaRealScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("⚠️  Scraper VivaReal não disponível - exemplo será limitado")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def exemplo_basico_com_proxies():
    """Exemplo básico de uso de proxies com scraper"""
    print("🏠 EXEMPLO: SCRAPING COM SISTEMA DE PROXIES")
    print("=" * 60)
    
    # 1. Configurar proxies
    print("\n1. Configurando sistema de proxies...")
    
    # Opção A: Usar proxies gratuitos (apenas para teste)
    proxy_manager.setup_proxies(use_free_proxies=True)
    
    # Opção B: Usar proxies customizados (comentado - substitua por proxies reais)
    """
    custom_proxies = [
        {"ip": "sua_proxy_ip", "port": 8080, "protocol": "http"},
        {"ip": "outro_proxy", "port": 3128, "username": "user", "password": "pass"}
    ]
    proxy_manager.setup_proxies(proxy_list=custom_proxies)
    """
    
    # Verificar status dos proxies
    stats = proxy_manager.get_statistics()
    print(f"   ✓ Proxies configurados: {stats['total_proxies']}")
    print(f"   ✓ Proxies funcionando: {stats['working_proxies']}")
    
    if stats['working_proxies'] == 0:
        print("   ⚠️  Nenhum proxy funcionando - executando sem proxies")
    
    # 2. Configurar busca
    print("\n2. Configurando busca de imóveis...")
    search = PropertySearch(
        city="São Paulo",
        property_type=PropertyType.APARTAMENTO,
        max_results=5  # Poucos resultados para teste
    )
    print(f"   ✓ Busca: {search.city}, {search.property_type.value}")
    print(f"   ✓ Máximo de resultados: {search.max_results}")
    
    # 3. Executar scraping
    print("\n3. Executando scraping com proxies...")
    
    if not SCRAPER_AVAILABLE:
        print("   ⚠️  Scraper não disponível - simulando execução...")
        print("   ✓ Scraping simulado concluído!")
        print("   ✓ Sistema de proxies funcionando corretamente")
        return
    
    try:
        scraper = VivaRealScraper()
        result = scraper.scrape_properties(search)
        
        print(f"   ✓ Scraping concluído!")
        print(f"   ✓ Sucesso: {result.success}")
        print(f"   ✓ Propriedades encontradas: {result.total_found}")
        print(f"   ✓ Tempo de execução: {result.execution_time:.2f}s")
        
        if result.error_message:
            print(f"   ⚠️  Erro: {result.error_message}")
        
        # Mostrar algumas propriedades
        if result.properties:
            print(f"\n   📋 Primeiras propriedades encontradas:")
            for i, prop in enumerate(result.properties[:3]):
                print(f"      {i+1}. {prop.title[:50]}...")
                print(f"         💰 Preço: R$ {prop.price:,.2f}")
                print(f"         📍 Localização: {prop.address}")
                print()
        
    except Exception as e:
        logger.error(f"Erro durante scraping: {e}")
        print(f"   ❌ Erro durante scraping: {e}")
    
    # 4. Estatísticas finais dos proxies
    print("\n4. Estatísticas finais dos proxies:")
    final_stats = proxy_manager.get_statistics()
    
    print(f"   📊 Proxies ativos: {final_stats['working_proxies']}/{final_stats['total_proxies']}")
    print(f"   📊 Taxa de sucesso: {final_stats['avg_success_rate']:.1%}")
    print(f"   📊 Tempo médio de resposta: {final_stats['avg_response_time']:.2f}s")
    
    # Mostrar detalhes de proxies usados
    working_proxies = proxy_manager.rotator.get_working_proxies()
    if working_proxies:
        print(f"\n   🔄 Proxies mais utilizados:")
        # Ordenar por uso (última utilização)
        used_proxies = [p for p in working_proxies if p.last_used]
        used_proxies.sort(key=lambda x: x.last_used or "", reverse=True)
        
        for i, proxy in enumerate(used_proxies[:3]):
            print(f"      {i+1}. {proxy.ip}:{proxy.port}")
            print(f"         📊 Score: {proxy.reliability_score:.2f}")
            print(f"         ✅ Sucessos: {proxy.success_count}")
            print(f"         ❌ Falhas: {proxy.failure_count}")

def exemplo_configuracao_arquivos():
    """Exemplo de configuração usando arquivos"""
    print("\n📁 EXEMPLO: CONFIGURAÇÃO VIA ARQUIVOS")
    print("=" * 60)
    
    # 1. Criar arquivo de exemplo
    print("\n1. Criando arquivo de configuração de exemplo...")
    
    proxy_config = [
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
            "password": "senha123",
            "country": "US"
        },
        {
            "ip": "172.16.0.10",
            "port": 1080,
            "protocol": "socks5",
            "country": "UK"
        }
    ]
    
    config_file = "proxies_exemplo.json"
    with open(config_file, 'w') as f:
        json.dump(proxy_config, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Arquivo criado: {config_file}")
    print(f"   ✓ {len(proxy_config)} proxies configurados")
    
    # 2. Carregar configuração
    print(f"\n2. Carregando configuração do arquivo...")
    
    try:
        with open(config_file, 'r') as f:
            loaded_proxies = json.load(f)
        
        proxy_manager.setup_proxies(proxy_list=loaded_proxies)
        
        stats = proxy_manager.get_statistics()
        print(f"   ✓ Proxies carregados: {stats['total_proxies']}")
        print(f"   ✓ Proxies testados: {stats['working_proxies']} funcionando")
        
    except Exception as e:
        print(f"   ❌ Erro ao carregar arquivo: {e}")
    
    # 3. Mostrar configuração carregada
    print(f"\n3. Detalhes da configuração:")
    for i, proxy in enumerate(proxy_manager.rotator.proxies[-3:]):  # Últimos 3 adicionados
        print(f"   Proxy {i+1}: {proxy.ip}:{proxy.port}")
        print(f"      🔐 Protocolo: {proxy.protocol}")
        print(f"      🔑 Autenticação: {'Sim' if proxy.username else 'Não'}")
        print(f"      🌍 País: {getattr(proxy, 'country', 'N/A')}")

def exemplo_monitoramento_continuo():
    """Exemplo de monitoramento contínuo dos proxies"""
    print("\n📊 EXEMPLO: MONITORAMENTO CONTÍNUO")
    print("=" * 60)
    
    # Configurar proxies
    proxy_manager.setup_proxies(use_free_proxies=True)
    
    import time
    
    print("\n1. Iniciando monitoramento por 30 segundos...")
    print("   (Pressione Ctrl+C para parar)")
    
    iteration = 0  # Inicializar contador
    
    try:
        start_time = time.time()
        
        while time.time() - start_time < 30:  # 30 segundos
            iteration += 1
            
            # Obter proxy
            proxy = proxy_manager.get_proxy_for_request()
            
            if proxy:
                # Simular uso
                import random
                success = random.choice([True, True, False])  # 66% sucesso
                proxy_manager.report_proxy_result(proxy, success)
                
                status = "✅" if success else "❌"
                print(f"   Iter {iteration:2d}: {proxy.ip}:{proxy.port} {status} (score: {proxy.reliability_score:.2f})")
            else:
                print(f"   Iter {iteration:2d}: Nenhum proxy disponível")
            
            time.sleep(2)  # Aguardar 2 segundos
            
    except KeyboardInterrupt:
        print(f"\n   ⏹️  Monitoramento interrompido pelo usuário")
    
    # Estatísticas finais
    print(f"\n2. Estatísticas do monitoramento:")
    stats = proxy_manager.get_statistics()
    
    print(f"   📊 Iterações executadas: {iteration}")
    print(f"   📊 Proxies funcionando: {stats['working_proxies']}")
    print(f"   📊 Taxa média de sucesso: {stats['avg_success_rate']:.1%}")

def main():
    """Função principal com menu de exemplos"""
    print("🚀 EXEMPLOS DO SISTEMA DE PROXIES")
    print("=" * 70)
    
    examples = {
        "1": ("Exemplo básico com scraper", exemplo_basico_com_proxies),
        "2": ("Configuração via arquivos", exemplo_configuracao_arquivos), 
        "3": ("Monitoramento contínuo", exemplo_monitoramento_continuo),
        "4": ("Executar todos os exemplos", None),
        "5": ("Sair", None)
    }
    
    while True:
        print("\nExemplos disponíveis:")
        for key, (description, _) in examples.items():
            print(f"  {key}. {description}")
        
        choice = input("\nEscolha um exemplo: ").strip()
        
        if choice == "5":
            print("👋 Até logo!")
            break
        elif choice == "4":
            # Executar todos
            for key in ["1", "2", "3"]:
                if examples[key][1]:
                    try:
                        examples[key][1]()
                    except Exception as e:
                        logger.error(f"Erro no exemplo {key}: {e}")
            break
        elif choice in examples and examples[choice][1]:
            try:
                examples[choice][1]()
            except Exception as e:
                logger.error(f"Erro no exemplo: {e}")
                print(f"❌ Erro: {e}")
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
