import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
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
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname;
      // Only redirect if not already on login page
      if (currentPath !== '/login') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
};

// Data API
export const dataApi = {
  getLatest: async () => {
    const response = await api.get('/api/data/latest');
    return response.data;
  },
  getRange: async (startTime: number, endTime: number) => {
    const response = await api.get('/api/data/range', {
      params: { startTime, endTime },
    });
    return response.data;
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
  createDevice: async (device: any) => {
    const response = await api.post('/api/simulator/devices', device);
    return response.data;
  },
  updateDevice: async (deviceId: string, device: any) => {
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
  addSignal: async (deviceId: string, signal: any) => {
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

// AI API
export const aiApi = {
  chat: async (message: string, context?: string): Promise<{ response: string }> => {
    const response = await api.post('/ai/chat', { message, context });
    return response.data;
  },
  getChatHistory: async (): Promise<any[]> => {
    const response = await api.get('/ai/chat/history');
    return response.data;
  },
};

export const isTokenValid = (token: string): boolean => {
  try {
    const decoded: any = jwtDecode(token);
    return decoded.exp * 1000 > Date.now();
  } catch {
    return false;
  }
};
