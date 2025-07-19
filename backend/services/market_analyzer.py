#!/usr/bin/env python3
# market_analyzer.py

import json
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import re

class MarketAnalyzer:
    """Classe para análise de mercado imobiliário com insights e relatórios avançados"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.properties = []
        self.analysis_results = {}
    
    def load_properties_data(self, file_path: str = 'processed_properties_data.json') -> bool:
        """Carrega dados processados de propriedades"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.properties = json.load(f)
            
            # Filtra apenas propriedades válidas
            self.properties = [p for p in self.properties if p.get('is_valid', False)]
            
            self.logger.info(f"Carregadas {len(self.properties)} propriedades válidas para análise")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            return False
    
    def analyze_by_neighborhood(self) -> Dict[str, Any]:
        """Analisa preços e características por bairro"""
        neighborhood_data = defaultdict(list)
        
        # Agrupa propriedades por bairro
        for prop in self.properties:
            neighborhood = prop.get('neighborhood', 'Não identificado')
            if neighborhood and neighborhood != 'Não identificado':
                neighborhood_data[neighborhood].append(prop)
        
        neighborhood_analysis = {}
        
        for neighborhood, props in neighborhood_data.items():
            if len(props) >= 2:  # Só analisa bairros com pelo menos 2 propriedades
                prices = [p['price'] for p in props if p.get('price')]
                areas = [p['area'] for p in props if p.get('area')]
                price_per_sqm = [p['price_per_sqm'] for p in props if p.get('price_per_sqm')]
                
                if prices:
                    neighborhood_analysis[neighborhood] = {
                        'total_properties': len(props),
                        'avg_price': statistics.mean(prices),
                        'median_price': statistics.median(prices),
                        'min_price': min(prices),
                        'max_price': max(prices),
                        'price_std': statistics.stdev(prices) if len(prices) > 1 else 0,
                        'avg_area': statistics.mean(areas) if areas else None,
                        'avg_price_per_sqm': statistics.mean(price_per_sqm) if price_per_sqm else None,
                        'property_types': Counter([p.get('property_type', 'N/A') for p in props]),
                        'bedrooms_distribution': Counter([p.get('bedrooms', 0) for p in props]),
                        'sample_properties': props[:3]  # Primeiras 3 para exemplos
                    }
        
        # Ordena por preço médio
        sorted_neighborhoods = dict(sorted(
            neighborhood_analysis.items(),
            key=lambda x: x[1]['avg_price'],
            reverse=True
        ))
        
        self.analysis_results['neighborhood_analysis'] = sorted_neighborhoods
        return sorted_neighborhoods
    
    def detect_opportunities(self, discount_threshold: float = 0.15) -> List[Dict[str, Any]]:
        """Detecta oportunidades de compra abaixo do preço médio"""
        if not self.properties:
            return []
        
        # Calcula preço médio geral por m²
        valid_price_per_sqm = [p['price_per_sqm'] for p in self.properties if p.get('price_per_sqm')]
        avg_price_per_sqm = statistics.mean(valid_price_per_sqm) if valid_price_per_sqm else 0
        
        # Calcula preço médio por tipo de propriedade
        type_avg_prices = {}
        for prop_type in set([p.get('property_type', 'N/A') for p in self.properties]):
            type_props = [p for p in self.properties if p.get('property_type') == prop_type]
            type_prices = [p['price_per_sqm'] for p in type_props if p.get('price_per_sqm')]
            if type_prices:
                type_avg_prices[prop_type] = statistics.mean(type_prices)
        
        opportunities = []
        
        for prop in self.properties:
            if not prop.get('price_per_sqm'):
                continue
            
            prop_type = prop.get('property_type', 'N/A')
            prop_price_per_sqm = prop['price_per_sqm']
            
            # Compara com média do tipo de propriedade
            type_avg = type_avg_prices.get(prop_type, avg_price_per_sqm)
            discount = (type_avg - prop_price_per_sqm) / type_avg
            
            if discount >= discount_threshold:
                opportunity_score = min(discount * 100, 50)  # Score máximo de 50
                
                opportunities.append({
                    'property': prop,
                    'discount_percentage': round(discount * 100, 1),
                    'savings_amount': round((type_avg - prop_price_per_sqm) * prop.get('area', 0), 2),
                    'opportunity_score': round(opportunity_score, 1),
                    'market_avg_price_per_sqm': round(type_avg, 2),
                    'property_price_per_sqm': round(prop_price_per_sqm, 2),
                    'analysis_reason': f"Preço {discount*100:.1f}% abaixo da média de {prop_type}"
                })
        
        # Ordena por score de oportunidade
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        self.analysis_results['opportunities'] = opportunities
        return opportunities
    
    def calculate_roi_metrics(self, estimated_rent_yield: float = 0.006) -> Dict[str, Any]:
        """Calcula métricas de ROI e potencial de valorização"""
        roi_analysis = {
            'rent_yield_analysis': [],
            'price_efficiency': [],
            'investment_recommendations': []
        }
        
        for prop in self.properties:
            if not prop.get('price') or not prop.get('area'):
                continue
            
            # Estimativa de aluguel mensal (0.6% do valor do imóvel por mês)
            estimated_monthly_rent = prop['price'] * estimated_rent_yield
            annual_rent = estimated_monthly_rent * 12
            rental_yield = (annual_rent / prop['price']) * 100
            
            # Payback period (tempo para recuperar investimento)
            payback_years = prop['price'] / annual_rent if annual_rent > 0 else float('inf')
            
            # Score de eficiência de preço (baseado em área e localização)
            area_score = min(prop['area'] / 100, 1.0)  # Normaliza área
            price_per_sqm = prop.get('price_per_sqm', 0)
            
            # Score composto
            efficiency_score = (area_score * 0.3 + 
                              min(rental_yield / 8, 1.0) * 0.4 +  # 8% yield = score máximo
                              (1 - min(price_per_sqm / 15000, 1.0)) * 0.3) * 100
            
            roi_data = {
                'property': prop,
                'estimated_monthly_rent': round(estimated_monthly_rent, 2),
                'annual_rent': round(annual_rent, 2),
                'rental_yield_percent': round(rental_yield, 2),
                'payback_years': round(payback_years, 1) if payback_years != float('inf') else None,
                'efficiency_score': round(efficiency_score, 1),
                'recommendation': self._get_investment_recommendation(rental_yield, payback_years, efficiency_score)
            }
            
            roi_analysis['rent_yield_analysis'].append(roi_data)
        
        # Ordena por yield de aluguel
        roi_analysis['rent_yield_analysis'].sort(key=lambda x: x['rental_yield_percent'], reverse=True)
        
        self.analysis_results['roi_metrics'] = roi_analysis
        return roi_analysis
    
    def _get_investment_recommendation(self, yield_pct: float, payback: float, efficiency: float) -> str:
        """Gera recomendação de investimento baseada nas métricas"""
        if yield_pct >= 8 and payback <= 12 and efficiency >= 70:
            return "EXCELENTE - Alto potencial de retorno"
        elif yield_pct >= 6 and payback <= 15 and efficiency >= 60:
            return "BOM - Investimento sólido"
        elif yield_pct >= 4 and payback <= 20 and efficiency >= 50:
            return "MODERADO - Considerar outros fatores"
        else:
            return "BAIXO - Não recomendado para renda"
    
    def generate_market_trends(self) -> Dict[str, Any]:
        """Gera análise de tendências de mercado"""
        trends = {
            'price_distribution': {},
            'area_analysis': {},
            'property_type_trends': {},
            'market_summary': {}
        }
        
        if not self.properties:
            return trends
        
        # Distribuição de preços
        prices = [p['price'] for p in self.properties if p.get('price')]
        if prices:
            trends['price_distribution'] = {
                'total_properties': len(prices),
                'average_price': round(statistics.mean(prices), 2),
                'median_price': round(statistics.median(prices), 2),
                'price_range': {
                    'min': min(prices),
                    'max': max(prices),
                    'std_deviation': round(statistics.stdev(prices) if len(prices) > 1 else 0, 2)
                },
                'price_brackets': {
                    'budget': len([p for p in prices if p <= 400000]),  # Até 400k
                    'mid_range': len([p for p in prices if 400000 < p <= 800000]),  # 400k-800k
                    'premium': len([p for p in prices if 800000 < p <= 1500000]),  # 800k-1.5M
                    'luxury': len([p for p in prices if p > 1500000])  # Acima 1.5M
                }
            }
        
        # Análise de área
        areas = [p['area'] for p in self.properties if p.get('area')]
        if areas:
            trends['area_analysis'] = {
                'average_area': round(statistics.mean(areas), 1),
                'median_area': round(statistics.median(areas), 1),
                'area_brackets': {
                    'compact': len([a for a in areas if a <= 60]),  # Até 60m²
                    'standard': len([a for a in areas if 60 < a <= 100]),  # 60-100m²
                    'spacious': len([a for a in areas if 100 < a <= 150]),  # 100-150m²
                    'large': len([a for a in areas if a > 150])  # Acima 150m²
                }
            }
        
        # Tendências por tipo de propriedade
        type_counter = Counter([p.get('property_type', 'N/A') for p in self.properties])
        type_prices = {}
        
        for prop_type in type_counter.keys():
            type_props = [p for p in self.properties if p.get('property_type') == prop_type]
            type_price_list = [p['price'] for p in type_props if p.get('price')]
            type_area_list = [p['area'] for p in type_props if p.get('area')]
            
            if type_price_list:
                type_prices[prop_type] = {
                    'count': len(type_props),
                    'avg_price': round(statistics.mean(type_price_list), 2),
                    'avg_area': round(statistics.mean(type_area_list), 1) if type_area_list else None,
                    'price_per_sqm': round(statistics.mean([p['price_per_sqm'] for p in type_props if p.get('price_per_sqm')]), 2)
                }
        
        trends['property_type_trends'] = type_prices
        
        # Resumo do mercado
        price_per_sqm_list = [p['price_per_sqm'] for p in self.properties if p.get('price_per_sqm')]
        trends['market_summary'] = {
            'total_analyzed_properties': len(self.properties),
            'avg_price_per_sqm': round(statistics.mean(price_per_sqm_list), 2) if price_per_sqm_list else 0,
            'market_liquidity': len(self.properties),  # Número de propriedades disponíveis
            'diversity_index': len(type_counter),  # Variedade de tipos de propriedade
            'most_common_type': type_counter.most_common(1)[0] if type_counter else None
        }
        
        self.analysis_results['market_trends'] = trends
        return trends
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Gera relatório completo de análise de mercado"""
        self.logger.info("Gerando relatório completo de análise de mercado...")
        
        # Executa todas as análises
        neighborhood_analysis = self.analyze_by_neighborhood()
        opportunities = self.detect_opportunities()
        roi_metrics = self.calculate_roi_metrics()
        market_trends = self.generate_market_trends()
        
        # Compila relatório final
        report = {
            'analysis_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_properties_analyzed': len(self.properties),
                'analysis_version': '1.0'
            },
            'executive_summary': self._generate_executive_summary(),
            'neighborhood_analysis': neighborhood_analysis,
            'investment_opportunities': opportunities[:10],  # Top 10 oportunidades
            'roi_metrics': roi_metrics,
            'market_trends': market_trends,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Gera resumo executivo da análise"""
        if not self.properties:
            return {}
        
        prices = [p['price'] for p in self.properties if p.get('price')]
        areas = [p['area'] for p in self.properties if p.get('area')]
        
        return {
            'market_overview': f"Análise de {len(self.properties)} propriedades no mercado de São Paulo",
            'price_range': f"R$ {min(prices):,.0f} - R$ {max(prices):,.0f}" if prices else "N/A",
            'average_price': f"R$ {statistics.mean(prices):,.0f}" if prices else "N/A",
            'average_area': f"{statistics.mean(areas):.0f} m²" if areas else "N/A",
            'total_opportunities': len(self.analysis_results.get('opportunities', [])),
            'neighborhoods_analyzed': len(self.analysis_results.get('neighborhood_analysis', {})),
            'market_activity': "Ativo" if len(self.properties) > 15 else "Moderado"
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Análise de oportunidades
        opportunities = self.analysis_results.get('opportunities', [])
        if opportunities:
            best_opportunity = opportunities[0]
            recommendations.append(
                f"OPORTUNIDADE DESTAQUE: {best_opportunity['property'].get('property_type', 'Propriedade')} "
                f"com desconto de {best_opportunity['discount_percentage']}% em "
                f"{best_opportunity['property'].get('neighborhood', 'localização premium')}"
            )
        
        # Análise de bairros
        neighborhood_analysis = self.analysis_results.get('neighborhood_analysis', {})
        if neighborhood_analysis:
            best_value_neighborhood = min(
                neighborhood_analysis.items(),
                key=lambda x: x[1]['avg_price_per_sqm'] if x[1]['avg_price_per_sqm'] else float('inf')
            )
            recommendations.append(
                f"MELHOR CUSTO-BENEFÍCIO: {best_value_neighborhood[0]} "
                f"com preço médio de R$ {best_value_neighborhood[1]['avg_price_per_sqm']:,.0f}/m²"
            )
        
        # Análise de ROI
        roi_metrics = self.analysis_results.get('roi_metrics', {})
        if roi_metrics and roi_metrics.get('rent_yield_analysis'):
            best_yield = roi_metrics['rent_yield_analysis'][0]
            if best_yield['rental_yield_percent'] >= 6:
                recommendations.append(
                    f"MELHOR INVESTIMENTO PARA RENDA: "
                    f"{best_yield['property'].get('property_type', 'Propriedade')} "
                    f"com yield de {best_yield['rental_yield_percent']}% ao ano"
                )
        
        # Tendências gerais
        market_trends = self.analysis_results.get('market_trends', {})
        if market_trends.get('market_summary'):
            avg_price_per_sqm = market_trends['market_summary'].get('avg_price_per_sqm', 0)
            if avg_price_per_sqm < 8000:
                recommendations.append("MERCADO ACESSÍVEL: Preços por m² abaixo da média da região metropolitana")
            elif avg_price_per_sqm > 12000:
                recommendations.append("MERCADO PREMIUM: Foco em propriedades de alto padrão")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = 'market_analysis_report.json') -> bool:
        """Salva o relatório em arquivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Relatório salvo em '{filename}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {e}")
            return False
