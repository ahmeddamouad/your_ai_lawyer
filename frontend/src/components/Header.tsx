/**
 * Header component with logo and language toggle
 */
import { Languages, Scale } from 'lucide-react';
import { Language } from '../../types';

interface HeaderProps {
  language: Language;
  onLanguageChange: (lang: Language) => void;
}

export function Header({ language, onLanguageChange }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary-700 rounded-lg flex items-center justify-center">
          <Scale className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">
            {language === 'ar' ? 'المساعد القانوني المغربي' : 'Assistant Juridique Marocain'}
          </h1>
          <p className="text-xs text-gray-500">
            {language === 'ar' ? 'مدعوم بالذكاء الاصطناعي' : 'Propulsé par l\'IA'}
          </p>
        </div>
      </div>

      <button
        onClick={() => onLanguageChange(language === 'fr' ? 'ar' : 'fr')}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
        title={language === 'ar' ? 'Passer au français' : 'التبديل إلى العربية'}
      >
        <Languages className="w-4 h-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">
          {language === 'ar' ? 'FR' : 'AR'}
        </span>
      </button>
    </header>
  );
}
