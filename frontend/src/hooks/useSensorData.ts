import { useState, useEffect } from 'react';
import { dataApi } from '../services/api';
import { SensorData } from '../types';

export function useSensorData(refreshInterval: number = 2000) {
  const [data, setData] = useState<SensorData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await dataApi.getLatest();
        setData(result);
        setError(null);
      } catch (err) {
        setError('Failed to fetch sensor data');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Set up polling
    const interval = setInterval(fetchData, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { data, loading, error };
}
