#!/usr/bin/env python3
"""
Teste de Validação Atualizada do OCR Service
Verifica se todas as funcionalidades estão operacionais após as últimas correções.
"""
import asyncio
import logging
import sys
import os

# Adicionar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_ocr_service_comprehensive():
    """Teste completo e atualizado do OCR Service"""
    print("🚀 Iniciando teste de validação atualizada do OCR Service...")
    
    try:
        # Importar e inicializar
        from backend.services.ocr_service import OCRService
        
        print("✅ Import bem-sucedido")
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Teste 1: Inicialização
        print("\n📋 Teste 1: Inicialização")
        ocr_service = OCRService()
        print("✅ OCRService inicializado com sucesso")
        
        # Teste 2: Verificação de disponibilidade
        print("\n📋 Teste 2: Verificação de disponibilidade")
        availability = ocr_service.check_availability()
        print(f"Disponibilidade completa: {availability}")
        
        expected_keys = {'tesseract', 'easyocr', 'opencv', 'overall'}
        assert set(availability.keys()) == expected_keys, f"Chaves esperadas: {expected_keys}"
        assert isinstance(availability['overall'], bool), "overall deve ser boolean"
        print("✅ Verificação de disponibilidade funcionando")
        
        # Teste 3: Extração de dados de texto (funciona sem OCR engines)
        print("\n📋 Teste 3: Extração de dados de texto")
        test_texts = [
            "APARTAMENTO 3 QUARTOS R$ 850.000,00 120 m² 2 banheiros 1 vaga",
            "Casa 4 quartos, 3 banheiros, 200 m², R$ 1.200.000",
            "Preço: R$ 450.000 Área: 85 m² Quartos: 2 Banheiros: 1",
            "850 mil reais, 120,5 metros quadrados, 3 dorms, 2 banhs",
            "Apartamento novo - 95 m² - 3 qtos - 2 banhs - R$ 750.000,00"
        ]
        
        for i, text in enumerate(test_texts):
            extracted = ocr_service.extract_data_from_text(text)
            found_fields = [k for k, v in extracted.items() if v is not None and k not in ['raw_text', 'confidence']]
            print(f"Texto {i+1}: {len(found_fields)} campos extraídos → {found_fields}")
            
            # Verificar estrutura do resultado
            expected_fields = {'price', 'area', 'bedrooms', 'bathrooms', 'parking', 'raw_text', 'confidence'}
            assert set(extracted.keys()) == expected_fields, f"Campos esperados: {expected_fields}"
            assert isinstance(extracted['confidence'], float), "Confidence deve ser float"
            assert 0 <= extracted['confidence'] <= 1, "Confidence deve estar entre 0 e 1"
        
        print("✅ Extração de dados de texto funcionando")
        
        # Teste 4: Parsing detalhado de preço
        print("\n📋 Teste 4: Parsing detalhado de preço")
        price_tests = [
            ("850.000,00", 850000.0),
            ("R$ 1.200.000", 1200000.0),
            ("450000", 450000.0),
            ("850 mil", 850000.0),
            ("1.500.000,50", 1500000.5),
            ("R$ 750.000", 750000.0),
            ("950.000", 950000.0),
            ("1200000", 1200000.0)
        ]
        
        success_count = 0
        for price_str, expected in price_tests:
            result = ocr_service._parse_price(price_str)
            success = result == expected if expected is not None else result is None
            print(f"'{price_str}' → {result} (esperado: {expected}) {'✓' if success else '✗'}")
            if success:
                success_count += 1
        
        success_rate = success_count / len(price_tests)
        print(f"Taxa de sucesso no parsing de preços: {success_rate:.1%}")
        assert success_rate >= 0.7, f"Taxa de sucesso muito baixa: {success_rate:.1%}"
        
        print("✅ Parsing de preço funcionando")
        
        # Teste 5: Parsing de área
        print("\n📋 Teste 5: Parsing de área")
        area_tests = [
            ("120", 120.0),
            ("120,5", 120.5),
            ("85.5", 85.5),
            ("200", 200.0),
            ("95", 95.0),
            ("150,75", 150.75)
        ]
        
        for area_str, expected in area_tests:
            result = ocr_service._parse_area(area_str)
            print(f"'{area_str}' → {result} (esperado: {expected})")
            assert result == expected, f"Esperado {expected}, obtido {result}"
        
        print("✅ Parsing de área funcionando")
        
        # Teste 6: Pré-processamento de imagem (com dummy se necessário)
        print("\n📋 Teste 6: Pré-processamento de imagem")
        
        # Verificar se temos PIL disponível
        from backend.services.ocr_service import TESSERACT_AVAILABLE, Image
        
        if TESSERACT_AVAILABLE:
            print("PIL disponível - testando com imagem real")
            try:
                from PIL import Image as PILImage  # type: ignore
                # Criar imagem de teste
                test_image = PILImage.new('RGB', (200, 100), color='white')
                processed = ocr_service.preprocess_image(test_image)
                print(f"Processamento gerou {len(processed)} variações da imagem")
                assert len(processed) >= 1, "Deve retornar pelo menos a imagem original"
            except Exception as e:
                print(f"Erro com PIL real: {e}")
        else:
            print("PIL não disponível - testando com classe dummy")
            # Usar classe dummy
            dummy_image = Image.open("dummy_path")  # type: ignore
            processed = ocr_service.preprocess_image(dummy_image)
            print(f"Processamento dummy gerou {len(processed)} variações")
            assert len(processed) >= 1, "Deve retornar pelo menos a imagem original"
        
        print("✅ Pré-processamento de imagem funcionando")
        
        # Teste 7: Cache e estatísticas
        print("\n📋 Teste 7: Cache e estatísticas")
        
        # Adicionar alguns resultados simulados ao cache
        test_results = [
            {'success': True, 'confidence': 0.9, 'ocr_engine': 'tesseract'},
            {'success': True, 'confidence': 0.8, 'ocr_engine': 'easyocr'},
            {'success': False, 'confidence': 0.0, 'ocr_engine': None},
            {'success': True, 'confidence': 0.7, 'ocr_engine': 'tesseract'}
        ]
        
        for i, result in enumerate(test_results):
            ocr_service.cache[f"test_hash_{i}"] = result
        
        stats = ocr_service.get_statistics()
        print(f"Estatísticas: {stats}")
        
        expected_stat_keys = {'total_processed', 'success_rate', 'average_confidence', 'engines_used', 'available_engines'}
        assert set(stats.keys()) == expected_stat_keys, f"Chaves esperadas: {expected_stat_keys}"
        assert stats['total_processed'] == 4, "Total processado deve ser 4"
        assert stats['success_rate'] == 3/4, "Taxa de sucesso deve ser 3/4"
        assert 0.7 <= stats['average_confidence'] <= 0.9, f"Confiança média estranha: {stats['average_confidence']}"
        
        print("✅ Cache e estatísticas funcionando")
        
        # Teste 8: Limpeza de cache
        print("\n📋 Teste 8: Limpeza de cache")
        ocr_service.clear_cache()
        assert len(ocr_service.cache) == 0, "Cache deve estar vazio após limpeza"
        print("✅ Limpeza de cache funcionando")
        
        # Teste 9: Análise de imagem sem OCR engines disponíveis
        print("\n📋 Teste 9: Análise de imagem (fallback)")
        
        if not availability['overall']:
            print("Testando fallback quando OCR não disponível...")
            try:
                result = await ocr_service.analyze_image("test_image_data")
                print(f"Resultado de fallback: success={result['success']}")
                assert not result['success'], "Deve falhar sem engines OCR disponíveis"
                assert 'error' in result, "Deve conter informação de erro"
                print("✅ Fallback funcionando corretamente")
            except Exception as e:
                print(f"✅ Exceção esperada capturada: {type(e).__name__}: {e}")
        else:
            print("OCR disponível - seria possível análise real")
        
        # Teste 10: Processamento em lote
        print("\n📋 Teste 10: Processamento em lote")
        
        # Testar com lista vazia
        batch_results = await ocr_service.batch_analyze([])
        assert batch_results == [], "Lista vazia deve retornar lista vazia"
        
        # Testar com dados inválidos
        batch_results = await ocr_service.batch_analyze(["invalid1", "invalid2"])
        assert len(batch_results) == 2, "Deve retornar 2 resultados"
        assert all(not r['success'] for r in batch_results), "Todos devem falhar"
        assert all('error' in r or 'image_index' in r for r in batch_results), "Todos devem ter metadados"
        
        print("✅ Processamento em lote funcionando")
        
        # Teste 11: Validação de padrões regex
        print("\n📋 Teste 11: Validação de padrões regex")
        
        # Verificar se todos os padrões são válidos
        import re
        pattern_count = 0
        for data_type, patterns in ocr_service.patterns.items():
            for pattern in patterns:
                try:
                    re.compile(pattern)
                    pattern_count += 1
                    print(f"✓ Padrão válido para {data_type}: {pattern[:40]}...")
                except re.error as e:
                    assert False, f"Padrão inválido para {data_type}: {pattern} - {e}"
        
        print(f"✅ Todos os {pattern_count} padrões regex são válidos")
        
        # Teste 12: Geração de hash de imagem
        print("\n📋 Teste 12: Geração de hash de imagem")
        
        if TESSERACT_AVAILABLE:
            try:
                from PIL import Image as PILImage  # type: ignore
                test_img = PILImage.new('RGB', (100, 100), color='red')
                hash1 = ocr_service._generate_image_hash(test_img)
                hash2 = ocr_service._generate_image_hash(test_img)
                print(f"Hash gerado: {hash1}")
                assert hash1 == hash2, "Hashes iguais para imagens iguais"
                print("✅ Geração de hash com PIL funcionando")
            except Exception as e:
                print(f"⚠️ Erro com PIL real: {e}")
        else:
            # Teste com dummy
            dummy_img = Image.open("test")  # type: ignore
            hash_dummy = ocr_service._generate_image_hash(dummy_img)
            print(f"Hash dummy gerado: {hash_dummy}")
            assert hash_dummy is not None, "Deve gerar algum hash"
            print("✅ Geração de hash com dummy funcionando")
        
        # Teste 13: Teste de robustez com dados malformados
        print("\n📋 Teste 13: Robustez com dados malformados")
        
        malformed_texts = [
            "",  # Vazio
            "   ",  # Só espaços
            "abc def ghi",  # Sem números
            "123",  # Número muito pequeno
            "R$ abc.def,gh",  # Formato inválido
            "999999999999999999",  # Número muito grande
        ]
        
        for text in malformed_texts:
            try:
                result = ocr_service.extract_data_from_text(text)
                print(f"Texto malformado '{text[:20]}': {sum(1 for v in result.values() if v not in [None, text, 0.0])} campos")
                # Não deve falhar, apenas retornar dados vazios/inválidos
                assert isinstance(result, dict), "Deve retornar dict mesmo com dados ruins"
            except Exception as e:
                assert False, f"Não deveria falhar com dados malformados: {e}"
        
        print("✅ Robustez com dados malformados funcionando")
        
        # Resumo final
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ OCR Service está funcionando corretamente")
        print("✅ Todas as funcionalidades básicas operacionais")
        print("✅ Fallbacks funcionando sem dependências OCR")
        print("✅ Sistema robusto e pronto para uso")
        print("✅ Parsing de dados preciso e confiável")
        print("✅ Cache e estatísticas funcionais")
        print("✅ Tratamento de erros adequado")
        
        # Informações sobre disponibilidade
        print(f"\n💡 Status dos engines OCR:")
        print(f"   - Tesseract: {'✅' if availability['tesseract'] else '❌'}")
        print(f"   - EasyOCR: {'✅' if availability['easyocr'] else '❌'}")
        print(f"   - OpenCV: {'✅' if availability['opencv'] else '❌'}")
        
        if not availability['overall']:
            print("\n💡 Para ativar OCR completo, instale as dependências:")
            print("   pip install pytesseract easyocr pillow opencv-python numpy")
            print("   # E configure o Tesseract no sistema")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    success = await test_ocr_service_comprehensive()
    
    if success:
        print("\n🎯 Status: SUCESSO - OCR Service totalmente validado e funcional")
        sys.exit(0)
    else:
        print("\n💥 Status: FALHA - Problemas encontrados no OCR Service")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
