#!/usr/bin/env python3
"""
Teste de Validação Completa do Smart Data Extractor
Verifica se todas as funcionalidades estão operacionais após as correções.
"""
import asyncio
import logging
import sys
import os

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_smart_data_extractor():
    """Teste completo do Smart Data Extractor"""
    print("🚀 Iniciando teste de validação completa do Smart Data Extractor...")
    
    try:
        # Importar e inicializar
        from backend.services.smart_data_extractor import SmartDataExtractor
        
        print("✅ Import bem-sucedido")
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Teste 1: Inicialização
        print("\n📋 Teste 1: Inicialização")
        extractor = SmartDataExtractor(use_cache=True, use_ocr=True)
        print("✅ SmartDataExtractor inicializado com sucesso")
        
        # Verificar configurações
        print(f"OCR disponível: {extractor.use_ocr_fallback}")
        print(f"Cache disponível: {extractor.use_cache}")
        print(f"OCR Service: {type(extractor.ocr_service).__name__ if extractor.ocr_service else 'None'}")
        print(f"Cache Service: {type(extractor.cache_service).__name__ if extractor.cache_service else 'None'}")
        print(f"DB Service: {type(extractor.db_service).__name__ if extractor.db_service else 'None'}")
        
        # Teste 2: Inicialização de serviços
        print("\n📋 Teste 2: Inicialização de serviços")
        await extractor.initialize()
        print("✅ Serviços inicializados")
        
        # Teste 3: Extração de dados estruturados
        print("\n📋 Teste 3: Extração de dados estruturados")
        structured_data = {
            'price': 850000,
            'area': 120,
            'bedrooms': 3,
            'bathrooms': 2,
            'address': 'Rua das Flores, 123',
            'city': 'São Paulo',
            'state': 'SP'
        }
        
        result = await extractor.extract_property_data(structured_data=structured_data)
        
        print(f"Sucesso: {result['success']}")
        print(f"Confiança: {result['overall_confidence']:.2f}")
        print(f"Campos extraídos: {len([k for k, v in result['data'].items() if v is not None])}")
        print(f"Fontes: {result['sources']}")
        print(f"Tempo de processamento: {result['processing_time']:.3f}s")
        
        assert result['success'], "Extração estruturada deveria ter sucesso"
        assert result['overall_confidence'] > 0.5, "Confiança deveria ser alta para dados estruturados"
        
        print("✅ Extração estruturada funcionando")
        
        # Teste 4: Extração de HTML
        print("\n📋 Teste 4: Extração de HTML")
        html_content = """
        <div class="property">
            <h1>Apartamento 3 quartos</h1>
            <span class="price">R$ 750.000,00</span>
            <div class="area">95 m²</div>
            <div class="bedrooms">2 quartos</div>
            <div class="bathrooms">1 banheiro</div>
        </div>
        """
        
        result_html = await extractor.extract_property_data(
            html_content=html_content,
            url="https://exemplo.com/imovel123"
        )
        
        print(f"Sucesso: {result_html['success']}")
        print(f"Confiança: {result_html['overall_confidence']:.2f}")
        print(f"Campos extraídos: {len([k for k, v in result_html['data'].items() if v is not None])}")
        
        assert result_html['success'] or result_html['overall_confidence'] > 0, "Deveria extrair algo do HTML"
        
        print("✅ Extração de HTML funcionando")
        
        # Teste 5: Parse de strings de preço e área
        print("\n📋 Teste 5: Parse de strings")
        
        # Teste de preço
        price_tests = [
            ("850.000,00", 850000.0),
            ("R$ 1.200.000", 1200000.0),
            ("450000", 450000.0),
            ("850 mil", None)  # Não implementado nesta função
        ]
        
        for price_str, expected in price_tests:
            result = extractor._parse_price_string(price_str)
            print(f"Preço '{price_str}' → {result} (esperado: {expected})")
            if expected is not None:
                assert result == expected, f"Esperado {expected}, obtido {result}"
        
        # Teste de área
        area_tests = [
            ("120", 120.0),
            ("120,5", 120.5),
            ("95.5", 95.5)
        ]
        
        for area_str, expected in area_tests:
            result = extractor._parse_area_string(area_str)
            print(f"Área '{area_str}' → {result} (esperado: {expected})")
            assert result == expected, f"Esperado {expected}, obtido {result}"
        
        print("✅ Parse de strings funcionando")
        
        # Teste 6: Validação de dados
        print("\n📋 Teste 6: Validação de dados")
        
        # Dados válidos
        valid_data = {
            'price': 850000,
            'area': 120,
            'bedrooms': 3,
            'bathrooms': 2
        }
        
        validation = extractor._validate_extracted_data(valid_data)
        print(f"Dados válidos - Válido: {validation['is_valid']}")
        assert validation['is_valid'], "Dados válidos deveriam passar na validação"
        
        # Dados inválidos
        invalid_data = {
            'price': 500,  # Muito baixo
            'area': 5000,  # Muito alto
            'bedrooms': 25  # Muito alto
        }
        
        validation_invalid = extractor._validate_extracted_data(invalid_data)
        print(f"Dados inválidos - Válido: {validation_invalid['is_valid']}")
        print(f"Erros: {len(validation_invalid['errors'])}")
        assert not validation_invalid['is_valid'], "Dados inválidos deveriam falhar na validação"
        
        print("✅ Validação de dados funcionando")
        
        # Teste 7: Cálculo de confiança
        print("\n📋 Teste 7: Cálculo de confiança")
        
        test_result = {
            'data': {'price': 850000, 'area': 120, 'bedrooms': 3},
            'confidence_scores': {'price': 0.9, 'area': 0.8, 'bedrooms': 0.7},
            'sources': ['structured']
        }
        
        confidence = extractor._calculate_overall_confidence(test_result)
        print(f"Confiança calculada: {confidence:.3f}")
        assert 0.0 <= confidence <= 1.0, "Confiança deve estar entre 0 e 1"
        assert confidence > 0.5, "Confiança deveria ser alta para dados bons"
        
        print("✅ Cálculo de confiança funcionando")
        
        # Teste 8: Geração de chave de cache
        print("\n📋 Teste 8: Geração de chave de cache")
        
        cache_key = extractor._generate_cache_key(
            structured_data={'test': 'data'},
            html_content="<div>test</div>",
            url="https://test.com"
        )
        
        print(f"Chave de cache gerada: {cache_key}")
        assert cache_key is not None, "Deveria gerar chave de cache"
        assert cache_key.startswith("smart_extract:"), "Chave deveria ter prefixo correto"
        
        print("✅ Geração de chave de cache funcionando")
        
        # Teste 9: Limpeza de valores
        print("\n📋 Teste 9: Limpeza de valores")
        
        # Teste de limpeza
        test_values = [
            ('price', '850.000,00', 850000.0),
            ('area', '120,5', 120.5),
            ('bedrooms', '3', 3),
            ('address', '  Rua das Flores  ', 'Rua das Flores')
        ]
        
        for field, value, expected in test_values:
            cleaned = extractor._clean_field_value(field, value)
            print(f"Limpar '{field}': '{value}' → {cleaned} (esperado: {expected})")
            assert cleaned == expected, f"Esperado {expected}, obtido {cleaned}"
        
        print("✅ Limpeza de valores funcionando")
        
        # Teste 10: Estatísticas
        print("\n📋 Teste 10: Estatísticas")
        
        stats = extractor.get_statistics()
        print(f"Estatísticas: {stats}")
        
        expected_keys = [
            'total_extractions', 'structured_success', 'ocr_fallback_used',
            'ocr_fallback_success', 'cache_hits', 'validation_failures'
        ]
        
        for key in expected_keys:
            assert key in stats, f"Estatística '{key}' deveria estar presente"
        
        assert stats['total_extractions'] >= 2, "Deveria ter registrado as extrações de teste"
        
        print("✅ Estatísticas funcionando")
        
        # Teste 11: Fechamento de serviços
        print("\n📋 Teste 11: Fechamento de serviços")
        await extractor.close()
        print("✅ Serviços fechados sem erros")
        
        # Resumo final
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Smart Data Extractor está funcionando corretamente")
        print("✅ Todas as funcionalidades básicas operacionais")
        print("✅ Fallbacks funcionando sem dependências externas")
        print("✅ Sistema pronto para uso")
        
        # Informações sobre serviços
        print(f"\n💡 Serviços disponíveis:")
        print(f"   - OCR Service: {'✅' if extractor.use_ocr_fallback else '❌'}")
        print(f"   - Cache Service: {'✅' if extractor.use_cache else '❌'}")
        print(f"   - Database Service: {'✅' if extractor.db_service else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    success = await test_smart_data_extractor()
    
    if success:
        print("\n🎯 Status: SUCESSO - Smart Data Extractor validado e funcional")
        sys.exit(0)
    else:
        print("\n💥 Status: FALHA - Problemas encontrados no Smart Data Extractor")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
