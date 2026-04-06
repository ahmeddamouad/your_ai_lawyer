/**
 * Message bubble component
 */
import { User, Bot, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Message, Language } from '../../types';

interface MessageBubbleProps {
  message: Message;
  language: Language;
}

export function MessageBubble({ message, language }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isRTL = language === 'ar';

  return (
    <div
      className={`flex gap-3 message-enter ${isUser ? 'flex-row-reverse' : ''}`}
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600' : 'bg-gray-200'
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-gray-600" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : 'text-left'}`}>
        <div
          className={`inline-block px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-primary-600 text-white rounded-tr-sm'
              : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className={`mt-2 flex flex-wrap gap-1 ${isRTL ? 'justify-end' : 'justify-start'}`}>
            {message.sources.slice(0, 3).map((source, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600"
                title={source}
              >
                <FileText className="w-3 h-3" />
                {source.split('/').pop()?.substring(0, 20)}...
              </span>
            ))}
            {message.sources.length > 3 && (
              <span className="px-2 py-1 text-xs text-gray-500">
                +{message.sources.length - 3} {isRTL ? 'المزيد' : 'de plus'}
              </span>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className={`text-xs text-gray-400 mt-1 ${isRTL ? 'text-right' : 'text-left'}`}>
          {message.timestamp.toLocaleTimeString(language === 'ar' ? 'ar-MA' : 'fr-FR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}
