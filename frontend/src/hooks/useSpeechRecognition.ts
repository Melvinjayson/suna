'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  SpeechConfig, 
  defaultSpeechConfig 
} from '@/lib/speech/speechConfig';
import {
  isSpeechRecognitionSupported,
  processSpeechResult,
  handleSpeechError,
  debounce,
  SpeechRecognitionResult,
  SpeechError
} from '@/lib/speech/speechUtils';

export interface UseSpeechRecognitionOptions {
  config?: Partial<SpeechConfig>;
  onResult?: (result: SpeechRecognitionResult) => void;
  onError?: (error: SpeechError) => void;
  onStart?: () => void;
  onEnd?: () => void;
  autoStart?: boolean;
}

export interface UseSpeechRecognitionReturn {
  isSupported: boolean;
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  confidence: number;
  error: SpeechError | null;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
}

export const useSpeechRecognition = (
  options: UseSpeechRecognitionOptions = {}
): UseSpeechRecognitionReturn => {
  const {
    config = {},
    onResult,
    onError,
    onStart,
    onEnd,
    autoStart = false
  } = options;

  const [isSupported] = useState(isSpeechRecognitionSupported());
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState<SpeechError | null>(null);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const finalConfig = { ...defaultSpeechConfig, ...config };

  // Debounced result handler to avoid too frequent updates
  const debouncedOnResult = useCallback(
    debounce((result: SpeechRecognitionResult) => {
      onResult?.(result);
    }, 100),
    [onResult]
  );

  // Initialize speech recognition
  useEffect(() => {
    if (!isSupported) return;

    const SpeechRecognition = 
      window.SpeechRecognition ||
      window.webkitSpeechRecognition ||
      window.mozSpeechRecognition ||
      window.msSpeechRecognition;

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.continuous = finalConfig.recognition.continuous;
    recognition.interimResults = finalConfig.recognition.interimResults;
    recognition.maxAlternatives = finalConfig.recognition.maxAlternatives;
    recognition.lang = finalConfig.recognition.language;

    if (finalConfig.recognition.grammars) {
      recognition.grammars = finalConfig.recognition.grammars;
    }

    // Event handlers
    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      onStart?.();
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const results = processSpeechResult(event);
      let finalTranscript = '';
      let interimText = '';

      results.forEach(result => {
        if (result.isFinal) {
          finalTranscript += result.transcript + ' ';
          setConfidence(result.confidence);
          debouncedOnResult(result);
        } else {
          interimText += result.transcript;
        }
      });

      if (finalTranscript) {
        setTranscript(prev => prev + finalTranscript);
      }
      setInterimTranscript(interimText);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      const speechError = handleSpeechError(event);
      setError(speechError);
      setIsListening(false);
      onError?.(speechError);
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
      onEnd?.();
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [isSupported, finalConfig, debouncedOnResult, onError, onStart, onEnd]);

  // Auto-start if requested
  useEffect(() => {
    if (autoStart && isSupported && recognitionRef.current && !isListening) {
      startListening();
    }
  }, [autoStart, isSupported, isListening]);

  const startListening = useCallback(() => {
    if (!isSupported || !recognitionRef.current || isListening) return;

    try {
      setError(null);
      recognitionRef.current.start();
    } catch (err) {
      const speechError: SpeechError = {
        error: 'start-failed',
        message: 'Failed to start speech recognition',
      };
      setError(speechError);
      onError?.(speechError);
    }
  }, [isSupported, isListening, onError]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;

    try {
      recognitionRef.current.stop();
    } catch (err) {
      console.warn('Error stopping speech recognition:', err);
    }
  }, [isListening]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setConfidence(0);
    setError(null);
  }, []);

  return {
    isSupported,
    isListening,
    transcript,
    interimTranscript,
    confidence,
    error,
    startListening,
    stopListening,
    resetTranscript,
  };
};
