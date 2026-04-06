/**
 * Main chat container component
 */
import { useRef, useEffect } from 'react';
import { MessageSquare, Trash2 } from 'lucide-react';
import { Message, Language } from '../../types';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import { InputArea } from './InputArea';

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  language: Language;
  onSendMessage: (message: string) => void;
  onClearChat: () => void;
}

export function ChatContainer({
  messages,
  isLoading,
  language,
  onSendMessage,
  onClearChat,
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isRTL = language === 'ar';

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <WelcomeMessage language={language} />
          ) : (
            <>
              {/* Clear button */}
              <div className="flex justify-center">
                <button
                  onClick={onClearChat}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-500
                    hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  {isRTL ? 'مسح المحادثة' : 'Effacer la conversation'}
                </button>
              </div>

              {/* Messages */}
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  language={language}
                />
              ))}

              {/* Typing indicator */}
              {isLoading && <TypingIndicator language={language} />}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input area */}
      <InputArea
        onSend={onSendMessage}
        isLoading={isLoading}
        language={language}
      />
    </div>
  );
}

/**
 * Welcome message component
 */
function WelcomeMessage({ language }: { language: Language }) {
  const isRTL = language === 'ar';

  const suggestions = isRTL
    ? [
        'ما هي حقوقي كمستهلك في المغرب؟',
        'كيف يمكنني تسجيل شركة جديدة؟',
        'ما هي إجراءات الطلاق في القانون المغربي؟',
        'ما هي العقوبات على السرقة؟',
      ]
    : [
        'Quels sont mes droits en tant que consommateur au Maroc?',
        'Comment puis-je enregistrer une nouvelle entreprise?',
        'Quelles sont les procédures de divorce au Maroc?',
        'Quelles sont les sanctions pour le vol?',
      ];

  return (
    <div
      className="flex flex-col items-center justify-center min-h-[60vh] text-center"
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-6">
        <MessageSquare className="w-8 h-8 text-primary-600" />
      </div>

      <h2 className="text-2xl font-semibold text-gray-900 mb-2">
        {isRTL ? 'مرحبًا بك في المساعد القانوني' : 'Bienvenue dans l\'Assistant Juridique'}
      </h2>

      <p className="text-gray-500 mb-8 max-w-md">
        {isRTL
          ? 'اسألني عن القانون المغربي - القانون المدني، قانون العمل، الضرائب، والإجراءات الإدارية'
          : 'Posez-moi vos questions sur le droit marocain - droit civil, droit du travail, fiscalité et procédures administratives'
        }
      </p>

      <div className="grid gap-3 w-full max-w-lg">
        <p className="text-sm text-gray-400">
          {isRTL ? 'جرب أن تسأل:' : 'Essayez de demander:'}
        </p>
        {suggestions.map((suggestion, i) => (
          <button
            key={i}
            className="w-full text-left px-4 py-3 bg-white border border-gray-200
              rounded-xl hover:border-primary-300 hover:bg-primary-50
              transition-colors text-gray-700 text-sm"
            onClick={() => {
              const event = new CustomEvent('suggestion-click', { detail: suggestion });
              window.dispatchEvent(event);
            }}
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
