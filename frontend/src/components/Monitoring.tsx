import { useState, useEffect } from 'react';
import Layout from './Layout';
import { dataApi } from '../services/api';
import { SensorData } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useToast } from '../hooks/use-toast';

const Monitoring = () => {
  const [historicalData, setHistoricalData] = useState<SensorData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await dataApi.getLatest();
        setHistoricalData((prev) => {
          const newData = [...prev, data];
          return newData.slice(-50); // Keep last 50 data points
        });
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        toast({
          title: "Connection Error",
          description: "Failed to fetch monitoring data",
          variant: "destructive",
        });
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);

    return () => clearInterval(interval);
  }, [toast]);

  const chartData = historicalData.map((data) => ({
    time: new Date(data.timestamp).toLocaleTimeString(),
    motor1Speed: data.motor1Speed,
    motor2Speed: data.motor2Speed,
    motor1Temp: data.motor1Temp,
    motor2Temp: data.motor2Temp,
    conveyorSpeed: data.conveyor1Speed,
  }));

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-primary text-lg">Loading monitoring data...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Live Monitoring</h1>
          <p className="text-muted-foreground">Real-time data visualization and trends</p>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Motor Speed Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="time"
                    stroke="hsl(var(--foreground))"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis
                    stroke="hsl(var(--foreground))"
                    style={{ fontSize: '12px' }}
                    label={{ value: 'RPM', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="motor1Speed"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth={2}
                    dot={false}
                    name="Motor 1"
                  />
                  <Line
                    type="monotone"
                    dataKey="motor2Speed"
                    stroke="hsl(var(--chart-2))"
                    strokeWidth={2}
                    dot={false}
                    name="Motor 2"
                  />
                  <Line
                    type="monotone"
                    dataKey="conveyorSpeed"
                    stroke="hsl(var(--chart-3))"
                    strokeWidth={2}
                    dot={false}
                    name="Conveyor"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Temperature Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="time"
                    stroke="hsl(var(--foreground))"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis
                    stroke="hsl(var(--foreground))"
                    style={{ fontSize: '12px' }}
                    label={{ value: '°C', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="motor1Temp"
                    stroke="hsl(var(--chart-4))"
                    strokeWidth={2}
                    dot={false}
                    name="Motor 1 Temp"
                  />
                  <Line
                    type="monotone"
                    dataKey="motor2Temp"
                    stroke="hsl(var(--chart-5))"
                    strokeWidth={2}
                    dot={false}
                    name="Motor 2 Temp"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Monitoring;
