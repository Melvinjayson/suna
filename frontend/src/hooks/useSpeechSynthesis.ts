'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  SpeechConfig, 
  defaultSpeechConfig,
  voicePresets 
} from '@/lib/speech/speechConfig';
import {
  isSpeechSynthesisSupported,
  getAvailableVoices,
  findBestVoice,
  formatTextForSpeech
} from '@/lib/speech/speechUtils';

export interface UseSpeechSynthesisOptions {
  config?: Partial<SpeechConfig>;
  onStart?: () => void;
  onEnd?: () => void;
  onError?: (error: SpeechSynthesisErrorEvent) => void;
  onPause?: () => void;
  onResume?: () => void;
  preset?: keyof typeof voicePresets;
}

export interface SpeechQueueItem {
  id: string;
  text: string;
  options?: Partial<SpeechConfig['synthesis']>;
  priority?: 'low' | 'normal' | 'high';
}

export interface UseSpeechSynthesisReturn {
  isSupported: boolean;
  isSpeaking: boolean;
  isPaused: boolean;
  currentText: string;
  availableVoices: SpeechSynthesisVoice[];
  selectedVoice: SpeechSynthesisVoice | null;
  queue: SpeechQueueItem[];
  speak: (text: string, options?: Partial<SpeechConfig['synthesis']>) => string;
  pause: () => void;
  resume: () => void;
  stop: () => void;
  clearQueue: () => void;
  setVoice: (voice: SpeechSynthesisVoice | null) => void;
  removeFromQueue: (id: string) => void;
}

export const useSpeechSynthesis = (
  options: UseSpeechSynthesisOptions = {}
): UseSpeechSynthesisReturn => {
  const {
    config = {},
    onStart,
    onEnd,
    onError,
    onPause,
    onResume,
    preset
  } = options;

  const [isSupported] = useState(isSpeechSynthesisSupported());
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentText, setCurrentText] = useState('');
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [queue, setQueue] = useState<SpeechQueueItem[]>([]);

  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const finalConfig = { 
    ...defaultSpeechConfig, 
    ...config,
    synthesis: {
      ...defaultSpeechConfig.synthesis,
      ...config.synthesis,
      ...(preset ? voicePresets[preset] : {})
    }
  };

  // Load available voices
  useEffect(() => {
    if (!isSupported) return;

    const loadVoices = () => {
      const voices = getAvailableVoices();
      setAvailableVoices(voices);
      
      // Auto-select best voice if none selected
      if (!selectedVoice && voices.length > 0) {
        const bestVoice = findBestVoice(finalConfig.synthesis.language);
        setSelectedVoice(bestVoice);
      }
    };

    // Load voices immediately
    loadVoices();

    // Some browsers load voices asynchronously
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, [isSupported, finalConfig.synthesis.language, selectedVoice]);

  // Process speech queue
  useEffect(() => {
    if (!isSupported || isSpeaking || queue.length === 0) return;

    const processNextInQueue = () => {
      const nextItem = queue[0];
      if (!nextItem) return;

      const utterance = new SpeechSynthesisUtterance(
        formatTextForSpeech(nextItem.text)
      );

      // Apply configuration
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }
      utterance.rate = nextItem.options?.rate ?? finalConfig.synthesis.rate;
      utterance.pitch = nextItem.options?.pitch ?? finalConfig.synthesis.pitch;
      utterance.volume = nextItem.options?.volume ?? finalConfig.synthesis.volume;
      utterance.lang = nextItem.options?.language ?? finalConfig.synthesis.language;

      // Event handlers
      utterance.onstart = () => {
        setIsSpeaking(true);
        setCurrentText(nextItem.text);
        onStart?.();
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        setCurrentText('');
        setQueue(prev => prev.slice(1)); // Remove completed item
        onEnd?.();
      };

      utterance.onerror = (event) => {
        setIsSpeaking(false);
        setCurrentText('');
        setQueue(prev => prev.slice(1)); // Remove failed item
        onError?.(event);
      };

      utterance.onpause = () => {
        setIsPaused(true);
        onPause?.();
      };

      utterance.onresume = () => {
        setIsPaused(false);
        onResume?.();
      };

      currentUtteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    };

    processNextInQueue();
  }, [isSupported, isSpeaking, queue, selectedVoice, finalConfig, onStart, onEnd, onError, onPause, onResume]);

  const speak = useCallback((
    text: string, 
    options?: Partial<SpeechConfig['synthesis']>
  ): string => {
    if (!isSupported || !text.trim()) return '';

    const id = `speech-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newItem: SpeechQueueItem = {
      id,
      text: text.trim(),
      options,
      priority: 'normal'
    };

    setQueue(prev => [...prev, newItem]);
    return id;
  }, [isSupported]);

  const pause = useCallback(() => {
    if (!isSupported || !isSpeaking) return;
    window.speechSynthesis.pause();
  }, [isSupported, isSpeaking]);

  const resume = useCallback(() => {
    if (!isSupported || !isPaused) return;
    window.speechSynthesis.resume();
  }, [isSupported, isPaused]);

  const stop = useCallback(() => {
    if (!isSupported) return;
    
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
    setCurrentText('');
    currentUtteranceRef.current = null;
  }, [isSupported]);

  const clearQueue = useCallback(() => {
    setQueue([]);
    stop();
  }, [stop]);

  const setVoice = useCallback((voice: SpeechSynthesisVoice | null) => {
    setSelectedVoice(voice);
  }, []);

  const removeFromQueue = useCallback((id: string) => {
    setQueue(prev => prev.filter(item => item.id !== id));
  }, []);

  return {
    isSupported,
    isSpeaking,
    isPaused,
    currentText,
    availableVoices,
    selectedVoice,
    queue,
    speak,
    pause,
    resume,
    stop,
    clearQueue,
    setVoice,
    removeFromQueue,
  };
};
