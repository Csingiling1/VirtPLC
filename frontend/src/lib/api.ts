import axios from 'axios';
import { SimulatorDevice, SignalConfig, SensorData, AIChatResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const AI_API_BASE_URL = import.meta.env.VITE_AI_API_URL || 'http://localhost:3001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (!error.response) {
      console.error('Network error: Backend API is not reachable at', API_BASE_URL);
      return Promise.reject({
        message: 'Backend API is not reachable. Please ensure the server is running.',
        isNetworkError: true,
        ...error
      });
    }
    
    return Promise.reject(error);
  }
);

// Data API
export const dataApi = {
  getLatest: async () => {
    const response = await api.get('/api/data/latest');
    return response.data;
  },
  getRange: async (startTime: number, endTime: number, page: number = 0, size: number = 1000, query?: string) => {
    // Use AI service historical data endpoint
    const params: any = { 
      start_time: new Date(startTime).toISOString(),
      end_time: new Date(endTime).toISOString(),
      limit: size 
    };
    if (query) {
      params.query = query;
    }
    const response = await aiApi.get('/api/analysis/historical', { params });
    // AI service returns { data: array, count: number }
    return response.data.data || [];
  },
  getHealth: async () => {
    const response = await api.get('/api/data/health');
    return response.data;
  },
};

// Simulator API
export const simulatorApi = {
  getDevices: async () => {
    const response = await api.get('/api/simulator/devices');
    return response.data;
  },
  getDevice: async (deviceId: string) => {
    const response = await api.get(`/api/simulator/devices/${deviceId}`);
    return response.data;
  },
  createDevice: async (device) => {
    const response = await api.post('/api/simulator/devices', device);
    return response.data;
  },
  updateDevice: async (deviceId: string, device: Partial<SimulatorDevice>) => {
    const response = await api.put(`/api/simulator/devices/${deviceId}`, device);
    return response.data;
  },
  deleteDevice: async (deviceId: string) => {
    const response = await api.delete(`/api/simulator/devices/${deviceId}`);
    return response.data;
  },
  getSignal: async (deviceId: string, signalName: string) => {
    const response = await api.get(`/api/simulator/devices/${deviceId}/signals/${signalName}`);
    return response.data;
  },
  setSignal: async (deviceId: string, signalName: string, value: number) => {
    const response = await api.put(`/api/simulator/devices/${deviceId}/signals/${signalName}`, { value });
    return response.data;
  },
  addSignal: async (deviceId: string, signal: Omit<SignalConfig, 'lastUpdate'>) => {
    const response = await api.post(`/api/simulator/devices/${deviceId}/signals`, signal);
    return response.data;
  },
  getStatus: async () => {
    const response = await api.get('/api/simulator/status');
    return response.data;
  },
  triggerUpdate: async () => {
    const response = await api.post('/api/simulator/update');
    return response.data;
  },
};

export const aiApi = axios.create({
  baseURL: AI_API_BASE_URL,
  timeout: 30000, // Longer timeout for AI operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for AI API error handling
aiApi.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (!error.response) {
      console.error('Network error: AI API is not reachable at', AI_API_BASE_URL);
      return Promise.reject({
        message: 'AI API is not reachable. Please ensure the AI service is running.',
        isNetworkError: true,
        ...error
      });
    }
    
    return Promise.reject(error);
  }
);

// AI API functions
export const aiApiFunctions = {
  chat: async (message: string, context?: string): Promise<AIChatResponse> => {
    const response = await aiApi.post('/api/chat/message', {
      message,
      context: context ? { description: context } : null,
    });
    return response.data;
  },
  getAnalysis: async (data: { sensorData?: SensorData[]; timeRange?: { start: number; end: number } }) => {
    const response = await aiApi.post('/analyze', data);
    return response.data;
  },
  getInsights: async (timeRange?: { start: number; end: number }) => {
    const response = await aiApi.get('/insights', {
      params: timeRange,
    });
    return response.data;
  },
};

