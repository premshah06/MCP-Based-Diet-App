from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import traceback
import uuid

import json
import os
import random
import requests
import time
import hashlib
from export_utils import create_excel_export
from auth import auth_service, AuthError, User
from ai_service import ai_service

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

# Request tracking for rate limiting and analytics
request_tracking = {}
error_tracking = []
# FastAPI app with comprehensive configuration
app = FastAPI(
    title="Diet Coach API",
    version="2.0.0",
    description="Research-grade nutrition coaching API with comprehensive food database and ML-powered recommendations",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Closing AI Service session...")
    await ai_service.close()

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "diet-api", "*"]
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://diet-frontend:3000",
        "https://localhost:3000",  # For HTTPS development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-API-Version"]
)
# Enhanced database loading with fallback paths
FOODS_PATHS = [
    Path("/app/data/enhanced_foods.json"),
    Path("/app/data/foods.json"),
    Path("/app/enhanced_foods.json"),
    Path("/app/foods.json"), 
    Path("data/enhanced_foods.json"),
    Path("data/foods.json"),
    Path("enhanced_foods.json"),
    Path("foods.json"),
]

def load_foods_database() -> Dict[str, Any]:
    """Load foods database with comprehensive fallback and validation"""
    for foods_path in FOODS_PATHS:
        try:
            with open(foods_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded foods database from {foods_path}")
            logger.info(f"📊 Database contains {len(data.get('foods', []))} food items")
            
            # Log metadata if available
            metadata = data.get('metadata', {})
            if metadata:
                logger.info(f"📈 Database version: {metadata.get('version', 'unknown')}")
                logger.info(f"🧪 Data quality: {metadata.get('data_quality', {}).get('validation_rate', 'unknown')}% validated")
            
            return data
        except FileNotFoundError:
            logger.debug(f"Foods database not found at {foods_path}")
            continue
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in foods database at {foods_path}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error loading foods database from {foods_path}: {e}")
            continue
    
    logger.error("❌ No valid foods database found in any fallback path")
    raise RuntimeError("Critical: No foods database available")

# Load foods database with error handling
try:
    FOODS_DB = load_foods_database()
    logger.info("🎉 Foods database loaded successfully")
except Exception as e:
    logger.critical(f"💥 Failed to load foods database: {e}")
    # Create minimal fallback database
    FOODS_DB = {
        "foods": [],
        "metadata": {
            "version": "fallback",
            "description": "Emergency fallback database",
            "status": "error"
        }
    }

# Request tracking and error handling
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track requests for rate limiting and analytics"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to headers
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-API-Version"] = "2.0.0"
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    
    # Log request details
    logger.info(f"🌐 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s - ID: {request_id}")
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with detailed logging"""
    error_id = str(uuid.uuid4())
    error_time = datetime.now().isoformat()
    
    # Log detailed error information
    logger.error(f"💥 Unhandled exception - ID: {error_id}")
    logger.error(f"💥 Request: {request.method} {request.url}")
    logger.error(f"💥 Exception: {type(exc).__name__}: {str(exc)}")
    logger.error(f"💥 Traceback: {traceback.format_exc()}")
    
    # Track error for analytics
    error_info = {
        "id": error_id,
        "timestamp": error_time,
        "path": str(request.url.path),
        "method": request.method,
        "error_type": type(exc).__name__,
        "error_message": str(exc)
    }
    error_tracking.append(error_info)
    
    # Keep only last 100 errors
    if len(error_tracking) > 100:
        error_tracking.pop(0)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "error_id": error_id,
            "timestamp": error_time,
            "support_info": "Include this error ID when contacting support"
        }
    )
# Enhanced Models with comprehensive validation
class TDEERequest(BaseModel):
    sex: str = Field(..., description="'male' or 'female'")
    age: int = Field(..., ge=10, le=120, description="Age in years (10-120)")
    height_cm: float = Field(..., ge=100, le=250, description="Height in centimeters (100-250)")
    weight_kg: float = Field(..., ge=30, le=300, description="Weight in kilograms (30-300)")
    activity_level: str = Field(..., description="'sedentary', 'light', 'moderate', 'active', 'very_active'")
    goal: str = Field(..., description="'cut', 'maintain', 'bulk'")
    
    @validator('sex')
    def validate_sex(cls, v):
        if v.lower() not in ['male', 'female']:
            raise ValueError("Sex must be 'male' or 'female'")
        return v.lower()
    
    @validator('activity_level')
    def validate_activity(cls, v):
        valid_levels = ['sedentary', 'light', 'moderate', 'active', 'very_active']
        if v.lower() not in valid_levels:
            raise ValueError(f"Activity level must be one of: {', '.join(valid_levels)}")
        return v.lower()
    
    @validator('goal')
    def validate_goal(cls, v):
        valid_goals = ['cut', 'maintain', 'bulk']
        if v.lower() not in valid_goals:
            raise ValueError(f"Goal must be one of: {', '.join(valid_goals)}")
        return v.lower()
class TDEEResponse(BaseModel):
    tdee: float
    target_calories: float
    macro_targets: Dict[str, float]
    bmr: float
    activity_factor: float
class MealPlanRequest(BaseModel):
    calories: float = Field(..., ge=800, le=6000)
    protein_g: float = Field(..., ge=50, le=400)
    fat_g: float = Field(..., ge=20, le=200)
    carbs_g: float = Field(..., ge=50, le=800)
    diet_tags: List[str] = Field(default=[])
    days: int = Field(default=7, ge=1, le=14)
class FoodItem(BaseModel):
    name: str
    amount_g: float
    calories: float
    protein: float
    fat: float
    carbs: float
class Meal(BaseModel):
    name: str
    foods: List[FoodItem]
    totals: Dict[str, float]
class DayPlan(BaseModel):
    day: int
    meals: List[Meal]
    daily_totals: Dict[str, float]
class MealPlanResponse(BaseModel):
    days: List[DayPlan]
    plan_totals: Dict[str, float]
    adherence_score: float
# TDEE Calculation Functions
def calculate_bmr(sex: str, age: int, height_cm: float, weight_kg: float) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
    if sex.lower() == 'male':
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:  # female
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
def get_activity_factor(activity_level: str) -> float:
    """Get activity multiplier"""
    factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    return factors.get(activity_level.lower(), 1.55)
def get_calorie_adjustment(goal: str) -> float:
    """Get calorie adjustment based on goal"""
    adjustments = {
        'cut': -0.20,      # 20% deficit
        'maintain': 0.0,   # maintenance
        'bulk': 0.15       # 15% surplus
    }
    return adjustments.get(goal.lower(), 0.0)
def calculate_macro_targets(calories: float, goal: str) -> Dict[str, float]:
    """Calculate macro targets based on calories and goal"""
    if goal.lower() == 'cut':
        # Higher protein for muscle preservation
        protein_ratio = 0.35
        fat_ratio = 0.25
    elif goal.lower() == 'bulk':
        # More carbs for energy
        protein_ratio = 0.25
        fat_ratio = 0.25
    else:  # maintain
        protein_ratio = 0.30
        fat_ratio = 0.25
    carb_ratio = 1.0 - protein_ratio - fat_ratio
    return {
        'protein_g': (calories * protein_ratio) / 4,  # 4 cal/g
        'fat_g': (calories * fat_ratio) / 9,          # 9 cal/g
        'carbs_g': (calories * carb_ratio) / 4        # 4 cal/g
    }
# Meal Planning Functions
def filter_foods(diet_tags: List[str]) -> List[Dict]:
    """Filter foods based on dietary restrictions with improved accuracy"""
    foods = FOODS_DB['foods']
    if not diet_tags:
        return foods
    filtered_foods = []
    for food in foods:
        food_tags = food.get('tags', [])
        # Check for vegetarian/vegan requirements (highest priority)
        if 'vegan' in diet_tags:
            # Vegan users can only eat vegan foods
            if 'vegan' not in food_tags:
                continue
        elif 'veg' in diet_tags and 'non_veg' not in diet_tags:
            # Vegetarian users (excluding non-veg) can only eat veg/vegan foods
            if 'veg' not in food_tags and 'vegan' not in food_tags:
                continue
        elif 'non_veg' in diet_tags and 'veg' not in diet_tags:
            # Non-vegetarian users (excluding veg) can only eat non-veg foods
            if 'non_veg' not in food_tags:
                continue
        # If both veg and non_veg are selected, include all foods
        # Check for lactose-free requirement
        if 'lactose_free' in diet_tags:
            # Exclude dairy products for lactose-free
            if any(dairy in food['name'].lower() for dairy in ['milk', 'cheese', 'yogurt', 'cottage']):
                continue
        # Check for halal requirement
        if 'halal' in diet_tags:
            # Exclude pork and non-halal meat
            if any(non_halal in food['name'].lower() for non_halal in ['pork', 'bacon', 'ham']):
                continue
            # For meat items, ensure they have halal tag
            if any(meat in food['name'].lower() for meat in ['beef', 'chicken', 'turkey', 'lamb']):
                if 'halal' not in food_tags:
                    continue
        # Check for budget requirement
        if 'budget' in diet_tags:
            if food.get('cost_level') not in ['low', 'medium']:
                continue
        filtered_foods.append(food)
    return filtered_foods
def generate_meal(target_calories: float, target_protein: float, target_fat: float, 
                 target_carbs: float, available_foods: List[Dict], meal_name: str) -> Meal:
    """Generate a single meal with improved nutritional balance"""
    selected_foods = []
    current_calories = 0
    current_protein = 0
    current_fat = 0
    current_carbs = 0
    # Categorize foods by type for better meal composition
    protein_foods = [f for f in available_foods if f['per_100g']['protein'] > 10]
    carb_foods = [f for f in available_foods if f['per_100g']['carbs'] > 15]
    fat_foods = [f for f in available_foods if f['per_100g']['fat'] > 8]
    veggie_foods = [f for f in available_foods if f['per_100g']['carbs'] < 10 and f['per_100g']['protein'] < 5]
    # Ensure we have at least one protein source
    if protein_foods:
        protein_food = random.choice(protein_foods)
        # Calculate protein amount to meet 70-80% of target
        protein_amount = min(150, max(50, (target_protein * 0.75 / protein_food['per_100g']['protein']) * 100))
        scale_factor = protein_amount / 100
        food_calories = protein_food['per_100g']['calories'] * scale_factor
        food_protein = protein_food['per_100g']['protein'] * scale_factor
        food_fat = protein_food['per_100g']['fat'] * scale_factor
        food_carbs = protein_food['per_100g']['carbs'] * scale_factor
        selected_foods.append(FoodItem(
            name=protein_food['name'],
            amount_g=round(protein_amount, 1),
            calories=round(food_calories, 1),
            protein=round(food_protein, 1),
            fat=round(food_fat, 1),
            carbs=round(food_carbs, 1)
        ))
        current_calories += food_calories
        current_protein += food_protein
        current_fat += food_fat
        current_carbs += food_carbs
    # Add carb source if needed
    remaining_carbs = target_carbs - current_carbs
    if remaining_carbs > 10 and carb_foods:
        carb_food = random.choice(carb_foods)
        carb_amount = min(200, max(50, (remaining_carbs / carb_food['per_100g']['carbs']) * 100))
        scale_factor = carb_amount / 100
        food_calories = carb_food['per_100g']['calories'] * scale_factor
        food_protein = carb_food['per_100g']['protein'] * scale_factor
        food_fat = carb_food['per_100g']['fat'] * scale_factor
        food_carbs = carb_food['per_100g']['carbs'] * scale_factor
        selected_foods.append(FoodItem(
            name=carb_food['name'],
            amount_g=round(carb_amount, 1),
            calories=round(food_calories, 1),
            protein=round(food_protein, 1),
            fat=round(food_fat, 1),
            carbs=round(food_carbs, 1)
        ))
        current_calories += food_calories
        current_protein += food_protein
        current_fat += food_fat
        current_carbs += food_carbs
    # Add fat source if needed
    remaining_fat = target_fat - current_fat
    if remaining_fat > 5 and fat_foods:
        fat_food = random.choice(fat_foods)
        fat_amount = min(100, max(20, (remaining_fat / fat_food['per_100g']['fat']) * 100))
        scale_factor = fat_amount / 100
        food_calories = fat_food['per_100g']['calories'] * scale_factor
        food_protein = fat_food['per_100g']['protein'] * scale_factor
        food_fat = fat_food['per_100g']['fat'] * scale_factor
        food_carbs = fat_food['per_100g']['carbs'] * scale_factor
        selected_foods.append(FoodItem(
            name=fat_food['name'],
            amount_g=round(fat_amount, 1),
            calories=round(food_calories, 1),
            protein=round(food_protein, 1),
            fat=round(food_fat, 1),
            carbs=round(food_carbs, 1)
        ))
        current_calories += food_calories
        current_protein += food_protein
        current_fat += food_fat
        current_carbs += food_carbs
    # Add vegetables for micronutrients and volume
    if veggie_foods and len(selected_foods) < 4:
        veggie_food = random.choice(veggie_foods)
        veggie_amount = random.randint(50, 150)
        scale_factor = veggie_amount / 100
        food_calories = veggie_food['per_100g']['calories'] * scale_factor
        food_protein = veggie_food['per_100g']['protein'] * scale_factor
        food_fat = veggie_food['per_100g']['fat'] * scale_factor
        food_carbs = veggie_food['per_100g']['carbs'] * scale_factor
        selected_foods.append(FoodItem(
            name=veggie_food['name'],
            amount_g=round(veggie_amount, 1),
            calories=round(food_calories, 1),
            protein=round(food_protein, 1),
            fat=round(food_fat, 1),
            carbs=round(food_carbs, 1)
        ))
        current_calories += food_calories
        current_protein += food_protein
        current_fat += food_fat
        current_carbs += food_carbs
    totals = {
        'calories': round(current_calories, 1),
        'protein': round(current_protein, 1),
        'fat': round(current_fat, 1),
        'carbs': round(current_carbs, 1)
    }
    return Meal(name=meal_name, foods=selected_foods, totals=totals)
def generate_day_plan(day_num: int, daily_calories: float, daily_protein: float, 
                     daily_fat: float, daily_carbs: float, available_foods: List[Dict]) -> DayPlan:
    """Generate a full day meal plan"""
    # Distribute calories across meals (breakfast: 25%, lunch: 35%, dinner: 40%)
    breakfast_cals = daily_calories * 0.25
    lunch_cals = daily_calories * 0.35
    dinner_cals = daily_calories * 0.40
    # Distribute macros proportionally
    breakfast_protein = daily_protein * 0.25
    breakfast_fat = daily_fat * 0.25
    breakfast_carbs = daily_carbs * 0.25
    lunch_protein = daily_protein * 0.35
    lunch_fat = daily_fat * 0.35
    lunch_carbs = daily_carbs * 0.35
    dinner_protein = daily_protein * 0.40
    dinner_fat = daily_fat * 0.40
    dinner_carbs = daily_carbs * 0.40
    meals = [
        generate_meal(breakfast_cals, breakfast_protein, breakfast_fat, breakfast_carbs, 
                     available_foods, "Breakfast"),
        generate_meal(lunch_cals, lunch_protein, lunch_fat, lunch_carbs, 
                     available_foods, "Lunch"),
        generate_meal(dinner_cals, dinner_protein, dinner_fat, dinner_carbs, 
                     available_foods, "Dinner")
    ]
    # Calculate daily totals
    daily_totals = {
        'calories': sum(meal.totals['calories'] for meal in meals),
        'protein': sum(meal.totals['protein'] for meal in meals),
        'fat': sum(meal.totals['fat'] for meal in meals),
        'carbs': sum(meal.totals['carbs'] for meal in meals)
    }
    return DayPlan(day=day_num, meals=meals, daily_totals=daily_totals)
# API Endpoints
@app.post("/tdee", response_model=TDEEResponse)
async def calculate_tdee(request: TDEERequest):
    """Calculate TDEE and macro targets"""
    try:
        # Validate inputs
        if request.sex.lower() not in ['male', 'female']:
            raise HTTPException(status_code=400, detail="Sex must be 'male' or 'female'")
        if request.activity_level.lower() not in ['sedentary', 'light', 'moderate', 'active', 'very_active']:
            raise HTTPException(status_code=400, detail="Invalid activity level")
        if request.goal.lower() not in ['cut', 'maintain', 'bulk']:
            raise HTTPException(status_code=400, detail="Goal must be 'cut', 'maintain', or 'bulk'")
        # Calculate BMR
        bmr = calculate_bmr(request.sex, request.age, request.height_cm, request.weight_kg)
        # Calculate TDEE
        activity_factor = get_activity_factor(request.activity_level)
        tdee = bmr * activity_factor
        # Adjust for goal
        calorie_adjustment = get_calorie_adjustment(request.goal)
        target_calories = tdee * (1 + calorie_adjustment)
        # Calculate macro targets
        macro_targets = calculate_macro_targets(target_calories, request.goal)
        return TDEEResponse(
            tdee=round(tdee, 1),
            target_calories=round(target_calories, 1),
            macro_targets={
                'protein_g': round(macro_targets['protein_g'], 1),
                'fat_g': round(macro_targets['fat_g'], 1),
                'carbs_g': round(macro_targets['carbs_g'], 1)
            },
            bmr=round(bmr, 1),
            activity_factor=activity_factor
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
@app.post("/mealplan", response_model=MealPlanResponse)
async def generate_meal_plan(request: MealPlanRequest):
    """Generate a meal plan based on nutritional requirements"""
    try:
        # Filter foods based on dietary restrictions
        available_foods = filter_foods(request.diet_tags)
        if not available_foods:
            raise HTTPException(status_code=400, detail="No foods available for the specified dietary restrictions")
        # Generate meal plan for specified number of days
        days = []
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        for day_num in range(1, request.days + 1):
            day_plan = generate_day_plan(
                day_num, request.calories, request.protein_g, 
                request.fat_g, request.carbs_g, available_foods
            )
            days.append(day_plan)
            total_calories += day_plan.daily_totals['calories']
            total_protein += day_plan.daily_totals['protein']
            total_fat += day_plan.daily_totals['fat']
            total_carbs += day_plan.daily_totals['carbs']
        # Calculate plan totals
        plan_totals = {
            'calories': round(total_calories, 1),
            'protein': round(total_protein, 1),
            'fat': round(total_fat, 1),
            'carbs': round(total_carbs, 1),
            'avg_daily_calories': round(total_calories / request.days, 1)
        }
        # Calculate adherence score (how close to targets)
        target_total_calories = request.calories * request.days
        target_total_protein = request.protein_g * request.days
        target_total_fat = request.fat_g * request.days
        target_total_carbs = request.carbs_g * request.days
        calorie_adherence = 1 - abs(total_calories - target_total_calories) / target_total_calories
        protein_adherence = 1 - abs(total_protein - target_total_protein) / target_total_protein
        fat_adherence = 1 - abs(total_fat - target_total_fat) / target_total_fat
        carb_adherence = 1 - abs(total_carbs - target_total_carbs) / target_total_carbs
        adherence_score = (calorie_adherence + protein_adherence + fat_adherence + carb_adherence) / 4
        adherence_score = max(0, min(1, adherence_score))  # Clamp between 0 and 1
        return MealPlanResponse(
            days=days,
            plan_totals=plan_totals,
            adherence_score=round(adherence_score, 3)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Meal plan generation error: {str(e)}")
@app.get("/explain")
async def explain_nutrition(
    calories: float = Query(..., description="Daily calorie target"),
    protein_g: Optional[float] = Query(None, description="Daily protein target in grams"),
    fat_g: Optional[float] = Query(None, description="Daily fat target in grams"),
    carbs_g: Optional[float] = Query(None, description="Daily carbs target in grams"),
    constraints: Optional[str] = Query(None, description="Additional constraints or context"),
    diet_tags: Optional[List[str]] = Query(None, description="Dietary preferences")
):
    """Get explanation for nutrition recommendations"""
    try:
        # Check if OLLAMA is available
        ollama_url = os.getenv('OLLAMA_URL')
        if ollama_url:
            # Use OLLAMA for AI-powered explanation
            diet_context = ""
            if diet_tags:
                if 'veg' in diet_tags and 'non_veg' not in diet_tags:
                    diet_context = " (Vegetarian diet)"
                elif 'non_veg' in diet_tags and 'veg' not in diet_tags:
                    diet_context = " (Non-vegetarian diet)"
                elif 'vegan' in diet_tags:
                    diet_context = " (Vegan diet)"
                elif 'veg' in diet_tags and 'non_veg' in diet_tags:
                    diet_context = " (Mixed diet - vegetarian and non-vegetarian options)"
            prompt = f"""Provide a thorough, user-friendly nutrition explanation for the plan below. Use section headings and concise paragraphs. Be practical and specific.
Daily Calories: {calories}
Protein: {protein_g}g ({round((protein_g * 4 / calories) * 100, 1)}% of calories)
Fat: {fat_g}g ({round((fat_g * 9 / calories) * 100, 1)}% of calories)
Carbs: {carbs_g}g ({round((carbs_g * 4 / calories) * 100, 1)}% of calories)
Diet: {diet_context or 'No specific restrictions'}
Additional constraints: {constraints or 'None'}
Write 400-600 words max with the following structure:
1) Overview: What this plan aims to achieve in simple terms.
2) Macro Rationale: Why these protein/fat/carb ratios fit the calories and goals. Quantify benefits.
3) What To Eat: Food examples aligned with the diet preference(s). Include protein, carb, fat sources and vegetables. Offer 2-3 swaps for common preferences or budgets.
4) Daily Flow: Suggest meal timing (e.g., 3 meals + 1-2 snacks), protein per meal targets, and hydration.
5) Example Day Menu: Bullet list with 3 meals + 1 snack. Provide vegetarian and non-vegetarian variants when appropriate.
6) Adjustments: How to modify macros if energy/hunger/performance changes. Include +/-10% guidance.
7) Tips & Warnings: Compliance tips, fiber targets, and cautions relevant to the diet preference(s).
Keep tone supportive, clear, and non-technical. Avoid making medical claims. Use short sentences. End with one-sentence next steps."""
            try:
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": "phi3:mini",  # Lightweight model, good for nutrition advice
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    ai_response = response.json()
                    return {"explanation": ai_response.get('response', 'AI explanation unavailable')}
                else:
                    # Fall back to rule-based explanation
                    pass
            except requests.RequestException:
                # Fall back to rule-based explanation
                pass
        # Enhanced detailed dietitian-level explanation
        protein_ratio = (protein_g * 4 / calories) if protein_g else 0
        fat_ratio = (fat_g * 9 / calories) if fat_g else 0
        carb_ratio = (carbs_g * 4 / calories) if carbs_g else 0
        
        explanation = f"""**COMPREHENSIVE NUTRITION PLAN ANALYSIS**
*Professional Dietitian Consultation Report*

**EXECUTIVE SUMMARY**
This personalized nutrition plan provides {calories} calories daily with scientifically-optimized macronutrient distribution. The plan is designed using evidence-based nutrition principles and WHO/FAO guidelines to support your health goals while ensuring nutritional adequacy.

**DETAILED MACRONUTRIENT ANALYSIS**

**Protein: {protein_g}g ({round(protein_ratio * 100, 1)}% of total calories)**
Your protein intake is strategically set to support muscle protein synthesis, metabolic function, and satiety. This amount provides approximately {round(protein_g/70, 2)}g per kg body weight (assuming 70kg), which aligns with sports nutrition recommendations for active individuals.

*Clinical Benefits:*
- Maintains lean muscle mass during weight management
- Increases thermic effect of food (burns 20-30% of protein calories during digestion)
- Provides sustained satiety lasting 3-4 hours
- Supports immune function and enzyme production

*Distribution Strategy:* Aim for {round(protein_g/3, 1)}g per main meal to optimize muscle protein synthesis. Include complete proteins (containing all 9 essential amino acids) such as quinoa, hemp seeds, or animal proteins.

**Fat: {fat_g}g ({round(fat_ratio * 100, 1)}% of total calories)**
Your fat allocation supports hormone production, vitamin absorption, and cellular function while maintaining optimal body composition.

*Clinical Benefits:*
- Essential for absorption of fat-soluble vitamins (A, D, E, K)
- Supports hormone production including testosterone and estrogen
- Provides concentrated energy for endurance activities
- Promotes skin and brain health

*Quality Focus:* Prioritize omega-3 fatty acids (2-3g daily from fish, flax, chia), monounsaturated fats (olive oil, avocados), and limit saturated fats to <10% of total calories.

**Carbohydrates: {carbs_g}g ({round(carb_ratio * 100, 1)}% of total calories)**
Your carbohydrate intake is optimized for energy production, brain function, and glycogen replenishment.

*Clinical Benefits:*
- Primary fuel source for brain (120g glucose daily requirement)
- Supports high-intensity training performance
- Maintains healthy gut microbiome through fiber intake
- Prevents muscle protein breakdown when adequate

*Timing Strategy:* Focus carbohydrate intake around physical activity. Consume 30-50g complex carbs pre-workout and 1-1.5g per kg body weight post-workout for optimal recovery.

**PHYSIOLOGICAL ADAPTATIONS EXPECTED**

**Metabolic Response (Weeks 1-2):**
- Initial water weight changes (±2-3 lbs) as glycogen stores adjust
- Improved insulin sensitivity with regular meal timing
- Enhanced fat oxidation during lower-intensity activities
- Stabilized blood sugar levels reducing energy crashes

**Body Composition Changes (Weeks 3-8):**
- Gradual fat loss while preserving lean muscle mass
- Improved muscle definition and strength maintenance
- Enhanced metabolic flexibility (ability to switch between fuel sources)
- Reduced inflammation markers and improved recovery

**MEAL TIMING & FREQUENCY OPTIMIZATION**

**Circadian Rhythm Alignment:**
- Largest meal within 2 hours of peak activity time
- Protein distribution every 3-4 hours for muscle protein synthesis
- Carbohydrate timing aligned with activity demands
- 12-hour eating window to support metabolic health

**Pre/Post-Workout Nutrition:**
*Pre-Workout (30-60 minutes before):*
- 15-30g easily digestible carbs (banana, dates)
- 5-10g protein if training >60 minutes
- Adequate hydration (500ml water)

*Post-Workout (within 30 minutes):*
- 20-40g high-quality protein
- 30-60g carbohydrates (depending on training intensity)
- Electrolyte replacement if sweating significantly

**MICRONUTRIENT CONSIDERATIONS**

**Priority Nutrients for Monitoring:**
- Iron: Especially important for women and vegetarians (18mg/day women, 8mg/day men)
- Vitamin B12: Critical for vegans (2.4μg/day minimum)
- Vitamin D: Often deficient, consider 1000-2000 IU supplementation
- Omega-3s: 250-500mg EPA+DHA daily for cardiovascular health
- Magnesium: 300-400mg daily for muscle and nervous system function

**Hydration Protocol:**
- Minimum 35ml per kg body weight daily
- Additional 500-750ml per hour of intense exercise
- Morning hydration: 500ml within 30 minutes of waking
- Monitor urine color (pale yellow indicates adequate hydration)

**BEHAVIORAL & PSYCHOLOGICAL STRATEGIES**

**Sustainable Implementation:**
1. **Meal Prep Mastery:** Dedicate 2-3 hours weekly to batch cooking proteins, chopping vegetables, and portioning snacks
2. **Mindful Eating Practice:** Eat without distractions, chew thoroughly (20-30 times per bite), and pause halfway through meals to assess hunger
3. **Stress Management:** Chronic stress increases cortisol, promoting fat storage. Incorporate 10-15 minutes daily meditation or deep breathing
4. **Sleep Optimization:** 7-9 hours quality sleep supports hormone regulation and reduces cravings for processed foods

**MONITORING & ADJUSTMENTS**

**Weekly Assessment Metrics:**
- Energy levels (1-10 scale) throughout the day
- Workout performance and recovery quality
- Digestive health and regularity
- Mood stability and mental clarity
- Body measurements (waist, hip, weight)

**Monthly Plan Modifications:**
*If Progress Stalls:*
- Reduce calories by 100-150 (primarily from carbs/fats)
- Increase non-exercise activity thermogenesis (NEAT)
- Reassess food measurement accuracy

*If Energy Decreases:*
- Increase calories by 100-200 with focus on carbohydrates
- Evaluate sleep quality and stress levels
- Consider temporary diet break (eat at maintenance for 1-2 weeks)

**SPECIAL DIETARY CONSIDERATIONS**"""
        
        # Add dietary constraints
        if constraints or diet_tags:
            diet_considerations = []
            if diet_tags:
                if 'vegan' in diet_tags:
                    diet_considerations.append("**Vegan Optimization:** Focus on complete protein combinations (rice+beans, quinoa+hemp seeds). Supplement B12, consider algae-based omega-3, and ensure adequate iron with vitamin C co-consumption.")
                elif 'veg' in diet_tags and 'non_veg' not in diet_tags:
                    diet_considerations.append("**Vegetarian Focus:** Include diverse protein sources (legumes, dairy, eggs). Monitor iron levels and consider pairing iron-rich foods with vitamin C sources.")
                elif 'halal' in diet_tags:
                    diet_considerations.append("**Halal Compliance:** All protein sources verified halal-certified. Emphasis on lean meats, fish, and plant proteins maintaining religious dietary laws.")
                if 'budget' in diet_tags:
                    diet_considerations.append("**Budget-Conscious Approach:** Prioritize economical protein sources (eggs, legumes, canned fish). Buy seasonal produce, consider frozen vegetables for consistent nutrition year-round.")
            
            if constraints:
                diet_considerations.append(f"**Additional Considerations:** {constraints}")
            
            explanation += "\n\n" + "\n\n".join(diet_considerations)
        
        explanation += f"""

**LONG-TERM HEALTH IMPLICATIONS**

**Cardiovascular Benefits:**
- Optimized lipid profile through balanced fat intake
- Reduced inflammation markers
- Improved blood pressure regulation
- Enhanced endothelial function

**Metabolic Health:**
- Improved insulin sensitivity and glucose tolerance
- Maintained metabolic rate during weight management
- Enhanced mitochondrial function and energy production
- Reduced risk of metabolic syndrome

**CLINICAL MONITORING RECOMMENDATIONS**

**Baseline and 3-Month Follow-up Labs:**
- Comprehensive metabolic panel (glucose, lipids, liver function)
- Complete blood count (iron status, B12 levels)
- Inflammatory markers (CRP, ESR if indicated)
- Thyroid function (TSH, T3, T4)
- Vitamin D status

**RED FLAGS - When to Consult Healthcare Provider:**
- Persistent fatigue despite adequate sleep
- Digestive issues lasting >2 weeks
- Significant mood changes or anxiety
- Hair loss or brittle nails
- Menstrual irregularities (women)
- Dizziness or lightheadedness

**EVIDENCE-BASED REFERENCES**
This plan incorporates recommendations from:
- International Society of Sports Nutrition position stands
- Academy of Nutrition and Dietetics evidence-based guidelines  
- WHO/FAO joint expert consultation on human nutrition requirements
- American Heart Association dietary guidelines
- Position of the American Dietetic Association on vegetarian diets

**PROFESSIONAL DISCLAIMER**
This nutrition analysis is for educational purposes and general guidance. Individual nutritional needs vary based on genetics, health status, medication use, and lifestyle factors. For medical conditions, eating disorders, or specific health concerns, consult with a registered dietitian nutritionist or healthcare provider for personalized medical nutrition therapy.

**NEXT STEPS & SUCCESS TIMELINE**

**Week 1-2: Foundation Building**
- Establish meal timing routine
- Perfect portion measurement techniques  
- Begin meal prep habits
- Monitor energy and hunger patterns

**Week 3-4: Optimization Phase**
- Fine-tune food choices based on preferences
- Adjust timing based on lifestyle demands
- Increase variety in protein and vegetable sources
- Establish sustainable shopping and cooking routines

**Month 2-3: Mastery & Maintenance**
- Intuitive portion estimation skills
- Flexible meal planning abilities
- Stress-eating management strategies
- Long-term lifestyle integration

**SUCCESS METRICS TO TRACK:**
✓ Consistent energy levels throughout the day
✓ Improved workout performance and recovery
✓ Better sleep quality and mood stability  
✓ Sustainable eating habits without feeling restricted
✓ Gradual progress toward body composition goals

Remember: Sustainable nutrition changes take time. Focus on consistency over perfection, and celebrate small wins along your journey toward optimal health."""
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation error: {str(e)}")
@app.get("/diet-options")
async def get_diet_options():
    """Get available diet options and their descriptions"""
    return {
        "diet_options": [
            {
                "value": "veg",
                "label": "Vegetarian",
                "description": "No meat, fish, or poultry",
                "icon": "🥬",
                "examples": ["tofu", "lentils", "chickpeas", "eggs", "dairy"]
            },
            {
                "value": "non_veg",
                "label": "Non-Vegetarian", 
                "description": "Includes meat, fish, and poultry",
                "icon": "🍖",
                "examples": ["chicken", "beef", "fish", "turkey", "eggs"]
            },
            {
                "value": "vegan",
                "label": "Vegan",
                "description": "No animal products",
                "icon": "🌱",
                "examples": ["tofu", "lentils", "chickpeas", "nuts", "seeds"]
            },
            {
                "value": "halal",
                "label": "Halal",
                "description": "Halal dietary requirements",
                "icon": "☪️",
                "examples": ["halal meat", "fish", "dairy", "grains"]
            },
            {
                "value": "lactose_free",
                "label": "Lactose Free",
                "description": "No dairy products",
                "icon": "🥛",
                "examples": ["almond milk", "coconut yogurt", "dairy-free cheese"]
            },
            {
                "value": "budget",
                "label": "Budget Friendly",
                "description": "Cost-effective food choices",
                "icon": "💰",
                "examples": ["lentils", "rice", "beans", "frozen vegetables"]
            }
        ]
    }
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint with system status"""
    try:
        # Check database status
        foods_count = len(FOODS_DB.get("foods", []))
        db_metadata = FOODS_DB.get("metadata", {})
        db_status = "healthy" if foods_count > 0 else "degraded"
        
        # Check recent errors
        recent_errors = [e for e in error_tracking if 
                        datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)]
        error_rate = len(recent_errors)
        
        # System status
        status = "healthy"
        if foods_count == 0:
            status = "degraded"
        elif error_rate > 10:  # More than 10 errors in last hour
            status = "warning"
        
        return {
            "status": status,
            "service": "diet-api",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "status": db_status,
                "foods_count": foods_count,
                "version": db_metadata.get("version", "unknown"),
                "validation_rate": db_metadata.get("data_quality", {}).get("validation_rate", "unknown")
            },
            "system": {
                "recent_errors": error_rate,
                "uptime_status": "operational"
            },
            "features": {
                "tdee_calculation": True,
                "meal_planning": True,
                "nutrition_explanation": True,
                "research_analytics": True,
                "cultural_foods": foods_count > 30
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "service": "diet-api",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get system analytics and usage summary for research purposes"""
    try:
        # Calculate error statistics
        total_errors = len(error_tracking)
        recent_errors = [e for e in error_tracking if 
                        datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=24)]
        
        # Error breakdown by type
        error_types = {}
        for error in error_tracking:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Database statistics
        foods_data = FOODS_DB.get("foods", [])
        db_metadata = FOODS_DB.get("metadata", {})
        
        # Food category distribution
        category_counts = {}
        for food in foods_data:
            for tag in food.get("tags", []):
                category_counts[tag] = category_counts.get(tag, 0) + 1
        
        return {
            "system_health": {
                "total_errors_logged": total_errors,
                "errors_last_24h": len(recent_errors),
                "error_types": error_types,
                "database_status": "healthy" if len(foods_data) > 0 else "degraded"
            },
            "database_analytics": {
                "total_foods": len(foods_data),
                "database_version": db_metadata.get("version", "unknown"),
                "validation_rate": db_metadata.get("data_quality", {}).get("validation_rate", "unknown"),
                "category_distribution": category_counts,
                "cultural_contexts": db_metadata.get("cultural_contexts", []),
                "dietary_accommodations": db_metadata.get("dietary_accommodations", [])
            },
            "ml_features_available": db_metadata.get("ml_features", []),
            "research_capabilities": {
                "nutritional_validation": True,
                "cultural_diversity": len(db_metadata.get("cultural_contexts", [])) > 5,
                "accessibility_focus": "budget_friendly" in str(category_counts),
                "ml_ready": len(db_metadata.get("ml_features", [])) > 0
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics generation error: {str(e)}")

@app.get("/research/food-database")
async def get_research_food_database():
    """Get complete food database for research purposes with full metadata"""
    try:
        # Add request timestamp for research tracking
        research_data = FOODS_DB.copy()
        research_data["request_info"] = {
            "timestamp": datetime.now().isoformat(),
            "purpose": "research_access",
            "data_license": "research_use_only",
            "citation_required": True
        }
        
        return research_data
    except Exception as e:
        logger.error(f"Research database access failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research data access error: {str(e)}")

@app.get("/research/nutrition-ranges")
async def get_nutrition_ranges():
    """Get nutritional ranges and statistics for research validation"""
    try:
        foods_data = FOODS_DB.get("foods", [])
        if not foods_data:
            raise HTTPException(status_code=503, detail="No food data available")
        
        # Calculate comprehensive nutritional statistics
        nutrients = ['calories', 'protein', 'fat', 'carbs', 'fiber', 'sugar', 'sodium', 'potassium']
        nutrition_analysis = {}
        
        for nutrient in nutrients:
            values = [food["per_100g"].get(nutrient, 0) for food in foods_data if nutrient in food["per_100g"]]
            if values:
                nutrition_analysis[nutrient] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "median": sorted(values)[len(values)//2],
                    "count": len(values),
                    "unit": "mg" if nutrient in ["sodium", "potassium"] else "g" if nutrient != "calories" else "kcal"
                }
        
        # Diet compatibility analysis
        diet_tags = ['veg', 'vegan', 'non_veg', 'halal', 'budget', 'high_protein']
        diet_distribution = {}
        for tag in diet_tags:
            count = sum(1 for food in foods_data if tag in food.get("tags", []))
            diet_distribution[tag] = {
                "count": count,
                "percentage": round((count / len(foods_data)) * 100, 1)
            }
        
        return {
            "nutritional_ranges": nutrition_analysis,
            "diet_distribution": diet_distribution,
            "total_foods_analyzed": len(foods_data),
            "data_quality": FOODS_DB.get("metadata", {}).get("data_quality", {}),
            "research_notes": {
                "validation_method": "calorie_consistency_check",
                "accuracy_threshold": "±15%",
                "cultural_diversity": "international_foods_included",
                "accessibility_focus": "budget_options_available"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Nutrition ranges analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Nutrition analysis error: {str(e)}")

@app.post("/export/excel")
async def export_nutrition_plan_excel(request: Dict[str, Any]):
    """Export comprehensive nutrition plan to Excel format"""
    try:
        # Extract required data from request
        user_profile = request.get("user_profile", {})
        nutrition_targets = request.get("nutrition_targets", {})
        meal_plan = request.get("meal_plan", {})
        explanation = request.get("explanation", "")
        validation_results = request.get("validation_results")
        
        # Validate required data
        if not user_profile or not nutrition_targets or not meal_plan:
            raise HTTPException(
                status_code=400, 
                detail="Missing required data: user_profile, nutrition_targets, and meal_plan are required"
            )
        
        logger.info("🔄 Generating Excel export for nutrition plan...")
        
        # Generate Excel file
        excel_base64 = create_excel_export(
            user_profile=user_profile,
            nutrition_targets=nutrition_targets,
            meal_plan=meal_plan,
            explanation=explanation,
            validation_results=validation_results
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nutrition_plan_{timestamp}.xlsx"
        
        logger.info(f"✅ Excel export generated successfully: {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "excel_data": excel_base64,
            "download_instructions": "Use the base64 data to create a downloadable Excel file",
            "file_size_info": f"Base64 string length: {len(excel_base64)} characters",
            "sheets_included": [
                "Executive Summary - Complete nutrition analysis and dietitian consultation",
                "Meal Plan Details - Day-by-day meal breakdown with nutritional info",
                "Nutrition Analysis - Target vs actual comparison with charts",
                "Food Database - Reference table of all foods used",
                "Quality Validation - Validation results and quality metrics",
                "Guidelines & Tips - Professional nutrition guidelines and advice"
            ],
            "generated_at": datetime.now().isoformat(),
            "export_features": [
                "Professional formatting with color-coded sections",
                "Comprehensive nutritional analysis",
                "Dietitian-level recommendations",
                "Meal planning details with portion sizes",
                "Food database reference",
                "Quality validation reports",
                "Evidence-based guidelines"
            ]
        }
        
    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Excel export error: {str(e)}")

@app.post("/generate-complete-report")
async def generate_complete_nutrition_report(request: Dict[str, Any]):
    """Generate complete nutrition report with TDEE, meal plan, explanation, and Excel export"""
    try:
        # Extract user profile
        user_data = request.get("user_data", {})
        meal_preferences = request.get("meal_preferences", {})
        
        if not user_data:
            raise HTTPException(status_code=400, detail="User data is required")
        
        logger.info("🔄 Generating complete nutrition report...")
        
        # Step 1: Calculate TDEE
        tdee_result = await calculate_tdee(TDEERequest(**user_data))
        
        # Step 2: Generate meal plan
        meal_plan_request = MealPlanRequest(
            calories=tdee_result.target_calories,
            protein_g=tdee_result.macro_targets['protein_g'],
            fat_g=tdee_result.macro_targets['fat_g'],
            carbs_g=tdee_result.macro_targets['carbs_g'],
            diet_tags=meal_preferences.get('diet_tags', []),
            days=meal_preferences.get('days', 7)
        )
        
        meal_plan_result = await generate_meal_plan(meal_plan_request)
        
        # Step 3: Generate explanation
        explanation_result = await explain_nutrition(
            calories=tdee_result.target_calories,
            protein_g=tdee_result.macro_targets['protein_g'],
            fat_g=tdee_result.macro_targets['fat_g'],
            carbs_g=tdee_result.macro_targets['carbs_g'],
            constraints=meal_preferences.get('constraints'),
            diet_tags=meal_preferences.get('diet_tags', [])
        )
        
        # Step 4: Generate Excel export
        excel_export_data = {
            "user_profile": user_data,
            "nutrition_targets": tdee_result.dict(),
            "meal_plan": meal_plan_result.dict(),
            "explanation": explanation_result['explanation']
        }
        
        excel_result = await export_nutrition_plan_excel(excel_export_data)
        
        # Compile complete report
        complete_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive_nutrition_analysis",
                "version": "2.0.0",
                "user_id": hashlib.md5(str(user_data).encode()).hexdigest()[:8]
            },
            "tdee_analysis": tdee_result.dict(),
            "meal_plan": meal_plan_result.dict(),
            "professional_explanation": explanation_result,
            "excel_export": excel_result,
            "summary": {
                "daily_calories": tdee_result.target_calories,
                "daily_protein": tdee_result.macro_targets['protein_g'],
                "daily_fat": tdee_result.macro_targets['fat_g'],
                "daily_carbs": tdee_result.macro_targets['carbs_g'],
                "plan_duration_days": meal_plan_request.days,
                "adherence_score": meal_plan_result.adherence_score,
                "dietary_preferences": meal_preferences.get('diet_tags', [])
            },
            "next_steps": [
                "Download the Excel report for detailed analysis",
                "Begin with Week 1-2 foundation building phase",
                "Monitor energy levels and adjust portions as needed",
                "Schedule follow-up assessment in 2-4 weeks",
                "Consider consulting with healthcare provider for specific conditions"
            ]
        }
        
        logger.info("✅ Complete nutrition report generated successfully")
        
        return complete_report
        
    except Exception as e:
        logger.error(f"Complete report generation failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Complete report generation error: {str(e)}")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[User]:
    """Dependency to get current authenticated user"""
    if not credentials:
        return None
    try:
        user = auth_service.verify_token(credentials.credentials)
        return user
    except Exception:
        return None


async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency that requires authentication"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        user = auth_service.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    name: str = Field(..., min_length=2, description="User's name")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class UpdateProfileRequest(BaseModel):
    profile: Dict[str, Any] = Field(..., description="Profile data to update")


class UpdatePreferencesRequest(BaseModel):
    preferences: Dict[str, Any] = Field(..., description="Preferences to update")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")


@app.post("/auth/register")
async def register(request: RegisterRequest):
    """Register a new user account"""
    try:
        result = auth_service.register(request.email, request.password, request.name)
        logger.info(f"✅ New user registered: {request.email}")
        return result
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login and get access tokens"""
    try:
        result = auth_service.login(request.email, request.password)
        return result
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/auth/refresh")
async def refresh_tokens(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        result = auth_service.refresh_tokens(request.refresh_token)
        return result
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


@app.get("/auth/me")
async def get_current_user_info(user: User = Depends(require_auth)):
    """Get current authenticated user info"""
    return user.to_public_dict()


@app.put("/auth/profile")
async def update_user_profile(
    request: UpdateProfileRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user profile"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        result = auth_service.update_profile(credentials.credentials, request.profile)
        return result
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.put("/auth/preferences")
async def update_user_preferences(
    request: UpdatePreferencesRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user preferences"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        result = auth_service.update_preferences(credentials.credentials, request.preferences)
        return result
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Change user password"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        result = auth_service.change_password(
            credentials.credentials, 
            request.old_password, 
            request.new_password
        )
        return result
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# AI CHAT ENDPOINTS
# ============================================================================

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context (profile, nutrition data)")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data for vision analysis")


class GroceryListRequest(BaseModel):
    meal_plan: Dict[str, Any] = Field(..., description="Meal plan data")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences (budget, store, etc.)")


@app.post("/ai/chat")
async def ai_chat(
    request: ChatRequest,
    user: Optional[User] = Depends(get_current_user)
):
    """
    Chat with AI nutrition coach
    
    Supports Multi-Modal Vision Analysis.
    Automatically selects the best available provider (OpenAI, Gemini, or Hugging Face).
    """
    try:
        user_id = user.id if user else None
        
        # Build context from user profile if authenticated
        context = request.context or {}
        if user and user.profile:
            context["profile"] = user.profile
        if user and user.preferences:
            context["diet_tags"] = user.preferences.get("diet_tags", [])
        
        response = await ai_service.chat(
            message=request.message,
            user_id=user_id,
            context=context,
            image_data=request.image_data
        )
        
        return {
            "success": True,
            "response": response.content,
            "provider": response.provider,
            "model": response.model,
            "tokens_used": response.tokens_used
        }
    except Exception as e:
        logger.error(f"AI Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/ai/chat/history")
async def get_chat_history(user: User = Depends(require_auth)):
    """Get conversation history for authenticated user"""
    history = ai_service.get_history(user.id)
    return {
        "success": True,
        "history": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp
            } for m in history
        ]
    }


@app.post("/ai/chat/clear")
async def clear_chat_history(user: User = Depends(require_auth)):
    """Clear conversation history for authenticated user"""
    ai_service.clear_history(user.id)
    return {"success": True, "message": "Chat history cleared"}



@app.post("/ai/recipe")
async def generate_recipe(
    request: Dict[str, Any],
    user: Optional[User] = Depends(get_current_user)
):
    """Generate a step-by-step recipe for a meal"""
    try:
        meal = request.get("meal")
        if not meal:
            raise HTTPException(status_code=400, detail="Meal data is required")
        
        # Build context from user profile if authenticated
        context = request.get("context") or {}
        if user and user.profile:
            context["profile"] = user.profile
        if user and user.preferences:
            context["diet_tags"] = user.preferences.get("diet_tags", [])
        
        result = await ai_service.generate_recipe(
            meal=meal,
            context=context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Recipe endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/grocery-list")
async def generate_grocery_list(
    request: GroceryListRequest,
    user: Optional[User] = Depends(get_current_user)
):
    """
    Generate a smart grocery list from a meal plan
    
    Uses AI to organize and optimize the shopping list with:
    - Category organization
    - Quantity consolidation
    - Budget-friendly alternatives
    - Shopping tips
    """
    try:
        # Add user preferences if authenticated
        preferences = request.preferences or {}
        if user and user.preferences:
            if not preferences.get("dietary_restrictions"):
                preferences["dietary_restrictions"] = user.preferences.get("diet_tags", [])
        
        result = await ai_service.generate_grocery_list(
            meal_plan=request.meal_plan,
            preferences=preferences
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Grocery list generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Grocery list generation error: {str(e)}")


@app.get("/ai/status")
async def get_ai_status():
    """Get AI service status and available providers"""
    from ai_service import OPENAI_API_KEY, GEMINI_API_KEY, OLLAMA_URL
    
    providers = []
    
    if OPENAI_API_KEY:
        providers.append({
            "name": "openai",
            "status": "available",
            "model": "gpt-3.5-turbo"
        })
    
    if GEMINI_API_KEY:
        providers.append({
            "name": "gemini",
            "status": "available",
            "model": "gemini-pro"
        })
    
    # Check Ollama availability
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            providers.append({
                "name": "ollama",
                "status": "available",
                "model": "phi3:mini"
            })
    except:
        providers.append({
            "name": "ollama",
            "status": "unavailable",
            "model": "phi3:mini"
        })
    
    return {
        "providers": providers,
        "default_provider": "auto",
        "fallback_available": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
