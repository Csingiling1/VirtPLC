import React, { useState, useEffect, useCallback, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { X, Download, Maximize2, Code, Settings, Play, Image } from 'lucide-react';
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
    const [showCustomization, setShowCustomization] = useState(false);
    const [showMaximize, setShowMaximize] = useState(false);
    const [showCodeEditor, setShowCodeEditor] = useState(false);
    const [editableCode, setEditableCode] = useState('');
    const chartRef = useRef<HTMLDivElement>(null);
    const [chartConfig, setChartConfig] = useState({
        showGrid: true,
        showTooltip: true,
        height: 300,
        colors: ['hsl(var(--chart-1))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))', 'hsl(var(--chart-4))', 'hsl(var(--chart-5))'],
        library: 'recharts' as 'recharts' | 'chartjs'
    });

    const generateReactCode = useCallback(() => {
        const componentName = suggestion.title.replace(/\s+/g, '').replace(/[^a-zA-Z0-9]/g, '');
        const dataKeys = chartData.length > 0 ? Object.keys(chartData[0]).filter(key => key !== 'timestamp') : ['value'];

        if (chartConfig.library === 'chartjs') {
            // Generate Chart.js code - support multiple chart types
            const dataTransformCode = dataKeys.map(key => `${key}: item.${key}`).join(',\n                    ');

            let chartImport = '';
            let chartComponent = '';
            let chartDataSetup = '';
            let chartOptions = '';

            if (suggestion.type === 'line_chart') {
                chartImport = 'import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from \'chart.js\';\nimport { Line } from \'react-chartjs-2\';\n\nChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);';
                chartComponent = 'Line';
                chartDataSetup = 'const data = {\n        labels: chartData.map(item => item.timestamp),\n        datasets: [\n            {\n                label: \'' + (dataKeys[0] || 'value') + '\',\n                data: chartData.map(item => item.' + (dataKeys[0] || 'value') + '),\n                backgroundColor: \'' + chartConfig.colors[0] + '\',\n                borderColor: \'' + chartConfig.colors[0] + '\',\n                borderWidth: 2\n            }\n        ]\n    };';
                chartOptions = 'const options = {\n        responsive: true,\n        maintainAspectRatio: false,\n        plugins: {\n            legend: { display: true },\n            tooltip: { enabled: showTooltip }\n        },\n        scales: {\n            x: { display: showGrid },\n            y: { display: showGrid }\n        }\n    };';
            } else if (suggestion.type === 'bar_chart') {
                chartImport = 'import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, BarElement, Title, Tooltip, Legend } from \'chart.js\';\nimport { Bar } from \'react-chartjs-2\';\n\nChartJS.register(CategoryScale, LinearScale, PointElement, BarElement, Title, Tooltip, Legend);';
                chartComponent = 'Bar';
                chartDataSetup = 'const data = {\n        labels: chartData.map(item => item.timestamp),\n        datasets: [\n            {\n                label: \'' + (dataKeys[0] || 'value') + '\',\n                data: chartData.map(item => item.' + (dataKeys[0] || 'value') + '),\n                backgroundColor: \'' + chartConfig.colors[0] + '\',\n                borderColor: \'' + chartConfig.colors[0] + '\',\n                borderWidth: 1\n            }\n        ]\n    };';
                chartOptions = 'const options = {\n        responsive: true,\n        maintainAspectRatio: false,\n        plugins: {\n            legend: { display: true },\n            tooltip: { enabled: showTooltip }\n        },\n        scales: {\n            x: { display: showGrid },\n            y: { display: showGrid }\n        }\n    };';
            } else if (suggestion.type === 'pie_chart') {
                chartImport = 'import { Chart as ChartJS, ArcElement, Tooltip, Legend } from \'chart.js\';\nimport { Pie } from \'react-chartjs-2\';\n\nChartJS.register(ArcElement, Tooltip, Legend);';
                chartComponent = 'Pie';
                chartDataSetup = 'const aggregatedData = chartData.reduce((acc, item) => {\n        const key = item.timestamp;\n        if (!acc[key]) acc[key] = 0;\n        acc[key] += item.' + (dataKeys[0] || 'value') + ' || 0;\n        return acc;\n    }, {});\n\n    const data = {\n        labels: Object.keys(aggregatedData),\n        datasets: [\n            {\n                data: Object.values(aggregatedData),\n                backgroundColor: [\'' + chartConfig.colors.join('\', \'') + '\'],\n                borderWidth: 1\n            }\n        ]\n    };';
                chartOptions = 'const options = {\n        responsive: true,\n        maintainAspectRatio: false,\n        plugins: {\n            legend: { display: true },\n            tooltip: { enabled: showTooltip }\n        }\n    };';
            } else {
                // Default to line chart
                chartImport = 'import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from \'chart.js\';\nimport { Line } from \'react-chartjs-2\';\n\nChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);';
                chartComponent = 'Line';
                chartDataSetup = 'const data = {\n        labels: chartData.map(item => item.timestamp),\n        datasets: [\n            {\n                label: \'' + (dataKeys[0] || 'value') + '\',\n                data: chartData.map(item => item.' + (dataKeys[0] || 'value') + '),\n                backgroundColor: \'' + chartConfig.colors[0] + '\',\n                borderColor: \'' + chartConfig.colors[0] + '\',\n                borderWidth: 2\n            }\n        ]\n    };';
                chartOptions = 'const options = {\n        responsive: true,\n        maintainAspectRatio: false,\n        plugins: {\n            legend: { display: true },\n            tooltip: { enabled: showTooltip }\n        },\n        scales: {\n            x: { display: showGrid },\n            y: { display: showGrid }\n        }\n    };';
            }

            const code = 'import React, { useState, useEffect } from \'react\';\n' +
                chartImport + '\n\n' +
                'interface ' + componentName + 'Props {\n' +
                '    startTime?: number;\n' +
                '    endTime?: number;\n' +
                '    height?: number;\n' +
                '    showGrid?: boolean;\n' +
                '    showTooltip?: boolean;\n' +
                '}\n\n' +
                'const ' + componentName + ': React.FC<' + componentName + 'Props> = ({ \n' +
                '    startTime = Date.now() - (24 * 60 * 60 * 1000), \n' +
                '    endTime = Date.now(),\n' +
                '    height = ' + chartConfig.height + ',\n' +
                '    showGrid = ' + chartConfig.showGrid + ',\n' +
                '    showTooltip = ' + chartConfig.showTooltip + '\n' +
                '}) => {\n' +
                '    const [chartData, setChartData] = useState([]);\n' +
                '    const [loading, setLoading] = useState(true);\n' +
                '    const [error, setError] = useState(null);\n\n' +
                '    useEffect(() => {\n' +
                '        const fetchData = async () => {\n' +
                '            try {\n' +
                '                setLoading(true);\n' +
                '                const response = await fetch(`/api/data/range?startTime=${startTime}&endTime=${endTime}`);\n' +
                '                const data = await response.json();\n' +
                '                \n' +
                '                const transformedData = data.map(item => ({\n' +
                '                    timestamp: new Date(item.timestamp).toLocaleTimeString(),\n' +
                '                    ' + dataTransformCode + '\n' +
                '                }));\n' +
                '                \n' +
                '                setChartData(transformedData);\n' +
                '            } catch (err) {\n' +
                '                setError(\'Failed to load data\');\n' +
                '            } finally {\n' +
                '                setLoading(false);\n' +
                '            }\n' +
                '        };\n\n' +
                '        fetchData();\n' +
                '    }, [startTime, endTime]);\n\n' +
                '    if (loading) return <div className="flex items-center justify-center" style={{ height: `${height}px` }}>Loading...</div>;\n' +
                '    if (error) return <div className="flex items-center justify-center text-red-500" style={{ height: `${height}px` }}>Error: {error}</div>;\n\n' +
                '    ' + chartDataSetup + '\n\n' +
                '    ' + chartOptions + '\n\n' +
                '    return (\n' +
                '        <div style={{ height: `${height}px` }}>\n' +
                '            <' + chartComponent + ' data={data} options={options} />\n' +
                '        </div>\n' +
                '    );\n' +
                '};\n\n' +
                'export default ' + componentName + ';';

            return code;
        }

        // Recharts code (existing)
        let chartCode = '';
        if (suggestion.type === 'line_chart') {
            chartCode = `
                <ResponsiveContainer width="100%" height={height}>
                    <LineChart data={chartData}>
                        {showGrid && <CartesianGrid strokeDasharray="3 3" />}
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        {showTooltip && <Tooltip />}
                        ${dataKeys.map((key, index) =>
                `<Line key="${key}" type="monotone" dataKey="${key}" stroke="${chartConfig.colors[index % chartConfig.colors.length]}" strokeWidth={2} />`
            ).join('\n                        ')}
                    </LineChart>
                </ResponsiveContainer>`;
        } else if (suggestion.type === 'bar_chart') {
            chartCode = `
                <ResponsiveContainer width="100%" height={height}>
                    <BarChart data={chartData}>
                        {showGrid && <CartesianGrid strokeDasharray="3 3" />}
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        {showTooltip && <Tooltip />}
                        ${dataKeys.map((key, index) =>
                `<Bar key="${key}" dataKey="${key}" fill="${chartConfig.colors[index % chartConfig.colors.length]}" />`
            ).join('\n                        ')}
                    </BarChart>
                </ResponsiveContainer>`;
        } else if (suggestion.type === 'pie_chart') {
            chartCode = `
                <ResponsiveContainer width="100%" height={height}>
                    <PieChart>
                        <Pie
                            data={aggregatedData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => \`\${name} \${((percent as number) * 100).toFixed(0)}%\`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {aggregatedData.map((entry, index) => (
                                <Cell key={\`cell-\${index}\`} fill={entry.fill} />
                            ))}
                        </Pie>
                        {showTooltip && <Tooltip />}
                    </PieChart>
                </ResponsiveContainer>`;
        } else {
            // Fallback: try to render based on available data
            if (chartData.length > 0 && Object.keys(chartData[0]).length > 1) {
                // Default to line chart if we have data
                chartCode = `
                    <ResponsiveContainer width="100%" height={height}>
                        <LineChart data={chartData}>
                            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
                            <XAxis dataKey="timestamp" fontSize={12} tick={{ fontSize: 10 }} />
                            <YAxis fontSize={12} />
                            {showTooltip && <Tooltip />}
                            ${Object.keys(chartData[0])
                        .filter(key => key !== 'timestamp')
                        .slice(0, 3) // Limit to 3 lines for readability
                        .map((key, index) => `<Line key="${key}" type="monotone" dataKey="${key}" stroke="${chartConfig.colors[index % chartConfig.colors.length]}" strokeWidth={2} name="${key}" />`)
                        .join('\n                            ')}
                        </LineChart>
                    </ResponsiveContainer>`;
            } else {
                chartCode = `// No data available for chart\nreturn <div className="flex items-center justify-center h-[400px] text-muted-foreground">No data available for chart</div>;`;
            }
        }

        const reactCode = `import React, { useState, useEffect } from 'react';
import { ${suggestion.type === 'line_chart' ? 'LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer' :
                suggestion.type === 'bar_chart' ? 'BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer' :
                    suggestion.type === 'pie_chart' ? 'PieChart, Pie, Cell, Tooltip, ResponsiveContainer' :
                        'ResponsiveContainer'} } from 'recharts';

interface ${componentName}Props {
    startTime?: number;
    endTime?: number;
    height?: number;
    showGrid?: boolean;
    showTooltip?: boolean;
}

const ${componentName}: React.FC<${componentName}Props> = ({ 
    startTime = Date.now() - (24 * 60 * 60 * 1000), 
    endTime = Date.now(),
    height = ${chartConfig.height},
    showGrid = ${chartConfig.showGrid},
    showTooltip = ${chartConfig.showTooltip}
}) => {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch(\`/api/data/range?startTime=\${startTime}&endTime=\${endTime}\`);
                const data = await response.json();
                
                const transformedData = data.map(item => ({
                    timestamp: new Date(item.timestamp).toLocaleTimeString(),
                    ${dataKeys.map(key => `${key}: item.${key}`).join(',\n                    ')}
                }));
                
                setChartData(transformedData);
            } catch (err) {
                setError('Failed to load data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [startTime, endTime]);

    if (loading) return <div className="flex items-center justify-center h-[\${height}px]">Loading...</div>;
    if (error) return <div className="flex items-center justify-center h-[\${height}px] text-red-500">Error: {error}</div>;

    return (
        <div className="w-full" style={{ height: \`\${height}px\` }}>
            ${chartCode}
        </div>
    );
};

export default ${componentName};
`;

        return reactCode;
    }, [suggestion, chartData, chartConfig]);

    const downloadCode = useCallback(() => {
        const code = generateReactCode();
        const componentName = suggestion.title.replace(/\s+/g, '').replace(/[^a-zA-Z0-9]/g, '');
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${componentName}.tsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, [generateReactCode, suggestion.title]);

    const downloadPNG = useCallback(async () => {
        if (!chartRef.current) return;

        try {
            // Dynamic import to avoid bundle size issues
            const html2canvas = (await import('html2canvas')).default;
            const canvas = await html2canvas(chartRef.current, {
                backgroundColor: 'white',
                scale: 2, // Higher resolution
                useCORS: true
            });

            const link = document.createElement('a');
            link.download = `${suggestion.title.replace(/\s+/g, '_')}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } catch (error) {
            console.error('Failed to download PNG:', error);
        }
    }, [suggestion.title]);

    const openCodeEditor = useCallback(() => {
        const code = generateReactCode();
        setEditableCode(code);
        setShowCodeEditor(true);
    }, [generateReactCode]);

    const runEditedCode = useCallback(() => {
        // Basic security: prevent dangerous operations
        const dangerousPatterns = [
            /eval\s*\(/g,
            /Function\s*\(/g,
            /setTimeout\s*\(/g,
            /setInterval\s*\(/g,
            /fetch\s*\(/g,
            /XMLHttpRequest/g,
            /import\s*\(/g,
            /require\s*\(/g,
            /process\./g,
            /window\./g,
            /document\./g,
            /localStorage/g,
            /sessionStorage/g,
            /console\./g,
            /alert\s*\(/g,
            /prompt\s*\(/g,
            /confirm\s*\(/g
        ];

        const hasDangerousCode = dangerousPatterns.some(pattern => pattern.test(editableCode));

        if (hasDangerousCode) {
            alert('Code contains potentially dangerous operations that are not allowed for security reasons.');
            return;
        }

        // For now, just show a preview message
        // In a real implementation, you might use react-live or a code sandbox
        alert('Code preview: This would render the edited chart component. Full implementation would require a secure code execution environment.');
    }, [editableCode]);

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
                    // Include all numeric values except timestamp
                    ...Object.fromEntries(
                        Object.entries(dataItem)
                            .filter(([key, value]) =>
                                key !== 'timestamp' &&
                                (typeof value === 'number' || (typeof value === 'string' && !isNaN(Number(value))))
                            )
                            .map(([key, value]) => [key, typeof value === 'string' ? Number(value) : value])
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
    }, []);

    useEffect(() => {
        loadChartData();
    }, [loadChartData]);

    const renderChart = () => {
        // Get data keys from chartData, excluding timestamp
        const dataKeys = chartData.length > 0 ? Object.keys(chartData[0]).filter(key => key !== 'timestamp') : [];

        console.log('Chart suggestion:', suggestion);
        console.log('Chart data keys:', dataKeys);
        console.log('Chart data sample:', chartData.slice(0, 2));

        if (suggestion.type === 'line_chart' || suggestion.type === 'line') {
            return (
                <ResponsiveContainer width="100%" height={chartConfig.height}>
                    <LineChart data={chartData}>
                        {chartConfig.showGrid && <CartesianGrid strokeDasharray="3 3" />}
                        <XAxis
                            dataKey="timestamp"
                            fontSize={12}
                            tick={{ fontSize: 10 }}
                        />
                        <YAxis fontSize={12} />
                        {chartConfig.showTooltip && <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--background))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '6px'
                            }}
                        />}
                        {dataKeys.map((key, index) => (
                            <Line
                                key={key}
                                type="monotone"
                                dataKey={key}
                                stroke={chartConfig.colors[index % chartConfig.colors.length]}
                                strokeWidth={2}
                                dot={false}
                                name={key}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            );
        }

        if (suggestion.type === 'bar_chart' || suggestion.type === 'bar') {
            return (
                <ResponsiveContainer width="100%" height={chartConfig.height}>
                    <BarChart data={chartData}>
                        {chartConfig.showGrid && <CartesianGrid strokeDasharray="3 3" />}
                        <XAxis
                            dataKey="timestamp"
                            fontSize={12}
                            tick={{ fontSize: 10 }}
                        />
                        <YAxis fontSize={12} />
                        {chartConfig.showTooltip && <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--background))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '6px'
                            }}
                        />}
                        {dataKeys.map((key, index) => (
                            <Bar
                                key={key}
                                dataKey={key}
                                fill={chartConfig.colors[index % chartConfig.colors.length]}
                                name={key}
                            />
                        ))}
                    </BarChart>
                </ResponsiveContainer>
            );
        }

        if (suggestion.type === 'pie_chart' || suggestion.type === 'pie') {
            // For pie chart, aggregate data by key
            const aggregatedData = dataKeys.map((key, index) => {
                const total = chartData.reduce((sum, item) => {
                    const value = item[key] || 0;
                    return sum + (typeof value === 'number' ? value : 0);
                }, 0);
                return {
                    name: key,
                    value: total,
                    fill: chartConfig.colors[index % chartConfig.colors.length]
                };
            });

            return (
                <ResponsiveContainer width="100%" height={chartConfig.height}>
                    <PieChart>
                        <Pie
                            data={aggregatedData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} ${((percent as number) * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {aggregatedData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                        </Pie>
                        {chartConfig.showTooltip && <Tooltip />}
                    </PieChart>
                </ResponsiveContainer>
            );
        }

        // Default fallback: try to render as line chart if we have data
        if (chartData.length > 0 && dataKeys.length > 0) {
            return (
                <ResponsiveContainer width="100%" height={chartConfig.height}>
                    <LineChart data={chartData}>
                        {chartConfig.showGrid && <CartesianGrid strokeDasharray="3 3" />}
                        <XAxis dataKey="timestamp" fontSize={12} tick={{ fontSize: 10 }} />
                        <YAxis fontSize={12} />
                        {chartConfig.showTooltip && <Tooltip />}
                        {dataKeys.slice(0, 3).map((key, index) => (
                            <Line
                                key={key}
                                type="monotone"
                                dataKey={key}
                                stroke={chartConfig.colors[index % chartConfig.colors.length]}
                                strokeWidth={2}
                                name={key}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            );
        }

        return (
            <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                Chart type not supported: {suggestion.type}
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
        <>
            <Card className="w-full">
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">{suggestion.title}</CardTitle>
                        <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => setShowCustomization(!showCustomization)} title="Customize Chart">
                                <Settings className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={downloadCode} title="Download React Code">
                                <Code className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={downloadPNG} title="Download as PNG">
                                <Image className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => setShowMaximize(true)} title="Maximize Chart">
                                <Maximize2 className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={openCodeEditor} title="Edit Code">
                                <Play className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={onClose}>
                                <X className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                    <p className="text-xs text-muted-foreground">{suggestion.description}</p>
                </CardHeader>
                <CardContent>
                    <div ref={chartRef}>
                        {renderChart()}
                    </div>
                    {showCustomization && (
                        <div className="mt-4 p-4 border-t space-y-4">
                            <h4 className="text-sm font-medium">Chart Customization</h4>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-medium">Height (px)</label>
                                    <input
                                        type="number"
                                        value={chartConfig.height}
                                        onChange={(e) => setChartConfig(prev => ({ ...prev, height: parseInt(e.target.value) || 300 }))}
                                        className="w-full px-2 py-1 text-sm border rounded"
                                        min="200"
                                        max="600"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-medium">Library</label>
                                    <select
                                        value={chartConfig.library}
                                        onChange={(e) => setChartConfig(prev => ({ ...prev, library: e.target.value as 'recharts' | 'chartjs' }))}
                                        className="w-full px-2 py-1 text-sm border rounded"
                                    >
                                        <option value="recharts">Recharts</option>
                                        <option value="chartjs">Chart.js</option>
                                    </select>
                                </div>
                                <div className="space-y-2 col-span-2">
                                    <label className="flex items-center space-x-2 text-xs">
                                        <input
                                            type="checkbox"
                                            checked={chartConfig.showGrid}
                                            onChange={(e) => setChartConfig(prev => ({ ...prev, showGrid: e.target.checked }))}
                                        />
                                        <span>Show Grid</span>
                                    </label>
                                    <label className="flex items-center space-x-2 text-xs">
                                        <input
                                            type="checkbox"
                                            checked={chartConfig.showTooltip}
                                            onChange={(e) => setChartConfig(prev => ({ ...prev, showTooltip: e.target.checked }))}
                                        />
                                        <span>Show Tooltip</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Maximize Modal */}
            <Dialog open={showMaximize} onOpenChange={setShowMaximize}>
                <DialogContent className="max-w-6xl max-h-[90vh] overflow-auto">
                    <DialogHeader>
                        <DialogTitle>{suggestion.title}</DialogTitle>
                    </DialogHeader>
                    <div className="w-full h-[70vh]" ref={chartRef}>
                        {renderChart()}
                    </div>
                </DialogContent>
            </Dialog>

            {/* Code Editor Modal */}
            <Dialog open={showCodeEditor} onOpenChange={setShowCodeEditor}>
                <DialogContent className="max-w-4xl max-h-[90vh]">
                    <DialogHeader>
                        <DialogTitle>Edit Chart Code</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                        <Textarea
                            value={editableCode}
                            onChange={(e) => setEditableCode(e.target.value)}
                            className="min-h-[400px] font-mono text-sm"
                            placeholder="Edit your React code here..."
                        />
                        <div className="flex gap-2">
                            <Button onClick={runEditedCode} className="flex items-center gap-2">
                                <Play className="h-4 w-4" />
                                Run Code
                            </Button>
                            <Button variant="outline" onClick={() => setEditableCode(generateReactCode())}>
                                Reset
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
};

export default AIChart;