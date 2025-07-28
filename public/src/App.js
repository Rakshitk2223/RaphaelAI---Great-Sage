import React, { useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './services/firebase';
import { sendMessageToRaphael } from './services/api';
import useSpeechSynthesis from './hooks/useSpeechSynthesis';
import AuthUI from './components/AuthUI';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';

function App() {
  const [messages, setMessages] = useState([]);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { isSpeaking, speak, stop: stopSpeaking } = useSpeechSynthesis();

  // Monitor authentication state
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      if (user) {
        addMessage("Hello! I'm Raphael, your personal AI assistant. I can help you remember things, manage your calendar, track homework, handle budgets, and much more. How can I assist you today?", 'raphael');
      } else {
        setMessages([]);
      }
    });

    return () => unsubscribe();
  }, []);

  const addMessage = (text, sender) => {
    const newMessage = {
      id: Date.now(),
      text,
      sender,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async (userMessage) => {
    if (!user || isLoading) return;

    addMessage(userMessage, 'user');
    setIsLoading(true);
    setError('');

    try {
      // Get Firebase ID token
      const idToken = await user.getIdToken();
      
      // Send message to backend
      const data = await sendMessageToRaphael(userMessage, idToken);
      
      const raphaelMessage = data.message || "I received your message but couldn't generate a response.";
      addMessage(raphaelMessage, 'raphael');
      
      // Speak the response
      speak(raphaelMessage);
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error.message || "Sorry, there was an error connecting to my services. Please check your internet connection.";
      addMessage(errorMessage, 'raphael');
      setError('Connection error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = (user) => {
    setError('');
    console.log('User logged in:', user.uid);
  };

  const handleLogoutSuccess = () => {
    setMessages([]);
    setError('');
    stopSpeaking();
    console.log('User logged out');
  };

  const handleAuthError = (errorMessage) => {
    setError(errorMessage);
  };

  const clearError = () => {
    setError('');
  };

  if (!user) {
    return (
      <div>
        {error && (
          <div className="fixed top-4 left-4 right-4 z-50">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex justify-between items-center max-w-md mx-auto">
              <span className="text-sm">{error}</span>
              <button onClick={clearError} className="text-red-700 hover:text-red-900">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}
        <AuthUI 
          user={user}
          onLoginSuccess={handleLoginSuccess}
          onLogoutSuccess={handleLogoutSuccess}
          onError={handleAuthError}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">R</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Raphael AI</h1>
              <p className="text-sm text-gray-600">Personal Assistant</p>
            </div>
          </div>
          <AuthUI 
            user={user}
            onLoginSuccess={handleLoginSuccess}
            onLogoutSuccess={handleLogoutSuccess}
            onError={handleAuthError}
          />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="max-w-4xl mx-auto px-4 py-2">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex justify-between items-center">
            <span className="text-sm">{error}</span>
            <button onClick={clearError} className="text-red-700 hover:text-red-900">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
          <ChatWindow messages={messages} isLoading={isLoading} />
          <MessageInput 
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            isSpeaking={isSpeaking}
            onStopSpeaking={stopSpeaking}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
