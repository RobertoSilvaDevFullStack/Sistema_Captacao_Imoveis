# demo_rate_limiting_avancado.py
"""
Demonstração do Sistema de Rate Limiting Inteligente Avançado
"""
import time
import random
import logging
from datetime import datetime
from src.utils.advanced_rate_limiter import advanced_rate_manager, BlockingLevel
from src.utils.rate_limiting_decorator import (
    intelligent_rate_limit, 
    zapimoveis_rate_limit,
    RateLimitedContext,
    get_portal_health,
    suggest_optimal_timing
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def demo_rate_limiting_basico():
    """Demonstração básica do rate limiting avançado"""
    print("🎯 DEMONSTRAÇÃO: RATE LIMITING INTELIGENTE AVANÇADO")
    print("=" * 70)
    
    print("\n1. Testando delays inteligentes...")
    
    portais = ['zapimoveis', 'olx', 'vivareal']
    acoes = ['navigation', 'search', 'reading', 'idle']
    
    for portal in portais:
        print(f"\n📊 Portal: {portal.upper()}")
        
        for acao in acoes[:2]:  # Testar apenas 2 ações por portal
            print(f"   🔄 Ação: {acao}")
            
            start_time = time.time()
            advanced_rate_manager.wait_for_request(portal, acao)
            delay_time = time.time() - start_time
            
            print(f"      ⏱️  Delay aplicado: {delay_time:.2f}s")
            
            # Simular resultado da requisição
            success = random.choice([True, True, True, False])  # 75% sucesso
            response_time = random.uniform(1.0, 5.0)
            
            advanced_rate_manager.record_request_result(
                portal=portal,
                success=success,
                response_time=response_time,
                status_code=200 if success else random.choice([403, 429, 503]),
                blocking_level=BlockingLevel.NORMAL if success else random.choice([
                    BlockingLevel.SOFT_BLOCK, BlockingLevel.HARD_BLOCK
                ])
            )
            
            status = "✅ Sucesso" if success else "❌ Falha"
            print(f"      📈 Resultado: {status} ({response_time:.2f}s)")

def demo_decorators():
    """Demonstração dos decorators de rate limiting"""
    print("\n🎭 DEMONSTRAÇÃO: DECORATORS DE RATE LIMITING")
    print("=" * 70)
    
    # Função simulada de scraping
    @zapimoveis_rate_limit(action_type='search', max_retries=2)
    def buscar_imoveis_zapimoveis(cidade: str, tipo: str):
        """Simula busca de imóveis no ZapImóveis"""
        print(f"   🔍 Buscando {tipo} em {cidade} no ZapImóveis...")
        
        # Simular falha ocasional
        if random.random() < 0.3:  # 30% chance de falha
            raise Exception("Erro simulado de rede")
        
        # Simular tempo de processamento
        time.sleep(random.uniform(0.5, 2.0))
        
        return f"Encontrados {random.randint(5, 50)} imóveis"
    
    @intelligent_rate_limit('olx', 'navigation', max_retries=1)
    def navegar_olx():
        """Simula navegação no OLX"""
        print("   🧭 Navegando no OLX...")
        
        if random.random() < 0.2:  # 20% chance de falha
            raise Exception("Timeout de conexão")
        
        time.sleep(random.uniform(0.2, 1.0))
        return "Página carregada com sucesso"
    
    print("\n1. Testando decorator específico do ZapImóveis...")
    try:
        resultado = buscar_imoveis_zapimoveis("São Paulo", "apartamento")
        print(f"   ✅ {resultado}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n2. Testando decorator genérico...")
    try:
        resultado = navegar_olx()
        print(f"   ✅ {resultado}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def demo_context_manager():
    """Demonstração do context manager"""
    print("\n🏗️ DEMONSTRAÇÃO: CONTEXT MANAGER")
    print("=" * 70)
    
    portais = ['zapimoveis', 'olx', 'vivareal']
    
    for portal in portais:
        print(f"\n📊 Testando context manager para {portal.upper()}...")
        
        try:
            with RateLimitedContext(portal, 'reading') as ctx:
                print(f"   📖 Simulando leitura de página...")
                
                # Simular trabalho
                time.sleep(random.uniform(0.5, 2.0))
                
                # Simular falha ocasional
                if random.random() < 0.2:  # 20% chance de falha
                    raise Exception(f"Erro simulado para {portal}")
                
                print(f"   ✅ Leitura concluída com sucesso")
                
        except Exception as e:
            print(f"   ❌ Erro capturado: {e}")

def demo_analise_comportamento():
    """Demonstração da análise de comportamento"""
    print("\n🧠 DEMONSTRAÇÃO: ANÁLISE DE COMPORTAMENTO DOS PORTAIS")
    print("=" * 70)
    
    # Simular histórico de requisições para análise
    print("\n1. Simulando histórico de requisições...")
    
    portais = ['zapimoveis', 'olx', 'vivareal']
    
    for portal in portais:
        print(f"\n📊 Analisando {portal.upper()}...")
        
        # Simular várias requisições para gerar dados
        for i in range(10):
            # Variar sucesso baseado no portal
            success_rates = {'zapimoveis': 0.8, 'olx': 0.9, 'vivareal': 0.7}
            success = random.random() < success_rates.get(portal, 0.8)
            
            response_time = random.uniform(1.0, 8.0)
            status_code = 200 if success else random.choice([403, 429, 503, 500])
            
            blocking_level = BlockingLevel.NORMAL
            if not success:
                blocking_level = random.choice([
                    BlockingLevel.SOFT_BLOCK,
                    BlockingLevel.HARD_BLOCK,
                    BlockingLevel.NORMAL
                ])
            
            advanced_rate_manager.record_request_result(
                portal=portal,
                success=success,
                response_time=response_time,
                status_code=status_code,
                blocking_level=blocking_level
            )
        
        # Analisar estatísticas
        stats = advanced_rate_manager.get_portal_statistics(portal)
        health = get_portal_health(portal)
        timing = suggest_optimal_timing(portal)
        
        print(f"   📈 Estatísticas:")
        print(f"      📊 Taxa de sucesso: {stats.get('success_rate', 0):.1%}")
        print(f"      ⏱️  Tempo médio: {stats.get('avg_response_time', 0):.2f}s")
        print(f"      🔥 Falhas recentes: {stats.get('recent_failures', 0)}")
        print(f"   🏥 Saúde: {health['health']} - {health['recommendation']}")
        print(f"   🕐 Timing: {timing['recommendation']}")

def demo_retry_inteligente():
    """Demonstração do sistema de retry inteligente"""
    print("\n🔄 DEMONSTRAÇÃO: SISTEMA DE RETRY INTELIGENTE")
    print("=" * 70)
    
    @intelligent_rate_limit('vivareal', 'search', max_retries=3, enable_retry=True)
    def funcao_com_falhas():
        """Função que falha propositalmente para testar retry"""
        # Simular diferentes tipos de falha
        error_types = [
            "Timeout de conexão",
            "Rate limit exceeded", 
            "Server temporarily unavailable",
            "Captcha detectado"
        ]
        
        error = random.choice(error_types)
        print(f"   💥 Simulando erro: {error}")
        
        if "Captcha" in error:
            raise Exception("Captcha detectado - bloqueio severo")
        elif "Rate limit" in error:
            raise Exception("429 - Rate limit exceeded")
        elif "Server" in error:
            raise Exception("503 - Server temporarily unavailable")
        else:
            raise Exception("Timeout de conexão")
    
    print("\n1. Testando retry com diferentes tipos de erro...")
    
    for i in range(3):
        print(f"\n   🎯 Teste {i + 1}:")
        try:
            resultado = funcao_com_falhas()
            print(f"   ✅ Sucesso: {resultado}")
        except Exception as e:
            print(f"   ❌ Falha final: {e}")

def demo_monitoramento_tempo_real():
    """Demonstração do monitoramento em tempo real"""
    print("\n📊 DEMONSTRAÇÃO: MONITORAMENTO EM TEMPO REAL")
    print("=" * 70)
    
    print("\n1. Executando requisições monitoradas por 30 segundos...")
    print("   (Ctrl+C para parar)")
    
    start_time = time.time()
    iteration = 0
    
    try:
        while time.time() - start_time < 30:  # 30 segundos
            iteration += 1
            
            # Escolher portal aleatório
            portal = random.choice(['zapimoveis', 'olx', 'vivareal'])
            action = random.choice(['navigation', 'search', 'reading'])
            
            print(f"\n   🔄 Iteração {iteration}: {portal} ({action})")
            
            # Simular requisição com rate limiting
            req_start = time.time()
            advanced_rate_manager.wait_for_request(portal, action)
            
            # Simular trabalho
            work_time = random.uniform(0.5, 3.0)
            time.sleep(work_time)
            
            # Simular resultado
            success = random.random() < 0.8  # 80% sucesso
            total_time = time.time() - req_start
            
            advanced_rate_manager.record_request_result(
                portal=portal,
                success=success,
                response_time=total_time,
                status_code=200 if success else random.choice([403, 429, 503]),
                blocking_level=BlockingLevel.NORMAL if success else BlockingLevel.SOFT_BLOCK
            )
            
            # Mostrar status
            health = get_portal_health(portal)
            status = "✅" if success else "❌"
            print(f"      {status} {total_time:.2f}s - Saúde: {health['health']}")
            
            # Pequeno delay entre iterações
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n   ⏹️  Monitoramento interrompido (executadas {iteration} iterações)")
    
    # Resumo final
    print(f"\n2. Resumo do monitoramento:")
    
    for portal in ['zapimoveis', 'olx', 'vivareal']:
        stats = advanced_rate_manager.get_portal_statistics(portal)
        health = get_portal_health(portal)
        
        if stats.get('status') == 'active':
            print(f"   📊 {portal.upper()}:")
            print(f"      🎯 Requisições: {stats.get('total_requests', 0)}")
            print(f"      ✅ Taxa sucesso: {stats.get('success_rate', 0):.1%}")
            print(f"      🏥 Saúde: {health['health']}")

def main():
    """Função principal com menu de demonstrações"""
    print("🚀 DEMONSTRAÇÕES DO RATE LIMITING INTELIGENTE AVANÇADO")
    print("=" * 80)
    
    demos = {
        "1": ("Rate Limiting Básico", demo_rate_limiting_basico),
        "2": ("Decorators de Rate Limiting", demo_decorators),
        "3": ("Context Manager", demo_context_manager),
        "4": ("Análise de Comportamento", demo_analise_comportamento),
        "5": ("Retry Inteligente", demo_retry_inteligente),
        "6": ("Monitoramento Tempo Real", demo_monitoramento_tempo_real),
        "7": ("Executar todas as demos", None),
        "8": ("Sair", None)
    }
    
    while True:
        print(f"\n📋 Demonstrações disponíveis:")
        for key, (description, _) in demos.items():
            print(f"  {key}. {description}")
        
        choice = input("\n🎯 Escolha uma demonstração: ").strip()
        
        if choice == "8":
            print("👋 Demonstrações encerradas!")
            break
        elif choice == "7":
            # Executar todas as demos
            for key in ["1", "2", "3", "4", "5"]:  # Excluir monitoramento tempo real
                if demos[key][1]:
                    try:
                        print(f"\n" + "="*80)
                        demos[key][1]()
                        time.sleep(2)  # Pausa entre demos
                    except Exception as e:
                        logger.error(f"Erro na demo {key}: {e}")
            break
        elif choice in demos and demos[choice][1]:
            try:
                demos[choice][1]()
            except Exception as e:
                logger.error(f"Erro na demonstração: {e}")
                print(f"❌ Erro: {e}")
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
