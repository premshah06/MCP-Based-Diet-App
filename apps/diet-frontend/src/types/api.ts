// API Request Types
export interface TDEERequest {
  sex: 'male' | 'female';
  age: number;
  height_cm: number;
  weight_kg: number;
  activity_level: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
  goal: 'cut' | 'maintain' | 'bulk';
}

export interface MealPlanRequest {
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  diet_tags: string[];
  days: number;
}

export interface ExplainRequest {
  calories: number;
  protein_g?: number;
  fat_g?: number;
  carbs_g?: number;
  constraints?: string;
  diet_tags?: string[];
}

// API Response Types
export interface TDEEResponse {
  tdee: number;
  target_calories: number;
  macro_targets: {
    protein_g: number;
    fat_g: number;
    carbs_g: number;
  };
  bmr: number;
  activity_factor: number;
}

export interface FoodItem {
  name: string;
  amount_g: number;
  calories: number;
  protein: number;
  fat: number;
  carbs: number;
}

export interface Meal {
  name: string;
  foods: FoodItem[];
  totals: {
    calories: number;
    protein: number;
    fat: number;
    carbs: number;
  };
}

export interface DayPlan {
  day: number;
  meals: Meal[];
  daily_totals: {
    calories: number;
    protein: number;
    fat: number;
    carbs: number;
  };
}

export interface MealPlanResponse {
  days: DayPlan[];
  plan_totals: {
    calories: number;
    protein: number;
    fat: number;
    carbs: number;
    avg_daily_calories: number;
  };
  adherence_score: number;
}

export interface ExplainResponse {
  explanation: string;
}

// UI State Types
export interface UserProfile {
  sex: 'male' | 'female';
  age: number;
  height_cm: number;
  weight_kg: number;
  activity_level: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
  goal: 'cut' | 'maintain' | 'bulk';
  diet_preferences: string[];
}

export interface NutritionResults {
  tdee: TDEEResponse;
  mealPlan?: MealPlanResponse;
  explanation?: string;
}

// Form Types
export interface ProfileFormData extends UserProfile {}

export interface MealPlanFormData {
  days: number;
  diet_tags: string[];
}

// Theme & UI Types
export type Theme = 'light' | 'dark' | 'system';

export interface AppState {
  theme: Theme;
  user: UserProfile | null;
  nutrition: NutritionResults | null;
  loading: boolean;
  error: string | null;
}
