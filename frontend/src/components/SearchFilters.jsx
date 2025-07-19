// frontend/src/components/SearchFilters.jsx
import React from 'react';
import { Search, Filter, DollarSign, Home } from 'lucide-react';
import { PROPERTY_TYPES, AVAILABLE_PORTALS } from '../services/propertyService';
import CitySelector from './CitySelector';

const SearchFilters = ({ 
  filters, 
  onFiltersChange, 
  onSearch, 
  isLoading = false,
  className = "" 
}) => {
  
  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    onFiltersChange(newFilters);
  };

  const handleSearch = () => {
    onSearch(filters);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="flex items-center mb-4">
        <Filter className="w-5 h-5 mr-2 text-blue-600" />
        <h2 className="text-lg font-semibold text-gray-900">Filtros de Busca</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {/* Seletor de Cidade */}
        <CitySelector
          selectedCity={filters.city || 'rio-de-janeiro'}
          onCityChange={(city) => handleFilterChange('city', city)}
        />

        {/* Tipo de Propriedade */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <Home className="inline w-4 h-4 mr-1" />
            Tipo de Imóvel
          </label>
          <select
            value={filters.propertyType || 'apartamento'}
            onChange={(e) => handleFilterChange('propertyType', e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {PROPERTY_TYPES.map((type) => (
              <option key={type.code} value={type.code}>
                {type.name}
              </option>
            ))}
          </select>
        </div>

        {/* Preço Mínimo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <DollarSign className="inline w-4 h-4 mr-1" />
            Preço Mínimo
          </label>
          <input
            type="number"
            placeholder="Ex: 500000"
            value={filters.minPrice || ''}
            onChange={(e) => handleFilterChange('minPrice', e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Preço Máximo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <DollarSign className="inline w-4 h-4 mr-1" />
            Preço Máximo
          </label>
          <input
            type="number"
            placeholder="Ex: 2000000"
            value={filters.maxPrice || ''}
            onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
            onKeyPress={handleKeyPress}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Termo de busca */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          <Search className="inline w-4 h-4 mr-1" />
          Buscar por palavra-chave
        </label>
        <input
          type="text"
          placeholder="Ex: piscina, garagem, vista mar..."
          value={filters.searchTerm || ''}
          onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
          onKeyPress={handleKeyPress}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Portal de busca */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Portal de Busca
        </label>
        <div className="flex flex-wrap gap-2">
          {AVAILABLE_PORTALS.map((portal) => (
            <button
              key={portal.code}
              onClick={() => handleFilterChange('portal', portal.code)}
              disabled={portal.status === 'blocked'}
              className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors
                ${filters.portal === portal.code 
                  ? 'bg-blue-600 text-white border-blue-600' 
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }
                ${portal.status === 'blocked' 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'cursor-pointer'
                }
              `}
            >
              {portal.name}
              {portal.status === 'blocked' && ' (Bloqueado)'}
              {portal.status === 'maintenance' && ' (Manutenção)'}
            </button>
          ))}
        </div>
      </div>

      {/* Botão de busca */}
      <div className="flex justify-end">
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className={`px-6 py-2 bg-blue-600 text-white rounded-lg font-medium 
                     hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
                     disabled:opacity-50 disabled:cursor-not-allowed
                     flex items-center gap-2`}
        >
          <Search className="w-4 h-4" />
          {isLoading ? 'Buscando...' : 'Buscar Imóveis'}
        </button>
      </div>
    </div>
  );
};

export default SearchFilters;
