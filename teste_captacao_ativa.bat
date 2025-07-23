@echo off
echo 🏠 TESTE IMEDIATO - SISTEMA DE CAPTACAO ATIVA
echo ===============================================
echo.

echo 📊 SITUACAO ATUAL IDENTIFICADA:
echo    ✅ 380 propriedades (Sao Paulo - VivaReal)
echo    ✅ 3 scrapers desenvolvidos
echo    ✅ 10+ cidades configuradas
echo    ❌ Captacao continua INATIVA
echo.

echo 🎯 TESTANDO SCRAPER OLX PARA RIO DE JANEIRO...
echo.

cd /d "C:\Users\rober\OneDrive\Desktop\Sistema_Captacao_Imoveis"

python -c "
import sys
import os
from pathlib import Path
import time

# Adicionar backend ao path
backend_path = Path.cwd() / 'backend'
sys.path.insert(0, str(backend_path))

print('🔧 Verificando infraestrutura...')

try:
    from config.location_config import LocationConfig
    config = LocationConfig()
    locations = config.list_locations()
    print(f'✅ LocationConfig: {len(locations)} cidades configuradas')
    
    # Testar Rio de Janeiro
    if 'rio_de_janeiro' in locations:
        print('✅ Rio de Janeiro: Configurado')
        
        # Testar OLX Scraper
        from scrapers.olx_scraper import OLXScraper
        print('✅ OLX Scraper: Importado com sucesso')
        
        # Inicializar scraper
        scraper = OLXScraper(location='rio_de_janeiro', property_type='apartamentos')
        print('✅ Scraper inicializado para Rio de Janeiro')
        
        print('🔄 Iniciando captacao de teste (max 3 propriedades)...')
        start_time = time.time()
        
        # Captacao com limite baixo
        try:
            properties = scraper.scrape_properties(max_pages=1)
            duration = time.time() - start_time
            
            if properties and len(properties) > 0:
                print(f'✅ SUCESSO! {len(properties)} propriedades em {duration:.1f}s')
                
                # Mostrar exemplos
                for i, prop in enumerate(properties[:2]):
                    neighborhood = prop.get('neighborhood', 'N/A')
                    price = prop.get('price', 'N/A')
                    print(f'   {i+1}. {neighborhood} - R$ {price}')
                
                print('🎯 SISTEMA FUNCIONANDO - CAPTACAO ATIVA CONFIRMADA!')
                
                # Salvar teste
                import json
                filename = f'teste_rio_{int(time.time())}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(properties[:3], f, indent=2, ensure_ascii=False)
                print(f'💾 Dados salvos: {filename}')
                
            else:
                print('⚠️ Nenhuma propriedade encontrada')
                
        except Exception as e:
            print(f'❌ Erro na captacao: {e}')
            
        finally:
            # Limpar
            if hasattr(scraper, 'driver') and scraper.driver:
                scraper.driver.quit()
                print('✅ Driver fechado')
    else:
        print('❌ Rio de Janeiro nao configurado')
        print(f'Cidades disponiveis: {locations[:5]}')
        
except ImportError as e:
    print(f'❌ Erro de import: {e}')
    print('💡 Verificar dependencias: selenium, webdriver-manager')
    
except Exception as e:
    print(f'❌ Erro geral: {e}')

print('\\n🎯 CONCLUSAO:')
print('Se apareceu SUCESSO acima, o sistema esta pronto!')
print('Pode executar captacao em multiplas cidades.')
"

echo.
echo ================================================
echo 🎯 TESTE CONCLUIDO - Verifique resultados acima
echo ================================================
pause
