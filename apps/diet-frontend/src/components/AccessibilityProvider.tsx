import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AccessibilitySettings {
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  contrast: 'normal' | 'high';
  reducedMotion: boolean;
  screenReaderOptimized: boolean;
  language: string;
  culturalPreferences: string[];
}

interface AccessibilityContextType {
  settings: AccessibilitySettings;
  updateSettings: (newSettings: Partial<AccessibilitySettings>) => void;
  increaseFontSize: () => void;
  decreaseFontSize: () => void;
  toggleHighContrast: () => void;
  toggleReducedMotion: () => void;
  toggleScreenReaderMode: () => void;
  setLanguage: (language: string) => void;
  addCulturalPreference: (preference: string) => void;
  removeCulturalPreference: (preference: string) => void;
}

const defaultSettings: AccessibilitySettings = {
  fontSize: 'medium',
  contrast: 'normal',
  reducedMotion: false,
  screenReaderOptimized: false,
  language: 'en',
  culturalPreferences: []
};

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

interface AccessibilityProviderProps {
  children: ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<AccessibilitySettings>(() => {
    // Load from localStorage
    const saved = localStorage.getItem('accessibility-settings');
    if (saved) {
      try {
        return { ...defaultSettings, ...JSON.parse(saved) };
      } catch {
        return defaultSettings;
      }
    }
    return defaultSettings;
  });

  // Save to localStorage whenever settings change
  useEffect(() => {
    localStorage.setItem('accessibility-settings', JSON.stringify(settings));
  }, [settings]);

  // Apply CSS classes based on settings
  useEffect(() => {
    const root = document.documentElement;
    
    // Font size
    root.className = root.className.replace(/font-size-\w+/g, '');
    root.classList.add(`font-size-${settings.fontSize}`);
    
    // High contrast
    if (settings.contrast === 'high') {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    
    // Reduced motion
    if (settings.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }
    
    // Screen reader optimized
    if (settings.screenReaderOptimized) {
      root.classList.add('screen-reader-optimized');
    } else {
      root.classList.remove('screen-reader-optimized');
    }
  }, [settings]);

  // Detect user preferences
  useEffect(() => {
    // Check for prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion && !settings.reducedMotion) {
      updateSettings({ reducedMotion: true });
    }

    // Check for prefers-contrast
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
    if (prefersHighContrast && settings.contrast === 'normal') {
      updateSettings({ contrast: 'high' });
    }
  }, []);

  const updateSettings = (newSettings: Partial<AccessibilitySettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  const increaseFontSize = () => {
    const sizes: AccessibilitySettings['fontSize'][] = ['small', 'medium', 'large', 'extra-large'];
    const currentIndex = sizes.indexOf(settings.fontSize);
    if (currentIndex < sizes.length - 1) {
      updateSettings({ fontSize: sizes[currentIndex + 1] });
    }
  };

  const decreaseFontSize = () => {
    const sizes: AccessibilitySettings['fontSize'][] = ['small', 'medium', 'large', 'extra-large'];
    const currentIndex = sizes.indexOf(settings.fontSize);
    if (currentIndex > 0) {
      updateSettings({ fontSize: sizes[currentIndex - 1] });
    }
  };

  const toggleHighContrast = () => {
    updateSettings({ 
      contrast: settings.contrast === 'normal' ? 'high' : 'normal' 
    });
  };

  const toggleReducedMotion = () => {
    updateSettings({ reducedMotion: !settings.reducedMotion });
  };

  const toggleScreenReaderMode = () => {
    updateSettings({ screenReaderOptimized: !settings.screenReaderOptimized });
  };

  const setLanguage = (language: string) => {
    updateSettings({ language });
    document.documentElement.lang = language;
  };

  const addCulturalPreference = (preference: string) => {
    if (!settings.culturalPreferences.includes(preference)) {
      updateSettings({ 
        culturalPreferences: [...settings.culturalPreferences, preference] 
      });
    }
  };

  const removeCulturalPreference = (preference: string) => {
    updateSettings({ 
      culturalPreferences: settings.culturalPreferences.filter(p => p !== preference) 
    });
  };

  const value: AccessibilityContextType = {
    settings,
    updateSettings,
    increaseFontSize,
    decreaseFontSize,
    toggleHighContrast,
    toggleReducedMotion,
    toggleScreenReaderMode,
    setLanguage,
    addCulturalPreference,
    removeCulturalPreference
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

// Cultural context data
export const CULTURAL_CONTEXTS = [
  { id: 'western', name: 'Western', description: 'European and North American dietary patterns' },
  { id: 'mediterranean', name: 'Mediterranean', description: 'Traditional Mediterranean diet' },
  { id: 'asian', name: 'Asian', description: 'East Asian dietary traditions' },
  { id: 'south_asian', name: 'South Asian', description: 'Indian subcontinent dietary patterns' },
  { id: 'middle_eastern', name: 'Middle Eastern', description: 'Middle Eastern and North African cuisine' },
  { id: 'latin_american', name: 'Latin American', description: 'Central and South American dietary traditions' },
  { id: 'african', name: 'African', description: 'Sub-Saharan African dietary patterns' },
  { id: 'indigenous', name: 'Indigenous', description: 'Native and traditional dietary practices' }
];

export const LANGUAGE_OPTIONS = [
  { code: 'en', name: 'English', native: 'English' },
  { code: 'es', name: 'Spanish', native: 'Español' },
  { code: 'fr', name: 'French', native: 'Français' },
  { code: 'de', name: 'German', native: 'Deutsch' },
  { code: 'zh', name: 'Chinese', native: '中文' },
  { code: 'ja', name: 'Japanese', native: '日本語' },
  { code: 'ko', name: 'Korean', native: '한국어' },
  { code: 'ar', name: 'Arabic', native: 'العربية' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'pt', name: 'Portuguese', native: 'Português' }
];
