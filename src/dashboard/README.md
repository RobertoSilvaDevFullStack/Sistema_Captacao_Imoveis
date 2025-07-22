# Sistema de Monitoramento - Dashboard Web

## 🎯 Visão Geral

Dashboard web completo para monitoramento em tempo real do sistema de scraping com anti-detecção. Interface moderna e responsiva com métricas detalhadas, alertas, gráficos interativos e logs do sistema.

## 📊 Funcionalidades Implementadas

### 1. Dashboard Principal (`dashboard.html`)
- **Interface Responsiva**: Bootstrap 5 com design moderno
- **Métricas do Sistema**: Uptime, containers ativos, CPU/memória
- **Status dos Portais**: Tabela com estatísticas detalhadas por portal
- **Gráficos Interativos**: Chart.js para visualização de dados
- **Alertas em Tempo Real**: Sistema de notificações automáticas
- **Logs ao Vivo**: Visualização dos logs recentes do sistema
- **Auto-refresh**: Atualização automática a cada 30 segundos

### 2. Backend de Monitoramento (`monitoring_dashboard.py`)
- **API RESTful**: Endpoints para todas as métricas
- **Integração Redis/PostgreSQL**: Persistência e cache de dados
- **Coleta de Métricas**: Sistema completo de monitoramento
- **Alertas Inteligentes**: Detecção automática de problemas
- **Performance Tracking**: Histórico de performance 24/7

### 3. Infraestrutura Docker (`docker-compose-production.yml`)
- **Selenium Grid**: Hub com containers especializados por portal
- **Redis**: Cache e armazenamento de métricas
- **PostgreSQL**: Banco de dados principal
- **Nginx**: Load balancer e proxy reverso
- **cAdvisor**: Monitoramento de containers

## 🚀 Como Usar

### 1. Iniciar o Sistema Completo
```bash
# Subir toda a infraestrutura
docker-compose -f docker-compose-production.yml up -d

# Verificar status dos containers
docker-compose -f docker-compose-production.yml ps
```

### 2. Acessar o Dashboard
```bash
# Iniciar o servidor de monitoramento
cd src/dashboard
python monitoring_dashboard.py

# Abrir no navegador
http://localhost:5000
```

### 3. Executar Scrapers com Monitoramento
```python
from backend.scrapers.zapimoveis_stealth import ZapImoveisStealthScraper

# Scraper com monitoramento automático
scraper = ZapImoveisStealthScraper()
properties = scraper.search_properties(
    location="São Paulo",
    property_type="apartamento"
)

# Métricas automaticamente enviadas para o dashboard
```

## 📈 Métricas Monitoradas

### Sistema
- **Uptime**: Tempo de funcionamento
- **Recursos**: CPU e memória em uso
- **Containers**: Status e disponibilidade
- **Performance**: Tempos de resposta e throughput

### Portais
- **Requisições**: Total e por período
- **Taxa de Sucesso**: Percentual de requisições bem-sucedidas
- **Bloqueios**: Detecção de anti-bot
- **Imóveis Coletados**: Volume de dados extraídos
- **Tempo de Resposta**: Latência média

### Alertas
- **Rate Limiting**: Violações detectadas
- **Bloqueios**: Captchas ou bloqueios por IP
- **Recursos**: Alto uso de CPU/memória
- **Containers**: Falhas ou indisponibilidade

## 🎨 Interface do Dashboard

### Layout Principal
```
┌─────────────────────────────────────────────────────────┐
│                    NAVBAR COM STATUS                    │
├─────────────────────────────────────────────────────────┤
│  [ALERTAS ATIVOS - Se houver]                          │
├─────────────────────────────────────────────────────────┤
│  UPTIME  │  CONTAINERS  │  CPU USAGE  │  MEMORY USAGE  │
├─────────────────────────────────────────────────────────┤
│                   STATUS DOS PORTAIS                    │
│  Portal │ Status │ Req │ Taxa │ Tempo │ Imóveis │ Bloq  │
├─────────────────────────────────────────────────────────┤
│  GRÁFICO REQUISIÇÕES  │     GRÁFICO TAXA SUCESSO       │
├─────────────────────────────────────────────────────────┤
│              TIMELINE DE PERFORMANCE (24h)              │
├─────────────────────────────────────────────────────────┤
│    LOGS RECENTES     │      STATUS CONTAINERS          │
└─────────────────────────────────────────────────────────┘
```

### Recursos Visuais
- **Cards Responsivos**: Adaptam-se a diferentes tamanhos de tela
- **Gráficos Interativos**: Hover, zoom e legendas dinâmicas
- **Códigos de Cor**: Verde (bom), amarelo (atenção), vermelho (problema)
- **Ícones FontAwesome**: Interface intuitiva e moderna
- **Auto-refresh Visual**: Indicador de atualização em tempo real

## 🔧 Configuração Avançada

### 1. Personalizar Intervalos de Refresh
```javascript
// Em dashboard.html, alterar linha:
refreshInterval = setInterval(refreshData, 30000); // 30 segundos

// Para 10 segundos:
refreshInterval = setInterval(refreshData, 10000);
```

### 2. Adicionar Novos Alertas
```python
# Em monitoring_dashboard.py
def check_custom_alert(self, portal_stats):
    if portal_stats.response_time > 10:  # 10 segundos
        return {
            'type': 'warning',
            'source': 'Performance',
            'message': f'Tempo de resposta alto: {portal_stats.response_time}s'
        }
```

### 3. Configurar Limites de Alerta
```python
# Arquivo de configuração
ALERT_THRESHOLDS = {
    'cpu_usage': 80,
    'memory_usage': 85,
    'error_rate': 20,
    'response_time': 5
}
```

## 📊 APIs Disponíveis

### Endpoints do Dashboard
```
GET /api/stats          # Estatísticas do sistema
GET /api/portals        # Status dos portais
GET /api/alerts         # Alertas ativos
GET /api/logs           # Logs recentes
GET /api/containers     # Status dos containers
GET /api/performance    # Dados de performance
```

### Exemplo de Resposta
```json
{
  "zapimoveis": {
    "total_requests": 150,
    "successful_requests": 145,
    "success_rate": 96.7,
    "avg_response_time": 2.3,
    "properties_scraped": 89,
    "blocked_requests": 2,
    "health_status": "good"
  }
}
```

## 🚀 Próximos Passos

Com o dashboard de monitoramento completo, agora podemos implementar:

1. **🎭 Sistema de Rotação de Proxies**
   - Pool de proxies residenciais
   - Rotação inteligente por geolocalização
   - Validação automática de proxies

2. **🤖 Modelos de ML para Detecção**
   - Análise de padrões de bloqueio
   - Predição de rate limits
   - Otimização automática de estratégias

O dashboard fornece a base de monitoramento necessária para implementar e acompanhar essas funcionalidades avançadas! 🎯
