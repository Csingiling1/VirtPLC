import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { simulatorApi } from '@/lib/api';
import { SimulatorDevice } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Server, Trash2, Edit, Factory, Cpu } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Devices = () => {
  const [devices, setDevices] = useState<SimulatorDevice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  const fetchDevices = useCallback(async () => {
    try {
      console.log('Fetching devices...');
      const devices = await simulatorApi.getDevices();
      console.log('Fetched devices:', devices);
      setDevices(devices);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
      toast({
        title: "Error",
        description: "Failed to fetch devices",
        variant: "destructive",
      });
      setDevices([]);
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  const handleDelete = async (deviceId: string) => {
    try {
      await simulatorApi.deleteDevice(deviceId);
      toast({
        title: "Device Deleted",
        description: "Device has been removed successfully",
      });
      fetchDevices();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete device",
        variant: "destructive",
      });
    }
  };

  // Group devices by factory for hierarchical display
  const groupedDevices = devices.reduce((acc, device) => {
    // For now, all devices are in the same factory
    const factoryKey = 'Demo Factory';
    if (!acc[factoryKey]) {
      acc[factoryKey] = [];
    }
    acc[factoryKey].push(device);
    return acc;
  }, {} as Record<string, SimulatorDevice[]>);

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-primary text-lg">Loading devices...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Device Management</h1>
            <p className="text-muted-foreground">Configure and monitor simulator devices</p>
          </div>
        </div>

        {/* Hierarchical Device Display */}
        <div className="space-y-6">
          {Object.entries(groupedDevices).map(([factoryName, factoryDevices]) => (
            <Card key={factoryName}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Factory className="h-5 w-5" />
                  {factoryName}
                  <Badge variant="secondary">{factoryDevices.length} devices</Badge>
                </CardTitle>
                <CardDescription>Devices in this factory</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {factoryDevices.map((device) => (
                    <Card key={device.id} className="border-l-4 border-l-primary">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                              <Cpu className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                              <CardTitle className="text-lg">{device.name}</CardTitle>
                              <CardDescription className="text-xs">{device.deviceType}</CardDescription>
                            </div>
                          </div>
                          <Badge variant={device.is_active ? "default" : "secondary"}>
                            {device.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">{device.description}</p>
                        <div className="flex items-center justify-between text-sm mb-4">
                          <span className="text-muted-foreground">Signals:</span>
                          <span className="font-medium">{device.signals?.length || 0}</span>
                        </div>
                        {device.signals && device.signals.length > 0 && (
                          <div className="space-y-2 mb-4">
                            {device.signals.slice(0, 3).map((signal, index) => (
                              <div key={index} className="flex items-center justify-between text-xs bg-secondary/50 rounded px-2 py-1">
                                <span className="text-muted-foreground">{signal.name}</span>
                                <span className="font-medium">{typeof signal.value === 'number' ? signal.value.toFixed(1) : String(signal.value)} {signal.unit}</span>
                              </div>
                            ))}
                            {device.signals.length > 3 && (
                              <div className="text-xs text-muted-foreground text-center">
                                +{device.signals.length - 3} more signals
                              </div>
                            )}
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="flex-1 gap-2">
                            <Edit className="h-4 w-4" />
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-2 text-destructive hover:text-destructive"
                            onClick={() => handleDelete(device.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {devices.length === 0 && (
          <div className="text-center py-12">
            <Server className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Devices Found</h3>
            <p className="text-muted-foreground mb-6">Get started by adding your first device</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Devices;
