#!/usr/bin/env python3
"""
Teste simples de conectividade com Selenium Grid Docker
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_selenium_grid():
    """Testa conectividade básica com Selenium Grid"""
    
    print("🧪 Testando Selenium Grid Docker...")
    
    try:
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Conectar ao Selenium Grid
        print("🔗 Conectando ao Selenium Grid em localhost:4444...")
        
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=chrome_options
        )
        
        print("✅ Conectado com sucesso ao Selenium Grid!")
        
        # Teste básico - acessar Google
        print("🌐 Testando navegação básica...")
        driver.get('https://www.google.com')
        
        # Verificar se carregou
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, 'q')))
        
        print(f"📄 Título da página: {driver.title}")
        print(f"🔍 Campo de busca encontrado: {search_box is not None}")
        
        # Teste com um site de imóveis (VivaReal)
        print("\n🏠 Testando acesso ao VivaReal...")
        driver.get('https://www.vivareal.com.br')
        
        time.sleep(3)  # Aguardar carregamento
        
        print(f"📄 Título VivaReal: {driver.title}")
        print(f"🌐 URL atual: {driver.current_url}")
        
        # Verificar se existem elementos de imóveis
        try:
            # Tentar encontrar elementos comuns do VivaReal
            elements = driver.find_elements(By.CLASS_NAME, "property-card")
            if not elements:
                elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='property']")
            if not elements:
                elements = driver.find_elements(By.CLASS_NAME, "listing-item")
                
            print(f"🏠 Elementos de imóveis encontrados: {len(elements)}")
            
        except Exception as e:
            print(f"⚠️  Erro ao buscar elementos: {e}")
        
        # Fechar driver
        driver.quit()
        
        print("\n✅ Teste concluído com sucesso!")
        print("🐳 Selenium Grid Docker está funcionando corretamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_containers_status():
    """Verifica status dos containers"""
    import subprocess
    
    print("\n🔍 Verificando status dos containers...")
    
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose-simple.yml', 'ps'],
            capture_output=True,
            text=True,
            cwd=r'C:\Users\rober\OneDrive\Desktop\Sistema_Captacao_Imoveis'
        )
        
        print("📊 Status dos containers:")
        print(result.stdout)
        
        return "Up" in result.stdout
        
    except Exception as e:
        print(f"❌ Erro ao verificar containers: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do ambiente Docker...")
    
    # Verificar containers
    containers_ok = test_containers_status()
    
    if containers_ok:
        print("\n✅ Containers estão rodando!")
        
        # Testar Selenium Grid
        selenium_ok = test_selenium_grid()
        
        if selenium_ok:
            print("\n🎉 SUCESSO: Ambiente Docker está pronto para os scrapers!")
            print("\n📋 Próximos passos:")
            print("   1. ✅ Docker Compose funcionando")
            print("   2. ✅ Selenium Grid operacional") 
            print("   3. ✅ Chrome remoto conectando")
            print("   4. 🔄 Scrapers podem usar: http://localhost:4444/wd/hub")
        else:
            print("\n❌ Problema com Selenium Grid")
    else:
        print("\n❌ Containers não estão rodando corretamente")
    
    print(f"\n⏰ Teste concluído em: {time.strftime('%H:%M:%S')}")
