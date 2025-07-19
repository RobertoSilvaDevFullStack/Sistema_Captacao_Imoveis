#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VivaReal com requests avançado - evita Cloudflare com headers específicos
"""

import requests
import logging
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class VivaRealAdvanced:
    """Scraper VivaReal usando requests com técnicas anti-detecção"""
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Configura sessão com headers avançados anti-detecção"""
        
        # Headers que imitam um browser real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
        
        self.session.headers.update(headers)
        
        # Configurações adicionais da sessão
        self.session.verify = True
        self.session.timeout = 30
        
    def scrape_properties(self, location: str = 'rio-de-janeiro', property_type: str = 'apartamento', max_results: int = 20) -> List[Dict]:
        """
        Scraping principal com múltiplas estratégias
        
        Args:
            location: cidade (ex: 'rio-de-janeiro', 'sao-paulo')
            property_type: tipo ('apartamento', 'casa', 'cobertura')
            max_results: máximo de resultados
        """
        logging.info(f"Iniciando scraping VivaReal Advanced: {location} - {property_type}")
        
        properties = []
        
        # Estratégia 1: Página de listagem padrão
        try:
            listing_properties = self._try_listing_page(location, property_type, max_results)
            if listing_properties:
                properties.extend(listing_properties)
                logging.info(f"Estratégia 1: {len(listing_properties)} propriedades")
        except Exception as e:
            logging.debug(f"Estratégia 1 falhou: {e}")
        
        # Estratégia 2: URLs alternativas
        if len(properties) < max_results:
            try:
                alt_properties = self._try_alternative_urls(location, property_type, max_results - len(properties))
                if alt_properties:
                    properties.extend(alt_properties)
                    logging.info(f"Estratégia 2: {len(alt_properties)} propriedades")
            except Exception as e:
                logging.debug(f"Estratégia 2 falhou: {e}")
        
        # Estratégia 3: URLs com parâmetros específicos
        if len(properties) < max_results:
            try:
                param_properties = self._try_parameterized_urls(location, property_type, max_results - len(properties))
                if param_properties:
                    properties.extend(param_properties)
                    logging.info(f"Estratégia 3: {len(param_properties)} propriedades")
            except Exception as e:
                logging.debug(f"Estratégia 3 falhou: {e}")
        
        logging.info(f"Total extraído: {len(properties)} propriedades")
        return properties[:max_results]
    
    def _try_listing_page(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Estratégia 1: Página de listagem padrão"""
        
        # Mapear tipos de propriedade
        type_mapping = {
            'apartamento': 'apartamento',
            'casa': 'casa', 
            'cobertura': 'cobertura',
            'todos': 'imoveis'
        }
        
        prop_type = type_mapping.get(property_type, 'apartamento')
        
        # Construir URL
        base_url = "https://www.vivareal.com.br"
        url = f"{base_url}/venda/{prop_type}/{location}/"
        
        logging.info(f"Tentando URL: {url}")
        
        try:
            # Fazer requisição com delay
            time.sleep(random.uniform(1, 3))
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                return self._parse_listing_page(response.text, max_results)
            else:
                logging.warning(f"Status code: {response.status_code if response else 'None'}")
                
        except Exception as e:
            logging.debug(f"Erro na página de listagem: {e}")
        
        return []
    
    def _try_alternative_urls(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Estratégia 2: URLs alternativas"""
        
        # URLs alternativas conhecidas
        alt_patterns = [
            f"https://www.vivareal.com.br/aluguel-e-venda/{property_type}/{location}/",
            f"https://www.vivareal.com.br/busca/{property_type}/{location}/",
            f"https://www.vivareal.com.br/imoveis/{location}/{property_type}/",
            f"https://glue-api.vivareal.com.br/search?city={location}&type={property_type}",
        ]
        
        for url in alt_patterns:
            try:
                logging.info(f"Tentando URL alternativa: {url}")
                time.sleep(random.uniform(1, 2))
                
                response = self._make_request(url)
                
                if response and response.status_code == 200:
                    if 'api' in url:
                        properties = self._parse_api_response(response.text)
                    else:
                        properties = self._parse_listing_page(response.text, max_results)
                    
                    if properties:
                        return properties
                        
            except Exception as e:
                logging.debug(f"URL alternativa {url} falhou: {e}")
                continue
        
        return []
    
    def _try_parameterized_urls(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Estratégia 3: URLs com parâmetros específicos"""
        
        base_url = "https://www.vivareal.com.br/venda/apartamento/"
        
        # Diferentes combinações de parâmetros
        param_sets = [
            {
                'addressCity': location.replace('-', ' ').title(),
                'business': 'SALE',
                'unitTypes': property_type.upper(),
                'size': min(max_results, 50)
            },
            {
                'q': location,
                'tipo': property_type,
                'negocio': 'venda',
                'tamanho': max_results
            }
        ]
        
        for params in param_sets:
            try:
                time.sleep(random.uniform(1, 2))
                response = self._make_request(base_url, params=params)
                
                if response and response.status_code == 200:
                    properties = self._parse_listing_page(response.text, max_results)
                    if properties:
                        return properties
                        
            except Exception as e:
                logging.debug(f"Parâmetros {params} falharam: {e}")
                continue
        
        return []
    
    def _make_request(self, url: str, params: Optional[Dict] = None, retries: int = 3) -> Optional[requests.Response]:
        """Faz requisição com retry e rotação de headers"""
        
        for attempt in range(retries):
            try:
                # Rotacionar User-Agent ocasionalmente
                if attempt > 0:
                    self._rotate_headers()
                
                response = self.session.get(url, params=params, timeout=30)
                
                # Verificar se não é página de erro/bloqueio
                if self._is_blocked_response(response):
                    logging.warning(f"Resposta bloqueada detectada (tentativa {attempt + 1})")
                    if attempt < retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                logging.debug(f"Erro na requisição (tentativa {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(2, 5))
                    continue
        
        return None
    
    def _rotate_headers(self):
        """Rotaciona headers para evitar detecção"""
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })
    
    def _is_blocked_response(self, response: requests.Response) -> bool:
        """Verifica se a resposta indica bloqueio"""
        
        # Códigos de status que indicam bloqueio
        if response.status_code in [403, 429, 503]:
            return True
        
        # Conteúdo que indica Cloudflare ou bloqueio
        content_lower = response.text.lower()
        blocked_indicators = [
            'cloudflare',
            'checking your browser',
            'ddos protection',
            'access denied',
            'blocked',
            'captcha',
            'just a moment'
        ]
        
        return any(indicator in content_lower for indicator in blocked_indicators)
    
    def _parse_listing_page(self, html: str, max_results: int) -> List[Dict]:
        """Parse página de listagem HTML"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            properties = []
            
            # Múltiplos seletores para propriedades
            selectors = [
                '[data-testid="property-card"]',
                '.property-card',
                '.listing-item', 
                '.js-card-selector',
                '.results-item',
                'article[data-position]',
                '.resultContainer .result-card'
            ]
            
            property_elements = []
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    property_elements = elements
                    logging.info(f"Usando seletor: {selector} - {len(elements)} elementos")
                    break
            
            if not property_elements:
                # Tentar extrair dados de scripts JSON
                properties = self._extract_from_scripts(soup)
                if properties:
                    logging.info(f"Extraído de scripts: {len(properties)} propriedades")
                    return properties[:max_results]
                
                logging.warning("❌ Nenhum elemento de propriedade encontrado no HTML")
                return []
            
            # Extrair dados de cada elemento
            for element in property_elements[:max_results]:
                try:
                    property_data = self._extract_property_data(element)
                    if property_data:
                        properties.append(property_data)
                except Exception as e:
                    logging.debug(f"Erro ao extrair propriedade: {e}")
                    continue
            
            return properties
            
        except Exception as e:
            logging.error(f"Erro no parse HTML: {e}")
            return []
    
    def _extract_from_scripts(self, soup) -> List[Dict]:
        """Extrai dados de scripts JSON na página"""
        
        properties = []
        
        try:
            # Procurar por scripts com dados JSON
            scripts = soup.find_all('script', type='application/json')
            scripts.extend(soup.find_all('script', string=re.compile(r'window\.__INITIAL_STATE__')))
            scripts.extend(soup.find_all('script', string=re.compile(r'window\.VivaReal')))
            
            for script in scripts:
                try:
                    if script.string:
                        # Tentar extrair JSON
                        json_match = re.search(r'({.*})', script.string, re.DOTALL)
                        if json_match:
                            import json
                            data = json.loads(json_match.group(1))
                            extracted = self._extract_properties_from_json(data)
                            properties.extend(extracted)
                            
                except Exception as e:
                    logging.debug(f"Erro ao processar script: {e}")
                    continue
            
        except Exception as e:
            logging.debug(f"Erro na extração de scripts: {e}")
        
        return properties
    
    def _extract_properties_from_json(self, data: dict) -> List[Dict]:
        """Extrai propriedades de dados JSON"""
        
        properties = []
        
        try:
            # Procurar estruturas conhecidas
            def find_listings(obj, path=""):
                if isinstance(obj, dict):
                    # Chaves que geralmente contêm listings
                    listing_keys = ['listings', 'results', 'properties', 'ads', 'search']
                    
                    for key, value in obj.items():
                        if key in listing_keys and isinstance(value, list):
                            return value
                        elif isinstance(value, (dict, list)):
                            result = find_listings(value, f"{path}.{key}")
                            if result:
                                return result
                
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, dict):
                            result = find_listings(item, path)
                            if result:
                                return result
                
                return None
            
            listings = find_listings(data)
            
            if listings:
                for listing in listings:
                    try:
                        property_data = {
                            'title': self._safe_extract(listing, ['title', 'heading', 'name']),
                            'price': self._safe_extract(listing, ['price', 'value', 'cost']),
                            'location': self._safe_extract(listing, ['address', 'location', 'city']),
                            'area': self._safe_extract(listing, ['area', 'size', 'squareMeters']),
                            'bedrooms': self._safe_extract(listing, ['bedrooms', 'rooms', 'quartos']),
                            'bathrooms': self._safe_extract(listing, ['bathrooms', 'banheiros']),
                            'url': self._safe_extract(listing, ['url', 'link', 'href']),
                            'source': 'VivaReal (Advanced)',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        if property_data['title'] or property_data['price']:
                            properties.append(property_data)
                            
                    except Exception as e:
                        logging.debug(f"Erro ao processar listing JSON: {e}")
                        continue
            
        except Exception as e:
            logging.debug(f"Erro na extração JSON: {e}")
        
        return properties
    
    def _safe_extract(self, obj: dict, keys: List[str]) -> str:
        """Extração segura de valores"""
        for key in keys:
            if key in obj and obj[key]:
                return str(obj[key])
        return ''
    
    def _extract_property_data(self, element) -> Optional[Dict]:
        """Extrai dados de um elemento de propriedade"""
        
        try:
            # Título
            title_elem = (
                element.select_one('[data-testid="property-card-title"]') or
                element.select_one('.property-card__title') or
                element.select_one('.listing-title') or
                element.select_one('h2 a') or
                element.select_one('h3 a')
            )
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Preço
            price_elem = (
                element.select_one('[data-testid="price-info"]') or
                element.select_one('.property-card__price') or
                element.select_one('.listing-price') or
                element.select_one('.price')
            )
            price = price_elem.get_text(strip=True) if price_elem else ''
            
            # Localização
            location_elem = (
                element.select_one('[data-testid="property-card-location"]') or
                element.select_one('.property-card__address') or
                element.select_one('.listing-location') or
                element.select_one('.address')
            )
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Área
            area_elem = (
                element.select_one('[data-testid="property-card-area"]') or
                element.select_one('.property-card__area') or
                element.select_one('.listing-area') or
                element.select_one('.area')
            )
            area = area_elem.get_text(strip=True) if area_elem else ''
            
            # URL
            url_elem = (
                element.select_one('a[href*="/imovel/"]') or
                element.select_one('a[href*="/apartamento/"]') or
                element.select_one('a[href*="/casa/"]') or
                element.select_one('a')
            )
            url = url_elem.get('href') if url_elem else ''
            
            # Montar dados
            property_data = {
                'title': title or 'Sem título',
                'price': price or 'N/A',
                'location': location or 'N/A',
                'area': area or 'N/A', 
                'bedrooms': 'N/A',
                'bathrooms': 'N/A',
                'url': urljoin('https://www.vivareal.com.br', url) if url else 'N/A',
                'source': 'VivaReal (Advanced)',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Só retornar se tiver dados úteis
            if property_data['title'] != 'Sem título' or property_data['price'] != 'N/A':
                return property_data
                
        except Exception as e:
            logging.debug(f"Erro ao extrair dados: {e}")
        
        return None
    
    def _parse_api_response(self, content: str) -> List[Dict]:
        """Parse resposta de API"""
        try:
            import json
            data = json.loads(content)
            return self._extract_properties_from_json(data)
        except:
            return []
    
    def close(self):
        """Fecha sessão"""
        try:
            self.session.close()
        except:
            pass
