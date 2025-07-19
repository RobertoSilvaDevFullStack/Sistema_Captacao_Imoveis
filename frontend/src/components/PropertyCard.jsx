// frontend/src/components/PropertyCard.jsx
import React from 'react';
import { ExternalLink, MapPin, Home, Bed, Bath, Maximize } from 'lucide-react';

const PropertyCard = ({ property, onClick }) => {
  const formatPrice = (price) => {
    if (!price || price === 'N/A') return 'Preço não informado';
    return price;
  };

  const formatArea = (area) => {
    if (!area || area === 'N/A') return '';
    return area;
  };

  const getSourceColor = (source) => {
    if (source?.includes('ZapImóveis')) return 'bg-green-100 text-green-800';
    if (source?.includes('OLX')) return 'bg-purple-100 text-purple-800';
    if (source?.includes('VivaReal')) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const handleExternalLink = (e) => {
    e.stopPropagation();
    if (property.url && property.url !== 'N/A' && property.url !== '#') {
      window.open(property.url, '_blank');
    }
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer border border-gray-200"
      onClick={() => onClick && onClick(property)}
    >
      {/* Header com fonte */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex justify-between items-start mb-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(property.source)}`}>
            {property.source || 'Fonte desconhecida'}
          </span>
          
          {property.url && property.url !== 'N/A' && property.url !== '#' && (
            <button
              onClick={handleExternalLink}
              className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
              title="Ver no site original"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          )}
        </div>
        
        <h3 className="font-semibold text-gray-900 text-lg line-clamp-2 leading-tight">
          {property.title || 'Título não informado'}
        </h3>
      </div>

      {/* Conteúdo principal */}
      <div className="p-4">
        {/* Preço */}
        <div className="mb-3">
          <p className="text-2xl font-bold text-green-600">
            {formatPrice(property.price)}
          </p>
        </div>

        {/* Localização */}
        {property.location && property.location !== 'N/A' && (
          <div className="flex items-center mb-3 text-gray-600">
            <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
            <p className="text-sm line-clamp-1">{property.location}</p>
          </div>
        )}

        {/* Características */}
        <div className="grid grid-cols-3 gap-2 text-sm text-gray-600">
          {/* Área */}
          {property.area && property.area !== 'N/A' && (
            <div className="flex items-center">
              <Maximize className="w-4 h-4 mr-1" />
              <span>{formatArea(property.area)}</span>
            </div>
          )}

          {/* Quartos */}
          {property.bedrooms && property.bedrooms !== 'N/A' && (
            <div className="flex items-center">
              <Bed className="w-4 h-4 mr-1" />
              <span>{property.bedrooms}</span>
            </div>
          )}

          {/* Banheiros */}
          {property.bathrooms && property.bathrooms !== 'N/A' && (
            <div className="flex items-center">
              <Bath className="w-4 h-4 mr-1" />
              <span>{property.bathrooms}</span>
            </div>
          )}
        </div>

        {/* Data de captura */}
        {property.scraped_at && (
          <div className="mt-3 pt-2 border-t border-gray-100">
            <p className="text-xs text-gray-400">
              Capturado em: {new Date(property.scraped_at).toLocaleDateString('pt-BR')}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PropertyCard;
