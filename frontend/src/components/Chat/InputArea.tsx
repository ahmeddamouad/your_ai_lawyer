/**
 * Chat input area component
 */
import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Language } from '../../types';

interface InputAreaProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  language: Language;
}

export function InputArea({ onSend, isLoading, language }: InputAreaProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isRTL = language === 'ar';

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const placeholder = isRTL
    ? 'اطرح سؤالك القانوني هنا...'
    : 'Posez votre question juridique ici...';

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div
        className="flex items-end gap-3 max-w-4xl mx-auto"
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            rows={1}
            className={`w-full px-4 py-3 border border-gray-300 rounded-xl resize-none
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              disabled:bg-gray-50 disabled:cursor-not-allowed
              ${isRTL ? 'text-right font-arabic' : 'text-left'}`}
            style={{ minHeight: '48px', maxHeight: '200px' }}
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center
            transition-colors disabled:cursor-not-allowed
            ${input.trim() && !isLoading
              ? 'bg-primary-600 hover:bg-primary-700 text-white'
              : 'bg-gray-100 text-gray-400'
            }`}
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className={`w-5 h-5 ${isRTL ? 'rotate-180' : ''}`} />
          )}
        </button>
      </div>

      <p className="text-xs text-gray-400 text-center mt-2">
        {isRTL
          ? 'المساعد القانوني يقدم معلومات عامة فقط وليس استشارة قانونية رسمية'
          : 'L\'assistant juridique fournit des informations générales uniquement, pas de conseil juridique officiel'
        }
      </p>
    </div>
  );
}
