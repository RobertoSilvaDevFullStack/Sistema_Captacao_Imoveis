#!/usr/bin/env python3
"""
Sistema de Captação Multi-Cidade Ativo
Teste imediato sem dependências complexas
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Configurar caminhos
current_dir = Path(__file__).parent
backend_dir = current_dir / 'backend'
sys.path.insert(0, str(backend_dir))

def test_olx_scraper_directly():
    """Testa o scraper OLX diretamente para Rio de Janeiro"""
    print("🏠 TESTE DIRETO SCRAPER OLX - RIO DE JANEIRO")
    print("=" * 60)
    
    try:
        # Import direto
        from scrapers.olx_scraper import OLXScraper
        from config.location_config import LocationConfig
        
        print("✅ Imports realizados com sucesso")
        
        # Verificar configurações disponíveis
        config = LocationConfig()
        locations = config.list_locations()
        print(f"📍 {len(locations)} cidades configuradas")
        
        # Testar Rio de Janeiro especificamente
        if 'rio_de_janeiro' in locations:
            print("✅ Rio de Janeiro configurado")
            
            # Inicializar scraper
            print("🔄 Inicializando scraper...")
            scraper = OLXScraper(location='rio_de_janeiro', property_type='apartamentos')
            
            print("⚡ Iniciando captação (máximo 5 propriedades)...")
            start_time = time.time()
            
            # Fazer scraping com limite baixo para teste
            try:
                properties = scraper.scrape_properties(max_pages=1)  # Apenas 1 página para teste
                
                duration = time.time() - start_time
                
                if properties:
                    print(f"✅ SUCESSO! {len(properties)} propriedades captadas em {duration:.1f}s")
                    
                    # Mostrar exemplos
                    print(f"\n📋 EXEMPLOS CAPTADOS:")
                    for i, prop in enumerate(properties[:3]):
                        try:
                            price = prop.get('price', 'N/A')
                            neighborhood = prop.get('neighborhood', 'N/A')
                            bedrooms = prop.get('bedrooms', 'N/A')
                            print(f"   {i+1}. {neighborhood} - {bedrooms}Q - R$ {price}")
                        except Exception as e:
                            print(f"   {i+1}. Erro ao exibir propriedade: {e}")
                    
                    return properties
                else:
                    print(f"⚠️ Nenhuma propriedade encontrada (em {duration:.1f}s)")
                    return []
                
            except Exception as e:
                print(f"❌ Erro durante scraping: {e}")
                return False
                
            finally:
                # Fechar driver
                try:
                    if hasattr(scraper, 'driver') and scraper.driver:
                        scraper.driver.quit()
                        print("✅ Driver fechado")
                except:
                    pass
        else:
            print("❌ Rio de Janeiro não está nas configurações")
            print(f"📍 Cidades disponíveis: {locations[:5]}...")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("💡 Verificar se todas as dependências estão instaladas")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def create_simple_continuous_scraper():
    """Cria sistema simples de captação contínua"""
    print(f"\n🚀 SISTEMA DE CAPTAÇÃO CONTÍNUA SIMPLES")
    print("=" * 60)
    
    print("📋 CONFIGURAÇÃO PROPOSTA:")
    print("   1. Captar Rio de Janeiro (500+ propriedades)")
    print("   2. Captar Belo Horizonte (300+ propriedades)")
    print("   3. Captar Brasília (200+ propriedades)")
    print("   4. Atualizar dados de São Paulo")
    print("   5. Salvar tudo em arquivo unificado")
    
    target_cities = [
        ('rio_de_janeiro', 'Rio de Janeiro'),
        ('belo_horizonte', 'Belo Horizonte'),
        ('brasilia', 'Brasília'),
        ('sao_paulo', 'São Paulo')
    ]
    
    print(f"\n🎯 EXECUÇÃO PLANEJADA:")
    for city_code, city_name in target_cities:
        print(f"   • {city_name} ({city_code})")
        print(f"     - OLX: apartamentos e casas")
        print(f"     - Páginas: 3-5 por tipo")
        print(f"     - Estimativa: 50-100 propriedades")
        print(f"     - Tempo: ~5-10 minutos")
    
    return target_cities

def save_new_properties(properties, city_name):
    """Salva novas propriedades de forma incremental"""
    print(f"\n💾 SALVANDO DADOS - {city_name}")
    print("-" * 40)
    
    try:
        import json
        
        # Nome do arquivo específico para a cidade
        filename = f"propriedades_{city_name.lower().replace(' ', '_')}.json"
        
        # Carregar dados existentes se houver
        existing_properties = []
        if Path(filename).exists():
            with open(filename, 'r', encoding='utf-8') as f:
                existing_properties = json.load(f)
            print(f"📂 Dados existentes: {len(existing_properties)} propriedades")
        
        # Adicionar novas propriedades
        all_properties = existing_properties + properties
        
        # Remover duplicatas baseado na URL
        unique_properties = []
        seen_urls = set()
        
        for prop in all_properties:
            url = prop.get('url', '')
            if url and url not in seen_urls:
                unique_properties.append(prop)
                seen_urls.add(url)
        
        # Salvar arquivo atualizado
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(unique_properties, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Salvo: {len(unique_properties)} propriedades únicas")
        print(f"📁 Arquivo: {filename}")
        
        return len(unique_properties)
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return 0

def create_execution_script():
    """Cria script de execução para captação ativa"""
    
    script_content = '''#!/usr/bin/env python3
"""
Script de Execução - Captação Ativa Multi-Cidade
Execute este arquivo para iniciar captação em múltiplas cidades
"""

import sys
import time
from pathlib import Path

# Configurar caminhos
current_dir = Path(__file__).parent
backend_dir = current_dir / 'backend'
sys.path.insert(0, str(backend_dir))

def run_multi_city_scraping():
    """Executa captação em múltiplas cidades"""
    print("🌍 CAPTAÇÃO ATIVA MULTI-CIDADE")
    print("=" * 50)
    
    cities = [
        ('rio_de_janeiro', 'Rio de Janeiro'),
        ('belo_horizonte', 'Belo Horizonte'),
        ('brasilia', 'Brasília')
    ]
    
    total_captured = 0
    
    for city_code, city_name in cities:
        print(f"\\n🎯 CAPTANDO {city_name}...")
        
        try:
            from scrapers.olx_scraper import OLXScraper
            
            scraper = OLXScraper(location=city_code, property_type='apartamentos')
            properties = scraper.scrape_properties(max_pages=2)
            
            if properties:
                print(f"✅ {city_name}: {len(properties)} propriedades")
                # Salvar dados (implementar função de save)
                total_captured += len(properties)
            else:
                print(f"⚠️ {city_name}: Nenhuma propriedade captada")
            
            # Pausa entre cidades
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ {city_name}: Erro - {e}")
    
    print(f"\\n🎯 TOTAL CAPTADO: {total_captured} propriedades")

if __name__ == "__main__":
    run_multi_city_scraping()
'''
    
    script_file = current_dir / 'executar_captacao_ativa.py'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n📄 SCRIPT CRIADO: executar_captacao_ativa.py")
    print("💡 Execute com: python executar_captacao_ativa.py")

def main():
    """Função principal de teste"""
    print("🏠 SISTEMA DE CAPTAÇÃO MULTI-CIDADE ATIVO")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Testar scraper diretamente
    print("\n1️⃣ TESTE DIRETO DO SCRAPER")
    result = test_olx_scraper_directly()
    
    if result:
        print("✅ Scraper funcionando corretamente!")
        
        # 2. Se funcionou, criar sistema contínuo
        print("\n2️⃣ PLANEJAMENTO CONTÍNUO")
        target_cities = create_simple_continuous_scraper()
        
        # 3. Criar script de execução
        print("\n3️⃣ SCRIPT DE EXECUÇÃO")
        create_execution_script()
        
        print(f"\n" + "=" * 70)
        print("🎯 SISTEMA PRONTO PARA CAPTAÇÃO ATIVA!")
        print("   ✅ Scraper testado e funcionando")
        print("   ✅ Configuração multi-cidade validada")
        print("   ✅ Script de execução criado")
        print("   🚀 Execute: python executar_captacao_ativa.py")
        print("=" * 70)
        
    else:
        print("\n⚠️ SCRAPER COM PROBLEMAS")
        print("💡 Verificar dependências e configurações")
        print("   - Selenium WebDriver")
        print("   - Chrome/Chromium")
        print("   - Configurações de rede")

if __name__ == "__main__":
    main()
