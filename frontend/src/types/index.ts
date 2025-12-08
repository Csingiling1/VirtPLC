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
  is_active: boolean;
  created_at: number;
  updated_at: number;
}

export interface SimulatorStatus {
  isRunning: boolean;
  activeDevices: number;
  totalSignals: number;
  lastUpdate: number;
}

export interface AIChatRequest {
  message: string;
  context?: { description: string };
}

export interface ChartSuggestion {
  type: string;
  title: string;
  description: string;
  data_source?: string;
  symbols?: string[];
  metrics?: string[];
  time_range?: string;
  data?: any[]; // Allow direct data injection
  devices?: string[]; // Add devices field which was used in AIChart
}

export interface AIChatResponse {
  response: string;
  session_id: number;
  metadata?: {
    model: string;
    tokens_used: number;
    context_symbols: string[];
    backend_data_accessed: boolean;
  };
  chart_suggestions?: ChartSuggestion[];
}
