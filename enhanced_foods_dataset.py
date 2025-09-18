#!/usr/bin/env python3
"""
Enhanced Food Dataset Generator for Diet Recommendation System
This script creates a comprehensive food dataset that includes:
- Wide variety of foods from salads to full meals
- Accurate nutritional information
- Dietary tags and restrictions
- Cost information
- Meal type categorization
- Seasonal availability
- Preparation difficulty
"""
import json
import pandas as pd
from datetime import datetime
class EnhancedFoodDatasetGenerator:
    """
    Generator for creating comprehensive food dataset
    """
    def __init__(self):
        self.foods = []
    def generate_enhanced_dataset(self):
        """
        Generate comprehensive food dataset with improved accuracy and variety
        """
        # PROTEINS
        proteins = [
            # Lean Meats
            {
                "id": "chicken_breast_grilled",
                "name": "Grilled Chicken Breast",
                "per_100g": {"calories": 165, "protein": 31.0, "fat": 3.6, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
                "tags": ["non_veg", "halal", "high_protein", "lean"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 15,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "salmon_wild",
                "name": "Wild Atlantic Salmon",
                "per_100g": {"calories": 208, "protein": 25.4, "fat": 12.4, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
                "tags": ["non_veg", "omega3", "high_protein"],
                "cost_level": "high",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 20,
                "difficulty": "medium",
                "season": "all"
            },
            {
                "id": "turkey_lean",
                "name": "Lean Ground Turkey",
                "per_100g": {"calories": 135, "protein": 30.1, "fat": 0.7, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
                "tags": ["non_veg", "halal", "high_protein", "lean"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 12,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "cod_atlantic",
                "name": "Atlantic Cod Fillet",
                "per_100g": {"calories": 82, "protein": 18.0, "fat": 0.7, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
                "tags": ["non_veg", "lean", "high_protein"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 15,
                "difficulty": "medium",
                "season": "all"
            },
            {
                "id": "tuna_fresh",
                "name": "Fresh Tuna Steak",
                "per_100g": {"calories": 144, "protein": 25.0, "fat": 4.9, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
                "tags": ["non_veg", "high_protein", "omega3"],
                "cost_level": "high",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 10,
                "difficulty": "medium",
                "season": "all"
            },
            # Plant-based Proteins
            {
                "id": "tofu_extra_firm",
                "name": "Extra Firm Tofu",
                "per_100g": {"calories": 144, "protein": 17.3, "fat": 8.7, "carbs": 2.8, "fiber": 2.3, "sugar": 0.6},
                "tags": ["veg", "vegan", "soy", "high_protein"],
                "cost_level": "low",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "preparation_time": 10,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "tempeh_organic",
                "name": "Organic Tempeh",
                "per_100g": {"calories": 190, "protein": 20.3, "fat": 10.8, "carbs": 7.6, "fiber": 9.0, "sugar": 0.0},
                "tags": ["veg", "vegan", "fermented", "high_protein"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 15,
                "difficulty": "medium",
                "season": "all"
            },
            {
                "id": "seitan_homemade",
                "name": "Homemade Seitan",
                "per_100g": {"calories": 370, "protein": 75.2, "fat": 1.9, "carbs": 14.2, "fiber": 1.9, "sugar": 0.0},
                "tags": ["veg", "vegan", "wheat", "very_high_protein"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 60,
                "difficulty": "hard",
                "season": "all"
            },
            # Legumes
            {
                "id": "lentils_red_cooked",
                "name": "Red Lentils (cooked)",
                "per_100g": {"calories": 116, "protein": 9.0, "fat": 0.4, "carbs": 20.1, "fiber": 7.9, "sugar": 1.8},
                "tags": ["veg", "vegan", "legume", "high_fiber"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 20,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "chickpeas_roasted",
                "name": "Roasted Chickpeas",
                "per_100g": {"calories": 164, "protein": 8.9, "fat": 2.6, "carbs": 27.4, "fiber": 7.6, "sugar": 4.8},
                "tags": ["veg", "vegan", "legume", "snack"],
                "cost_level": "low",
                "meal_types": ["snack", "lunch"],
                "preparation_time": 45,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "black_beans_organic",
                "name": "Organic Black Beans",
                "per_100g": {"calories": 132, "protein": 8.9, "fat": 0.5, "carbs": 23.7, "fiber": 8.7, "sugar": 0.3},
                "tags": ["veg", "vegan", "legume", "high_fiber"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 25,
                "difficulty": "easy",
                "season": "all"
            },
            # Eggs and Dairy
            {
                "id": "eggs_pasture_raised",
                "name": "Pasture-Raised Eggs",
                "per_100g": {"calories": 155, "protein": 13.0, "fat": 11.0, "carbs": 1.1, "fiber": 0.0, "sugar": 1.1},
                "tags": ["veg", "high_protein", "omega3"],
                "cost_level": "medium",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "preparation_time": 5,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "greek_yogurt_plain",
                "name": "Plain Greek Yogurt (0% fat)",
                "per_100g": {"calories": 59, "protein": 10.3, "fat": 0.4, "carbs": 3.6, "fiber": 0.0, "sugar": 3.2},
                "tags": ["veg", "probiotic", "high_protein"],
                "cost_level": "medium",
                "meal_types": ["breakfast", "snack"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "all"
            }
        ]
        # CARBOHYDRATES
        carbohydrates = [
            {
                "id": "quinoa_tricolor",
                "name": "Tricolor Quinoa (cooked)",
                "per_100g": {"calories": 120, "protein": 4.4, "fat": 1.9, "carbs": 21.8, "fiber": 2.8, "sugar": 0.9},
                "tags": ["veg", "vegan", "gluten_free", "complete_protein"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 15,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "brown_rice_short_grain",
                "name": "Short Grain Brown Rice",
                "per_100g": {"calories": 111, "protein": 2.6, "fat": 0.9, "carbs": 22.0, "fiber": 1.8, "sugar": 0.4},
                "tags": ["veg", "vegan", "whole_grain"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 45,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "oats_steel_cut",
                "name": "Steel Cut Oats (dry)",
                "per_100g": {"calories": 389, "protein": 16.9, "fat": 6.9, "carbs": 66.3, "fiber": 10.6, "sugar": 1.1},
                "tags": ["veg", "vegan", "whole_grain", "high_fiber"],
                "cost_level": "low",
                "meal_types": ["breakfast"],
                "preparation_time": 30,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "sweet_potato_orange",
                "name": "Orange Sweet Potato (baked)",
                "per_100g": {"calories": 90, "protein": 2.0, "fat": 0.2, "carbs": 20.7, "fiber": 3.3, "sugar": 6.8},
                "tags": ["veg", "vegan", "high_fiber", "vitamin_a"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 45,
                "difficulty": "easy",
                "season": "fall"
            },
            {
                "id": "pasta_whole_wheat",
                "name": "Whole Wheat Pasta (cooked)",
                "per_100g": {"calories": 124, "protein": 5.3, "fat": 1.1, "carbs": 25.1, "fiber": 3.2, "sugar": 0.8},
                "tags": ["veg", "vegan", "whole_grain"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 12,
                "difficulty": "easy",
                "season": "all"
            }
        ]
        # VEGETABLES
        vegetables = [
            # Leafy Greens
            {
                "id": "spinach_baby",
                "name": "Baby Spinach (fresh)",
                "per_100g": {"calories": 23, "protein": 2.9, "fat": 0.4, "carbs": 3.6, "fiber": 2.2, "sugar": 0.4},
                "tags": ["veg", "vegan", "leafy_green", "iron", "vitamin_k"],
                "cost_level": "low",
                "meal_types": ["breakfast", "lunch", "dinner", "snack"],
                "preparation_time": 2,
                "difficulty": "none",
                "season": "all"
            },
            {
                "id": "kale_curly",
                "name": "Curly Kale (fresh)",
                "per_100g": {"calories": 35, "protein": 2.9, "fat": 0.4, "carbs": 8.8, "fiber": 3.6, "sugar": 2.3},
                "tags": ["veg", "vegan", "superfood", "vitamin_c", "vitamin_k"],
                "cost_level": "low",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "preparation_time": 5,
                "difficulty": "easy",
                "season": "winter"
            },
            {
                "id": "arugula_wild",
                "name": "Wild Arugula",
                "per_100g": {"calories": 25, "protein": 2.6, "fat": 0.7, "carbs": 3.7, "fiber": 1.6, "sugar": 2.1},
                "tags": ["veg", "vegan", "peppery", "vitamin_k"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 2,
                "difficulty": "none",
                "season": "spring"
            },
            # Cruciferous Vegetables
            {
                "id": "broccoli_organic",
                "name": "Organic Broccoli (steamed)",
                "per_100g": {"calories": 35, "protein": 2.8, "fat": 0.4, "carbs": 7.0, "fiber": 2.6, "sugar": 1.5},
                "tags": ["veg", "vegan", "cruciferous", "vitamin_c"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 8,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "cauliflower_roasted",
                "name": "Roasted Cauliflower",
                "per_100g": {"calories": 25, "protein": 1.9, "fat": 0.3, "carbs": 5.0, "fiber": 2.0, "sugar": 1.9},
                "tags": ["veg", "vegan", "cruciferous", "low_carb"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 25,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "brussels_sprouts",
                "name": "Brussels Sprouts (roasted)",
                "per_100g": {"calories": 43, "protein": 3.4, "fat": 0.3, "carbs": 8.9, "fiber": 3.8, "sugar": 2.2},
                "tags": ["veg", "vegan", "cruciferous", "vitamin_k"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 20,
                "difficulty": "easy",
                "season": "fall"
            },
            # Root Vegetables
            {
                "id": "carrots_rainbow",
                "name": "Rainbow Carrots (raw)",
                "per_100g": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 9.6, "fiber": 2.8, "sugar": 4.7},
                "tags": ["veg", "vegan", "vitamin_a", "crunchy"],
                "cost_level": "low",
                "meal_types": ["snack", "lunch", "dinner"],
                "preparation_time": 3,
                "difficulty": "none",
                "season": "all"
            },
            {
                "id": "beets_golden",
                "name": "Golden Beets (roasted)",
                "per_100g": {"calories": 44, "protein": 1.6, "fat": 0.2, "carbs": 10.0, "fiber": 2.0, "sugar": 6.8},
                "tags": ["veg", "vegan", "nitrates", "antioxidants"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 45,
                "difficulty": "easy",
                "season": "fall"
            },
            # Bell Peppers and Others
            {
                "id": "bell_peppers_rainbow",
                "name": "Rainbow Bell Peppers",
                "per_100g": {"calories": 31, "protein": 1.0, "fat": 0.3, "carbs": 7.3, "fiber": 2.5, "sugar": 4.2},
                "tags": ["veg", "vegan", "vitamin_c", "colorful"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner", "snack"],
                "preparation_time": 5,
                "difficulty": "easy",
                "season": "summer"
            },
            {
                "id": "zucchini_spiralized",
                "name": "Spiralized Zucchini (zoodles)",
                "per_100g": {"calories": 17, "protein": 1.2, "fat": 0.3, "carbs": 3.1, "fiber": 1.0, "sugar": 2.5},
                "tags": ["veg", "vegan", "low_carb", "pasta_substitute"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 10,
                "difficulty": "easy",
                "season": "summer"
            }
        ]
        # FRUITS
        fruits = [
            {
                "id": "berries_mixed_organic",
                "name": "Organic Mixed Berries",
                "per_100g": {"calories": 57, "protein": 0.7, "fat": 0.3, "carbs": 14.5, "fiber": 2.4, "sugar": 10.0},
                "tags": ["veg", "vegan", "antioxidants", "low_glycemic"],
                "cost_level": "high",
                "meal_types": ["breakfast", "snack"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "summer"
            },
            {
                "id": "avocado_hass",
                "name": "Hass Avocado",
                "per_100g": {"calories": 160, "protein": 2.0, "fat": 14.7, "carbs": 8.5, "fiber": 6.7, "sugar": 0.7},
                "tags": ["veg", "vegan", "healthy_fats", "potassium"],
                "cost_level": "medium",
                "meal_types": ["breakfast", "lunch", "snack"],
                "preparation_time": 2,
                "difficulty": "none",
                "season": "all"
            },
            {
                "id": "apple_honeycrisp",
                "name": "Honeycrisp Apple",
                "per_100g": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 13.8, "fiber": 2.4, "sugar": 10.4},
                "tags": ["veg", "vegan", "fiber", "vitamin_c"],
                "cost_level": "low",
                "meal_types": ["snack", "breakfast"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "fall"
            },
            {
                "id": "banana_organic",
                "name": "Organic Banana",
                "per_100g": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 22.8, "fiber": 2.6, "sugar": 12.2},
                "tags": ["veg", "vegan", "potassium", "energy"],
                "cost_level": "low",
                "meal_types": ["breakfast", "snack"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "all"
            }
        ]
        # HEALTHY FATS
        healthy_fats = [
            {
                "id": "olive_oil_extra_virgin",
                "name": "Extra Virgin Olive Oil",
                "per_100g": {"calories": 884, "protein": 0.0, "fat": 100.0, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
                "tags": ["veg", "vegan", "monounsaturated", "mediterranean"],
                "cost_level": "medium",
                "meal_types": ["cooking", "dressing"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "all"
            },
            {
                "id": "almonds_raw",
                "name": "Raw Almonds",
                "per_100g": {"calories": 579, "protein": 21.2, "fat": 49.9, "carbs": 21.6, "fiber": 12.5, "sugar": 4.4},
                "tags": ["veg", "vegan", "vitamin_e", "magnesium"],
                "cost_level": "high",
                "meal_types": ["snack"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "all"
            },
            {
                "id": "walnuts_halves",
                "name": "Walnut Halves",
                "per_100g": {"calories": 654, "protein": 15.2, "fat": 65.2, "carbs": 13.7, "fiber": 6.7, "sugar": 2.6},
                "tags": ["veg", "vegan", "omega3", "brain_food"],
                "cost_level": "high",
                "meal_types": ["snack"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "all"
            },
            {
                "id": "chia_seeds_organic",
                "name": "Organic Chia Seeds",
                "per_100g": {"calories": 486, "protein": 16.5, "fat": 30.7, "carbs": 42.1, "fiber": 34.4, "sugar": 0.0},
                "tags": ["veg", "vegan", "omega3", "superfood"],
                "cost_level": "medium",
                "meal_types": ["breakfast", "snack"],
                "preparation_time": 0,
                "difficulty": "none",
                "season": "all"
            }
        ]
        # MEAL COMBINATIONS (Salads to Complete Meals)
        meal_combinations = [
            {
                "id": "mediterranean_salad",
                "name": "Mediterranean Chickpea Salad",
                "per_100g": {"calories": 152, "protein": 6.2, "fat": 8.1, "carbs": 16.8, "fiber": 4.2, "sugar": 3.1},
                "tags": ["veg", "vegan", "mediterranean", "complete_meal"],
                "cost_level": "medium",
                "meal_types": ["lunch"],
                "preparation_time": 15,
                "difficulty": "easy",
                "season": "summer"
            },
            {
                "id": "quinoa_power_bowl",
                "name": "Quinoa Power Bowl",
                "per_100g": {"calories": 180, "protein": 8.5, "fat": 6.2, "carbs": 24.3, "fiber": 5.1, "sugar": 4.2},
                "tags": ["veg", "vegan", "complete_meal", "balanced"],
                "cost_level": "medium",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 25,
                "difficulty": "medium",
                "season": "all"
            },
            {
                "id": "grilled_salmon_vegetables",
                "name": "Grilled Salmon with Roasted Vegetables",
                "per_100g": {"calories": 145, "protein": 18.2, "fat": 6.8, "carbs": 5.2, "fiber": 2.1, "sugar": 2.8},
                "tags": ["non_veg", "omega3", "complete_meal"],
                "cost_level": "high",
                "meal_types": ["dinner"],
                "preparation_time": 35,
                "difficulty": "medium",
                "season": "all"
            },
            {
                "id": "lentil_vegetable_soup",
                "name": "Hearty Lentil Vegetable Soup",
                "per_100g": {"calories": 95, "protein": 6.8, "fat": 0.8, "carbs": 16.2, "fiber": 6.2, "sugar": 3.1},
                "tags": ["veg", "vegan", "comfort_food", "high_fiber"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 45,
                "difficulty": "easy",
                "season": "winter"
            },
            {
                "id": "tofu_stir_fry",
                "name": "Asian Tofu Vegetable Stir Fry",
                "per_100g": {"calories": 112, "protein": 8.9, "fat": 6.2, "carbs": 8.1, "fiber": 2.8, "sugar": 4.2},
                "tags": ["veg", "vegan", "asian", "complete_meal"],
                "cost_level": "low",
                "meal_types": ["lunch", "dinner"],
                "preparation_time": 20,
                "difficulty": "medium",
                "season": "all"
            }
        ]
        # SNACKS AND BEVERAGES
        snacks_beverages = [
            {
                "id": "green_smoothie",
                "name": "Green Smoothie (spinach, banana, berries)",
                "per_100g": {"calories": 65, "protein": 2.1, "fat": 0.5, "carbs": 14.8, "fiber": 2.8, "sugar": 9.2},
                "tags": ["veg", "vegan", "smoothie", "vitamin_rich"],
                "cost_level": "medium",
                "meal_types": ["breakfast", "snack"],
                "preparation_time": 5,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "hummus_classic",
                "name": "Classic Hummus",
                "per_100g": {"calories": 166, "protein": 8.0, "fat": 9.6, "carbs": 14.3, "fiber": 6.0, "sugar": 0.3},
                "tags": ["veg", "vegan", "mediterranean", "dip"],
                "cost_level": "low",
                "meal_types": ["snack"],
                "preparation_time": 10,
                "difficulty": "easy",
                "season": "all"
            },
            {
                "id": "protein_smoothie",
                "name": "Post-Workout Protein Smoothie",
                "per_100g": {"calories": 95, "protein": 12.5, "fat": 1.2, "carbs": 8.8, "fiber": 1.5, "sugar": 6.2},
                "tags": ["veg", "high_protein", "post_workout"],
                "cost_level": "medium",
                "meal_types": ["snack"],
                "preparation_time": 5,
                "difficulty": "easy",
                "season": "all"
            }
        ]
        # Combine all food categories
        all_foods = (proteins + carbohydrates + vegetables + fruits + 
                    healthy_fats + meal_combinations + snacks_beverages)
        return {"foods": all_foods}
    def add_nutritional_accuracy_features(self, foods_data):
        """
        Add features to improve nutritional accuracy and recommendations
        """
        enhanced_foods = []
        for food in foods_data["foods"]:
            # Calculate additional nutritional metrics
            nutrition = food["per_100g"]
            # Macronutrient ratios
            total_calories = nutrition["calories"]
            if total_calories > 0:
                protein_ratio = (nutrition["protein"] * 4) / total_calories
                fat_ratio = (nutrition["fat"] * 9) / total_calories
                carb_ratio = (nutrition["carbs"] * 4) / total_calories
            else:
                protein_ratio = fat_ratio = carb_ratio = 0
            # Nutritional density scores
            protein_density = nutrition["protein"] / total_calories if total_calories > 0 else 0
            fiber_density = nutrition.get("fiber", 0) / total_calories if total_calories > 0 else 0
            # Diet compatibility scores
            keto_score = fat_ratio * 0.7 + protein_ratio * 0.3 if nutrition["carbs"] < 5 else 0
            paleo_score = 1.0 if "whole_food" in food.get("tags", []) else 0.5
            mediterranean_score = 1.0 if "mediterranean" in food.get("tags", []) else 0.3
            # Satiety index (estimated)
            satiety_index = (
                nutrition["protein"] * 0.4 +
                nutrition.get("fiber", 0) * 0.3 +
                (nutrition["fat"] * 0.2) +
                (20 - min(nutrition["carbs"], 20)) * 0.1
            )
            # Enhanced food item
            enhanced_food = food.copy()
            enhanced_food["nutritional_metrics"] = {
                "protein_ratio": round(protein_ratio, 3),
                "fat_ratio": round(fat_ratio, 3),
                "carb_ratio": round(carb_ratio, 3),
                "protein_density": round(protein_density, 4),
                "fiber_density": round(fiber_density, 4),
                "satiety_index": round(satiety_index, 2),
                "diet_scores": {
                    "keto": round(keto_score, 2),
                    "paleo": round(paleo_score, 2),
                    "mediterranean": round(mediterranean_score, 2)
                }
            }
            # Add allergen information
            allergens = []
            if "soy" in food.get("tags", []):
                allergens.append("soy")
            if "wheat" in food.get("tags", []):
                allergens.append("gluten")
            if any(dairy in food["name"].lower() for dairy in ["milk", "cheese", "yogurt"]):
                allergens.append("dairy")
            if "nut" in food["name"].lower() or any(nut in food["name"].lower() for nut in ["almond", "walnut", "pecan"]):
                allergens.append("nuts")
            enhanced_food["allergens"] = allergens
            # Add environmental impact score (simplified)
            if "vegan" in food.get("tags", []):
                environmental_score = 0.9
            elif "veg" in food.get("tags", []):
                environmental_score = 0.7
            elif "non_veg" in food.get("tags", []):
                environmental_score = 0.3
            else:
                environmental_score = 0.5
            enhanced_food["environmental_score"] = environmental_score
            enhanced_foods.append(enhanced_food)
        return {"foods": enhanced_foods}
    def save_enhanced_dataset(self, filename="enhanced_foods.json"):
        """
        Generate and save the enhanced food dataset
        """
        print("🍎 Generating enhanced food dataset...")
        # Generate base dataset
        foods_data = self.generate_enhanced_dataset()
        # Add accuracy features
        enhanced_data = self.add_nutritional_accuracy_features(foods_data)
        # Add metadata
        enhanced_data["metadata"] = {
            "version": "2.0",
            "generated_date": datetime.now().isoformat(),
            "total_foods": len(enhanced_data["foods"]),
            "description": "Enhanced food dataset with improved nutritional accuracy and ML features",
            "categories": [
                "proteins", "carbohydrates", "vegetables", "fruits", 
                "healthy_fats", "meal_combinations", "snacks_beverages"
            ],
            "features": [
                "basic_nutrition", "dietary_tags", "cost_level", "meal_types",
                "preparation_info", "seasonal_availability", "nutritional_metrics",
                "allergen_info", "environmental_score"
            ]
        }
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Enhanced dataset saved to {filename}")
        print(f"📊 Total foods: {len(enhanced_data['foods'])}")
        print("🏷️  Categories included:")
        for category in enhanced_data["metadata"]["categories"]:
            print(f"   - {category}")
        return enhanced_data
def main():
    """
    Main execution function
    """
    print("🍎 Enhanced Food Dataset Generator")
    print("=" * 40)
    generator = EnhancedFoodDatasetGenerator()
    # Generate and save enhanced dataset
    enhanced_data = generator.save_enhanced_dataset()
    # Also update the original foods.json for backward compatibility
    simplified_data = {
        "foods": [
            {
                "id": food["id"],
                "name": food["name"],
                "per_100g": food["per_100g"],
                "tags": food["tags"],
                "cost_level": food["cost_level"]
            }
            for food in enhanced_data["foods"]
        ]
    }
    with open("foods.json", 'w', encoding='utf-8') as f:
        json.dump(simplified_data, f, indent=2, ensure_ascii=False)
    print("✅ Updated foods.json for backward compatibility")
    print("\n🎉 Dataset generation complete!")
    print("\nFiles created:")
    print("- enhanced_foods.json (full dataset with ML features)")
    print("- foods.json (simplified for existing system)")
if __name__ == "__main__":
    main()
