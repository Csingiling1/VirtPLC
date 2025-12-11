import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ArtifactRendererProps {
    content: string;
    title: string;
    onSave?: (config: any) => void;
}

interface ChartConfig {
    type: string;
    title: string;
    query: string;
    x_field?: string;
    y_field?: string;
    group_by?: string;
}

interface DashboardConfig {
    charts: ChartConfig[];
}

const ArtifactRenderer: React.FC<ArtifactRendererProps> = ({ content, title, onSave }) => {
    let config: DashboardConfig;
    try {
        config = JSON.parse(content);
    } catch (e) {
        return <div className="text-red-500">Error parsing artifact content</div>;
    }

    return (
        <div className="space-y-4 mt-4 border rounded-lg p-4 bg-slate-50 dark:bg-slate-900">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">{title}</h3>
                {onSave && (
                    <button
                        onClick={() => onSave(config)}
                        className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                    >
                        Save Dashboard
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {config.charts.map((chart, index) => (
                    <ExecutableChart key={index} config={chart} />
                ))}
            </div>
        </div>
    );
};

const ExecutableChart: React.FC<{ config: ChartConfig }> = ({ config }) => {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch('http://localhost:3001/api/chat/message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: `[TOOL: query {"sql": "${config.query.replace(/"/g, '\\"')}"}]`,
                        session_id: 1
                    })
                });

                if (!response.ok) throw new Error('Query failed');

                const result = await response.json();
                
                // Parse tool result from response
                const match = result.response.match(/\[TOOL_RESULT\]:\s*({.*})/s);
                if (match) {
                    const toolResult = JSON.parse(match[1]);
                    if (toolResult.results) {
                        setData(toolResult.results);
                    } else if (toolResult.error) {
                        setError(toolResult.error);
                    }
                } else {
                    setError('No data returned from query');
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };

        if (config.query) {
            fetchData();
        }
    }, [config.query]);

    if (loading) {
        return (
            <Card className="w-full">
                <CardHeader><CardTitle className="text-sm">{config.title}</CardTitle></CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="w-full">
                <CardHeader><CardTitle className="text-sm">{config.title}</CardTitle></CardHeader>
                <CardContent>
                    <div className="text-red-500 text-sm">{error}</div>
                    <div className="mt-2 text-xs text-gray-500 font-mono bg-gray-100 p-2 rounded">
                        {config.query}
                    </div>
                </CardContent>
            </Card>
        );
    }

    const Chart = config.type === 'bar' ? BarChart : config.type === 'area' ? AreaChart : LineChart;
    const Element = config.type === 'bar' ? Bar : config.type === 'area' ? Area : Line;

    // Group data if group_by is specified
    const groupedData = config.group_by && data.length > 0
        ? groupDataBy(data, config.group_by)
        : { ungrouped: data };

    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

    return (
        <Card className="w-full">
            <CardHeader><CardTitle className="text-sm">{config.title}</CardTitle></CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <Chart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey={config.x_field || 'timestamp'} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        {config.group_by ? (
                            Object.keys(groupedData).map((group, idx) => (
                                <Element
                                    key={group}
                                    dataKey={config.y_field || 'value'}
                                    data={groupedData[group]}
                                    name={group}
                                    stroke={colors[idx % colors.length]}
                                    fill={colors[idx % colors.length]}
                                />
                            ))
                        ) : (
                            <Element
                                dataKey={config.y_field || 'value'}
                                stroke="#3b82f6"
                                fill="#3b82f6"
                            />
                        )}
                    </Chart>
                </ResponsiveContainer>
                <div className="mt-2 text-xs text-gray-500 font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto max-h-20">
                    {config.query}
                </div>
                <div className="mt-1 text-xs text-gray-600">
                    {data.length} data points
                </div>
            </CardContent>
        </Card>
    );
};

function groupDataBy(data: any[], field: string): Record<string, any[]> {
    const grouped: Record<string, any[]> = {};
    data.forEach(item => {
        const key = item[field] || 'unknown';
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(item);
    });
    return grouped;
}

export default ArtifactRenderer;
