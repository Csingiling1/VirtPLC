import { ApiClient } from './apiClient';
import { SimulatorDevice, SignalConfig, SensorData, AIChatResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const AI_API_BASE_URL = import.meta.env.VITE_AI_API_URL || 'http://localhost:3001';

// Create API clients with proper configuration
const apiClient = new ApiClient({
  baseURL: API_BASE_URL,
  timeout: 30000,
  retries: 3,
});

const aiApiClient = new ApiClient({
  baseURL: AI_API_BASE_URL,
  timeout: 60000, // Longer timeout for AI operations
  retries: 2,
});

// Data API with type-safe methods
export const dataApi = {
  getLatest: async () => {
    return apiClient.get('/api/data/latest');
  },
  getHierarchical: async () => {
    return apiClient.get('/api/data/hierarchical-live');
  },
  getRange: async (startTime: number, endTime: number, page: number = 0, size: number = 1000, query?: string) => {
    const params: Record<string, any> = {
      start_time: new Date(startTime).toISOString(),
      end_time: new Date(endTime).toISOString(),
      limit: size
    };
    if (query) {
      params.query = query;
    }
    const response = await aiApiClient.get('/api/analysis/historical', { params });
    return response.data || [];
  },
  getHealth: async () => {
    return apiClient.get('/api/data/health');
  },
};

// Simulator API with type-safe methods
export const simulatorApi = {
  getDevices: async (): Promise<SimulatorDevice[]> => {
    return apiClient.get('/api/simulator/devices');
  },
  getDevice: async (deviceId: string): Promise<SimulatorDevice> => {
    return apiClient.get(`/api/simulator/devices/${deviceId}`);
  },
  createDevice: async (device: Omit<SimulatorDevice, 'id'>): Promise<SimulatorDevice> => {
    return apiClient.post('/api/simulator/devices', device);
  },
  updateDevice: async (deviceId: string, device: Partial<SimulatorDevice>): Promise<SimulatorDevice> => {
    return apiClient.put(`/api/simulator/devices/${deviceId}`, device);
  },
  deleteDevice: async (deviceId: string): Promise<void> => {
    return apiClient.delete(`/api/simulator/devices/${deviceId}`);
  },
  getSignal: async (deviceId: string, signalName: string): Promise<SignalConfig> => {
    return apiClient.get(`/api/simulator/devices/${deviceId}/signals/${signalName}`);
  },
  setSignal: async (deviceId: string, signalName: string, value: number): Promise<SignalConfig> => {
    return apiClient.put(`/api/simulator/devices/${deviceId}/signals/${signalName}`, { value });
  },
  addSignal: async (deviceId: string, signal: Omit<SignalConfig, 'lastUpdate'>): Promise<SignalConfig> => {
    return apiClient.post(`/api/simulator/devices/${deviceId}/signals`, signal);
  },
  getStatus: async () => {
    return apiClient.get('/api/simulator/status');
  },
  triggerUpdate: async () => {
    return apiClient.post('/api/simulator/update', {});
  },
};

// AI API functions with type-safe methods
export const aiApiFunctions = {
  chat: async (message: string, context?: string, model: 'ollama' | 'claude' = 'ollama'): Promise<AIChatResponse> => {
    return aiApiClient.post('/api/chat/message', {
      message,
      context: context ? { description: context } : null,
      model,
    });
  },
  getAnalysis: async (data: { sensorData?: SensorData[]; timeRange?: { start: number; end: number } }) => {
    return aiApiClient.post('/analyze', data);
  },
  getInsights: async (timeRange?: { start: number; end: number }) => {
    return aiApiClient.get('/insights', { params: timeRange });
  },
};

// Export the clients for direct use if needed
export { apiClient, aiApiClient };

