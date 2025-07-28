// Message input component - handles text input and voice recognition
import React, { useState, useEffect } from 'react';
import useSpeechRecognition from '../hooks/useSpeechRecognition';

const MessageInput = ({ onSendMessage, isLoading, isSpeaking, onStopSpeaking }) => {
  const [message, setMessage] = useState('');
  const {
    isListening,
    transcript,
    error: speechError,
    isSupported: speechSupported,
    startListening,
    stopListening,
    resetTranscript
  } = useSpeechRecognition();

  // Update message when speech recognition provides transcript
  useEffect(() => {
    if (transcript) {
      setMessage(transcript);
      resetTranscript();
    }
  }, [transcript, resetTranscript]);

  const handleSendMessage = () => {
    if (!message.trim() || isLoading) return;
    
    const userMessage = message.trim();
    setMessage('');
    onSendMessage(userMessage);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="border-t bg-gray-50 p-4">
      <div className="flex items-center space-x-2">
        {/* Microphone Button */}
        <button
          onClick={handleMicClick}
          disabled={isLoading || !speechSupported}
          className={`p-3 rounded-full transition duration-200 ${
            isListening
              ? 'bg-red-600 hover:bg-red-700 text-white mic-pulse'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
          } ${(isLoading || !speechSupported) ? 'opacity-50 cursor-not-allowed' : ''}`}
          title={!speechSupported ? 'Voice recognition not supported' : (isListening ? 'Stop listening' : 'Start voice input')}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>
        
        {/* Text Input */}
        <div className="flex-1">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message or use the microphone..."
            disabled={isLoading}
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="1"
            style={{ minHeight: '50px', maxHeight: '120px' }}
          />
        </div>
        
        {/* Send Button */}
        <button
          onClick={handleSendMessage}
          disabled={!message.trim() || isLoading}
          className="p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-full transition duration-200"
          title="Send message"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>

        {/* Stop Speaking Button */}
        {isSpeaking && (
          <button
            onClick={onStopSpeaking}
            className="p-3 bg-orange-600 hover:bg-orange-700 text-white rounded-full transition duration-200"
            title="Stop speaking"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10h6v4H9z" />
            </svg>
          </button>
        )}
      </div>
      
      {/* Status Indicators */}
      {(isListening || isSpeaking) && (
        <div className="mt-2 text-center">
          <span className={`text-sm font-medium ${isListening ? 'text-red-600' : 'text-blue-600'}`}>
            {isListening ? '🎤 Listening...' : '🔊 Speaking...'}
          </span>
        </div>
      )}

      {/* Speech Error Display */}
      {speechError && (
        <div className="mt-2 text-center">
          <span className="text-sm text-red-600">{speechError}</span>
        </div>
      )}

      {/* Helper Text */}
      <div className="mt-2 text-xs text-gray-500 text-center">
        Try: "Remember my cat's name is Whiskers" • "What's my schedule today?" • "Calculate 25 * 4" • "Add homework"
      </div>
    </div>
  );
};

export default MessageInput;
