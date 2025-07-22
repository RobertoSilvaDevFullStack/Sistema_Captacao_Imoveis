# backend/api_integrations/registry_apis.py
"""
Integração com APIs de Cartórios e Registro de Imóveis
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
import time
import hashlib

class RegistryAPIs:
    """Cliente para APIs de cartórios e registro de imóveis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # URLs de cartórios e serviços de registro
        self.registry_services = {
            'nacional': {
                'srei_url': 'https://www.registradores.org.br',  # Colégio de Registradores
                'cni_url': 'https://www.cni.org.br',  # Central Nacional de Informações
                'irib_url': 'https://www.irib.org.br'  # Instituto de Registro Imobiliário
            },
            'sao_paulo': {
                'arisp_url': 'https://www.arisp.com.br',  # Associação dos Registradores SP
                'tabelionato_url': 'https://www.tabelionato.com.br'
            },
            'rio_de_janeiro': {
                'anoreg_url': 'https://www.anoreg-rj.org.br'  # Associação dos Notários RJ
            }
        }
        
        self.request_delay = 1.0  # 1 segundo entre requests
        self.last_request_time = {}
    
    async def search_property_registry(self, address: str, city: str, state: str) -> Optional[Dict[str, Any]]:
        """Busca registro do imóvel"""
        try:
            await self._rate_limit('registry_search')
            
            # Em implementação real, integrar com sistemas de cartórios
            # Por enquanto, simular dados estruturados
            
            registry_data = {
                'registry_office': self._get_registry_office(city, state),
                'property_registration': self._generate_property_registration(address, city),
                'ownership_history': await self._get_ownership_history(address),
                'encumbrances': await self._get_encumbrances(address),
                'legal_status': await self._check_legal_status(address),
                'documentation': await self._get_documentation_status(address),
                'taxes_status': await self._get_taxes_status(address)
            }
            
            return registry_data
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar registro do imóvel: {e}")
        
        return None
    
    async def get_ownership_history(self, property_id: str) -> List[Dict[str, Any]]:
        """Busca histórico de propriedade"""
        try:
            await self._rate_limit('ownership_history')
            
            # Simular histórico de propriedade
            history = []
            
            # Gerar 2-5 transações históricas
            num_transactions = 2 + (hash(property_id) % 4)
            
            for i in range(num_transactions):
                transaction = {
                    'transaction_id': f"TXN{hash(property_id + str(i)) % 1000000:06d}",
                    'date': f"20{15 + i:02d}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                    'transaction_type': self._get_transaction_type(i),
                    'value': 300000 + (i * 50000) + (hash(property_id) % 100000),
                    'buyer': self._generate_person_name(f"buyer_{i}"),
                    'seller': self._generate_person_name(f"seller_{i}") if i > 0 else "Incorporadora Original",
                    'registry_number': f"REG{hash(property_id + str(i)) % 100000:05d}",
                    'notary': self._get_notary_info(i)
                }
                history.append(transaction)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar histórico de propriedade: {e}")
        
        return []
    
    async def check_encumbrances(self, property_id: str) -> List[Dict[str, Any]]:
        """Verifica ônus e gravames"""
        try:
            await self._rate_limit('encumbrances')
            
            encumbrances = []
            
            # Simular possíveis ônus baseado no hash do property_id
            property_hash = hash(property_id)
            
            # 30% chance de ter financiamento
            if property_hash % 10 < 3:
                encumbrances.append({
                    'type': 'financing',
                    'creditor': 'Banco do Brasil S.A.',
                    'amount': 450000.00,
                    'registration_date': '2022-03-15',
                    'status': 'active',
                    'details': 'Financiamento habitacional - SFH'
                })
            
            # 10% chance de ter penhora
            if property_hash % 10 < 1:
                encumbrances.append({
                    'type': 'seizure',
                    'creditor': 'União Federal',
                    'amount': 85000.00,
                    'registration_date': '2023-01-10',
                    'status': 'active',
                    'details': 'Execução fiscal - débitos tributários'
                })
            
            # 5% chance de ter usufruto
            if property_hash % 20 < 1:
                encumbrances.append({
                    'type': 'usufruct',
                    'beneficiary': 'Maria da Silva Santos',
                    'registration_date': '2020-08-20',
                    'status': 'active',
                    'details': 'Usufruto vitalício'
                })
            
            return encumbrances
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar ônus: {e}")
        
        return []
    
    async def get_legal_documentation(self, property_id: str) -> Dict[str, Any]:
        """Busca documentação legal"""
        try:
            await self._rate_limit('legal_docs')
            
            # Simular status da documentação
            property_hash = hash(property_id)
            
            documentation = {
                'registry_status': 'regular' if property_hash % 10 < 9 else 'irregular',
                'habite_se': {
                    'number': f"HS{property_hash % 100000:05d}",
                    'issue_date': '2021-12-15',
                    'status': 'valid'
                },
                'building_permit': {
                    'number': f"AL{property_hash % 100000:05d}",
                    'issue_date': '2020-03-10',
                    'status': 'valid'
                },
                'property_tax_certificate': {
                    'status': 'up_to_date' if property_hash % 10 < 8 else 'pending',
                    'last_payment': '2024-01-15'
                },
                'condominium_documentation': {
                    'convention': 'registered',
                    'minutes_up_to_date': True,
                    'debts': property_hash % 10 < 2  # 20% chance de ter dívidas
                },
                'environmental_licenses': {
                    'required': property_hash % 5 < 1,  # 20% precisam
                    'status': 'compliant' if property_hash % 10 < 9 else 'pending'
                }
            }
            
            return documentation
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar documentação: {e}")
        
        return {}
    
    async def verify_property_authenticity(self, property_id: str, address: str) -> Dict[str, Any]:
        """Verifica autenticidade do imóvel"""
        try:
            await self._rate_limit('authenticity_check')
            
            property_hash = hash(property_id + address)
            
            authenticity = {
                'verification_score': 0.85 + (property_hash % 100) / 1000,  # 85-95%
                'verified_elements': {
                    'address_exists': True,
                    'registry_match': property_hash % 10 < 9,  # 90% match
                    'ownership_clear': property_hash % 10 < 8,  # 80% clear
                    'documentation_complete': property_hash % 10 < 7,  # 70% complete
                    'no_litigation': property_hash % 10 < 9  # 90% no litigation
                },
                'risk_factors': [],
                'recommendations': []
            }
            
            # Adicionar fatores de risco baseado nos elementos verificados
            if not authenticity['verified_elements']['registry_match']:
                authenticity['risk_factors'].append("Divergência entre endereço e registro")
                authenticity['recommendations'].append("Verificar documentação no cartório")
            
            if not authenticity['verified_elements']['ownership_clear']:
                authenticity['risk_factors'].append("Propriedade com pendências")
                authenticity['recommendations'].append("Solicitar certidão negativa de ônus")
            
            if not authenticity['verified_elements']['no_litigation']:
                authenticity['risk_factors'].append("Possível litígio em andamento")
                authenticity['recommendations'].append("Consultar tribunal de justiça")
            
            return authenticity
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de autenticidade: {e}")
        
        return {}
    
    async def get_property_valuation_history(self, property_id: str) -> List[Dict[str, Any]]:
        """Busca histórico de avaliações"""
        try:
            await self._rate_limit('valuation_history')
            
            property_hash = hash(property_id)
            base_value = 400000 + (property_hash % 500000)
            
            valuations = []
            
            # Gerar 3-7 avaliações históricas
            num_valuations = 3 + (property_hash % 5)
            
            for i in range(num_valuations):
                year = 2024 - i
                # Crescimento/decrescimento aleatório baseado no hash
                variation = 1 + ((property_hash + i) % 20 - 10) / 100  # -10% a +10%
                value = base_value * (0.95 ** i) * variation  # Deprecia com o tempo
                
                valuation = {
                    'date': f"{year}-{(i % 12) + 1:02d}-15",
                    'value': round(value, 2),
                    'evaluator': self._get_evaluator_name(i),
                    'method': self._get_valuation_method(i),
                    'purpose': self._get_valuation_purpose(i),
                    'market_conditions': self._get_market_conditions(year)
                }
                valuations.append(valuation)
            
            return valuations
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar histórico de avaliações: {e}")
        
        return []
    
    # Métodos auxiliares privados
    def _get_registry_office(self, city: str, state: str) -> Dict[str, Any]:
        """Informações do cartório responsável"""
        return {
            'name': f"{1 + (hash(city) % 10)}º Cartório de Registro de Imóveis de {city}",
            'address': f"Rua do Cartório, {100 + (hash(city) % 900)} - Centro - {city}/{state}",
            'registrar': self._generate_person_name(f"registrar_{city}"),
            'phone': f"({11 + (hash(state) % 80):02d}) 3{hash(city) % 1000:03d}-{hash(city + state) % 10000:04d}",
            'email': f"cartorio{1 + (hash(city) % 10)}@{city.lower().replace(' ', '')}.org.br"
        }
    
    def _generate_property_registration(self, address: str, city: str) -> Dict[str, Any]:
        """Gera dados de registro do imóvel"""
        reg_hash = hash(address + city)
        
        return {
            'registration_number': f"REG{reg_hash % 1000000:06d}",
            'registration_date': f"20{15 + (reg_hash % 8):02d}-{(reg_hash % 12) + 1:02d}-{(reg_hash % 28) + 1:02d}",
            'book_number': f"Livro {2 + (reg_hash % 50):02d}",
            'page_number': f"Folha {1 + (reg_hash % 500):03d}",
            'area_m2': 80 + (reg_hash % 150),  # 80-230 m²
            'built_area_m2': 60 + (reg_hash % 120),  # 60-180 m²
            'property_type': 'Apartamento' if reg_hash % 3 < 2 else 'Casa',
            'description': f"Imóvel localizado em {address}, {city}"
        }
    
    async def _get_ownership_history(self, address: str) -> List[Dict[str, Any]]:
        """Histórico de propriedade simplificado"""
        return await self.get_ownership_history(str(hash(address)))
    
    async def _get_encumbrances(self, address: str) -> List[Dict[str, Any]]:
        """Ônus e gravames simplificados"""
        return await self.check_encumbrances(str(hash(address)))
    
    async def _check_legal_status(self, address: str) -> str:
        """Status legal do imóvel"""
        status_options = ['regular', 'irregular', 'pendente', 'em_regularização']
        weights = [80, 10, 5, 5]  # 80% regular, 10% irregular, etc.
        
        addr_hash = hash(address) % 100
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if addr_hash < cumulative:
                return status_options[i]
        
        return 'regular'
    
    async def _get_documentation_status(self, address: str) -> Dict[str, str]:
        """Status da documentação"""
        return {
            'certidao_negativa': 'valid',
            'escritura': 'registered',
            'habite_se': 'valid',
            'iptu': 'up_to_date'
        }
    
    async def _get_taxes_status(self, address: str) -> Dict[str, Any]:
        """Status de impostos"""
        addr_hash = hash(address)
        
        return {
            'iptu_status': 'up_to_date' if addr_hash % 10 < 8 else 'pending',
            'last_payment': f"2024-{(addr_hash % 12) + 1:02d}-15",
            'pending_amount': 0 if addr_hash % 10 < 8 else 1200 + (addr_hash % 2000),
            'installments_available': True
        }
    
    def _get_transaction_type(self, index: int) -> str:
        """Tipo de transação baseado no índice"""
        types = ['purchase', 'inheritance', 'donation', 'exchange']
        return types[index % len(types)]
    
    def _generate_person_name(self, seed: str) -> str:
        """Gera nome de pessoa baseado em seed"""
        first_names = ['João', 'Maria', 'José', 'Ana', 'Carlos', 'Luiza', 'Pedro', 'Sofia']
        last_names = ['Silva', 'Santos', 'Oliveira', 'Souza', 'Pereira', 'Costa', 'Ferreira', 'Almeida']
        
        name_hash = hash(seed)
        first = first_names[name_hash % len(first_names)]
        last = last_names[(name_hash // len(first_names)) % len(last_names)]
        
        return f"{first} {last}"
    
    def _get_notary_info(self, index: int) -> Dict[str, str]:
        """Informações do tabelião"""
        notaries = [
            "Dra. Maria Fernanda Teixeira",
            "Dr. Carlos Alberto Santos",
            "Dra. Ana Paula Oliveira",
            "Dr. João Pedro Silva"
        ]
        
        return {
            'name': notaries[index % len(notaries)],
            'registry': f"CNT{1000 + index:04d}"
        }
    
    def _get_evaluator_name(self, index: int) -> str:
        """Nome do avaliador"""
        evaluators = [
            "CRECI Avaliações Ltda",
            "Imovel Expert Consultoria",
            "Avalia Mais Engenharia",
            "Precisão Imobiliária"
        ]
        return evaluators[index % len(evaluators)]
    
    def _get_valuation_method(self, index: int) -> str:
        """Método de avaliação"""
        methods = ['comparativo_direto', 'custo_reproducao', 'renda', 'evolutivo']
        return methods[index % len(methods)]
    
    def _get_valuation_purpose(self, index: int) -> str:
        """Finalidade da avaliação"""
        purposes = ['financiamento', 'seguro', 'judicial', 'garantia']
        return purposes[index % len(purposes)]
    
    def _get_market_conditions(self, year: int) -> str:
        """Condições de mercado por ano"""
        conditions = {
            2024: 'estável',
            2023: 'aquecido',
            2022: 'muito_aquecido',
            2021: 'recuperação',
            2020: 'desaquecido',
            2019: 'estável',
            2018: 'aquecido'
        }
        return conditions.get(year, 'estável')
    
    async def _rate_limit(self, operation: str):
        """Aplica rate limiting por operação"""
        now = time.time()
        last_request = self.last_request_time.get(operation, 0)
        
        if now - last_request < self.request_delay:
            await asyncio.sleep(self.request_delay - (now - last_request))
        
        self.last_request_time[operation] = time.time()
