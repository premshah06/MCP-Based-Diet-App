import os
import json
import logging
from openai import AsyncOpenAI
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# AI Service Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HISTORY_FILE = Path(os.getenv("HISTORY_FILE", "/app/chat_history.json"))

# Fallback paths for history file
HISTORY_PATHS = [
    Path("/app/chat_history.json"),
    Path("chat_history.json"),
    Path("./chat_history.json"),
]


class AIProvider(str, Enum):
    OPENAI = "openai"


@dataclass
class ChatMessage:
    """Chat message data model"""
    role: str  # system, user, assistant
    content: str
    image_data: Optional[str] = None  # Base64 encoded image
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = {"role": self.role, "content": self.content}
        if self.image_data:
            d["image_data"] = self.image_data
        if self.timestamp:
            d["timestamp"] = self.timestamp
        return d


@dataclass
class ChatResponse:
    """AI response data model"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None


# Nutrition coaching system prompt
SYSTEM_PROMPT = """You are an expert AI nutrition coach with deep knowledge of:
- Dietetics and nutritional science
- Macronutrient optimization (proteins, fats, carbohydrates)
- Micronutrient balance (vitamins, minerals)
- Meal planning and food combinations
- Dietary restrictions (vegan, vegetarian, halal, kosher, allergies)
- Fitness goals (weight loss, muscle gain, maintenance, athletic performance)
- Cultural food preferences and international cuisines

Your role is to:
1. Provide personalized, science-based nutrition advice
2. Answer questions about food, nutrition, and healthy eating
3. Suggest meal ideas and food substitutions
4. Explain nutritional concepts in simple terms
5. Help users understand their macro and calorie targets
6. Be encouraging and supportive of their health journey

Guidelines:
- Always be friendly, supportive, and non-judgmental
- Provide accurate, evidence-based information
- When unsure, acknowledge limitations and suggest consulting a healthcare professional
- Consider user's dietary restrictions and preferences
- Make recommendations practical and achievable
- Use emojis occasionally to make responses engaging
- Keep responses concise but informative

Remember: You are not a doctor. Always recommend consulting healthcare professionals for medical advice."""


RECIPE_SYSTEM_PROMPT = """You are a professional chef and nutritionist. Your task is to provide clear, healthy, and easy-to-follow recipes based on the ingredients provided.

Guidelines for recipes:
1. Provide a catchy title
2. List prep time, cook time, and difficulty
3. List equipment needed
4. Provide clear, numbered step-by-step instructions
5. Include chef's tips for better flavor or easier prep
6. Mention nutritional highlights (e.g., "high protein", "rich in fiber")
7. Suggest simple swaps for dietary restrictions if relevant

Format the recipe as a clean, structured JSON object."""


GROCERY_SYSTEM_PROMPT = """You are an expert grocery list generator and meal planning assistant. 

Your task is to create organized, practical grocery lists based on meal plans.

When generating grocery lists:
1. Organize items by category (Produce, Proteins, Dairy, Grains, Pantry, etc.)
2. Combine similar ingredients across meals
3. Suggest approximate quantities
4. Include helpful notes (e.g., "buy fresh" or "frozen works")
5. Consider budget-friendly alternatives when appropriate
6. Account for common pantry staples the user likely has

Format your grocery list as a clean, organized JSON structure."""


class AIService:
    """OpenAI-powered AI service for nutrition coaching"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.history_file = self._find_history_file()
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
        self._load_history()
    
    def _find_history_file(self) -> Path:
        """Find or create history file, prioritizing HISTORY_FILE env var"""
        # Try specific history file from env first
        if HISTORY_FILE and (HISTORY_FILE.parent.exists() or HISTORY_FILE.exists()):
            return HISTORY_FILE

        for path in HISTORY_PATHS:
            if path.exists():
                return path
        
        # Create new file in first available path
        history_file = HISTORY_FILE if HISTORY_FILE else HISTORY_PATHS[0]
        if not history_file.parent.exists():
            history_file = HISTORY_PATHS[1]
            
        try:
            if not history_file.exists():
                history_file.write_text(json.dumps({}))
        except Exception:
            pass
        return history_file

    def _load_history(self):
        """Load conversation history from file"""
        try:
            if self.history_file.exists():
                data = json.loads(self.history_file.read_text())
                for user_id, messages in data.items():
                    self.conversation_history[user_id] = [
                        ChatMessage(**msg) for msg in messages
                    ]
                logger.info(f"✅ Loaded chat history for {len(self.conversation_history)} users")
        except Exception as e:
            logger.error(f"❌ Error loading history: {e}")
            self.conversation_history = {}

    def _save_history(self):
        """Save conversation history to file"""
        try:
            data = {
                uid: [m.to_dict() for m in msgs] 
                for uid, msgs in self.conversation_history.items()
            }
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"❌ Error saving history: {e}")
    
    async def close(self):
        """Close OpenAI client (no-op for SDK)"""
        pass
    
    async def chat(
        self,
        message: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        image_data: Optional[str] = None
    ) -> ChatResponse:
        """
        Send a chat message and get AI response
        
        Args:
            message: User's message
            user_id: Optional user ID for conversation tracking
            context: Optional context (user profile, nutrition data, etc.)
            image_data: Optional base64 image data for Vision
        
        Returns:
            ChatResponse with AI's response
        """
        # Build conversation context
        messages = self._build_messages(message, user_id, context, image_data)
        
        try:
            response = await self._chat_openai(messages)
            
            # Store in conversation history
            if user_id:
                self._add_to_history(user_id, ChatMessage("user", message, image_data=image_data))
                self._add_to_history(user_id, ChatMessage("assistant", response.content))
            
            return response
            
        except Exception as e:
            logger.error(f"❌ OpenAI chat error: {e}")
            # Fallback to basic response
            return ChatResponse(
                content=self._get_fallback_response(message, context),
                provider="fallback",
                model="rule-based"
            )
    
    def _build_messages(
        self,
        message: str,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]],
        image_data: Optional[str] = None
    ) -> List[ChatMessage]:
        """Build message list with system prompt and context"""
        messages = [ChatMessage("system", SYSTEM_PROMPT)]
        
        # Add user context if available
        if context:
            context_str = self._format_context(context)
            messages.append(ChatMessage("system", f"User Context:\n{context_str}"))
        
        # Add conversation history
        if user_id and user_id in self.conversation_history:
            # Keep last 10 messages for context
            history = self.conversation_history[user_id][-10:]
            messages.extend(history)
        
        # Add current message
        messages.append(ChatMessage("user", message, image_data=image_data))
        
        return messages
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format user context for system prompt"""
        parts = []
        
        if "profile" in context:
            profile = context["profile"]
            parts.append(f"- Age: {profile.get('age', 'N/A')}")
            parts.append(f"- Sex: {profile.get('sex', 'N/A')}")
            parts.append(f"- Goal: {profile.get('goal', 'N/A')}")
            parts.append(f"- Activity Level: {profile.get('activity_level', 'N/A')}")
        
        if "nutrition" in context:
            nutrition = context["nutrition"]
            parts.append(f"- Daily Calories Target: {nutrition.get('target_calories', 'N/A')} kcal")
            macros = nutrition.get("macro_targets", {})
            parts.append(f"- Protein Target: {macros.get('protein_g', 'N/A')}g")
            parts.append(f"- Fat Target: {macros.get('fat_g', 'N/A')}g")
            parts.append(f"- Carbs Target: {macros.get('carbs_g', 'N/A')}g")
        
        if "diet_tags" in context:
            parts.append(f"- Dietary Restrictions: {', '.join(context['diet_tags']) or 'None'}")
        
        return "\n".join(parts) if parts else "No context available"

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Robust JSON extraction from AI response text"""
        if not text:
            return None
            
        # Clean up markdown code fences if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            # Try direct parse first
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback to regex search for the first { ... } block
            import re
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    return None
        return None
    
    async def _chat_openai(self, messages: List[ChatMessage]) -> ChatResponse:
        """Chat using official OpenAI SDK (supports Vision gpt-4o)"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized (check API key)")
        
        openai_messages = []
        for m in messages:
            if m.image_data:
                content = [
                    {"type": "text", "text": m.content},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{m.image_data}"}
                    }
                ]
                openai_messages.append({"role": m.role, "content": content})
            else:
                openai_messages.append({"role": m.role, "content": m.content})
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=openai_messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            choice = response.choices[0]
            
            return ChatResponse(
                content=choice.message.content,
                provider="openai",
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=choice.finish_reason
            )
        except Exception as e:
            logger.error(f"OpenAI SDK error: {e}")
            raise
    

    def _get_fallback_response(self, message: str, context: Optional[Dict]) -> str:
        """Generate a basic fallback response when AI is unavailable"""
        message_lower = message.lower()
        
        if "calorie" in message_lower or "calories" in message_lower:
            return "🔥 Calories are units of energy from food. Your daily needs depend on age, sex, weight, height, and activity level. I recommend using our TDEE calculator for personalized targets!"
        
        if "protein" in message_lower:
            return "💪 Protein is essential for muscle building and repair. Great sources include chicken, fish, eggs, tofu, legumes, and Greek yogurt. Aim for 0.8-1g per pound of body weight for muscle building goals."
        
        if "carb" in message_lower or "carbohydrate" in message_lower:
            return "🍞 Carbohydrates are your body's main energy source. Focus on complex carbs like whole grains, vegetables, and legumes for sustained energy. Simple carbs from fruits are great pre/post workout!"
        
        if "fat" in message_lower:
            return "🥑 Healthy fats are crucial for hormone production and nutrient absorption. Include sources like avocados, nuts, olive oil, and fatty fish. Aim for 20-35% of your daily calories from fats."
        
        if "meal" in message_lower or "eat" in message_lower:
            return "🍽️ A balanced meal includes protein (palm-sized portion), complex carbs (fist-sized), vegetables (half the plate), and healthy fats. Check out our meal planning feature for personalized suggestions!"
        
        if "weight loss" in message_lower or "lose weight" in message_lower:
            return "⚖️ For sustainable weight loss, aim for a 300-500 calorie deficit. Focus on protein to preserve muscle, fiber for satiety, and plenty of water. Combine with regular exercise for best results!"
        
        if "muscle" in message_lower or "bulk" in message_lower:
            return "🏋️ For muscle building, eat in a slight caloric surplus (200-300 calories), prioritize protein (1g per lb bodyweight), train consistently, and get adequate rest. Our bulk mode can help customize your targets!"
        
        return "👋 I'm your AI nutrition coach! Ask me about calories, macros, meal planning, weight loss, muscle building, or any nutrition questions. I'm here to help you on your health journey!"
    
    def _add_to_history(self, user_id: str, message: ChatMessage):
        """Add message to conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        message.timestamp = datetime.utcnow().isoformat()
        self.conversation_history[user_id].append(message)
        
        # Keep only last 50 messages per user
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]
        
        self._save_history()
    
    def get_history(self, user_id: str) -> List[ChatMessage]:
        """Get history for a user"""
        return self.conversation_history.get(user_id, [])

    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            self._save_history()
    
    async def generate_recipe(
        self,
        meal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a step-by-step recipe for a meal
        """
        prompt = f"""Generate a detailed recipe for this meal.
Meal: {meal.get('name')}
Ingredients: {json.dumps(meal.get('foods', []), indent=2)}
"""
        if context:
            prompt += f"\nUser Context: {json.dumps(context, indent=2)}"

        prompt += """
Please provide the response in this JSON format:
{
  "title": "Recipe Title",
  "prep_time": "min",
  "cook_time": "min",
  "difficulty": "Easy/Medium/Hard",
  "equipment": ["item1", "item2"],
  "ingredients": [{"name": "item", "amount": "quantity"}],
  "instructions": ["Step 1", "Step 2"],
  "tips": ["Tip 1"],
  "nutritional_highlights": ["Highlight 1"]
}"""

        messages = [
            ChatMessage("system", RECIPE_SYSTEM_PROMPT),
            ChatMessage("user", prompt)
        ]
        
        try:
            response = await self._chat_openai(messages)
            
            # Extract JSON using robust method
            recipe = self._extract_json(response.content)
            if not recipe:
                raise Exception("Could not parse recipe JSON from AI response")
                
            return {
                "success": True,
                "recipe": recipe,
                "provider": response.provider
            }
            
        except Exception as e:
            logger.error(f"Recipe generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "Sorry, I couldn't generate a detailed recipe right now. Use the ingredients listed to prepare your meal!"
            }

    async def generate_grocery_list(
        self,
        meal_plan: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a smart grocery list from a meal plan
        
        Args:
            meal_plan: Meal plan data with days and meals
            preferences: User preferences (budget, store preferences, etc.)
        
        Returns:
            Organized grocery list with categories
        """
        # Build prompt
        prompt = self._build_grocery_prompt(meal_plan, preferences)
        
        messages = [
            ChatMessage("system", GROCERY_SYSTEM_PROMPT),
            ChatMessage("user", prompt)
        ]
        
        try:
            response = await self._chat_openai(messages)
            
            # Parse the response
            grocery_list = self._parse_grocery_response(response.content, meal_plan)
            
            return {
                "success": True,
                "grocery_list": grocery_list,
                "provider": response.provider,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Grocery list generation error: {e}")
            # Fall back to basic extraction
            return {
                "success": True,
                "grocery_list": self._extract_basic_grocery_list(meal_plan),
                "provider": "fallback",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _build_grocery_prompt(
        self,
        meal_plan: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for grocery list generation"""
        # Extract all foods from meal plan
        foods = []
        for day in meal_plan.get("days", []):
            for meal in day.get("meals", []):
                for food in meal.get("foods", []):
                    foods.append({
                        "name": food.get("name"),
                        "amount_g": food.get("amount_g")
                    })
        
        prompt = f"""Generate a comprehensive grocery list for the following meal plan.

Meal Plan Foods:
{json.dumps(foods, indent=2)}

Number of Days: {len(meal_plan.get('days', []))}
"""
        
        if preferences:
            if preferences.get("budget"):
                prompt += f"\nBudget Level: {preferences['budget']}"
            if preferences.get("store"):
                prompt += f"\nPreferred Store: {preferences['store']}"
            if preferences.get("dietary_restrictions"):
                prompt += f"\nDietary Restrictions: {', '.join(preferences['dietary_restrictions'])}"
        
        prompt += """

Please generate a JSON grocery list with the following format:
{
  "categories": [
    {
      "name": "Category Name",
      "icon": "emoji",
      "items": [
        {
          "name": "Item Name",
          "quantity": "Amount needed",
          "unit": "unit of measure",
          "notes": "optional tips",
          "estimated_price": "optional price estimate"
        }
      ]
    }
  ],
  "total_items": number,
  "shopping_tips": ["tip1", "tip2"],
  "estimated_total": "optional total estimate"
}"""
        
        return prompt
    
    def _parse_grocery_response(
        self,
        response: str,
        meal_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse AI response to extract grocery list using robust method"""
        recipe = self._extract_json(response)
        if recipe:
            return recipe
        
        # Fall back to basic extraction
        return self._extract_basic_grocery_list(meal_plan)
    
    def _extract_basic_grocery_list(self, meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic grocery list from meal plan without AI"""
        # Collect all foods
        food_counts: Dict[str, Dict[str, Any]] = {}
        
        for day in meal_plan.get("days", []):
            for meal in day.get("meals", []):
                for food in meal.get("foods", []):
                    name = food.get("name", "Unknown")
                    amount = food.get("amount_g", 0)
                    
                    if name in food_counts:
                        food_counts[name]["total_g"] += amount
                        food_counts[name]["count"] += 1
                    else:
                        food_counts[name] = {
                            "total_g": amount,
                            "count": 1,
                            "category": self._categorize_food(name)
                        }
        
        # Organize by category
        categories_map = {}
        for food_name, data in food_counts.items():
            category = data["category"]
            if category not in categories_map:
                categories_map[category] = {
                    "name": category,
                    "icon": self._get_category_icon(category),
                    "items": []
                }
            
            categories_map[category]["items"].append({
                "name": food_name,
                "quantity": f"{round(data['total_g'])}g total",
                "unit": "g",
                "notes": f"Used in {data['count']} meals"
            })
        
        return {
            "categories": list(categories_map.values()),
            "total_items": len(food_counts),
            "shopping_tips": [
                "Buy fresh produce closer to when you'll use it",
                "Check your pantry for staples before shopping",
                "Consider buying in bulk for items used frequently"
            ]
        }
    
    def _categorize_food(self, food_name: str) -> str:
        """Categorize food by name"""
        food_lower = food_name.lower()
        
        proteins = ["chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp", "tofu", "tempeh", "eggs", "turkey"]
        dairy = ["milk", "cheese", "yogurt", "butter", "cream"]
        grains = ["rice", "bread", "pasta", "oats", "quinoa", "cereal", "tortilla"]
        produce = ["apple", "banana", "orange", "spinach", "broccoli", "carrot", "tomato", "lettuce", "avocado", "pepper", "onion", "garlic"]
        legumes = ["beans", "lentils", "chickpeas", "peas"]
        nuts = ["almonds", "walnuts", "peanut", "cashew", "seeds"]
        
        for protein in proteins:
            if protein in food_lower:
                return "🥩 Proteins"
        
        for item in dairy:
            if item in food_lower:
                return "🥛 Dairy"
        
        for grain in grains:
            if grain in food_lower:
                return "🌾 Grains & Bread"
        
        for item in produce:
            if item in food_lower:
                return "🥬 Fresh Produce"
        
        for legume in legumes:
            if legume in food_lower:
                return "🫘 Legumes"
        
        for nut in nuts:
            if nut in food_lower:
                return "🥜 Nuts & Seeds"
        
        return "🛒 Other"
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for category"""
        icons = {
            "🥩 Proteins": "🥩",
            "🥛 Dairy": "🥛",
            "🌾 Grains & Bread": "🌾",
            "🥬 Fresh Produce": "🥬",
            "🫘 Legumes": "🫘",
            "🥜 Nuts & Seeds": "🥜",
            "🛒 Other": "🛒"
        }
        return icons.get(category, "🛒")



# Global AI service instance
ai_service = AIService()
