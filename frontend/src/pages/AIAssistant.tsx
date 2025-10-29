import { useState, useEffect, useRef } from 'react';
import { aiApiFunctions } from '../lib/api';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, User, Send, BarChart3, TrendingUp } from 'lucide-react';
import { AIChatResponse, ChartSuggestion } from '../types';
import AIChart from '../components/AIChart';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    chartSuggestions?: ChartSuggestion[];
}

function AIAssistant() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [embeddedCharts, setEmbeddedCharts] = useState<{ id: string; suggestion: ChartSuggestion }[]>([]);
    const scrollAreaRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        if (scrollAreaRef.current) {
            const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollContainer) {
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
            }
        }
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // Call AI service
            const response: AIChatResponse = await aiApiFunctions.chat(input, 'VirtPLC system assistance');

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.response,
                timestamp: new Date(),
                chartSuggestions: response.chart_suggestions
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error: unknown) {
            console.error('AI chat error:', error);
            let errorContent = 'Sorry, I encountered an error. Please try again later.';

            const err = error as { isNetworkError?: boolean; code?: string; status?: number };
            if (err.isNetworkError || err.code === 'ERR_BAD_REQUEST' || err.status === 404) {
                errorContent = 'AI service is currently unavailable. Please ensure the AI service is running and try again.';
            }

            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: errorContent,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleChartGeneration = (suggestion: ChartSuggestion) => {
        const chartId = `chart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setEmbeddedCharts(prev => [...prev, { id: chartId, suggestion }]);
    };

    const handleChartClose = (chartId: string) => {
        setEmbeddedCharts(prev => prev.filter(chart => chart.id !== chartId));
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <Layout>
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold">AI Assistant</h1>
                    <p className="text-muted-foreground">Get insights and assistance about your VirtPLC system</p>
                </div>

                <Card className="h-[70vh] flex flex-col">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="h-5 w-5" />
                            AI Assistant Chat
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col p-0">
                        {/* Chat Messages */}
                        <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
                            {messages.length === 0 ? (
                                <div className="flex items-center justify-center h-full text-muted-foreground">
                                    Start a conversation with the AI assistant...
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {messages.map((message) => (
                                        <div
                                            key={message.id}
                                            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                                }`}
                                        >
                                            {message.role === 'assistant' && (
                                                <div className="flex-shrink-0">
                                                    <Bot className="h-8 w-8 text-primary" />
                                                </div>
                                            )}
                                            <div
                                                className={`max-w-[70%] rounded-lg p-3 ${message.role === 'user'
                                                    ? 'bg-primary text-primary-foreground'
                                                    : 'bg-muted'
                                                    }`}
                                            >
                                                <div className="flex items-center gap-2 mb-1">
                                                    {message.role === 'user' ? (
                                                        <User className="h-4 w-4" />
                                                    ) : (
                                                        <Bot className="h-4 w-4" />
                                                    )}
                                                    <span className="text-sm font-medium">
                                                        {message.role === 'user' ? 'You' : 'AI Assistant'}
                                                    </span>
                                                </div>
                                                <div className="whitespace-pre-wrap">{message.content}</div>
                                                <div className="text-xs opacity-70 mt-2">
                                                    {message.timestamp.toLocaleTimeString()}
                                                </div>
                                                {message.chartSuggestions && message.chartSuggestions.length > 0 && (
                                                    <div className="mt-3 space-y-2">
                                                        <div className="text-sm font-medium text-primary">Suggested Charts:</div>
                                                        {message.chartSuggestions.map((suggestion, index) => (
                                                            <Button
                                                                key={index}
                                                                variant="outline"
                                                                size="sm"
                                                                onClick={() => handleChartGeneration(suggestion)}
                                                                className="w-full justify-start text-left h-auto p-3"
                                                            >
                                                                <BarChart3 className="h-4 w-4 mr-2 flex-shrink-0" />
                                                                <div>
                                                                    <div className="font-medium">{suggestion.title}</div>
                                                                    <div className="text-xs opacity-70">{suggestion.description}</div>
                                                                </div>
                                                            </Button>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                            {message.role === 'user' && (
                                                <div className="flex-shrink-0">
                                                    <User className="h-8 w-8 text-primary" />
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                    {isLoading && (
                                        <div className="flex gap-3 justify-start">
                                            <div className="flex-shrink-0">
                                                <Bot className="h-8 w-8 text-primary" />
                                            </div>
                                            <div className="bg-muted rounded-lg p-3 max-w-[70%]">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Bot className="h-4 w-4" />
                                                    <span className="text-sm font-medium">AI Assistant</span>
                                                </div>
                                                <div>Thinking...</div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </ScrollArea>

                        {/* Embedded Charts */}
                        {embeddedCharts.length > 0 && (
                            <div className="space-y-4 p-4 border-t">
                                <h3 className="text-sm font-medium text-primary">Generated Charts</h3>
                                {embeddedCharts.map((chart) => (
                                    <AIChart
                                        key={chart.id}
                                        suggestion={chart.suggestion}
                                        onClose={() => handleChartClose(chart.id)}
                                    />
                                ))}
                            </div>
                        )}

                        {/* Input Area */}
                        <div className="border-t p-4">
                            <div className="flex gap-2">
                                <Textarea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ask me anything about your VirtPLC system..."
                                    className="min-h-[60px] resize-none"
                                    disabled={isLoading}
                                />
                                <Button
                                    onClick={sendMessage}
                                    disabled={isLoading || !input.trim()}
                                    size="icon"
                                    className="self-end"
                                >
                                    <Send className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </Layout>
    );
}

export default AIAssistant;