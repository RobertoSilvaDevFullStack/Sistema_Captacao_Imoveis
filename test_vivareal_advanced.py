#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste VivaReal Advanced - Estratégia com headers e parsing avançado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scrapers.vivareal_advanced import VivaRealAdvanced
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_vivareal_advanced():
    """Testa o scraper VivaReal Advanced"""
    
    print("🔥 Testando VivaReal Advanced (Headers + Parsing)")
    print("=" * 55)
    
    scraper = VivaRealAdvanced()
    
    try:
        # Teste 1: Rio de Janeiro - Apartamentos
        print("\n📍 Teste 1: Rio de Janeiro - Apartamentos")
        print("-" * 40)
        
        properties = scraper.scrape_properties(
            location='rio-de-janeiro',
            property_type='apartamento',
            max_results=15
        )
        
        print(f"✅ Resultado: {len(properties)} propriedades encontradas")
        
        # Mostrar algumas propriedades
        for i, prop in enumerate(properties[:5], 1):
            print(f"\n{i}. {prop.get('title', 'Sem título')[:60]}...")
            print(f"   💰 Preço: {prop.get('price', 'N/A')}")
            print(f"   📍 Local: {prop.get('location', 'N/A')[:40]}...")
            print(f"   📐 Área: {prop.get('area', 'N/A')}")
            if prop.get('url') != 'N/A':
                print(f"   🔗 URL válida: Sim")
            else:
                print(f"   🔗 URL válida: Não")
        
        # Teste 2: São Paulo - Casas  
        print(f"\n\n📍 Teste 2: São Paulo - Casas")
        print("-" * 40)
        
        sp_properties = scraper.scrape_properties(
            location='sao-paulo',
            property_type='casa',
            max_results=10
        )
        
        print(f"✅ Resultado: {len(sp_properties)} propriedades encontradas")
        
        if sp_properties:
            prop = sp_properties[0]
            print(f"\n📋 Exemplo de São Paulo:")
            print(f"   Título: {prop.get('title', 'N/A')[:50]}...")
            print(f"   Preço: {prop.get('price', 'N/A')}")
            print(f"   Local: {prop.get('location', 'N/A')}")
        
        # Teste 3: Belo Horizonte - Apartamentos
        print(f"\n\n📍 Teste 3: Belo Horizonte - Apartamentos")
        print("-" * 40)
        
        bh_properties = scraper.scrape_properties(
            location='belo-horizonte',
            property_type='apartamento',
            max_results=8
        )
        
        print(f"✅ Resultado: {len(bh_properties)} propriedades encontradas")
        
        # Estatísticas finais
        total_properties = len(properties) + len(sp_properties) + len(bh_properties)
        print(f"\n📊 RESUMO FINAL")
        print("=" * 30)
        print(f"Rio de Janeiro: {len(properties)} propriedades")
        print(f"São Paulo: {len(sp_properties)} propriedades")
        print(f"Belo Horizonte: {len(bh_properties)} propriedades")
        print(f"TOTAL: {total_properties} propriedades")
        
        # Análise de qualidade
        all_properties = properties + sp_properties + bh_properties
        
        if all_properties:
            with_price = sum(1 for p in all_properties if p.get('price') != 'N/A')
            with_location = sum(1 for p in all_properties if p.get('location') != 'N/A')
            with_url = sum(1 for p in all_properties if p.get('url') != 'N/A')
            
            print(f"\n📈 QUALIDADE DOS DADOS:")
            print(f"   💰 Com preço: {with_price}/{total_properties} ({with_price/total_properties*100:.1f}%)")
            print(f"   📍 Com localização: {with_location}/{total_properties} ({with_location/total_properties*100:.1f}%)")
            print(f"   🔗 Com URL: {with_url}/{total_properties} ({with_url/total_properties*100:.1f}%)")
        
        if total_properties > 0:
            print(f"\n🎉 SUCESSO! VivaReal Advanced funcionando!")
            print(f"   Taxa de sucesso: {total_properties}/3 cidades testadas")
            return True
        else:
            print(f"\n😞 FALHOU! Nenhuma propriedade encontrada")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        scraper.close()

def test_error_handling():
    """Testa tratamento de erros"""
    
    print(f"\n🧪 Testando tratamento de erros")
    print("-" * 35)
    
    scraper = VivaRealAdvanced()
    
    try:
        # Teste com localização inválida
        print("🔍 Testando localização inválida...")
        invalid_props = scraper.scrape_properties(
            location='cidade-inexistente-xyz',
            property_type='apartamento',
            max_results=5
        )
        print(f"   Resultado: {len(invalid_props)} propriedades (esperado: 0)")
        
        # Teste com tipo inválido
        print("🔍 Testando tipo de propriedade inválido...")
        invalid_type_props = scraper.scrape_properties(
            location='rio-de-janeiro',
            property_type='tipo-inexistente',
            max_results=5
        )
        print(f"   Resultado: {len(invalid_type_props)} propriedades")
        
        print("✅ Tratamento de erros funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de erro: {e}")
        return False
    
    finally:
        scraper.close()

if __name__ == "__main__":
    print("🚀 Iniciando testes VivaReal Advanced")
    print("🎯 Objetivo: Contornar Cloudflare com headers avançados")
    print()
    
    # Teste principal
    success1 = test_vivareal_advanced()
    
    # Teste de tratamento de erro
    success2 = test_error_handling()
    
    print(f"\n" + "="*60)
    
    if success1:
        print("🏆 RESULTADO: VivaReal Advanced FUNCIONANDO!")
        print("✅ Conseguimos contornar as proteções do VivaReal")
        print("✅ Sistema pode usar este scraper em produção")
    else:
        print("😞 RESULTADO: VivaReal Advanced não funcionou")
        print("❌ Proteções do VivaReal ainda ativas")
        print("💡 Pode ser necessário tentar outras abordagens")
    
    print(f"\n🔧 Próximos passos sugeridos:")
    if success1:
        print("   1. Integrar com o sistema principal")
        print("   2. Configurar para múltiplas cidades")
        print("   3. Otimizar rate limiting")
    else:
        print("   1. Tentar com proxies rotativos")
        print("   2. Implementar delays maiores")
        print("   3. Considerar Playwright/Selenium com stealth")
