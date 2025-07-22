@echo off
echo ========================================
echo   SISTEMA DE CAPTACAO DE IMOVEIS
echo   Iniciando todos os serviços...
echo ========================================

echo.
echo [1/3] Ativando ambiente virtual Python...
call .venv\Scripts\activate.bat

echo.
echo [2/3] Iniciando Backend (Flask API)...
start "Backend Flask" cmd /c "python backend\main.py"

echo.
echo Aguardando 5 segundos para o backend inicializar...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Iniciando Frontend (React)...
cd frontend
start "Frontend React" cmd /c "npm start"

echo.
echo ========================================
echo   SISTEMA INICIADO COM SUCESSO!
echo ========================================
echo.
echo  Backend API:  http://localhost:5000
echo  Frontend:     http://localhost:3000
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
