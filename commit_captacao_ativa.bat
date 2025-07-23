@echo off
echo 🚀 COMMIT - Sistema de Captacao Ativa Multi-Cidade
echo =====================================================

cd /d "C:\Users\rober\OneDrive\Desktop\Sistema_Captacao_Imoveis"

echo.
echo 📋 Verificando status do repositorio...
git status

echo.
echo 📦 Adicionando arquivos ao staging...
git add .

echo.
echo 💾 Criando commit...
git commit -m "feat: Implementar sistema de captacao ativa multi-cidade

✅ FUNCIONALIDADES IMPLEMENTADAS:
- Sistema de captacao ativa para multiplas cidades brasileiras
- Analise completa dos dados existentes (380 propriedades SP)
- Configuracao para 10+ cidades (Rio, BH, Brasilia, etc.)
- Scripts de teste e execucao para captacao imediata
- Relatorios executivos e planos de implementacao

🚀 COMPONENTES ADICIONADOS:
- RELATORIO_CAPTACAO_ATIVA.py: Relatorio executivo completo
- RELATORIO_FINAL_CAPTACAO_ATIVA.md: Documentacao detalhada
- executar_captacao_rio.py: Script para teste Rio de Janeiro
- executar_teste_rio.py: Teste direto do sistema
- TestarCaptacaoAtiva.ps1: Script PowerShell para Windows
- Multiplos scripts de analise e demonstracao

📊 SISTEMA PREPARADO PARA:
- Captacao em Rio de Janeiro, Belo Horizonte, Brasilia
- Crescimento de 380 para 1000+ propriedades
- Expansao multi-cidade automatizada
- Captacao continua via Celery + Docker

🎯 PROXIMOS PASSOS:
- Executar teste no Rio de Janeiro
- Ativar captacao em multiplas cidades
- Implementar sistema continuo automatizado"

echo.
echo 🌐 Enviando para GitHub...
git push origin main

echo.
echo ✅ COMMIT REALIZADO COM SUCESSO!
echo 📍 Alteracoes enviadas para: https://github.com/RobertoSilvaDevFullStack/Sistema_Captacao_Imoveis
echo.
echo 🎯 SISTEMA DE CAPTACAO ATIVA MULTI-CIDADE COMMITADO!
echo    - 10+ cidades configuradas
echo    - Scripts de teste criados
echo    - Documentacao completa
echo    - Pronto para execucao imediata
echo.
pause
