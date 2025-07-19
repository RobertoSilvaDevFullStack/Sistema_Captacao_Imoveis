// frontend/src/components/CitySelector.jsx
import React from 'react';
import { MapPin, ChevronDown } from 'lucide-react';
import { AVAILABLE_CITIES } from '../services/propertyService';

const CitySelector = ({ selectedCity, onCityChange, className = "" }) => {
  const selectedCityData = AVAILABLE_CITIES.find(city => city.code === selectedCity);

  return (
    <div className={`relative ${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        <MapPin className="inline w-4 h-4 mr-1" />
        Cidade
      </label>
      
      <div className="relative">
        <select
          value={selectedCity}
          onChange={(e) => onCityChange(e.target.value)}
          className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-3 py-2 pr-8 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     text-gray-900 font-medium cursor-pointer"
        >
          {AVAILABLE_CITIES.map((city) => (
            <option key={city.code} value={city.code}>
              {city.name} - {city.state}
            </option>
          ))}
        </select>
        
        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
      </div>
      
      {selectedCityData && (
        <p className="text-xs text-gray-500 mt-1">
          Selecionado: {selectedCityData.name}, {selectedCityData.state}
        </p>
      )}
    </div>
  );
};

export default CitySelector;
