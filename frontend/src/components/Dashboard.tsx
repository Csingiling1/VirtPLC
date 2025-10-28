import { useState, useEffect } from 'react';
import Layout from './Layout';
import StatusCard from './StatusCard';
import { dataApi } from '../services/api';
import { SensorData } from '../types';
import { Activity, Gauge, ThermometerSun, AlertCircle, CheckCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Dashboard = () => {
  const [sensorData, setSensorData] = useState<SensorData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await dataApi.getLatest();
        setSensorData(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        toast({
          title: "Connection Error",
          description: "Failed to fetch sensor data",
          variant: "destructive",
        });
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);

    return () => clearInterval(interval);
  }, [toast]);

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-primary text-lg">Loading dashboard...</div>
        </div>
      </Layout>
    );
  }

  const getMotorStatus = (isRunning: boolean, hasFault: boolean) => {
    if (hasFault) return 'danger';
    if (isRunning) return 'success';
    return 'warning';
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">System Dashboard</h1>
          <p className="text-muted-foreground">Real-time factory monitoring and control</p>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="System Status"
            value={sensorData?.systemStatus || 'Unknown'}
            icon={sensorData?.systemStatus === 'Running' ? CheckCircle : AlertCircle}
            status={sensorData?.systemStatus === 'Running' ? 'success' : 'warning'}
          />
          <StatusCard
            title="Motor 1 Speed"
            value={`${sensorData?.motor1Speed.toFixed(0) || 0} RPM`}
            icon={Gauge}
            status={getMotorStatus(sensorData?.motor1Run || false, sensorData?.motor1Fault || false)}
            subtitle={sensorData?.motor1Run ? 'Running' : 'Stopped'}
          />
          <StatusCard
            title="Motor 1 Temperature"
            value={`${sensorData?.motor1Temp.toFixed(1) || 0}°C`}
            icon={ThermometerSun}
            status={(sensorData?.motor1Temp || 0) > 80 ? 'danger' : 'success'}
          />
          <StatusCard
            title="Sensor 1 Value"
            value={sensorData?.sensor1Value.toFixed(2) || 0}
            icon={Activity}
            status="info"
          />
        </div>

        {/* Motor 2 Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="Motor 2 Speed"
            value={`${sensorData?.motor2Speed.toFixed(0) || 0} RPM`}
            icon={Gauge}
            status={getMotorStatus(sensorData?.motor2Run || false, sensorData?.motor2Fault || false)}
            subtitle={sensorData?.motor2Run ? 'Running' : 'Stopped'}
          />
          <StatusCard
            title="Motor 2 Temperature"
            value={`${sensorData?.motor2Temp.toFixed(1) || 0}°C`}
            icon={ThermometerSun}
            status={(sensorData?.motor2Temp || 0) > 80 ? 'danger' : 'success'}
          />
          <StatusCard
            title="Conveyor Speed"
            value={`${sensorData?.conveyor1Speed.toFixed(0) || 0} m/min`}
            icon={Gauge}
            status={sensorData?.conveyor1Run ? 'success' : 'warning'}
            subtitle={sensorData?.conveyor1Run ? 'Running' : 'Stopped'}
          />
          <StatusCard
            title="Sensor 2 Status"
            value={sensorData?.sensor2Value ? 'Active' : 'Inactive'}
            icon={Activity}
            status={sensorData?.sensor2Value ? 'success' : 'warning'}
          />
        </div>

        {/* Quick Info */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Last Update:</span>{' '}
              <span className="text-foreground font-medium">
                {new Date(sensorData?.timestamp || Date.now()).toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Active Motors:</span>{' '}
              <span className="text-foreground font-medium">
                {[sensorData?.motor1Run, sensorData?.motor2Run].filter(Boolean).length} / 2
              </span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
