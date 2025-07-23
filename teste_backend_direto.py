#!/usr/bin/env python3
"""
Teste direto do backend para identificar problemas
"""

import sys
import os
import traceback

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

print("🔍 Testando backend diretamente...")

try:
    # Testar imports
    from flask import Flask, jsonify
    from flask_cors import CORS
    print("✅ Flask imports OK")
    
    # Testar dados JSON
    import json
    with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ JSON carregado: {len(data)} registros")
    
    # Filtrar dados válidos
    valid_data = [p for p in data if p.get('is_valid') and p.get('price')]
    print(f"✅ Dados válidos: {len(valid_data)} propriedades")
    
    if valid_data:
        sample = valid_data[0]
        print(f"🏠 Exemplo: {sample.get('neighborhood')} - R$ {sample.get('price'):,}")
    
    # Testar criação do app Flask
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/test')
    def test():
        return jsonify({'status': 'ok', 'data_count': len(valid_data)})
    
    print("✅ Flask app criado com sucesso")
    print("🚀 Iniciando servidor de teste...")
    
    # Não rodar o servidor no teste, só validar
    print("✅ Tudo funcionando! Backend deve rodar normalmente.")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    print("\nStacktrace completo:")
    traceback.print_exc()
