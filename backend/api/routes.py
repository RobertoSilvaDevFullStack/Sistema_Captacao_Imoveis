from flask import Flask, jsonify, request
from flask_cors import CORS
from .services.analysis_service import AnalysisService
from .models.property import Property
from .database import db_session

app = Flask(__name__)
CORS(app)

@app.route('/api/market-overview')
def market_overview():
    days_back = request.args.get('days', 30, type=int)
    analysis_service = AnalysisService(db_session)
    data = analysis_service.get_market_overview(days_back)
    return jsonify(data)

@app.route('/api/properties')
def get_properties():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    neighborhood = request.args.get('neighborhood')
    
    query = db_session.query(Property).filter(Property.is_active == True)
    
    if neighborhood:
        query = query.filter(Property.neighborhood == neighborhood)
    
    properties = query.offset((page - 1) * per_page).limit(per_page).all()
    total = query.count()
    
    return jsonify({
        'properties': [prop.to_dict() for prop in properties],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/opportunities')
def get_opportunities():
    analysis_service = AnalysisService(db_session)
    opportunities = analysis_service.get_top_opportunities()
    return jsonify(opportunities)

@app.route('/api/neighborhoods')
def get_neighborhoods():
    neighborhoods = db_session.query(Property.neighborhood).distinct().all()
    return jsonify([n[0] for n in neighborhoods if n[0]])

if __name__ == '__main__':
    app.run(debug=True)