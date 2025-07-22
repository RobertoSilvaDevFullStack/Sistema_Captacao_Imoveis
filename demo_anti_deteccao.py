#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração das melhorias de anti-detecção implementadas
"""
import os
import sys

# Adicionar diretório src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def main():
    print("🚀 Sistema de Anti-Detecção - Demonstração")
    print("=" * 50)
    
    try:
        # Testar Header Rotator
        print("\n1️⃣ Testando Rotação de Headers...")
        from utils.header_rotator import header_rotator
        
        headers_zap = header_rotator.get_random_headers('zapimoveis')
        headers_olx = header_rotator.get_random_headers('olx')
        
        print(f"✅ ZapImóveis User-Agent: {headers_zap['User-Agent'][:60]}...")
        print(f"✅ OLX User-Agent: {headers_olx['User-Agent'][:60]}...")
        
        # Testar headers mobile
        mobile_headers = header_rotator.get_mobile_headers('zapimoveis')
        print(f"✅ Mobile User-Agent: {mobile_headers['User-Agent'][:60]}...")
        
    except Exception as e:
        print(f"❌ Erro no teste de headers: {e}")
    
    try:
        # Testar Rate Limiter
        print("\n2️⃣ Testando Rate Limiting...")
        from utils.rate_limiter import rate_manager
        
        # Status inicial dos portais
        for portal in ['zapimoveis', 'olx', 'vivareal']:
            status = rate_manager.get_portal_status(portal)
            print(f"✅ {portal.capitalize()}: {status['current_delay']:.1f}s delay, {status['failure_count']} falhas")
        
    except Exception as e:
        print(f"❌ Erro no teste de rate limiting: {e}")
    
    try:
        # Testar Rate Limiting Avançado
        print("\n2️⃣b Testando Rate Limiting Avançado...")
        from utils.advanced_rate_limiter import advanced_rate_manager
        from utils.rate_limiting_decorator import get_portal_health, suggest_optimal_timing
        
        # Testar health dos portais
        for portal in ['zapimoveis', 'olx', 'vivareal']:
            health = get_portal_health(portal)
            timing = suggest_optimal_timing(portal)
            
            print(f"✅ {portal.capitalize()}:")
            print(f"   🏥 Saúde: {health['health']}")
            print(f"   💡 Timing: {'✓ Ótimo' if timing['is_optimal_time'] else f'Aguardar {timing['hours_to_optimal']}h'}")
        
    except Exception as e:
        print(f"❌ Erro no teste de rate limiting avançado: {e}")
    
    try:
        # Testar Selenium Stealth
        print("\n4️⃣ Testando Selenium Stealth...")
        
        try:
            from utils.selenium_stealth import (
                StealthConfig, 
                HumanBehaviorConfig,
                create_stealth_driver
            )
            
            print("✅ Módulos Selenium Stealth disponíveis")
            
            # Testar configurações por portal
            portais_stealth = ['zapimoveis', 'olx', 'vivareal']
            for portal in portais_stealth:
                print(f"   🎯 {portal.capitalize()}: Configuração stealth preparada")
                
                # Simular criação de configuração (sem criar driver real)
                config = StealthConfig(
                    use_undetected_chrome=True,
                    headless=True,
                    window_size=(1366, 768) if portal == 'zapimoveis' else (1920, 1080)
                )
                print(f"      📐 Janela: {config.window_size}")
                print(f"      🤖 Undetected: {config.use_undetected_chrome}")
            
            print("✅ Selenium Stealth configurado com sucesso!")
            
        except ImportError:
            print("⚠️ Selenium Stealth não disponível")
            print("   💡 Execute: pip install selenium-stealth undetected-chromedriver")
        
    except Exception as e:
        print(f"❌ Erro no teste de Selenium Stealth: {e}")
    
    try:
        # Testar Sistema de Containers
        print("\n5️⃣ Testando Sistema de Containers...")
        
        try:
            from utils.selenium_containers import (
                SeleniumContainerPool,
                ContainerConfig,
                create_docker_compose_config
            )
            
            print("✅ Módulos de containers disponíveis")
            
            # Verificar Docker
            try:
                import docker
                client = docker.from_env()
                client.ping()
                print("   🐳 Docker está disponível e funcionando")
                
                # Mostrar configuração exemplo
                config = ContainerConfig(
                    image="selenium/standalone-chrome:latest",
                    memory_limit="1g",
                    shm_size="2g"
                )
                print(f"   📋 Configuração exemplo: {config.image}")
                print(f"   💾 Memória: {config.memory_limit}, SHM: {config.shm_size}")
                
            except Exception:
                print("   ⚠️ Docker não está disponível")
                print("   💡 Instale Docker Desktop para usar containers")
            
            print("✅ Sistema de containers configurado!")
            
        except ImportError:
            print("⚠️ Módulos de containers não disponíveis")
            print("   💡 Execute: pip install docker")
            
    except Exception as e:
        print(f"❌ Erro no teste de containers: {e}")
    
    try:
        # Testar Selenium Options
        print("\n3️⃣ Testando Opções Selenium...")
        
        selenium_options = header_rotator.get_selenium_options('zapimoveis')
        print(f"✅ Geradas {len(selenium_options)} opções para ZapImóveis")
        print(f"   Exemplo: {selenium_options[0]}")
        
    except Exception as e:
        print(f"❌ Erro no teste de Selenium: {e}")
    
    print("\n🎉 Demonstração Concluída!")
    print("\n📋 Melhorias Implementadas:")
    print("✅ Rotação de User-Agents realísticos (12+ variações)")
    print("✅ Headers específicos por portal (ZAP, OLX, VivaReal)")
    print("✅ Headers mobile para menor detecção")
    print("✅ Rate limiting inteligente por portal")
    print("✅ Backoff exponencial após falhas")
    print("✅ Configurações Selenium anti-detecção")
    print("✅ Monitoramento de requisições por minuto")
    print("✅ Rate Limiting Avançado com comportamento humano")
    print("✅ Sistema Selenium Stealth com evasão de detecção")
    print("✅ Containers Docker para paralelização")
    print("✅ Simulação de comportamento humano realístico")
    
    print("\n⚡ Próximos Passos Recomendados:")
    print("1. 🐳 Configurar Docker para containers Selenium")
    print("2. 🔧 Instalar dependências stealth completas")
    print("3. 🎭 Implementar rotação de proxies")
    print("4. 📊 Configurar dashboard de monitoramento")
    print("5. 🤖 Testar com sites reais")
    
    print("\n💡 Comandos de Setup:")
    print("# Instalar dependências stealth:")
    print("pip install selenium-stealth undetected-chromedriver docker")
    print("\n# Iniciar Selenium Grid:")
    print("docker-compose -f docker-compose-selenium.yml up -d")
    print("\n# Testar sistema completo:")
    print("python demo_selenium_stealth.py")

if __name__ == "__main__":
    main()
