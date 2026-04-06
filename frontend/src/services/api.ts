/**
 * API service for communicating with the backend
 */
import { ChatRequest, ChatResponse, SessionInfo, StatsResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  return response.json();
}

export const chatApi = {
  /**
   * Send a message to the chat API
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    return fetchApi<ChatResponse>('/api/chat/', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Get all sessions
   */
  getSessions: async (): Promise<{ sessions: SessionInfo[] }> => {
    return fetchApi<{ sessions: SessionInfo[] }>('/api/chat/sessions');
  },

  /**
   * Get a specific session
   */
  getSession: async (sessionId: string) => {
    return fetchApi(`/api/chat/session/${sessionId}`);
  },

  /**
   * Clear a session
   */
  clearSession: async (sessionId: string) => {
    return fetchApi(`/api/chat/session/${sessionId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Get RAG stats
   */
  getStats: async (): Promise<StatsResponse> => {
    return fetchApi<StatsResponse>('/api/chat/stats');
  },
};

export const healthApi = {
  /**
   * Check API health
   */
  check: async () => {
    return fetchApi('/health');
  },
};

export { ApiError };
