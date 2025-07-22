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
    
    print("\n⚡ Próximos Passos Recomendados:")
    print("1. Implementar sistema de proxies rotativos")
    print("2. Adicionar stealth mode para Selenium")
    print("3. Configurar alertas de bloqueio")
    print("4. Testar com sites reais")

if __name__ == "__main__":
    main()
