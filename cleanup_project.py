#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Limpeza do Projeto
Remove arquivos antigos e organiza a estrutura
"""

import os
import shutil
import logging
from pathlib import Path

def setup_logging():
    """Configura logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def create_backup_folder():
    """Cria pasta de backup para arquivos antigos"""
    backup_path = Path("backup_old_files")
    if backup_path.exists():
        shutil.rmtree(backup_path)
    backup_path.mkdir()
    logging.info(f"📁 Pasta de backup criada: {backup_path}")
    return backup_path

def get_files_to_clean():
    """Lista arquivos para limpeza"""
    current_dir = Path(".")
    
    # Padrões de arquivos para mover para backup
    test_patterns = [
        "test_*.py",
        "debug_*.py", 
        "demo_*.py",
        "*_test.py",
        "*_demo.py",
        "*_debug.py"
    ]
    
    # Arquivos específicos para backup
    specific_files = [
        "integration_demo.py",
        "final_integration_demo.py", 
        "simple_data_demo.py",
        "simple_integration_test.py",
        "main_fixed.py",
        "main_backup.py"
    ]
    
    files_to_backup = []
    
    # Buscar por padrões
    for pattern in test_patterns:
        files_to_backup.extend(current_dir.glob(pattern))
    
    # Adicionar arquivos específicos
    for file_name in specific_files:
        file_path = current_dir / file_name
        if file_path.exists():
            files_to_backup.append(file_path)
    
    # Buscar em subdiretórios também
    for pattern in test_patterns:
        files_to_backup.extend(current_dir.glob(f"**/{pattern}"))
    
    return list(set(files_to_backup))  # Remove duplicatas

def get_folders_to_clean():
    """Lista pastas para limpeza"""
    current_dir = Path(".")
    
    folders_to_backup = []
    
    # Pasta backend antiga (mover conteúdo útil primeiro)
    backend_path = current_dir / "backend"
    if backend_path.exists():
        folders_to_backup.append(backend_path)
    
    return folders_to_backup

def move_files_to_backup(files, backup_path):
    """Move arquivos para pasta de backup"""
    logging.info(f"🔄 Movendo {len(files)} arquivos para backup...")
    
    moved_count = 0
    for file_path in files:
        try:
            if file_path.exists():
                # Criar estrutura de diretórios no backup se necessário
                relative_path = file_path.relative_to(".")
                backup_file_path = backup_path / relative_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(file_path), str(backup_file_path))
                logging.info(f"✅ Movido: {file_path}")
                moved_count += 1
        except Exception as e:
            logging.error(f"❌ Erro ao mover {file_path}: {e}")
    
    logging.info(f"📦 {moved_count} arquivos movidos para backup")

def preserve_important_backend_files(backup_path):
    """Preserva arquivos importantes do backend antes de mover"""
    backend_path = Path("backend")
    if not backend_path.exists():
        return
    
    logging.info("💾 Preservando arquivos importantes do backend...")
    
    # Arquivos para preservar na nova estrutura
    important_files = {
        "backend/scrapers/zapimoveis_advanced.py": "src/scrapers/zapimoveis_advanced_backup.py",
        "backend/scrapers/olx_advanced.py": "src/scrapers/olx_advanced_backup.py"
    }
    
    for old_path, new_path in important_files.items():
        old_file = Path(old_path)
        new_file = Path(new_path)
        
        if old_file.exists():
            try:
                new_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(old_file), str(new_file))
                logging.info(f"💾 Preservado: {old_path} -> {new_path}")
            except Exception as e:
                logging.error(f"❌ Erro ao preservar {old_path}: {e}")

def clean_empty_folders():
    """Remove pastas vazias"""
    current_dir = Path(".")
    
    # Buscar pastas vazias
    for folder in current_dir.rglob("*"):
        if folder.is_dir() and not any(folder.iterdir()):
            try:
                folder.rmdir()
                logging.info(f"🗑️ Pasta vazia removida: {folder}")
            except Exception as e:
                logging.warning(f"⚠️ Não foi possível remover pasta vazia {folder}: {e}")

def update_gitignore():
    """Atualiza .gitignore para nova estrutura"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
.venv/
env/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/
scraper_*.log

# Database
*.db
*.sqlite3

# Selenium
*.log
chromedriver
geckodriver

# OS
.DS_Store
Thumbs.db

# Project specific
backup_old_files/
temp/
*.tmp

# Chrome driver cache
.wdm/

# Data files
*.json
!package.json
!requirements*.txt

# Screenshots and debug files
screenshots/
debug_*.html
"""

    gitignore_path = Path(".gitignore")
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    logging.info("📝 .gitignore atualizado")

def create_cleanup_report(backup_path, files_moved, folders_moved):
    """Cria relatório da limpeza"""
    report_content = f"""# Relatório de Limpeza do Projeto

## Resumo
- **Arquivos movidos para backup**: {len(files_moved)}
- **Pastas movidas para backup**: {len(folders_moved)}
- **Data**: {Path(__file__).stat().st_mtime}

## Arquivos Movidos
"""
    
    for file_path in files_moved:
        report_content += f"- {file_path}\n"
    
    report_content += "\n## Pastas Movidas\n"
    for folder_path in folders_moved:
        report_content += f"- {folder_path}\n"
    
    report_content += """
## Nova Estrutura
```
src/                    # Código principal organizado
├── api/               # API Flask
├── scrapers/          # Scrapers organizados
├── models/            # Modelos de dados
├── config/            # Configurações
└── utils/             # Utilitários

frontend/              # Interface React
tests/                 # Testes organizados
docs/                  # Documentação
scripts/               # Scripts utilitários
backup_old_files/      # Arquivos antigos (backup)
```

## Próximos Passos
1. Revisar backup_old_files/ se necessário
2. Testar nova estrutura
3. Remover backup_old_files/ quando confirmar que está tudo ok
"""
    
    report_path = backup_path / "cleanup_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    logging.info(f"📊 Relatório criado: {report_path}")

def main():
    """Função principal de limpeza"""
    setup_logging()
    
    logging.info("🧹 Iniciando limpeza do projeto...")
    
    # Criar backup
    backup_path = create_backup_folder()
    
    # Preservar arquivos importantes
    preserve_important_backend_files(backup_path)
    
    # Obter arquivos e pastas para limpeza
    files_to_backup = get_files_to_clean()
    folders_to_backup = get_folders_to_clean()
    
    logging.info(f"📊 Encontrados:")
    logging.info(f"   - {len(files_to_backup)} arquivos para backup")
    logging.info(f"   - {len(folders_to_backup)} pastas para backup")
    
    # Mover arquivos
    move_files_to_backup(files_to_backup, backup_path)
    
    # Mover pastas
    for folder in folders_to_backup:
        try:
            backup_folder_path = backup_path / folder.name
            shutil.move(str(folder), str(backup_folder_path))
            logging.info(f"📁 Pasta movida: {folder}")
        except Exception as e:
            logging.error(f"❌ Erro ao mover pasta {folder}: {e}")
    
    # Limpeza final
    clean_empty_folders()
    update_gitignore()
    
    # Criar relatório
    create_cleanup_report(backup_path, files_to_backup, folders_to_backup)
    
    logging.info("✅ Limpeza concluída!")
    logging.info(f"📦 Arquivos antigos em: {backup_path}/")
    logging.info("🎯 Projeto organizado e limpo!")

if __name__ == "__main__":
    main()
