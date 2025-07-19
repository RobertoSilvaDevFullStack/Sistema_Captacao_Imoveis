#!/usr/bin/env python3
# advanced_market_insights.py

import json
import logging
import statistics
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

class AdvancedMarketInsights:
    """Classe para insights avançados de mercado imobiliário"""
    
    def __init__(self, analyzer_data: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.data = analyzer_data
        self.properties = analyzer_data.get('properties', [])
    
    def calculate_market_heat_index(self) -> Dict[str, Any]:
        """Calcula índice de aquecimento do mercado por região"""
        neighborhood_heat = {}
        
        neighborhood_analysis = self.data.get('neighborhood_analysis', {})
        
        for neighborhood, data in neighborhood_analysis.items():
            # Fatores para cálculo do índice de aquecimento
            property_count = data.get('total_properties', 0)
            price_variation = data.get('price_std', 0) / data.get('avg_price', 1) if data.get('avg_price') else 0
            avg_price_per_sqm = data.get('avg_price_per_sqm', 0)
            
            # Normaliza fatores (0-100)
            volume_score = min(property_count * 10, 100)  # Volume de propriedades
            stability_score = max(100 - (price_variation * 1000), 0)  # Estabilidade de preços
            value_score = min(avg_price_per_sqm / 150, 100) if avg_price_per_sqm else 0  # Valor por m²
            
            # Índice composto
            heat_index = (volume_score * 0.3 + stability_score * 0.4 + value_score * 0.3)
            
            # Classificação
            if heat_index >= 80:
                classification = "MUITO QUENTE - Alta demanda e valorização"
            elif heat_index >= 60:
                classification = "QUENTE - Mercado ativo"
            elif heat_index >= 40:
                classification = "MORNO - Mercado estável"
            else:
                classification = "FRIO - Baixa atividade"
            
            neighborhood_heat[neighborhood] = {
                'heat_index': round(heat_index, 1),
                'classification': classification,
                'volume_score': round(volume_score, 1),
                'stability_score': round(stability_score, 1),
                'value_score': round(value_score, 1),
                'property_count': property_count,
                'avg_price_per_sqm': avg_price_per_sqm
            }
        
        # Ordena por índice de aquecimento
        sorted_heat = dict(sorted(
            neighborhood_heat.items(),
            key=lambda x: x[1]['heat_index'],
            reverse=True
        ))
        
        return sorted_heat
    
    def analyze_investment_diversification(self) -> Dict[str, Any]:
        """Analisa oportunidades de diversificação de portfólio"""
        diversification_analysis = {
            'by_property_type': {},
            'by_price_range': {},
            'by_neighborhood': {},
            'portfolio_recommendations': []
        }
        
        # Análise por tipo de propriedade
        type_data = defaultdict(list)
        for prop in self.properties:
            prop_type = prop.get('property_type', 'N/A')
            if prop_type != 'N/A':
                type_data[prop_type].append(prop)
        
        for prop_type, props in type_data.items():
            if len(props) > 0:
                prices = [p.get('price', 0) for p in props if p.get('price')]
                yields = [p.get('price_per_sqm', 0) for p in props if p.get('price_per_sqm')]
                
                if prices and yields:
                    diversification_analysis['by_property_type'][prop_type] = {
                        'count': len(props),
                        'avg_investment': round(statistics.mean(prices), 2),
                        'min_investment': min(prices),
                        'max_investment': max(prices),
                        'avg_price_per_sqm': round(statistics.mean(yields), 2),
                        'risk_level': self._calculate_risk_level(prices),
                        'liquidity_score': min(len(props) * 10, 100)  # Baseado na disponibilidade
                    }
        
        # Análise por faixa de preço
        price_ranges = {
            'entry_level': [p for p in self.properties if p.get('price', 0) <= 400000],
            'mid_range': [p for p in self.properties if 400000 < p.get('price', 0) <= 800000],
            'premium': [p for p in self.properties if 800000 < p.get('price', 0) <= 1500000],
            'luxury': [p for p in self.properties if p.get('price', 0) > 1500000]
        }
        
        for range_name, props in price_ranges.items():
            if props:
                areas = [p.get('area', 0) for p in props if p.get('area')]
                neighborhoods = [p.get('neighborhood') for p in props if p.get('neighborhood')]
                
                diversification_analysis['by_price_range'][range_name] = {
                    'count': len(props),
                    'avg_area': round(statistics.mean(areas), 1) if areas else 0,
                    'neighborhoods_available': len(set(neighborhoods)),
                    'diversity_score': len(set([p.get('property_type') for p in props]))
                }
        
        # Recomendações de portfólio
        total_properties = len(self.properties)
        if total_properties > 0:
            # Portfolio balanceado sugerido
            diversification_analysis['portfolio_recommendations'] = [
                {
                    'strategy': 'CONSERVADOR',
                    'allocation': {
                        'Apartamento': '60%',
                        'Casa': '30%',
                        'Sobrado': '10%'
                    },
                    'price_range_focus': 'mid_range',
                    'expected_yield': '5-7% ao ano',
                    'risk_level': 'Baixo'
                },
                {
                    'strategy': 'MODERADO',
                    'allocation': {
                        'Apartamento': '50%',
                        'Casa': '35%',
                        'Sobrado': '15%'
                    },
                    'price_range_focus': 'entry_level + mid_range',
                    'expected_yield': '6-9% ao ano',
                    'risk_level': 'Médio'
                },
                {
                    'strategy': 'AGRESSIVO',
                    'allocation': {
                        'Apartamento': '40%',
                        'Casa': '40%',
                        'Premium': '20%'
                    },
                    'price_range_focus': 'premium + luxury',
                    'expected_yield': '8-12% ao ano',
                    'risk_level': 'Alto'
                }
            ]
        
        return diversification_analysis
    
    def _calculate_risk_level(self, prices: List[float]) -> str:
        """Calcula nível de risco baseado na variabilidade de preços"""
        if len(prices) <= 1:
            return "INDEFINIDO"
        
        cv = statistics.stdev(prices) / statistics.mean(prices)  # Coeficiente de variação
        
        if cv <= 0.15:
            return "BAIXO"
        elif cv <= 0.30:
            return "MÉDIO"
        else:
            return "ALTO"
    
    def generate_comparative_analysis(self) -> Dict[str, Any]:
        """Gera análise comparativa detalhada"""
        comparative = {
            'best_value_properties': [],
            'growth_potential_areas': [],
            'yield_champions': [],
            'market_gaps': []
        }
        
        # Melhores valores (preço vs qualidade)
        for prop in self.properties:
            if prop.get('price') and prop.get('area') and prop.get('bedrooms'):
                # Score baseado em preço/m², área e quartos
                price_score = 100 - min((prop.get('price_per_sqm', 0) / 200), 100)
                area_score = min(prop.get('area', 0) / 2, 100)
                rooms_score = min(prop.get('bedrooms', 0) * 20, 100)
                
                value_score = (price_score * 0.4 + area_score * 0.3 + rooms_score * 0.3)
                
                if value_score >= 70:
                    comparative['best_value_properties'].append({
                        'property': prop,
                        'value_score': round(value_score, 1),
                        'price_score': round(price_score, 1),
                        'area_score': round(area_score, 1),
                        'rooms_score': round(rooms_score, 1)
                    })
        
        # Ordena por score de valor
        comparative['best_value_properties'].sort(
            key=lambda x: x['value_score'], reverse=True
        )
        
        # Áreas com potencial de crescimento (baixo preço/m², boa infraestrutura)
        neighborhood_analysis = self.data.get('neighborhood_analysis', {})
        avg_price_per_sqm_general = statistics.mean([
            data.get('avg_price_per_sqm', 0) 
            for data in neighborhood_analysis.values() 
            if data.get('avg_price_per_sqm')
        ]) if neighborhood_analysis else 0
        
        for neighborhood, data in neighborhood_analysis.items():
            price_per_sqm = data.get('avg_price_per_sqm', 0)
            property_count = data.get('total_properties', 0)
            
            # Potencial baseado em preço abaixo da média geral e volume de propriedades
            if price_per_sqm > 0 and price_per_sqm < avg_price_per_sqm_general * 0.8 and property_count >= 2:
                growth_potential = (
                    (avg_price_per_sqm_general - price_per_sqm) / avg_price_per_sqm_general * 100
                )
                
                comparative['growth_potential_areas'].append({
                    'neighborhood': neighborhood,
                    'current_price_per_sqm': price_per_sqm,
                    'market_avg_price_per_sqm': round(avg_price_per_sqm_general, 2),
                    'growth_potential_percentage': round(growth_potential, 1),
                    'property_count': property_count,
                    'avg_price': data.get('avg_price', 0)
                })
        
        # Ordena por potencial de crescimento
        comparative['growth_potential_areas'].sort(
            key=lambda x: x['growth_potential_percentage'], reverse=True
        )
        
        # Detecta lacunas no mercado
        type_counts = Counter([p.get('property_type') for p in self.properties if p.get('property_type')])
        bedroom_counts = Counter([p.get('bedrooms') for p in self.properties if p.get('bedrooms')])
        
        # Identifica tipos/configurações com poucas opções
        total_props = len(self.properties)
        for prop_type, count in type_counts.items():
            if count / total_props < 0.1 and prop_type != 'N/A':  # Menos de 10% do mercado
                comparative['market_gaps'].append({
                    'gap_type': 'property_type',
                    'description': f"Baixa oferta de {prop_type}",
                    'current_count': count,
                    'market_share_percentage': round((count / total_props) * 100, 1),
                    'opportunity': f"Nicho de mercado com potencial para {prop_type}"
                })
        
        return comparative
    
    def calculate_investment_scenarios(self, initial_budget: float = 500000) -> Dict[str, Any]:
        """Calcula cenários de investimento para diferentes estratégias"""
        scenarios = {
            'budget': initial_budget,
            'single_property_scenarios': [],
            'portfolio_scenarios': [],
            'risk_return_analysis': {}
        }
        
        # Cenários de propriedade única
        suitable_properties = [
            p for p in self.properties 
            if p.get('price', 0) <= initial_budget and p.get('price', 0) > 0
        ]
        
        if suitable_properties:
            # Ordena por diferentes critérios
            by_yield = sorted(
                suitable_properties, 
                key=lambda x: x.get('price_per_sqm', float('inf'))
            )[:5]
            
            by_area = sorted(
                suitable_properties,
                key=lambda x: x.get('area', 0),
                reverse=True
            )[:5]
            
            scenarios['single_property_scenarios'] = [
                {
                    'strategy': 'MAXIMIZAR ÁREA',
                    'properties': by_area,
                    'rationale': 'Foco em maior espaço pelo orçamento'
                },
                {
                    'strategy': 'MELHOR PREÇO/M²',
                    'properties': by_yield,
                    'rationale': 'Foco em melhor custo-benefício'
                }
            ]
        
        # Cenários de portfólio (múltiplas propriedades)
        budget_ranges = [
            {'min': 0, 'max': initial_budget * 0.4, 'label': 'ENTRADA'},
            {'min': initial_budget * 0.4, 'max': initial_budget * 0.7, 'label': 'MÉDIO'},
            {'min': initial_budget * 0.7, 'max': initial_budget, 'label': 'PREMIUM'}
        ]
        
        for budget_range in budget_ranges:
            suitable_for_range = [
                p for p in self.properties
                if budget_range['min'] <= p.get('price', 0) <= budget_range['max']
            ]
            
            if suitable_for_range:
                avg_price = statistics.mean([p.get('price', 0) for p in suitable_for_range])
                possible_count = int(initial_budget / avg_price) if avg_price > 0 else 0
                
                scenarios['portfolio_scenarios'].append({
                    'range_label': budget_range['label'],
                    'price_range': f"R$ {budget_range['min']:,.0f} - R$ {budget_range['max']:,.0f}",
                    'avg_property_price': round(avg_price, 2),
                    'possible_property_count': possible_count,
                    'total_investment': round(avg_price * possible_count, 2),
                    'remaining_budget': round(initial_budget - (avg_price * possible_count), 2),
                    'diversification_benefit': 'Alto' if possible_count >= 3 else 'Médio' if possible_count == 2 else 'Baixo'
                })
        
        return scenarios
    
    def export_insights_summary(self, filename: str = 'advanced_market_insights.json') -> Dict[str, Any]:
        """Exporta resumo completo dos insights avançados"""
        summary = {
            'market_heat_index': self.calculate_market_heat_index(),
            'investment_diversification': self.analyze_investment_diversification(),
            'comparative_analysis': self.generate_comparative_analysis(),
            'investment_scenarios_500k': self.calculate_investment_scenarios(500000),
            'investment_scenarios_1m': self.calculate_investment_scenarios(1000000),
            'generation_timestamp': time.time()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Insights avançados exportados para '{filename}'")
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar insights: {e}")
            return {}
