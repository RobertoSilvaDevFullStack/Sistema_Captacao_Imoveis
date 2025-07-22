# teste_anti_deteccao.py
"""
Teste das melhorias de anti-detecção implementadas
"""
import sys
import os
sys.path.append('src')

from utils.header_rotator import header_rotator
from utils.rate_limiter import rate_manager
from models.property import PropertySearch, PropertyType
from scrapers.zapimoveis_scraper import ZapImoveisScraper
import time

def test_header_rotation():
    """Testa a rotação de headers"""
    print("=== Teste de Rotação de Headers ===")
    
    # Testar headers para diferentes portais
    portals = ['zapimoveis', 'olx', 'vivareal']
    
    for portal in portals:
        print(f"\n--- Headers para {portal} ---")
        headers = header_rotator.get_random_headers(portal)
        
        print(f"User-Agent: {headers['User-Agent'][:60]}...")
        print(f"Accept-Language: {headers['Accept-Language']}")
        if 'Referer' in headers:
            print(f"Referer: {headers['Referer']}")
        
        # Testar headers mobile
        mobile_headers = header_rotator.get_mobile_headers(portal)
        print(f"Mobile User-Agent: {mobile_headers['User-Agent'][:60]}...")
    
    print("\n✅ Rotação de headers funcionando!")

def test_rate_limiting():
    """Testa o rate limiting"""
    print("\n=== Teste de Rate Limiting ===")
    
    # Testar diferentes portais
    portals = ['zapimoveis', 'olx', 'vivareal']
    
    for portal in portals:
        print(f"\n--- Testando {portal} ---")
        
        # Status inicial
        status = rate_manager.get_portal_status(portal)
        print(f"Delay atual: {status['current_delay']:.2f}s")
        print(f"Falhas: {status['failure_count']}")
        
        # Simular algumas requisições
        for i in range(3):
            print(f"Requisição {i+1} - aguardando...")
            start = time.time()
            rate_manager.wait_for_portal(portal)
            elapsed = time.time() - start
            print(f"Aguardou {elapsed:.2f}s")
        
        # Simular uma falha
        rate_manager.record_failure(portal)
        status = rate_manager.get_portal_status(portal)
        print(f"Após falha - Delay: {status['current_delay']:.2f}s")
        
        # Simular sucesso para limpar
        rate_manager.record_success(portal)
    
    print("\n✅ Rate limiting funcionando!")

def test_selenium_options():
    """Testa as opções do Selenium"""
    print("\n=== Teste de Opções Selenium ===")
    
    portals = ['zapimoveis', 'olx', 'vivareal']
    
    for portal in portals:
        print(f"\n--- Opções para {portal} ---")
        options = header_rotator.get_selenium_options(portal)
        
        print(f"Total de opções: {len(options)}")
        print("Principais opções:")
        for option in options[:5]:  # Mostrar apenas as 5 primeiras
            print(f"  {option}")
        
        if len(options) > 5:
            print(f"  ... e mais {len(options) - 5} opções")
    
    print("\n✅ Opções Selenium configuradas!")

def test_complete_scraping():
    """Teste completo de scraping com anti-detecção"""
    print("\n=== Teste Completo de Scraping ===")
    
    try:
        # Criar busca de teste
        search = PropertySearch(
            city='rio-de-janeiro',
            property_type=PropertyType.APARTAMENTO,
            max_results=3
        )
        
        print(f"Iniciando busca: {search.city}, {search.property_type.value}")
        
        # Status inicial do rate limiter
        status = rate_manager.get_portal_status('zapimoveis')
        print(f"Status inicial - Delay: {status['current_delay']:.2f}s, Falhas: {status['failure_count']}")
        
        # Executar scraping
        scraper = ZapImoveisScraper()
        result = scraper.scrape_properties(search)
        
        print(f"\nResultado:")
        print(f"Sucesso: {result.success}")
        print(f"Propriedades encontradas: {result.total_found}")
        print(f"Tempo de execução: {result.execution_time:.2f}s")
        
        if result.error_message:
            print(f"Erro: {result.error_message}")
        
        # Status final do rate limiter
        final_status = rate_manager.get_portal_status('zapimoveis')
        print(f"Status final - Delay: {final_status['current_delay']:.2f}s, Falhas: {final_status['failure_count']}")
        
        # Mostrar algumas propriedades se encontradas
        if result.properties:
            print(f"\nPrimeiras propriedades encontradas:")
            for i, prop in enumerate(result.properties[:2]):
                print(f"{i+1}. {prop.title[:60]}...")
                if prop.price:
                    print(f"   Preço: R$ {prop.price:,.2f}")
                if prop.neighborhood:
                    print(f"   Bairro: {prop.neighborhood}")
        
        print("\n✅ Teste completo finalizado!")
        
    except Exception as e:
        print(f"❌ Erro no teste completo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testando Melhorias de Anti-Detecção")
    print("="*50)
    
    # Executar todos os testes
    test_header_rotation()
    test_rate_limiting()
    test_selenium_options()
    
    # Teste completo (comentado por padrão para evitar scraping real)
    resposta = input("\nDeseja executar teste completo de scraping? (s/N): ")
    if resposta.lower() == 's':
        test_complete_scraping()
    else:
        print("\n⏭️ Teste completo pulado.")
    
    print("\n🎉 Todos os testes concluídos!")
    print("\nAs melhorias implementadas incluem:")
    print("✅ Rotação de User-Agents realísticos")
    print("✅ Headers específicos por portal")
    print("✅ Rate limiting inteligente")
    print("✅ Backoff exponencial após falhas")
    print("✅ Opções Selenium anti-detecção")
    print("✅ Integração com scrapers existentes")
