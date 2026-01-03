/**
 * AI Chat Component
 * Interactive nutrition Q&A with AI-powered responses
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Send, Trash2, X, Camera } from 'lucide-react';
import { dietAPI } from '@/services/api';
import { useAuth } from '@/hooks/useAuth';
import type { ChatMessage } from '@/types/api';
import toast from 'react-hot-toast';

interface AIChatProps {
  isOpen: boolean;
  onClose: () => void;
  context?: Record<string, any>;
}

export function AIChat({ isOpen, onClose, context }: AIChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { isAuthenticated } = useAuth();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Add welcome message or load history on first open
  useEffect(() => {
    const loadHistory = async () => {
      if (isOpen && isAuthenticated && messages.length === 0) {
        setIsLoading(true);
        try {
          const response = await dietAPI.getChatHistory();
          if (response.history && response.history.length > 0) {
            setMessages(response.history.map((m, i) => ({
              id: `history-${i}`,
              role: m.role as 'user' | 'assistant',
              content: m.content,
              timestamp: new Date(m.timestamp),
            })));
          } else {
            // Only add welcome if no history
            setMessages([
              {
                id: 'welcome',
                role: 'assistant',
                content: "👋 Hi! I'm your AI nutrition coach. Ask me anything about nutrition, meal planning, macros, or healthy eating. I'm here to help you on your health journey!",
                timestamp: new Date(),
                provider: 'system',
              },
            ]);
          }
        } catch (error) {
          console.error('Failed to load chat history');
        } finally {
          setIsLoading(false);
        }
      } else if (isOpen && !isAuthenticated && messages.length === 0) {
        setMessages([
          {
            id: 'welcome',
            role: 'assistant',
            content: "👋 Hi! I'm your AI nutrition coach. Ask me anything about nutrition, meal planning, macros, or healthy eating. I'm here to help you on your health journey!",
            timestamp: new Date(),
            provider: 'system',
          },
        ]);
      }
    };

    loadHistory();
  }, [isOpen, isAuthenticated]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
      image_data: selectedImage || undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setSelectedImage(null);
    setIsLoading(true);

    try {
      const response = await dietAPI.chat({
        message: userMessage.content,
        context,
        image_data: userMessage.image_data,
      });

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        provider: response.provider,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      toast.error(error.message || 'Failed to get response');
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: "I'm sorry, I couldn't process your request. Please try again.",
          timestamp: new Date(),
          provider: 'error',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image is too large. Max 5MB allowed.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      setSelectedImage(base64String.split(',')[1]); // Only send the data part
    };
    reader.readAsDataURL(file);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    if (isAuthenticated) {
      try {
        await dietAPI.clearChatHistory();
      } catch (error) {
        console.warn('Failed to clear server chat history');
      }
    }
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: "Welcome to your AI Health Dashboard. I am your specialized nutrition coach, ready to analyze your macros, optimize your meal plans, or answer complex dietary questions. How can I assist you today?",
        timestamp: new Date(),
        provider: 'system',
      },
    ]);
  };

  const quickQuestions = [
    "How much protein do I need?",
    "What are good pre-workout foods?",
    "How can I reduce sugar cravings?",
    "Best foods for muscle building?",
  ];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          className="bg-white dark:bg-gray-800 sm:rounded-2xl shadow-2xl w-full sm:max-w-2xl h-full sm:h-[80vh] flex flex-col overflow-hidden relative"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-5 text-white flex items-center justify-between shadow-lg">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/20">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-black tracking-tight">AI Systems Protocol</h2>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                  <p className="text-emerald-100 text-xs font-bold uppercase tracking-widest">Active Nutrition Analysis</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={clearChat}
                className="p-2.5 hover:bg-white/10 rounded-xl transition-all border border-white/10"
                title="Clear chat"
              >
                <Trash2 className="w-5 h-5" />
              </button>
              <button
                onClick={onClose}
                className="p-2.5 hover:bg-white/10 rounded-xl transition-all border border-white/10"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
                    ? 'bg-primary-500 text-white rounded-br-md shadow-lg shadow-primary-500/20'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md'
                    }`}
                >
                  {message.image_data && (
                    <div className="mb-2 rounded-lg overflow-hidden border border-white/20">
                      <img
                        src={`data:image/jpeg;base64,${message.image_data}`}
                        alt="Uploaded food"
                        className="max-h-60 w-full object-cover"
                      />
                    </div>
                  )}
                  <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  {message.provider && message.role === 'assistant' && message.provider !== 'system' && (
                    <p className="text-xs mt-2 opacity-60">
                      via {message.provider}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick questions */}
          {messages.length <= 1 && (
            <div className="px-4 pb-2">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Quick questions:</p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question) => (
                  <button
                    key={question}
                    onClick={() => {
                      setInput(question);
                      inputRef.current?.focus();
                    }}
                    className="text-sm px-3 py-1.5 bg-gray-100 dark:bg-gray-700 
                             text-gray-700 dark:text-gray-300 rounded-full
                             hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
            {selectedImage && (
              <div className="mb-3 relative inline-block">
                <img
                  src={`data:image/jpeg;base64,${selectedImage}`}
                  alt="Preview"
                  className="w-20 h-20 object-cover rounded-xl border-2 border-emerald-500 shadow-md"
                />
                <button
                  onClick={() => setSelectedImage(null)}
                  className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}
            <div className="flex items-center gap-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageSelect}
                accept="image/*"
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                className="p-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 rounded-xl transition-all active:scale-95 disabled:opacity-50"
                title="Upload meal image"
              >
                <Camera className="w-5 h-5" />
              </button>
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={selectedImage ? "Describe this meal..." : "Ask about nutrition, meals, macros..."}
                disabled={isLoading}
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-emerald-500 focus:border-transparent
                         disabled:opacity-50 transition-colors"
              />
              <button
                onClick={sendMessage}
                disabled={(!input.trim() && !selectedImage) || isLoading}
                className="p-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl
                         disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-emerald-500/20 active:scale-95"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

export default AIChat;
