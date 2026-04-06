/**
 * Custom hook for chat functionality
 */
import { useState, useCallback } from 'react';
import { Message, Language, ChatResponse } from '../types';
import { chatApi } from '../services/api';

interface UseChatOptions {
  initialLanguage?: Language;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  language: Language;
  sendMessage: (content: string) => Promise<void>;
  setLanguage: (lang: Language) => void;
  clearChat: () => void;
}

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [language, setLanguage] = useState<Language>(options.initialLanguage || 'fr');

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await chatApi.sendMessage({
        message: content.trim(),
        session_id: sessionId || undefined,
        language,
      });

      // Update session ID
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);

      // Add error message
      const errorMsg: Message = {
        id: generateId(),
        role: 'assistant',
        content: language === 'ar'
          ? `عذراً، حدث خطأ: ${errorMessage}`
          : `Désolé, une erreur s'est produite: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, language]);

  const clearChat = useCallback(() => {
    if (sessionId) {
      chatApi.clearSession(sessionId).catch(console.error);
    }
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, [sessionId]);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    language,
    sendMessage,
    setLanguage,
    clearChat,
  };
}
