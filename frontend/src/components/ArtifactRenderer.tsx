import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import AIChart from './AIChart';
import { ChartSuggestion } from '../types';

interface ArtifactRendererProps {
    content: string;
    title: string;
    onSave?: (config: any) => void;
}

interface DashboardConfig {
    charts: Array<{
        type: string;
        title: string;
        data_source: string;
        query?: string;
        x_axis?: string;
        y_axis?: string;
        metrics?: string[];
        symbols?: string[];
        data?: any[];
    }>;
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
                {config.charts.map((chart, index) => {
                    // Convert artifact chart config to ChartSuggestion format expected by AIChart
                    const suggestion: ChartSuggestion = {
                        type: chart.type as any,
                        title: chart.title,
                        description: '',
                        data_source: chart.data_source,
                        symbols: chart.symbols || [],
                        metrics: chart.metrics || [],
                        priority: 'high',
                        data: chart.data
                    };

                    return (
                        <Card key={index} className="w-full">
                            <CardHeader>
                                <CardTitle className="text-sm">{chart.title}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <AIChart suggestion={suggestion} onClose={() => { }} />
                                {chart.query && (
                                    <div className="mt-2 text-xs text-gray-500 font-mono bg-gray-100 p-2 rounded overflow-x-auto">
                                        {chart.query}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
};

export default ArtifactRenderer;
