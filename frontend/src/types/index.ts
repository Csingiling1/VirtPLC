// API Response Types
export interface AuthResponse {
  token: string;
  username: string;
  message: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

// Sensor Data Types
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

// Simulator Device Types
export interface SignalConfig {
  name: string;
  unit: string;
  value: number;
  generator: string;
  isRunning: boolean;
  minValue?: number;
  maxValue?: number;
  mean?: number;
  stdDev?: number;
  rate?: number;
  frequency?: number;
  amplitude?: number;
  offset?: number;
  stepSize?: number;
  lastUpdate?: number;
}

export interface SimulatorDevice {
  id: string;
  name: string;
  description: string;
  deviceType: string;
  signals: SignalConfig[];
  isActive: boolean;
  createdAt: number;
  updatedAt: number;
}

// API Request Types
export interface CreateDeviceRequest {
  name: string;
  description: string;
  deviceType: string;
  signals: SignalConfig[];
}

export interface UpdateDeviceRequest {
  name?: string;
  description?: string;
  deviceType?: string;
  signals?: SignalConfig[];
  isActive?: boolean;
}

export interface SetSignalRequest {
  value: number;
}

// Simulation Status Types
export interface SimulationStatus {
  isRunning: boolean;
  deviceCount: number;
  signalCount: number;
  lastUpdate: number;
  errors: string[];
}

// Chart Data Types
export interface ChartDataPoint {
  time: string;
  [key: string]: string | number;
}

// Component Props Types
export interface LayoutProps {
  children: React.ReactNode;
}

export interface StatusCardProps {
  title: string;
  value: string | number;
  status?: 'success' | 'warning' | 'error' | 'info';
  icon?: React.ComponentType<any>;
}

// Context Types
export interface AuthContextType {
  isAuthenticated: boolean;
  user: string | null;
  login: (token: string, username: string) => void;
  logout: () => void;
}