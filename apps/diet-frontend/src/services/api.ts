/**
 * Diet Coach API Service
 * Handles all API communication with the backend
 */

import type {
  TDEERequest,
  TDEEResponse,
  MealPlanRequest,
  MealPlanResponse,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  AuthUser,
  AuthTokens,
  ChatRequest,
  ChatResponse,
  GroceryListRequest,
  GroceryListResponse,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token storage keys
const ACCESS_TOKEN_KEY = 'diet_access_token';
const REFRESH_TOKEN_KEY = 'diet_refresh_token';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Token management
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  setTokens(tokens: AuthTokens): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  }

  clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getAccessToken();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Try to refresh token
      const refreshed = await this.refreshTokens();
      if (refreshed) {
        // Retry the request with new token
        const newToken = this.getAccessToken();
        (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
        const retryResponse = await fetch(url, { ...options, headers });
        if (!retryResponse.ok) {
          throw new Error(await retryResponse.text());
        }
        return retryResponse.json();
      }
      this.clearTokens();
      throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async health(): Promise<any> {
    return this.request('/health');
  }

  // ============================================================================
  // AUTHENTICATION
  // ============================================================================

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setTokens(response.tokens);
    return response;
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setTokens(response.tokens);
    return response;
  }

  async logout(): Promise<void> {
    this.clearTokens();
  }

  async refreshTokens(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      this.setTokens(data.tokens);
      return true;
    } catch {
      return false;
    }
  }

  async getCurrentUser(): Promise<AuthUser> {
    return this.request<AuthUser>('/auth/me');
  }

  async updateProfile(profile: Record<string, any>): Promise<{ user: AuthUser; message: string }> {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify({ profile }),
    });
  }

  async updatePreferences(preferences: Record<string, any>): Promise<{ user: AuthUser; message: string }> {
    return this.request('/auth/preferences', {
      method: 'PUT',
      body: JSON.stringify({ preferences }),
    });
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  }

  // ============================================================================
  // NUTRITION ENDPOINTS
  // ============================================================================

  async calculateTDEE(data: TDEERequest): Promise<TDEEResponse> {
    return this.request<TDEEResponse>('/tdee', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateMealPlan(data: MealPlanRequest): Promise<MealPlanResponse> {
    return this.request<MealPlanResponse>('/mealplan', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async explainNutrition(params: {
    calories: number;
    protein_g?: number;
    fat_g?: number;
    carbs_g?: number;
    constraints?: string;
    diet_tags?: string[];
  }): Promise<{ explanation: string }> {
    const queryParams = new URLSearchParams();
    queryParams.append('calories', params.calories.toString());
    if (params.protein_g) queryParams.append('protein_g', params.protein_g.toString());
    if (params.fat_g) queryParams.append('fat_g', params.fat_g.toString());
    if (params.carbs_g) queryParams.append('carbs_g', params.carbs_g.toString());
    if (params.constraints) queryParams.append('constraints', params.constraints);
    if (params.diet_tags) {
      params.diet_tags.forEach(tag => queryParams.append('diet_tags', tag));
    }

    return this.request(`/explain?${queryParams.toString()}`);
  }

  async getDietOptions(): Promise<{ diet_options: any[] }> {
    return this.request('/diet-options');
  }

  // ============================================================================
  // AI CHAT
  // ============================================================================

  async chat(data: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/ai/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getChatHistory(): Promise<{ history: any[] }> {
    return this.request<{ history: any[] }>('/ai/chat/history');
  }

  async clearChatHistory(): Promise<{ success: boolean; message: string }> {
    return this.request('/ai/chat/clear', {
      method: 'POST',
    });
  }

  async getAIStatus(): Promise<{
    providers: Array<{ name: string; status: string; model: string }>;
    default_provider: string;
    fallback_available: boolean;
  }> {
    return this.request('/ai/status');
  }

  // ============================================================================
  // GROCERY LIST
  // ============================================================================

  async generateGroceryList(data: GroceryListRequest): Promise<GroceryListResponse> {
    return this.request<GroceryListResponse>('/ai/grocery-list', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateRecipe(data: { meal: any; context?: any; provider?: string }): Promise<any> {
    return this.request('/ai/recipe', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // ============================================================================
  // EXPORT
  // ============================================================================

  async exportToExcel(data: {
    user_profile: any;
    nutrition_targets: any;
    meal_plan: any;
    explanation?: string;
  }): Promise<{
    success: boolean;
    filename: string;
    excel_data: string;
  }> {
    return this.request('/export/excel', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Transform user profile data into TDEE request format
 */
export const transformUserProfileToTDEE = (profile: any): TDEERequest => {
  return {
    sex: profile.sex,
    age: Number(profile.age),
    height_cm: Number(profile.height_cm),
    weight_kg: Number(profile.weight_kg),
    activity_level: profile.activity_level,
    goal: profile.goal,
  };
};

/**
 * Transform TDEE response into Meal Plan request format
 */
export const transformTDEEToMealPlan = (
  tdee: TDEEResponse,
  options: { days: number; diet_tags: string[] }
): MealPlanRequest => {
  return {
    calories: tdee.target_calories,
    protein_g: tdee.macro_targets.protein_g,
    fat_g: tdee.macro_targets.fat_g,
    carbs_g: tdee.macro_targets.carbs_g,
    diet_tags: options.diet_tags,
    days: options.days,
  };
};

// Export singleton instance
export const dietAPI = new ApiService();
export default dietAPI;
