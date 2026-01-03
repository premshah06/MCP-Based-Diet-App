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

// Authentication Types
export interface AuthUser {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  profile: UserProfile | null;
  preferences: UserPreferences | null;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  diet_tags: string[];
  notifications: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: AuthUser;
  tokens: AuthTokens;
  message: string;
}

// AI Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  provider?: string;
  image_data?: string; // Base64 encoding of image sent by user
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
  image_data?: string; // Base64 encoded image
}

export interface ChatResponse {
  success: boolean;
  response: string;
  provider: string;
  model: string;
  tokens_used?: number;
}

// Grocery List Types
export interface GroceryItem {
  name: string;
  quantity: string;
  unit: string;
  notes?: string;
  estimated_price?: string;
}

export interface GroceryCategory {
  name: string;
  icon: string;
  items: GroceryItem[];
}

export interface GroceryList {
  categories: GroceryCategory[];
  total_items: number;
  shopping_tips: string[];
  estimated_total?: string;
}

export interface GroceryListRequest {
  meal_plan: MealPlanResponse;
  preferences?: {
    budget?: string;
    store?: string;
    dietary_restrictions?: string[];
  };
  provider?: string;
}

export interface GroceryListResponse {
  success: boolean;
  grocery_list: GroceryList;
  provider: string;
  generated_at: string;
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
export interface ProfileFormData extends UserProfile { }

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
  authUser: AuthUser | null;
  isAuthenticated: boolean;

  // Methods
  updateUserProfile: (profile: UserProfile) => void;
  updateNutritionResults: (nutrition: NutritionResults) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearData: () => void;
  setTheme: (theme: Theme) => void;
  openChat: () => void;
  openGroceryList: () => void;
  openRecipe: (meal: any) => void;
}
