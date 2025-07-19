# Sistema de Captação de Imóveis 🏠

Sistema profissional para scraping e análise de propriedades imobiliárias com foco em oportunidades de investimento.

## 🎯 **Funcionalidades Principais**

- ✅ **Scraping Inteligente**: Extração de dados dos principais portais imobiliários
- ✅ **Detecção de Oportunidades**: Identificação automática de lançamentos e promoções
- ✅ **API REST**: Interface moderna para integração
- ✅ **Frontend React**: Dashboard interativo para visualização
- ✅ **Análise de Mercado**: Métricas e insights de investimento

## 🏗️ **Arquitetura Limpa**

```
src/
├── api/           # API Flask
├── scrapers/      # Scrapers organizados
├── models/        # Modelos de dados
├── services/      # Lógica de negócio
├── config/        # Configurações
└── utils/         # Utilitários

frontend/          # Interface React
tests/             # Testes automatizados
docs/              # Documentação
scripts/           # Scripts utilitários
```

## 🚀 **Instalação e Configuração**

### Pré-requisitos
- Python 3.9+
- Node.js 16+
- Chrome/Chromium (para Selenium)

### 1. Instalar Dependências Python
```bash
pip install -r requirements_clean.txt
```

### 2. Instalar Dependências Frontend
```bash
cd frontend
npm install
```

### 3. Configurar Variáveis de Ambiente
```bash
# Criar arquivo .env na raiz
ENVIRONMENT=development
SECRET_KEY=sua-chave-secreta
```

## 🎮 **Como Usar**

### Iniciar API
```bash
cd src
python api/app.py
```

### Iniciar Frontend
```bash
cd frontend
npm start
```

### Testar Sistema
```bash
python test_clean_system.py
```

## 📊 **Portais Suportados**

| Portal | Status | Recursos |
|--------|--------|----------|
| **ZapImóveis** | ✅ Ativo | Badges, Preços, Localização |
| **OLX** | 🔄 Desenvolvimento | - |
| **VivaReal** | 📅 Planejado | - |

## 🔍 **API Endpoints**

### Buscar Propriedades
```http
GET /api/properties/search?city=rio-de-janeiro&property_type=apartamento&portal=zapimoveis
```

### Status dos Scrapers
```http
GET /api/scrapers/status
```

### Health Check
```http
GET /api/health
```

## 🎯 **Recursos Especiais**

### Detecção de Oportunidades
O sistema identifica automaticamente propriedades com:
- 🏷️ **Badges Especiais**: OPORTUNIDADE, LANÇAMENTO, PROMOÇÃO
- 💰 **Preços Competitivos**: Análise comparativa de mercado
- ⚡ **Recém-Adicionadas**: Propriedades novas no portal

### Anti-Detecção Avançada
- 🤖 **User Agents Rotativos**: Simula navegadores reais
- ⏱️ **Delays Inteligentes**: Comportamento humano
- 🔄 **Retry Logic**: Recuperação automática de erros

## 🧪 **Testes**

```bash
# Teste completo do sistema
python test_clean_system.py

# Testes específicos
pytest tests/
```

## 📈 **Monitoramento**

- 📊 **Logs Estruturados**: Rastreamento completo de operações
- 🚨 **Alertas de Erro**: Notificação automática de falhas
- 📉 **Métricas de Performance**: Tempo de resposta e taxa de sucesso

## 🔧 **Configurações Avançadas**

### Scraper Settings
```python
SCRAPER = ScraperConfig(
    max_results=20,
    timeout=30,
    retry_attempts=3,
    delay_between_requests=1.0
)
```

### API Settings
```python
API = APIConfig(
    host='0.0.0.0',
    port=5000,
    debug=False,
    cors_enabled=True
)
```

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 **Autor**

**Roberto Silva**
- 🌐 GitHub: [@RobertoSilvaDevFullStack](https://github.com/RobertoSilvaDevFullStack)
- 📧 Email: [seu-email@exemplo.com]

---

⭐ **Se este projeto foi útil, deixe uma estrela!**
