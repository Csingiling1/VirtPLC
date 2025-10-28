import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import type {
  AuthResponse,
  LoginRequest,
  SensorData,
  SimulatorDevice,
  CreateDeviceRequest,
  UpdateDeviceRequest,
  SetSignalRequest,
  SignalConfig,
  SimulationStatus
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

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
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
};

// Data API
export const dataApi = {
  getLatest: async (): Promise<SensorData> => {
    const response = await api.get('/api/data/latest');
    return response.data;
  },
  getRange: async (startTime: number, endTime: number): Promise<SensorData[]> => {
    const response = await api.get('/api/data/range', {
      params: { startTime, endTime },
    });
    return response.data;
  },
  getHealth: async (): Promise<string> => {
    const response = await api.get('/api/data/health');
    return response.data;
  },
};

// Simulator API
export const simulatorApi = {
  getDevices: async (): Promise<SimulatorDevice[]> => {
    const response = await api.get('/api/simulator/devices');
    return response.data;
  },
  getDevice: async (deviceId: string): Promise<SimulatorDevice> => {
    const response = await api.get(`/api/simulator/devices/${deviceId}`);
    return response.data;
  },
  createDevice: async (device: CreateDeviceRequest): Promise<SimulatorDevice> => {
    const response = await api.post('/api/simulator/devices', device);
    return response.data;
  },
  updateDevice: async (deviceId: string, device: UpdateDeviceRequest): Promise<SimulatorDevice> => {
    const response = await api.put(`/api/simulator/devices/${deviceId}`, device);
    return response.data;
  },
  deleteDevice: async (deviceId: string): Promise<void> => {
    const response = await api.delete(`/api/simulator/devices/${deviceId}`);
    return response.data;
  },
  getSignal: async (deviceId: string, signalName: string): Promise<{ deviceId: string; signalName: string; value: number }> => {
    const response = await api.get(`/api/simulator/devices/${deviceId}/signals/${signalName}`);
    return response.data;
  },
  setSignal: async (deviceId: string, signalName: string, request: SetSignalRequest): Promise<void> => {
    const response = await api.put(`/api/simulator/devices/${deviceId}/signals/${signalName}`, request);
    return response.data;
  },
  addSignal: async (deviceId: string, signal: SignalConfig): Promise<void> => {
    const response = await api.post(`/api/simulator/devices/${deviceId}/signals`, signal);
    return response.data;
  },
  getStatus: async (): Promise<SimulationStatus> => {
    const response = await api.get('/api/simulator/status');
    return response.data;
  },
  triggerUpdate: async (): Promise<void> => {
    const response = await api.post('/api/simulator/update');
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
