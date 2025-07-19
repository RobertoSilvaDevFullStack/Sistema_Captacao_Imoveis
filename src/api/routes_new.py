# src/api/routes.py
"""
Rotas da API organizadas
"""
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
import traceback

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
        
        logger.info(f"Buscando propriedades: {city}, {property_type_str}, {portal_str}")
        
        # Converter para enums
        try:
            property_type = PropertyType(property_type_str)
        except ValueError:
            property_type = PropertyType.APARTAMENTO
            
        try:
            portal = PropertySource(portal_str)
        except ValueError:
            portal = PropertySource.ZAPIMOVEIS
        
        properties = []
        
        # ZapImóveis com scraper novo
        if portal == PropertySource.ZAPIMOVEIS:
            try:
                logger.info("Usando ZapImóveis Scraper limpo")
                scraper = ZapImoveisScraper()
                
                search = PropertySearch(
                    city=city,
                    property_type=property_type,
                    portal=portal,
                    max_results=min(max_results, 15)
                )
                
                result = scraper.scrape_properties(search)
                
                if result.success:
                    properties = [prop.to_dict() for prop in result.properties]
                    logger.info(f"ZapImóveis retornou {len(properties)} propriedades")
                else:
                    logger.error(f"Erro no scraping: {result.error_message}")
                
            except Exception as e:
                logger.error(f"Erro no ZapImóveis: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                properties = []
        else:
            # Outros portais temporariamente indisponíveis
            logger.info(f"Portal {portal.value} temporariamente indisponível")
            properties = []
        
        return jsonify({
            'success': True,
            'properties': properties,
            'total': len(properties),
            'filters': {
                'city': city,
                'property_type': property_type.value,
                'portal': portal.value
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro na busca de propriedades: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'properties': []
        }), 500

@api_bp.route('/scrapers/status', methods=['GET'])
def get_scrapers_status():
    """Status dos scrapers"""
    try:
        status = {
            'zapimoveis': {
                'status': 'active',
                'last_run': datetime.now().isoformat(),
                'description': 'Scraper limpo com foco em oportunidades'
            },
            'olx': {
                'status': 'development',
                'last_run': datetime.now().isoformat(),
                'description': 'Em desenvolvimento na nova estrutura'
            },
            'vivareal': {
                'status': 'planned',
                'last_run': datetime.now().isoformat(),
                'description': 'Planejado para próxima versão'
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
    """Health check da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })
