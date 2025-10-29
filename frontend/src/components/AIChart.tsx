import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X, Download, Maximize2 } from 'lucide-react';
import { ChartSuggestion } from '../types';
import { dataApi } from '../lib/api';

interface AIChartProps {
    suggestion: ChartSuggestion;
    onClose: () => void;
}

interface ChartDataPoint {
    timestamp: string;
    [key: string]: string | number;
}

const AIChart: React.FC<AIChartProps> = ({ suggestion, onClose }) => {
    const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadChartData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // Get time range (default to last 24 hours)
            const endTime = Date.now();
            const startTime = endTime - (24 * 60 * 60 * 1000); // 24 hours ago

            // Fetch data from backend
            const response = await dataApi.getRange(startTime, endTime);
            const rawData = response || [];

            // Transform data for the chart
            const transformedData: ChartDataPoint[] = rawData.map((item: unknown) => {
                const dataItem = item as Record<string, unknown>;
                return {
                    timestamp: new Date(dataItem.timestamp as number).toLocaleTimeString(),
                    ...Object.fromEntries(
                        Object.entries(dataItem).filter(([key]) =>
                            suggestion.symbols?.some((symbol: string) => key.includes(symbol)) ||
                            suggestion.metrics?.some((metric: string) => key.includes(metric)) ||
                            ['value', 'temperature', 'vibration', 'current', 'speed'].includes(key)
                        )
                    )
                };
            });

            setChartData(transformedData.slice(-50)); // Limit to last 50 points for performance
        } catch (err) {
            setError('Failed to load chart data');
            console.error('Chart data loading error:', err);
        } finally {
            setLoading(false);
        }
    }, [suggestion]);

    useEffect(() => {
        loadChartData();
    }, [loadChartData]);

    const renderChart = () => {
        if (suggestion.type === 'line_chart') {
            return (
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                            dataKey="timestamp"
                            fontSize={12}
                            tick={{ fontSize: 10 }}
                        />
                        <YAxis fontSize={12} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--background))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '6px'
                            }}
                        />
                        {suggestion.symbols?.map((symbol, index) => {
                            const dataKey = `${symbol.toLowerCase()}_value`;
                            return (
                                <Line
                                    key={symbol}
                                    type="monotone"
                                    dataKey={chartData.some(d => dataKey in d) ? dataKey : 'value'}
                                    stroke={`hsl(var(--chart-${(index % 5) + 1}))`}
                                    strokeWidth={2}
                                    dot={false}
                                    name={symbol}
                                />
                            );
                        })}
                    </LineChart>
                </ResponsiveContainer>
            );
        }

        return (
            <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                Chart type not supported yet
            </div>
        );
    };

    if (loading) {
        return (
            <Card className="w-full">
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">{suggestion.title}</CardTitle>
                        <Button variant="ghost" size="sm" onClick={onClose}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-[300px]">
                        <div className="text-muted-foreground">Loading chart data...</div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="w-full">
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">{suggestion.title}</CardTitle>
                        <Button variant="ghost" size="sm" onClick={onClose}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center h-[300px] text-red-500">
                        {error}
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="w-full">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{suggestion.title}</CardTitle>
                    <div className="flex gap-1">
                        <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                            <Maximize2 className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={onClose}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
                <p className="text-xs text-muted-foreground">{suggestion.description}</p>
            </CardHeader>
            <CardContent>
                {renderChart()}
            </CardContent>
        </Card>
    );
};

export default AIChart;