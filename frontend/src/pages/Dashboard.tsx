import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import StatusCard from '@/components/StatusCard';
import { dataApi } from '@/lib/api';
import { SensorData } from '@/types';
import { Activity, Gauge, ThermometerSun, AlertCircle, CheckCircle, Building, Factory, MapPin, Server } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface HierarchicalSensorData {
  tenants: Array<{
    id: string;
    name: string;
    description: string;
    manufacturers: Array<{
      id: string;
      name: string;
      description: string;
      factories: Array<{
        id: string;
        name: string;
        description: string;
        plcs: Array<{
          id: string;
          name: string;
          description: string;
          sensors: Array<{
            id: string;
            name: string;
            value: number;
            unit: string;
          }>;
        }>;
      }>;
    }>;
  }>;
}

const Dashboard = () => {
  const [sensorData, setSensorData] = useState<HierarchicalSensorData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/stream/latest');
        const data = await response.json();
        setSensorData(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch data:', error);

        const errorMessage = error.isNetworkError
          ? "Cannot connect to simulator API. Please check the simulator is running."
          : "Failed to fetch sensor data. Please try again.";

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
          <h1 className="text-3xl font-bold mb-2">Company Name Dashboard</h1>
          <p className="text-muted-foreground">Real-time factory monitoring and control</p>
        </div>

        {sensorData?.tenants ? (
          <div className="space-y-8">
            {sensorData.tenants.map((tenant) => (
              <div key={tenant.id} className="space-y-6">
                <div className="flex items-center gap-3">
                  <Building className="h-8 w-8 text-primary" />
                  <div>
                    <h2 className="text-2xl font-bold">{tenant.name}</h2>
                    <p className="text-muted-foreground">{tenant.description}</p>
                  </div>
                </div>

                {tenant.manufacturers?.map((manufacturer) => (
                  <div key={manufacturer.id} className="ml-8 space-y-4">
                    <div className="flex items-center gap-3">
                      <Factory className="h-6 w-6 text-blue-500" />
                      <div>
                        <h3 className="text-xl font-semibold">{manufacturer.name}</h3>
                        <p className="text-sm text-muted-foreground">{manufacturer.description}</p>
                      </div>
                    </div>

                    {manufacturer.factories?.map((factory) => (
                      <div key={factory.id} className="ml-8 space-y-4">
                        <div className="flex items-center gap-3">
                          <MapPin className="h-5 w-5 text-green-500" />
                          <div>
                            <h4 className="text-lg font-medium">{factory.name}</h4>
                            <p className="text-sm text-muted-foreground">{factory.description}</p>
                          </div>
                        </div>

                        <div className="ml-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {factory.plcs?.map((plc) => (
                            <Card key={plc.id} className="border-l-4 border-l-primary">
                              <CardHeader className="pb-3">
                                <div className="flex items-center gap-2">
                                  <Server className="h-4 w-4 text-primary" />
                                  <CardTitle className="text-base">{plc.name}</CardTitle>
                                </div>
                                <CardDescription>{plc.description}</CardDescription>
                              </CardHeader>
                              <CardContent>
                                <div className="space-y-2">
                                  {plc.sensors?.slice(0, 4).map((sensor) => (
                                    <div key={sensor.id} className="flex items-center justify-between text-sm">
                                      <span className="text-muted-foreground">{sensor.name}:</span>
                                      <span className="font-medium">
                                        {sensor.value?.toFixed(1)} {sensor.unit}
                                      </span>
                                    </div>
                                  ))}
                                  {plc.sensors?.length > 4 && (
                                    <div className="text-xs text-muted-foreground text-center">
                                      +{plc.sensors.length - 4} more sensors
                                    </div>
                                  )}
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatusCard
              title="System Status"
              value="Loading..."
              icon={Activity}
              status="info"
            />
          </div>
        )}

        {/* Quick Info */}
        <div className="bg-card border border-border rounded-lg p-6 mt-8">
          <h2 className="text-xl font-semibold mb-4">System Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Active Tenants:</span>{' '}
              <span className="text-foreground font-medium">
                {sensorData?.tenants?.length || 0}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Total Factories:</span>{' '}
              <span className="text-foreground font-medium">
                {sensorData?.tenants?.reduce((acc, tenant) =>
                  acc + tenant.manufacturers?.reduce((mAcc, manufacturer) =>
                    mAcc + (manufacturer.factories?.length || 0), 0) || 0, 0) || 0}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Active Devices:</span>{' '}
              <span className="text-foreground font-medium">
                {sensorData?.tenants?.reduce((acc, tenant) =>
                  acc + tenant.manufacturers?.reduce((mAcc, manufacturer) =>
                    mAcc + manufacturer.factories?.reduce((fAcc, factory) =>
                      fAcc + (factory.plcs?.length || 0), 0) || 0, 0) || 0, 0) || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
