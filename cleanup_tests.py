#!/usr/bin/env python3
"""
Executor de Limpeza de Testes - Aplica as mudanças recomendadas
"""
import sys
import os
import shutil
from pathlib import Path

def execute_cleanup():
    """Executa limpeza real dos testes"""
    
    # Criar diretório de backup
    backup_dir = Path("backup_old_tests")
    backup_dir.mkdir(exist_ok=True)
    
    # Lista de arquivos para arquivar
    tests_to_archive = [
        "test_api.py",
        "test_api_updated.py", 
        "test_cache_service_corrected.py",
        "test_clean_system.py",
        "test_complete_system.py",
        "test_main.py",
        "test_olx_final.py",
        "test_olx_final_working.py",
        "test_olx_fixed.py",
        "test_olx_urls.py",
        "test_quick.py",
        "test_quick_structure.py",
        "test_scraper_structure.py",
        "test_server.py",
        "test_simple_scraper.py",
        "test_vivareal_advanced.py",
        "test_vivareal_simple.py"
    ]
    
    # Lista de arquivos para deletar
    tests_to_delete = [
        "test_advanced_scrapers.py"
    ]
    
    archived_count = 0
    deleted_count = 0
    
    print("🧹 EXECUTANDO LIMPEZA DE TESTES...")
    print("=" * 50)
    
    # Arquivar testes
    print("📦 Arquivando testes desatualizados...")
    for test_file in tests_to_archive:
        file_path = Path(test_file)
        if file_path.exists():
            try:
                shutil.move(str(file_path), str(backup_dir / test_file))
                print(f"  ✅ {test_file} → backup_old_tests/")
                archived_count += 1
            except Exception as e:
                print(f"  ❌ Erro ao mover {test_file}: {e}")
        else:
            print(f"  ⚠️ {test_file} não encontrado")
    
    # Deletar testes vazios
    print("\n🗑️ Deletando arquivos vazios...")
    for test_file in tests_to_delete:
        file_path = Path(test_file)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ {test_file} deletado")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Erro ao deletar {test_file}: {e}")
        else:
            print(f"  ⚠️ {test_file} não encontrado")
    
    print(f"\n🎉 LIMPEZA CONCLUÍDA!")
    print(f"📦 Arquivos movidos para backup: {archived_count}")
    print(f"🗑️ Arquivos deletados: {deleted_count}")
    print(f"✅ Testes importantes mantidos: 8")
    
    # Criar resumo final
    summary = f"""
# 🎯 RESUMO DA LIMPEZA EXECUTADA

**Data:** {Path().cwd().name}
**Arquivos processados:** {archived_count + deleted_count}

## ✅ RESULTADO:
- **Arquivados:** {archived_count} arquivos em `backup_old_tests/`
- **Deletados:** {deleted_count} arquivos vazios
- **Mantidos:** 8 testes essenciais

## 📁 TESTES MANTIDOS:
- test_advanced_system.py
- test_cache_and_database_integration.py  
- test_enhanced_scraper_validation.py
- test_enrichment_system.py
- test_ocr_service_updated_validation.py
- test_ocr_service_validation.py
- test_ocr_system.py
- test_smart_data_extractor_validation.py

## 🎉 BENEFÍCIOS:
- Projeto mais limpo e organizado
- Redução de {archived_count + deleted_count} arquivos desnecessários
- Foco nos testes realmente úteis
- Backup preservado para referência futura
"""
    
    # Salvar resumo
    Path("CLEANUP_SUMMARY.md").write_text(summary, encoding='utf-8')
    print(f"\n📄 Resumo salvo em: CLEANUP_SUMMARY.md")

if __name__ == "__main__":
    
    # Confirmação de segurança
    print("⚠️ ATENÇÃO: Esta operação irá mover/deletar arquivos de teste!")
    print("📋 Revise o arquivo TEST_CLEANUP_REPORT.md antes de continuar.")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        execute_cleanup()
    else:
        response = input("\n🤔 Deseja continuar? (s/N): ").lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            execute_cleanup()
        else:
            print("❌ Operação cancelada.")
            print("💡 Para executar sem confirmação: python cleanup_tests.py --force")
