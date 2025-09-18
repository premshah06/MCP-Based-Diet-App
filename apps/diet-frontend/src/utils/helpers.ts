import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility for combining Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format numbers with proper precision
export const formatNumber = (value: number, precision: number = 1): string => {
  return value.toFixed(precision);
};

// Format calories with proper units
export const formatCalories = (calories: number): string => {
  return `${formatNumber(calories, 0)} kcal`;
};

// Format macros with units
export const formatMacro = (grams: number, unit: string = 'g'): string => {
  return `${formatNumber(grams)}${unit}`;
};

// Format weight with proper units
export const formatWeight = (kg: number, unit: 'kg' | 'lbs' = 'kg'): string => {
  if (unit === 'lbs') {
    return `${formatNumber(kg * 2.20462)} lbs`;
  }
  return `${formatNumber(kg)} kg`;
};

// Format height with proper units
export const formatHeight = (cm: number, unit: 'cm' | 'ft' = 'cm'): string => {
  if (unit === 'ft') {
    const totalInches = cm / 2.54;
    const feet = Math.floor(totalInches / 12);
    const inches = Math.round(totalInches % 12);
    return `${feet}'${inches}"`;
  }
  return `${formatNumber(cm, 0)} cm`;
};

// Calculate BMI
export const calculateBMI = (weightKg: number, heightCm: number): number => {
  const heightM = heightCm / 100;
  return weightKg / (heightM * heightM);
};

// Get BMI category
export const getBMICategory = (bmi: number): { category: string; color: string } => {
  if (bmi < 18.5) return { category: 'Underweight', color: 'text-blue-600' };
  if (bmi < 25) return { category: 'Normal weight', color: 'text-green-600' };
  if (bmi < 30) return { category: 'Overweight', color: 'text-yellow-600' };
  return { category: 'Obese', color: 'text-red-600' };
};

// Calculate macro percentages
export const calculateMacroPercentages = (
  protein: number,
  fat: number,
  carbs: number,
  totalCalories: number
) => {
  const proteinCals = protein * 4;
  const fatCals = fat * 9;
  const carbsCals = carbs * 4;
  
  return {
    protein: Math.round((proteinCals / totalCalories) * 100),
    fat: Math.round((fatCals / totalCalories) * 100),
    carbs: Math.round((carbsCals / totalCalories) * 100),
  };
};

// Validate form data
export const validateAge = (age: number): boolean => age >= 10 && age <= 120;
export const validateHeight = (height: number): boolean => height >= 100 && height <= 250;
export const validateWeight = (weight: number): boolean => weight >= 30 && weight <= 300;

// Format time ago
export const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  
  return date.toLocaleDateString();
};

// Local storage utilities
export const storage = {
  get: <T>(key: string): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Silently fail if storage is not available
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch {
      // Silently fail if storage is not available
    }
  }
};

// Debounce function for performance
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: number;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = window.setTimeout(() => func.apply(null, args), wait);
  };
};

// Generate random ID
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

// Copy to clipboard
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return true;
  }
};

// Download data as JSON file
export const downloadJSON = (data: any, filename: string): void => {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.json`;
  link.click();
  URL.revokeObjectURL(url);
};

// Get contrast color for text readability
export const getContrastColor = (hexColor: string): string => {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness > 128 ? '#000000' : '#ffffff';
};
