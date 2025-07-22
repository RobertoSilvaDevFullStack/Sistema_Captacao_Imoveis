#!/usr/bin/env python3
"""
Organizador de Testes - Sistema de Captação de Imóveis
Analisa, categoriza e limpa arquivos de teste desnecessários
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import re

class TestOrganizer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / "backup_old_tests"
        self.tests_to_keep = []
        self.tests_to_archive = []
        self.tests_to_delete = []
        
    def analyze_test_files(self):
        """Analisa todos os arquivos de teste"""
        print("🔍 Analisando arquivos de teste...")
        
        test_files = list(self.project_root.glob("test_*.py"))
        
        # Categorias de testes
        important_tests = {
            'test_advanced_system.py': 'Sistema avançado - MANTER',
            'test_enhanced_scraper_validation.py': 'Validação scraper principal - MANTER',
            'test_ocr_service_updated_validation.py': 'OCR service atual - MANTER',
            'test_smart_data_extractor_validation.py': 'Data extractor atual - MANTER',
            'test_cache_and_database_integration.py': 'Integração cache/DB - MANTER',
            'test_enrichment_system.py': 'Sistema de enriquecimento - MANTER'
        }
        
        outdated_tests = [
            'test_olx_final_working.py',
            'test_olx_final.py', 
            'test_olx_fixed.py',
            'test_olx_urls.py',
            'test_vivareal_advanced.py',
            'test_vivareal_simple.py',
            'test_quick.py',
            'test_quick_structure.py',
            'test_simple_scraper.py',
            'test_scraper_structure.py',
            'test_clean_system.py',
            'test_complete_system.py'
        ]
        
        debug_tests = [
            'test_main.py',
            'test_server.py',
            'test_api.py',
            'test_api_updated.py'
        ]
        
        # Categorizar testes
        for test_file in test_files:
            file_name = test_file.name
            
            if file_name in important_tests:
                self.tests_to_keep.append((test_file, important_tests[file_name]))
            elif file_name in outdated_tests:
                self.tests_to_archive.append((test_file, "Teste desatualizado"))
            elif file_name in debug_tests:
                self.tests_to_archive.append((test_file, "Teste de debug"))
            elif self._is_empty_or_minimal(test_file):
                self.tests_to_delete.append((test_file, "Arquivo vazio ou minimal"))
            else:
                # Analisar conteúdo para decidir
                content_analysis = self._analyze_content(test_file)
                if content_analysis['keep']:
                    self.tests_to_keep.append((test_file, content_analysis['reason']))
                else:
                    self.tests_to_archive.append((test_file, content_analysis['reason']))
    
    def _is_empty_or_minimal(self, file_path):
        """Verifica se arquivo está vazio ou tem conteúdo mínimo"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Considera vazio se tem menos de 10 linhas úteis
            if len(lines) < 10:
                return True
                
            # Verifica se é só comentários
            code_lines = [line for line in lines if not line.startswith('#') and not line.startswith('"""')]
            return len(code_lines) < 5
            
        except:
            return True
    
    def _analyze_content(self, file_path):
        """Analisa conteúdo do arquivo para decidir se manter"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Indicadores de teste importante
            important_keywords = [
                'def test_', 'class Test', 'unittest', 'pytest',
                'backend/main.py', 'enhanced_scraper', 'ocr_service',
                'smart_data_extractor', 'database_service'
            ]
            
            # Indicadores de teste desatualizado
            outdated_keywords = [
                'debug', 'temp', 'old', 'backup', 'deprecated',
                'teste_', 'exemplo_', 'demo_'
            ]
            
            important_count = sum(1 for keyword in important_keywords if keyword in content)
            outdated_count = sum(1 for keyword in outdated_keywords if keyword in content)
            
            if important_count >= 2:
                return {'keep': True, 'reason': 'Contém testes importantes'}
            elif outdated_count > 0:
                return {'keep': False, 'reason': 'Contém código desatualizado'}
            else:
                return {'keep': False, 'reason': 'Teste experimental ou temporário'}
                
        except:
            return {'keep': False, 'reason': 'Erro ao ler arquivo'}
    
    def create_backup_directory(self):
        """Cria diretório de backup"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir()
            print(f"📁 Diretório de backup criado: {self.backup_dir}")
    
    def generate_report(self):
        """Gera relatório da análise"""
        report = f"""
# 📊 RELATÓRIO DE ORGANIZAÇÃO DE TESTES
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 RESUMO:
- **Total de arquivos analisados:** {len(self.tests_to_keep) + len(self.tests_to_archive) + len(self.tests_to_delete)}
- **Testes a manter:** {len(self.tests_to_keep)}
- **Testes a arquivar:** {len(self.tests_to_archive)}
- **Testes a deletar:** {len(self.tests_to_delete)}

## ✅ TESTES A MANTER ({len(self.tests_to_keep)}):
"""
        
        for test_file, reason in self.tests_to_keep:
            report += f"- **{test_file.name}** - {reason}\n"
        
        report += f"\n## 📦 TESTES A ARQUIVAR ({len(self.tests_to_archive)}):\n"
        for test_file, reason in self.tests_to_archive:
            report += f"- **{test_file.name}** - {reason}\n"
        
        report += f"\n## 🗑️ TESTES A DELETAR ({len(self.tests_to_delete)}):\n"
        for test_file, reason in self.tests_to_delete:
            report += f"- **{test_file.name}** - {reason}\n"
        
        report += """
## 🎯 RECOMENDAÇÕES:

### ✅ ESTRUTURA FINAL DE TESTES:
```
tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
├── system/         # Testes de sistema
└── validation/     # Testes de validação
```

### 🚀 AÇÕES SUGERIDAS:
1. **Manter** apenas os testes essenciais
2. **Arquivar** testes desatualizados no backup
3. **Deletar** arquivos vazios ou experimentais
4. **Organizar** testes restantes em estrutura clara

### 💡 BENEFÍCIOS:
- Projeto mais limpo e organizado
- Redução de arquivos desnecessários
- Melhor manutenibilidade
- Foco nos testes realmente úteis
"""
        
        return report
    
    def execute_cleanup(self, dry_run=True):
        """Executa a limpeza dos testes"""
        if dry_run:
            print("🔍 MODO SIMULAÇÃO - Nenhum arquivo será movido/deletado")
        else:
            self.create_backup_directory()
        
        print(f"\n📊 AÇÕES A EXECUTAR:")
        print(f"✅ Manter: {len(self.tests_to_keep)} arquivos")
        print(f"📦 Arquivar: {len(self.tests_to_archive)} arquivos")
        print(f"🗑️ Deletar: {len(self.tests_to_delete)} arquivos")
        
        # Arquivar testes desatualizados
        if self.tests_to_archive:
            print(f"\n📦 Arquivando {len(self.tests_to_archive)} testes:")
            for test_file, reason in self.tests_to_archive:
                print(f"  → {test_file.name} ({reason})")
                if not dry_run:
                    shutil.move(str(test_file), str(self.backup_dir / test_file.name))
        
        # Deletar testes vazios
        if self.tests_to_delete:
            print(f"\n🗑️ Deletando {len(self.tests_to_delete)} arquivos:")
            for test_file, reason in self.tests_to_delete:
                print(f"  → {test_file.name} ({reason})")
                if not dry_run:
                    test_file.unlink()
        
        # Manter testes importantes
        if self.tests_to_keep:
            print(f"\n✅ Mantendo {len(self.tests_to_keep)} testes essenciais:")
            for test_file, reason in self.tests_to_keep:
                print(f"  → {test_file.name} ({reason})")

def main():
    """Função principal"""
    print("🧹 ORGANIZADOR DE TESTES")
    print("Sistema de Captação de Imóveis")
    print("=" * 50)
    
    organizer = TestOrganizer()
    organizer.analyze_test_files()
    
    # Gerar relatório
    report = organizer.generate_report()
    
    # Salvar relatório
    report_file = Path("TEST_CLEANUP_REPORT.md")
    report_file.write_text(report, encoding='utf-8')
    print(f"📄 Relatório salvo em: {report_file}")
    
    # Mostrar resumo
    print(f"\n📊 RESUMO DA ANÁLISE:")
    print(f"✅ Testes a manter: {len(organizer.tests_to_keep)}")
    print(f"📦 Testes a arquivar: {len(organizer.tests_to_archive)}")
    print(f"🗑️ Testes a deletar: {len(organizer.tests_to_delete)}")
    
    # Executar simulação
    print(f"\n🔍 SIMULAÇÃO DE LIMPEZA:")
    organizer.execute_cleanup(dry_run=True)
    
    print(f"\n💡 Para executar a limpeza real:")
    print(f"   1. Revise o relatório: TEST_CLEANUP_REPORT.md")
    print(f"   2. Execute: python organize_tests.py --execute")

if __name__ == "__main__":
    main()
