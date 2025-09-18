// Activity level options with descriptions
export const ACTIVITY_LEVELS = [
  {
    value: 'sedentary',
    label: 'Sedentary',
    description: 'Little to no exercise',
    factor: 1.2,
    icon: '🪑'
  },
  {
    value: 'light',
    label: 'Light Activity',
    description: 'Light exercise 1-3 days/week',
    factor: 1.375,
    icon: '🚶'
  },
  {
    value: 'moderate',
    label: 'Moderate Activity',
    description: 'Moderate exercise 3-5 days/week',
    factor: 1.55,
    icon: '🏃'
  },
  {
    value: 'active',
    label: 'Active',
    description: 'Hard exercise 6-7 days/week',
    factor: 1.725,
    icon: '🏋️'
  },
  {
    value: 'very_active',
    label: 'Very Active',
    description: 'Very hard exercise, physical job',
    factor: 1.9,
    icon: '💪'
  }
] as const;

// Goal options with descriptions
export const GOALS = [
  {
    value: 'cut',
    label: 'Weight Loss',
    description: 'Lose weight with a caloric deficit',
    adjustment: -0.20,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    icon: '📉'
  },
  {
    value: 'maintain',
    label: 'Maintain Weight',
    description: 'Maintain current weight',
    adjustment: 0.0,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    icon: '⚖️'
  },
  {
    value: 'bulk',
    label: 'Weight Gain',
    description: 'Gain weight with a caloric surplus',
    adjustment: 0.15,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    icon: '📈'
  }
] as const;

// Dietary preferences/restrictions
export const DIET_TAGS = [
  {
    value: 'veg',
    label: 'Vegetarian',
    description: 'No meat, fish, or poultry',
    icon: '🥬',
    color: 'bg-green-100 text-green-800'
  },
  {
    value: 'non_veg',
    label: 'Non-Vegetarian',
    description: 'Includes meat, fish, and poultry',
    icon: '🍖',
    color: 'bg-red-100 text-red-800'
  },
  {
    value: 'vegan',
    label: 'Vegan',
    description: 'No animal products',
    icon: '🌱',
    color: 'bg-emerald-100 text-emerald-800'
  },
  {
    value: 'halal',
    label: 'Halal',
    description: 'Halal dietary requirements',
    icon: '☪️',
    color: 'bg-blue-100 text-blue-800'
  },
  {
    value: 'lactose_free',
    label: 'Lactose Free',
    description: 'No dairy products',
    icon: '🥛',
    color: 'bg-yellow-100 text-yellow-800'
  },
  {
    value: 'budget',
    label: 'Budget Friendly',
    description: 'Cost-effective food choices',
    icon: '💰',
    color: 'bg-purple-100 text-purple-800'
  }
] as const;

// Form validation constants
export const VALIDATION = {
  age: { min: 10, max: 120 },
  height: { min: 100, max: 250 },
  weight: { min: 30, max: 300 },
  days: { min: 1, max: 14 },
} as const;

// Macro color schemes for charts
export const MACRO_COLORS = {
  protein: {
    primary: '#ef4444',
    light: '#fee2e2',
    dark: '#991b1b'
  },
  fat: {
    primary: '#f59e0b',
    light: '#fef3c7',
    dark: '#92400e'
  },
  carbs: {
    primary: '#10b981',
    light: '#d1fae5',
    dark: '#047857'
  }
} as const;

// App configuration
export const APP_CONFIG = {
  name: 'Diet Coach',
  description: 'AI-powered nutrition and meal planning assistant',
  version: '1.0.0',
  author: 'Diet Coach Team',
  social: {
    twitter: '@dietcoach',
    github: 'https://github.com/dietcoach'
  }
} as const;

// Breakpoints for responsive design
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
} as const;

// Animation durations
export const ANIMATION = {
  fast: 0.15,
  normal: 0.3,
  slow: 0.5,
  verySlow: 1.0
} as const;

// Local storage keys
export const STORAGE_KEYS = {
  theme: 'diet-coach-theme',
  userProfile: 'diet-coach-profile',
  preferences: 'diet-coach-preferences'
} as const;
