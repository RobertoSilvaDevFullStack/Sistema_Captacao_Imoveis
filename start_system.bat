@echo off
chcp 65001 >nul
echo ========================================
echo    SISTEMA DE CAPTACAO DE IMOVEIS
echo    Iniciando todos os serviços...
echo ========================================
echo.

echo [1/4] Verificando ambiente virtual...
if exist ".venv\Scripts\python.exe" (
    echo ✓ Ambiente virtual encontrado
) else (
    echo ✗ Ambiente virtual não encontrado
    pause
    exit /b 1
)

echo.
echo [2/4] Iniciando Backend Flask...
start "Backend Flask API" cmd /c ".venv\Scripts\python.exe backend\main.py"
echo ✓ Backend iniciado

echo.
echo [3/4] Iniciando Monitoring Dashboard...
start "Monitoring Dashboard" cmd /c ".venv\Scripts\python.exe simple_monitoring_dashboard.py"
echo ✓ Monitoring dashboard iniciado

echo.
echo [4/4] Iniciando Frontend React...
cd frontend
start "Frontend React" cmd /c "npm start"
cd ..
echo ✓ Frontend iniciado

echo.
echo ========================================
echo    SISTEMA INICIADO COM SUCESSO!
echo ========================================
echo.
echo  Backend API:      http://localhost:5000
echo  Frontend React:   http://localhost:3000
echo  Monitoring:       http://localhost:8080
echo.
echo Aguardando 10 segundos e abrindo dashboards...
timeout /t 10 /nobreak >nul

echo.
echo Abrindo dashboards no navegador...
start http://localhost:3000
start http://localhost:8080

echo.
echo 🎉 Sistema totalmente ativo!
echo    Dashboards abertos no navegador
echo.
pause
