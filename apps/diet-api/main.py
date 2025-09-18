from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

import json
import os
import random
import requests
app = FastAPI(title="Diet Coach API", version="1.0.0")
# CORS configuration for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# Load foods database
FOODS_PATH = Path("/app/foods.json")
with open(FOODS_PATH, 'r') as f:
    FOODS_DB = json.load(f)
# Models
class TDEERequest(BaseModel):
    sex: str = Field(..., description="'male' or 'female'")
    age: int = Field(..., ge=10, le=120)
    height_cm: float = Field(..., ge=100, le=250)
    weight_kg: float = Field(..., ge=30, le=300)
    activity_level: str = Field(..., description="'sedentary', 'light', 'moderate', 'active', 'very_active'")
    goal: str = Field(..., description="'cut', 'maintain', 'bulk'")
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
        # Rule-based explanation
        protein_ratio = (protein_g * 4 / calories) if protein_g else 0
        fat_ratio = (fat_g * 9 / calories) if fat_g else 0
        carb_ratio = (carbs_g * 4 / calories) if carbs_g else 0
        explanation = f"**Nutrition Plan (Daily {calories} kcal)**\n\n"
        # Macro breakdown (more detailed)
        if protein_g:
            explanation += f"**Protein:** {protein_g}g ({round(protein_ratio * 100, 1)}%). Supports muscle repair, satiety, and metabolic health. Aim ~25-40g per meal.\n"
        if fat_g:
            explanation += f"**Fat:** {fat_g}g ({round(fat_ratio * 100, 1)}%). Aids hormone function and vitamin absorption. Prefer olive oil, nuts, seeds, avocado.\n"
        if carbs_g:
            explanation += f"**Carbs:** {carbs_g}g ({round(carb_ratio * 100, 1)}%). Fuels training and daily activity. Choose mostly fiber-rich carbs.\n"
        # Goal inference
        explanation += f"\n**What This Plan Suits:** "
        if calories < 1800:
            explanation += "Likely a fat-loss phase (caloric deficit)."
        elif calories > 2500:
            explanation += "Likely a muscle-gain or high-activity maintenance phase."
        else:
            explanation += "Likely a maintenance or gentle fat-loss phase."
        # Constraints consideration
        if constraints or diet_tags:
            diet_str = ""
            if diet_tags:
                if 'vegan' in diet_tags:
                    diet_str = "Vegan"
                elif 'veg' in diet_tags and 'non_veg' not in diet_tags:
                    diet_str = "Vegetarian"
                elif 'non_veg' in diet_tags and 'veg' not in diet_tags:
                    diet_str = "Non-vegetarian"
                elif 'veg' in diet_tags and 'non_veg' in diet_tags:
                    diet_str = "Mixed (veg + non-veg)"
            addl = constraints or ""
            display = (diet_str + ("; " if diet_str and addl else "") + addl).strip()
            if display:
                explanation += f"\n**Special Considerations:** {display}"
        # Practical guidance
        explanation += "\n\n**What to Eat:** Choose lean proteins, colorful vegetables, whole grains or starchy veg, and healthy fats. Build each plate with 1) protein palm-size, 2) carbs cupped-hand, 3) vegetables 1-2 fists, 4) fats thumb-size."
        # Example day menu
        explanation += "\n\n**Example Day Menu:**\n"
        explanation += "- Breakfast: Oats with Greek yogurt and berries; or tofu scramble with whole-grain toast (vegan).\n"
        explanation += "- Lunch: Grain bowl (quinoa, chickpeas/tofu or chicken), mixed veggies, olive-oil dressing.\n"
        explanation += "- Snack: Apple + 2 tbsp peanut butter; or protein shake with banana.\n"
        explanation += "- Dinner: Stir-fry with vegetables + rice; protein as tofu/tempeh (veg/vegan) or chicken/fish (non-veg).\n"
        # Adjustments
        explanation += "\n**Adjustments:** If hungry/low energy, add ~10% carbs or fats. If progress stalls, reduce calories ~10% mainly from carbs/fats while keeping protein steady. Increase steps or training volume gradually."
        # Tips
        explanation += "\n**Tips:** Target 25-35g fiber/day, drink 2-3L water, salt to taste if active. Prep 2-3 days of meals. Track trends weekly, not daily."
        explanation += "\n\nNext step: Follow the example day for a week and adjust portions using the guidelines above."
        explanation += "\n\n**Implementation Tips:** Focus on whole foods, meal prep for consistency, and adjust portions based on hunger and energy levels."
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
    """Health check endpoint"""
    return {"status": "healthy", "service": "diet-api"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
