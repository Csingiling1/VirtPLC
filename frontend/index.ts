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
  isActive: boolean;
  createdAt: number;
  updatedAt: number;
}

export interface SimulatorStatus {
  isRunning: boolean;
  activeDevices: number;
  totalSignals: number;
  lastUpdate: number;
}
