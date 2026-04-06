/**
 * Typing indicator component
 */
import { Language } from '../../types';

interface TypingIndicatorProps {
  language: Language;
}

export function TypingIndicator({ language }: TypingIndicatorProps) {
  return (
    <div className="flex gap-3" dir={language === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
        <span className="text-sm">AI</span>
      </div>
      <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></span>
          <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></span>
          <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></span>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          {language === 'ar' ? 'جارٍ الكتابة...' : 'En train d\'écrire...'}
        </p>
      </div>
    </div>
  );
}
