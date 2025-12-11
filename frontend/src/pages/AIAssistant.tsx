import { useState, useEffect, useRef, useCallback } from 'react';
import { aiApiFunctions } from '../lib/api';
import Layout from '../components/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, User, Send, BarChart3, TrendingUp, Plus, Trash2, MessageSquare, Edit3, X, Clock, Terminal } from 'lucide-react';
import { AIChatResponse, ChartSuggestion } from '../types';
import AIChart from '../components/AIChart';
import ArtifactRenderer from '../components/ArtifactRenderer';

interface Artifact {
    type: string;
    title: string;
    content: string;
}

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    chartSuggestions?: ChartSuggestion[];
    isStreaming?: boolean;
    artifacts?: Artifact[];
    logs?: string[];
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
    const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
    const [editingContent, setEditingContent] = useState('');
    const [isTemporaryMode, setIsTemporaryMode] = useState(false);
    const scrollAreaRef = useRef<HTMLDivElement>(null);

    // Clear localStorage when entering temporary mode
    useEffect(() => {
        if (isTemporaryMode) {
            localStorage.removeItem(STORAGE_KEY);
            localStorage.removeItem(CURRENT_KEY);
        }
    }, [isTemporaryMode]);

    // Persistence keys
    const STORAGE_KEY = 'aiAssistant.conversations';
    const CURRENT_KEY = 'aiAssistant.currentConversationId';

    // Raw types for parsing storage safely
    type RawMessage = {
        id: string;
        role: 'user' | 'assistant';
        content: string;
        timestamp: string;
        chartSuggestions?: ChartSuggestion[];
        artifacts?: Artifact[];
        logs?: string[];
    };
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
                        messages: (c.messages || []).map(m => ({
                            id: m.id,
                            role: m.role,
                            content: m.content,
                            chartSuggestions: m.chartSuggestions,
                            timestamp: new Date(m.timestamp),
                            artifacts: m.artifacts,
                            logs: m.logs
                        })),
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
        if (isTemporaryMode) return; // Don't persist in temporary mode

        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(nextConversations));
            if (nextCurrentId) localStorage.setItem(CURRENT_KEY, nextCurrentId);
            else localStorage.removeItem(CURRENT_KEY);
        } catch (e) {
            console.error('Failed to persist conversations', e);
        }
    }, [isTemporaryMode]);

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
    }, [messages, embeddedCharts, currentConversationId, persistConversations]);

    const parseContent = (text: string) => {
        const artifactRegex = /<artifact\s+type="([^"]+)"\s+title="([^"]+)">([\s\S]*?)<\/artifact>/g;
        const toolRegex = /\[TOOL:.*?\]/g;

        const artifacts: Artifact[] = [];
        let cleanText = text;
        let match;

        while ((match = artifactRegex.exec(text)) !== null) {
            artifacts.push({
                type: match[1],
                title: match[2],
                content: match[3].trim()
            });
            cleanText = cleanText.replace(match[0], '');
        }

        const logs = text.match(toolRegex) || [];
        cleanText = cleanText.replace(toolRegex, '');

        return { cleanText, artifacts, logs };
    };

    const sendQuery = async (content: string, contextMessages: Message[]) => {
        setIsLoading(true);

        try {
            // Create placeholder assistant message
            const assistantMessageId = (Date.now() + 1).toString();
            const placeholderMessage: Message = {
                id: assistantMessageId,
                role: 'assistant',
                content: 'Thinking...',
                timestamp: new Date(),
                isStreaming: true
            };

            setMessages(prev => [...prev, placeholderMessage]);

            // Call AI service (non-streaming)
            const response = await fetch('http://localhost:3001/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: content,
                    session_id: currentConversationId ? parseInt(currentConversationId.split('-')[1] || '1') : 1,
                    context: { messages: contextMessages.map(m => ({ role: m.role, content: m.content })) }
                }),
            });

            if (!response.ok) {
                throw new Error(`Failed to get response: ${response.status}`);
            }

            const data: AIChatResponse = await response.json();

            const { cleanText, artifacts, logs } = parseContent(data.response || '');

            // Update message with actual response
            setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                    ? {
                        ...msg,
                        content: cleanText,
                        chartSuggestions: data.chart_suggestions,
                        artifacts: artifacts,
                        logs: logs as string[],
                        isStreaming: false
                    }
                    : msg
            ));

        } catch (error: unknown) {
            console.error('AI error:', error);

            // Remove the placeholder message and add error message
            setMessages(prev => prev.filter(msg => !msg.isStreaming));

            let errorContent = 'Sorry, I encountered an error. Please try again later.';
            const err = error as { message?: string };
            if (err.message?.includes('Failed to fetch') || err.message?.includes('Network')) {
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

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        const previousMessages = messages;  // Capture before adding user message

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Update conversation title if this is the first message
        if (messages.length === 0 && currentConversationId) {
            const title = input.length > 50 ? input.substring(0, 50) + '...' : input;
            setConversations(prev => prev.map(c =>
                c.id === currentConversationId ? { ...c, title } : c
            ));
        }

        await sendQuery(input, previousMessages);
    };    // Conversation management helpers
    const createNewConversation = () => {
        const id = `conv-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;
        const conv: Conversation = {
            id,
            title: 'New Chat',
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

    const startEditingMessage = (messageId: string, content: string) => {
        setEditingMessageId(messageId);
        setEditingContent(content);
    };

    const cancelEditingMessage = () => {
        setEditingMessageId(null);
        setEditingContent('');
    };

    const saveEditedMessage = () => {
        if (!editingMessageId || !editingContent.trim()) return;

        const content = editingContent.trim();
        const index = messages.findIndex(m => m.id === editingMessageId);
        const updatedMessages = messages.map(msg =>
            msg.id === editingMessageId
                ? { ...msg, content }
                : msg
        );
        const trimmed = updatedMessages.slice(0, index + 1);
        setMessages(trimmed);
        sendQuery(content, trimmed.slice(0, -1));

        setEditingMessageId(null);
        setEditingContent('');
    };

    const deleteMessage = (messageId: string) => {
        // Find the message to delete
        const messageToDelete = messages.find(msg => msg.id === messageId);
        if (!messageToDelete) return;

        // If it's a user message, also delete the following assistant message if it exists
        const messageIndex = messages.findIndex(msg => msg.id === messageId);
        let messagesToDelete = [messageId];

        if (messageToDelete.role === 'user' && messageIndex < messages.length - 1) {
            const nextMessage = messages[messageIndex + 1];
            if (nextMessage.role === 'assistant') {
                messagesToDelete.push(nextMessage.id);
            }
        }

        setMessages(prev => prev.filter(msg => !messagesToDelete.includes(msg.id)));
    };

    const toggleTemporaryMode = () => {
        setIsTemporaryMode(!isTemporaryMode);
        if (!isTemporaryMode) {
            // Switching to temporary mode - don't persist current conversation
            localStorage.removeItem(STORAGE_KEY);
            localStorage.removeItem(CURRENT_KEY);
        } else {
            // Switching back to persistent mode - save current state
            persistConversations(conversations, currentConversationId);
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
            <div className="flex h-screen bg-gray-50">
                {/* Sidebar */}
                <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
                    {/* Header */}
                    <div className="p-4 border-b border-gray-200 space-y-3">
                        <Button
                            onClick={createNewConversation}
                            className="w-full justify-start gap-2"
                            variant="outline"
                        >
                            <Plus className="h-4 w-4" />
                            New Chat
                        </Button>

                        <Button
                            onClick={toggleTemporaryMode}
                            className={`w-full justify-start gap-2 ${isTemporaryMode ? 'bg-orange-100 border-orange-300 text-orange-700' : ''}`}
                            variant="outline"
                        >
                            <Clock className="h-4 w-4" />
                            {isTemporaryMode ? 'Temporary Mode' : 'Persistent Mode'}
                        </Button>

                        {isTemporaryMode && (
                            <p className="text-xs text-orange-600 px-2">
                                Chats won't be saved when you leave
                            </p>
                        )}
                    </div>

                    {/* Conversations List */}
                    <ScrollArea className="flex-1">
                        <div className="p-2">
                            {conversations.length === 0 ? (
                                <div className="text-center text-gray-500 py-8">
                                    <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                    <p className="text-sm">No conversations yet</p>
                                    <p className="text-xs">Start a new chat to get help</p>
                                </div>
                            ) : (
                                <div className="space-y-1">
                                    {conversations.map((conversation) => (
                                        <div
                                            key={conversation.id}
                                            className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${currentConversationId === conversation.id
                                                ? 'bg-gray-100'
                                                : 'hover:bg-gray-50'
                                                }`}
                                            onClick={() => switchConversation(conversation.id)}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-gray-900 truncate">
                                                        {conversation.title}
                                                    </p>
                                                    <p className="text-xs text-gray-500">
                                                        {conversation.messages.length > 0
                                                            ? `${conversation.messages.length} messages`
                                                            : 'Empty conversation'
                                                        }
                                                    </p>
                                                </div>
                                                <Button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        deleteConversation(conversation.id);
                                                    }}
                                                    size="sm"
                                                    variant="ghost"
                                                    className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 hover:bg-red-100 hover:text-red-600"
                                                >
                                                    <Trash2 className="h-3 w-3" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </ScrollArea>
                </div>

                {/* Main Chat Area */}
                <div className="flex-1 flex flex-col">
                    {currentConversationId ? (
                        <>
                            {/* Chat Header */}
                            <div className="bg-white border-b border-gray-200 px-6 py-4">
                                <h1 className="text-xl font-semibold text-gray-900">
                                    {conversations.find(c => c.id === currentConversationId)?.title || 'AI Assistant'}
                                </h1>
                            </div>

                            {/* Messages */}
                            <ScrollArea ref={scrollAreaRef} className="flex-1 p-6">
                                {messages.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center h-full text-center">
                                        <Bot className="h-16 w-16 text-gray-400 mb-4" />
                                        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                                            How can I help you?
                                        </h2>
                                        <p className="text-gray-500 max-w-md">
                                            Ask me anything about your VirtPLC system. I can help with insights, troubleshooting, and data analysis.
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-6 max-w-4xl mx-auto">
                                        {messages.map((message) => (
                                            <div
                                                key={message.id}
                                                className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                            >
                                                {message.role === 'assistant' && (
                                                    <div className="flex-shrink-0">
                                                        <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                                                            <Bot className="h-4 w-4 text-white" />
                                                        </div>
                                                    </div>
                                                )}
                                                <div
                                                    className={`max-w-2xl rounded-lg px-4 py-3 ${message.role === 'user'
                                                        ? 'bg-blue-600 text-white'
                                                        : 'bg-white border border-gray-200 text-gray-900'
                                                        }`}
                                                >
                                                    {editingMessageId === message.id ? (
                                                        <div className="space-y-2">
                                                            <Textarea
                                                                value={editingContent}
                                                                onChange={(e) => setEditingContent(e.target.value)}
                                                                className="min-h-[80px] bg-white text-gray-900 border-gray-300"
                                                                placeholder="Edit your message..."
                                                            />
                                                            <div className="flex gap-2">
                                                                <Button
                                                                    onClick={saveEditedMessage}
                                                                    size="sm"
                                                                    className="bg-green-600 hover:bg-green-700"
                                                                >
                                                                    Save
                                                                </Button>
                                                                <Button
                                                                    onClick={cancelEditingMessage}
                                                                    size="sm"
                                                                    variant="outline"
                                                                    className="border-gray-300 text-gray-700 hover:bg-gray-50"
                                                                >
                                                                    Cancel
                                                                </Button>
                                                            </div>
                                                        </div>
                                                    ) : message.isStreaming ? (
                                                        <div className="space-y-2">
                                                            {message.logs && message.logs.length > 0 && (
                                                                <div className="mb-2 space-y-1">
                                                                    {message.logs.map((log, i) => (
                                                                        <div key={i} className="text-xs text-gray-400 font-mono flex items-center gap-1">
                                                                            <Terminal className="h-3 w-3" />
                                                                            {log.replace('[TOOL: ', '').replace(']', '')}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            )}
                                                            <div className="whitespace-pre-wrap">{message.content}</div>
                                                            {message.artifacts && message.artifacts.map((artifact, i) => (
                                                                <ArtifactRenderer
                                                                    key={i}
                                                                    content={artifact.content}
                                                                    title={artifact.title}
                                                                />
                                                            ))}
                                                            <div className="flex items-center space-x-1">
                                                                <div className="flex space-x-1">
                                                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                                                </div>
                                                                <span className="text-xs text-gray-500 ml-2">AI is thinking...</span>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <div className="space-y-2">
                                                            {message.logs && message.logs.length > 0 && (
                                                                <div className="mb-2 space-y-1">
                                                                    {message.logs.map((log, i) => (
                                                                        <div key={i} className="text-xs text-gray-400 font-mono flex items-center gap-1">
                                                                            <Terminal className="h-3 w-3" />
                                                                            {log.replace('[TOOL: ', '').replace(']', '')}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            )}
                                                            <div className="whitespace-pre-wrap">{message.content}</div>
                                                            {message.artifacts && message.artifacts.map((artifact, i) => (
                                                                <ArtifactRenderer
                                                                    key={i}
                                                                    content={artifact.content}
                                                                    title={artifact.title}
                                                                />
                                                            ))}
                                                        </div>
                                                    )}
                                                    <div className={`flex items-center justify-between mt-2 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                                                        <span className="text-xs">
                                                            {message.timestamp.toLocaleTimeString()}
                                                        </span>
                                                        {message.role === 'user' && !message.isStreaming && editingMessageId !== message.id && (
                                                            <div className="flex gap-1">
                                                                <Button
                                                                    onClick={() => startEditingMessage(message.id, message.content)}
                                                                    size="sm"
                                                                    variant="ghost"
                                                                    className="h-6 w-6 p-0 hover:bg-blue-700 text-blue-100"
                                                                >
                                                                    <Edit3 className="h-3 w-3" />
                                                                </Button>
                                                                <Button
                                                                    onClick={() => deleteMessage(message.id)}
                                                                    size="sm"
                                                                    variant="ghost"
                                                                    className="h-6 w-6 p-0 hover:bg-red-700 text-blue-100"
                                                                >
                                                                    <X className="h-3 w-3" />
                                                                </Button>
                                                            </div>
                                                        )}
                                                    </div>
                                                    {message.chartSuggestions && message.chartSuggestions.length > 0 && (
                                                        <div className="mt-4 space-y-2">
                                                            <div className="text-sm font-medium text-gray-700">Suggested Charts:</div>
                                                            {message.chartSuggestions.map((suggestion, index) => (
                                                                <Button
                                                                    key={index}
                                                                    variant="outline"
                                                                    size="sm"
                                                                    onClick={() => handleChartGeneration(suggestion)}
                                                                    className="w-full justify-start text-left h-auto p-3 border-gray-300"
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
                                                        <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                                                            <User className="h-4 w-4 text-white" />
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                        {isLoading && (
                                            <div className="flex gap-4 justify-start">
                                                <div className="flex-shrink-0">
                                                    <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                                                        <Bot className="h-4 w-4 text-white" />
                                                    </div>
                                                </div>
                                                <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 max-w-2xl">
                                                    <div className="flex items-center gap-2">
                                                        <div className="flex space-x-1">
                                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                                        </div>
                                                        <span className="text-sm text-gray-600">AI is thinking...</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </ScrollArea>

                            {/* Embedded Charts */}
                            {embeddedCharts.length > 0 && (
                                <div className="border-t border-gray-200 bg-gray-50 p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Charts</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-6xl mx-auto">
                                        {embeddedCharts.map((chart) => (
                                            <AIChart
                                                key={chart.id}
                                                suggestion={chart.suggestion}
                                                onClose={() => handleChartClose(chart.id)}
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Input Area */}
                            <div className="border-t border-gray-200 bg-white px-6 py-4">
                                <div className="max-w-4xl mx-auto">
                                    <div className="flex gap-3">
                                        <Textarea
                                            value={input}
                                            onChange={(e) => setInput(e.target.value)}
                                            onKeyPress={handleKeyPress}
                                            placeholder="Ask me anything about your VirtPLC system..."
                                            className="min-h-[52px] resize-none border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                                            disabled={isLoading}
                                        />
                                        <Button
                                            onClick={sendMessage}
                                            disabled={isLoading || !input.trim()}
                                            size="lg"
                                            className="px-6"
                                        >
                                            <Send className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </>
                    ) : (
                        /* Welcome Screen */
                        <div className="flex-1 flex items-center justify-center bg-white">
                            <div className="text-center max-w-md mx-auto px-6">
                                <Bot className="h-16 w-16 text-gray-400 mx-auto mb-6" />
                                <h1 className="text-3xl font-bold text-gray-900 mb-4">
                                    VirtPLC AI Assistant
                                </h1>
                                <p className="text-gray-600 mb-8">
                                    Get intelligent insights and assistance about your industrial control system.
                                    Ask questions about data, performance, troubleshooting, and more.
                                </p>
                                <Button
                                    onClick={createNewConversation}
                                    size="lg"
                                    className="px-8 py-3"
                                >
                                    <Plus className="h-5 w-5 mr-2" />
                                    Start New Chat
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
}

export default AIAssistant;