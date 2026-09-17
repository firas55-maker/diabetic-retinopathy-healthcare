import React, { useState, useRef, useEffect } from 'react';
import './EducationalChatWidget.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface EducationalChatWidgetProps {
  onClose?: () => void;
}

export const EducationalChatWidget: React.FC<EducationalChatWidgetProps> = ({ onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! 👋 I\'m your diabetes and retinopathy educational assistant. Ask me anything about prevention, symptoms, screening, or management. Remember: I educate, not diagnose. Always consult your doctor with health concerns.',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiKeyError, setApiKeyError] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if API is properly configured on component mount
  useEffect(() => {
    const checkApiConfiguration = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/chat/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'test', conversation_history: [] }),
        });
        const data = await response.json();
        if (response.status === 500 && data.detail && data.detail.includes('not configured')) {
          setApiKeyError(true);
        }
      } catch (err) {
        // Silently fail - we'll catch it on first real message attempt
      }
    };
    checkApiConfiguration();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Check for API key error before attempting to send
    if (apiKeyError) {
      setError('API key not configured. Please ensure GEMINI_API_KEY is set in the backend environment.');
      return;
    }

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError('');
    setIsLoading(true);

    try {
      // Build conversation history for context
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Call backend chat endpoint
      const response = await fetch('http://localhost:8000/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 500 && errorData.detail && errorData.detail.includes('not configured')) {
          setApiKeyError(true);
          throw new Error('GEMINI_API_KEY is not configured. Please set it in your .env file and restart the backend.');
        }
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();

      // Add assistant response to chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError(err.message || 'Failed to send message. Please try again.');

      // Remove the user message if request failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! 👋 I\'m your diabetes and retinopathy educational assistant. Ask me anything about prevention, symptoms, screening, or management. Remember: I educate, not diagnose. Always consult your doctor with health concerns.',
        timestamp: new Date(),
      },
    ]);
    setError('');
  };

  return (
    <div className="chat-widget">
      {apiKeyError && (
        <div className="chat-api-key-error">
          <p>
            <strong>⚠️ Configuration Issue:</strong> Please set your actual GEMINI_API_KEY in .env before testing.
            The chat widget will not function without a valid API key.
          </p>
        </div>
      )}

      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-header-avatar">🤖</div>
          <div>
            <h3 className="chat-title">Educational Assistant</h3>
            <p className="chat-subtitle">Diabetes & Retinopathy Education</p>
          </div>
        </div>
        <button className="chat-clear-btn" onClick={clearChat} title="Clear conversation">
          ↻
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message chat-message-${message.role}`}>
            <div className="chat-message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="chat-message-content">
              <p className="chat-message-text">{message.content}</p>
              <span className="chat-message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-message chat-message-assistant">
            <div className="chat-message-avatar">🤖</div>
            <div className="chat-message-content">
              <div className="chat-loading">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          <p>⚠️ {error}</p>
        </div>
      )}

      <form onSubmit={handleSendMessage} className="chat-form">
        <div className="chat-input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about prevention, symptoms, or screening..."
            className="chat-input"
            disabled={isLoading}
            maxLength={500}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={isLoading || !input.trim()}
            title="Send message"
          >
            {isLoading ? '...' : '→'}
          </button>
        </div>
      </form>

      <div className="chat-disclaimer">
        <p>
          <strong>Disclaimer:</strong> Educational information only. Does not diagnose or interpret results. Always consult your doctor.
        </p>
      </div>
    </div>
  );
};
