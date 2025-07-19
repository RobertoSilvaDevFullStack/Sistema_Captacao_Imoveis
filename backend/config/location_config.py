#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Configuração de Localizações para Scrapers
Permite buscar imóveis em qualquer estado/cidade do Brasil
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class Location:
    """Configuração de localização para busca"""
    name: str
    state: str
    state_code: str
    olx_path: str
    vivareal_path: str
    zapimoveis_path: str

class LocationConfig:
    """Configurador de localizações para os scrapers"""
    
    def __init__(self):
        self.locations = self._load_locations()
    
    def _load_locations(self) -> Dict[str, Location]:
        """Carrega configurações de localizações"""
        locations = {
            # Rio de Janeiro
            'rio_de_janeiro': Location(
                name='Rio de Janeiro',
                state='Rio de Janeiro',
                state_code='rj',
                olx_path='rj/rio-de-janeiro-e-regiao',
                vivareal_path='rio-de-janeiro',
                zapimoveis_path='rj+rio-de-janeiro'
            ),
            
            # São Paulo
            'sao_paulo': Location(
                name='São Paulo',
                state='São Paulo',
                state_code='sp',
                olx_path='sp/sao-paulo-e-regiao',
                vivareal_path='sao-paulo',
                zapimoveis_path='sp+sao-paulo'
            ),
            
            # Belo Horizonte
            'belo_horizonte': Location(
                name='Belo Horizonte',
                state='Minas Gerais',
                state_code='mg',
                olx_path='mg/belo-horizonte-e-regiao',
                vivareal_path='minas-gerais/belo-horizonte',
                zapimoveis_path='mg+belo-horizonte'
            ),
            
            # Brasília
            'brasilia': Location(
                name='Brasília',
                state='Distrito Federal',
                state_code='df',
                olx_path='df/distrito-federal-e-regiao',
                vivareal_path='distrito-federal/brasilia',
                zapimoveis_path='df+brasilia'
            ),
            
            # Salvador
            'salvador': Location(
                name='Salvador',
                state='Bahia',
                state_code='ba',
                olx_path='ba/salvador-e-regiao',
                vivareal_path='bahia/salvador',
                zapimoveis_path='ba+salvador'
            ),
            
            # Fortaleza
            'fortaleza': Location(
                name='Fortaleza',
                state='Ceará',
                state_code='ce',
                olx_path='ce/fortaleza-e-regiao',
                vivareal_path='ceara/fortaleza',
                zapimoveis_path='ce+fortaleza'
            ),
            
            # Recife
            'recife': Location(
                name='Recife',
                state='Pernambuco',
                state_code='pe',
                olx_path='pe/recife-e-regiao',
                vivareal_path='pernambuco/recife',
                zapimoveis_path='pe+recife'
            ),
            
            # Porto Alegre
            'porto_alegre': Location(
                name='Porto Alegre',
                state='Rio Grande do Sul',
                state_code='rs',
                olx_path='rs/porto-alegre-e-regiao',
                vivareal_path='rio-grande-do-sul/porto-alegre',
                zapimoveis_path='rs+porto-alegre'
            ),
            
            # Curitiba
            'curitiba': Location(
                name='Curitiba',
                state='Paraná',
                state_code='pr',
                olx_path='pr/curitiba-e-regiao',
                vivareal_path='parana/curitiba',
                zapimoveis_path='pr+curitiba'
            ),
            
            # Florianópolis
            'florianopolis': Location(
                name='Florianópolis',
                state='Santa Catarina',
                state_code='sc',
                olx_path='sc/grande-florianopolis',
                vivareal_path='santa-catarina/florianopolis',
                zapimoveis_path='sc+florianopolis'
            )
        }
        
        return locations
    
    def get_location(self, location_key: str) -> Optional[Location]:
        """Obtém configuração de uma localização"""
        return self.locations.get(location_key)
    
    def list_locations(self) -> List[str]:
        """Lista todas as localizações disponíveis"""
        return list(self.locations.keys())
    
    def get_location_display_names(self) -> Dict[str, str]:
        """Retorna nomes de exibição das localizações"""
        return {key: loc.name for key, loc in self.locations.items()}
    
    def build_urls(self, location_key: str, property_type: str = 'apartamentos') -> Dict[str, str]:
        """Constrói URLs para os scrapers baseado na localização"""
        location = self.get_location(location_key)
        if not location:
            raise ValueError(f"Localização '{location_key}' não encontrada")
        
        # Mapear tipos de imóveis
        property_mapping = {
            'apartamentos': {
                'olx': 'apartamentos',
                'vivareal': 'apartamento',
                'zapimoveis': 'apartamentos'
            },
            'casas': {
                'olx': 'casas',
                'vivareal': 'casa',
                'zapimoveis': 'casas'
            },
            'todos': {
                'olx': 'imoveis',
                'vivareal': '',
                'zapimoveis': ''
            }
        }
        
        prop_types = property_mapping.get(property_type, property_mapping['apartamentos'])
        
        urls = {
            'olx': f"https://www.olx.com.br/imoveis/venda/{prop_types['olx']}/estado-{location.state_code}",
            'vivareal': f"https://www.vivareal.com.br/venda/{location.vivareal_path}/{prop_types['vivareal']}/",
            'zapimoveis': f"https://www.zapimoveis.com.br/venda/{prop_types['zapimoveis']}/{location.zapimoveis_path}/"
        }
        
        return urls
    
    def add_custom_location(self, key: str, location: Location):
        """Adiciona uma localização customizada"""
        self.locations[key] = location
    
    def save_locations_to_file(self, filepath: str):
        """Salva configurações em arquivo JSON"""
        data = {}
        for key, loc in self.locations.items():
            data[key] = {
                'name': loc.name,
                'state': loc.state,
                'state_code': loc.state_code,
                'olx_path': loc.olx_path,
                'vivareal_path': loc.vivareal_path,
                'zapimoveis_path': loc.zapimoveis_path
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_locations_from_file(self, filepath: str):
        """Carrega configurações de arquivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for key, loc_data in data.items():
                self.locations[key] = Location(
                    name=loc_data['name'],
                    state=loc_data['state'],
                    state_code=loc_data['state_code'],
                    olx_path=loc_data['olx_path'],
                    vivareal_path=loc_data['vivareal_path'],
                    zapimoveis_path=loc_data['zapimoveis_path']
                )
        except FileNotFoundError:
            pass  # Usar configurações padrão
