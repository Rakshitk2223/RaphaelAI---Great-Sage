// ChatWindow Component - Displays conversation and handles voice output
// Integrates speech synthesis for voice responses as specified in blueprint

import React, { useEffect, useRef } from 'react';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';

const ChatWindow = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);
  const {
    speak,
    cancel,
    isSpeaking,
    isSupported: speechSupported
  } = useSpeechSynthesis();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSpeakMessage = (text) => {
    if (speechSupported) {
      if (isSpeaking) {
        cancel();
      } else {
        speak(text);
      }
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="raphael-avatar">
              <span>R</span>
            </div>
            <h3>Hello! I'm Raphael AI</h3>
            <p>Your personal assistant inspired by Great Sage. I can help you with:</p>
            <ul>
              <li>📝 Managing tasks and homework</li>
              <li>📅 Calendar events and scheduling</li>
              <li>💰 Budget tracking and calculations</li>
              <li>🧠 Storing and recalling memories</li>
              <li>🗣️ Voice conversations (click the mic!)</li>
            </ul>
            <p>Just ask me anything or use voice input to get started!</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">
                <div className="message-header">
                  <span className="message-role">
                    {msg.role === 'user' ? 'You' : 'Raphael'}
                  </span>
                  <span className="message-time">
                    {formatTimestamp(msg.timestamp)}
                  </span>
                </div>
                
                <div className="message-text">
                  {msg.content}
                </div>
                
                {msg.role === 'assistant' && speechSupported && (
                  <button
                    onClick={() => handleSpeakMessage(msg.content)}
                    className={`speak-button ${isSpeaking ? 'speaking' : ''}`}
                    title={isSpeaking ? "Stop speaking" : "Read aloud"}
                  >
                    <svg className="speak-icon" viewBox="0 0 24 24">
                      {isSpeaking ? (
                        <path fill="currentColor" d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                      ) : (
                        <path fill="currentColor" d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                      )}
                    </svg>
                  </button>
                )}
                
                {msg.actions && msg.actions.length > 0 && (
                  <div className="message-actions">
                    <strong>Actions performed:</strong>
                    <ul>
                      {msg.actions.map((action, actionIndex) => (
                        <li key={actionIndex}>
                          {action.type}: {action.description}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message assistant-message loading">
            <div className="message-content">
              <div className="message-header">
                <span className="message-role">Raphael</span>
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
