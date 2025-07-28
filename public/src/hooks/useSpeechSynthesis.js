// Custom hook for Speech Synthesis using Web Speech API
import { useState, useEffect, useRef } from 'react';

const useSpeechSynthesis = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState('');
  const synthRef = useRef(null);

  // Check if browser supports Speech Synthesis
  const isSupported = 'speechSynthesis' in window;

  useEffect(() => {
    if (isSupported) {
      synthRef.current = window.speechSynthesis;
    } else {
      setError('Speech synthesis is not supported in this browser');
    }

    // Cleanup function
    return () => {
      if (synthRef.current && isSpeaking) {
        synthRef.current.cancel();
      }
    };
  }, [isSpeaking]);

  const speak = (text, options = {}) => {
    if (!isSupported) {
      setError('Speech synthesis is not supported');
      return;
    }

    if (!text || !synthRef.current) return;

    // Stop any ongoing speech
    synthRef.current.cancel();

    // Clean the text for speech (remove markdown and special characters)
    const cleanText = text.replace(/[*_~`]/g, '').replace(/\n/g, ' ');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Configure voice settings
    utterance.rate = options.rate || 0.9;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 0.8;

    // Try to find a pleasant voice
    const voices = synthRef.current.getVoices();
    if (options.voice) {
      utterance.voice = options.voice;
    } else {
      const preferredVoice = voices.find(voice => 
        voice.name.includes('Google') || 
        voice.name.includes('Microsoft') ||
        voice.lang.startsWith('en')
      );
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
    }

    // Event handlers
    utterance.onstart = () => {
      setIsSpeaking(true);
      setError('');
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setError(`Speech synthesis error: ${event.error}`);
      setIsSpeaking(false);
    };

    synthRef.current.speak(utterance);
  };

  const stop = () => {
    if (synthRef.current && isSpeaking) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const getVoices = () => {
    if (synthRef.current) {
      return synthRef.current.getVoices();
    }
    return [];
  };

  return {
    isSpeaking,
    error,
    isSupported,
    speak,
    stop,
    getVoices
  };
};

export default useSpeechSynthesis;
