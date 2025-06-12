'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';
import { SpeechConfig } from '@/lib/speech/speechConfig';
import { SpeechError } from '@/lib/speech/speechUtils';

export interface VoiceContextValue {
  // Speech Recognition
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  speechError: SpeechError | null;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  
  // Speech Synthesis
  isSpeaking: boolean;
  currentText: string;
  speak: (text: string) => void;
  stopSpeaking: () => void;
  
  // Voice Settings
  voiceSettings: VoiceSettings;
  updateVoiceSettings: (settings: Partial<VoiceSettings>) => void;
  
  // Voice Mode
  isVoiceMode: boolean;
  enableVoiceMode: () => void;
  disableVoiceMode: () => void;
  toggleVoiceMode: () => void;
  
  // Wake Word
  isWakeWordActive: boolean;
  enableWakeWord: () => void;
  disableWakeWord: () => void;
  
  // Support Status
  isVoiceSupported: boolean;
}

export interface VoiceSettings {
  language: string;
  rate: number;
  pitch: number;
  volume: number;
  autoSpeak: boolean;
  wakeWordEnabled: boolean;
  voice: SpeechSynthesisVoice | null;
}

const defaultVoiceSettings: VoiceSettings = {
  language: 'en-US',
  rate: 1.0,
  pitch: 1.0,
  volume: 0.9,
  autoSpeak: true,
  wakeWordEnabled: true,
  voice: null,
};

const VoiceContext = createContext<VoiceContextValue | undefined>(undefined);

export interface VoiceProviderProps {
  children: ReactNode;
  config?: Partial<SpeechConfig>;
}

export const VoiceProvider: React.FC<VoiceProviderProps> = ({
  children,
  config = {},
}) => {
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>(defaultVoiceSettings);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isWakeWordActive, setIsWakeWordActive] = useState(false);

  const speechConfig: Partial<SpeechConfig> = {
    recognition: {
      continuous: true,
      interimResults: true,
      language: voiceSettings.language,
      ...config.recognition,
    },
    synthesis: {
      rate: voiceSettings.rate,
      pitch: voiceSettings.pitch,
      volume: voiceSettings.volume,
      language: voiceSettings.language,
      voice: voiceSettings.voice,
      ...config.synthesis,
    },
  };

  const {
    isSupported: speechRecognitionSupported,
    isListening,
    transcript,
    interimTranscript,
    error: speechError,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition({
    config: speechConfig,
    autoStart: isWakeWordActive,
  });

  const {
    isSupported: speechSynthesisSupported,
    isSpeaking,
    currentText,
    speak: speakText,
    stop: stopSpeaking,
  } = useSpeechSynthesis({
    config: speechConfig,
    onStart: () => {
      // Pause listening while speaking to avoid feedback
      if (isListening) {
        stopListening();
      }
    },
    onEnd: () => {
      // Resume listening after speaking if in voice mode
      if (isVoiceMode && !isListening) {
        setTimeout(() => startListening(), 500);
      }
    },
  });

  const isVoiceSupported = speechRecognitionSupported && speechSynthesisSupported;

  const updateVoiceSettings = useCallback((newSettings: Partial<VoiceSettings>) => {
    setVoiceSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  const speak = useCallback((text: string) => {
    if (voiceSettings.autoSpeak && text.trim()) {
      speakText(text);
    }
  }, [voiceSettings.autoSpeak, speakText]);

  const enableVoiceMode = useCallback(() => {
    if (!isVoiceSupported) return;
    setIsVoiceMode(true);
    if (voiceSettings.wakeWordEnabled) {
      setIsWakeWordActive(true);
    }
  }, [isVoiceSupported, voiceSettings.wakeWordEnabled]);

  const disableVoiceMode = useCallback(() => {
    setIsVoiceMode(false);
    setIsWakeWordActive(false);
    if (isListening) {
      stopListening();
    }
    if (isSpeaking) {
      stopSpeaking();
    }
  }, [isListening, isSpeaking, stopListening, stopSpeaking]);

  const toggleVoiceMode = useCallback(() => {
    if (isVoiceMode) {
      disableVoiceMode();
    } else {
      enableVoiceMode();
    }
  }, [isVoiceMode, enableVoiceMode, disableVoiceMode]);

  const enableWakeWord = useCallback(() => {
    if (!isVoiceSupported) return;
    setIsWakeWordActive(true);
    setVoiceSettings(prev => ({ ...prev, wakeWordEnabled: true }));
    if (!isListening) {
      startListening();
    }
  }, [isVoiceSupported, isListening, startListening]);

  const disableWakeWord = useCallback(() => {
    setIsWakeWordActive(false);
    setVoiceSettings(prev => ({ ...prev, wakeWordEnabled: false }));
    if (isListening && !isVoiceMode) {
      stopListening();
    }
  }, [isListening, isVoiceMode, stopListening]);

  const contextValue: VoiceContextValue = {
    // Speech Recognition
    isListening,
    transcript,
    interimTranscript,
    speechError,
    startListening,
    stopListening,
    resetTranscript,
    
    // Speech Synthesis
    isSpeaking,
    currentText,
    speak,
    stopSpeaking,
    
    // Voice Settings
    voiceSettings,
    updateVoiceSettings,
    
    // Voice Mode
    isVoiceMode,
    enableVoiceMode,
    disableVoiceMode,
    toggleVoiceMode,
    
    // Wake Word
    isWakeWordActive,
    enableWakeWord,
    disableWakeWord,
    
    // Support Status
    isVoiceSupported,
  };

  return (
    <VoiceContext.Provider value={contextValue}>
      {children}
    </VoiceContext.Provider>
  );
};

export const useVoice = (): VoiceContextValue => {
  const context = useContext(VoiceContext);
  if (context === undefined) {
    throw new Error('useVoice must be used within a VoiceProvider');
  }
  return context;
};
