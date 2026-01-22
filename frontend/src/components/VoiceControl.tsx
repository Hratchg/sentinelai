/**
 * Voice Control Component
 *
 * Visual UI for voice-activated commands with "Hey Sentinel" wake word.
 *
 * Features:
 * - Microphone toggle button
 * - Audio waveform visualization
 * - Wake word detection indicator
 * - Real-time transcript display
 * - Status indicators
 */

import { useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, AlertCircle } from 'lucide-react';
import { useVoiceControl } from '../hooks/useVoiceControl';

interface VoiceControlProps {
  onCommand: (command: string) => void;
  enabled?: boolean;
}

export function VoiceControl({ onCommand, enabled = true }: VoiceControlProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const {
    isListening,
    transcript,
    isWakeWordActive,
    audioLevel,
    error,
    toggleListening
  } = useVoiceControl({
    onWakeWordDetected: () => {
      console.log('Wake word activated!');
    },
    onTranscript: (text) => {
      console.log('Voice command:', text);
      onCommand(text);
    },
    enabled
  });

  // Draw audio waveform visualization
  useEffect(() => {
    if (!canvasRef.current || !isListening) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = 'rgba(17, 24, 39, 0.8)'; // dark gray with transparency
    ctx.fillRect(0, 0, width, height);

    // Draw waveform based on audio level
    const barWidth = 4;
    const barSpacing = 2;
    const numBars = Math.floor(width / (barWidth + barSpacing));
    const centerY = height / 2;

    for (let i = 0; i < numBars; i++) {
      // Add randomness for visual effect (in production, use actual FFT data)
      const randomFactor = 0.5 + Math.random() * 0.5;
      const barHeight = audioLevel * height * randomFactor;

      const x = i * (barWidth + barSpacing);
      const y = centerY - barHeight / 2;

      // Color based on wake word state
      let color;
      if (isWakeWordActive) {
        color = '#3b82f6'; // blue when wake word detected
      } else if (audioLevel > 0.3) {
        color = '#10b981'; // green when voice detected
      } else {
        color = '#6b7280'; // gray when quiet
      }

      ctx.fillStyle = color;
      ctx.fillRect(x, y, barWidth, barHeight);
    }

    // Add glow effect for wake word
    if (isWakeWordActive) {
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#3b82f6';
    }
  }, [audioLevel, isListening, isWakeWordActive]);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-gray-800 rounded-lg shadow-2xl p-4 w-80 border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-blue-400" />
            <h3 className="text-white font-semibold">Voice Control</h3>
          </div>

          <button
            onClick={toggleListening}
            disabled={!!error}
            className={`p-2 rounded-full transition-colors ${
              error
                ? 'bg-gray-600 cursor-not-allowed'
                : isListening
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-green-500 hover:bg-green-600'
            }`}
            title={isListening ? 'Stop listening' : 'Start listening'}
          >
            {isListening ? (
              <Mic className="w-5 h-5 text-white" />
            ) : (
              <MicOff className="w-5 h-5 text-white" />
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-3 p-2 bg-red-900 bg-opacity-50 rounded border border-red-700 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-red-300">{error}</p>
          </div>
        )}

        {/* Waveform Canvas */}
        <canvas
          ref={canvasRef}
          width={300}
          height={80}
          className="w-full rounded border border-gray-700 mb-3 bg-gray-900"
        />

        {/* Status Indicator */}
        <div className="text-center mb-2">
          {isListening ? (
            <div className="flex items-center justify-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isWakeWordActive
                    ? 'bg-blue-400 animate-pulse'
                    : audioLevel > 0.1
                    ? 'bg-green-400'
                    : 'bg-gray-500'
                }`}
              />
              <span className="text-sm text-gray-300">
                {isWakeWordActive
                  ? 'Listening for command...'
                  : 'Say "Hey Sentinel" to activate'}
              </span>
            </div>
          ) : (
            <span className="text-sm text-gray-500">
              {error ? 'Voice control unavailable' : 'Click microphone to start'}
            </span>
          )}
        </div>

        {/* Transcript Display */}
        {transcript && (
          <div className="bg-gray-900 rounded p-2 text-xs text-gray-400 max-h-20 overflow-y-auto mb-2">
            <span className="text-gray-500 font-mono">→</span> {transcript}
          </div>
        )}

        {/* Instructions */}
        {!transcript && !error && (
          <div className="text-xs text-gray-500 text-center space-y-1">
            <p className="font-medium text-gray-400">Try saying:</p>
            <p className="italic text-gray-600">"Hey Sentinel, who is on camera 1?"</p>
            <p className="italic text-gray-600">"Hey Sentinel, what is John doing?"</p>
          </div>
        )}

        {/* Audio Level Indicator (Debug) */}
        {isListening && (
          <div className="mt-2 pt-2 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Audio Level:</span>
              <span className="font-mono">{Math.round(audioLevel * 100)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1.5 mt-1">
              <div
                className="bg-green-500 h-1.5 rounded-full transition-all duration-100"
                style={{ width: `${audioLevel * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
