# src/api/routes.py
"""
Rotas da API
"""
import logging
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request

from ..scrapers import ZapImoveisScraper
from ..models.property import PropertySearch, PropertyType, PropertySource

# Criar blueprint
api_bp = Blueprint('api', __name__)

# Logger
logger = logging.getLogger(__name__)

@api_bp.route('/properties/search', methods=['GET'])
def search_properties():
    """Buscar propriedades com filtros"""
    try:
        # Obter parâmetros da requisição
        city = request.args.get('city', 'rio-de-janeiro')
        property_type_str = request.args.get('property_type', 'apartamento')
        portal_str = request.args.get('portal', 'zapimoveis')
        max_results = int(request.args.get('max_results', 20))
        only_opportunities = request.args.get('only_opportunities', 'false').lower() == 'true'
        
        # Converter para enums
        try:
            property_type = PropertyType(property_type_str)
        except ValueError:
            property_type = PropertyType.APARTAMENTO
            
        try:
            portal = PropertySource(portal_str)
        except ValueError:
            portal = PropertySource.ZAPIMOVEIS
        
        logger.info(f"Buscando propriedades: {city}, {property_type.value}, {portal.value}")
        
        # Criar parâmetros de busca
        search = PropertySearch(
            city=city,
            property_type=property_type,
            portal=portal,
            max_results=max_results,
            only_opportunities=only_opportunities
        )
        
        # Executar scraping baseado no portal
        if portal == PropertySource.ZAPIMOVEIS:
            scraper = ZapImoveisScraper()
            result = scraper.scrape_properties(search)
        else:
            # Outros portais em desenvolvimento
            logger.warning(f"Portal {portal.value} em desenvolvimento")
            from ..models.property import ScrapingResult
            result = ScrapingResult(source=portal)
            result.success = False
            result.error_message = f"Portal {portal.value} em desenvolvimento"
        
        # Converter propriedades para dict
        properties_data = [prop.to_dict() for prop in result.properties]
        
        return jsonify({
            'success': result.success,
            'properties': properties_data,
            'total': result.total_found,
            'execution_time': result.execution_time,
            'filters': {
                'city': city,
                'property_type': property_type.value,
                'portal': portal.value,
                'only_opportunities': only_opportunities
            },
            'timestamp': datetime.now().isoformat(),
            'error': result.error_message if not result.success else None
        })
        
    except Exception as e:
        logger.error(f"Erro na busca de propriedades: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'properties': [],
            'total': 0
        }), 500

@api_bp.route('/scrapers/status', methods=['GET'])
def get_scrapers_status():
    """Status dos scrapers"""
    try:
        status = {
            'zapimoveis': {
                'status': 'active',
                'description': 'Scraper avançado com foco em lançamentos e oportunidades',
                'last_run': datetime.now().isoformat()
            },
            'olx': {
                'status': 'development',
                'description': 'Em desenvolvimento',
                'last_run': None
            },
            'vivareal': {
                'status': 'development',
                'description': 'Em desenvolvimento',
                'last_run': None
            }
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status dos scrapers: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })
