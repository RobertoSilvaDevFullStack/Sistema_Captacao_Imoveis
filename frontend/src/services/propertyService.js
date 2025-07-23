// frontend/src/services/propertyService.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Configuração do axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Interceptor para logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// Cidades disponíveis (baseado no location_config.py)
export const AVAILABLE_CITIES = [
  { code: 'rio-de-janeiro', name: 'Rio de Janeiro', state: 'RJ' },
  { code: 'sao-paulo', name: 'São Paulo', state: 'SP' },
  { code: 'belo-horizonte', name: 'Belo Horizonte', state: 'MG' },
  { code: 'brasilia', name: 'Brasília', state: 'DF' },
  { code: 'salvador', name: 'Salvador', state: 'BA' },
  { code: 'fortaleza', name: 'Fortaleza', state: 'CE' },
  { code: 'recife', name: 'Recife', state: 'PE' },
  { code: 'porto-alegre', name: 'Porto Alegre', state: 'RS' },
  { code: 'curitiba', name: 'Curitiba', state: 'PR' },
  { code: 'florianopolis', name: 'Florianópolis', state: 'SC' }
];

// Tipos de propriedade
export const PROPERTY_TYPES = [
  { code: 'todos', name: 'Todos os tipos' },
  { code: 'apartamento', name: 'Apartamentos' },
  { code: 'casa', name: 'Casas' },
  { code: 'cobertura', name: 'Coberturas' }
];

// Portais disponíveis
export const AVAILABLE_PORTALS = [
  { code: 'zapimoveis', name: 'ZapImóveis', status: 'active' },
  { code: 'olx', name: 'OLX', status: 'maintenance' },
  { code: 'vivareal', name: 'VivaReal', status: 'blocked' }
];

// Serviços da API
export const propertyService = {
  
  // Buscar propriedades
  async searchProperties(filters = {}) {
    try {
      const params = {
        city: filters.city || 'rio-de-janeiro',
        property_type: filters.propertyType || 'apartamento',
        portal: filters.portal || 'zapimoveis',
        max_results: filters.maxResults || 50,
        min_price: filters.minPrice || null,
        max_price: filters.maxPrice || null,
        ...filters
      };

      const response = await apiClient.post('/api/search', params);
      
      return {
        success: true,
        data: response.data.data || response.data,
        total: response.data.total || response.data.length,
        timestamp: response.data.timestamp || new Date().toISOString()
      };
      
    } catch (error) {
      console.error('❌ ERRO ao buscar propriedades:', error);
      console.error('🔍 Tentando conectar com:', API_BASE_URL);
      
      // Em vez de retornar dados mockados, retornar erro
      return {
        success: false,
        error: `Erro de conexão: ${error.message}. Backend não está respondendo em ${API_BASE_URL}`,
        data: [],
        total: 0
      };
    }
  },

  // Obter estatísticas do mercado
  async getMarketStats(city = 'rio-de-janeiro') {
    try {
      const response = await apiClient.get(`/api/market/stats/${city}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Erro ao obter estatísticas:', error);
      return this.getMockStats(city);
    }
  },

  // Buscar propriedades por bairro
  async getPropertiesByNeighborhood(city, neighborhood) {
    try {
      const response = await apiClient.get(`/api/properties/neighborhood/${city}/${neighborhood}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Erro ao buscar por bairro:', error);
      return { success: false, error: error.message };
    }
  },

  // Obter detalhes de uma propriedade
  async getPropertyDetails(propertyId) {
    try {
      const response = await apiClient.get(`/api/properties/${propertyId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Erro ao obter detalhes:', error);
      return { success: false, error: error.message };
    }
  },

  // Status dos scrapers
  async getScrapersStatus() {
    try {
      const response = await apiClient.get('/api/scrapers/status');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Erro ao obter status:', error);
      return this.getMockScrapersStatus();
    }
  },

  // Dados mockados para fallback
  getMockProperties(filters = {}) {
    const mockProperties = [
      {
        id: 'mock-1',
        title: 'Apartamento 2 quartos em Copacabana',
        price: 'R$ 850.000',
        location: 'Copacabana, Rio de Janeiro - RJ',
        area: '75 m²',
        bedrooms: '2',
        bathrooms: '1',
        url: '#',
        source: 'ZapImóveis (Demo)',
        neighborhood: 'Copacabana',
        scraped_at: new Date().toISOString()
      },
      {
        id: 'mock-2', 
        title: 'Casa 3 quartos com quintal',
        price: 'R$ 1.200.000',
        location: 'Tijuca, Rio de Janeiro - RJ',
        area: '120 m²',
        bedrooms: '3',
        bathrooms: '2',
        url: '#',
        source: 'ZapImóveis (Demo)',
        neighborhood: 'Tijuca',
        scraped_at: new Date().toISOString()
      },
      {
        id: 'mock-3',
        title: 'Cobertura duplex vista mar',
        price: 'R$ 2.500.000',
        location: 'Ipanema, Rio de Janeiro - RJ', 
        area: '180 m²',
        bedrooms: '4',
        bathrooms: '3',
        url: '#',
        source: 'ZapImóveis (Demo)',
        neighborhood: 'Ipanema',
        scraped_at: new Date().toISOString()
      }
    ];

    return {
      success: true,
      data: mockProperties,
      total: mockProperties.length,
      timestamp: new Date().toISOString(),
      mock: true
    };
  },

  getMockStats(city) {
    return {
      success: true,
      data: {
        totalProperties: 847,
        avgPrice: 1250000,
        avgPricePerSqm: 8500,
        newListings: 23,
        priceChange: 2.5,
        city: city,
        lastUpdate: new Date().toISOString()
      },
      mock: true
    };
  },

  getMockScrapersStatus() {
    return {
      success: true,
      data: {
        zapimoveis: { status: 'active', lastRun: new Date().toISOString(), propertiesFound: 10 },
        olx: { status: 'maintenance', lastRun: new Date().toISOString(), propertiesFound: 0 },
        vivareal: { status: 'blocked', lastRun: new Date().toISOString(), propertiesFound: 0 }
      },
      mock: true
    };
  }
};

export default propertyService;
