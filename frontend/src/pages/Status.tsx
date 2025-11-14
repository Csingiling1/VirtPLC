import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Settings, Server, Wifi, Save } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Status = () => {
  const [config, setConfig] = useState({
    simulatorHost: 'localhost',
    simulatorPort: '8000',
    opcuaEndpoint: 'opc.tcp://simulator:4840',
    backendHost: 'localhost',
    backendPort: '18080',
    tenantId: 'demo-tenant',
    manufacturerId: 'demo-mfg',
    factoryId: 'demo-factory'
  });
  const { toast } = useToast();

  useEffect(() => {
    // Load saved configuration
    const savedConfig = localStorage.getItem('plc-config');
    if (savedConfig) {
      try {
        setConfig(JSON.parse(savedConfig));
      } catch (error) {
        console.error('Failed to load saved config:', error);
      }
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('plc-config', JSON.stringify(config));
    toast({
      title: "Configuration Saved",
      description: "PLC connection settings have been saved successfully",
    });
  };

  const handleInputChange = (field: string, value: string) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">PLC Configuration</h1>
          <p className="text-muted-foreground">Configure PLC listening ports and connection settings</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Simulator Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Simulator Connection
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="simulatorHost">Host</Label>
                  <Input
                    id="simulatorHost"
                    value={config.simulatorHost}
                    onChange={(e) => handleInputChange('simulatorHost', e.target.value)}
                    placeholder="localhost"
                  />
                </div>
                <div>
                  <Label htmlFor="simulatorPort">Port</Label>
                  <Input
                    id="simulatorPort"
                    value={config.simulatorPort}
                    onChange={(e) => handleInputChange('simulatorPort', e.target.value)}
                    placeholder="8000"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="opcuaEndpoint">OPC-UA Endpoint</Label>
                <Input
                  id="opcuaEndpoint"
                  value={config.opcuaEndpoint}
                  onChange={(e) => handleInputChange('opcuaEndpoint', e.target.value)}
                  placeholder="opc.tcp://simulator:4840"
                />
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="gap-1">
                  <Wifi className="h-3 w-3" />
                  Web API
                </Badge>
                <span className="text-sm text-muted-foreground">
                  http://{config.simulatorHost}:{config.simulatorPort}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Backend Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Backend Connection
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="backendHost">Host</Label>
                  <Input
                    id="backendHost"
                    value={config.backendHost}
                    onChange={(e) => handleInputChange('backendHost', e.target.value)}
                    placeholder="localhost"
                  />
                </div>
                <div>
                  <Label htmlFor="backendPort">Port</Label>
                  <Input
                    id="backendPort"
                    value={config.backendPort}
                    onChange={(e) => handleInputChange('backendPort', e.target.value)}
                    placeholder="18080"
                  />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="gap-1">
                  <Wifi className="h-3 w-3" />
                  REST API
                </Badge>
                <span className="text-sm text-muted-foreground">
                  http://{config.backendHost}:{config.backendPort}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Tenant Configuration */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Tenant & Factory Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="tenantId">Tenant ID</Label>
                  <Input
                    id="tenantId"
                    value={config.tenantId}
                    onChange={(e) => handleInputChange('tenantId', e.target.value)}
                    placeholder="demo-tenant"
                  />
                </div>
                <div>
                  <Label htmlFor="manufacturerId">Manufacturer ID</Label>
                  <Input
                    id="manufacturerId"
                    value={config.manufacturerId}
                    onChange={(e) => handleInputChange('manufacturerId', e.target.value)}
                    placeholder="demo-mfg"
                  />
                </div>
                <div>
                  <Label htmlFor="factoryId">Factory ID</Label>
                  <Input
                    id="factoryId"
                    value={config.factoryId}
                    onChange={(e) => handleInputChange('factoryId', e.target.value)}
                    placeholder="demo-factory"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-6 flex justify-end">
          <Button onClick={handleSave} className="gap-2">
            <Save className="h-4 w-4" />
            Save Configuration
          </Button>
        </div>
      </div>
    </Layout>
  );
};

export default Status;
