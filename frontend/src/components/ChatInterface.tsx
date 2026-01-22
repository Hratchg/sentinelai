/**
 * ChatInterface Component
 *
 * LLM-powered conversational interface for surveillance queries.
 * Ask questions and receive answers with video clip evidence.
 */

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface VideoClip {
  clip_url: string;
  person_id: string;
  timestamp: string;
  event_type: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  video_clips?: VideoClip[];
  timestamp: Date;
}

interface ChatInterfaceProps {
  apiBaseUrl?: string;
  voiceResponses?: any[];
}

export function ChatInterface({ apiBaseUrl = 'http://localhost:8000', voiceResponses = [] }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your surveillance AI assistant. You can ask me questions like:\n• \"Who is on camera 1?\"\n• \"When did I last see John?\"\n• \"What is Sarah doing right now?\"\n• \"Show me all times Michael visited this week\"\n\nYou can also use voice commands - just say \"Hey Sentinel\" followed by your question!",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add voice responses to messages
  useEffect(() => {
    if (voiceResponses && voiceResponses.length > 0) {
      const latestVoiceResponse = voiceResponses[0];

      // Add user question
      const userMessage: Message = {
        role: 'user',
        content: latestVoiceResponse.question,
        timestamp: new Date(latestVoiceResponse.timestamp)
      };

      // Add assistant answer
      const assistantMessage: Message = {
        role: 'assistant',
        content: latestVoiceResponse.answer,
        video_clips: latestVoiceResponse.video_clips || [],
        timestamp: new Date(latestVoiceResponse.timestamp)
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
    }
  }, [voiceResponses]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Query chat API
      const response = await axios.post(`${apiBaseUrl}/api/v1/chat`, {
        message: input,
        include_clips: true
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        video_clips: response.data.video_clips || [],
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chat error:', error);

      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-2xl ${msg.role === 'user' ? 'ml-12' : 'mr-12'}`}>
              {/* Message bubble */}
              <div
                className={`rounded-lg p-4 shadow-md ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-200 border border-gray-700'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {/* Video clips */}
                {msg.video_clips && msg.video_clips.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {msg.video_clips.map((clip, j) => (
                      <div key={j} className="bg-black rounded-lg overflow-hidden shadow-lg">
                        <video
                          src={`${apiBaseUrl}${clip.clip_url}`}
                          controls
                          className="w-full"
                          preload="metadata"
                        >
                          Your browser does not support video playback.
                        </video>
                        <div className="bg-gray-900 text-gray-300 text-xs p-2 flex justify-between">
                          <span className="font-semibold">{clip.person_id}</span>
                          <span>{clip.event_type.replace('_', ' ')}</span>
                          <span>{new Date(clip.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Timestamp */}
                <div className={`text-xs mt-2 ${
                  msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                }`}>
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-lg p-4 shadow-md border border-gray-700">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="animate-bounce w-2 h-2 bg-blue-500 rounded-full" style={{ animationDelay: '0.1s' }}></div>
                <div className="animate-bounce w-2 h-2 bg-blue-500 rounded-full" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="bg-gray-800 border-t border-gray-700 p-4">
        <div className="flex space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about the surveillance system..."
            className="flex-1 bg-gray-900 border border-gray-700 text-gray-200 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none placeholder-gray-500"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              'Send'
            )}
          </button>
        </div>

        {/* Example questions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-sm text-gray-400">Try:</span>
          {[
            "Who is on camera 1?",
            "When did I last see anyone?",
            "What gestures have been detected?"
          ].map((example, i) => (
            <button
              key={i}
              onClick={() => setInput(example)}
              className="text-sm px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-full text-gray-300 transition-colors"
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
