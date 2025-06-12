import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTranscription } from '@/hooks/react-query/transcription/use-transcription';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { isSpeechRecognitionSupported } from '@/lib/speech/speechUtils';

interface VoiceRecorderProps {
    onTranscription: (text: string) => void;
    disabled?: boolean;
    useRealtimeRecognition?: boolean;
}

const MAX_RECORDING_TIME = 15 * 60 * 1000; // 15 minutes in milliseconds

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
    onTranscription,
    disabled = false,
    useRealtimeRecognition = true,
}) => {
    const [state, setState] = useState<'idle' | 'recording' | 'processing'>('idle');
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);
    const streamRef = useRef<MediaStream | null>(null);
    const recordingStartTimeRef = useRef<number | null>(null);
    const maxTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const transcriptionMutation = useTranscription();

    // Real-time speech recognition
    const {
        isSupported: speechRecognitionSupported,
        isListening: isRealtimeListening,
        transcript: realtimeTranscript,
        confidence,
        error: speechError,
        startListening: startRealtimeListening,
        stopListening: stopRealtimeListening,
        resetTranscript,
    } = useSpeechRecognition({
        config: {
            recognition: {
                continuous: false,
                interimResults: true,
                language: 'en-US',
            },
        },
        onResult: (result) => {
            if (result.isFinal && result.transcript.trim()) {
                onTranscription(result.transcript.trim());
                resetTranscript();
            }
        },
        onError: (error) => {
            console.error('Real-time speech recognition error:', error);
        },
    });

    const shouldUseRealtime = useRealtimeRecognition && speechRecognitionSupported && isSpeechRecognitionSupported();

    // Auto-stop recording after 15 minutes
    useEffect(() => {
        if (state === 'recording') {
            recordingStartTimeRef.current = Date.now();
            maxTimeoutRef.current = setTimeout(() => {
                console.log('Auto-stopping recording after 15 minutes');
                stopRecording();
            }, MAX_RECORDING_TIME);
        } else {
            recordingStartTimeRef.current = null;
            if (maxTimeoutRef.current) {
                clearTimeout(maxTimeoutRef.current);
                maxTimeoutRef.current = null;
            }
        }

        return () => {
            if (maxTimeoutRef.current) {
                clearTimeout(maxTimeoutRef.current);
            }
        };
    }, [state]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const options = { mimeType: 'audio/webm' };
            const mediaRecorder = new MediaRecorder(stream, options);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                if (chunksRef.current.length === 0) {
                    // Recording was cancelled
                    cleanupStream();
                    setState('idle');
                    return;
                }

                setState('processing');
                const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
                const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });

                transcriptionMutation.mutate(audioFile, {
                    onSuccess: (data) => {
                        onTranscription(data.text);
                        setState('idle');
                    },
                    onError: (error) => {
                        console.error('Transcription failed:', error);
                        setState('idle');
                    },
                });

                cleanupStream();
            };

            mediaRecorder.start();
            setState('recording');
        } catch (error) {
            console.error('Error starting recording:', error);
            setState('idle');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && state === 'recording') {
            mediaRecorderRef.current.stop();
        }
    };

    const cancelRecording = () => {
        if (mediaRecorderRef.current && state === 'recording') {
            chunksRef.current = []; // Clear chunks to signal cancellation
            mediaRecorderRef.current.stop();
            cleanupStream();
            setState('idle');
        }
    };

    const cleanupStream = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
    };

    const handleClick = () => {
        if (shouldUseRealtime) {
            // Use real-time speech recognition
            if (isRealtimeListening) {
                stopRealtimeListening();
            } else {
                resetTranscript();
                startRealtimeListening();
            }
        } else {
            // Use traditional recording + transcription
            if (state === 'idle') {
                startRecording();
            } else if (state === 'recording') {
                stopRecording();
            }
        }
    };

    const handleRightClick = (e: React.MouseEvent) => {
        e.preventDefault();
        if (shouldUseRealtime) {
            if (isRealtimeListening) {
                stopRealtimeListening();
                resetTranscript();
            }
        } else {
            if (state === 'recording') {
                cancelRecording();
            }
        }
    };

    const getButtonClass = () => {
        if (shouldUseRealtime) {
            if (isRealtimeListening) {
                return 'text-red-500 hover:bg-red-600 animate-pulse';
            }
            return 'hover:bg-gray-100';
        } else {
            switch (state) {
                case 'recording':
                    return 'text-red-500 hover:bg-red-600';
                case 'processing':
                    return 'hover:bg-gray-100';
                default:
                    return 'hover:bg-gray-100';
            }
        }
    };

    const getIcon = () => {
        if (shouldUseRealtime) {
            if (isRealtimeListening) {
                return <MicOff className="h-4 w-4" />;
            }
            return <Mic className="h-4 w-4" />;
        } else {
            switch (state) {
                case 'recording':
                    return <Square className="h-4 w-4" />;
                case 'processing':
                    return <Loader2 className="h-4 w-4 animate-spin" />;
                default:
                    return <Mic className="h-4 w-4" />;
            }
        }
    };

    const getTitle = () => {
        if (shouldUseRealtime) {
            return isRealtimeListening ? 'Click to stop listening' : 'Click to start voice input';
        } else {
            return state === 'recording' ? 'Click to stop recording' : 'Click to start recording';
        }
    };

    return (
        <div className="flex items-center gap-1">
            <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleClick}
                onContextMenu={handleRightClick}
                disabled={disabled || state === 'processing'}
                className={`h-8 w-8 p-0 transition-colors ${getButtonClass()}`}
                title={getTitle()}
            >
                {getIcon()}
            </Button>

            {/* Show confidence indicator for real-time recognition */}
            {shouldUseRealtime && isRealtimeListening && confidence > 0 && (
                <Badge variant="outline" className="text-xs px-1 py-0">
                    {Math.round(confidence * 100)}%
                </Badge>
            )}

            {/* Show error indicator */}
            {shouldUseRealtime && speechError && (
                <Badge variant="destructive" className="text-xs px-1 py-0">
                    Error
                </Badge>
            )}
        </div>
    );
}; 