import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

// Components
import Layout from '@/components/Layout';
import HomePage from '@/pages/HomePage';
import ProfilePage from '@/pages/ProfilePage';
import ResultsPage from '@/pages/ResultsPage';
import MealPlanPage from '@/pages/MealPlanPage';
import AboutPage from '@/pages/AboutPage';

// Hooks and utilities
import { useTheme } from '@/hooks/useTheme';
import { storage } from '@/utils/helpers';
import { STORAGE_KEYS } from '@/utils/constants';
import { dietAPI } from '@/services/api';

// Types
import type { UserProfile, NutritionResults, AppState } from '@/types/api';

function App() {
  // Theme management
  const { theme, setTheme } = useTheme();

  // Application state
  const [state, setState] = useState<AppState>({
    theme,
    user: null,
    nutrition: null,
    loading: false,
    error: null,
  });

  // Load saved user profile on mount
  useEffect(() => {
    const savedProfile = storage.get<UserProfile>(STORAGE_KEYS.userProfile);
    if (savedProfile) {
      setState(prev => ({ ...prev, user: savedProfile }));
    }

    // Test API connection
    const testConnection = async () => {
      try {
        await dietAPI.health();
        console.log('✅ API connection successful');
      } catch (error) {
        console.warn('⚠️ API connection failed:', error);
        toast.error('Could not connect to the nutrition service. Some features may be limited.');
      }
    };

    testConnection();
  }, []);

  // Update theme when it changes
  useEffect(() => {
    setState(prev => ({ ...prev, theme }));
  }, [theme]);

  // Save user profile when it changes
  useEffect(() => {
    if (state.user) {
      storage.set(STORAGE_KEYS.userProfile, state.user);
    }
  }, [state.user]);

  // Update user profile
  const updateUserProfile = (profile: UserProfile) => {
    setState(prev => ({ ...prev, user: profile }));
  };

  // Update nutrition results
  const updateNutritionResults = (nutrition: NutritionResults) => {
    setState(prev => ({ ...prev, nutrition }));
  };

  // Set loading state
  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  };

  // Set error state
  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
    if (error) {
      toast.error(error);
    }
  };

  // Clear all data
  const clearData = () => {
    setState(prev => ({
      ...prev,
      user: null,
      nutrition: null,
      error: null,
    }));
    storage.remove(STORAGE_KEYS.userProfile);
    toast.success('Data cleared successfully');
  };

  // App context value
  const appContext = {
    ...state,
    updateUserProfile,
    updateNutritionResults,
    setLoading,
    setError,
    clearData,
    setTheme,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      <AnimatePresence mode="wait">
        <motion.div
          key={theme}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="min-h-screen"
        >
          <Layout context={appContext}>
            <Routes>
              {/* Home page */}
              <Route 
                path="/" 
                element={<HomePage context={appContext} />} 
              />
              
              {/* Profile setup */}
              <Route 
                path="/profile" 
                element={<ProfilePage context={appContext} />} 
              />
              
              {/* Nutrition results */}
              <Route 
                path="/results" 
                element={
                  state.nutrition ? (
                    <ResultsPage context={appContext} />
                  ) : (
                    <Navigate to="/profile" replace />
                  )
                } 
              />
              
              {/* Meal plan */}
              <Route 
                path="/meal-plan" 
                element={
                  state.nutrition ? (
                    <MealPlanPage context={appContext} />
                  ) : (
                    <Navigate to="/profile" replace />
                  )
                } 
              />
              
              {/* About page */}
              <Route 
                path="/about" 
                element={<AboutPage context={appContext} />} 
              />
              
              {/* Catch-all redirect */}
              <Route 
                path="*" 
                element={<Navigate to="/" replace />} 
              />
            </Routes>
          </Layout>
        </motion.div>
      </AnimatePresence>

      {/* Global loading overlay */}
      <AnimatePresence>
        {state.loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl flex flex-col items-center space-y-4"
            >
              <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
              <p className="text-gray-600 dark:text-gray-300 font-medium">
                Calculating your nutrition plan...
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Development mode indicator */}
      {import.meta.env?.DEV && (
        <div className="fixed bottom-4 left-4 z-40 bg-yellow-400 text-yellow-900 px-2 py-1 rounded text-xs font-mono">
          DEV
        </div>
      )}
    </div>
  );
}

export default App;
