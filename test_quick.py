#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Teste simples do sistema
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.abspath('.'))

try:
    from backend.main import app
    print("✅ Aplicação Flask importada com sucesso")
    
    # Testar se o app está configurado
    print(f"✅ App configurado: {app.name}")
    print(f"✅ Rotas disponíveis: {[rule.rule for rule in app.url_map.iter_rules()]}")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n--- Teste do ZapImoveisSimple ---")
try:
    from backend.scrapers.zapimoveis_simple import ZapImoveisSimple
    print("✅ ZapImoveisSimple importado com sucesso")
    
    scraper = ZapImoveisSimple()
    print("✅ Scraper instanciado com sucesso")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")
