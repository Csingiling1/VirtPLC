import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CalendarIcon, Download } from 'lucide-react';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import { cn } from '@/lib/utils';
import { dataApi, apiClient } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useToast } from '@/hooks/use-toast';

interface DeviceInfo {
  deviceId: string;
  name: string;
  plcId: string;
  plcName: string;
}

interface HistoricalDataPoint {
  timestamp: number;
  deviceId: string;
  value: number;
}

const History = () => {
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: startOfDay(subDays(new Date(), 1)),
    to: endOfDay(new Date()),
  });
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  // Fetch available devices on mount
  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const hierarchicalData = await dataApi.getHierarchical();
        const deviceList: DeviceInfo[] = [];

        if (!hierarchicalData?.tenants || !Array.isArray(hierarchicalData.tenants)) {
          console.warn('No tenants in hierarchical data:', hierarchicalData);
          return;
        }

        hierarchicalData.tenants.forEach((tenant: any) => {
          if (!tenant?.manufacturers || !Array.isArray(tenant.manufacturers)) return;

          tenant.manufacturers.forEach((manufacturer: any) => {
            if (!manufacturer?.factories || !Array.isArray(manufacturer.factories)) return;

            manufacturer.factories.forEach((factory: any) => {
              if (!factory?.plcs || !Array.isArray(factory.plcs)) return;

              factory.plcs.forEach((plc: any) => {
                if (!plc?.sensors || !Array.isArray(plc.sensors)) return;

                plc.sensors.forEach((sensor: any) => {
                  const deviceId = sensor.deviceId || sensor.id;
                  if (!deviceId) return;

                  deviceList.push({
                    deviceId,
                    name: `${plc.name || 'Unknown PLC'} - ${sensor.name || 'Unknown Sensor'}`,
                    plcId: plc.id,
                    plcName: plc.name
                  });
                });
              });
            });
          });
        });

        console.log('Found devices:', deviceList.length);
        setDevices(deviceList);
        if (deviceList.length > 0) {
          setSelectedDevice(deviceList[0].deviceId);
        }
      } catch (error) {
        console.error('Failed to fetch devices:', error);
        toast({
          title: "Error",
          description: "Failed to load available devices",
          variant: "destructive",
        });
      }
    };

    fetchDevices();
  }, [toast]);

  const handleLoadData = useCallback(async () => {
    if (!dateRange.from || !dateRange.to) {
      toast({
        title: "Error",
        description: "Please select both start and end dates",
        variant: "destructive",
      });
      return;
    }

    if (!selectedDevice) {
      toast({
        title: "Error",
        description: "Please select a device",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const startTime = dateRange.from.getTime();
      const endTime = dateRange.to.getTime();

      // Query TimescaleDB through backend for device historical data
      const response = await apiClient.get(`/api/data/device/${selectedDevice}/history`, {
        params: { startTime, endTime }
      });

      // Backend returns array directly, apiClient.get returns response.data which is the array
      const dataArray = Array.isArray(response) ? response : [];

      console.log('Loaded historical data points:', dataArray.length);
      setHistoricalData(dataArray);

      toast({
        title: "Success",
        description: `Loaded ${dataArray.length} data points`,
      });
    } catch (error: any) {
      console.error('Failed to fetch historical data:', error);

      let errorMessage = "Failed to load historical data";
      if (error.response?.status === 404) {
        errorMessage = "No historical data found for selected device and time range";
      }

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      setHistoricalData([]);
    } finally {
      setIsLoading(false);
    }
  }, [dateRange.from, dateRange.to, selectedDevice, toast]);

  const formatChartData = () => {
    if (!Array.isArray(historicalData)) {
      return [];
    }
    return historicalData.map(data => ({
      timestamp: format(new Date(data.timestamp), 'MM/dd HH:mm:ss'),
      value: data.value,
    }));
  };

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Historical Data</h1>
          <p className="text-muted-foreground">Analyze past trends and export data</p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Date Range & Device Selection</CardTitle>
            <CardDescription>Select a device and time period to view historical data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Select Device</label>
                <Select value={selectedDevice} onValueChange={setSelectedDevice}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Choose a device" />
                  </SelectTrigger>
                  <SelectContent>
                    {devices.map((device, index) => (
                      <SelectItem key={`${device.deviceId}-${index}`} value={device.deviceId}>
                        {device.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-wrap gap-4 items-end">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Start Date</label>
                  <Popover key="start-date-popover">
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-[240px] justify-start text-left font-normal",
                          !dateRange.from && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange.from ? format(dateRange.from, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={dateRange.from}
                        onSelect={(date) => setDateRange((prev) => ({ ...prev, from: date }))}
                        initialFocus
                        className="pointer-events-auto"
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">End Date</label>
                  <Popover key="end-date-popover">
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-[240px] justify-start text-left font-normal",
                          !dateRange.to && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange.to ? format(dateRange.to, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={dateRange.to}
                        onSelect={(date) => setDateRange((prev) => ({ ...prev, to: date }))}
                        initialFocus
                        className="pointer-events-auto"
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <Button onClick={handleLoadData} disabled={isLoading}>
                  {isLoading ? "Loading..." : "Load Data"}
                </Button>
                <Button variant="outline" className="gap-2">
                  <Download className="h-4 w-4" />
                  Export CSV
                </Button>
              </div>

              <div className="flex gap-2 flex-wrap">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDateRange({
                    from: startOfDay(subDays(new Date(), 1)),
                    to: endOfDay(new Date()),
                  })}
                >
                  Last 24 Hours
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDateRange({
                    from: startOfDay(subDays(new Date(), 7)),
                    to: endOfDay(new Date()),
                  })}
                >
                  Last 7 Days
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDateRange({
                    from: startOfDay(subDays(new Date(), 30)),
                    to: endOfDay(new Date()),
                  })}
                >
                  Last 30 Days
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDateRange({ from: undefined, to: undefined })}
                >
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {historicalData.length > 0 ? (
          <div className="grid grid-cols-1 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{devices.find(d => d.deviceId === selectedDevice)?.name || 'Sensor Data'}</CardTitle>
                <CardDescription>Values over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={formatChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#8884d8" name="Value" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Summary</CardTitle>
                <CardDescription>Overview of loaded data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p><strong>Device:</strong> {devices.find(d => d.deviceId === selectedDevice)?.name || 'Unknown'}</p>
                  <p><strong>Total Points:</strong> {historicalData.length}</p>
                  <p><strong>Time Range:</strong> {dateRange.from && dateRange.to ?
                    `${format(dateRange.from, "PPP")} - ${format(dateRange.to, "PPP")}` :
                    "Not selected"}</p>
                  {historicalData.length > 0 && (
                    <>
                      <p><strong>First Reading:</strong> {format(new Date(historicalData[0].timestamp), "PPP p")}</p>
                      <p><strong>Last Reading:</strong> {format(new Date(historicalData[historicalData.length - 1].timestamp), "PPP p")}</p>
                      <p><strong>Min Value:</strong> {Math.min(...historicalData.map(d => d.value)).toFixed(2)}</p>
                      <p><strong>Max Value:</strong> {Math.max(...historicalData.map(d => d.value)).toFixed(2)}</p>
                      <p><strong>Avg Value:</strong> {(historicalData.reduce((sum, d) => sum + d.value, 0) / historicalData.length).toFixed(2)}</p>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Historical Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                {selectedDevice && dateRange.from && dateRange.to ?
                  "Click 'Load Data' to view historical trends" :
                  "Select a device and date range to view historical data"}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default History;
