import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { dataApi, api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Factory, MapPin, Activity, ThermometerSun, Gauge } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface DevicePosition {
    id: string;
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
    type: string;
    x_position: number;
    y_position: number;
    sensors: Array<{
        name: string;
        value: number;
        unit: string;
        lastUpdate: number;
    }>;
}

interface FactoryData {
    id: string;
    name: string;
    shape: string;
    width_meters: number;
    height_meters: number;
    wireframe_color?: string;
    plcs: Array<{
        id: string;
        name: string;
        x_position: number;
        y_position: number;
        width: number;
        height: number;
        sensors: Array<{
            signal_config: {
                name: string;
                value: number;
                unit: string;
            };
        }>;
    }>;
}

const FactoryView = () => {
    const [devices, setDevices] = useState<DevicePosition[]>([]);
    const [factoryData, setFactoryData] = useState<FactoryData | null>(null);
    const [selectedDevice, setSelectedDevice] = useState<DevicePosition | null>(null);
    const [hoveredDevice, setHoveredDevice] = useState<DevicePosition | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [allFactories, setAllFactories] = useState<FactoryData[]>([]);
    const [selectedFactoryId, setSelectedFactoryId] = useState<string>('');
    const [zoom, setZoom] = useState(1);
    const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const { toast } = useToast();

    // Default factory layout dimensions (will be overridden by API data)
    const [factoryLayout, setFactoryLayout] = useState({
        width: 800,
        height: 600,
        width_meters: 100,
        height_meters: 80,
    });

    useEffect(() => {
        const fetchFactoryData = async () => {
            try {
                // Fetch tenants data to get factory information (filtered by user's manufacturer)
                const tenantsResponse = await api.get('/api/simulator/tenants/my-data');
                const tenants = tenantsResponse.data;

                if (tenants && tenants.length > 0) {
                    // Collect all factories from all manufacturers and tenants
                    const factories: FactoryData[] = [];
                    tenants.forEach((tenant: any) => {
                        tenant.manufacturers?.forEach((manufacturer: any) => {
                            manufacturer.factories?.forEach((factory: any) => {
                                factories.push(factory);
                            });
                        });
                    });

                    setAllFactories(factories);

                    // Select the first factory if none is selected
                    if (factories.length > 0 && !selectedFactoryId) {
                        setSelectedFactoryId(factories[0].id);
                    }

                    // Get the currently selected factory or the first one
                    const currentFactory = factories.find(f => f.id === selectedFactoryId) || factories[0];

                    if (currentFactory) {
                        // Calculate pixel dimensions based on meter dimensions with a reasonable scale
                        const pixelsPerMeter = 6; // pixels per meter for better fit
                        const pixelWidth = currentFactory.width_meters * pixelsPerMeter;
                        const pixelHeight = currentFactory.height_meters * pixelsPerMeter;

                        setFactoryData(currentFactory);
                        setFactoryLayout({
                            width: pixelWidth,
                            height: pixelHeight,
                            width_meters: currentFactory.width_meters || 100,
                            height_meters: currentFactory.height_meters || 80,
                        });

                        // Convert PLCs to device positions (positions are now in meters from API)
                        const devicePositions: DevicePosition[] = currentFactory.plcs.map((plc) => ({
                            id: plc.id,
                            name: plc.name,
                            x: plc.x_position * pixelsPerMeter, // Convert meters to pixels
                            y: plc.y_position * pixelsPerMeter, // Convert meters to pixels
                            width: Math.min(40, Math.max(20, (plc.width || 2.5) * pixelsPerMeter)), // Scale from meters but clamp
                            height: Math.min(30, Math.max(15, (plc.height || 1.8) * pixelsPerMeter)), // Scale from meters but clamp
                            x_position: plc.x_position,
                            y_position: plc.y_position,
                            type: 'plc',
                            sensors: plc.sensors.map((sensor) => ({
                                name: sensor.signal_config.name,
                                value: sensor.signal_config.value,
                                unit: sensor.signal_config.unit,
                                lastUpdate: Date.now()
                            }))
                        }));

                        setDevices(devicePositions);
                    }
                }

                setIsLoading(false);
            } catch (error) {
                console.error('Failed to fetch factory data:', error);

                // Fallback to mock data
                const mockDevices: DevicePosition[] = [
                    { id: 'plc-1', name: 'Main PLC', x: 100, y: 100, width: 50, height: 30, x_position: 12.5, y_position: 13.33, type: 'plc', sensors: [] },
                    { id: 'motor-1', name: 'Conveyor Motor', x: 300, y: 150, width: 40, height: 25, x_position: 37.5, y_position: 20, type: 'motor', sensors: [] },
                    { id: 'sensor-1', name: 'Temp Sensor 1', x: 500, y: 200, width: 20, height: 15, x_position: 62.5, y_position: 26.67, type: 'sensor', sensors: [] },
                    { id: 'sensor-2', name: 'Pressure Sensor', x: 650, y: 300, width: 20, height: 15, x_position: 81.25, y_position: 40, type: 'sensor', sensors: [] },
                    { id: 'motor-2', name: 'Assembly Motor', x: 200, y: 400, width: 40, height: 25, x_position: 25, y_position: 53.33, type: 'motor', sensors: [] },
                    { id: 'plc-2', name: 'Backup PLC', x: 600, y: 500, width: 50, height: 30, x_position: 75, y_position: 66.67, type: 'plc', sensors: [] },
                ];
                setDevices(mockDevices);

                toast({
                    title: "Connection Error",
                    description: "Failed to fetch factory data, using mock data",
                    variant: "destructive",
                });
                setIsLoading(false);
            }
        };

        fetchFactoryData();
        const interval = setInterval(fetchFactoryData, 2000);

        return () => clearInterval(interval);
    }, [toast, selectedFactoryId]);

    useEffect(() => {
        const handleGlobalMouseMove = (e: MouseEvent) => {
            if (isDragging) {
                setPanOffset({
                    x: e.clientX - dragStart.x,
                    y: e.clientY - dragStart.y,
                });
            }
        };

        const handleGlobalMouseUp = () => {
            setIsDragging(false);
        };

        if (isDragging) {
            document.addEventListener('mousemove', handleGlobalMouseMove);
            document.addEventListener('mouseup', handleGlobalMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleGlobalMouseMove);
            document.removeEventListener('mouseup', handleGlobalMouseUp);
        };
    }, [isDragging, dragStart]);

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

    const renderFactoryShape = (shape: string, width: number, height: number, color: string) => {
        const fillColor = color || '#333333';
        const strokeColor = '#666666';

        switch (shape) {
            case 'L':
                return (
                    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="absolute inset-0 pointer-events-none">
                        {/* L-shape: filled areas */}
                        <rect x="0" y="0" width={width} height={height} fill="transparent" />
                        <rect x="0" y="0" width="20" height={height} fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                        <rect x="0" y={height - 20} width={width} height="20" fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                    </svg>
                );
            case 'I':
                return (
                    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="absolute inset-0 pointer-events-none">
                        {/* I-shape: filled vertical bar */}
                        <rect x={width / 2 - 10} y="0" width="20" height={height} fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                    </svg>
                );
            case 'Z':
                return (
                    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="absolute inset-0 pointer-events-none">
                        {/* Z-shape: filled areas */}
                        <rect x="0" y="0" width={width} height="20" fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                        <rect x={width - 20} y="0" width="20" height={height} fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                        <rect x="0" y={height - 20} width={width} height="20" fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                    </svg>
                );
            case 'rectangle':
            default:
                return (
                    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="absolute inset-0 pointer-events-none">
                        {/* Filled rectangle */}
                        <rect x="0" y="0" width={width} height={height} fill={fillColor} stroke={strokeColor} strokeWidth="1" />
                    </svg>
                );
        }
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        e.preventDefault();
        if (e.target === e.currentTarget) { // Only start drag if clicking on the background
            setIsDragging(true);
            setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (isDragging) {
            setPanOffset({
                x: e.clientX - dragStart.x,
                y: e.clientY - dragStart.y,
            });
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    const handleWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        setZoom(prevZoom => Math.max(0.5, Math.min(2, prevZoom * zoomFactor)));
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
                    {/* Factory Selection and Map */}
                    <div className="lg:col-span-2">
                        {/* Factory Selection Dropdown */}
                        {allFactories.length > 1 && (
                            <Card className="mb-4">
                                <CardContent className="pt-6">
                                    <div className="flex items-center gap-4">
                                        <label htmlFor="factory-select" className="text-sm font-medium">
                                            Select Factory:
                                        </label>
                                        <Select value={selectedFactoryId} onValueChange={setSelectedFactoryId}>
                                            <SelectTrigger className="w-64">
                                                <SelectValue placeholder="Choose a factory" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {allFactories.map((factory) => (
                                                    <SelectItem key={factory.id} value={factory.id}>
                                                        {factory.name} ({factory.shape} - {factory.width_meters}m × {factory.height_meters}m)
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Factory className="h-5 w-5" />
                                    {factoryData ? `${factoryData.name} Layout` : 'Factory Layout'}
                                </CardTitle>
                                {factoryData && (
                                    <p className="text-sm text-muted-foreground">
                                        Dimensions: {factoryData.width_meters}m × {factoryData.height_meters}m
                                    </p>
                                )}
                            </CardHeader>
                            <CardContent>
                                <div className="mb-4 flex items-center justify-between">
                                    <div className="text-sm text-muted-foreground">
                                        Drag to pan • Scroll to zoom • Click devices for details
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                                            className="px-2 py-1 text-xs bg-secondary rounded hover:bg-secondary/80"
                                            disabled={zoom <= 0.5}
                                        >
                                            Zoom Out
                                        </button>
                                        <span className="text-xs text-muted-foreground min-w-[60px] text-center">
                                            {Math.round(zoom * 100)}%
                                        </span>
                                        <button
                                            onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                                            className="px-2 py-1 text-xs bg-secondary rounded hover:bg-secondary/80"
                                            disabled={zoom >= 2}
                                        >
                                            Zoom In
                                        </button>
                                    </div>
                                </div>

                                <div
                                    className={`relative bg-black border-2 border-gray-600 rounded-lg overflow-hidden mx-auto ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
                                    style={{
                                        height: '600px',
                                        width: '100%',
                                        maxWidth: '800px',
                                    }}
                                    onMouseDown={handleMouseDown}
                                    onMouseMove={handleMouseMove}
                                    onMouseUp={handleMouseUp}
                                    onMouseLeave={handleMouseUp}
                                    onWheel={handleWheel}
                                >
                                    <div
                                        className="relative w-full h-full"
                                        style={{
                                            transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoom})`,
                                            transformOrigin: 'center',
                                            transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                                        }}
                                    >
                                        {/* Factory Shape Overlay */}
                                        {factoryData && renderFactoryShape(
                                            factoryData.shape || 'rectangle',
                                            factoryLayout.width,
                                            factoryLayout.height,
                                            factoryData.wireframe_color || '#666666'
                                        )}

                                        {devices.map((device) => {
                                            // Ensure devices stay within factory bounds (in pixels)
                                            const maxX = factoryLayout.width - device.width;
                                            const maxY = factoryLayout.height - device.height;
                                            const clampedX = Math.max(0, Math.min(device.x, maxX));
                                            const clampedY = Math.max(0, Math.min(device.y, maxY));

                                            return (
                                                <div
                                                    key={device.id}
                                                    className="absolute cursor-pointer transition-all duration-200 hover:scale-105 z-10"
                                                    style={{
                                                        left: `${(clampedX / factoryLayout.width) * 100}%`,
                                                        top: `${(clampedY / factoryLayout.height) * 100}%`,
                                                        width: `${device.width}px`,
                                                        height: `${device.height}px`,
                                                    }}
                                                    onMouseEnter={() => setHoveredDevice(device)}
                                                    onMouseLeave={() => setHoveredDevice(null)}
                                                    onClick={() => setSelectedDevice(device)}
                                                >
                                                    <div
                                                        className="w-full h-full rounded flex items-center justify-center text-white font-bold shadow-lg border-2 border-white"
                                                        style={{ backgroundColor: getDeviceColor(device.type, device.sensors) }}
                                                    >
                                                        {getDeviceIcon(device.type)}
                                                    </div>
                                                </div>
                                            );
                                        })}

                                        {/* Hover Tooltip */}
                                        {/* Hover Tooltip */}
                                        {hoveredDevice && (() => {
                                            const tooltipX = Math.max(0, Math.min(hoveredDevice.x, factoryLayout.width - 60));
                                            const tooltipY = Math.max(0, Math.min(hoveredDevice.y, factoryLayout.height - 40));
                                            return (
                                                <div
                                                    className="absolute bg-black text-white px-3 py-2 rounded-lg text-sm pointer-events-none z-20 shadow-lg"
                                                    style={{
                                                        left: `${(tooltipX / factoryLayout.width) * 100}%`,
                                                        top: `${(tooltipY / factoryLayout.height) * 100}%`,
                                                        transform: 'translateX(10px) translateY(-100%)',
                                                    }}
                                                >
                                                    <div className="font-semibold">{hoveredDevice.name}</div>
                                                    <div className="text-xs opacity-90">{hoveredDevice.type.toUpperCase()}</div>
                                                </div>
                                            );
                                        })()}
                                    </div>
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
                                                Position: ({selectedDevice.x_position.toFixed(1)}m, {selectedDevice.y_position.toFixed(1)}m)
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