import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { dataApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Factory, MapPin, Activity, ThermometerSun, Gauge } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface DevicePosition {
    id: string;
    name: string;
    x: number;
    y: number;
    type: string;
    sensors: Array<{
        name: string;
        value: number;
        unit: string;
        lastUpdate: number;
    }>;
}

const FactoryView = () => {
    const [devices, setDevices] = useState<DevicePosition[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<DevicePosition | null>(null);
    const [hoveredDevice, setHoveredDevice] = useState<DevicePosition | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const { toast } = useToast();

    // Mock factory layout with device positions
    const factoryLayout = {
        width: 800,
        height: 600,
        devices: [
            { id: 'plc-1', name: 'Main PLC', x: 100, y: 100, type: 'plc' },
            { id: 'motor-1', name: 'Conveyor Motor', x: 300, y: 150, type: 'motor' },
            { id: 'sensor-1', name: 'Temp Sensor 1', x: 500, y: 200, type: 'sensor' },
            { id: 'sensor-2', name: 'Pressure Sensor', x: 650, y: 300, type: 'sensor' },
            { id: 'motor-2', name: 'Assembly Motor', x: 200, y: 400, type: 'motor' },
            { id: 'plc-2', name: 'Backup PLC', x: 600, y: 500, type: 'plc' },
        ]
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await dataApi.getLatest();
                // Transform the data into device positions with sensor values
                const mockDevices: DevicePosition[] = factoryLayout.devices.map(device => ({
                    ...device,
                    sensors: [
                        {
                            name: 'Temperature',
                            value: data?.motor1Temp || 25 + Math.random() * 10,
                            unit: '°C',
                            lastUpdate: Date.now()
                        },
                        {
                            name: 'Pressure',
                            value: data?.sensor1Value || 1 + Math.random() * 2,
                            unit: 'bar',
                            lastUpdate: Date.now()
                        },
                        {
                            name: 'Speed',
                            value: data?.motor1Speed || 1000 + Math.random() * 500,
                            unit: 'RPM',
                            lastUpdate: Date.now()
                        }
                    ]
                }));
                setDevices(mockDevices);
                setIsLoading(false);
            } catch (error) {
                console.error('Failed to fetch data:', error);
                toast({
                    title: "Connection Error",
                    description: "Failed to fetch factory data",
                    variant: "destructive",
                });
                setIsLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000);

        return () => clearInterval(interval);
    }, [toast, factoryLayout.devices]);

    const getDeviceColor = (type: string, sensors: Array<{ name: string; value: number; unit: string; lastUpdate: number }>) => {
        const avgTemp = sensors.find(s => s.name === 'Temperature')?.value || 0;
        const pressure = sensors.find(s => s.name === 'Pressure')?.value || 0;

        if (type === 'plc') return '#3b82f6'; // blue
        if (type === 'motor') {
            if (avgTemp > 80) return '#ef4444'; // red
            if (avgTemp > 60) return '#f59e0b'; // yellow
            return '#10b981'; // green
        }
        if (type === 'sensor') {
            if (pressure > 2.5) return '#ef4444'; // red
            if (pressure > 1.5) return '#f59e0b'; // yellow
            return '#10b981'; // green
        }
        return '#6b7280'; // gray
    };

    const getDeviceIcon = (type: string) => {
        switch (type) {
            case 'plc': return '🔧';
            case 'motor': return '⚙️';
            case 'sensor': return '📡';
            default: return '📦';
        }
    };

    if (isLoading) {
        return (
            <Layout>
                <div className="flex items-center justify-center h-full">
                    <div className="animate-pulse text-primary text-lg">Loading factory view...</div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="p-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2">Factory View</h1>
                    <p className="text-muted-foreground">2D visualization of factory equipment and real-time sensor data</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Factory Map */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Factory className="h-5 w-5" />
                                    Factory Layout
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div
                                    className="relative bg-slate-50 border-2 border-dashed border-slate-300 rounded-lg"
                                    style={{ width: factoryLayout.width, height: factoryLayout.height, margin: '0 auto' }}
                                >
                                    {devices.map((device) => (
                                        <div
                                            key={device.id}
                                            className="absolute cursor-pointer transform -translate-x-1/2 -translate-y-1/2 transition-all duration-200 hover:scale-110"
                                            style={{
                                                left: device.x,
                                                top: device.y,
                                            }}
                                            onMouseEnter={() => setHoveredDevice(device)}
                                            onMouseLeave={() => setHoveredDevice(null)}
                                            onClick={() => setSelectedDevice(device)}
                                        >
                                            <div
                                                className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold shadow-lg border-2 border-white"
                                                style={{ backgroundColor: getDeviceColor(device.type, device.sensors) }}
                                            >
                                                {getDeviceIcon(device.type)}
                                            </div>
                                        </div>
                                    ))}

                                    {/* Hover Tooltip */}
                                    {hoveredDevice && (
                                        <div
                                            className="absolute bg-black text-white px-3 py-2 rounded-lg text-sm pointer-events-none z-10 shadow-lg"
                                            style={{
                                                left: hoveredDevice.x + 20,
                                                top: hoveredDevice.y - 10,
                                            }}
                                        >
                                            <div className="font-semibold">{hoveredDevice.name}</div>
                                            <div className="text-xs opacity-90">{hoveredDevice.type.toUpperCase()}</div>
                                        </div>
                                    )}
                                </div>

                                {/* Legend */}
                                <div className="mt-4 flex flex-wrap gap-4 text-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                                        <span>PLC</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full bg-green-500"></div>
                                        <span>Motor (Normal)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                                        <span>Motor (Warning)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full bg-red-500"></div>
                                        <span>Motor (Critical)</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Device Details */}
                    <div>
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" />
                                    {selectedDevice ? selectedDevice.name : 'Select Device'}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {selectedDevice ? (
                                    <div className="space-y-4">
                                        <div>
                                            <Badge variant="outline" className="mb-2">
                                                {selectedDevice.type.toUpperCase()}
                                            </Badge>
                                            <p className="text-sm text-muted-foreground">
                                                Position: ({selectedDevice.x}, {selectedDevice.y})
                                            </p>
                                        </div>

                                        <div className="space-y-3">
                                            {selectedDevice.sensors.map((sensor, index) => (
                                                <div key={index} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                                                    <div className="flex items-center gap-2">
                                                        {sensor.name === 'Temperature' && <ThermometerSun className="h-4 w-4 text-red-500" />}
                                                        {sensor.name === 'Pressure' && <Gauge className="h-4 w-4 text-blue-500" />}
                                                        {sensor.name === 'Speed' && <Activity className="h-4 w-4 text-green-500" />}
                                                        <span className="font-medium">{sensor.name}</span>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="font-bold text-primary">
                                                            {sensor.value.toFixed(1)} {sensor.unit}
                                                        </div>
                                                        <div className="text-xs text-muted-foreground">
                                                            {new Date(sensor.lastUpdate).toLocaleTimeString()}
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="text-center py-8 text-muted-foreground">
                                        <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
                                        <p>Click on a device in the factory map to view its details</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default FactoryView;