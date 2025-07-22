# Inicializar Sistema de Captação de Imóveis
Write-Host "========================================" -ForegroundColor Green
Write-Host "   SISTEMA DE CAPTACAO DE IMOVEIS" -ForegroundColor Green
Write-Host "   Iniciando todos os serviços..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Navegar para diretório do projeto
$projectPath = "c:\Users\rober\OneDrive\Desktop\Sistema_Captacao_Imoveis"
Set-Location $projectPath
Write-Host "Diretório atual: $(Get-Location)" -ForegroundColor Cyan

Write-Host "`n[1/4] Verificando ambiente virtual Python..." -ForegroundColor Yellow
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "✓ Ambiente virtual encontrado" -ForegroundColor Green
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "✗ Ambiente virtual não encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/4] Iniciando Backend (Flask API)..." -ForegroundColor Yellow
if (Test-Path "backend\main.py") {
    Write-Host "✓ Backend encontrado, iniciando servidor..." -ForegroundColor Green
    $backend = Start-Process python -ArgumentList "backend\main.py" -NoNewWindow -PassThru
    Write-Host "Backend iniciado (PID: $($backend.Id))" -ForegroundColor Green
} else {
    Write-Host "✗ Arquivo backend\main.py não encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/4] Iniciando Monitoring Dashboard (Python)..." -ForegroundColor Yellow
if (Test-Path "simple_monitoring_dashboard.py") {
    Write-Host "✓ Simple monitoring dashboard encontrado, iniciando..." -ForegroundColor Green
    $monitoring = Start-Process python -ArgumentList "simple_monitoring_dashboard.py" -NoNewWindow -PassThru
    Write-Host "Monitoring dashboard iniciado (PID: $($monitoring.Id))" -ForegroundColor Green
} else {
    Write-Host "⚠ Simple monitoring dashboard não encontrado, continuando..." -ForegroundColor Yellow
}

Write-Host "`nAguardando 5 segundos para o backend inicializar..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "`n[4/4] Iniciando Frontend (React)..." -ForegroundColor Yellow
Set-Location "frontend"
if (Test-Path "package.json") {
    Write-Host "✓ Frontend encontrado, verificando dependências..." -ForegroundColor Green
    if (Test-Path "node_modules") {
        Write-Host "✓ Dependências instaladas" -ForegroundColor Green
    } else {
        Write-Host "⚠ Instalando dependências..." -ForegroundColor Yellow
        npm install
    }
    $frontend = Start-Process npm -ArgumentList "start" -NoNewWindow -PassThru
    Write-Host "Frontend iniciado (PID: $($frontend.Id))" -ForegroundColor Green
} else {
    Write-Host "✗ package.json não encontrado no diretório frontend" -ForegroundColor Red
    Set-Location $projectPath
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   SISTEMA INICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n Backend API:      http://localhost:5000" -ForegroundColor Cyan
Write-Host " Frontend React:   http://localhost:3000" -ForegroundColor Cyan
Write-Host " Monitoring:       http://localhost:8080" -ForegroundColor Cyan
Write-Host "`nProcessos em execução:" -ForegroundColor Yellow
Write-Host " - Backend PID: $($backend.Id)" -ForegroundColor White
if ($monitoring) { Write-Host " - Monitoring PID: $($monitoring.Id)" -ForegroundColor White }
Write-Host " - Frontend PID: $($frontend.Id)" -ForegroundColor White

# Aguardar 10 segundos e testar conectividade
Write-Host "`nAguardando serviços iniciarem..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "`nTestando conectividade..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "✓ Backend respondendo na porta 5000" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend não está respondendo" -ForegroundColor Red
}

try {
    Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "✓ Frontend respondendo na porta 3000" -ForegroundColor Green
} catch {
    Write-Host "⚠ Frontend ainda carregando ou não disponível" -ForegroundColor Yellow
}

Write-Host "`nSistema pronto para uso!" -ForegroundColor Green

# Abrir dashboards automaticamente
Write-Host "`nAbrindo dashboards..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Abrir frontend no navegador padrão
try {
    Start-Process "http://localhost:3000"
    Write-Host "✓ Dashboard React aberto no navegador" -ForegroundColor Green
} catch {
    Write-Host "⚠ Não foi possível abrir o navegador automaticamente" -ForegroundColor Yellow
}

Write-Host "`n🎉 Todos os serviços foram iniciados!" -ForegroundColor Green
Write-Host "   Acesse http://localhost:3000 para usar o sistema" -ForegroundColor Cyan
