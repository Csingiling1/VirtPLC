import { useState } from 'react';
import { aiApi } from '../services/api';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

function AIAssistant() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

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
            const response = await aiApi.chat(input, 'VirtPLC system assistance');

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.response,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('AI chat error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again later.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="container">
            <h1>AI Assistant</h1>

            <div className="card" style={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
                {/* Chat Messages */}
                <div
                    style={{
                        flex: 1,
                        overflowY: 'auto',
                        padding: '1rem',
                        background: '#1a1a1a',
                        borderRadius: '8px',
                        marginBottom: '1rem',
                        border: '1px solid #333'
                    }}
                >
                    {messages.length === 0 ? (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            height: '100%',
                            color: '#666',
                            fontStyle: 'italic'
                        }}>
                            Start a conversation with the AI assistant...
                        </div>
                    ) : (
                        messages.map((message) => (
                            <div
                                key={message.id}
                                style={{
                                    marginBottom: '1rem',
                                    padding: '0.75rem',
                                    borderRadius: '8px',
                                    background: message.role === 'user' ? '#2a4a7a' : '#2a2a2a',
                                    border: `1px solid ${message.role === 'user' ? '#4a6fa5' : '#444'}`,
                                    marginLeft: message.role === 'user' ? '2rem' : '0',
                                    marginRight: message.role === 'assistant' ? '2rem' : '0',
                                }}
                            >
                                <div style={{
                                    fontSize: '0.8rem',
                                    color: '#888',
                                    marginBottom: '0.5rem',
                                    fontWeight: 'bold'
                                }}>
                                    {message.role === 'user' ? 'You' : 'AI Assistant'}
                                </div>
                                <div style={{ whiteSpace: 'pre-wrap' }}>
                                    {message.content}
                                </div>
                                <div style={{
                                    fontSize: '0.7rem',
                                    color: '#666',
                                    marginTop: '0.5rem'
                                }}>
                                    {message.timestamp.toLocaleTimeString()}
                                </div>
                            </div>
                        ))
                    )}
                    {isLoading && (
                        <div style={{
                            marginBottom: '1rem',
                            padding: '0.75rem',
                            borderRadius: '8px',
                            background: '#2a2a2a',
                            border: '1px solid #444',
                            marginLeft: '0',
                            marginRight: '2rem',
                        }}>
                            <div style={{
                                fontSize: '0.8rem',
                                color: '#888',
                                marginBottom: '0.5rem',
                                fontWeight: 'bold'
                            }}>
                                AI Assistant
                            </div>
                            <div>Thinking...</div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask me anything about your VirtPLC system..."
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            border: '1px solid #444',
                            borderRadius: '8px',
                            background: '#1a1a1a',
                            color: '#fff',
                            fontSize: '1rem',
                            resize: 'vertical',
                            minHeight: '60px',
                            maxHeight: '120px'
                        }}
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        style={{
                            padding: '0.75rem 1.5rem',
                            background: isLoading || !input.trim() ? '#444' : '#646cff',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
                            fontSize: '1rem',
                            whiteSpace: 'nowrap'
                        }}
                    >
                        {isLoading ? 'Sending...' : 'Send'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default AIAssistant;