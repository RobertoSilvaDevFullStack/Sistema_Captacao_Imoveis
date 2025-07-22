#!/usr/bin/env python3
"""
Teste Simples do Sistema de Enriquecimento de Dados com APIs Oficiais
Demonstra as principais funcionalidades do sistema de APIs
"""

import asyncio
import json
import logging
import sys
import os

# Adicionar o diretório raiz ao Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.data_enrichment_service import DataEnrichmentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_property_enrichment():
    """Testa o enriquecimento de uma propriedade"""
    
    print("🏠 Teste do Sistema de Enriquecimento de Dados")
    print("=" * 50)
    
    # Dados de exemplo de uma propriedade
    sample_property = {
        'id': 'test_001',
        'title': 'Apartamento 3 quartos em Copacabana',
        'address': 'Rua Barata Ribeiro, 500, Copacabana',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'neighborhood': 'Copacabana',
        'price': 1200000,
        'area': 120,
        'bedrooms': 3,
        'bathrooms': 2,
        'property_type': 'APARTMENT',
        'business_type': 'SALE'
    }
    
    print("📋 Dados originais da propriedade:")
    print(json.dumps(sample_property, indent=2, ensure_ascii=False))
    
    try:
        # Inicializar serviço de enriquecimento
        print("\n🔧 Inicializando serviço de enriquecimento...")
        enrichment_service = DataEnrichmentService()
        
        # Executar enriquecimento
        print("\n🔍 Enriquecendo propriedade com APIs oficiais...")
        enriched_data = await enrichment_service.enrich_property(sample_property)
        
        # Converter para dict para visualização
        if hasattr(enriched_data, '__dict__'):
            enriched_dict = enriched_data.__dict__
        else:
            enriched_dict = enriched_data
        
        print("\n✅ Dados enriquecidos:")
        print(json.dumps(enriched_dict, indent=2, ensure_ascii=False, default=str))
        
        # Análise de enriquecimento
        print("\n📊 Análise do enriquecimento:")
        original_fields = len(sample_property.keys())
        
        def count_nested_fields(data, prefix=""):
            count = 0
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        count += count_nested_fields(value, f"{prefix}.{key}" if prefix else key)
                    else:
                        count += 1
            return count
        
        enriched_fields = count_nested_fields(enriched_dict)
        enhancement_factor = enriched_fields / original_fields if original_fields > 0 else 0
        
        print(f"Campos originais: {original_fields}")
        print(f"Campos enriquecidos: {enriched_fields}")
        print(f"Fator de enriquecimento: {enhancement_factor:.2f}x")
        
        # Verificar qualidade dos dados
        print("\n🎯 Qualidade dos dados:")
        
        # Acessar atributos do dataclass PropertyEnrichment
        location_data = getattr(enriched_data, 'location', None)
        if location_data and hasattr(location_data, 'latitude') and hasattr(location_data, 'longitude'):
            if location_data.latitude and location_data.longitude:
                print("✅ Coordenadas geográficas obtidas")
            else:
                print("❌ Coordenadas geográficas não obtidas")
        else:
            print("❌ Dados de localização não obtidos")
        
        municipal_data = getattr(enriched_data, 'municipal_data', None)
        if municipal_data:
            print("✅ Dados municipais obtidos")
        else:
            print("❌ Dados municipais não obtidos")
        
        market_data = getattr(enriched_data, 'market_data', None)
        if market_data:
            print("✅ Dados de mercado obtidos")
        else:
            print("❌ Dados de mercado não obtidos")
        
        registry_data = getattr(enriched_data, 'registry_data', None)
        if registry_data:
            print("✅ Dados de cartório obtidos")
        else:
            print("❌ Dados de cartório não obtidos")
        
        google_data = getattr(enriched_data, 'google_data', None)
        if google_data:
            print("✅ Dados do Google Maps obtidos")
        else:
            print("❌ Dados do Google Maps não obtidos")
        
        confidence_score = getattr(enriched_data, 'confidence_score', 0)
        print(f"\n🎲 Score de confiança: {confidence_score:.2f}")
        
        if confidence_score > 0.8:
            print("🟢 Alta confiança nos dados")
        elif confidence_score > 0.6:
            print("🟡 Confiança média nos dados")
        else:
            print("🔴 Baixa confiança nos dados")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_multiple_properties():
    """Testa o enriquecimento de múltiplas propriedades"""
    
    print("\n" + "=" * 50)
    print("🏘️ Teste de Múltiplas Propriedades")
    print("=" * 50)
    
    # Lista de propriedades de exemplo
    properties = [
        {
            'id': 'test_001',
            'address': 'Av. Copacabana, 1000, Copacabana',
            'city': 'Rio de Janeiro',
            'state': 'RJ',
            'price': 1200000,
            'area': 120,
            'bedrooms': 3
        },
        {
            'id': 'test_002',
            'address': 'Rua Augusta, 500, Vila Madalena',
            'city': 'São Paulo',
            'state': 'SP',
            'price': 800000,
            'area': 80,
            'bedrooms': 2
        },
        {
            'id': 'test_003',
            'address': 'Av. Boa Viagem, 200, Boa Viagem',
            'city': 'Recife',
            'state': 'PE',
            'price': 600000,
            'area': 100,
            'bedrooms': 3
        }
    ]
    
    enrichment_service = DataEnrichmentService()
    
    for i, property_data in enumerate(properties, 1):
        print(f"\n🔍 Enriquecendo propriedade {i}/{len(properties)}")
        print(f"📍 {property_data['address']}")
        
        try:
            enriched_data = await enrichment_service.enrich_property(property_data)
            
            # Extrair informações principais
            location = getattr(enriched_data, 'location', {})
            confidence = getattr(enriched_data, 'confidence_score', 0)
            
            if hasattr(location, '__dict__'):
                location_dict = location.__dict__
            else:
                location_dict = location if isinstance(location, dict) else {}
            
            print(f"✅ Sucesso - Confiança: {confidence:.2f}")
            
            if location_dict.get('latitude') and location_dict.get('longitude'):
                print(f"📍 Coordenadas: {location_dict['latitude']:.6f}, {location_dict['longitude']:.6f}")
            
            # Pequeno delay
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print("\n✅ Teste de múltiplas propriedades concluído!")

async def main():
    """Função principal"""
    
    try:
        # Teste básico
        await test_property_enrichment()
        
        # Teste de múltiplas propriedades
        await test_multiple_properties()
        
        print("\n🎉 Todos os testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"\n💥 Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Iniciando testes do sistema de enriquecimento...")
    asyncio.run(main())
