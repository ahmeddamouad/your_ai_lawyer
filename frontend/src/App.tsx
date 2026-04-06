/**
 * Main App component
 */
import { useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ChatContainer } from './components/Chat/ChatContainer';
import { useChat } from './hooks/useChat';

function App() {
  const {
    messages,
    isLoading,
    language,
    sendMessage,
    setLanguage,
    clearChat,
  } = useChat({ initialLanguage: 'fr' });

  // Handle suggestion clicks
  const handleSuggestion = useCallback((e: Event) => {
    const customEvent = e as CustomEvent<string>;
    sendMessage(customEvent.detail);
  }, [sendMessage]);

  useEffect(() => {
    window.addEventListener('suggestion-click', handleSuggestion);
    return () => window.removeEventListener('suggestion-click', handleSuggestion);
  }, [handleSuggestion]);

  return (
    <div
      className="min-h-screen flex flex-col bg-gray-50"
      dir={language === 'ar' ? 'rtl' : 'ltr'}
    >
      <Header
        language={language}
        onLanguageChange={setLanguage}
      />

      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        language={language}
        onSendMessage={sendMessage}
        onClearChat={clearChat}
      />
    </div>
  );
}

export default App;
