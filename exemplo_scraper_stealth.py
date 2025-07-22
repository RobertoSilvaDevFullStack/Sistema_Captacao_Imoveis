# exemplo_scraper_stealth.py
"""
Exemplo prático de integração do Selenium Stealth com scrapers existentes
"""
import time
import logging
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def exemplo_scraper_zapimoveis_stealth():
    """Exemplo de scraper ZapImóveis usando Selenium Stealth"""
    print("🏠 EXEMPLO: Scraper ZapImóveis com Stealth")
    print("=" * 50)
    
    try:
        from src.utils.selenium_stealth import create_stealth_driver
        from src.utils.advanced_rate_limiter import advanced_rate_manager
        from src.utils.rate_limiting_decorator import zapimoveis_rate_limit
        
        print("✅ Módulos importados com sucesso")
        
        # Função exemplo de busca com stealth
        @zapimoveis_rate_limit(action_type='search', max_retries=3)
        def buscar_imoveis_stealth(cidade: str, tipo: str = 'apartamento'):
            """Busca imóveis usando Selenium Stealth"""
            
            print(f"🔍 Buscando {tipo} em {cidade}...")
            
            # Criar driver stealth específico para ZapImóveis
            with create_stealth_driver('zapimoveis', headless=True) as stealth_driver:
                
                # URL de exemplo (usando página de teste)
                url_busca = f"https://httpbin.org/get?cidade={cidade}&tipo={tipo}"
                
                # Navegar com comportamento humano
                print("🌐 Navegando para página de busca...")
                stealth_driver.get(url_busca, simulate_reading=True)
                
                # Simular interação humana
                print("🤖 Simulando comportamento humano...")
                
                # Scroll para simular visualização dos resultados
                stealth_driver.scroll_page('down', 400)
                stealth_driver.wait_and_think(2, 4)
                stealth_driver.scroll_page('down', 300)
                stealth_driver.wait_and_think(1, 3)
                
                # Simular tempo de análise dos resultados
                stealth_driver.behavior_simulator.simulate_page_reading(
                    stealth_driver.driver, 
                    reading_duration=8.0
                )
                
                # Extrair dados (simulado)
                resultados = {
                    'cidade': cidade,
                    'tipo': tipo,
                    'total_encontrados': 25,  # Simulado
                    'imoveis': [
                        {'id': i, 'preco': 500000 + (i * 10000), 'quartos': 2 + (i % 3)}
                        for i in range(5)  # Simulado
                    ],
                    'user_agent_usado': stealth_driver.driver.execute_script("return navigator.userAgent;")[:60] + "...",
                    'timestamp': time.time()
                }
                
                print(f"✅ Encontrados {resultados['total_encontrados']} imóveis")
                print(f"🤖 User-Agent: {resultados['user_agent_usado']}")
                
                return resultados
        
        # Testar busca
        resultado = buscar_imoveis_stealth("São Paulo", "apartamento")
        
        print(f"\n📊 Resultado da busca:")
        print(f"   🏙️  Cidade: {resultado['cidade']}")
        print(f"   🏠 Tipo: {resultado['tipo']}")
        print(f"   📈 Total: {resultado['total_encontrados']} imóveis")
        print(f"   🕒 Timestamp: {time.strftime('%H:%M:%S', time.localtime(resultado['timestamp']))}")
        
        # Mostrar alguns imóveis encontrados
        print(f"\n🏘️  Primeiros imóveis:")
        for imovel in resultado['imoveis'][:3]:
            print(f"   #{imovel['id']}: R$ {imovel['preco']:,} - {imovel['quartos']} quartos")
        
        print("✅ Scraper stealth executado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no scraper stealth: {e}")
        import traceback
        traceback.print_exc()

def exemplo_scraper_paralelo_containers():
    """Exemplo de scraping paralelo usando containers"""
    print("\n🐳 EXEMPLO: Scraping Paralelo com Containers")
    print("=" * 55)
    
    try:
        # Simular uso de containers (sem executar realmente)
        cidades = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre']
        
        print("🏗️  Configurando tarefas paralelas...")
        
        def tarefa_busca_cidade(selenium_url: str, cidade: str):
            """Tarefa de busca para uma cidade específica"""
            print(f"🔍 Executando busca para {cidade} via {selenium_url}")
            
            # Simular processamento
            time.sleep(2)  # Simular tempo de busca
            
            return {
                'cidade': cidade,
                'imoveis_encontrados': len(cidade) * 10,  # Simulado
                'tempo_execucao': 2.0,
                'selenium_url': selenium_url
            }
        
        # Simular execução paralela
        resultados_simulados = []
        
        for i, cidade in enumerate(cidades):
            selenium_url = f"http://localhost:444{4+i}/wd/hub"  # URLs simuladas
            resultado = {
                'cidade': cidade,
                'imoveis_encontrados': len(cidade) * 10,
                'tempo_execucao': 2.0 + (i * 0.5),
                'selenium_url': selenium_url
            }
            resultados_simulados.append(resultado)
            print(f"   ✅ {cidade}: {resultado['imoveis_encontrados']} imóveis em {resultado['tempo_execucao']:.1f}s")
        
        # Consolidar resultados
        total_imoveis = sum(r['imoveis_encontrados'] for r in resultados_simulados)
        tempo_total = max(r['tempo_execucao'] for r in resultados_simulados)
        
        print(f"\n📊 Resultados Consolidados:")
        print(f"   🏙️  Cidades processadas: {len(cidades)}")
        print(f"   🏠 Total de imóveis: {total_imoveis}")
        print(f"   ⏱️  Tempo total: {tempo_total:.1f}s (paralelo)")
        print(f"   🚀 Speedup: {sum(r['tempo_execucao'] for r in resultados_simulados) / tempo_total:.1f}x")
        
        print("\n💡 Para executar realmente:")
        print("   1. docker-compose -f docker-compose-selenium.yml up -d")
        print("   2. Aguardar containers iniciarem")
        print("   3. Usar execute_parallel_selenium_tasks()")
        
    except Exception as e:
        print(f"❌ Erro no exemplo de containers: {e}")

def exemplo_comportamento_humano_avancado():
    """Exemplo de comportamento humano avançado"""
    print("\n🧠 EXEMPLO: Comportamento Humano Avançado")
    print("=" * 50)
    
    try:
        from src.utils.selenium_stealth import (
            StealthWebDriver, 
            StealthConfig, 
            HumanBehaviorConfig
        )
        
        print("🎭 Configurando comportamento humano...")
        
        # Configuração de comportamento realístico
        behavior_config = HumanBehaviorConfig(
            reading_speed_wpm=180,  # Leitura mais lenta
            typing_speed_cpm=160,   # Digitação realística
            min_scroll_pause=1.0,   # Pausas maiores
            max_scroll_pause=3.0,
            min_click_delay=0.5,
            max_click_delay=2.0
        )
        
        stealth_config = StealthConfig(
            use_undetected_chrome=True,
            headless=True,
            window_size=(1366, 768)
        )
        
        print("✅ Configurações criadas:")
        print(f"   📖 Velocidade de leitura: {behavior_config.reading_speed_wpm} WPM")
        print(f"   ⌨️  Velocidade de digitação: {behavior_config.typing_speed_cpm} CPM")
        print(f"   🖱️  Delay de clique: {behavior_config.min_click_delay}-{behavior_config.max_click_delay}s")
        print(f"   📜 Pausa de scroll: {behavior_config.min_scroll_pause}-{behavior_config.max_scroll_pause}s")
        
        # Exemplo de uso
        with StealthWebDriver(stealth_config, behavior_config) as driver:
            print("\n🌐 Simulando navegação humana...")
            
            # Navegar para página de teste
            driver.get("https://httpbin.org/html", simulate_reading=True)
            
            # Comportamentos humanos
            behaviors = [
                ("Scroll para baixo", lambda: driver.scroll_page('down', 300)),
                ("Pausa para leitura", lambda: driver.wait_and_think(3, 6)),
                ("Scroll para cima", lambda: driver.scroll_page('up', 150)),
                ("Análise da página", lambda: driver.behavior_simulator.simulate_page_reading(driver.driver, 5.0))
            ]
            
            for nome, acao in behaviors:
                print(f"   🎬 {nome}...")
                acao()
                time.sleep(0.5)  # Pequena pausa entre ações
        
        print("✅ Simulação de comportamento humano concluída!")
        
    except Exception as e:
        print(f"❌ Erro na simulação de comportamento: {e}")

def exemplo_monitoramento_deteccao():
    """Exemplo de monitoramento de detecção"""
    print("\n📊 EXEMPLO: Monitoramento de Detecção")
    print("=" * 45)
    
    try:
        from src.utils.advanced_rate_limiter import advanced_rate_manager, BlockingLevel
        from src.utils.rate_limiting_decorator import get_portal_health
        
        print("🔍 Simulando tentativas de scraping...")
        
        # Simular diferentes cenários
        cenarios = [
            ("Requisição normal", True, 1.5, 200, BlockingLevel.NORMAL),
            ("Timeout leve", False, 8.0, 504, BlockingLevel.SOFT_BLOCK),
            ("Rate limit", False, 0.5, 429, BlockingLevel.HARD_BLOCK),
            ("Requisição normal", True, 2.1, 200, BlockingLevel.NORMAL),
            ("Captcha detectado", False, 3.0, 403, BlockingLevel.CAPTCHA),
            ("Requisição normal", True, 1.8, 200, BlockingLevel.NORMAL),
        ]
        
        portal = 'zapimoveis'
        
        for i, (descricao, sucesso, tempo, status, nivel) in enumerate(cenarios, 1):
            print(f"\n{i}. {descricao}:")
            
            # Aplicar rate limiting
            advanced_rate_manager.wait_for_request(portal, 'search')
            
            # Registrar resultado
            advanced_rate_manager.record_request_result(
                portal=portal,
                success=sucesso,
                response_time=tempo,
                status_code=status,
                blocking_level=nivel
            )
            
            status_icon = "✅" if sucesso else "❌"
            print(f"   {status_icon} {descricao}: {tempo:.1f}s, status={status}, level={nivel.value}")
            
            # Verificar se deve fazer retry
            should_retry, retry_delay = advanced_rate_manager.should_retry_request(
                portal=portal,
                attempt=1,
                last_error=f"Status {status}"
            )
            
            if not sucesso:
                retry_info = f"Retry em {retry_delay:.1f}s" if should_retry else "Não retentar"
                print(f"   🔄 {retry_info}")
        
        # Análise final
        print(f"\n📈 Análise Final:")
        stats = advanced_rate_manager.get_portal_statistics(portal)
        health = get_portal_health(portal)
        
        print(f"   📊 Total de requisições: {stats.get('total_requests', 0)}")
        print(f"   ✅ Taxa de sucesso: {stats.get('success_rate', 0):.1%}")
        print(f"   ⏱️  Tempo médio: {stats.get('avg_response_time', 0):.2f}s")
        print(f"   🏥 Saúde do portal: {health['health']}")
        print(f"   💡 Recomendação: {health['recommendation']}")
        
        # Recomendações baseadas na saúde
        if health['health'] == 'poor':
            print("\n⚠️  Portal com problemas detectados!")
            print("   🛑 Recomendação: Pausar scraping por 30-60 minutos")
            print("   🔄 Considerar mudar User-Agent ou usar proxy")
        elif health['health'] == 'fair':
            print("\n⚠️  Portal com problemas intermitentes")
            print("   🐌 Recomendação: Reduzir frequência de requisições")
            print("   ⏱️  Aumentar delays entre requisições")
        else:
            print("\n✅ Portal funcionando bem!")
            print("   🚀 Pode continuar com scraping normal")
        
    except Exception as e:
        print(f"❌ Erro no monitoramento: {e}")

def main():
    """Função principal"""
    print("🚀 EXEMPLOS PRÁTICOS: SELENIUM STEALTH + ANTI-DETECÇÃO")
    print("=" * 70)
    
    exemplos = [
        ("Scraper ZapImóveis Stealth", exemplo_scraper_zapimoveis_stealth),
        ("Scraping Paralelo com Containers", exemplo_scraper_paralelo_containers),
        ("Comportamento Humano Avançado", exemplo_comportamento_humano_avancado),
        ("Monitoramento de Detecção", exemplo_monitoramento_deteccao)
    ]
    
    for nome, exemplo_func in exemplos:
        try:
            exemplo_func()
            time.sleep(2)  # Pausa entre exemplos
        except KeyboardInterrupt:
            print("\n⚠️ Demonstração interrompida pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro no exemplo '{nome}': {e}")
            continue
    
    print("\n🎉 EXEMPLOS CONCLUÍDOS!")
    print("\n📋 Sistema Completo Implementado:")
    print("✅ Selenium Stealth com evasão de detecção")
    print("✅ Comportamento humano realístico")
    print("✅ Rate limiting inteligente")
    print("✅ Sistema de containers para paralelização")
    print("✅ Monitoramento de saúde dos portais")
    print("✅ Configurações específicas por portal")
    print("✅ Retry inteligente com backoff exponencial")
    
    print("\n🚀 Próximos Passos:")
    print("1. 🔧 Integrar com scrapers existentes")
    print("2. 🐳 Configurar Docker Grid para produção")
    print("3. 📊 Implementar dashboard de monitoramento")
    print("4. 🎭 Adicionar rotação de proxies")
    print("5. 🤖 Treinar modelos de ML para detecção")

if __name__ == "__main__":
    main()
