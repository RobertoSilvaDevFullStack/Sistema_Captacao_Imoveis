import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Home, MapPin, DollarSign, Calendar, ExternalLink, Filter, Search } from 'lucide-react';

const RealEstateDashboard = () => {
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedNeighborhood, setSelectedNeighborhood] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Dados mockados para demonstração
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

  const neighborhoodData = [
    { name: 'Copacabana', properties: 156, avgPrice: 980000, avgPricePerSqm: 9200 },
    { name: 'Ipanema', properties: 89, avgPrice: 1850000, avgPricePerSqm: 12500 },
    { name: 'Leblon', properties: 67, avgPrice: 2200000, avgPricePerSqm: 15000 },
    { name: 'Botafogo', properties: 134, avgPrice: 750000, avgPricePerSqm: 7800 },
    { name: 'Flamengo', properties: 112, avgPrice: 890000, avgPricePerSqm: 8900 },
    { name: 'Lagoa', properties: 78, avgPrice: 1650000, avgPricePerSqm: 11200 },
    { name: 'Jardim Botânico', properties: 45, avgPrice: 1920000, avgPricePerSqm: 13800 },
    { name: 'Humaitá', properties: 56, avgPrice: 1150000, avgPricePerSqm: 9800 },
    { name: 'Urca', properties: 34, avgPrice: 1450000, avgPricePerSqm: 10500 },
    { name: 'Leme', properties: 76, avgPrice: 1100000, avgPricePerSqm: 9500 }
  ];

  const bedroomDistribution = [
    { name: '1 Quarto', value: 156, color: '#8884d8' },
    { name: '2 Quartos', value: 289, color: '#82ca9d' },
    { name: '3 Quartos', value: 234, color: '#ffc658' },
    { name: '4+ Quartos', value: 168, color: '#ff7c7c' }
  ];

  const priceRanges = [
    { range: 'Até R$ 500k', count: 89 },
    { range: 'R$ 500k - R$ 1M', count: 234 },
    { range: 'R$ 1M - R$ 1.5M', count: 198 },
    { range: 'R$ 1.5M - R$ 2M', count: 156 },
    { range: 'R$ 2M - R$ 3M', count: 123 },
    { range: 'Acima de R$ 3M', count: 47 }
  ];

  const recentProperties = [
    {
      id: 1,
      title: 'Apartamento 3 quartos em Copacabana',
      price: 950000,
      neighborhood: 'Copacabana',
      bedrooms: 3,
      area: 95,
      url: 'https://www.vivareal.com.br/imovel/apartamento-3-quartos-copacabana',
      source: 'VivaReal',
      addedDate: '2024-07-16'
    },
    {
      id: 2,
      title: 'Cobertura duplex em Ipanema',
      price: 2850000,
      neighborhood: 'Ipanema',
      bedrooms: 4,
      area: 180,
      url: 'https://www.zapimoveis.com.br/imovel/cobertura-ipanema',
      source: 'ZapImóveis',
      addedDate: '2024-07-16'
    },
    {
      id: 3,
      title: 'Apartamento 2 quartos no Leblon',
      price: 1650000,
      neighborhood: 'Leblon',
      bedrooms: 2,
      area: 85,
      url: 'https://www.vivareal.com.br/imovel/apartamento-2-quartos-leblon',
      source: 'VivaReal',
      addedDate: '2024-07-16'
    },
    {
      id: 4,
      title: 'Studio em Botafogo',
      price: 480000,
      neighborhood: 'Botafogo',
      bedrooms: 1,
      area: 45,
      url: 'https://www.olx.com.br/imovel/studio-botafogo',
      source: 'OLX',
      addedDate: '2024-07-15'
    },
    {
      id: 5,
      title: 'Apartamento 3 quartos no Flamengo',
      price: 1120000,
      neighborhood: 'Flamengo',
      bedrooms: 3,
      area: 110,
      url: 'https://www.zapimoveis.com.br/imovel/apartamento-flamengo',
      source: 'ZapImóveis',
      addedDate: '2024-07-15'
    }
  ];

  const opportunities = [
    {
      id: 1,
      title: 'Oportunidade: Apartamento 3 quartos - Copacabana',
      price: 780000,
      marketPrice: 980000,
      discount: 20.4,
      neighborhood: 'Copacabana',
      bedrooms: 3,
      area: 88,
      url: 'https://www.vivareal.com.br/imovel/oportunidade-copacabana',
      source: 'VivaReal',
      reason: 'Preço 20% abaixo da média do bairro'
    },
    {
      id: 2,
      title: 'Oportunidade: Cobertura 4 quartos - Botafogo',
      price: 1200000,
      marketPrice: 1500000,
      discount: 20.0,
      neighborhood: 'Botafogo',
      bedrooms: 4,
      area: 160,
      url: 'https://www.zapimoveis.com.br/imovel/cobertura-botafogo',
      source: 'ZapImóveis',
      reason: 'Preço por m² muito atrativo'
    },
    {
      id: 3,
      title: 'Oportunidade: Apartamento 2 quartos - Flamengo',
      price: 650000,
      marketPrice: 890000,
      discount: 27.0,
      neighborhood: 'Flamengo',
      bedrooms: 2,
      area: 75,
      url: 'https://www.vivareal.com.br/imovel/apartamento-flamengo-oportunidade',
      source: 'VivaReal',
      reason: 'Preço 27% abaixo da média - análise urgente'
    }
  ];

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(price);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('pt-BR').format(num);
  };

  const filteredNeighborhoods = selectedNeighborhood === 'all' 
    ? neighborhoodData 
    : neighborhoodData.filter(n => n.name === selectedNeighborhood);

  const filteredProperties = recentProperties.filter(prop => {
    const matchesSearch = searchTerm === '' || 
      prop.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prop.neighborhood.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesNeighborhood = selectedNeighborhood === 'all' || 
      prop.neighborhood === selectedNeighborhood;
    
    return matchesSearch && matchesNeighborhood;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Dashboard de Análise de Imóveis
          </h1>
          <p className="text-blue-200 text-lg">
            Zona Sul - Rio de Janeiro | Última atualização: 16/07/2024 às 14:30
          </p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Total de Imóveis</p>
                <p className="text-3xl font-bold text-white">{formatNumber(marketData.totalProperties)}</p>
              </div>
              <Home className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Preço Médio</p>
                <p className="text-2xl font-bold text-white">{formatPrice(marketData.avgPrice)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-green-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Preço por m²</p>
                <p className="text-2xl font-bold text-white">{formatPrice(marketData.avgPricePerSqm)}</p>
              </div>
              <MapPin className="w-8 h-8 text-purple-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Novos Hoje</p>
                <p className="text-3xl font-bold text-white">{marketData.newListings}</p>
              </div>
              <Calendar className="w-8 h-8 text-yellow-400" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-200 text-sm">Variação do Mês</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-green-400">+{marketData.priceChange}%</p>
                  <TrendingUp className="w-5 h-5 text-green-400" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filtros */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-blue-400" />
              <label className="text-white font-medium">Bairro:</label>
              <select 
                className="bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-600"
                value={selectedNeighborhood}
                onChange={(e) => setSelectedNeighborhood(e.target.value)}
              >
                <option value="all">Todos os bairros</option>
                {neighborhoodData.map(n => (
                  <option key={n.name} value={n.name}>{n.name}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <Search className="w-5 h-5 text-blue-400" />
              <input
                type="text"
                placeholder="Buscar imóveis..."
                className="bg-slate-800 text-white px-3 py-2 rounded-lg border border-slate-600"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Gráficos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Tendência de Novos Imóveis */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Novos Imóveis - Últimos 7 dias</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dailyListings}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }} 
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="novos" 
                  stroke="#3B82F6" 
                  strokeWidth={3}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  name="Novos Imóveis"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Distribuição por Quartos */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Distribuição por Quartos</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={bedroomDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {bedroomDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Análise por Bairro */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">Análise por Bairro</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={filteredNeighborhoods}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }} 
                formatter={(value, name) => [
                  name === 'avgPrice' ? formatPrice(value) : formatNumber(value),
                  name === 'properties' ? 'Imóveis' : 
                  name === 'avgPrice' ? 'Preço Médio' : 'Preço por m²'
                ]}
              />
              <Legend />
              <Bar dataKey="properties" fill="#3B82F6" name="Quantidade" />
              <Bar dataKey="avgPrice" fill="#10B981" name="Preço Médio" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Oportunidades */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 mb-8">
          <h3 className="text-xl font-bold text-white mb-4">🎯 Oportunidades de Captação</h3>
          <div className="grid gap-4">
            {opportunities.map((opp) => (
              <div key={opp.id} className="bg-gradient-to-r from-red-900/30 to-orange-900/30 p-4 rounded-lg border border-red-500/30">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-semibold text-white text-lg">{opp.title}</h4>
                    <p className="text-orange-200 text-sm mb-2">{opp.reason}</p>
                    <div className="flex gap-4 text-sm text-blue-200">
                      <span>{opp.neighborhood}</span>
                      <span>{opp.bedrooms} quartos</span>
                      <span>{opp.area}m²</span>
                      <span className="text-green-400 font-medium">{opp.source}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-400">{formatPrice(opp.price)}</div>
                    <div className="text-sm text-gray-400 line-through">{formatPrice(opp.marketPrice)}</div>
                    <div className="text-sm text-red-400 font-bold">-{opp.discount}%</div>
                    <a 
                      href={opp.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mt-2 bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-white text-sm transition-colors"
                    >
                      Ver Imóvel <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lista de Imóveis Recentes */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4">
            Imóveis Recentes ({filteredProperties.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/20">
                  <th className="py-3 px-4 text-blue-200">Título</th>
                  <th className="py-3 px-4 text-blue-200">Bairro</th>
                  <th className="py-3 px-4 text-blue-200">Preço</th>
                  <th className="py-3 px-4 text-blue-200">Quartos</th>
                  <th className="py-3 px-4 text-blue-200">Área</th>
                  <th className="py-3 px-4 text-blue-200">Fonte</th>
                  <th className="py-3 px-4 text-blue-200">Ações</th>
                </tr>
              </thead>
              <tbody>
                {filteredProperties.map((property) => (
                  <tr key={property.id} className="border-b border-white/10 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4 text-white">{property.title}</td>
                    <td className="py-3 px-4 text-blue-200">{property.neighborhood}</td>
                    <td className="py-3 px-4 text-green-400 font-semibold">{formatPrice(property.price)}</td>
                    <td className="py-3 px-4 text-white">{property.bedrooms}</td>
                    <td className="py-3 px-4 text-white">{property.area}m²</td>
                    <td className="py-3 px-4 text-purple-400">{property.source}</td>
                    <td className="py-3 px-4">
                      <a 
                        href={property.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-white text-sm transition-colors"
                      >
                        Ver <ExternalLink className="w-3 h-3" />
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-blue-200">
          <p>Sistema de Análise de Imóveis - Desenvolvido para otimizar sua captação</p>
          <p className="text-sm mt-2">Dados coletados de VivaReal, ZapImóveis e OLX</p>
        </div>
      </div>
    </div>
  );
};

export default RealEstateDashboard;