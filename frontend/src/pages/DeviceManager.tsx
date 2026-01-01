import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { useDroppable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { Save, Database, Factory, AlertTriangle, Plus, Edit, Trash2, MoreHorizontal } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface Device {
    id: string;
    name: string;
    type: string;
    factoryId?: string;
    signals: Signal[];
}

interface Signal {
    id: string;
    name: string;
    type: string;
    unit?: string;
    deviceId: string;
}

interface Factory {
    id: string;
    factoryId: string;
    name: string;
    description?: string;
    devices: Device[];
    createdAt?: string;
}

interface DeviceManagerProps {
    id: string;
    device: Device;
    factoryId?: string;
}

const SortableDevice = ({ id, device, factoryId }: DeviceManagerProps) => {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...attributes}
            {...listeners}
            className="p-3 bg-card border rounded-lg cursor-move hover:shadow-md transition-shadow"
        >
            <div className="flex items-center justify-between">
                <div>
                    <div className="font-medium">{device.name}</div>
                    <div className="text-sm text-muted-foreground">{device.type}</div>
                </div>
                <Badge variant="outline">{device.signals?.length || 0} signals</Badge>
            </div>
        </div>
    );
};

const DroppableFactory = ({ factory, onEdit, onDelete }: { factory: Factory; onEdit: (factory: Factory) => void; onDelete: (factory: Factory) => void }) => {
    const { setNodeRef } = useDroppable({
        id: factory.id,
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Factory className="h-5 w-5" />
                    {factory.name}
                </CardTitle>
                {factory.description && (
                    <p className="text-sm text-muted-foreground mt-1">{factory.description}</p>
                )}
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Devices:</span>
                        <Badge variant="secondary">{factory.devices?.length || 0}</Badge>
                    </div>
                    <SortableContext
                        items={factory.devices?.map(d => d.id) || []}
                        strategy={verticalListSortingStrategy}
                    >
                        <div
                            ref={setNodeRef}
                            className="space-y-2 min-h-[100px] border-2 border-dashed border-muted-foreground/25 rounded-lg p-4"
                        >
                            {factory.devices && factory.devices.length > 0 ? (
                                factory.devices.map((device) => (
                                    <SortableDevice
                                        key={device.id}
                                        id={device.id}
                                        device={device}
                                        factoryId={factory.id}
                                    />
                                ))
                            ) : (
                                <div className="text-center text-muted-foreground py-4">
                                    <Factory className="mx-auto h-6 w-6 mb-2" />
                                    <p className="text-sm">Drop devices here</p>
                                </div>
                            )}
                        </div>
                    </SortableContext>
                </div>
            </CardContent>
        </Card>
    );
};

export default function DeviceManager() {
    const { user } = useAuth();
    const { toast } = useToast();
    const [factories, setFactories] = useState<Factory[]>([]);
    const [orphanDevices, setOrphanDevices] = useState<Device[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [editingFactory, setEditingFactory] = useState<Factory | null>(null);
    const [newFactoryName, setNewFactoryName] = useState('');
    const [newFactoryDescription, setNewFactoryDescription] = useState('');
    const [editFactoryName, setEditFactoryName] = useState('');
    const [editFactoryDescription, setEditFactoryDescription] = useState('');
    const [creating, setCreating] = useState(false);
    const [updating, setUpdating] = useState(false);
    const [activeTab, setActiveTab] = useState('assignments');

    const navigate = useNavigate();

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [factoriesResponse, devicesResponse] = await Promise.all([
                api.get('/api/admin/factories'),
                api.get('/api/admin/devices'),
            ]);

            setFactories(factoriesResponse.data);
            // Filter orphan devices and deduplicate by id
            const allDevices = devicesResponse.data;
            const uniqueDevices = Array.from(new Map(allDevices.map(d => [d.id, d])).values());
            setOrphanDevices(uniqueDevices.filter((d: Device) => !d.factoryId));
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to load data',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;

        if (!over) return;

        const activeId = active.id as string;
        const overId = over.id as string;

        // Find the device being dragged
        const device = [...factories.flatMap(f => f.devices), ...orphanDevices].find(d => d.id === activeId);
        if (!device) return;

        // If dropping on a factory
        const targetFactory = factories.find(f => f.id === overId);
        if (targetFactory) {
            // Move device to factory
            setFactories(prev => prev.map(f => {
                if (f.id === targetFactory.id) {
                    return { ...f, devices: [...f.devices, { ...device, factoryId: f.id }] };
                }
                return { ...f, devices: f.devices.filter(d => d.id !== activeId) };
            }));
            setOrphanDevices(prev => prev.filter(d => d.id !== activeId));
        } else {
            // Move to unassigned
            setFactories(prev => prev.map(f => ({ ...f, devices: f.devices.filter(d => d.id !== activeId) })));
            setOrphanDevices(prev => [...prev, { ...device, factoryId: undefined }]);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            const assignments = factories.flatMap(factory =>
                factory.devices.map(device => ({
                    deviceId: device.id,
                    factoryId: factory.id,
                    signalIds: device.signals?.map(signal => signal.id) || [],
                }))
            );

            await api.post('/api/admin/device-assignments', { assignments });
            toast({
                title: 'Success',
                description: 'Device assignments saved successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to save device assignments',
                variant: 'destructive',
            });
        } finally {
            setSaving(false);
        }
    };

    const handleCreateFactory = async () => {
        if (!newFactoryName.trim()) {
            toast({
                title: 'Error',
                description: 'Factory name is required',
                variant: 'destructive',
            });
            return;
        }

        try {
            setCreating(true);
            const response = await api.post('/api/admin/factories', {
                name: newFactoryName.trim(),
                description: newFactoryDescription.trim(),
            });

            setFactories(prev => [...prev, response.data]);
            setCreateDialogOpen(false);
            setNewFactoryName('');
            setNewFactoryDescription('');

            toast({
                title: 'Success',
                description: 'Factory created successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to create factory',
                variant: 'destructive',
            });
        } finally {
            setCreating(false);
        }
    };

    const handleEditFactory = (factory: Factory) => {
        setEditingFactory(factory);
        setEditFactoryName(factory.name);
        setEditFactoryDescription(factory.description || '');
        setEditDialogOpen(true);
    };

    const handleUpdateFactory = async () => {
        if (!editingFactory || !editFactoryName.trim()) {
            toast({
                title: 'Error',
                description: 'Factory name is required',
                variant: 'destructive',
            });
            return;
        }

        try {
            setUpdating(true);
            const response = await api.put(`/api/admin/factories/${editingFactory.id}`, {
                name: editFactoryName.trim(),
                description: editFactoryDescription.trim(),
            });

            setFactories(prev => prev.map(f =>
                f.id === editingFactory.id ? { ...f, ...response.data } : f
            ));
            setEditDialogOpen(false);
            setEditingFactory(null);

            toast({
                title: 'Success',
                description: 'Factory updated successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to update factory',
                variant: 'destructive',
            });
        } finally {
            setUpdating(false);
        }
    };

    const handleDeleteFactory = async (factory: Factory) => {
        if (factory.devices.length > 0) {
            toast({
                title: 'Error',
                description: 'Cannot delete factory with assigned devices. Please unassign all devices first.',
                variant: 'destructive',
            });
            return;
        }

        if (!confirm(`Are you sure you want to delete "${factory.name}"? This action cannot be undone.`)) {
            return;
        }

        try {
            await api.delete(`/api/admin/factories/${factory.id}`);
            setFactories(prev => prev.filter(f => f.id !== factory.id));

            toast({
                title: 'Success',
                description: 'Factory deleted successfully',
            });
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to delete factory',
                variant: 'destructive',
            });
        }
    };

    if (user?.role !== 'ADMIN') {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="p-6">
                        <div className="text-center">
                            <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
                            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
                            <p className="text-muted-foreground">
                                You need administrator privileges to access this page.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="p-6">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            </div>
        );
    }

    return (
        <Layout>
            <div className="p-6 space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Device Manager</h1>
                        <p className="text-muted-foreground">
                            Manage factory assignments and device configurations
                        </p>
                    </div>
                </div>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="assignments">Device Assignments</TabsTrigger>
                    <TabsTrigger value="overview">Factory Overview</TabsTrigger>
                    <TabsTrigger value="management">Factory Management</TabsTrigger>
                </TabsList>

                <TabsContent value="assignments" className="space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-xl font-semibold">Device Assignments</h2>
                            <p className="text-sm text-muted-foreground">
                                Drag and drop devices between factories to manage assignments
                            </p>
                        </div>
                        <Button onClick={handleSave} disabled={saving}>
                            <Save className="mr-2 h-4 w-4" />
                            {saving ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </div>

                    <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                    >
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {factories.map((factory) => (
                                <DroppableFactory
                                    key={factory.id}
                                    factory={factory}
                                    onEdit={handleEditFactory}
                                    onDelete={handleDeleteFactory}
                                />
                            ))}

                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Database className="h-5 w-5" />
                                        Unassigned Devices
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <SortableContext
                                        items={orphanDevices.map(d => d.id)}
                                        strategy={verticalListSortingStrategy}
                                    >
                                        <div className="space-y-2">
                                            {orphanDevices.map((device) => (
                                                <SortableDevice
                                                    key={device.id}
                                                    id={device.id}
                                                    device={device}
                                                />
                                            ))}
                                            {orphanDevices.length === 0 && (
                                                <div className="text-center text-muted-foreground py-8">
                                                    <Database className="mx-auto h-8 w-8 mb-2" />
                                                    <p>No unassigned devices</p>
                                                </div>
                                            )}
                                        </div>
                                    </SortableContext>
                                </CardContent>
                            </Card>
                        </div>
                    </DndContext>
                </TabsContent>

                <TabsContent value="overview" className="space-y-6">
                    <div>
                        <h2 className="text-xl font-semibold">Factory Overview</h2>
                        <p className="text-sm text-muted-foreground">
                            View all factories and their assigned devices
                        </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {factories.map((factory) => (
                            <Card key={factory.id} className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate(`/monitoring?factoryId=${factory.factoryId}`)}>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Factory className="h-5 w-5" />
                                        {factory.name}
                                    </CardTitle>
                                    {factory.description && (
                                        <p className="text-sm text-muted-foreground">{factory.description}</p>
                                    )}
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Devices:</span>
                                            <Badge variant="secondary">{factory.devices?.length || 0}</Badge>
                                        </div>
                                        {factory.devices && factory.devices.length > 0 && (
                                            <div className="space-y-2">
                                                {factory.devices.slice(0, 5).map((device: any) => (
                                                    <div key={device.id} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                                                        <div>
                                                            <div className="font-medium text-sm">{device.name}</div>
                                                            <div className="text-xs text-muted-foreground">{device.type}</div>
                                                        </div>
                                                        <Badge variant="outline" className="text-xs">
                                                            {device.signals?.length || 0} signals
                                                        </Badge>
                                                    </div>
                                                ))}
                                                {factory.devices.length > 5 && (
                                                    <div className="text-xs text-muted-foreground text-center">
                                                        +{factory.devices.length - 5} more devices
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                        {factories.length === 0 && (
                            <div className="col-span-full text-center py-8">
                                <Factory className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                                <h3 className="text-lg font-medium mb-2">No Factories</h3>
                                <p className="text-muted-foreground">Create your first factory to get started.</p>
                            </div>
                        )}
                    </div>
                </TabsContent>

                <TabsContent value="management" className="space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-xl font-semibold">Factory Management</h2>
                            <p className="text-sm text-muted-foreground">
                                Create, edit, and delete factories
                            </p>
                        </div>
                        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                            <DialogTrigger asChild>
                                <Button>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Factory
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Create New Factory</DialogTitle>
                                    <DialogDescription>
                                        Add a new factory to organize your devices.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4">
                                    <div>
                                        <Label htmlFor="factory-name">Factory Name</Label>
                                        <Input
                                            id="factory-name"
                                            value={newFactoryName}
                                            onChange={(e) => setNewFactoryName(e.target.value)}
                                            placeholder="Enter factory name"
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="factory-description">Description (Optional)</Label>
                                        <Textarea
                                            id="factory-description"
                                            value={newFactoryDescription}
                                            onChange={(e) => setNewFactoryDescription(e.target.value)}
                                            placeholder="Enter factory description"
                                            rows={3}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                                        Cancel
                                    </Button>
                                    <Button onClick={handleCreateFactory} disabled={!newFactoryName.trim()}>
                                        Create Factory
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {factories.map((factory) => (
                            <Card key={factory.id}>
                                <CardHeader>
                                    <CardTitle className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <Factory className="h-5 w-5" />
                                            {factory.name}
                                        </div>
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" size="sm">
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onClick={() => handleEditFactory(factory)}>
                                                    <Edit className="mr-2 h-4 w-4" />
                                                    Edit
                                                </DropdownMenuItem>
                                                <DropdownMenuSeparator />
                                                <DropdownMenuItem
                                                    onClick={() => handleDeleteFactory(factory)}
                                                    className="text-destructive"
                                                >
                                                    <Trash2 className="mr-2 h-4 w-4" />
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </CardTitle>
                                    {factory.description && (
                                        <p className="text-sm text-muted-foreground">{factory.description}</p>
                                    )}
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Devices:</span>
                                            <Badge variant="secondary">{factory.devices?.length || 0}</Badge>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Created:</span>
                                            <span className="text-sm">
                                                {new Date(factory.createdAt).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                        {factories.length === 0 && (
                            <div className="col-span-full text-center py-8">
                                <Factory className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                                <h3 className="text-lg font-medium mb-2">No Factories</h3>
                                <p className="text-muted-foreground">Create your first factory to get started.</p>
                            </div>
                        )}
                    </div>

                    {/* Edit Factory Dialog */}
                    <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Edit Factory</DialogTitle>
                                <DialogDescription>
                                    Update factory information.
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="edit-factory-name">Factory Name</Label>
                                    <Input
                                        id="edit-factory-name"
                                        value={editFactoryName}
                                        onChange={(e) => setEditFactoryName(e.target.value)}
                                        placeholder="Enter factory name"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="edit-factory-description">Description (Optional)</Label>
                                    <Textarea
                                        id="edit-factory-description"
                                        value={editFactoryDescription}
                                        onChange={(e) => setEditFactoryDescription(e.target.value)}
                                        placeholder="Enter factory description"
                                        rows={3}
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
                                    Cancel
                                </Button>
                                <Button onClick={handleUpdateFactory} disabled={!editFactoryName.trim()}>
                                    Update Factory
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </TabsContent>
            </Tabs>
            </div>
        </Layout>
    );
};