# demo_selenium_stealth.py
"""
Demonstração do Sistema Selenium Stealth com Comportamento Humano
"""
import time
import logging
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

try:
    from src.utils.selenium_stealth import (
        StealthWebDriver, 
        StealthConfig, 
        HumanBehaviorConfig,
        create_stealth_driver,
        stealth_manager
    )
    from src.utils.selenium_containers import (
        SeleniumContainerPool,
        execute_parallel_selenium_tasks,
        ContainerConfig
    )
    SELENIUM_STEALTH_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erro ao importar módulos stealth: {e}")
    SELENIUM_STEALTH_AVAILABLE = False

def demo_stealth_basico():
    """Demonstração básica do Selenium Stealth"""
    print("\n🎭 DEMONSTRAÇÃO: Selenium Stealth Básico")
    print("=" * 50)
    
    if not SELENIUM_STEALTH_AVAILABLE:
        print("❌ Módulos stealth não disponíveis")
        return
    
    try:
        # Criar driver stealth
        print("🚀 Criando driver stealth...")
        
        stealth_config = StealthConfig(
            use_undetected_chrome=True,
            headless=False,  # Visível para demonstração
            window_size=(1366, 768)
        )
        
        behavior_config = HumanBehaviorConfig(
            reading_speed_wpm=220,
            typing_speed_cpm=180
        )
        
        with StealthWebDriver(stealth_config, behavior_config) as stealth_driver:
            # Navegar com comportamento humano
            print("🌐 Navegando para página de teste...")
            stealth_driver.get("https://httpbin.org/user-agent", simulate_reading=True)
            
            # Aguardar e "pensar"
            stealth_driver.wait_and_think(2, 5)
            
            # Fazer scroll humano
            print("📜 Simulando scroll humano...")
            stealth_driver.scroll_page('down', 300)
            stealth_driver.wait_and_think(1, 3)
            stealth_driver.scroll_page('up', 150)
            
            # Simular leitura da página
            print("📖 Simulando leitura...")
            stealth_driver.behavior_simulator.simulate_page_reading(
                stealth_driver.driver, 
                reading_duration=8.0
            )
            
            print("✅ Demonstração básica concluída!")
            
    except Exception as e:
        print(f"❌ Erro na demonstração básica: {e}")
        import traceback
        traceback.print_exc()

def demo_comportamento_humano():
    """Demonstração de comportamento humano avançado"""
    print("\n🧠 DEMONSTRAÇÃO: Comportamento Humano Avançado")
    print("=" * 55)
    
    if not SELENIUM_STEALTH_AVAILABLE:
        print("❌ Módulos stealth não disponíveis")
        return
    
    try:
        print("🎯 Criando driver para ZapImóveis...")
        
        with create_stealth_driver('zapimoveis') as stealth_driver:
            # Navegar para site de teste com formulário
            print("🌐 Navegando para página de teste...")
            stealth_driver.get("https://httpbin.org/forms/post", simulate_reading=True)
            
            # Simular preenchimento de formulário
            print("📝 Simulando preenchimento humano de formulário...")
            
            try:
                # Encontrar campos de entrada
                email_field = stealth_driver.driver.find_element(By.NAME, "email")
                if email_field:
                    print("   ✍️ Digitando email...")
                    stealth_driver.behavior_simulator.human_typing(
                        email_field, 
                        "teste@exemplo.com"
                    )
                
                # Pausa para "pensar"
                stealth_driver.wait_and_think(2, 4)
                
                # Campo de comentário
                comment_field = stealth_driver.driver.find_element(By.NAME, "comments")
                if comment_field:
                    print("   ✍️ Digitando comentário...")
                    stealth_driver.behavior_simulator.human_typing(
                        comment_field,
                        "Este é um teste de comportamento humano realístico."
                    )
                
                # Scroll antes de submeter
                stealth_driver.scroll_page('down', 200)
                stealth_driver.wait_and_think(1, 2)
                
                print("✅ Simulação de formulário concluída!")
                
            except Exception as form_error:
                print(f"ℹ️ Página de teste pode não ter formulário: {form_error}")
            
    except Exception as e:
        print(f"❌ Erro na demonstração de comportamento: {e}")
        import traceback
        traceback.print_exc()

def demo_deteccao_evasao():
    """Demonstração de evasão de detecção"""
    print("\n🕵️ DEMONSTRAÇÃO: Evasão de Detecção")
    print("=" * 45)
    
    if not SELENIUM_STEALTH_AVAILABLE:
        print("❌ Módulos stealth não disponíveis")
        return
    
    try:
        print("🔍 Testando diferentes configurações stealth...")
        
        # Configuração 1: Chrome normal com stealth
        print("\n1️⃣ Chrome com Selenium-Stealth:")
        stealth_config_1 = StealthConfig(
            use_undetected_chrome=False,
            use_stealth=True,
            headless=True
        )
        
        with StealthWebDriver(stealth_config_1) as driver1:
            driver1.get("https://httpbin.org/headers", simulate_reading=False)
            headers = driver1.driver.execute_script("return navigator.userAgent;")
            print(f"   User-Agent: {headers[:80]}...")
            
            # Verificar propriedades que indicam webdriver
            webdriver_detected = driver1.driver.execute_script("""
                return {
                    webdriver: navigator.webdriver,
                    plugins: navigator.plugins.length,
                    languages: navigator.languages,
                    platform: navigator.platform
                };
            """)
            print(f"   WebDriver detectado: {webdriver_detected.get('webdriver', 'N/A')}")
            print(f"   Plugins: {webdriver_detected.get('plugins', 0)}")
        
        # Configuração 2: Undetected Chrome
        if True:  # Sempre tentar, mesmo sem biblioteca
            print("\n2️⃣ Undetected Chrome:")
            stealth_config_2 = StealthConfig(
                use_undetected_chrome=True,
                headless=True
            )
            
            try:
                with StealthWebDriver(stealth_config_2) as driver2:
                    driver2.get("https://httpbin.org/headers", simulate_reading=False)
                    headers = driver2.driver.execute_script("return navigator.userAgent;")
                    print(f"   User-Agent: {headers[:80]}...")
                    
                    webdriver_detected = driver2.driver.execute_script("""
                        return {
                            webdriver: navigator.webdriver,
                            plugins: navigator.plugins.length,
                            chrome: !!window.chrome
                        };
                    """)
                    print(f"   WebDriver detectado: {webdriver_detected.get('webdriver', 'N/A')}")
                    print(f"   Chrome object: {webdriver_detected.get('chrome', False)}")
            except Exception as uc_error:
                print(f"   ⚠️ Undetected Chrome não disponível: {uc_error}")
        
        print("✅ Testes de detecção concluídos!")
        
    except Exception as e:
        print(f"❌ Erro nos testes de detecção: {e}")
        import traceback
        traceback.print_exc()

def demo_containers_selenium():
    """Demonstração do sistema de containers"""
    print("\n🐳 DEMONSTRAÇÃO: Selenium com Containers")
    print("=" * 50)
    
    try:
        import docker
        
        # Verificar se Docker está disponível
        try:
            client = docker.from_env()
            client.ping()
            print("✅ Docker está disponível")
        except Exception as docker_error:
            print(f"❌ Docker não disponível: {docker_error}")
            print("💡 Para usar containers:")
            print("   1. Instale Docker Desktop")
            print("   2. Execute: docker-compose -f docker-compose-selenium.yml up -d")
            print("   3. Aguarde containers iniciarem")
            return
        
        # Exemplo de uso do pool de containers
        print("🏊 Criando pool de containers...")
        
        # Esta parte requer containers em execução
        print("📋 Comandos para iniciar Selenium Grid:")
        print("   docker-compose -f docker-compose-selenium.yml up -d")
        print("   # Aguardar containers iniciarem")
        print("   # Acessar http://localhost:4444 para ver o grid")
        
        # Exemplo de tarefa paralela (sem executar)
        def exemplo_tarefa_selenium(selenium_url: str, cidade: str):
            """Exemplo de tarefa que seria executada em container"""
            print(f"Executando busca para {cidade} via {selenium_url}")
            # Aqui seria a lógica real de scraping
            return f"Resultados para {cidade}"
        
        # Demonstrar como seria o uso
        tarefas_exemplo = [
            {'func': exemplo_tarefa_selenium, 'args': ('http://localhost:4444/wd/hub', 'São Paulo')},
            {'func': exemplo_tarefa_selenium, 'args': ('http://localhost:4444/wd/hub', 'Rio de Janeiro')},
            {'func': exemplo_tarefa_selenium, 'args': ('http://localhost:4444/wd/hub', 'Belo Horizonte')}
        ]
        
        print(f"📝 Exemplo de {len(tarefas_exemplo)} tarefas paralelas preparadas")
        print("✅ Demonstração de containers preparada!")
        
    except ImportError:
        print("❌ Docker library não disponível")
        print("💡 Execute: pip install docker")
    except Exception as e:
        print(f"❌ Erro na demonstração de containers: {e}")

def demo_configuracoes_portais():
    """Demonstração de configurações específicas por portal"""
    print("\n🎯 DEMONSTRAÇÃO: Configurações por Portal")
    print("=" * 50)
    
    if not SELENIUM_STEALTH_AVAILABLE:
        print("❌ Módulos stealth não disponíveis")
        return
    
    portais = ['zapimoveis', 'olx', 'vivareal']
    
    for portal in portais:
        print(f"\n🏢 Portal: {portal.upper()}")
        
        try:
            # Criar driver específico para o portal
            driver_wrapper = create_stealth_driver(portal, headless=True)
            
            # Mostrar configurações aplicadas
            config = driver_wrapper.stealth_config
            print(f"   📐 Tamanho da janela: {config.window_size}")
            print(f"   🕶️ Headless: {config.headless}")
            print(f"   🤖 Undetected Chrome: {config.use_undetected_chrome}")
            
            if config.user_agent_override:
                print(f"   🌐 User-Agent customizado: {config.user_agent_override[:60]}...")
            else:
                print("   🌐 User-Agent padrão")
            
            # Testar criação do driver
            with driver_wrapper as stealth:
                print("   ✅ Driver criado com sucesso")
                
                # Navegar para página de teste
                stealth.get("https://httpbin.org/user-agent", simulate_reading=False)
                
                # Verificar user agent retornado
                try:
                    user_agent = stealth.driver.execute_script("return navigator.userAgent;")
                    print(f"   📊 User-Agent ativo: {user_agent[:60]}...")
                except:
                    print("   📊 Não foi possível verificar User-Agent")
                
        except Exception as e:
            print(f"   ❌ Erro no portal {portal}: {e}")

def main():
    """Função principal de demonstração"""
    print("🚀 SISTEMA SELENIUM STEALTH - DEMONSTRAÇÃO COMPLETA")
    print("=" * 65)
    print("\n🎭 Recursos Implementados:")
    print("✅ Selenium Stealth com undetected-chromedriver")
    print("✅ Simulação de comportamento humano realístico")
    print("✅ Delays inteligentes e movimento natural do mouse")
    print("✅ Sistema de containers Docker para paralelização")
    print("✅ Configurações específicas por portal")
    print("✅ Evasão avançada de detecção de bots")
    
    demos = [
        ("Stealth Básico", demo_stealth_basico),
        ("Comportamento Humano", demo_comportamento_humano),
        ("Evasão de Detecção", demo_deteccao_evasao),
        ("Configurações por Portal", demo_configuracoes_portais),
        ("Containers Docker", demo_containers_selenium)
    ]
    
    for nome, demo_func in demos:
        try:
            demo_func()
            time.sleep(2)  # Pausa entre demonstrações
        except KeyboardInterrupt:
            print("\n⚠️ Demonstração interrompida pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro na demonstração '{nome}': {e}")
            continue
    
    print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("\n📋 Próximos Passos:")
    print("1. 🐳 Configure Docker para usar containers")
    print("2. 🔧 Instale dependências: pip install selenium-stealth undetected-chromedriver")
    print("3. 🚀 Execute scrapers com modo stealth")
    print("4. 📊 Monitore taxa de sucesso vs detecção")
    
    print("\n⚡ Comandos Úteis:")
    print("# Iniciar Selenium Grid:")
    print("docker-compose -f docker-compose-selenium.yml up -d")
    print("\n# Ver status do Grid:")
    print("open http://localhost:4444")
    print("\n# Parar Grid:")
    print("docker-compose -f docker-compose-selenium.yml down")

if __name__ == "__main__":
    main()
