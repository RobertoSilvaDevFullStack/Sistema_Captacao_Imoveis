#!/usr/bin/env python3
"""
Teste mínimo de conectividade
"""

import requests
import json

def test_selenium_hub():
    """Testa se o Selenium Hub está respondendo"""
    
    print("🔍 Testando Selenium Hub...")
    
    try:
        # Testar endpoint de status
        response = requests.get('http://localhost:4444/status', timeout=10)
        
        if response.status_code == 200:
            print("✅ Selenium Hub está respondendo!")
            
            data = response.json()
            print(f"📊 Status: {data.get('value', {}).get('ready', 'N/A')}")
            
            nodes = data.get('value', {}).get('nodes', [])
            print(f"🖥️  Nós disponíveis: {len(nodes)}")
            
            for i, node in enumerate(nodes):
                print(f"   Node {i+1}: {node.get('status', 'N/A')}")
            
            return True
        else:
            print(f"❌ Hub retornou status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Hub: {e}")
        return False

def test_containers():
    """Verifica containers Docker"""
    
    print("\n🐳 Verificando containers...")
    
    import subprocess
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        if 'selenium-hub' in result.stdout:
            print("✅ Container selenium-hub está rodando")
        else:
            print("❌ Container selenium-hub não encontrado")
            
        if 'chrome-node' in result.stdout:
            print("✅ Container chrome-node está rodando") 
        else:
            print("❌ Container chrome-node não encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar containers: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Teste Rápido - Ambiente Docker\n")
    
    # Teste containers
    test_containers()
    
    # Teste Selenium Hub
    hub_ok = test_selenium_hub()
    
    if hub_ok:
        print("\n🎉 SUCESSO: Ambiente pronto!")
        print("🔗 Selenium Grid: http://localhost:4444")
    else:
        print("\n❌ Problema detectado no ambiente")
        
    print(f"\n⏰ Concluído!")
