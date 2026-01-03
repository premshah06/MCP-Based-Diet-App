import { useState, useEffect } from 'react';
import { storage } from '@/utils/helpers';
import { STORAGE_KEYS } from '@/utils/constants';
import type { Theme } from '@/types/api';

export function useTheme() {
  // Initialize theme from localStorage or system preference
  const getInitialTheme = (): Theme => {
    const stored = storage.get<Theme>(STORAGE_KEYS.theme);
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      return stored;
    }
    return 'system';
  };

  const [theme, setThemeState] = useState<Theme>(getInitialTheme);

  // Get the actual theme to apply (resolve 'system' to 'light' or 'dark')
  const getResolvedTheme = (theme: Theme): 'light' | 'dark' => {
    if (theme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return theme;
  };

  // Apply theme to document
  const applyTheme = (resolvedTheme: 'light' | 'dark') => {
    const root = document.documentElement;
    
    if (resolvedTheme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute(
        'content',
        resolvedTheme === 'dark' ? '#0f172a' : '#10b981'
      );
    }
  };

  // Set theme and persist to localStorage
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    storage.set(STORAGE_KEYS.theme, newTheme);
  };

  // Effect to apply theme changes
  useEffect(() => {
    const resolvedTheme = getResolvedTheme(theme);
    applyTheme(resolvedTheme);
  }, [theme]);

  // Effect to listen for system theme changes when using 'system' theme
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      applyTheme(e.matches ? 'dark' : 'light');
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleSystemThemeChange);
      return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
    } 
    // Legacy browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleSystemThemeChange);
      return () => mediaQuery.removeListener(handleSystemThemeChange);
    }
  }, [theme]);

  // Get current resolved theme for UI display
  const currentTheme = getResolvedTheme(theme);

  return {
    theme,
    currentTheme,
    setTheme,
    isDark: currentTheme === 'dark',
    isLight: currentTheme === 'light',
    isSystem: theme === 'system',
  };
}
