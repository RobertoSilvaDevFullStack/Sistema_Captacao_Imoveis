#!/usr/bin/env python3
"""
Teste rápido do backend para identificar erros
"""

import sys
import traceback

try:
    print("🔍 Testando imports...")
    
    # Teste 1: Imports básicos
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    import asyncio
    import time
    from datetime import datetime
    import threading
    import json
    import logging
    print("✅ Imports básicos OK")
    
    # Teste 2: Carregar dados JSON
    with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Dados JSON carregados: {len(data)} propriedades")
    
    # Teste 3: Verificar primeira propriedade
    if data:
        prop = data[0]
        print(f"✅ Primeira propriedade: {prop.get('neighborhood', 'N/A')} - R$ {prop.get('price', 0)}")
    
    # Teste 4: Imports dos scrapers (opcional)
    try:
        from backend.scrapers.vivareal_scraper import VivaRealScraper
        print("✅ Scraper imports OK")
        SCRAPERS_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Scrapers não disponíveis: {e}")
        SCRAPERS_AVAILABLE = False
    
    print("\n🎉 Todos os testes passaram! Backend deve funcionar.")
    
except Exception as e:
    print(f"❌ ERRO encontrado:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    print("\nTraceback completo:")
    traceback.print_exc()
    sys.exit(1)
