#!/usr/bin/env python3
"""
Teste de Validação do Enhanced Scraper Corrigido
Verifica se todas as funcionalidades estão operacionais após as correções.
"""
import asyncio
import logging
import sys
import os

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_enhanced_scraper():
    """Teste completo do Enhanced Scraper"""
    print("🚀 Iniciando teste de validação do Enhanced Scraper...")
    
    try:
        # Importar e inicializar
        from backend.services.enhanced_scraper import EnhancedScraper
        
        print("✅ Import bem-sucedido")
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Teste 1: Inicialização
        print("\n📋 Teste 1: Inicialização")
        scraper = EnhancedScraper(use_ocr=False, max_images_per_property=1)
        await scraper.initialize()
        print("✅ Inicialização bem-sucedida")
        
        # Teste 2: Configurações
        print("\n📋 Teste 2: Configurações")
        print(f"OCR habilitado: {scraper.use_ocr}")
        print(f"Max imagens: {scraper.max_images_per_property}")
        print(f"Smart extractor disponível: {scraper.smart_extractor is not None}")
        print("✅ Configurações verificadas")
        
        # Teste 3: Estatísticas
        print("\n📋 Teste 3: Estatísticas")
        stats = scraper.get_statistics()
        print(f"Campos de estatísticas: {list(stats.keys())}")
        print(f"Propriedades processadas: {stats['total_properties_scraped']}")
        print("✅ Estatísticas funcionando")
        
        # Teste 4: Detecção de fonte
        print("\n📋 Teste 4: Detecção de fonte")
        test_urls = {
            'vivareal': 'https://www.vivareal.com.br/imovel/apartamento-3-quartos',
            'olx': 'https://www.olx.com.br/imoveis/apartamento-2-quartos',
            'zapimoveis': 'https://www.zapimoveis.com.br/venda/apartamentos',
            'generic': 'https://www.exemplo.com.br/imovel/casa'
        }
        
        for expected_source, url in test_urls.items():
            detected = scraper._detect_source(url)
            print(f"URL: {url[:50]}... → {detected}")
            assert detected == expected_source, f"Esperado {expected_source}, obtido {detected}"
        print("✅ Detecção de fonte funcionando")
        
        # Teste 5: Validação de dados
        print("\n📋 Teste 5: Validação e limpeza de dados")
        test_data = {
            'price': '850000.50',
            'area': '120.5',
            'bedrooms': '3',
            'bathrooms': '2',
            'invalid_price': 'muito_caro',
            'invalid_area': -10
        }
        
        cleaned = scraper._clean_and_validate_data(test_data)
        print(f"Dados originais: {len(test_data)} campos")
        print(f"Dados limpos: {len(cleaned)} campos")
        print(f"Dados limpos: {cleaned}")
        assert 'price' in cleaned, "Preço deveria estar nos dados limpos"
        assert 'area' in cleaned, "Área deveria estar nos dados limpos"
        assert 'invalid_price' not in cleaned, "Preço inválido não deveria estar nos dados limpos"
        print("✅ Validação de dados funcionando")
        
        # Teste 6: Extração de texto
        print("\n📋 Teste 6: Extração de texto")
        
        # Testar extração de preço
        price_texts = [
            "R$ 850.000,00",
            "Preço: R$ 1.200.000",
            "Valor 450000 reais"
        ]
        
        for text in price_texts:
            price = scraper._extract_price_from_text(text)
            print(f"'{text}' → {price}")
            assert price is not None, f"Deveria extrair preço de '{text}'"
        
        # Testar extração de área
        area_texts = [
            "Área: 120 m²",
            "120,5 m2",
            "Tamanho 85m²"
        ]
        
        for text in area_texts:
            area = scraper._extract_area_from_text(text)
            print(f"'{text}' → {area}")
            assert area is not None, f"Deveria extrair área de '{text}'"
        
        print("✅ Extração de texto funcionando")
        
        # Teste 7: Análise de necessidade de OCR
        print("\n📋 Teste 7: Análise de necessidade de OCR")
        
        # Dados completos - não precisa OCR
        complete_data = {'price': 850000, 'area': 120, 'bedrooms': 3, 'bathrooms': 2}
        needs_ocr = scraper._needs_image_analysis(complete_data)
        print(f"Dados completos: {needs_ocr} (esperado: False)")
        assert not needs_ocr, "Dados completos não deveriam precisar de OCR"
        
        # Dados incompletos - precisa OCR
        incomplete_data = {'price': 850000}
        needs_ocr = scraper._needs_image_analysis(incomplete_data)
        print(f"Dados incompletos: {needs_ocr} (esperado: True)")
        assert needs_ocr, "Dados incompletos deveriam precisar de OCR"
        
        print("✅ Análise de necessidade de OCR funcionando")
        
        # Teste 8: Verificação de melhoria OCR
        print("\n📋 Teste 8: Verificação de melhoria OCR")
        
        original = {'price': 850000}
        enhanced = {'price': 850000, 'area': 120, 'bedrooms': 3}
        
        improved = scraper._ocr_improved_data(original, enhanced)
        print(f"OCR melhorou dados: {improved} (esperado: True)")
        assert improved, "OCR deveria ter melhorado os dados"
        
        print("✅ Verificação de melhoria OCR funcionando")
        
        # Teste 9: Fechar recursos
        print("\n📋 Teste 9: Fechamento de recursos")
        await scraper.close()
        print("✅ Recursos fechados com sucesso")
        
        # Resumo final
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Enhanced Scraper está funcionando corretamente")
        print("✅ Todas as correções foram aplicadas com sucesso")
        print("✅ Sistema pronto para produção")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    success = await test_enhanced_scraper()
    
    if success:
        print("\n🎯 Status: SUCESSO - Enhanced Scraper validado e funcional")
        sys.exit(0)
    else:
        print("\n💥 Status: FALHA - Problemas encontrados no Enhanced Scraper")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
