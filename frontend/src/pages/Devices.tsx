import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { simulatorApi } from '@/lib/api';
import { SimulatorDevice } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Server, Plus, Trash2, Edit, Building, Factory, Cpu, Activity } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Devices = () => {
  const [devices, setDevices] = useState<SimulatorDevice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newDevice, setNewDevice] = useState({
    name: '',
    description: '',
    deviceType: 'plc',
    tenantId: 'demo-tenant',
    tenantName: 'Demo Tenant',
    manufacturerId: 'demo-mfg',
    manufacturerName: 'Demo Manufacturer',
    factoryId: 'demo-factory',
    factoryName: 'Demo Factory'
  });
  const { toast } = useToast();

  interface HierarchicalData {
    tenants: Array<{
      manufacturers: Array<{
        factories: Array<{
          name: string;
          plcs: Array<{
            id: string;
            name: string;
            description?: string;
            sensors: Array<{
              name: string;
              unit: string;
              value: number;
              timestamp: number;
            }>;
          }>;
        }>;
      }>;
    }>;
  }

  const fetchDevices = useCallback(async () => {
    try {
      // Fetch hierarchical data from simulator
      const response = await fetch('http://localhost:5000/api/stream/latest');
      const data: HierarchicalData = await response.json();

      // Extract PLCs from hierarchical structure
      const extractedDevices: SimulatorDevice[] = [];
      if (data.tenants) {
        data.tenants.forEach((tenant) => {
          tenant.manufacturers?.forEach((manufacturer) => {
            manufacturer.factories?.forEach((factory) => {
              factory.plcs?.forEach((plc) => {
                extractedDevices.push({
                  id: plc.id,
                  name: plc.name,
                  description: plc.description || `${plc.name} in ${factory.name}`,
                  deviceType: 'plc',
                  signals: plc.sensors?.map((sensor) => ({
                    name: sensor.name,
                    unit: sensor.unit,
                    value: sensor.value,
                    generator: 'constant', // Default
                    isRunning: true,
                    lastUpdate: sensor.timestamp
                  })) || [],
                  is_active: true,
                  created_at: Date.now(),
                  updated_at: Date.now()
                });
              });
            });
          });
        });
      }

      setDevices(extractedDevices);
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

  const handleCreateDevice = async () => {
    try {
      await simulatorApi.createDevice({
        name: newDevice.name,
        description: newDevice.description,
        deviceType: newDevice.deviceType,
        tenantId: newDevice.tenantId,
        tenantName: newDevice.tenantName,
        manufacturerId: newDevice.manufacturerId,
        manufacturerName: newDevice.manufacturerName,
        factoryId: newDevice.factoryId,
        factoryName: newDevice.factoryName
      });
      toast({
        title: "Device Created",
        description: "New device has been created successfully",
      });
      setIsCreateDialogOpen(false);
      setNewDevice({
        name: '',
        description: '',
        deviceType: 'plc',
        tenantId: 'demo-tenant',
        tenantName: 'Demo Tenant',
        manufacturerId: 'demo-mfg',
        manufacturerName: 'Demo Manufacturer',
        factoryId: 'demo-factory',
        factoryName: 'Demo Factory'
      });
      fetchDevices();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create device",
        variant: "destructive",
      });
    }
  };

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
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Add Device
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Create New Device</DialogTitle>
                <DialogDescription>
                  Add a new PLC device to the simulator with hierarchical organization.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="deviceName">Device Name</Label>
                    <Input
                      id="deviceName"
                      value={newDevice.name}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Main PLC"
                    />
                  </div>
                  <div>
                    <Label htmlFor="deviceType">Device Type</Label>
                    <Select value={newDevice.deviceType} onValueChange={(value) => setNewDevice(prev => ({ ...prev, deviceType: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="plc">PLC</SelectItem>
                        <SelectItem value="sensor">Sensor</SelectItem>
                        <SelectItem value="motor">Motor</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newDevice.description}
                    onChange={(e) => setNewDevice(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Device description"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="tenantId">Tenant ID</Label>
                    <Input
                      id="tenantId"
                      value={newDevice.tenantId}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, tenantId: e.target.value }))}
                      placeholder="demo-tenant"
                    />
                  </div>
                  <div>
                    <Label htmlFor="tenantName">Tenant Name</Label>
                    <Input
                      id="tenantName"
                      value={newDevice.tenantName}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, tenantName: e.target.value }))}
                      placeholder="Demo Tenant"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="manufacturerId">Manufacturer ID</Label>
                    <Input
                      id="manufacturerId"
                      value={newDevice.manufacturerId}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, manufacturerId: e.target.value }))}
                      placeholder="demo-mfg"
                    />
                  </div>
                  <div>
                    <Label htmlFor="manufacturerName">Manufacturer Name</Label>
                    <Input
                      id="manufacturerName"
                      value={newDevice.manufacturerName}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, manufacturerName: e.target.value }))}
                      placeholder="Demo Manufacturer"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="factoryId">Factory ID</Label>
                    <Input
                      id="factoryId"
                      value={newDevice.factoryId}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, factoryId: e.target.value }))}
                      placeholder="demo-factory"
                    />
                  </div>
                  <div>
                    <Label htmlFor="factoryName">Factory Name</Label>
                    <Input
                      id="factoryName"
                      value={newDevice.factoryName}
                      onChange={(e) => setNewDevice(prev => ({ ...prev, factoryName: e.target.value }))}
                      placeholder="Demo Factory"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateDevice} disabled={!newDevice.name}>
                  Create Device
                </Button>
              </div>
            </DialogContent>
          </Dialog>
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
                                <span className="font-medium">{signal.value.toFixed(1)} {signal.unit}</span>
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
            <Button className="gap-2" onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="h-4 w-4" />
              Add Device
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
};
