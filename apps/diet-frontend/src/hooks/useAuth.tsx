/**
 * Authentication Hook and Context
 * Manages user authentication state across the app
 */

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { dietAPI } from '@/services/api';
import type { AuthUser, LoginRequest, RegisterRequest } from '@/types/api';

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateProfile: (profile: Record<string, any>) => Promise<void>;
  updatePreferences: (preferences: Record<string, any>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = dietAPI.getAccessToken();
      if (token) {
        try {
          const userData = await dietAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.warn('Session expired or invalid');
          dietAPI.clearTokens();
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    const response = await dietAPI.login(data);
    setUser(response.user);
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    const response = await dietAPI.register(data);
    setUser(response.user);
  }, []);

  const logout = useCallback(() => {
    dietAPI.logout();
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (profile: Record<string, any>) => {
    const response = await dietAPI.updateProfile(profile);
    setUser(response.user);
  }, []);

  const updatePreferences = useCallback(async (preferences: Record<string, any>) => {
    const response = await dietAPI.updatePreferences(preferences);
    setUser(response.user);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await dietAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
        updatePreferences,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default useAuth;
