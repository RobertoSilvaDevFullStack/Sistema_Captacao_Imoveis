@echo off
chcp 65001 >nul
echo ================================================================
echo          🏠 SISTEMA DE CAPTACAO DE IMOVEIS  
echo ================================================================
echo.
echo 🚀 Iniciando sistema completo...
echo.

echo 📡 [1/3] Iniciando Backend API (porta 8000)...
start /min "Backend API" cmd /c ".venv\Scripts\python.exe backend_api_server.py"
echo ✅ Backend API iniciado
timeout /t 5 > nul

echo 📊 [2/3] Iniciando Dashboard Monitoramento (porta 5000)...
start /min "Dashboard Monitor" cmd /c ".venv\Scripts\python.exe test_server.py"  
echo ✅ Dashboard Monitoramento iniciado
timeout /t 3 > nul

echo ⚛️  [3/3] Iniciando Frontend React (porta 3000)...
cd frontend
if exist "node_modules" (
    echo ✅ Dependências React OK
    start "React Dashboard" cmd /c "npm start"
) else (
    echo ⚠️  Instalando dependências React...
    start "React Dashboard" cmd /c "npm install && npm start"
)
cd ..
echo ✅ Frontend React iniciado

echo.
echo ⏳ Aguardando todos os serviços iniciarem...
timeout /t 15 > nul

echo.
echo ================================================================
echo                    🎉 SISTEMA INICIADO!
echo ================================================================
echo.
echo 🌐 Acesse as URLs:
echo.
echo    🎯 DASHBOARD PRINCIPAL (React):
echo       👉 http://localhost:3000  ^<-- PRINCIPAL
echo.
echo    📊 Dashboard Monitoramento:
echo       http://localhost:5000
echo.
echo    📡 API Backend:  
echo       http://localhost:8000/api/health
echo.
echo ================================================================
echo.
echo 💡 INSTRUÇÕES:
echo    1. Use o Dashboard React (3000) como TELA PRINCIPAL
echo    2. Acesse monitoramento via botão no Dashboard React
echo    3. Aguarde ~30seg para tudo carregar completamente
echo.

echo 🌍 Abrindo navegador na página principal...
timeout /t 3 > nul
start http://localhost:3000

echo.
echo ✨ Sistema rodando! Pressione qualquer tecla para sair...
pause > nul

echo.
echo 👋 Encerrando serviços...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
echo ✅ Sistema encerrado!
