import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import Layout from "@/components/Layout";
import { api } from "@/lib/api";

interface Device {
    id: string;
    name: string;
    type: string;
    factoryId: string;
    status: string;
}

interface Factory {
    id: string;
    name: string;
    location: string;
}

interface Signal {
    id: string;
    name: string;
    deviceId: string;
    type: string;
    unit: string;
    value: number;
}

interface CanvasItem {
    id: string;
    type: 'factory' | 'device' | 'signal';
    data: any;
    x: number;
    y: number;
}

interface DashboardTemplate {
    id: string;
    name: string;
    description: string;
    items: CanvasItem[];
}

const DashboardBuilder = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [factories, setFactories] = useState<Factory[]>([]);
    const [signals, setSignals] = useState<Signal[]>([]);
    const [loading, setLoading] = useState(false);
    const [canvasItems, setCanvasItems] = useState<CanvasItem[]>([]);
    const [showTemplates, setShowTemplates] = useState(false);

    const templates: DashboardTemplate[] = [
        {
            id: 'factory-overview',
            name: 'Factory Overview',
            description: 'Comprehensive factory monitoring with key metrics from live data',
            items: [] // Will be populated with real data when loaded
        },
        {
            id: 'device-monitoring',
            name: 'Device Monitoring',
            description: 'Focus on device status and performance from live data',
            items: [] // Will be populated with real data when loaded
        },
        {
            id: 'signal-dashboard',
            name: 'Signal Dashboard',
            description: 'Real-time signal monitoring and KPIs from live data',
            items: [] // Will be populated with real data when loaded
        }
    ];

    // Fetch real data from APIs
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [devicesRes, factoriesRes, signalsRes] = await Promise.all([
                    api.get('/api/simulator/devices'),
                    api.get('/api/mcp/factories'),
                    api.get('/api/simulator/signals')
                ]);
                setDevices(devicesRes.data);
                setFactories(factoriesRes.data.data || []);
                setSignals(signalsRes.data);
            } catch (error) {
                console.error('Failed to fetch data:', error);
                // Set empty arrays on error to ensure clean state
                setDevices([]);
                setFactories([]);
                setSignals([]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <>
            <Layout>
                <div className="container mx-auto p-6">
                    <div className="mb-6">
                        <h1 className="text-3xl font-bold">Dashboard Builder</h1>
                        <p className="text-muted-foreground">
                            Drag and drop components to create custom dashboards
                        </p>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        {/* Data Sources Sidebar */}
                        <div className="lg:col-span-1 space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Factories</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ScrollArea className="h-48">
                                        {loading ? (
                                            <div className="flex items-center justify-center h-full">
                                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                {factories.length === 0 ? (
                                                    <p className="text-sm text-muted-foreground text-center py-4">No factories available</p>
                                                ) : (
                                                    factories.map((factory) => (
                                                        <div
                                                            key={factory.id}
                                                            className="p-2 border rounded cursor-pointer hover:bg-accent"
                                                            draggable
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('text/plain', JSON.stringify({ type: 'factory', data: factory }));
                                                            }}
                                                        >
                                                            <div className="font-medium">{factory.name}</div>
                                                            <div className="text-sm text-muted-foreground">{factory.location}</div>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        )}
                                    </ScrollArea>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Devices</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ScrollArea className="h-48">
                                        {loading ? (
                                            <div className="flex items-center justify-center h-full">
                                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                {devices.length === 0 ? (
                                                    <p className="text-sm text-muted-foreground text-center py-4">No devices available</p>
                                                ) : (
                                                    devices.map((device) => (
                                                        <div
                                                            key={device.id}
                                                            className="p-2 border rounded cursor-pointer hover:bg-accent"
                                                            draggable
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('text/plain', JSON.stringify({ type: 'device', data: device }));
                                                            }}
                                                        >
                                                            <div className="font-medium">{device.name}</div>
                                                            <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold">{device.type}</span>
                                                            <div className="text-sm text-muted-foreground">Status: {device.status}</div>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        )}
                                    </ScrollArea>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Signals</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ScrollArea className="h-48">
                                        {loading ? (
                                            <div className="flex items-center justify-center h-full">
                                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                {signals.length === 0 ? (
                                                    <p className="text-sm text-muted-foreground text-center py-4">No signals available</p>
                                                ) : (
                                                    signals.map((signal) => (
                                                        <div
                                                            key={signal.id}
                                                            className="p-2 border rounded cursor-pointer hover:bg-accent"
                                                            draggable
                                                            onDragStart={(e) => {
                                                                e.dataTransfer.setData('text/plain', JSON.stringify({ type: 'signal', data: signal }));
                                                            }}
                                                        >
                                                            <div className="font-medium">{signal.name}</div>
                                                            <div className="text-sm text-muted-foreground">
                                                                {signal.type} • {signal.unit} • {signal.value}
                                                            </div>
                                                        </div>
                                                    ))
                                                )}
                                            </div>
                                        )}
                                    </ScrollArea>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Dashboard Canvas */}
                        <div className="lg:col-span-3">
                            <Card className="h-full">
                                <CardHeader>
                                    <CardTitle>Dashboard Canvas</CardTitle>
                                    <div className="flex gap-2">
                                        <Button variant="outline" size="sm">Save Dashboard</Button>
                                        <Button variant="outline" size="sm" onClick={() => setShowTemplates(true)}>Load Template</Button>
                                        <Button variant="outline" size="sm">Export</Button>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div
                                        className="min-h-96 border-2 border-dashed border-muted-foreground/25 rounded-lg p-4"
                                        onDragOver={(e) => e.preventDefault()}
                                        onDrop={(e) => {
                                            e.preventDefault();
                                            const data = JSON.parse(e.dataTransfer.getData('text/plain'));
                                            const rect = e.currentTarget.getBoundingClientRect();
                                            const x = e.clientX - rect.left;
                                            const y = e.clientY - rect.top;
                                            const newItem: CanvasItem = {
                                                id: `${data.type}-${Date.now()}`,
                                                type: data.type,
                                                data: data.data,
                                                x,
                                                y,
                                            };
                                            setCanvasItems(prev => [...prev, newItem]);
                                        }}
                                    >
                                        {canvasItems.map((item) => (
                                            <div
                                                key={item.id}
                                                className="absolute p-2 bg-white border rounded shadow-sm"
                                                style={{ left: item.x, top: item.y }}
                                            >
                                                {item.type === 'factory' && (
                                                    <div>
                                                        <div className="font-medium">{item.data.name}</div>
                                                        <div className="text-sm text-muted-foreground">{item.data.location}</div>
                                                    </div>
                                                )}
                                                {item.type === 'device' && (
                                                    <div>
                                                        <div className="font-medium">{item.data.name}</div>
                                                        <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold">{item.data.type}</span>
                                                        <div className="text-sm text-muted-foreground">Status: {item.data.status}</div>
                                                    </div>
                                                )}
                                                {item.type === 'signal' && (
                                                    <div>
                                                        <div className="font-medium">{item.data.name}</div>
                                                        <div className="text-sm text-muted-foreground">
                                                            {item.data.type} • {item.data.unit} • {item.data.value}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                        {canvasItems.length === 0 && (
                                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                                <div className="text-center">
                                                    <p className="text-lg mb-2">Drop components here</p>
                                                    <p className="text-sm">Drag factories, devices, or signals from the sidebar</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </Layout>

            <Dialog open={showTemplates} onOpenChange={setShowTemplates}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Choose a Dashboard Template</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4">
                        {templates.map((template) => (
                            <Card key={template.id} className="cursor-pointer hover:bg-accent" onClick={() => {
                                // Load template with real data
                                const populatedItems: CanvasItem[] = [];
                                let xOffset = 50;
                                const yOffset = 50;

                                if (template.id === 'factory-overview') {
                                    // Add first available factory
                                    if (factories.length > 0) {
                                        populatedItems.push({
                                            id: `factory-${factories[0].id}`,
                                            type: 'factory',
                                            data: factories[0],
                                            x: xOffset,
                                            y: yOffset
                                        });
                                        xOffset += 200;
                                    }
                                    // Add first available device
                                    if (devices.length > 0) {
                                        populatedItems.push({
                                            id: `device-${devices[0].id}`,
                                            type: 'device',
                                            data: devices[0],
                                            x: xOffset,
                                            y: yOffset
                                        });
                                        xOffset += 200;
                                    }
                                    // Add first available signal
                                    if (signals.length > 0) {
                                        populatedItems.push({
                                            id: `signal-${signals[0].id}`,
                                            type: 'signal',
                                            data: signals[0],
                                            x: xOffset,
                                            y: yOffset
                                        });
                                    }
                                } else if (template.id === 'device-monitoring') {
                                    // Add first two devices
                                    devices.slice(0, 2).forEach((device, index) => {
                                        populatedItems.push({
                                            id: `device-${device.id}`,
                                            type: 'device',
                                            data: device,
                                            x: 50 + (index * 200),
                                            y: yOffset
                                        });
                                    });
                                } else if (template.id === 'signal-dashboard') {
                                    // Add first two signals
                                    signals.slice(0, 2).forEach((signal, index) => {
                                        populatedItems.push({
                                            id: `signal-${signal.id}`,
                                            type: 'signal',
                                            data: signal,
                                            x: 50 + (index * 200),
                                            y: yOffset
                                        });
                                    });
                                }

                                setCanvasItems(populatedItems);
                                setShowTemplates(false);
                            }}>
                                <CardHeader>
                                    <CardTitle className="text-lg">{template.name}</CardTitle>
                                    <p className="text-sm text-muted-foreground">{template.description}</p>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm">
                                        {template.id === 'factory-overview' && `${Math.min(3, factories.length + devices.length + signals.length)} components`}
                                        {template.id === 'device-monitoring' && `${Math.min(2, devices.length)} components`}
                                        {template.id === 'signal-dashboard' && `${Math.min(2, signals.length)} components`}
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
};

export default DashboardBuilder;