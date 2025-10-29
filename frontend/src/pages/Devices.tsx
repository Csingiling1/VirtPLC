import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { simulatorApi } from '@/lib/api';
import { SimulatorDevice } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Server, Plus, Trash2, Edit } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Devices = () => {
  const [devices, setDevices] = useState<SimulatorDevice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  const fetchDevices = async () => {
    try {
      const data = await simulatorApi.getDevices();
      setDevices(Array.isArray(data) ? data : []);
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
  };

  useEffect(() => {
    fetchDevices();
  }, []);

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
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Add Device
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices.map((device) => (
            <Card key={device.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Server className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{device.name}</CardTitle>
                      <CardDescription className="text-xs">{device.deviceType}</CardDescription>
                    </div>
                  </div>
                  <Badge variant={device.isActive ? "default" : "secondary"}>
                    {device.isActive ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{device.description}</p>
                <div className="flex items-center justify-between text-sm mb-4">
                  <span className="text-muted-foreground">Signals:</span>
                  <span className="font-medium">{device.signals?.length || 0}</span>
                </div>
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

        {devices.length === 0 && (
          <div className="text-center py-12">
            <Server className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Devices Found</h3>
            <p className="text-muted-foreground mb-6">Get started by adding your first device</p>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Add Device
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Devices;
