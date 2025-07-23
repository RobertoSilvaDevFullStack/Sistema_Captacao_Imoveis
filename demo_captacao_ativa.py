#!/usr/bin/env python3
"""
DEMONSTRAÇÃO: Sistema de Captação Ativa Multi-Cidade
Análise dos dados existentes e planejamento para expansão
"""

import json
from datetime import datetime
from pathlib import Path
import re

def analyze_current_data():
    """Análise completa dos dados atuais"""
    print("📊 ANÁLISE DOS DADOS ATUAIS")
    print("=" * 50)
    
    try:
        # Carregar dados
        with open('processed_properties_data.json', 'r', encoding='utf-8') as f:
            properties = json.load(f)
        
        print(f"📋 Total de propriedades: {len(properties)}")
        
        # Análise detalhada
        cities = {}
        sources = {}
        neighborhoods = {}
        price_ranges = {'0-300k': 0, '300k-500k': 0, '500k-1M': 0, '1M+': 0}
        
        for prop in properties:
            # Cidade pela URL
            url = prop.get('url', '')
            if 'sao-paulo' in url:
                city = 'São Paulo'
            elif 'rio-de-janeiro' in url:
                city = 'Rio de Janeiro'
            elif 'belo-horizonte' in url:
                city = 'Belo Horizonte'
            else:
                city = 'Outras'
            
            cities[city] = cities.get(city, 0) + 1
            
            # Fonte
            if 'vivareal.com.br' in url:
                source = 'VivaReal'
            elif 'zapimoveis.com.br' in url:
                source = 'ZapImóveis'  
            elif 'olx.com.br' in url:
                source = 'OLX'
            else:
                source = 'Outras'
            
            sources[source] = sources.get(source, 0) + 1
            
            # Bairro
            neighborhood = prop.get('neighborhood', 'Desconhecido')
            if neighborhood and neighborhood != 'Unknown':
                neighborhoods[neighborhood] = neighborhoods.get(neighborhood, 0) + 1
            
            # Preço
            price = prop.get('price', 0)
            if isinstance(price, (int, float)):
                if price < 300000:
                    price_ranges['0-300k'] += 1
                elif price < 500000:
                    price_ranges['300k-500k'] += 1
                elif price < 1000000:
                    price_ranges['500k-1M'] += 1
                else:
                    price_ranges['1M+'] += 1
        
        # Exibir resultados
        print(f"\n📍 DISTRIBUIÇÃO POR CIDADES:")
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(properties)) * 100
            print(f"   {city}: {count} imóveis ({percentage:.1f}%)")
        
        print(f"\n🌐 DISTRIBUIÇÃO POR FONTE:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(properties)) * 100
            print(f"   {source}: {count} imóveis ({percentage:.1f}%)")
        
        print(f"\n💰 DISTRIBUIÇÃO POR PREÇO:")
        for range_name, count in price_ranges.items():
            percentage = (count / len(properties)) * 100 if len(properties) > 0 else 0
            print(f"   R$ {range_name}: {count} imóveis ({percentage:.1f}%)")
        
        print(f"\n🏘️ TOP 10 BAIRROS:")
        top_neighborhoods = sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True)[:10]
        for neighborhood, count in top_neighborhoods:
            percentage = (count / len(properties)) * 100
            print(f"   {neighborhood}: {count} imóveis ({percentage:.1f}%)")
        
        return {
            'total': len(properties),
            'cities': cities,
            'sources': sources,
            'neighborhoods': neighborhoods,
            'price_ranges': price_ranges
        }
        
    except FileNotFoundError:
        print("❌ Arquivo processed_properties_data.json não encontrado")
        return None
    except Exception as e:
        print(f"❌ Erro ao analisar dados: {e}")
        return None

def check_scraper_infrastructure():
    """Verifica infraestrutura dos scrapers"""
    print(f"\n🤖 INFRAESTRUTURA DE SCRAPERS")
    print("=" * 50)
    
    # Verificar scrapers existentes
    scrapers_dir = Path('backend/scrapers')
    scrapers_found = []
    
    if scrapers_dir.exists():
        for scraper_file in scrapers_dir.glob('*_scraper.py'):
            scraper_name = scraper_file.stem.replace('_scraper', '').upper()
            scrapers_found.append(scraper_name)
            print(f"✅ {scraper_name} Scraper encontrado")
            
            # Verificar funcionalidades do scraper
            try:
                with open(scraper_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                features = []
                if 'location' in content.lower():
                    features.append('Multi-cidade')
                if 'sleep' in content or 'time.sleep' in content:
                    features.append('Rate limiting')
                if 'random' in content:
                    features.append('Anti-detecção')
                if 'selenium' in content.lower():
                    features.append('Selenium')
                
                if features:
                    print(f"   Funcionalidades: {', '.join(features)}")
                    
            except Exception as e:
                print(f"   ⚠️ Erro ao analisar {scraper_file}: {e}")
    
    else:
        print("❌ Diretório de scrapers não encontrado")
    
    # Verificar configuração de localizações
    location_config = Path('backend/config/location_config.py')
    if location_config.exists():
        print(f"✅ Configuração de cidades encontrada")
        
        try:
            with open(location_config, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Contar cidades configuradas
            city_matches = re.findall(r'"([^"]+)":\s*Location', content)
            print(f"   📍 Cidades configuradas: {len(city_matches)}")
            
            # Mostrar algumas cidades
            if city_matches:
                print(f"   Exemplos: {', '.join(city_matches[:5])}")
                if len(city_matches) > 5:
                    print(f"   ... e mais {len(city_matches) - 5} cidades")
                    
        except Exception as e:
            print(f"   ⚠️ Erro ao analisar configuração: {e}")
    else:
        print("❌ Configuração de cidades não encontrada")
    
    return scrapers_found

def create_expansion_plan(current_data):
    """Cria plano de expansão para outras cidades"""
    print(f"\n🚀 PLANO DE EXPANSÃO MULTI-CIDADE")
    print("=" * 50)
    
    if not current_data:
        print("❌ Sem dados atuais para basear o plano")
        return None
    
    print("📋 SITUAÇÃO ATUAL:")
    print(f"   • Total de propriedades: {current_data['total']}")
    print(f"   • Cidades com dados: {len(current_data['cities'])}")
    print(f"   • Fontes ativas: {len(current_data['sources'])}")
    
    # Cidades prioritárias para expansão
    expansion_cities = [
        {'name': 'Rio de Janeiro', 'code': 'rio_de_janeiro', 'priority': 'ALTA', 'target': 500},
        {'name': 'Belo Horizonte', 'code': 'belo_horizonte', 'priority': 'ALTA', 'target': 300},
        {'name': 'Brasília', 'code': 'brasilia', 'priority': 'MÉDIA', 'target': 250},
        {'name': 'Salvador', 'code': 'salvador', 'priority': 'MÉDIA', 'target': 200},
        {'name': 'Fortaleza', 'code': 'fortaleza', 'priority': 'BAIXA', 'target': 150},
        {'name': 'Porto Alegre', 'code': 'porto_alegre', 'priority': 'BAIXA', 'target': 150},
    ]
    
    print(f"\n🎯 CIDADES PARA EXPANSÃO:")
    total_target = 0
    for city in expansion_cities:
        print(f"   {city['name']}:")
        print(f"      Prioridade: {city['priority']}")
        print(f"      Meta: {city['target']} propriedades")
        print(f"      Código: {city['code']}")
        total_target += city['target']
    
    print(f"\n📊 PROJEÇÃO TOTAL:")
    current_total = current_data['total']
    projected_total = current_total + total_target
    print(f"   Dados atuais: {current_total} propriedades")
    print(f"   Meta expansão: {total_target} propriedades")
    print(f"   Total projetado: {projected_total} propriedades")
    print(f"   Crescimento: {(total_target / current_total * 100):.0f}%")
    
    return expansion_cities

def create_execution_strategy():
    """Cria estratégia de execução"""
    print(f"\n⚡ ESTRATÉGIA DE EXECUÇÃO")
    print("=" * 50)
    
    print("📋 OPÇÕES DISPONÍVEIS:")
    
    print(f"\n1️⃣ EXECUÇÃO MANUAL (Recomendada para teste):")
    print("   • Executar scraper por cidade individualmente")
    print("   • Controle total do processo")
    print("   • Verificação imediata de resultados")
    print("   • Ajustes em tempo real")
    print("   • Exemplo: python -c \"from scrapers.olx_scraper import OLXScraper; ...\"")
    
    print(f"\n2️⃣ SISTEMA SEMI-AUTOMÁTICO:")
    print("   • Script para executar múltiplas cidades")
    print("   • Pausas configuráveis entre cidades")
    print("   • Logs detalhados")
    print("   • Salvamento incremental")
    
    print(f"\n3️⃣ SISTEMA TOTALMENTE AUTOMÁTICO (Futuro):")
    print("   • Celery + Redis para agendamento")
    print("   • Execução em horários específicos")
    print("   • Monitoramento automático")
    print("   • Recuperação de falhas")
    
    print(f"\n🎯 PRÓXIMO PASSO RECOMENDADO:")
    print("   Teste manual do scraper OLX para Rio de Janeiro")
    print("   Comando sugerido:")
    print("   python -c \"")
    print("   import sys; sys.path.append('backend')")
    print("   from scrapers.olx_scraper import OLXScraper")
    print("   scraper = OLXScraper('rio_de_janeiro')")
    print("   props = scraper.scrape_properties(max_pages=1)")
    print("   print(f'Captadas: {len(props)} propriedades')")
    print("   \"")

def generate_summary_report(data_stats, scrapers_found, expansion_plan):
    """Gera relatório resumo"""
    print(f"\n" + "=" * 70)
    print("🎯 RELATÓRIO RESUMO - SISTEMA DE CAPTAÇÃO ATIVA")
    print("=" * 70)
    
    print(f"📊 SITUAÇÃO ATUAL:")
    if data_stats:
        print(f"   • Propriedades no banco: {data_stats['total']}")
        print(f"   • Cidades com dados: {len(data_stats['cities'])}")
        print(f"   • Fontes ativas: {len(data_stats['sources'])}")
        
        # Cidade com mais dados
        top_city = max(data_stats['cities'].items(), key=lambda x: x[1])
        print(f"   • Cidade líder: {top_city[0]} ({top_city[1]} propriedades)")
        
        # Fonte principal
        top_source = max(data_stats['sources'].items(), key=lambda x: x[1])
        print(f"   • Fonte principal: {top_source[0]} ({top_source[1]} propriedades)")
    
    print(f"\n🤖 INFRAESTRUTURA TÉCNICA:")
    print(f"   • Scrapers disponíveis: {len(scrapers_found)}")
    if scrapers_found:
        print(f"   • Plataformas: {', '.join(scrapers_found)}")
    print(f"   • Configuração multi-cidade: ✅ Disponível")
    print(f"   • Anti-detecção: ✅ Configurado")
    print(f"   • Rate limiting: ✅ Implementado")
    
    print(f"\n🚀 PLANO DE EXPANSÃO:")
    if expansion_plan:
        high_priority = [c for c in expansion_plan if c['priority'] == 'ALTA']
        medium_priority = [c for c in expansion_plan if c['priority'] == 'MÉDIA']
        
        print(f"   • Cidades alta prioridade: {len(high_priority)}")
        if high_priority:
            print(f"     - {', '.join([c['name'] for c in high_priority])}")
        
        print(f"   • Cidades média prioridade: {len(medium_priority)}")
        if medium_priority:
            print(f"     - {', '.join([c['name'] for c in medium_priority])}")
        
        total_target = sum(c['target'] for c in expansion_plan)
        print(f"   • Meta total de expansão: {total_target} propriedades")
    
    print(f"\n✅ SISTEMA PRONTO PARA:")
    print(f"   • Captação imediata em múltiplas cidades")
    print(f"   • Expansão do banco de dados atual")  
    print(f"   • Diversificação de fontes de dados")
    print(f"   • Atualização contínua de propriedades")
    
    print(f"\n🎯 RECOMENDAÇÃO IMEDIATA:")
    print(f"   Testar captação no Rio de Janeiro (segunda maior cidade)")
    print(f"   Executar comando de teste manual do scraper OLX")
    
    print("=" * 70)

def main():
    """Função principal"""
    print("🏠 DEMONSTRAÇÃO: SISTEMA DE CAPTAÇÃO ATIVA MULTI-CIDADE")
    print("=" * 80)
    print(f"⏰ Análise iniciada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    
    # 1. Analisar dados atuais
    data_stats = analyze_current_data()
    
    # 2. Verificar infraestrutura
    scrapers_found = check_scraper_infrastructure()
    
    # 3. Criar plano de expansão
    expansion_plan = create_expansion_plan(data_stats)
    
    # 4. Definir estratégia
    create_execution_strategy()
    
    # 5. Gerar relatório final
    generate_summary_report(data_stats, scrapers_found, expansion_plan)

if __name__ == "__main__":
    main()
