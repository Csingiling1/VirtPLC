import React, { useState } from 'react';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Button } from './ui/button';
import { X, Code2, Eye, Copy, Download, BarChart3 } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as Babel from '@babel/standalone';

interface Artifact {
    type: string;
    title: string;
    content: string;
}

interface ArtifactPanelProps {
    artifact: Artifact | null;
    onClose: () => void;
}

// Component to execute React/TypeScript code
const LivePreview: React.FC<{ code: string }> = ({ code }) => {
    const [Component, setComponent] = useState<React.ComponentType | null>(null);
    const [error, setError] = useState<Error | null>(null);

    React.useEffect(() => {
        try {
            // Remove import statements
            let cleanCode = code.replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '');
            cleanCode = cleanCode.replace(/export\s+default\s+/g, '');

            // Transform JSX to JavaScript using Babel
            const transformed = Babel.transform(cleanCode, {
                presets: ['react'],
                filename: 'artifact.tsx'
            }).code || '';

            // Extract function name
            const functionMatch = cleanCode.match(/function\s+(\w+)/);
            const functionName = functionMatch ? functionMatch[1] : 'Component';

            // Create function scope with all dependencies
            const scope = {
                React,
                useState: React.useState,
                useEffect: React.useEffect,
                LineChart,
                Line,
                BarChart,
                Bar,
                AreaChart,
                Area,
                XAxis,
                YAxis,
                CartesianGrid,
                Tooltip,
                Legend,
                ResponsiveContainer
            };

            // Execute transformed code in scope
            const scopeKeys = Object.keys(scope);
            const scopeValues = Object.values(scope);

            const componentCode = `
                ${transformed}
                return ${functionName};
            `;

            const componentFunction = new Function(...scopeKeys, componentCode);
            const comp = componentFunction(...scopeValues);

            setComponent(() => comp);
            setError(null);
        } catch (err) {
            console.error('Preview error:', err);
            setError(err as Error);
            setComponent(null);
        }
    }, [code]);

    if (error) {
        return (
            <div className="p-8 bg-red-50 rounded-lg animate-in fade-in duration-300">
                <h3 className="text-lg font-semibold text-red-800 mb-2">Preview Error</h3>
                <p className="text-sm text-red-600 mb-4">{error.message}</p>
                <details className="text-xs">
                    <summary className="cursor-pointer text-red-700 font-medium hover:text-red-900">View Code</summary>
                    <pre className="mt-2 p-3 bg-red-100 rounded overflow-auto text-xs">{code}</pre>
                </details>
            </div>
        );
    }

    if (!Component) {
        return (
            <div className="p-8 flex items-center justify-center">
                <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
            </div>
        );
    }

    return <Component />;
};

const ArtifactPanel: React.FC<ArtifactPanelProps> = ({ artifact, onClose }) => {
    const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

    if (!artifact) return null;

    const copyCode = () => {
        navigator.clipboard.writeText(artifact.content);
    };

    const downloadCode = () => {
        const blob = new Blob([artifact.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${artifact.title.replace(/\s+/g, '_')}.tsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="h-full flex flex-col bg-white border-l animate-in slide-in-from-right duration-300">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-50 to-gray-50">
                <div className="flex items-center gap-2 animate-in fade-in slide-in-from-left duration-500">
                    <BarChart3 className="h-5 w-5 text-blue-600" />
                    <div>
                        <h2 className="font-semibold text-gray-900">{artifact.title}</h2>
                        <p className="text-xs text-gray-500">Live Artifact</p>
                    </div>
                </div>
                <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-gray-200 transition-colors">
                    <X className="h-4 w-4" />
                </Button>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'preview' | 'code')} className="flex-1 flex flex-col">
                <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
                    <TabsList className="animate-in fade-in duration-500 delay-100">
                        <TabsTrigger value="preview" className="gap-2 transition-all">
                            <Eye className="h-4 w-4" />
                            Preview
                        </TabsTrigger>
                        <TabsTrigger value="code" className="gap-2 transition-all">
                            <Code2 className="h-4 w-4" />
                            Code
                        </TabsTrigger>
                    </TabsList>
                    <div className="flex gap-2 animate-in fade-in duration-500 delay-200">
                        <Button variant="outline" size="sm" onClick={copyCode} className="hover:bg-gray-100 transition-colors">
                            <Copy className="h-4 w-4 mr-1" />
                            Copy
                        </Button>
                        <Button variant="outline" size="sm" onClick={downloadCode} className="hover:bg-gray-100 transition-colors">
                            <Download className="h-4 w-4 mr-1" />
                            Download
                        </Button>
                    </div>
                </div>


                <TabsContent value="preview" className="flex-1 overflow-auto m-0 p-6 animate-in fade-in zoom-in-95 duration-500">
                    {artifact.type === 'react' ? (
                        <LivePreview code={artifact.content} />
                    ) : (
                        <div className="p-4 bg-yellow-50 rounded animate-in fade-in duration-300">
                            <p className="text-yellow-800">Preview not available for type: {artifact.type}</p>
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="code" className="flex-1 overflow-auto m-0 animate-in fade-in duration-500">
                    <div className="relative h-full">
                        <pre className="p-6 bg-gray-900 text-gray-100 text-sm h-full overflow-auto font-mono">
                            <code>{artifact.content}</code>
                        </pre>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default ArtifactPanel;
