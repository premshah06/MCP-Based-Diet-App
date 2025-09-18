import axios from 'axios';
import type {
  TDEERequest,
  TDEEResponse,
  MealPlanRequest,
  MealPlanResponse,
  ExplainRequest,
  ExplainResponse,
} from '@/types/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use((config) => {
  console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    
    // Transform API errors to user-friendly messages
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail;
      if (Array.isArray(detail)) {
        const messages = detail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`);
        throw new Error(`Validation Error: ${messages.join(', ')}`);
      }
      throw new Error(`Validation Error: ${detail || 'Invalid input data'}`);
    }
    
    if (error.response?.status === 500) {
      throw new Error('Server error occurred. Please try again later.');
    }
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.');
    }
    
    if (!error.response) {
      throw new Error('Network error. Please check your connection.');
    }
    
    throw new Error(error.response?.data?.detail || error.message || 'An error occurred');
  }
);

// API Methods
export const dietAPI = {
  // Health check
  async health(): Promise<{ status: string; service: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Calculate TDEE and macro targets
  async calculateTDEE(data: TDEERequest): Promise<TDEEResponse> {
    const response = await api.post('/tdee', data);
    return response.data;
  },

  // Generate meal plan
  async generateMealPlan(data: MealPlanRequest): Promise<MealPlanResponse> {
    const response = await api.post('/mealplan', data);
    return response.data;
  },

  // Get nutrition explanation
  async explainNutrition(data: ExplainRequest): Promise<ExplainResponse> {
    const params = new URLSearchParams();
    params.append('calories', data.calories.toString());
    if (data.protein_g) params.append('protein_g', data.protein_g.toString());
    if (data.fat_g) params.append('fat_g', data.fat_g.toString());
    if (data.carbs_g) params.append('carbs_g', data.carbs_g.toString());
    if (data.constraints) params.append('constraints', data.constraints);

    const response = await api.get(`/explain?${params.toString()}`);
    return response.data;
  },

  // Get available diet options
  async getDietOptions(): Promise<{ diet_options: Array<{
    value: string;
    label: string;
    description: string;
    icon: string;
    examples: string[];
  }> }> {
    const response = await api.get('/diet-options');
    return response.data;
  },
};

// Helper functions for data transformation
export const transformUserProfileToTDEE = (profile: any): TDEERequest => ({
  sex: profile.sex,
  age: profile.age,
  height_cm: profile.height_cm,
  weight_kg: profile.weight_kg,
  activity_level: profile.activity_level,
  goal: profile.goal,
});

export const transformTDEEToMealPlan = (
  tdee: TDEEResponse,
  preferences: { days: number; diet_tags: string[] }
): MealPlanRequest => ({
  calories: tdee.target_calories,
  protein_g: tdee.macro_targets.protein_g,
  fat_g: tdee.macro_targets.fat_g,
  carbs_g: tdee.macro_targets.carbs_g,
  days: preferences.days,
  diet_tags: preferences.diet_tags,
});

// Utility functions
export const formatMacroPercentage = (macroGrams: number, totalCalories: number, caloriesPerGram: number): number => {
  return Math.round((macroGrams * caloriesPerGram / totalCalories) * 100);
};

export const calculateMacroPercentages = (protein: number, fat: number, carbs: number, calories: number) => ({
  protein: formatMacroPercentage(protein, calories, 4),
  fat: formatMacroPercentage(fat, calories, 9),
  carbs: formatMacroPercentage(carbs, calories, 4),
});

export default api;
