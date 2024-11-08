import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { Loader2, CloudRain, Wind, Thermometer, Droplets } from 'lucide-react';

// Initialize Supabase client
const supabase = createClient(
  "SUPABASE_URL",
  "SUPABASE_KEY"
);

export default function WeatherDashboard() {
  const [weatherData, setWeatherData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWeatherData();
  }, []);

  const fetchWeatherData = async () => {
    try {
      const { data, error } = await supabase
        .from('weather_analysis')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(10);

      if (error) throw error;

      // Parse the weather_data JSON string for each record
      const parsedData = data.map(record => ({
        ...record,
        weather_data: JSON.parse(record.weather_data)
      }));

      setWeatherData(parsedData);
      setLoading(false);
    } catch (err) {
      setError('Error fetching weather data');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Weather Analysis Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {weatherData.map((city) => (
          <div key={city.id} className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">{city.location}</h2>
              <span className="text-gray-500">{city.country}</span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="flex items-center">
                <Thermometer className="h-5 w-5 text-red-500 mr-2" />
                <span>{city.weather_data.temperature}°C</span>
              </div>
              
              <div className="flex items-center">
                <Wind className="h-5 w-5 text-blue-500 mr-2" />
                <span>{city.weather_data.wind_kph} km/h</span>
              </div>
              
              <div className="flex items-center">
                <Droplets className="h-5 w-5 text-blue-400 mr-2" />
                <span>{city.weather_data.humidity}%</span>
              </div>
              
              <div className="flex items-center">
                <CloudRain className="h-5 w-5 text-gray-500 mr-2" />
                <span className="truncate">{city.weather_data.condition}</span>
              </div>
            </div>
            
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-600 mb-2">AI Analysis:</h3>
              <p className="text-sm text-gray-700">{city.ai_analysis}</p>
            </div>
            
            <div className="mt-4 text-xs text-gray-500">
              Last updated: {new Date(city.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
      
      <button 
        onClick={fetchWeatherData}
        className="mt-8 mx-auto block bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
      >
        Refresh Data
      </button>
    </div>
  );
}