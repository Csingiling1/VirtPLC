import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface SensorData {
  timestamp: number;
  motor1Speed: number;
  motor1Temp: number;
  motor1Run: boolean;
  motor1Fault: boolean;
  motor2Speed: number;
  motor2Temp: number;
  motor2Run: boolean;
  motor2Fault: boolean;
  conveyor1Speed: number;
  conveyor1Run: boolean;
  sensor1Value: number;
  sensor2Value: boolean;
  systemStatus: string;
}

export interface AuthResponse {
  token: string;
  username: string;
  message: string;
}

export const login = async (username: string, password: string): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/login', { username, password });
  return response.data;
};

export const getLatestData = async (): Promise<SensorData> => {
  const response = await api.get<SensorData>('/api/data/latest');
  return response.data;
};

export const getDataRange = async (startTime: number, endTime: number): Promise<SensorData[]> => {
  const response = await api.get<SensorData[]>('/api/data/range', {
    params: { startTime, endTime }
  });
  return response.data;
};

export default api;
