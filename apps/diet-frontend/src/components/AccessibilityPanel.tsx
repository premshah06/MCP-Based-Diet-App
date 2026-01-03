import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  Eye,
  Globe,
  Languages,
  X
} from 'lucide-react';
import { useAccessibility, CULTURAL_CONTEXTS, LANGUAGE_OPTIONS } from './AccessibilityProvider';

interface AccessibilityPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const AccessibilityPanel: React.FC<AccessibilityPanelProps> = ({ isOpen, onClose }) => {
  const {
    settings,
    increaseFontSize,
    decreaseFontSize,
    toggleHighContrast,
    toggleReducedMotion,
    toggleScreenReaderMode,
    setLanguage,
    addCulturalPreference,
    removeCulturalPreference
  } = useAccessibility();

  const [activeTab, setActiveTab] = useState<'display' | 'language' | 'cultural'>('display');

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                <Settings className="w-6 h-6 mr-2" />
                Accessibility & Cultural Settings
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="Close accessibility panel"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="px-6 py-2 border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-4">
              {[
                { id: 'display', name: 'Display', icon: Eye },
                { id: 'language', name: 'Language', icon: Languages },
                { id: 'cultural', name: 'Cultural', icon: Globe }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                      : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
                    }`}
                >
                  <tab.icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="p-6 max-h-96 overflow-y-auto">
            <AnimatePresence mode="wait">
              {activeTab === 'display' && (
                <motion.div
                  key="display"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  {/* Font Size */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Font Size
                    </label>
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={decreaseFontSize}
                        disabled={settings.fontSize === 'small'}
                        className="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                        aria-label="Decrease font size"
                      >
                        A-
                      </button>
                      <span className="flex-1 text-center font-medium capitalize">
                        {settings.fontSize.replace('-', ' ')}
                      </span>
                      <button
                        onClick={increaseFontSize}
                        disabled={settings.fontSize === 'extra-large'}
                        className="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                        aria-label="Increase font size"
                      >
                        A+
                      </button>
                    </div>
                  </div>

                  {/* High Contrast */}
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        High Contrast Mode
                      </label>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Increases color contrast for better visibility
                      </p>
                    </div>
                    <button
                      onClick={toggleHighContrast}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${settings.contrast === 'high'
                          ? 'bg-primary-600'
                          : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      role="switch"
                      aria-checked={settings.contrast === 'high'}
                      aria-label="Toggle high contrast mode"
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${settings.contrast === 'high' ? 'translate-x-6' : 'translate-x-1'
                          }`}
                      />
                    </button>
                  </div>

                  {/* Reduced Motion */}
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Reduced Motion
                      </label>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Minimizes animations and transitions
                      </p>
                    </div>
                    <button
                      onClick={toggleReducedMotion}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${settings.reducedMotion
                          ? 'bg-primary-600'
                          : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      role="switch"
                      aria-checked={settings.reducedMotion}
                      aria-label="Toggle reduced motion"
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${settings.reducedMotion ? 'translate-x-6' : 'translate-x-1'
                          }`}
                      />
                    </button>
                  </div>

                  {/* Screen Reader Optimization */}
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Screen Reader Optimization
                      </label>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Enhanced descriptions and navigation
                      </p>
                    </div>
                    <button
                      onClick={toggleScreenReaderMode}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${settings.screenReaderOptimized
                          ? 'bg-primary-600'
                          : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      role="switch"
                      aria-checked={settings.screenReaderOptimized}
                      aria-label="Toggle screen reader optimization"
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${settings.screenReaderOptimized ? 'translate-x-6' : 'translate-x-1'
                          }`}
                      />
                    </button>
                  </div>
                </motion.div>
              )}

              {activeTab === 'language' && (
                <motion.div
                  key="language"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Interface Language
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {LANGUAGE_OPTIONS.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => setLanguage(lang.code)}
                          className={`p-3 text-left rounded-lg border transition-colors ${settings.language === lang.code
                              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                            }`}
                        >
                          <div className="font-medium">{lang.native}</div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {lang.name}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {activeTab === 'cultural' && (
                <motion.div
                  key="cultural"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      Cultural Dietary Preferences
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                      Select cultural contexts that influence your dietary preferences and restrictions
                    </p>
                    <div className="space-y-2">
                      {CULTURAL_CONTEXTS.map((context) => (
                        <div
                          key={context.id}
                          className={`p-3 rounded-lg border cursor-pointer transition-colors ${settings.culturalPreferences.includes(context.id)
                              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900'
                              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                            }`}
                          onClick={() => {
                            if (settings.culturalPreferences.includes(context.id)) {
                              removeCulturalPreference(context.id);
                            } else {
                              addCulturalPreference(context.id);
                            }
                          }}
                        >
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={settings.culturalPreferences.includes(context.id)}
                              onChange={() => { }} // Handled by div onClick
                              className="sr-only"
                            />
                            <div className="font-medium text-gray-900 dark:text-white">
                              {context.name}
                            </div>
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {context.description}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Settings are automatically saved and will persist across sessions.
              Cultural preferences help customize food recommendations and dietary suggestions.
            </p>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AccessibilityPanel;
