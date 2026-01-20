import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import Layout from "@/components/Layout";
import { apiClient } from "@/lib/api";
import {
    DndContext,
    DragEndEvent,
    DragOverlay,
    DragStartEvent,
    PointerSensor,
    useSensor,
    useSensors,
    closestCenter,
    useDraggable,
    useDroppable,
} from "@dnd-kit/core";
import {
    SortableContext,
    arrayMove,
    rectSortingStrategy,
} from "@dnd-kit/sortable";
import {
    useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

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
    location?: string;
    factory_id?: string;
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
    type: 'factory' | 'device' | 'signal' | 'chart' | 'gauge' | 'button';
    data: any;
    x: number;
    y: number;
    width: number;
    height: number;
    gridX: number;
    gridY: number;
    gridWidth: number;
    gridHeight: number;
}

interface Dashboard {
    id?: string;
    name: string;
    description: string;
    items: CanvasItem[];
    gridSize: number;
    autoTile: boolean;
    userId: string;
    createdAt?: string;
    updatedAt?: string;
}

interface DashboardTemplate {
    id: string;
    name: string;
    description: string;
    items: CanvasItem[];
}

const CanvasItem = ({ item, onRemove, onSendSignal }: {
    item: CanvasItem;
    onRemove: (id: string) => void;
    onSendSignal?: (id: string, value: any) => void
}) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: item.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    const renderItem = () => {
        switch (item.type) {
            case 'factory':
                return (
                    <Card className="h-full">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">🏭 {item.data.name || item.data.factory_id}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-xs text-muted-foreground">Factory Monitor</p>
                            <Badge variant="outline" className="mt-2">Active</Badge>
                        </CardContent>
                    </Card>
                );
            case 'device':
                return (
                    <Card className="h-full">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">⚙️ {item.data.name}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-xs text-muted-foreground">Type: {item.data.type}</p>
                            <Badge variant={item.data.status === 'online' ? 'default' : 'secondary'} className="mt-2">
                                {item.data.status || 'Unknown'}
                            </Badge>
                        </CardContent>
                    </Card>
                );
            case 'signal':
                return (
                    <Card className="h-full">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">📊 {item.data.name}</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-lg font-bold">{item.data.value || 'N/A'}</p>
                            <p className="text-xs text-muted-foreground">{item.data.unit}</p>
                            <div className="flex gap-2 mt-2">
                                <Button size="sm" variant="outline" onClick={() => onSendSignal?.(item.data.id, 1)}>
                                    ON
                                </Button>
                                <Button size="sm" variant="outline" onClick={() => onSendSignal?.(item.data.id, 0)}>
                                    OFF
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                );
            case 'chart':
                return (
                    <Card className="h-full">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">📈 Chart</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="h-32 bg-muted rounded flex items-center justify-center">
                                <span className="text-muted-foreground">Chart Placeholder</span>
                            </div>
                        </CardContent>
                    </Card>
                );
            case 'gauge':
                return (
                    <Card className="h-full">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">⭕ Gauge</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="h-32 bg-muted rounded flex items-center justify-center">
                                <span className="text-muted-foreground">Gauge Placeholder</span>
                            </div>
                        </CardContent>
                    </Card>
                );
            case 'button':
                return (
                    <Card className="h-full">
                        <CardContent className="p-4">
                            <Button className="w-full" onClick={() => onSendSignal?.(item.data.id, item.data.value)}>
                                {item.data.label || 'Button'}
                            </Button>
                        </CardContent>
                    </Card>
                );
            default:
                return <div>Unknown item type</div>;
        }
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...attributes}
            {...listeners}
            className="relative group cursor-move"
        >
            {renderItem()}
            <Button
                variant="destructive"
                size="sm"
                className="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                    e.stopPropagation();
                    onRemove(item.id);
                }}
            >
                ×
            </Button>
        </div>
    );
};

const DraggableSidebarItem = ({ id, children, onClick }: { id: string; children: React.ReactNode; onClick?: () => void }) => {
    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
        id,
    });

    const style = {
        transform: CSS.Transform.toString(transform),
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...listeners}
            {...attributes}
            onClick={onClick}
            className="cursor-grab active:cursor-grabbing"
        >
            {children}
        </div>
    );
};

const DroppableCanvas = ({ children }: { children: React.ReactNode }) => {
    const { setNodeRef, isOver } = useDroppable({
        id: 'canvas-drop-zone',
    });

    return (
        <div
            ref={setNodeRef}
            className={`relative bg-muted/20 border-2 border-dashed rounded-lg min-h-[600px] overflow-auto ${isOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/20'
                }`}
            style={{
                backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
                backgroundSize: '20px 20px',
            }}
        >
            {children}
        </div>
    );
};

const DashboardBuilder = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [factories, setFactories] = useState<Factory[]>([]);
    const [signals, setSignals] = useState<Signal[]>([]);
    const [loading, setLoading] = useState(false);
    const [canvasItems, setCanvasItems] = useState<CanvasItem[]>([]);
    const [activeId, setActiveId] = useState<string | null>(null);
    const [gridSize, setGridSize] = useState(20);
    const [autoTile, setAutoTile] = useState(true);
    const [savedDashboards, setSavedDashboards] = useState<Dashboard[]>([]);
    const [currentDashboard, setCurrentDashboard] = useState<Dashboard | null>(null);
    const [dashboardName, setDashboardName] = useState('');
    const [dashboardDescription, setDashboardDescription] = useState('');

    const sensors = useSensor(PointerSensor, {
        activationConstraint: {
            distance: 8,
        },
    });
    const sensorsList = useSensors(sensors);

    const templates: DashboardTemplate[] = [
        {
            id: 'factory-overview',
            name: 'Factory Overview',
            description: 'Comprehensive factory monitoring dashboard',
            items: factories.slice(0, 3).map((factory, index) => ({
                id: `template-factory-${factory.id}`,
                type: 'factory' as const,
                data: factory,
                x: index * 320,
                y: 0,
                width: 300,
                height: 200,
                gridX: index * 16,
                gridY: 0,
                gridWidth: 15,
                gridHeight: 10,
            })),
        },
        {
            id: 'device-monitoring',
            name: 'Device Monitoring',
            description: 'Real-time device status and performance',
            items: devices.slice(0, 4).map((device, index) => ({
                id: `template-device-${device.id}`,
                type: 'device' as const,
                data: device,
                x: (index % 2) * 320,
                y: Math.floor(index / 2) * 220,
                width: 300,
                height: 200,
                gridX: (index % 2) * 16,
                gridY: Math.floor(index / 2) * 11,
                gridWidth: 15,
                gridHeight: 10,
            })),
        },
        {
            id: 'signal-dashboard',
            name: 'Signal Dashboard',
            description: 'Real-time signal monitoring with controls',
            items: signals.slice(0, 6).map((signal, index) => ({
                id: `template-signal-${signal.id}`,
                type: 'signal' as const,
                data: signal,
                x: (index % 3) * 220,
                y: Math.floor(index / 3) * 180,
                width: 200,
                height: 160,
                gridX: (index % 3) * 11,
                gridY: Math.floor(index / 3) * 9,
                gridWidth: 10,
                gridHeight: 8,
            })),
        },
    ];

    // Fetch real data from APIs
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [devices, factories, signals] = await Promise.all([
                    apiClient.get('/simulator/devices'),
                    apiClient.get('/mcp/factories'),
                    apiClient.get('/simulator/signals')
                ]);

                // Transform device data to match frontend interface
                const transformedDevices = (devices || []).map((device: any) => ({
                    id: device.id,
                    name: device.name,
                    type: device.deviceType,
                    factoryId: device.factory_id || '',
                    status: device.is_active ? 'active' : 'inactive'
                }));

                setDevices(transformedDevices);
                setFactories(factoriesRes.data?.data || []);
                setSignals(signalsRes.data || []);
                console.log('Fetched data:', { devices: devicesRes.data, factories: factoriesRes.data, signals: signalsRes.data });
            } catch (error) {
                console.error('Failed to fetch data:', error);
                // Set empty arrays on error
                setDevices([]);
                setFactories([]);
                setSignals([]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Rearrange items when autoTile changes or items are added/removed
    const prevItemsLengthRef = React.useRef(canvasItems.length);
    const prevAutoTileRef = React.useRef(autoTile);
    useEffect(() => {
        const currentLength = canvasItems.length;
        const lengthChanged = currentLength !== prevItemsLengthRef.current;
        const autoTileChanged = autoTile !== prevAutoTileRef.current;
        prevItemsLengthRef.current = currentLength;
        prevAutoTileRef.current = autoTile;

        if (autoTile && canvasItems.length > 0 && (lengthChanged || autoTileChanged)) {
            // Auto-tile mode: arrange items in a compact grid that fills the space without overlaps
            setCanvasItems(prev => {
                const items = [...prev];
                const canvasWidth = 800; // Approximate canvas width
                const canvasHeight = 600; // Approximate canvas height
                const padding = 10;

                // Sort items by size (larger items first for better packing)
                const sortedItems = items.sort((a, b) => (b.width * b.height) - (a.width * a.height));

                // Initialize placed items array
                const placedItems: CanvasItem[] = [];
                const occupiedRects: { x: number; y: number; width: number; height: number }[] = [];

                const checkOverlap = (x: number, y: number, width: number, height: number): boolean => {
                    return occupiedRects.some(rect =>
                        !(x + width + padding <= rect.x ||
                            rect.x + rect.width + padding <= x ||
                            y + height + padding <= rect.y ||
                            rect.y + rect.height + padding <= y)
                    );
                };

                const findBestPosition = (itemWidth: number, itemHeight: number) => {
                    const maxX = canvasWidth - itemWidth;
                    const maxY = canvasHeight - itemHeight;

                    // Smart 2D packing: try to fill both horizontally and vertically efficiently
                    let bestPosition = { x: 0, y: 0 };
                    let bestScore = -1;

                    // Check positions in a way that balances horizontal and vertical filling
                    const stepSize = 25;

                    for (let y = 0; y <= maxY; y += stepSize) {
                        for (let x = 0; x <= maxX; x += stepSize) {
                            if (!checkOverlap(x, y, itemWidth, itemHeight)) {
                                // Calculate a score based on multiple factors:
                                // 1. How much space this leaves for future items (higher is better)
                                // 2. How "compact" the layout becomes (prefer positions that fill gaps)
                                const spaceBelow = Math.max(0, maxY - (y + itemHeight));
                                const spaceRight = Math.max(0, maxX - (x + itemWidth));

                                // Bonus for positions that allow stacking below
                                const canStackBelow = y + itemHeight + stepSize <= maxY;
                                const canStackRight = x + itemWidth + stepSize <= maxX;

                                let score = spaceBelow + spaceRight;

                                // Prefer positions that allow stacking in both directions equally
                                if (canStackBelow) score += 50;
                                if (canStackRight) score += 50;

                                // Prefer positions closer to top-left for more natural layout
                                score -= (x + y) * 0.1;

                                if (score > bestScore) {
                                    bestScore = score;
                                    bestPosition = { x, y };
                                }
                            }
                        }
                    }

                    // If we found a good position, return it
                    if (bestScore >= 0) {
                        return bestPosition;
                    }

                    // Fallback: fine-grained search
                    for (let y = 0; y <= maxY; y += 10) {
                        for (let x = 0; x <= maxX; x += 10) {
                            if (!checkOverlap(x, y, itemWidth, itemHeight)) {
                                return { x, y };
                            }
                        }
                    }

                    // Ultimate fallback
                    return { x: Math.max(0, canvasWidth - itemWidth), y: Math.max(0, canvasHeight - itemHeight) };
                };

                sortedItems.forEach(item => {
                    const itemWidth = item.width || 200;
                    const itemHeight = item.height || 150;
                    const position = findBestPosition(itemWidth, itemHeight);

                    const placedItem = {
                        ...item,
                        x: position.x,
                        y: position.y,
                        gridX: Math.floor(position.x / gridSize),
                        gridY: Math.floor(position.y / gridSize),
                        width: itemWidth,
                        height: itemHeight,
                    };

                    placedItems.push(placedItem);
                    occupiedRects.push({
                        x: position.x,
                        y: position.y,
                        width: itemWidth,
                        height: itemHeight
                    });
                });

                return placedItems;
            });
        } else if (!autoTile) {
            // Floating mode: allow free positioning, items stay where they are
            // but ensure they don't go off-screen when switching from auto-tile
            setCanvasItems(prev =>
                prev.map(item => ({
                    ...item,
                    // Keep current positions but ensure they're within reasonable bounds
                    x: Math.max(0, Math.min(item.x, 800 - (item.width || 200))),
                    y: Math.max(0, Math.min(item.y, 600 - (item.height || 150))),
                }))
            );
        }
    }, [autoTile]);

    const addItemToCanvas = useCallback((type: CanvasItem['type'], data: any) => {
        // Calculate next available position in grid without overlaps
        const calculateNextPosition = () => {
            if (!autoTile) {
                return {
                    x: Math.random() * 400,
                    y: Math.random() * 300,
                    gridX: Math.floor(Math.random() * 20),
                    gridY: Math.floor(Math.random() * 15),
                };
            }

            // Find next available position using smart 2D packing
            const itemWidth = 200;
            const itemHeight = 150;
            const padding = 10;
            const maxX = 800 - itemWidth;
            const maxY = 600 - itemHeight;

            const checkOverlap = (x: number, y: number) => {
                return canvasItems.some(item =>
                    !(x + itemWidth + padding <= item.x ||
                        item.x + (item.width || 200) + padding <= x ||
                        y + itemHeight + padding <= item.y ||
                        item.y + (item.height || 150) + padding <= y)
                );
            };

            // Smart 2D packing: try to fill both horizontally and vertically efficiently
            let bestPosition = { x: 0, y: 0 };
            let bestScore = -1;

            // Check positions in a way that balances horizontal and vertical filling
            const stepSize = 25;

            for (let y = 0; y <= maxY; y += stepSize) {
                for (let x = 0; x <= maxX; x += stepSize) {
                    if (!checkOverlap(x, y)) {
                        // Calculate a score based on multiple factors:
                        // 1. How much space this leaves for future items (higher is better)
                        // 2. How "compact" the layout becomes (prefer positions that fill gaps)
                        const spaceBelow = Math.max(0, maxY - (y + itemHeight));
                        const spaceRight = Math.max(0, maxX - (x + itemWidth));

                        // Bonus for positions that allow stacking below
                        const canStackBelow = y + itemHeight + stepSize <= maxY;
                        const canStackRight = x + itemWidth + stepSize <= maxX;

                        let score = spaceBelow + spaceRight;

                        // Heavily prefer positions that allow vertical stacking
                        if (canStackBelow) score += 100;
                        if (canStackRight) score += 50;

                        // Prefer positions closer to top-left for more natural layout
                        score -= (x + y) * 0.1;

                        if (score > bestScore) {
                            bestScore = score;
                            bestPosition = { x, y };
                        }
                    }
                }
            }

            // If we found a good position, return it
            if (bestScore >= 0) {
                return {
                    x: bestPosition.x,
                    y: bestPosition.y,
                    gridX: Math.floor(bestPosition.x / gridSize),
                    gridY: Math.floor(bestPosition.y / gridSize),
                };
            }

            // Fallback: fine-grained search
            for (let y = 0; y <= maxY; y += 10) {
                for (let x = 0; x <= maxX; x += 10) {
                    if (!checkOverlap(x, y)) {
                        return {
                            x,
                            y,
                            gridX: Math.floor(x / gridSize),
                            gridY: Math.floor(y / gridSize),
                        };
                    }
                }
            }

            // Ultimate fallback
            return {
                x: Math.max(0, 800 - itemWidth),
                y: Math.max(0, 600 - itemHeight),
                gridX: Math.floor((800 - itemWidth) / gridSize),
                gridY: Math.floor((600 - itemHeight) / gridSize),
            };
        }; const position = calculateNextPosition();

        const newItem: CanvasItem = {
            id: `${type}-${Date.now()}`,
            type,
            data,
            x: position.x,
            y: position.y,
            width: 200,
            height: 150,
            gridX: position.gridX,
            gridY: position.gridY,
            gridWidth: Math.ceil(200 / gridSize),
            gridHeight: Math.ceil(150 / gridSize),
        };
        setCanvasItems(prev => [...prev, newItem]);
    }, [autoTile, canvasItems, gridSize]);

    const removeItemFromCanvas = useCallback((id: string) => {
        setCanvasItems(prev => prev.filter(item => item.id !== id));
    }, []);

    const sendSignalToPLC = useCallback(async (signalId: string, value: any) => {
        try {
            await apiClient.post('/simulator/signals/send', { signalId, value });
            console.log('Signal sent to PLC:', { signalId, value });
        } catch (error) {
            console.error('Failed to send signal:', error);
        }
    }, []);

    const applyTemplate = useCallback((template: DashboardTemplate) => {
        setCanvasItems(template.items.map(item => ({
            ...item,
            id: `${item.type}-${Date.now()}-${Math.random()}`,
        })));
    }, []);

    const saveDashboard = useCallback(async () => {
        if (!dashboardName.trim()) return;

        const dashboard: Dashboard = {
            name: dashboardName,
            description: dashboardDescription,
            items: canvasItems,
            gridSize,
            autoTile,
            userId: 'current-user', // TODO: Get from auth context
        };

        try {
            if (currentDashboard?.id) {
                await apiClient.put(`/dashboards/${currentDashboard.id}`, dashboard);
            } else {
                const response = await apiClient.post('/dashboards', dashboard);
                setCurrentDashboard(response);
            }
            // Refresh saved dashboards
            loadSavedDashboards();
        } catch (error) {
            console.error('Failed to save dashboard:', error);
        }
    }, [dashboardName, dashboardDescription, canvasItems, gridSize, autoTile, currentDashboard]);

    const loadSavedDashboards = useCallback(async () => {
        try {
            const response = await apiClient.get('/dashboards');
            setSavedDashboards(response || []);
        } catch (error) {
            console.error('Failed to load dashboards:', error);
        }
    }, []);

    const loadDashboard = useCallback((dashboard: Dashboard) => {
        setCurrentDashboard(dashboard);
        setCanvasItems(dashboard.items);
        setGridSize(dashboard.gridSize);
        setAutoTile(dashboard.autoTile);
        setDashboardName(dashboard.name);
        setDashboardDescription(dashboard.description || '');
    }, []);

    const exportDashboard = useCallback((format: 'csv' | 'json' | 'png') => {
        switch (format) {
            case 'json':
                const dataStr = JSON.stringify({
                    dashboard: currentDashboard,
                    items: canvasItems,
                    exportedAt: new Date().toISOString(),
                }, null, 2);
                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${dashboardName || 'dashboard'}.json`;
                link.click();
                break;
            case 'csv':
                // Export canvas items as CSV
                const csvContent = [
                    ['ID', 'Type', 'Name', 'X', 'Y', 'Width', 'Height'].join(','),
                    ...canvasItems.map(item => [
                        item.id,
                        item.type,
                        item.data?.name || item.data?.factory_id || 'Unknown',
                        item.x,
                        item.y,
                        item.width,
                        item.height,
                    ].join(','))
                ].join('\n');
                const csvBlob = new Blob([csvContent], { type: 'text/csv' });
                const csvUrl = URL.createObjectURL(csvBlob);
                const csvLink = document.createElement('a');
                csvLink.href = csvUrl;
                csvLink.download = `${dashboardName || 'dashboard'}.csv`;
                csvLink.click();
                break;
            case 'png':
                // For PNG export, we'd need html2canvas or similar
                alert('PNG export not yet implemented');
                break;
        }
    }, [canvasItems, currentDashboard, dashboardName]);

    useEffect(() => {
        loadSavedDashboards();
    }, [loadSavedDashboards]);

    const handleDragStart = (event: DragStartEvent) => {
        setActiveId(event.active.id as string);
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over, delta } = event;
        setActiveId(null);

        if (!over) return;

        const activeId = active.id as string;
        const overId = over.id as string;

        // Handle dropping from sidebar onto canvas
        if (activeId.startsWith('sidebar-')) {
            const parts = activeId.split('-');
            const itemType = parts[1] as CanvasItem['type'];
            const itemId = parts.slice(2).join('-'); // For items with IDs in the name

            let itemData: any = {};

            // Get data based on type
            switch (itemType) {
                case 'factory':
                    itemData = factories.find(f => f.id === itemId);
                    break;
                case 'device':
                    itemData = devices.find(d => d.id === itemId);
                    break;
                case 'signal':
                    itemData = signals.find(s => s.id === itemId);
                    break;
                case 'chart':
                    itemData = { label: 'Chart' };
                    break;
                case 'gauge':
                    itemData = { label: 'Gauge' };
                    break;
                case 'button':
                    itemData = { label: 'Button', value: 1 };
                    break;
            }

            if (itemData) {
                addItemToCanvas(itemType, itemData);
            }
            return;
        }

        // Handle repositioning items on canvas (only when autoTile is disabled)
        if (!autoTile && overId === 'canvas-drop-zone' && delta) {
            setCanvasItems(prev => prev.map(item => {
                if (item.id === activeId) {
                    return {
                        ...item,
                        x: Math.max(0, item.x + delta.x),
                        y: Math.max(0, item.y + delta.y),
                        gridX: Math.floor((item.x + delta.x) / gridSize),
                        gridY: Math.floor((item.y + delta.y) / gridSize),
                    };
                }
                return item;
            }));
            return;
        }

        // Handle dropping items into charts
        if (overId.startsWith('chart-')) {
            const chartItem = canvasItems.find(item => item.id === overId);
            if (chartItem && chartItem.type === 'chart') {
                const draggedItem = canvasItems.find(item => item.id === activeId);
                if (draggedItem && (draggedItem.type === 'signal' || draggedItem.type === 'device')) {
                    // Add data binding to chart
                    setCanvasItems(prev => prev.map(item => {
                        if (item.id === overId) {
                            return {
                                ...item,
                                data: {
                                    ...item.data,
                                    dataSources: [
                                        ...(item.data.dataSources || []),
                                        {
                                            id: draggedItem.id,
                                            type: draggedItem.type,
                                            data: draggedItem.data
                                        }
                                    ]
                                }
                            };
                        }
                        return item;
                    }));
                }
            }
            return;
        }

        // Handle reordering within canvas (when autoTile is enabled)
        if (autoTile && activeId !== overId) {
            setCanvasItems((items) => {
                const oldIndex = items.findIndex((item) => item.id === activeId);
                const newIndex = items.findIndex((item) => item.id === overId);

                if (oldIndex === -1 || newIndex === -1) return items;

                return arrayMove(items, oldIndex, newIndex);
            });
        }
    };

    return (
        <Layout>
            <div className="flex h-screen bg-background">
                {/* Left Sidebar - Components */}
                <div className="w-80 border-r bg-card p-4">
                    <Tabs defaultValue="components" className="h-full">
                        <TabsList className="grid w-full grid-cols-3">
                            <TabsTrigger value="components">Components</TabsTrigger>
                            <TabsTrigger value="templates">Templates</TabsTrigger>
                            <TabsTrigger value="settings">Settings</TabsTrigger>
                        </TabsList>

                        <TabsContent value="components" className="h-full">
                            <ScrollArea className="h-[calc(100%-60px)]">
                                <div className="space-y-4">
                                    {/* Factories */}
                                    <div>
                                        <h3 className="font-semibold mb-2">🏭 Factories</h3>
                                        {loading ? (
                                            <div>Loading factories...</div>
                                        ) : factories.length > 0 ? (
                                            <div className="space-y-2">
                                                {factories.map((factory) => (
                                                    <DraggableSidebarItem
                                                        key={factory.id}
                                                        id={`sidebar-factory-${factory.id}`}
                                                        onClick={() => addItemToCanvas('factory', factory)}
                                                    >
                                                        <Card className="cursor-pointer hover:bg-accent">
                                                            <CardContent className="p-3">
                                                                <div className="font-medium text-sm">{factory.name || factory.factory_id}</div>
                                                                <div className="text-xs text-muted-foreground">Factory</div>
                                                            </CardContent>
                                                        </Card>
                                                    </DraggableSidebarItem>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="text-sm text-muted-foreground">No factories available</div>
                                        )}
                                    </div>

                                    {/* Devices */}
                                    <div>
                                        <h3 className="font-semibold mb-2">⚙️ Devices</h3>
                                        {loading ? (
                                            <div>Loading devices...</div>
                                        ) : devices.length > 0 ? (
                                            <div className="space-y-2">
                                                {devices.map((device) => (
                                                    <DraggableSidebarItem
                                                        key={device.id}
                                                        id={`sidebar-device-${device.id}`}
                                                        onClick={() => addItemToCanvas('device', device)}
                                                    >
                                                        <Card className="cursor-pointer hover:bg-accent">
                                                            <CardContent className="p-3">
                                                                <div className="font-medium text-sm">{device.name}</div>
                                                                <div className="text-xs text-muted-foreground">{device.type}</div>
                                                            </CardContent>
                                                        </Card>
                                                    </DraggableSidebarItem>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="text-sm text-muted-foreground">No devices available</div>
                                        )}
                                    </div>

                                    {/* Signals */}
                                    <div>
                                        <h3 className="font-semibold mb-2">📊 Signals</h3>
                                        {loading ? (
                                            <div>Loading signals...</div>
                                        ) : signals.length > 0 ? (
                                            <div className="space-y-2">
                                                {signals.map((signal) => (
                                                    <DraggableSidebarItem
                                                        key={signal.id}
                                                        id={`sidebar-signal-${signal.id}`}
                                                        onClick={() => addItemToCanvas('signal', signal)}
                                                    >
                                                        <Card className="cursor-pointer hover:bg-accent">
                                                            <CardContent className="p-3">
                                                                <div className="font-medium text-sm">{signal.name}</div>
                                                                <div className="text-xs text-muted-foreground">{signal.unit} ({signal.value})</div>
                                                            </CardContent>
                                                        </Card>
                                                    </DraggableSidebarItem>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="text-sm text-muted-foreground">No signals available</div>
                                        )}
                                    </div>

                                    {/* Widget Components */}
                                    <div>
                                        <h3 className="font-semibold mb-2">🎛️ Widgets</h3>
                                        <div className="space-y-2">
                                            <DraggableSidebarItem
                                                id="sidebar-chart"
                                                onClick={() => addItemToCanvas('chart', { label: 'Chart' })}
                                            >
                                                <Card className="cursor-pointer hover:bg-accent">
                                                    <CardContent className="p-3">
                                                        <div className="font-medium text-sm">📈 Chart</div>
                                                        <div className="text-xs text-muted-foreground">Data visualization</div>
                                                    </CardContent>
                                                </Card>
                                            </DraggableSidebarItem>
                                            <DraggableSidebarItem
                                                id="sidebar-gauge"
                                                onClick={() => addItemToCanvas('gauge', { label: 'Gauge' })}
                                            >
                                                <Card className="cursor-pointer hover:bg-accent">
                                                    <CardContent className="p-3">
                                                        <div className="font-medium text-sm">⭕ Gauge</div>
                                                        <div className="text-xs text-muted-foreground">Circular indicator</div>
                                                    </CardContent>
                                                </Card>
                                            </DraggableSidebarItem>
                                            <DraggableSidebarItem
                                                id="sidebar-button"
                                                onClick={() => addItemToCanvas('button', { label: 'Button', value: 1 })}
                                            >
                                                <Card className="cursor-pointer hover:bg-accent">
                                                    <CardContent className="p-3">
                                                        <div className="font-medium text-sm">🔘 Button</div>
                                                        <div className="text-xs text-muted-foreground">PLC control</div>
                                                    </CardContent>
                                                </Card>
                                            </DraggableSidebarItem>
                                        </div>
                                    </div>
                                </div>
                            </ScrollArea>
                        </TabsContent>

                        <TabsContent value="templates" className="h-full">
                            <ScrollArea className="h-[calc(100%-60px)]">
                                <div className="space-y-4">
                                    {templates.map((template) => (
                                        <Card key={template.id} className="cursor-pointer hover:bg-accent"
                                            onClick={() => applyTemplate(template)}>
                                            <CardHeader>
                                                <CardTitle className="text-lg">{template.name}</CardTitle>
                                                <p className="text-sm text-muted-foreground">{template.description}</p>
                                            </CardHeader>
                                            <CardContent>
                                                <p className="text-sm">{template.items.length} components</p>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </ScrollArea>
                        </TabsContent>

                        <TabsContent value="settings" className="h-full">
                            <ScrollArea className="h-[calc(100%-60px)]">
                                <div className="space-y-4">
                                    <div>
                                        <Label htmlFor="grid-size">Grid Size</Label>
                                        <Slider
                                            id="grid-size"
                                            min={10}
                                            max={50}
                                            step={5}
                                            value={[gridSize]}
                                            onValueChange={(value) => setGridSize(value[0])}
                                            className="mt-2"
                                        />
                                        <div className="text-sm text-muted-foreground mt-1">{gridSize}px</div>
                                    </div>

                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <Switch
                                                id="auto-tile"
                                                checked={autoTile}
                                                onCheckedChange={setAutoTile}
                                            />
                                            <Label htmlFor="auto-tile">Auto Tile</Label>
                                        </div>
                                        {autoTile && (
                                            <Button
                                                onClick={() => {
                                                    // Trigger re-tiling by temporarily disabling and re-enabling autoTile
                                                    setAutoTile(false);
                                                    setTimeout(() => setAutoTile(true), 10);
                                                }}
                                                size="sm"
                                                variant="outline"
                                            >
                                                Re-tile
                                            </Button>
                                        )}
                                    </div>

                                    <Separator />

                                    <div>
                                        <Label htmlFor="dashboard-name">Dashboard Name</Label>
                                        <Input
                                            id="dashboard-name"
                                            value={dashboardName}
                                            onChange={(e) => setDashboardName(e.target.value)}
                                            placeholder="Enter dashboard name"
                                            className="mt-1"
                                        />
                                    </div>

                                    <div>
                                        <Label htmlFor="dashboard-desc">Description</Label>
                                        <Input
                                            id="dashboard-desc"
                                            value={dashboardDescription}
                                            onChange={(e) => setDashboardDescription(e.target.value)}
                                            placeholder="Enter description"
                                            className="mt-1"
                                        />
                                    </div>

                                    <Button onClick={saveDashboard} className="w-full">
                                        {currentDashboard ? 'Update Dashboard' : 'Save Dashboard'}
                                    </Button>

                                    <Separator />

                                    <div>
                                        <Label>Saved Dashboards</Label>
                                        <ScrollArea className="h-32 mt-2">
                                            <div className="space-y-2">
                                                {savedDashboards.map((dashboard) => (
                                                    <Card key={dashboard.id} className="cursor-pointer hover:bg-accent"
                                                        onClick={() => loadDashboard(dashboard)}>
                                                        <CardContent className="p-3">
                                                            <div className="font-medium text-sm">{dashboard.name}</div>
                                                            <div className="text-xs text-muted-foreground">{dashboard.description}</div>
                                                        </CardContent>
                                                    </Card>
                                                ))}
                                            </div>
                                        </ScrollArea>
                                    </div>
                                </div>
                            </ScrollArea>
                        </TabsContent>
                    </Tabs>
                </div>

                {/* Main Canvas */}
                <div className="flex-1 p-4">
                    <div className="flex justify-between items-center mb-4">
                        <h1 className="text-2xl font-bold">Dashboard Builder</h1>
                        <div className="flex gap-2">
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="outline">
                                        Export ▼
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                    <DropdownMenuItem onClick={() => exportDashboard('json')}>
                                        Export as JSON
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => exportDashboard('csv')}>
                                        Export as CSV
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => exportDashboard('png')}>
                                        Export as PNG
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                            <Button onClick={() => setCanvasItems([])}>Clear Canvas</Button>
                        </div>
                    </div>

                    <DndContext
                        sensors={sensorsList}
                        collisionDetection={closestCenter}
                        onDragStart={handleDragStart}
                        onDragEnd={handleDragEnd}
                    >
                        <DroppableCanvas>
                            {autoTile ? (
                                <SortableContext items={canvasItems.map(item => item.id)} strategy={rectSortingStrategy}>
                                    {canvasItems.map((item) => (
                                        <div
                                            key={item.id}
                                            style={{
                                                position: 'absolute',
                                                left: item.x,
                                                top: item.y,
                                                width: item.width,
                                                height: item.height,
                                            }}
                                        >
                                            <CanvasItem
                                                item={item}
                                                onRemove={removeItemFromCanvas}
                                                onSendSignal={sendSignalToPLC}
                                            />
                                        </div>
                                    ))}
                                </SortableContext>
                            ) : (
                                canvasItems.map((item) => (
                                    <div
                                        key={item.id}
                                        style={{
                                            position: 'absolute',
                                            left: item.x,
                                            top: item.y,
                                            width: item.width,
                                            height: item.height,
                                        }}
                                    >
                                        <CanvasItem
                                            item={item}
                                            onRemove={removeItemFromCanvas}
                                            onSendSignal={sendSignalToPLC}
                                        />
                                    </div>
                                ))
                            )}
                        </DroppableCanvas>

                        <DragOverlay>
                            {activeId ? (
                                <div className="opacity-50">
                                    <CanvasItem
                                        item={canvasItems.find(item => item.id === activeId)!}
                                        onRemove={() => { }}
                                    />
                                </div>
                            ) : null}
                        </DragOverlay>
                    </DndContext>
                </div>
            </div>
        </Layout>
    );
};

export default DashboardBuilder;