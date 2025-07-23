# 🏠 Sistema de Captação de Imóveis

## 🎯 **COMO USAR - VERSÃO PRINCIPAL**

### 🚀 **Início Rápido**

**1. Execute o sistema completo:**
```bash
# Windows:
start_main_system.bat

# Ou manualmente:
python start_system.py
```

**2. Acesse o Dashboard Principal:**
```
🎯 Dashboard React: http://localhost:3000
```

### 📊 **Arquitetura do Sistema**

```
┌─────────────────────────────────────────┐
│          🎯 TELA PRINCIPAL              │
│      Dashboard React (porta 3000)       │  
│                                         │
│  ┌─────────────────────────────────────┐ │
│  │ • Busca de imóveis                  │ │
│  │ • Filtros avançados                 │ │
│  │ • Visualização de propriedades      │ │
│  │ • Gráficos e estatísticas          │ │
│  │ • Botão p/ Dashboard Monitoramento │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
             ↑ Principal ↑

┌─────────────────────────────────────────┐
│       📊 DASHBOARD SECUNDÁRIO           │
│   Dashboard Monitoramento (porta 5000)  │
│                                         │
│  ┌─────────────────────────────────────┐ │  
│  │ • Status dos scrapers               │ │
│  │ • Logs do sistema                   │ │
│  │ • Métricas de performance          │ │
│  │ • Status dos containers            │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
            ↑ Secundário ↑

┌─────────────────────────────────────────┐
│           📡 BACKEND API                │
│        API Server (porta 8000)          │
│                                         │
│  ┌─────────────────────────────────────┐ │
│  │ • /api/search - Buscar propriedades │ │
│  │ • /api/scrapers/status - Status     │ │  
│  │ • /api/cities - Lista cidades       │ │
│  │ • /api/stats - Estatísticas        │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 🎨 **Funcionalidades do Dashboard Principal (React)**

#### 🔍 **Busca de Imóveis**
- **Filtros Avançados**: Cidade, tipo de imóvel, portal
- **Resultados em Tempo Real**: Visualização imediata
- **Cards Interativos**: Detalhes completos das propriedades

#### 📊 **Visualizações**
- **Gráficos**: Novos anúncios, distribuição por quartos
- **Estatísticas**: Preço médio, preço por m², total de imóveis
- **Métricas**: Uptime, performance dos portais

#### 🎯 **Interface**
- **Moderna**: Design responsivo com TailwindCSS
- **Intuitiva**: Navegação simples e clara
- **Acessível**: Botão direto para Dashboard de Monitoramento

### 🔧 **Configuração dos Portais**

#### Portais Disponíveis:
- **🟦 ZapImóveis**: Portal principal de imóveis
- **🟩 VivaReal**: Portal do Grupo OLX  
- **🟨 OLX**: Classificados online

#### Cidades Suportadas:
- Rio de Janeiro, São Paulo, Belo Horizonte
- Brasília, Salvador, Fortaleza, Recife
- Porto Alegre, Curitiba, Florianópolis

### 📱 **Como Navegar**

#### **Dashboard Principal (React) - http://localhost:3000**
1. **Selecione os filtros**: Cidade, tipo de imóvel, portal
2. **Clique em "Buscar"**: Sistema executará scraping
3. **Veja os resultados**: Cards com detalhes das propriedades  
4. **Análise visual**: Gráficos e estatísticas automáticas
5. **Acesse monitoramento**: Botão "Dashboard de Monitoramento"

#### **Dashboard Monitoramento (Python) - http://localhost:5000**  
- **Status dos Portais**: Ver se scrapers estão funcionando
- **Logs em Tempo Real**: Acompanhar execução
- **Métricas do Sistema**: CPU, memória, containers
- **Alertas**: Problemas detectados automaticamente

### ⚡ **Fluxo de Uso Recomendado**

```
1. 🚀 Execute: start_main_system.bat
   ↓
2. 🌐 Abra: http://localhost:3000 (abre automaticamente)
   ↓  
3. 🔍 Configure filtros no Dashboard React
   ↓
4. 📊 Execute busca e veja resultados
   ↓
5. 🔧 Se precisar de monitoramento detalhado:
   Clique em "Dashboard de Monitoramento"
   ↓
6. 📈 Analise dados, logs e métricas
```

### 🛠️ **Resolução de Problemas**

#### **Dashboard não carrega:**
```bash
# Verificar se serviços estão rodando:
curl http://localhost:3000  # React
curl http://localhost:8000/api/health  # Backend API
curl http://localhost:5000/api/health  # Monitoramento
```

#### **Busca não funciona:**
1. Verificar se Backend API está rodando (porta 8000)
2. Abrir Dashboard de Monitoramento para ver logs
3. Verificar se containers Docker estão ativos

#### **Scrapers não respondem:**
1. Ir para Dashboard de Monitoramento  
2. Ver status de cada portal (ZapImóveis, OLX, VivaReal)
3. Verificar logs de erro em tempo real

### 📋 **Arquivos Importantes**

```
Sistema_Captacao_Imoveis/
├── 🎯 start_main_system.bat     # Iniciar sistema completo
├── 📡 backend_api_server.py     # API para React
├── 📊 test_server.py           # Dashboard monitoramento  
├── 🐳 docker-compose-*.yml     # Containers (Selenium, Redis)
└── frontend/                   # Dashboard React
    ├── src/pages/Dashboard_new.jsx  # Página principal
    └── src/services/propertyService.js  # Conexão com API
```

### 🎉 **Resumo**

- **🎯 Dashboard React (3000)**: TELA PRINCIPAL - Use aqui!
- **📊 Dashboard Python (5000)**: Monitoramento e logs
- **📡 Backend API (8000)**: Serviços para o React
- **🐳 Docker**: Selenium Grid + Redis + PostgreSQL

**O Dashboard React é sua interface principal!** O dashboard de monitoramento é complementar para acompanhar o sistema.
