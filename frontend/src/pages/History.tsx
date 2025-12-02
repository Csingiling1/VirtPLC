import { useState, useEffect, useCallback } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Download } from 'lucide-react';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import { cn } from '@/lib/utils';
import { dataApi } from '@/lib/api';
import { SensorData } from '@/types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useToast } from '@/hooks/use-toast';

interface ApiError {
  response?: {
    status: number;
  };
  isNetworkError?: boolean;
  message?: string;
}

const History = () => {
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: undefined, // No default date range
    to: undefined,
  });
  const [historicalData, setHistoricalData] = useState<SensorData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleLoadData = useCallback(async () => {
    if (!dateRange.from || !dateRange.to) {
      toast({
        title: "Error",
        description: "Please select both start and end dates",
        variant: "destructive",
      });
      return;
    }

    const rangeMs = dateRange.to.getTime() - dateRange.from.getTime();
    const rangeDays = rangeMs / (1000 * 60 * 60 * 24);

    if (rangeDays > 7) {
      toast({
        title: "Large Date Range",
        description: "Date ranges over 7 days may load slowly. Consider selecting a smaller range for better performance.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const startTime = dateRange.from.getTime();
      const endTime = dateRange.to.getTime();

      const data = await dataApi.getRange(startTime, endTime);

      // Limit to 1000 data points for performance
      const maxPoints = 1000;
      let processedData = data;
      if (data.length > maxPoints) {
        // Sample evenly across the range
        const step = Math.floor(data.length / maxPoints);
        processedData = data.filter((_, index) => index % step === 0).slice(0, maxPoints);
        toast({
          title: "Data Sampled",
          description: `Loaded ${processedData.length} of ${data.length} data points (sampled for performance)`,
        });
      } else {
        toast({
          title: "Success",
          description: `Loaded ${data.length} data points`,
        });
      }

      setHistoricalData(processedData);
    } catch (error: unknown) {
      console.error('Failed to fetch historical data:', error);

      let errorMessage = "Failed to load historical data";

      const err = error as ApiError;
      if (err.response) {
        // Server responded with error status
        if (err.response.status === 401) {
          errorMessage = "Authentication required. Please log in again.";
        } else if (err.response.status === 400) {
          errorMessage = "Invalid request. Please check your date range.";
        } else if (err.response.status === 403) {
          errorMessage = "Access denied. You don't have permission to view this data.";
        } else {
          errorMessage = `Server error: ${err.response.status}`;
        }
      } else if (err.isNetworkError) {
        errorMessage = err.message || "Network error occurred";
      }

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [dateRange.from, dateRange.to, toast]);

  // Removed auto-load on mount and date change for performance

  const formatChartData = () => {
    return historicalData.map(data => ({
      timestamp: format(new Date(data.timestamp), 'HH:mm:ss'),
      motor1Speed: data.motor1Speed,
      motor1Temp: data.motor1Temp,
      motor2Speed: data.motor2Speed,
      motor2Temp: data.motor2Temp,
      conveyor1Speed: data.conveyor1Speed,
      sensor1Value: data.sensor1Value,
      sensor2Value: data.sensor2Value,
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
            <CardTitle>Date Range Selection</CardTitle>
            <CardDescription>Select a time period to view historical data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-4 items-end">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Start Date</label>
                  <Popover>
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
                  <Popover>
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Motor Speeds</CardTitle>
                <CardDescription>RPM values over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={formatChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="motor1Speed" stroke="#8884d8" name="Motor 1 Speed" />
                    <Line type="monotone" dataKey="motor2Speed" stroke="#82ca9d" name="Motor 2 Speed" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Motor Temperatures</CardTitle>
                <CardDescription>Temperature values over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={formatChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="motor1Temp" stroke="#ff7300" name="Motor 1 Temp" />
                    <Line type="monotone" dataKey="motor2Temp" stroke="#00ff00" name="Motor 2 Temp" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Conveyor & Sensors</CardTitle>
                <CardDescription>Conveyor speed and sensor values</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={formatChartData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="conveyor1Speed" stroke="#ffc658" name="Conveyor Speed" />
                    <Line type="monotone" dataKey="sensor1Value" stroke="#ff0000" name="Sensor 1" />
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
                  <p><strong>Total Points:</strong> {historicalData.length}</p>
                  <p><strong>Time Range:</strong> {dateRange.from && dateRange.to ?
                    `${format(dateRange.from, "PPP")} - ${format(dateRange.to, "PPP")}` :
                    "Not selected"}</p>
                  <p><strong>Last Update:</strong> {historicalData.length > 0 ?
                    format(new Date(historicalData[historicalData.length - 1].timestamp), "PPP p") :
                    "N/A"}</p>
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
                {dateRange.from && dateRange.to ?
                  "Click 'Load Data' to view historical trends" :
                  "Select a date range to view historical data"}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default History;
