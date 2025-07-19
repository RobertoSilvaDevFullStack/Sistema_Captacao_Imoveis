#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solução simplificada para VivaReal - evita Cloudflare usando APIs públicas
"""

import requests
import logging
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
import json
import re

class VivaRealSimple:
    """Scraper VivaReal simplificado usando APIs públicas"""
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Configura sessão com headers realistas"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://www.vivareal.com.br',
            'Referer': 'https://www.vivareal.com.br/',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def scrape_properties(self, location: str = 'rio-de-janeiro', property_type: str = 'apartamento', max_results: int = 20) -> List[Dict]:
        """
        Scraping usando APIs diretas do VivaReal
        
        Args:
            location: cidade (ex: 'rio-de-janeiro', 'sao-paulo')
            property_type: tipo ('apartamento', 'casa', 'cobertura')
            max_results: máximo de resultados
        """
        logging.info(f"Iniciando busca VivaReal: {location} - {property_type}")
        
        properties = []
        
        # Estratégia 1: API de busca pública
        try:
            api_properties = self._try_search_api(location, property_type, max_results)
            if api_properties:
                properties.extend(api_properties)
                logging.info(f"API de busca retornou {len(api_properties)} propriedades")
        except Exception as e:
            logging.debug(f"API de busca falhou: {e}")
        
        # Estratégia 2: API de listagens
        if len(properties) < max_results:
            try:
                listing_properties = self._try_listing_api(location, property_type, max_results - len(properties))
                if listing_properties:
                    properties.extend(listing_properties)
                    logging.info(f"API de listagens retornou {len(listing_properties)} propriedades")
            except Exception as e:
                logging.debug(f"API de listagens falhou: {e}")
        
        # Estratégia 3: Scraping de feeds RSS/XML
        if len(properties) < max_results:
            try:
                feed_properties = self._try_feed_scraping(location, property_type, max_results - len(properties))
                if feed_properties:
                    properties.extend(feed_properties)
                    logging.info(f"Feed scraping retornou {len(feed_properties)} propriedades")
            except Exception as e:
                logging.debug(f"Feed scraping falhou: {e}")
        
        logging.info(f"Total de propriedades encontradas: {len(properties)}")
        return properties[:max_results]
    
    def _try_search_api(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Tenta usar API de busca do VivaReal"""
        try:
            # URLs conhecidas da API do VivaReal
            api_urls = [
                "https://glue-api.vivareal.com/v2/listings",
                "https://search.vivareal.com/v1/search",
                "https://api.vivareal.com/listings/search"
            ]
            
            for api_url in api_urls:
                try:
                    params = {
                        'addressCity': location.replace('-', ' ').title(),
                        'business': 'SALE',
                        'unitTypes': property_type.upper(),
                        'size': min(max_results, 50),
                        'from': 0,
                        'includeFields': 'listing(displayAddressType,amenities,usableAreas,constructionStatus,listingType,description,title,stampUrls,createdAt,floors,unitTypes,providerId,propertyType,unitSubTypes,unitsOnTheFloor,legacyId,id,portal,unitFloor,parkingSpaces,updatedAt,address,suites,publicationType,externalId,bathrooms,usableArea,totalAreas,advertiserId,advertiserContact,whatsappNumber,bedrooms,acceptExchange,pricingInfos,showPrice,resale,buildings,capacityLimit,status),account(id,name,logoUrl,licenseNumber,showAddress,legacyVivarealId,legacyZapId,minisite),medias,accountLink,link'
                    }
                    
                    response = self.session.get(api_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_search_api_response(data)
                    
                except Exception as e:
                    logging.debug(f"API URL {api_url} falhou: {e}")
                    continue
                    
        except Exception as e:
            logging.debug(f"Erro na API de busca: {e}")
        
        return []
    
    def _try_listing_api(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Tenta API de listagens alternativa"""
        try:
            # Simular requisições de listagem
            listing_endpoints = [
                f"https://www.vivareal.com.br/api/listings?city={location}&type={property_type}",
                f"https://glue-api.vivareal.com/listings?addressCity={location}&unitTypes={property_type}"
            ]
            
            for endpoint in listing_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    
                    if response.status_code == 200:
                        # Tentar interpretar como JSON
                        try:
                            data = response.json()
                            return self._parse_listing_response(data)
                        except:
                            # Se não for JSON, tentar extrair dados da resposta HTML
                            return self._extract_from_html_response(response.text, max_results)
                    
                except Exception as e:
                    logging.debug(f"Endpoint {endpoint} falhou: {e}")
                    continue
                    
        except Exception as e:
            logging.debug(f"Erro na API de listagens: {e}")
        
        return []
    
    def _try_feed_scraping(self, location: str, property_type: str, max_results: int) -> List[Dict]:
        """Tenta scraping de feeds públicos"""
        try:
            # URLs de feeds conhecidos
            feed_urls = [
                f"https://www.vivareal.com.br/sitemap/listings-{location}.xml",
                f"https://feeds.vivareal.com.br/{location}/{property_type}.json",
                f"https://www.vivareal.com.br/rss/imoveis-{location}"
            ]
            
            for feed_url in feed_urls:
                try:
                    response = self.session.get(feed_url, timeout=10)
                    
                    if response.status_code == 200:
                        if 'xml' in feed_url:
                            return self._parse_xml_feed(response.text, max_results)
                        elif 'json' in feed_url:
                            data = response.json()
                            return self._parse_json_feed(data, max_results)
                        else:
                            return self._parse_rss_feed(response.text, max_results)
                    
                except Exception as e:
                    logging.debug(f"Feed {feed_url} falhou: {e}")
                    continue
                    
        except Exception as e:
            logging.debug(f"Erro no feed scraping: {e}")
        
        return []
    
    def _parse_search_api_response(self, data: dict) -> List[Dict]:
        """Parse resposta da API de busca"""
        properties = []
        try:
            # Estruturas comuns de resposta da API VivaReal
            listings = []
            
            if 'listings' in data:
                listings = data['listings']
            elif 'results' in data:
                listings = data['results']
            elif 'search' in data and 'result' in data['search']:
                listings = data['search']['result']['listings']
            
            for listing in listings:
                try:
                    property_data = {
                        'title': self._safe_get(listing, ['title', 'listing.title']),
                        'price': self._extract_price(listing),
                        'location': self._extract_location(listing),
                        'area': self._extract_area(listing),
                        'bedrooms': self._safe_get(listing, ['bedrooms', 'listing.bedrooms']),
                        'bathrooms': self._safe_get(listing, ['bathrooms', 'listing.bathrooms']),
                        'url': self._extract_url(listing),
                        'description': self._safe_get(listing, ['description', 'listing.description']),
                        'source': 'VivaReal',
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    if property_data['title'] or property_data['price']:
                        properties.append(property_data)
                        
                except Exception as e:
                    logging.debug(f"Erro ao processar listing: {e}")
                    continue
                    
        except Exception as e:
            logging.debug(f"Erro ao parse API response: {e}")
        
        return properties
    
    def _safe_get(self, obj: dict, keys: List[str]) -> str:
        """Extração segura de valores aninhados"""
        for key in keys:
            try:
                if '.' in key:
                    # Navegar por chaves aninhadas
                    parts = key.split('.')
                    value = obj
                    for part in parts:
                        value = value[part]
                    if value:
                        return str(value)
                else:
                    if key in obj and obj[key]:
                        return str(obj[key])
            except:
                continue
        return ''
    
    def _extract_price(self, listing: dict) -> str:
        """Extrai preço do listing"""
        price_keys = [
            'pricingInfos.0.price',
            'pricingInfos.price',
            'price',
            'listing.price',
            'listing.pricingInfos.0.price'
        ]
        
        for key in price_keys:
            try:
                if '.' in key:
                    parts = key.split('.')
                    value = listing
                    for part in parts:
                        if part.isdigit():
                            value = value[int(part)]
                        else:
                            value = value[part]
                    if value:
                        return f"R$ {value:,.2f}" if isinstance(value, (int, float)) else str(value)
                else:
                    if key in listing and listing[key]:
                        value = listing[key]
                        return f"R$ {value:,.2f}" if isinstance(value, (int, float)) else str(value)
            except:
                continue
        return ''
    
    def _extract_location(self, listing: dict) -> str:
        """Extrai localização do listing"""
        location_keys = [
            'address.city',
            'address.neighborhood',
            'listing.address.city',
            'location',
            'address'
        ]
        
        return self._safe_get(listing, location_keys)
    
    def _extract_area(self, listing: dict) -> str:
        """Extrai área do listing"""
        area_keys = [
            'usableArea',
            'listing.usableArea',
            'totalArea',
            'listing.totalArea',
            'area'
        ]
        
        area = self._safe_get(listing, area_keys)
        if area and area.isdigit():
            return f"{area} m²"
        return area
    
    def _extract_url(self, listing: dict) -> str:
        """Extrai URL do listing"""
        url_keys = [
            'link.href',
            'url',
            'listing.url',
            'link'
        ]
        
        url = self._safe_get(listing, url_keys)
        if url and not url.startswith('http'):
            url = f"https://www.vivareal.com.br{url}"
        return url
    
    def _parse_listing_response(self, data: dict) -> List[Dict]:
        """Parse resposta de API de listagens"""
        # Implementação similar ao _parse_search_api_response
        return self._parse_search_api_response(data)
    
    def _extract_from_html_response(self, html: str, max_results: int) -> List[Dict]:
        """Extrai dados de resposta HTML"""
        properties = []
        try:
            # Buscar por dados JSON embutidos no HTML
            json_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
            matches = re.findall(json_pattern, html, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    extracted = self._parse_search_api_response(data)
                    properties.extend(extracted)
                    if len(properties) >= max_results:
                        break
                except:
                    continue
                    
        except Exception as e:
            logging.debug(f"Erro ao extrair HTML: {e}")
        
        return properties[:max_results]
    
    def _parse_xml_feed(self, xml_content: str, max_results: int) -> List[Dict]:
        """Parse feed XML"""
        properties = []
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(xml_content)
            
            # Processar URLs do sitemap
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and len(properties) < max_results:
                    # Extrair informações básicas da URL
                    url = loc_elem.text
                    if 'imovel' in url:
                        property_data = {
                            'title': '',
                            'price': '',
                            'location': '',
                            'url': url,
                            'source': 'VivaReal',
                            'scraped_at': datetime.now().isoformat()
                        }
                        properties.append(property_data)
                        
        except Exception as e:
            logging.debug(f"Erro ao parse XML: {e}")
        
        return properties
    
    def _parse_json_feed(self, data: dict, max_results: int) -> List[Dict]:
        """Parse feed JSON"""
        return self._parse_search_api_response(data)
    
    def _parse_rss_feed(self, rss_content: str, max_results: int) -> List[Dict]:
        """Parse feed RSS"""
        properties = []
        try:
            from xml.etree import ElementTree as ET
            root = ET.fromstring(rss_content)
            
            for item in root.findall('.//item')[:max_results]:
                property_data = {
                    'title': item.findtext('title', ''),
                    'price': '',
                    'location': '',
                    'url': item.findtext('link', ''),
                    'description': item.findtext('description', ''),
                    'source': 'VivaReal',
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Tentar extrair preço da descrição
                desc = property_data['description'].lower()
                price_match = re.search(r'r\$\s*([\d.,]+)', desc)
                if price_match:
                    property_data['price'] = f"R$ {price_match.group(1)}"
                
                properties.append(property_data)
                
        except Exception as e:
            logging.debug(f"Erro ao parse RSS: {e}")
        
        return properties
    
    def close(self):
        """Fecha sessão"""
        try:
            self.session.close()
        except:
            pass
