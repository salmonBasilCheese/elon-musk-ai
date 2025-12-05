'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Brain } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    thinkingProcess?: string;
    responseTimeMs?: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Simple markdown to HTML converter for readable responses
function renderMarkdown(text: string): string {
    return text
        // Headers
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        // Bold
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Unordered lists
        .replace(/^[-•] (.+)$/gm, '<li>$1</li>')
        // Ordered lists  
        .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
        // Wrap consecutive list items
        .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
        // Paragraphs (double newline)
        .replace(/\n\n+/g, '</p><p>')
        // Remove single newlines (they're in lists already)
        .replace(/\n/g, ' ')
        // Wrap in paragraph
        .replace(/^/, '<p>')
        .replace(/$/, '</p>')
        // Clean up
        .replace(/<p><\/p>/g, '')
        .replace(/<p><ul>/g, '<ul>')
        .replace(/<\/ul><\/p>/g, '</ul>')
        .replace(/<p><h/g, '<h')
        .replace(/<\/h(\d)><\/p>/g, '</h$1>');
}

export default function Home() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const chatContainerRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [input]);

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    mode: 'auto',  // Auto-detect mode on backend
                    conversation_history: messages.slice(-10).map(m => ({
                        role: m.role,
                        content: m.content,
                    })),
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'API request failed');
            }

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.message,
                timestamp: new Date(),
                thinkingProcess: data.thinking_process,
                responseTimeMs: data.response_time_ms,
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: error instanceof Error ? error.message : 'エラーが発生しました。',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const handleExampleClick = (prompt: string) => {
        setInput(prompt);
        textareaRef.current?.focus();
    };

    const examplePrompts = [
        'AIが人類に与える影響をどう考えるべきか？',
        '転職すべきか迷っています。どう判断すれば？',
        '起業のアイデアがあるが、リスクが怖い',
        '人生で本当に大切なことは何だと思う？',
    ];

    return (
        <div className="app-container">
            {/* Header */}
            <header className="header">
                <div className="logo" onClick={() => setMessages([])} style={{ cursor: 'pointer' }} title="ホームに戻る">
                    <img src="/elon-logo.png" alt="Elon Musk" className="logo-icon" style={{ objectFit: 'cover' }} />
                    <span className="logo-text">Elon Musk AI</span>
                </div>
            </header>

            {/* Chat Area */}
            {messages.length === 0 ? (
                <div className="welcome-container">
                    <img src="/elon-logo.png" alt="Elon Musk" className="welcome-icon" style={{ objectFit: 'cover' }} />
                    <h1 className="welcome-title">Elon Musk AI</h1>
                    <p className="welcome-subtitle">
                        ビジネス、技術、人生の悩みまで、あらゆる質問に回答します。
                        質問内容に応じて最適な思考スタイルを自動で適用します。
                    </p>
                    <div className="example-prompts">
                        {examplePrompts.map((prompt, i) => (
                            <button
                                key={i}
                                className="example-prompt"
                                onClick={() => handleExampleClick(prompt)}
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="chat-container" ref={chatContainerRef}>
                    {messages.map((message) => (
                        <div key={message.id} className={`message ${message.role}`}>
                            <div className="message-avatar">
                                {message.role === 'user' ? '👤' : '🚀'}
                            </div>
                            <div className="message-content">
                                {message.role === 'user' ? (
                                    <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
                                ) : (
                                    <div
                                        dangerouslySetInnerHTML={{
                                            __html: renderMarkdown(message.content)
                                        }}
                                    />
                                )}
                                {message.role === 'assistant' && (
                                    <div className="message-meta">
                                        {message.thinkingProcess && (
                                            <span className="thinking-badge">
                                                <Brain size={12} />
                                                {message.thinkingProcess}
                                            </span>
                                        )}
                                        {message.responseTimeMs && (
                                            <span>{(message.responseTimeMs / 1000).toFixed(1)}秒</span>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message assistant">
                            <div className="message-avatar">🚀</div>
                            <div className="thinking-indicator">
                                <div className="thinking-dots">
                                    <div className="thinking-dot" />
                                    <div className="thinking-dot" />
                                    <div className="thinking-dot" />
                                </div>
                                <span className="thinking-text">思考中...</span>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Input Area */}
            <div className="input-container">
                <div className="input-wrapper">
                    <textarea
                        ref={textareaRef}
                        className="input-field"
                        placeholder="何でも質問してください..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        rows={1}
                        disabled={isLoading}
                    />
                    <button
                        className="send-btn"
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
}
