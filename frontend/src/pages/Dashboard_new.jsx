import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Home, MapPin, DollarSign, Calendar, ExternalLink, Filter, Search, RefreshCw, AlertCircle } from 'lucide-react';
import SearchFilters from '../components/SearchFilters';
import PropertyCard from '../components/PropertyCard';
import propertyService from '../services/propertyService';

const RealEstateDashboard = () => {
  // Estados para filtros e dados
  const [filters, setFilters] = useState({
    city: 'rio-de-janeiro',
    propertyType: 'apartamento',
    portal: 'zapimoveis',
    maxResults: 20
  });
  
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [error, setError] = useState(null);
  const [scrapersStatus, setScrapersStatus] = useState({});

  // Dados mockados para demonstração do dashboard
  const marketData = {
    totalProperties: 847,
    avgPrice: 1250000,
    avgPricePerSqm: 8500,
    newListings: 23,
    priceChange: 2.5
  };

  const dailyListings = [
    { date: '16/07', novos: 12, total: 847 },
    { date: '15/07', novos: 8, total: 835 },
    { date: '14/07', novos: 15, total: 827 },
    { date: '13/07', novos: 6, total: 812 },
    { date: '12/07', novos: 18, total: 806 },
    { date: '11/07', novos: 10, total: 788 },
    { date: '10/07', novos: 14, total: 778 }
  ];

  const bedroomDistribution = [
    { name: '1 Quarto', value: 156, color: '#8884d8' },
    { name: '2 Quartos', value: 289, color: '#82ca9d' },
    { name: '3 Quartos', value: 234, color: '#ffc658' },
    { name: '4+ Quartos', value: 168, color: '#ff7c7c' }
  ];

  // Buscar propriedades
  const handleSearch = async (searchFilters) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('🔍 Iniciando busca com filtros:', searchFilters);
      const result = await propertyService.searchProperties(searchFilters);
      
      if (result.success) {
        setProperties(result.data);
        setLastUpdate(new Date().toLocaleString('pt-BR'));
        console.log('✅ Busca concluída:', result.data.length, 'propriedades');
      } else {
        setError('Erro ao buscar propriedades');
      }
    } catch (err) {
      console.error('❌ Erro na busca:', err);
      setError('Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar status dos scrapers
  const fetchScrapersStatus = async () => {
    try {
      const result = await propertyService.getScrapersStatus();
      if (result.success) {
        setScrapersStatus(result.data);
      }
    } catch (err) {
      console.error('Erro ao buscar status dos scrapers:', err);
    }
  };

  // Busca inicial
  useEffect(() => {
    handleSearch(filters);
    fetchScrapersStatus();
  }, []);

  // Atualizar filtros
  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  // Refresh manual
  const handleRefresh = () => {
    handleSearch(filters);
    fetchScrapersStatus();
  };

  // Abrir Simple Dashboard em nova aba
  const openSimpleDashboard = () => {
    window.open('http://localhost:5001', '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Home className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Sistema de Captação de Imóveis</h1>
                <p className="text-sm text-gray-500">Dashboard em tempo real</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {lastUpdate && (
                <div className="text-sm text-gray-500">
                  Última atualização: {lastUpdate}
                </div>
              )}
              
              <button
                onClick={openSimpleDashboard}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <ExternalLink className="w-4 h-4" />
                Dashboard de Monitoramento
              </button>
              
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Atualizar
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Status dos Scrapers */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Status dos Portais</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(scrapersStatus).map(([portal, status]) => (
              <div key={portal} className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900 capitalize">{portal}</h3>
                    <p className="text-sm text-gray-500">{status.description}</p>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${
                    status.status === 'active' ? 'bg-green-400' :
                    status.status === 'maintenance' ? 'bg-yellow-400' : 'bg-red-400'
                  }`} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Filtros de Busca */}
        <div className="mb-6">
          <SearchFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onSearch={handleSearch}
            isLoading={isLoading}
          />
        </div>

        {/* Acesso Rápido ao Dashboard de Monitoramento */}
        <div className="mb-6">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">📊 Dashboard de Monitoramento Avançado</h3>
                <p className="text-blue-100 mb-3">
                  Acesse métricas detalhadas, logs em tempo real e estatísticas dos portais de scraping
                </p>
                <ul className="text-sm text-blue-100 space-y-1">
                  <li>• Status detalhado dos portais (ZapImóveis, OLX, VivaReal)</li>
                  <li>• Logs do sistema em tempo real</li>
                  <li>• Gráficos de performance e alertas</li>
                  <li>• Estatísticas de CPU, memória e containers</li>
                </ul>
              </div>
              <div className="flex flex-col gap-3">
                <button
                  onClick={openSimpleDashboard}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-50 font-medium shadow-md transition-all duration-200 transform hover:scale-105"
                >
                  <ExternalLink className="w-5 h-5" />
                  Abrir Dashboard
                </button>
                <div className="text-xs text-blue-200 text-center">
                  Abre em nova aba
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Mensagem de Erro */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Resultados da Busca */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Propriedades Encontradas ({properties.length})
            </h2>
            
            {isLoading && (
              <div className="flex items-center gap-2 text-blue-600">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Carregando...</span>
              </div>
            )}
          </div>

          {/* Grid de Propriedades */}
          {properties.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {properties.map((property, index) => (
                <PropertyCard
                  key={property.id || index}
                  property={property}
                  onClick={(prop) => console.log('Propriedade clicada:', prop)}
                />
              ))}
            </div>
          ) : !isLoading && (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <Home className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma propriedade encontrada</h3>
              <p className="mt-1 text-sm text-gray-500">
                Tente ajustar os filtros para encontrar propriedades.
              </p>
            </div>
          )}
        </div>

        {/* Estatísticas Rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Home className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total de Imóveis</dt>
                  <dd className="text-lg font-medium text-gray-900">{marketData.totalProperties}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Preço Médio</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    R$ {(marketData.avgPrice / 1000000).toFixed(1)}M
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <MapPin className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Preço por m²</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    R$ {marketData.avgPricePerSqm.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Calendar className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Novos Hoje</dt>
                  <dd className="flex items-baseline">
                    <div className="text-lg font-medium text-gray-900">{marketData.newListings}</div>
                    <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                      <TrendingUp className="h-4 w-4 flex-shrink-0 self-center" />
                      <span className="sr-only">Aumento de</span>
                      {marketData.priceChange}%
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Gráfico de Novos Anúncios */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Novos Anúncios por Dia</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyListings}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="novos" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Distribuição por Quartos */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Distribuição por Quartos</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={bedroomDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {bedroomDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealEstateDashboard;
