# demo_proxy_system.py
"""
Demonstração do sistema de proxies rotativos
"""
import asyncio
import logging
import time
from src.utils.proxy_rotator import proxy_manager, ProxyInfo
from src.utils.selenium_proxy_config import selenium_proxy_config
from src.models.property import PropertySource

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def demo_proxy_basic():
    """Demonstração básica do sistema de proxies"""
    print("🔄 DEMONSTRAÇÃO DO SISTEMA DE PROXIES ROTATIVOS")
    print("=" * 60)
    
    # 1. Configurar proxies (usando lista de proxies gratuitos para demo)
    print("\n1. Configurando proxies...")
    proxy_manager.setup_proxies(use_free_proxies=True)
    
    # 2. Mostrar estatísticas iniciais
    stats = proxy_manager.get_statistics()
    print(f"   ✓ Proxies carregados: {stats['total_proxies']}")
    print(f"   ✓ Proxies funcionando: {stats['working_proxies']}")
    print(f"   ✓ Taxa de sucesso: {stats['success_rate']:.1%}")
    
    if stats['working_proxies'] == 0:
        print("   ⚠️  Nenhum proxy funcionando - demonstração limitada")
        return
    
    # 3. Testar diferentes estratégias de rotação
    print("\n2. Testando estratégias de rotação...")
    
    strategies = ['best', 'random', 'round_robin']
    for strategy in strategies:
        print(f"\n   📊 Estratégia: {strategy}")
        proxy_manager.rotation_strategy = strategy
        
        for i in range(3):
            proxy = proxy_manager.get_proxy_for_request()
            if proxy:
                print(f"      Proxy {i+1}: {proxy.ip}:{proxy.port} (score: {proxy.reliability_score:.2f})")
            else:
                print(f"      Proxy {i+1}: Nenhum disponível")
    
    # 4. Testar configuração Selenium
    print("\n3. Testando configuração Selenium...")
    proxy = proxy_manager.get_proxy_for_request()
    
    if proxy:
        print(f"   📋 Configurando Selenium com proxy: {proxy.ip}:{proxy.port}")
        
        try:
            chrome_options = selenium_proxy_config.configure_chrome_with_proxy(proxy)
            print(f"   ✓ Chrome configurado com {len(chrome_options.arguments)} argumentos")
            
            # Mostrar alguns argumentos
            proxy_args = [arg for arg in chrome_options.arguments if 'proxy' in arg.lower()]
            if proxy_args:
                print(f"   ✓ Argumentos de proxy: {proxy_args}")
            
        except Exception as e:
            print(f"   ❌ Erro na configuração: {e}")
    
    # 5. Simular uso e reportar resultados
    print("\n4. Simulando uso dos proxies...")
    
    for i in range(5):
        proxy = proxy_manager.get_proxy_for_request()
        if proxy:
            # Simular sucesso/falha aleatório
            import random
            success = random.choice([True, True, True, False])  # 75% sucesso
            
            proxy_manager.report_proxy_result(proxy, success)
            status = "✓ Sucesso" if success else "❌ Falha"
            print(f"   Uso {i+1}: {proxy.ip}:{proxy.port} - {status}")
        
        time.sleep(0.5)
    
    # 6. Estatísticas finais
    print("\n5. Estatísticas finais:")
    final_stats = proxy_manager.get_statistics()
    print(f"   📊 Proxies funcionando: {final_stats['working_proxies']}/{final_stats['total_proxies']}")
    print(f"   📊 Taxa de sucesso geral: {final_stats['avg_success_rate']:.1%}")
    print(f"   📊 Tempo médio de resposta: {final_stats['avg_response_time']:.2f}s")

def demo_proxy_advanced():
    """Demonstração avançada com proxies customizados"""
    print("\n🚀 DEMONSTRAÇÃO AVANÇADA COM PROXIES CUSTOMIZADOS")
    print("=" * 60)
    
    # Lista de proxies customizada (exemplo)
    custom_proxies = [
        {"ip": "192.168.1.1", "port": 8080, "protocol": "http"},
        {"ip": "10.0.0.1", "port": 3128, "protocol": "http", "username": "user", "password": "pass"},
        {"ip": "172.16.0.1", "port": 1080, "protocol": "socks5"},
    ]
    
    print("\n1. Configurando proxies customizados...")
    print("   ⚠️  Nota: Estes são proxies de exemplo - substitua por proxies reais")
    
    proxy_manager.setup_proxies(proxy_list=custom_proxies)
    
    # Mostrar detalhes dos proxies
    print("\n2. Detalhes dos proxies configurados:")
    for i, proxy in enumerate(proxy_manager.rotator.proxies):
        print(f"   Proxy {i+1}:")
        print(f"      📍 Endereço: {proxy.ip}:{proxy.port}")
        print(f"      🔐 Protocolo: {proxy.protocol}")
        print(f"      🔑 Autenticação: {'Sim' if proxy.username else 'Não'}")
        print(f"      📊 Score: {proxy.reliability_score:.2f}")
        print(f"      🌐 URL: {proxy.proxy_url}")
        print()

def demo_proxy_selenium_integration():
    """Demonstração da integração com Selenium"""
    print("\n🌐 DEMONSTRAÇÃO DA INTEGRAÇÃO COM SELENIUM")
    print("=" * 60)
    
    # Configurar proxies
    proxy_manager.setup_proxies(use_free_proxies=True)
    
    proxy = proxy_manager.get_proxy_for_request()
    if not proxy:
        print("❌ Nenhum proxy disponível para teste com Selenium")
        return
    
    print(f"📋 Testando proxy com Selenium: {proxy.ip}:{proxy.port}")
    
    try:
        # Testar proxy com Selenium (modo headless para demo)
        print("   🔍 Iniciando teste de conectividade...")
        
        result = selenium_proxy_config.test_proxy_with_selenium(proxy, browser='chrome')
        
        if result:
            print("   ✅ Proxy funcionando com Selenium!")
            proxy_manager.report_proxy_result(proxy, True)
        else:
            print("   ❌ Proxy não funcionou com Selenium")
            proxy_manager.report_proxy_result(proxy, False)
            
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")

def demo_proxy_monitoring():
    """Demonstração do monitoramento de proxies"""
    print("\n📊 DEMONSTRAÇÃO DO MONITORAMENTO DE PROXIES")
    print("=" * 60)
    
    # Configurar proxies
    proxy_manager.setup_proxies(use_free_proxies=True)
    
    print("\n1. Status inicial dos proxies:")
    stats = proxy_manager.get_statistics()
    
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n2. Proxies individuais:")
    working_proxies = proxy_manager.rotator.get_working_proxies()
    
    for i, proxy in enumerate(working_proxies[:5]):  # Mostrar apenas os primeiros 5
        print(f"   Proxy {i+1}: {proxy.ip}:{proxy.port}")
        print(f"      ⚡ Tempo resposta: {proxy.response_time:.2f}s")
        print(f"      ✅ Sucessos: {proxy.success_count}")
        print(f"      ❌ Falhas: {proxy.failure_count}")
        print(f"      📊 Taxa sucesso: {proxy.success_rate:.1%}")
        print(f"      🏆 Score confiabilidade: {proxy.reliability_score:.2f}")
        print()

def main():
    """Função principal de demonstração"""
    try:
        # Demonstrações
        demo_proxy_basic()
        demo_proxy_advanced()
        demo_proxy_monitoring()
        
        # Opcional: teste com Selenium (comentado por padrão)
        # demo_proxy_selenium_integration()
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print("💡 Próximos passos:")
        print("   1. Configure proxies reais em produção")
        print("   2. Integre com scrapers existentes")
        print("   3. Configure monitoramento contínuo")
        print("   4. Implemente rotação automática")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demonstração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro na demonstração: {e}")
        print(f"\n❌ Erro na demonstração: {e}")

if __name__ == "__main__":
    main()
