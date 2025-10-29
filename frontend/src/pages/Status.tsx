import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import StatusCard from '@/components/StatusCard';
import { simulatorApi, dataApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Server, Activity, AlertCircle, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Status = () => {
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [simulatorStatus, setSimulatorStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [health, simStatus] = await Promise.all([
          dataApi.getHealth().catch(() => ({ status: 'Unknown' })),
          simulatorApi.getStatus().catch(() => ({ isRunning: false })),
        ]);
        setSystemHealth(health);
        setSimulatorStatus(simStatus);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch status:', error);
        toast({
          title: "Error",
          description: "Failed to fetch system status",
          variant: "destructive",
        });
        setIsLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);

    return () => clearInterval(interval);
  }, [toast]);

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-primary text-lg">Loading status...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">System Status</h1>
          <p className="text-muted-foreground">Monitor system health and performance</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="Backend Connection"
            value={systemHealth?.status || 'Connected'}
            icon={systemHealth?.status === 'Unknown' ? AlertCircle : CheckCircle}
            status={systemHealth?.status === 'Unknown' ? 'warning' : 'success'}
          />
          <StatusCard
            title="Simulator Status"
            value={simulatorStatus?.isRunning ? 'Running' : 'Stopped'}
            icon={simulatorStatus?.isRunning ? Activity : Server}
            status={simulatorStatus?.isRunning ? 'success' : 'warning'}
          />
          <StatusCard
            title="Active Devices"
            value={simulatorStatus?.activeDevices || 0}
            icon={Server}
            status="info"
          />
          <StatusCard
            title="Total Signals"
            value={simulatorStatus?.totalSignals || 0}
            icon={Activity}
            status="info"
          />
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Connection Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-border">
                <span className="text-muted-foreground">API Base URL</span>
                <span className="font-medium">
                  {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-border">
                <span className="text-muted-foreground">Authentication</span>
                <span className="font-medium text-status-success">Authenticated</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-muted-foreground">Last Update</span>
                <span className="font-medium">
                  {new Date(simulatorStatus?.lastUpdate || Date.now()).toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default Status;
