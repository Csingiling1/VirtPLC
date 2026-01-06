import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { dataApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { Server, ChevronLeft, ChevronRight, Activity } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface Sensor {
  id: string;
  name: string;
  value: number;
  unit: string;
  timestamp: number;
}

interface PLC {
  id: string;
  name: string;
  description: string;
  sensors: Sensor[];
}

interface HierarchicalData {
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
        plcs: PLC[];
      }>;
    }>;
  }>;
}

const MonitoringNew = () => {
  const [historicalData, setHistoricalData] = useState<HierarchicalData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPLCIndex, setCurrentPLCIndex] = useState(0);
  const { toast } = useToast();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const factoryId = searchParams.get('factoryId');

  // Fetch data every 2 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await dataApi.getHierarchical();

        // Filter by user's manufacturer if not admin
        let filteredData = data;
        if (user && user.role !== 'ADMIN' && user.manufacturer) {
          filteredData = {
            ...data,
            tenants: data.tenants.map(tenant => ({
              ...tenant,
              manufacturers: tenant.manufacturers.filter(
                m => m.id === user.manufacturer.manufacturerId
              )
            })).filter(tenant => tenant.manufacturers.length > 0)
          };
        }

        // Filter by factory if specified
        if (factoryId) {
          filteredData = {
            ...filteredData,
            tenants: filteredData.tenants.map(tenant => ({
              ...tenant,
              manufacturers: tenant.manufacturers.map(manufacturer => ({
                ...manufacturer,
                factories: manufacturer.factories.filter(f => f.id === factoryId)
              })).filter(manufacturer => manufacturer.factories.length > 0)
            })).filter(tenant => tenant.manufacturers.length > 0)
          };
        }

        setHistoricalData((prev) => {
          // Create a new timestamp for this data point
          const timestampedData = {
            ...filteredData,
            timestamp: Date.now()
          };
          const newData = [...prev, timestampedData];
          return newData.slice(-60); // Keep last 60 data points (2 minutes at 2s interval)
        });
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        if (isLoading) {
          toast({
            title: "Connection Error",
            description: "Failed to fetch monitoring data. Please try again.",
            variant: "destructive",
          });
        }
        setIsLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, [toast, isLoading, user, factoryId]);

  // Get all unique PLCs across all data
  const allPLCs: PLC[] = [];
  if (historicalData.length > 0) {
    const latestData = historicalData[historicalData.length - 1];
    latestData.tenants.forEach(tenant => {
      tenant.manufacturers.forEach(manufacturer => {
        manufacturer.factories.forEach(factory => {
          factory.plcs.forEach(plc => {
            allPLCs.push(plc);
          });
        });
      });
    });
  }

  const currentPLC = allPLCs[currentPLCIndex];

  // Dynamically detect if this PLC has position sensors (any sensor with X/Y in the name)
  const positionSensors = currentPLC?.sensors.filter(s => {
    const name = s.name.toLowerCase();
    return name.includes('position') && (name.includes('_x') || name.includes('_y') || name.endsWith('x') || name.endsWith('y'));
  }) || [];

  const hasPositionSensors = positionSensors.length >= 2;

  // Prepare position data for scatter plot if we have X and Y sensors
  const positionData = hasPositionSensors ? historicalData.map(dataPoint => {
    let posX: number | null = null;
    let posY: number | null = null;
    let timestamp = dataPoint.timestamp;

    dataPoint.tenants.forEach(tenant => {
      tenant.manufacturers.forEach(manufacturer => {
        manufacturer.factories.forEach(factory => {
          factory.plcs.forEach(plc => {
            if (plc.id === currentPLC.id) {
              // Dynamically find X and Y position sensors
              const posXSensor = plc.sensors.find(s => {
                const name = s.name.toLowerCase();
                return name.includes('position') && (name.includes('_x') || name.endsWith('x'));
              });
              const posYSensor = plc.sensors.find(s => {
                const name = s.name.toLowerCase();
                return name.includes('position') && (name.includes('_y') || name.endsWith('y'));
              });
              if (posXSensor) posX = posXSensor.value;
              if (posYSensor) posY = posYSensor.value;
            }
          });
        });
      });
    });

    return {
      x: posX,
      y: posY,
      time: new Date(timestamp).toLocaleTimeString(),
      timestamp
    };
  }).filter(point => point.x !== null && point.y !== null && !isNaN(point.x as number) && !isNaN(point.y as number)) : [];

  // Prepare chart data for current PLC's sensors (exclude position sensors if they'll be shown in scatter plot)
  const sensorChartData = currentPLC?.sensors
    .filter(sensor => {
      // If this PLC has a 2D scatter plot, exclude the position X/Y sensors from individual charts
      if (hasPositionSensors) {
        const name = sensor.name.toLowerCase();
        return !(name.includes('position') && (name.includes('_x') || name.includes('_y') || name.endsWith('x') || name.endsWith('y')));
      }
      return true;
    })
    .map(sensor => {
      const timeSeriesData = historicalData.map(dataPoint => {
        let sensorValue: number | null = null;
        dataPoint.tenants.forEach(tenant => {
          tenant.manufacturers.forEach(manufacturer => {
            manufacturer.factories.forEach(factory => {
              factory.plcs.forEach(plc => {
                if (plc.id === currentPLC.id) {
                  const matchingSensor = plc.sensors.find(s => s.id === sensor.id);
                  if (matchingSensor) {
                    sensorValue = matchingSensor.value;
                  }
                }
              });
            });
          });
        });

        return {
          time: new Date(dataPoint.timestamp).toLocaleTimeString(),
          value: sensorValue,
          timestamp: dataPoint.timestamp
        };
      }).filter(point => point.value !== null && !isNaN(point.value as number));

      return {
        id: sensor.id,
        name: sensor.name,
        unit: sensor.unit,
        currentValue: sensor.value,
        data: timeSeriesData
      };
    }) || [];

  const handlePrevPLC = () => {
    setCurrentPLCIndex((prev) => (prev > 0 ? prev - 1 : allPLCs.length - 1));
  };

  const handleNextPLC = () => {
    setCurrentPLCIndex((prev) => (prev < allPLCs.length - 1 ? prev + 1 : 0));
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-primary text-lg flex items-center gap-2">
            <Activity className="animate-spin" />
            Loading monitoring data...
          </div>
        </div>
      </Layout>
    );
  }

  if (allPLCs.length === 0) {
    return (
      <Layout>
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Live Monitoring</h1>
            <p className="text-muted-foreground">Real-time sensor data visualization</p>
          </div>
          <Card>
            <CardContent className="flex items-center justify-center h-64">
              <p className="text-muted-foreground">No devices found. Please check your data sources.</p>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Live Monitoring</h1>
            <p className="text-muted-foreground">Real-time sensor data visualization</p>
          </div>
          <Badge variant="outline" className="text-lg px-4 py-2">
            <Activity className="mr-2 h-4 w-4 animate-pulse" />
            Live Data
          </Badge>
        </div>

        {/* PLC Navigation */}
        <div className="mb-6 flex items-center justify-between bg-card p-4 rounded-lg border">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrevPLC}
            disabled={allPLCs.length <= 1}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>

          <div className="flex items-center gap-3">
            <Server className="h-6 w-6 text-primary" />
            <div className="text-center">
              <h2 className="text-xl font-bold">{currentPLC?.name}</h2>
              <p className="text-sm text-muted-foreground">
                {currentPLC?.description} • Device {currentPLCIndex + 1} of {allPLCs.length}
              </p>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleNextPLC}
            disabled={allPLCs.length <= 1}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>

        {/* Position Scatter Plot for Placer */}
        {hasPositionSensors && positionData.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Position Tracking (2D)</CardTitle>
                <Badge variant="secondary">
                  Latest: ({positionData[positionData.length - 1]?.x?.toFixed(1)}, {positionData[positionData.length - 1]?.y?.toFixed(1)})
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="X Position"
                    tick={{ fontSize: 12 }}
                    label={{ value: 'X Position', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Y Position"
                    tick={{ fontSize: 12 }}
                    label={{ value: 'Y Position', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    formatter={(value: number, name: string) => [value.toFixed(2), name]}
                    labelFormatter={(label) => `Time: ${positionData.find(d => d.time === label)?.time || label}`}
                  />
                  <Legend />
                  <Scatter
                    name="Position"
                    data={positionData}
                    fill="#8b5cf6"
                    line={{ stroke: '#8b5cf6', strokeWidth: 1, strokeOpacity: 0.5 }}
                    isAnimationActive={false}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Sensor Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {sensorChartData.map((sensor) => (
            <Card key={sensor.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{sensor.name}</CardTitle>
                  <Badge variant="secondary">
                    {sensor.currentValue?.toFixed(2)} {sensor.unit}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {sensor.data.length > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={sensor.data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="time"
                        tick={{ fontSize: 12 }}
                        interval="preserveStartEnd"
                      />
                      <YAxis
                        tick={{ fontSize: 12 }}
                        label={{ value: sensor.unit, angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip
                        formatter={(value: number) => [`${value.toFixed(2)} ${sensor.unit}`, sensor.name]}
                        labelStyle={{ color: '#000' }}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[200px] text-muted-foreground">
                    No data available
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Data Quality Indicator */}
        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          Updating every 2 seconds • {historicalData.length} data points collected
        </div>
      </div>
    </Layout>
  );
};

export default MonitoringNew;
