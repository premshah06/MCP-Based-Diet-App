import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import App from './App';
import './index.css';

// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Application Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="text-center p-8">
            <div className="mb-4 text-6xl">😵</div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Oops! Something went wrong
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              We're sorry, but something unexpected happened.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Reload Page
            </button>
            {import.meta.env?.DEV && this.state.error && (
              <details className="mt-4 text-left">
                <summary className="cursor-pointer text-sm text-gray-500">
                  Error Details (Development)
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-auto">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Toast configuration
const toastOptions = {
  duration: 4000,
  position: 'top-right' as const,
  style: {
    background: 'var(--toast-bg)',
    color: 'var(--toast-color)',
    borderRadius: '12px',
    border: '1px solid var(--toast-border)',
    backdropFilter: 'blur(8px)',
  },
  success: {
    iconTheme: {
      primary: '#10b981',
      secondary: '#ffffff',
    },
  },
  error: {
    iconTheme: {
      primary: '#ef4444',
      secondary: '#ffffff',
    },
  },
};

// Root element check
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

// Render the application
ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
        <Toaster toastOptions={toastOptions} />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);

// Service worker registration for PWA
if ('serviceWorker' in navigator && import.meta.env?.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Theme detection and CSS custom properties
const updateThemeVars = () => {
  const isDark = document.documentElement.classList.contains('dark');
  const root = document.documentElement;
  
  if (isDark) {
    root.style.setProperty('--toast-bg', 'rgba(31, 41, 55, 0.9)');
    root.style.setProperty('--toast-color', 'rgb(243, 244, 246)');
    root.style.setProperty('--toast-border', 'rgba(75, 85, 99, 0.3)');
  } else {
    root.style.setProperty('--toast-bg', 'rgba(255, 255, 255, 0.9)');
    root.style.setProperty('--toast-color', 'rgb(17, 24, 39)');
    root.style.setProperty('--toast-border', 'rgba(209, 213, 219, 0.3)');
  }
};

// Initial theme setup
updateThemeVars();

// Watch for theme changes
const observer = new MutationObserver(updateThemeVars);
observer.observe(document.documentElement, {
  attributes: true,
  attributeFilter: ['class'],
});

// Performance monitoring (development only)
if (import.meta.env?.DEV) {
  // Log render performance
  const logPerformance = () => {
    if ('performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      console.log('Page Load Performance:', {
        domContentLoaded: Math.round(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart),
        loadComplete: Math.round(navigation.loadEventEnd - navigation.loadEventStart),
        totalTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
      });
    }
  };

  window.addEventListener('load', logPerformance);
}
