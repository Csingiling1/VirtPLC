import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Eye, Calendar, User, BarChart3 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

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

interface CanvasItem {
    id: string;
    type: 'chart' | 'gauge' | 'button' | 'factory' | 'device' | 'signal';
    x: number;
    y: number;
    width: number;
    height: number;
    gridX: number;
    gridY: number;
    data?: any;
}

const Dashboards = () => {
    const [dashboards, setDashboards] = useState<Dashboard[]>([]);
    const [selectedDashboard, setSelectedDashboard] = useState<Dashboard | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        loadDashboards();
    }, []);

    const loadDashboards = async () => {
        try {
            const response = await apiClient.get('/dashboards');
            // Ensure response is always an array
            const dashboardsData = Array.isArray(response) ? response :
                (response?.data && Array.isArray(response.data)) ? response.data : [];
            setDashboards(dashboardsData);
        } catch (error) {
            console.error('Failed to load dashboards:', error);
            toast({
                title: "Error",
                description: "Failed to load dashboards",
                variant: "destructive",
            });
            setDashboards([]);
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return 'Unknown';
        return new Date(dateString).toLocaleDateString();
    };

    const getItemTypeIcon = (type: string) => {
        switch (type) {
            case 'chart': return '📊';
            case 'gauge': return '⚡';
            case 'button': return '🔘';
            case 'factory': return '🏭';
            case 'device': return '🔧';
            case 'signal': return '📡';
            default: return '📦';
        }
    };

    const renderCanvasItem = (item: CanvasItem) => {
        const style = {
            position: 'absolute' as const,
            left: item.x,
            top: item.y,
            width: item.width,
            height: item.height,
            border: '1px solid #e2e8f0',
            borderRadius: '4px',
            backgroundColor: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            color: '#64748b',
        };

        return (
            <div key={item.id} style={style}>
                <div className="text-center">
                    <div className="text-lg mb-1">{getItemTypeIcon(item.type)}</div>
                    <div className="font-medium capitalize">{item.type}</div>
                    {item.data?.label && <div className="text-xs">{item.data.label}</div>}
                </div>
            </div>
        );
    };

    if (isLoading) {
        return (
            <Layout>
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl font-bold">Dashboards</h1>
                        <p className="text-muted-foreground">View and manage your custom monitoring dashboards</p>
                    </div>
                    <Button onClick={loadDashboards} variant="outline">
                        Refresh
                    </Button>
                </div>

                {dashboards.length === 0 ? (
                    <Card className="p-8 text-center">
                        <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                        <h3 className="text-lg font-semibold mb-2">No Dashboards Found</h3>
                        <p className="text-muted-foreground mb-4">
                            You haven't created any dashboards yet. Use the Dashboard Builder to create your first monitoring dashboard.
                        </p>
                        <Button asChild>
                            <a href="/dashboard-builder">Create Dashboard</a>
                        </Button>
                    </Card>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {dashboards.map((dashboard) => (
                            <Card key={dashboard.id} className="hover:shadow-lg transition-shadow">
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <CardTitle className="text-lg">{dashboard.name}</CardTitle>
                                            <CardDescription className="mt-1">
                                                {dashboard.description || 'No description'}
                                            </CardDescription>
                                        </div>
                                        <Badge variant={dashboard.autoTile ? "default" : "secondary"}>
                                            {dashboard.autoTile ? 'Auto-tile' : 'Floating'}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {/* Mini canvas preview */}
                                        <div
                                            className="relative bg-gray-50 border rounded-lg overflow-hidden"
                                            style={{ height: '120px' }}
                                        >
                                            <div className="absolute inset-0 p-2">
                                                {dashboard.items.slice(0, 4).map((item) => renderCanvasItem(item))}
                                                {dashboard.items.length > 4 && (
                                                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                                                        +{dashboard.items.length - 4} more
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex items-center justify-between text-sm text-muted-foreground">
                                            <div className="flex items-center gap-4">
                                                <div className="flex items-center gap-1">
                                                    <BarChart3 className="h-4 w-4" />
                                                    {dashboard.items.length} items
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <Calendar className="h-4 w-4" />
                                                    {formatDate(dashboard.createdAt)}
                                                </div>
                                            </div>
                                        </div>

                                        <Dialog>
                                            <DialogTrigger asChild>
                                                <Button
                                                    className="w-full"
                                                    onClick={() => setSelectedDashboard(dashboard)}
                                                >
                                                    <Eye className="h-4 w-4 mr-2" />
                                                    View Dashboard
                                                </Button>
                                            </DialogTrigger>
                                            <DialogContent className="max-w-6xl max-h-[90vh] overflow-auto">
                                                <DialogHeader>
                                                    <DialogTitle className="flex items-center gap-2">
                                                        <BarChart3 className="h-5 w-5" />
                                                        {dashboard.name}
                                                    </DialogTitle>
                                                </DialogHeader>
                                                <div className="mt-4">
                                                    <div className="relative bg-white border rounded-lg overflow-hidden">
                                                        <div
                                                            className="relative"
                                                            style={{
                                                                width: '100%',
                                                                height: '600px',
                                                                backgroundColor: '#f8fafc'
                                                            }}
                                                        >
                                                            {dashboard.items.map((item) => renderCanvasItem(item))}
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 text-sm text-muted-foreground">
                                                        <p><strong>Description:</strong> {dashboard.description || 'No description'}</p>
                                                        <p><strong>Items:</strong> {dashboard.items.length}</p>
                                                        <p><strong>Layout:</strong> {dashboard.autoTile ? 'Auto-tile' : 'Floating'}</p>
                                                        <p><strong>Created:</strong> {formatDate(dashboard.createdAt)}</p>
                                                    </div>
                                                </div>
                                            </DialogContent>
                                        </Dialog>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default Dashboards;