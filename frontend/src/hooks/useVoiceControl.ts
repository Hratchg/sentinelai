/**
 * Voice Control Hook for "Hey Sentinel" Wake Word Detection
 *
 * Provides:
 * - Web Speech API integration
 * - Wake word detection
 * - Audio level monitoring
 * - Continuous listening mode
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// Extend Window interface for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface UseVoiceControlOptions {
  onWakeWordDetected?: () => void;
  onTranscript?: (text: string) => void;
  wakeWord?: string;
  enabled?: boolean;
}

export function useVoiceControl({
  onWakeWordDetected,
  onTranscript,
  wakeWord = 'hey sentinel',
  enabled = true
}: UseVoiceControlOptions = {}) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isWakeWordActive, setIsWakeWordActive] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Initialize Web Speech API
  useEffect(() => {
    if (!enabled) return;

    // Check for Web Speech API support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      console.error('Web Speech API not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onresult = (event: any) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptSegment = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalTranscript += transcriptSegment + ' ';
        } else {
          interimTranscript += transcriptSegment;
        }
      }

      const currentTranscript = (finalTranscript || interimTranscript).trim();
      setTranscript(currentTranscript);

      // Check for wake word
      const lowerTranscript = currentTranscript.toLowerCase();
      const lowerWakeWord = wakeWord.toLowerCase();

      if (lowerTranscript.includes(lowerWakeWord)) {
        console.log('Wake word detected:', wakeWord);
        setIsWakeWordActive(true);
        onWakeWordDetected?.();

        // Extract command after wake word
        const wakeWordIndex = lowerTranscript.indexOf(lowerWakeWord);
        const command = currentTranscript.slice(wakeWordIndex + wakeWord.length).trim();

        if (command) {
          console.log('Command extracted:', command);
          onTranscript?.(command);
        }
      } else if (isWakeWordActive && finalTranscript) {
        // Continuation of command after wake word
        console.log('Command continuation:', finalTranscript.trim());
        onTranscript?.(finalTranscript.trim());
        setIsWakeWordActive(false);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);

      if (event.error === 'no-speech') {
        // Not an actual error, just no speech detected
        return;
      }

      if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access.');
      } else {
        setError(`Speech recognition error: ${event.error}`);
      }

      setIsListening(false);
    };

    recognition.onend = () => {
      if (enabled && isListening) {
        // Restart if still enabled
        try {
          recognition.start();
        } catch (e) {
          console.error('Failed to restart recognition:', e);
        }
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Ignore errors during cleanup
        }
      }
    };
  }, [enabled, wakeWord, isWakeWordActive, onWakeWordDetected, onTranscript, isListening]);

  // Initialize audio level monitoring
  useEffect(() => {
    if (!enabled || !isListening) {
      // Stop monitoring when disabled or not listening
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      return;
    }

    const initAudioMonitoring = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;

        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;

        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        analyserRef.current = analyser;

        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const updateLevel = () => {
          if (!isListening) {
            if (animationFrameRef.current) {
              cancelAnimationFrame(animationFrameRef.current);
              animationFrameRef.current = null;
            }
            return;
          }

          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average / 255); // Normalize to 0-1

          animationFrameRef.current = requestAnimationFrame(updateLevel);
        };

        updateLevel();
      } catch (error) {
        console.error('Error accessing microphone:', error);
        setError('Failed to access microphone. Please check permissions.');
      }
    };

    initAudioMonitoring();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [enabled, isListening]);

  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setError(null);
        console.log('Voice control started');
      } catch (e) {
        console.error('Failed to start speech recognition:', e);
        setError('Failed to start voice recognition');
      }
    }
  }, [isListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
        setIsListening(false);
        setIsWakeWordActive(false);
        setTranscript('');
        console.log('Voice control stopped');
      } catch (e) {
        console.error('Failed to stop speech recognition:', e);
      }
    }
  }, [isListening]);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  return {
    isListening,
    transcript,
    isWakeWordActive,
    audioLevel,
    error,
    startListening,
    stopListening,
    toggleListening
  };
}
