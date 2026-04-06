/**
 * Type definitions for the Moroccan Legal AI Chatbot
 */

export type Language = 'fr' | 'ar';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
}

export interface Conversation {
  sessionId: string;
  messages: Message[];
  language: Language;
  createdAt: Date;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  language: Language;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  session_id: string;
  language: Language;
}

export interface SessionInfo {
  session_id: string;
  message_count: number;
  created_at: string;
  language: Language;
}

export interface StatsResponse {
  model: string;
  embedding_model: string;
  ollama_host: string;
  document_count: number;
  retrieval_k: number;
}
