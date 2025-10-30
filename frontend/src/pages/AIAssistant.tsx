import { useState, useEffect, useRef, useCallback } from 'react';
import { aiApiFunctions } from '../lib/api';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, User, Send, BarChart3, TrendingUp, Plus, Trash } from 'lucide-react';
import { AIChatResponse, ChartSuggestion } from '../types';
import AIChart from '../components/AIChart';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    chartSuggestions?: ChartSuggestion[];
}

interface Conversation {
    id: string;
    title: string;
    messages: Message[];
    embeddedCharts: { id: string; suggestion: ChartSuggestion }[];
    updatedAt: string; // ISO
}

function AIAssistant() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
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

    // Persistence keys
    const STORAGE_KEY = 'aiAssistant.conversations';
    const CURRENT_KEY = 'aiAssistant.currentConversationId';

    // Raw types for parsing storage safely
    type RawMessage = { id: string; role: 'user' | 'assistant'; content: string; timestamp: string; chartSuggestions?: ChartSuggestion[] };
    type RawConversation = { id: string; title: string; messages?: RawMessage[]; embeddedCharts?: { id: string; suggestion: ChartSuggestion }[]; updatedAt: string };

    // Load conversations from localStorage on mount
    useEffect(() => {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            const curr = localStorage.getItem(CURRENT_KEY);
            if (raw) {
                const parsedRaw = JSON.parse(raw) as RawConversation[] | unknown;
                const parsed: Conversation[] = Array.isArray(parsedRaw)
                    ? parsedRaw.map((c) => ({
                        id: c.id,
                        title: c.title,
                        messages: (c.messages || []).map(m => ({ id: m.id, role: m.role, content: m.content, chartSuggestions: m.chartSuggestions, timestamp: new Date(m.timestamp) })),
                        embeddedCharts: c.embeddedCharts || [],
                        updatedAt: c.updatedAt,
                    }))
                    : [];

                setConversations(parsed);
                if (curr && parsed.find(p => p.id === curr)) {
                    setCurrentConversationId(curr);
                    const conv = parsed.find(p => p.id === curr)!;
                    setMessages(conv.messages || []);
                    setEmbeddedCharts(conv.embeddedCharts || []);
                    return;
                }
                // if no current selected, pick last updated
                if (parsed.length > 0) {
                    const sorted = parsed.slice().sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
                    setCurrentConversationId(sorted[0].id);
                    setMessages(sorted[0].messages || []);
                    setEmbeddedCharts(sorted[0].embeddedCharts || []);
                }
            }
        } catch (e) {
            console.error('Failed to load conversations', e);
        }
    }, []);

    // Save current conversation list and current id whenever they change
    const persistConversations = useCallback((nextConversations: Conversation[], nextCurrentId: string | null) => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(nextConversations));
            if (nextCurrentId) localStorage.setItem(CURRENT_KEY, nextCurrentId);
            else localStorage.removeItem(CURRENT_KEY);
        } catch (e) {
            console.error('Failed to persist conversations', e);
        }
    }, []);

    // keep the conversations in sync when messages or embeddedCharts change
    useEffect(() => {
        if (!currentConversationId) return;
        const updated = conversations.map(c => {
            if (c.id !== currentConversationId) return c;
            return {
                ...c,
                messages,
                embeddedCharts,
                updatedAt: new Date().toISOString(),
            };
        });
        setConversations(updated);
        persistConversations(updated, currentConversationId);
    }, [messages, embeddedCharts, currentConversationId, conversations, persistConversations]);

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

    // Conversation management helpers
    const createNewConversation = () => {
        const id = `conv-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
        const conv: Conversation = {
            id,
            title: `Conversation ${conversations.length + 1}`,
            messages: [],
            embeddedCharts: [],
            updatedAt: new Date().toISOString(),
        };
        const next = [conv, ...conversations];
        setConversations(next);
        setCurrentConversationId(id);
        setMessages([]);
        setEmbeddedCharts([]);
        persistConversations(next, id);
    };

    const switchConversation = (id: string) => {
        const conv = conversations.find(c => c.id === id);
        if (!conv) return;
        setCurrentConversationId(id);
        setMessages(conv.messages || []);
        setEmbeddedCharts(conv.embeddedCharts || []);
        persistConversations(conversations, id);
    };

    const deleteConversation = (id: string) => {
        const next = conversations.filter(c => c.id !== id);
        setConversations(next);
        if (currentConversationId === id) {
            if (next.length > 0) {
                switchConversation(next[0].id);
            } else {
                setCurrentConversationId(null);
                setMessages([]);
                setEmbeddedCharts([]);
                persistConversations(next, null);
            }
        } else {
            persistConversations(next, currentConversationId);
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
                        <div className="flex items-center justify-between w-full">
                            <div className="flex items-center gap-2">
                                <Bot className="h-5 w-5" />
                                <CardTitle>AI Assistant Chat</CardTitle>
                            </div>
                            <div className="flex items-center gap-2">
                                <select
                                    value={currentConversationId ?? ''}
                                    onChange={(e) => switchConversation(e.target.value)}
                                    className="rounded border px-2 py-1 bg-white"
                                >
                                    {conversations.length === 0 && <option value="">(no conversations)</option>}
                                    {conversations.map((c) => (
                                        <option key={c.id} value={c.id}>{c.title}</option>
                                    ))}
                                </select>
                                <Button onClick={createNewConversation} size="sm" variant="outline">
                                    <Plus className="h-4 w-4 mr-2" /> New
                                </Button>
                                {currentConversationId && (
                                    <Button onClick={() => deleteConversation(currentConversationId)} size="sm" variant="destructive">
                                        <Trash className="h-4 w-4" />
                                    </Button>
                                )}
                            </div>
                        </div>
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