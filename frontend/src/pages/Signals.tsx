import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { simulatorApi } from '@/lib/api';
import { SimulatorDevice } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Radio, Play, Pause } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Signals = () => {
  const [devices, setDevices] = useState<SimulatorDevice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const data = await simulatorApi.getDevices();
        setDevices(Array.isArray(data) ? data : []);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch devices:', error);
        toast({
          title: "Error",
          description: "Failed to fetch signal data",
          variant: "destructive",
        });
        setDevices([]);
        setIsLoading(false);
      }
    };

    fetchDevices();
  }, [toast]);

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-primary text-lg">Loading signals...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Signal Configuration</h1>
          <p className="text-muted-foreground">Manage and configure device signals</p>
        </div>

        <div className="space-y-6">
          {devices.map((device) => (
            <Card key={device.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{device.name}</CardTitle>
                    <CardDescription>{device.description}</CardDescription>
                  </div>
                  <Badge variant={device.isActive ? "default" : "secondary"}>
                    {device.isActive ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {device.signals && device.signals.length > 0 ? (
                  <div className="space-y-3">
                    {device.signals.map((signal, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 rounded-lg bg-secondary/50 border border-border"
                      >
                        <div className="flex items-center gap-4 flex-1">
                          <Radio className="h-5 w-5 text-primary" />
                          <div className="flex-1">
                            <div className="font-medium">{signal.name}</div>
                            <div className="text-sm text-muted-foreground">
                              Generator: {signal.generator}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-bold text-primary">
                              {signal.value.toFixed(2)}
                            </div>
                            <div className="text-xs text-muted-foreground">{signal.unit}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <Button
                            size="sm"
                            variant="outline"
                            className="gap-2"
                          >
                            {signal.isRunning ? (
                              <>
                                <Pause className="h-4 w-4" />
                                Pause
                              </>
                            ) : (
                              <>
                                <Play className="h-4 w-4" />
                                Start
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    No signals configured for this device
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          {devices.length === 0 && (
            <div className="text-center py-12">
              <Radio className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Signals Found</h3>
              <p className="text-muted-foreground">Add devices to configure signals</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Signals;
