import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Home, 
  User, 
  BarChart3, 
  UtensilsCrossed, 
  Info, 
  Sun, 
  Moon, 
  Monitor,
  Menu,
  X
} from 'lucide-react';
import { cn } from '@/utils/helpers';
import type { AppState, Theme } from '@/types/api';

interface LayoutProps {
  children: React.ReactNode;
  context: AppState & {
    setTheme: (theme: Theme) => void;
    clearData: () => void;
  };
}

export default function Layout({ children, context }: LayoutProps) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const navigation = [
    { name: 'Home', href: '/', icon: Home, current: location.pathname === '/' },
    { name: 'Profile', href: '/profile', icon: User, current: location.pathname === '/profile' },
    { 
      name: 'Results', 
      href: '/results', 
      icon: BarChart3, 
      current: location.pathname === '/results',
      disabled: !context.nutrition
    },
    { 
      name: 'Meal Plan', 
      href: '/meal-plan', 
      icon: UtensilsCrossed, 
      current: location.pathname === '/meal-plan',
      disabled: !context.nutrition
    },
    { name: 'About', href: '/about', icon: Info, current: location.pathname === '/about' },
  ];

  const themeOptions = [
    { value: 'light' as Theme, label: 'Light', icon: Sun },
    { value: 'dark' as Theme, label: 'Dark', icon: Moon },
    { value: 'system' as Theme, label: 'System', icon: Monitor },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2 group">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center"
              >
                <UtensilsCrossed className="w-5 h-5 text-white" />
              </motion.div>
              <span className="text-xl font-bold font-display bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                Diet Coach
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2',
                      item.current
                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                        : item.disabled
                        ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
                    )}
                    onClick={(e) => {
                      if (item.disabled) {
                        e.preventDefault();
                      }
                    }}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Theme Switcher & Mobile Menu */}
            <div className="flex items-center space-x-2">
              {/* Theme Switcher */}
              <div className="relative">
                <select
                  value={context.theme}
                  onChange={(e) => context.setTheme(e.target.value as Theme)}
                  className="appearance-none bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {themeOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                  {themeOptions.find(o => o.value === context.theme)?.icon && (
                    React.createElement(themeOptions.find(o => o.value === context.theme)!.icon, {
                      className: "w-4 h-4 text-gray-500"
                    })
                  )}
                </div>
              </div>

              {/* Mobile menu button */}
              <button
                type="button"
                className="md:hidden p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900"
          >
            <div className="px-4 py-2 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center space-x-3 px-3 py-2 rounded-lg text-base font-medium transition-colors',
                      item.current
                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300'
                        : item.disabled
                        ? 'text-gray-400 dark:text-gray-600 cursor-not-allowed'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )}
                    onClick={(e) => {
                      if (item.disabled) {
                        e.preventDefault();
                      } else {
                        setMobileMenuOpen(false);
                      }
                    }}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              © 2024 Diet Coach. Powered by AI nutrition science.
            </div>
            <div className="flex items-center space-x-4">
              {context.user && (
                <button
                  onClick={context.clearData}
                  className="text-sm text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                >
                  Clear Data
                </button>
              )}
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {context.user ? `Welcome, ${context.user.sex === 'male' ? '👨' : '👩'}` : 'Ready to start?'}
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
