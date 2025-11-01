import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useToast } from '@/hooks/use-toast';
import { Server } from 'lucide-react';

interface HierarchicalSensorData {
  timestamp: number;
  tenants: Array<{
    id: string;
    name: string;
    manufacturers: Array<{
      id: string;
      name: string;
      factories: Array<{
        id: string;
        name: string;
        plcs: Array<{
          id: string;
          name: string;
          sensors: Array<{
            id: string;
            name: string;
            value: number;
            unit: string;
            timestamp: number;
          }>;
        }>;
      }>;
    }>;
  }>;
}

const Monitoring = () => {
  const [historicalData, setHistoricalData] = useState<HierarchicalSensorData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/stream/latest');
        const data: HierarchicalSensorData = await response.json();
        setHistoricalData((prev) => {
          const newData = [...prev, data];
          return newData.slice(-20); // Keep last 20 data points
        });
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch data:', error);

        const errorMessage = (error as { isNetworkError?: boolean; message?: string }).isNetworkError
          ? "Cannot connect to simulator API. Please check the simulator is running."
          : "Failed to fetch monitoring data. Please try again.";

        if (isLoading) {
          // Only show toast on initial load failure
          toast({
            title: "Connection Error",
            description: errorMessage,
            variant: "destructive",
          });
        }
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);

    return () => clearInterval(interval);
  }, [toast, isLoading]);

  interface ChartDataPoint {
    time: string;
    [key: string]: string | number;
  }

  // Extract key metrics from hierarchical data for charting
  const chartData: ChartDataPoint[] = historicalData.map((data) => {
    const metrics: ChartDataPoint = {
      time: new Date(data.timestamp).toLocaleTimeString(),
    };

    // Extract some key sensor values for monitoring
    let sensorCount = 0;
    data.tenants?.forEach(tenant => {
      tenant.manufacturers?.forEach(manufacturer => {
        manufacturer.factories?.forEach(factory => {
          factory.plcs?.forEach(plc => {
            plc.sensors?.forEach(sensor => {
              sensorCount++;
              // Add first few sensors as chart lines
              if (sensorCount <= 6) {
                const key = sensor.name.replace(/\s+/g, '').toLowerCase();
                metrics[key] = sensor.value;
                metrics[`${key}Unit`] = sensor.unit;
              }
            });
          });
        });
      });
    });

    return metrics;
  });

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
              <CardTitle>Real-time Sensor Monitoring</CardTitle>
              <p className="text-sm text-muted-foreground">Live data from factory sensors across all facilities</p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
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
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  {chartData.length > 0 && Object.keys(chartData[0])
                    .filter(key => key !== 'time' && !key.endsWith('Unit'))
                    .slice(0, 6)
                    .map((key, index) => {
                      const colors = ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))', 'hsl(var(--chart-5))', 'hsl(var(--chart-6))'];
                      const unit = chartData[0][`${key}Unit`] || '';
                      return (
                        <Line
                          key={key}
                          type="monotone"
                          dataKey={key}
                          stroke={colors[index % colors.length]}
                          strokeWidth={2}
                          dot={false}
                          name={`${key} ${unit ? `(${unit})` : ''}`}
                        />
                      );
                    })}
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Device-specific monitoring */}
          {historicalData.length > 0 && historicalData[historicalData.length - 1].tenants?.map((tenant) =>
            tenant.manufacturers?.map((manufacturer) =>
              manufacturer.factories?.map((factory) =>
                factory.plcs?.map((plc) => (
                  <Card key={plc.id}>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Server className="h-5 w-5" />
                        {plc.name}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {factory.name} • {manufacturer.name} • {tenant.name}
                      </p>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {plc.sensors?.map((sensor) => (
                          <div key={sensor.id} className="text-center">
                            <div className="text-2xl font-bold text-primary">
                              {sensor.value.toFixed(1)}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {sensor.name}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {sensor.unit}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )
            )
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Active Tenants:</span>
                    <span className="text-sm font-medium">
                      {historicalData.length > 0 ? historicalData[historicalData.length - 1].tenants?.length || 0 : 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Total Sensors:</span>
                    <span className="text-sm font-medium">
                      {historicalData.length > 0 ? (() => {
                        let count = 0;
                        historicalData[historicalData.length - 1].tenants?.forEach(tenant => {
                          tenant.manufacturers?.forEach(manufacturer => {
                            manufacturer.factories?.forEach(factory => {
                              factory.plcs?.forEach(plc => {
                                count += plc.sensors?.length || 0;
                              });
                            });
                          });
                        });
                        return count;
                      })() : 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Data Points:</span>
                    <span className="text-sm font-medium">{chartData.length}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Latest Values</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {historicalData.length > 0 && (() => {
                    const latest = historicalData[historicalData.length - 1];
                    const sensors: Array<{ name: string, value: number, unit: string }> = [];

                    latest.tenants?.forEach(tenant => {
                      tenant.manufacturers?.forEach(manufacturer => {
                        manufacturer.factories?.forEach(factory => {
                          factory.plcs?.forEach(plc => {
                            plc.sensors?.slice(0, 8).forEach(sensor => {
                              sensors.push({
                                name: sensor.name,
                                value: sensor.value,
                                unit: sensor.unit
                              });
                            });
                          });
                        });
                      });
                    });

                    return sensors.slice(0, 8).map((sensor, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="text-muted-foreground truncate mr-2">{sensor.name}:</span>
                        <span className="font-medium">
                          {sensor.value.toFixed(1)} {sensor.unit}
                        </span>
                      </div>
                    ));
                  })()}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Monitoring;
