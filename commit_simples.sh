#!/bin/bash
# Script simples para commit das alterações

echo "🚀 COMMIT: Sistema de Captação Ativa Multi-Cidade"
echo "================================================="

# Navegar para o diretório do projeto
cd "C:\Users\rober\OneDrive\Desktop\Sistema_Captacao_Imoveis"

# Adicionar todos os arquivos
echo "📦 Adicionando arquivos..."
git add .

# Criar commit
echo "💾 Criando commit..."
git commit -m "feat: Sistema de captação ativa multi-cidade

Implementação completa do sistema de captação ativa para múltiplas cidades:
- 10+ cidades brasileiras configuradas (Rio, BH, Brasília, etc.)
- Scripts de teste e execução imediata
- Análise dos 380 imóveis existentes de São Paulo  
- Sistema preparado para crescer para 1000+ propriedades
- Documentação completa e relatórios executivos
- Componentes: OLX, VivaReal, ZapImóveis scrapers
- Automação via Celery + Docker configurada"

# Enviar para GitHub
echo "🌐 Enviando para GitHub..."
git push origin main

echo "✅ COMMIT REALIZADO COM SUCESSO!"
echo "🔗 https://github.com/RobertoSilvaDevFullStack/Sistema_Captacao_Imoveis"
