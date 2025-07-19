# test_database.py

print("🔄 Testando conexão com banco de dados...")

try:
    import sys
    print(f"Python path: {sys.path}")
    
    from database import engine, Base, SessionLocal
    print("✅ Importação do database.py OK")
    
    # Testa conexão
    print("🔄 Testando conexão...")
    connection = engine.connect()
    print("✅ Conexão com banco OK")
    connection.close()
    
    # Importa modelos
    print("🔄 Importando modelos...")
    from backend.models.property import Property, PropertyPriceHistory, PropertyAnalysis
    print("✅ Modelos importados OK")
    
    # Cria tabelas
    print("🔄 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas OK")
    
    # Verifica tabelas
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📊 Tabelas no banco: {tables}")
    
    print("🎉 Teste concluído com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
