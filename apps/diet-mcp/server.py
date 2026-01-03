#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import traceback
from contextlib import asynccontextmanager
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
)
from pydantic import BaseModel, Field
# Setup enhanced logging with more detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Set specific logger levels for better debugging
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("mcp").setLevel(logging.DEBUG)
# Configuration
API_BASE_URL = os.getenv("DIET_API_URL", "http://diet-api:8000")
FOODS_PATHS = [
    Path("/app/data/enhanced_foods.json"),
    Path("/app/data/foods.json"),
    Path("../diet-api/data/enhanced_foods.json"),
    Path("../diet-api/data/foods.json"),
    Path("apps/diet-api/data/enhanced_foods.json"),
    Path("apps/diet-api/data/foods.json"),
    Path("foods.json"),
    Path("enhanced_foods.json")
]

# Global session for HTTP requests
http_session: Optional[aiohttp.ClientSession] = None

def load_foods_database() -> Dict[str, Any]:
    """Load foods database with multiple fallback paths"""
    for foods_path in FOODS_PATHS:
        try:
            with open(foods_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded {len(data.get('foods', []))} foods from {foods_path}")
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
    
    logger.warning("No foods database found in any fallback path, using empty dataset")
    return {"foods": []}

# Load foods database with fallback paths
FOODS_DATA = load_foods_database()
# Server instance
server = Server("diet-coach-mcp")
# Tool schemas
class CalculateCaloriesArgs(BaseModel):
    sex: str = Field(description="Gender: 'male' or 'female'")
    age: int = Field(ge=10, le=120, description="Age in years (10-120)")
    height_cm: float = Field(ge=100, le=250, description="Height in centimeters (100-250)")
    weight_kg: float = Field(ge=30, le=300, description="Weight in kilograms (30-300)")
    activity_level: str = Field(description="Activity level: 'sedentary', 'light', 'moderate', 'active', 'very_active'")
    goal: str = Field(description="Goal: 'cut' (weight loss), 'maintain' (maintenance), 'bulk' (weight gain)")
class MealPlanArgs(BaseModel):
    calories: float = Field(ge=800, le=6000, description="Daily calorie target (800-6000)")
    protein_g: float = Field(ge=50, le=400, description="Daily protein target in grams (50-400)")
    fat_g: float = Field(ge=20, le=200, description="Daily fat target in grams (20-200)")
    carbs_g: float = Field(ge=50, le=800, description="Daily carbohydrate target in grams (50-800)")
    diet_tags: List[str] = Field(default=[], description="Dietary restrictions: ['veg', 'vegan', 'halal', 'lactose_free', 'budget']")
    days: int = Field(default=7, ge=1, le=14, description="Number of days for meal plan (1-14)")
class ExplainPlanArgs(BaseModel):
    calories: float = Field(description="Daily calorie target")
    protein_g: Optional[float] = Field(default=None, description="Daily protein target in grams")
    fat_g: Optional[float] = Field(default=None, description="Daily fat target in grams") 
    carbs_g: Optional[float] = Field(default=None, description="Daily carbohydrate target in grams")
    constraints: Optional[str] = Field(default=None, description="Additional constraints or context")


class GroceryListArgs(BaseModel):
    meal_plan: Dict[str, Any] = Field(description="The complete meal plan object")
    budget: Optional[str] = Field(default="moderate", description="Budget preference: 'low', 'moderate', 'high'")


class GenerateRecipeArgs(BaseModel):
    meal: Dict[str, Any] = Field(description="The specific meal object from the plan")
    constraints: Optional[str] = Field(default=None, description="User dietary restrictions or context")
# Tool definitions
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="calculate_calories",
            description="Calculate TDEE (Total Daily Energy Expenditure) and macro targets based on personal stats and goals",
            inputSchema=CalculateCaloriesArgs.model_json_schema()
        ),
        Tool(
            name="meal_plan",
            description="Generate a personalized meal plan based on calorie and macro targets with dietary restrictions",
            inputSchema=MealPlanArgs.model_json_schema()
        ),
        Tool(
            name="explain_plan",
            description="Get detailed explanation and rationale for nutrition recommendations and meal plans",
            inputSchema=ExplainPlanArgs.model_json_schema()
        ),
        Tool(
            name="grocery_list",
            description="Generate a consolidated, categorized grocery shopping list from a meal plan",
            inputSchema=GroceryListArgs.model_json_schema()
        ),
        Tool(
            name="generate_recipe",
            description="Generate detailed step-by-step cooking instructions and tips for a specific meal",
            inputSchema=GenerateRecipeArgs.model_json_schema()
        )
    ]
# Resource definitions
@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available MCP resources"""
    return [
        Resource(
            uri="file://diet/foods",
            name="Foods Database",
            description="Complete database of foods with nutritional information per 100g including calories, macros, and dietary tags",
            mimeType="application/json"
        )
    ]
@server.read_resource()
async def handle_read_resource(request: ReadResourceRequest) -> str:
    """Read MCP resource content"""
    if request.uri == "file://diet/foods":
        return json.dumps(FOODS_DATA, indent=2)
    else:
        raise ValueError(f"Unknown resource: {request.uri}")
# Session management
@asynccontextmanager
async def get_http_session():
    """Get or create HTTP session with proper cleanup"""
    global http_session
    if http_session is None or http_session.closed:
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        http_session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'Content-Type': 'application/json'},
            connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
        )
    try:
        yield http_session
    except Exception:
        # Session will be cleaned up in main() if needed
        raise

async def cleanup_session():
    """Clean up HTTP session"""
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()
        http_session = None

# Tool implementations
async def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make async HTTP request to the diet API with comprehensive error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        logger.info(f"🌐 Making {method} request to {url}")
        
        async with get_http_session() as session:
            if method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    response_text = await response.text()
                    logger.info(f"📡 API response status: {response.status}")
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 422:
                        try:
                            error_data = await response.json()
                            error_detail = error_data.get('detail', 'Validation error')
                        except:
                            error_detail = 'Validation error - unable to parse response'
                        raise Exception(f"Invalid input parameters: {error_detail}")
                    else:
                        raise Exception(f"Diet API error ({response.status}): {response_text}")
            else:  # GET
                params = data if data else {}
                async with session.get(url, params=params) as response:
                    response_text = await response.text()
                    logger.info(f"📡 API response status: {response.status}")
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 422:
                        try:
                            error_data = await response.json()
                            error_detail = error_data.get('detail', 'Validation error')
                        except:
                            error_detail = 'Validation error - unable to parse response'
                        raise Exception(f"Invalid input parameters: {error_detail}")
                    else:
                        raise Exception(f"Diet API error ({response.status}): {response_text}")
                        
    except asyncio.TimeoutError:
        logger.error(f"⏰ Timeout error for {url}")
        raise Exception("Request to diet API timed out. The service may be overloaded.")
    except aiohttp.ClientConnectorError as e:
        logger.error(f"🔌 Connection error to {url}: {e}")
        raise Exception(f"Could not connect to diet API at {API_BASE_URL}. Make sure the diet-api service is running and accessible.")
    except aiohttp.ClientError as e:
        logger.error(f"🚫 Client error for {url}: {e}")
        raise Exception(f"HTTP client error: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"🔧 JSON decode error for {url}: {e}")
        raise Exception("Invalid JSON response from diet API")
    except Exception as e:
        logger.error(f"💥 Unexpected error for {url}: {e}")
        logger.error(f"💥 Traceback: {traceback.format_exc()}")
        raise Exception(f"Unexpected error calling diet API: {str(e)}")
@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> List[TextContent]:
    """Handle MCP tool calls"""
    logger.debug(f"🔧 Tool call received: {request.name}")
    logger.debug(f"🔧 Tool arguments: {request.arguments}")
    
    try:
        if request.name == "calculate_calories":
            # Validate arguments
            args = CalculateCaloriesArgs.model_validate(request.arguments)
            # Call TDEE endpoint
            result = await make_api_request("/tdee", "POST", args.model_dump())
            # Format response
            response_text = f"""**TDEE Calculation Results**
**Personal Stats:**
- Sex: {args.sex.title()}
- Age: {args.age} years
- Height: {args.height_cm} cm
- Weight: {args.weight_kg} kg
- Activity Level: {args.activity_level.replace('_', ' ').title()}
- Goal: {args.goal.title()}
**Metabolic Calculations:**
- BMR (Basal Metabolic Rate): {result['bmr']} calories/day
- Activity Factor: {result['activity_factor']}x
- TDEE (Total Daily Energy Expenditure): {result['tdee']} calories/day
- Target Calories for Goal: {result['target_calories']} calories/day
**Daily Macro Targets:**
- Protein: {result['macro_targets']['protein_g']}g ({round((result['macro_targets']['protein_g'] * 4 / result['target_calories']) * 100, 1)}% of calories)
- Fat: {result['macro_targets']['fat_g']}g ({round((result['macro_targets']['fat_g'] * 9 / result['target_calories']) * 100, 1)}% of calories)
- Carbohydrates: {result['macro_targets']['carbs_g']}g ({round((result['macro_targets']['carbs_g'] * 4 / result['target_calories']) * 100, 1)}% of calories)
These targets are calculated using the Mifflin-St Jeor equation for BMR and adjusted based on your activity level and goal."""
            return [TextContent(type="text", text=response_text)]
        elif request.name == "meal_plan":
            # Validate arguments
            args = MealPlanArgs.model_validate(request.arguments)
            # Call meal plan endpoint
            result = await make_api_request("/mealplan", "POST", args.model_dump())
            # Format response
            diet_tags_str = ", ".join(args.diet_tags) if args.diet_tags else "None"
            response_text = f"""**{args.days}-Day Meal Plan**
**Targets:** {args.calories} calories, {args.protein_g}g protein, {args.fat_g}g fat, {args.carbs_g}g carbs
**Dietary Restrictions:** {diet_tags_str}
**Plan Adherence Score:** {result['adherence_score']:.1%}
"""
            # Add each day
            for day in result['days']:
                response_text += f"**Day {day['day']}:**\n"
                for meal in day['meals']:
                    response_text += f"\n*{meal['name']}:*\n"
                    for food in meal['foods']:
                        response_text += f"- {food['name']}: {food['amount_g']}g ({food['calories']} cal, {food['protein']}g P, {food['fat']}g F, {food['carbs']}g C)\n"
                    response_text += f"  *Meal totals: {meal['totals']['calories']} cal, {meal['totals']['protein']}g P, {meal['totals']['fat']}g F, {meal['totals']['carbs']}g C*\n"
                dt = day['daily_totals']
                response_text += f"\n*Day {day['day']} totals: {dt['calories']} cal, {dt['protein']}g P, {dt['fat']}g F, {dt['carbs']}g C*\n\n"
            # Add plan summary
            pt = result['plan_totals']
            response_text += f"""**Plan Summary:**
- Total Calories: {pt['calories']} ({pt['avg_daily_calories']}/day avg)
- Total Protein: {pt['protein']}g ({pt['protein']/args.days:.1f}g/day avg)
- Total Fat: {pt['fat']}g ({pt['fat']/args.days:.1f}g/day avg)
- Total Carbs: {pt['carbs']}g ({pt['carbs']/args.days:.1f}g/day avg)
- Adherence Score: {result['adherence_score']:.1%}
*Note: Adjust portion sizes as needed based on hunger, energy levels, and progress toward your goals.*"""
            return [TextContent(type="text", text=response_text)]
        elif request.name == "explain_plan":
            # Validate arguments
            args = ExplainPlanArgs.model_validate(request.arguments)
            # Prepare query parameters
            params = {"calories": args.calories}
            if args.protein_g is not None:
                params["protein_g"] = args.protein_g
            if args.fat_g is not None:
                params["fat_g"] = args.fat_g
            if args.carbs_g is not None:
                params["carbs_g"] = args.carbs_g
            if args.constraints:
                params["constraints"] = args.constraints
            # Call explain endpoint
            result = await make_api_request("/explain", "GET", params)
            response_text = f"""**Nutrition Plan Explanation**
{result['explanation']}
*This explanation considers your specific calorie and macro targets along with any dietary constraints you've mentioned. Use this guidance to better understand your nutrition plan and make informed adjustments as needed.*"""
            return [TextContent(type="text", text=response_text)]
        elif request.name == "grocery_list":
            args = GroceryListArgs.model_validate(request.arguments)
            payload = {
                "meal_plan": args.meal_plan,
                "preferences": {"budget": args.budget}
            }
            result = await make_api_request("/ai/grocery-list", "POST", payload)
            
            gl = result['grocery_list']
            response_text = f"## 🛒 Smart Grocery List\n\n"
            for category in gl['categories']:
                response_text += f"### {category['icon']} {category['name']}\n"
                for item in category['items']:
                    line = f"- [ ] **{item['name']}**: {item['quantity']} {item['unit']}"
                    if item.get('notes'): line += f" ({item['notes']})"
                    response_text += line + "\n"
                response_text += "\n"
            
            response_text += "### 💡 Shopping Tips\n"
            for tip in gl['shopping_tips']:
                response_text += f"- {tip}\n"
            
            return [TextContent(type="text", text=response_text)]
        elif request.name == "generate_recipe":
            args = GenerateRecipeArgs.model_validate(request.arguments)
            payload = {
                "meal": args.meal,
                "context": {"constraints": args.constraints} if args.constraints else {}
            }
            result = await make_api_request("/ai/recipe", "POST", payload)
            
            r = result['recipe']
            response_text = f"# 🍳 {r['title']}\n"
            response_text += f"**⏱️ Prep:** {r['prep_time']} | **🔥 Cook:** {r['cook_time']} | **📊 Difficulty:** {r['difficulty']}\n\n"
            
            response_text += "## 🧂 Ingredients\n"
            for ing in r['ingredients']:
                response_text += f"- {ing['name']}: {ing['amount']}\n"
            
            response_text += "\n## 🥣 Instructions\n"
            for i, step in enumerate(r['instructions'], 1):
                response_text += f"{i}. {step}\n"
            
            response_text += "\n## 💡 Chef's Tips\n"
            for tip in r['tips']:
                response_text += f"- {tip}\n"
                
            return [TextContent(type="text", text=response_text)]
        else:
            raise ValueError(f"Unknown tool: {request.name}")
    except Exception as e:
        logger.error(f"❌ Tool execution error for {request.name}: {str(e)}")
        logger.error(f"❌ Full error details: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        error_text = f"Error executing {request.name}: {str(e)}\n\nThis is likely due to:\n1. API connection issues\n2. Invalid input parameters\n3. Service dependencies not running\n\nPlease check the logs for more details."
        return [TextContent(type="text", text=error_text)]
async def health_check() -> bool:
    """Perform comprehensive health check"""
    logger.info("🏥 Performing health check...")
    
    # Check foods data availability
    foods_count = len(FOODS_DATA.get("foods", []))
    if foods_count == 0:
        logger.warning("⚠️ No foods data available - this may affect functionality")
    else:
        logger.info(f"✅ Foods database loaded with {foods_count} items")
    
    # Test API connectivity (async, non-blocking)
    api_healthy = False
    try:
        async with get_http_session() as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    logger.info("✅ Diet API is accessible")
                    api_healthy = True
                else:
                    logger.warning(f"⚠️ Diet API health check failed: {response.status}")
    except Exception as e:
        logger.warning(f"⚠️ Could not reach Diet API: {e} - will retry during actual requests")
    
    logger.info(f"🏥 Health check completed - Foods: {'✅' if foods_count > 0 else '⚠️'}, API: {'✅' if api_healthy else '⚠️'}")
    return foods_count > 0 and api_healthy

async def main():
    """Run the MCP server with enhanced async handling and proper cleanup"""
    logger.info("🚀 Starting Diet Coach MCP server...")
    logger.debug(f"🔧 API Base URL: {API_BASE_URL}")
    logger.debug(f"🔧 Foods Paths: {[str(p) for p in FOODS_PATHS]}")
    logger.debug(f"🔧 Python version: {sys.version}")
    
    try:
        # Perform health check
        await health_check()
        
        # Initialize MCP server
        logger.info("🔌 Initializing MCP server with stdio transport...")
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ MCP server running successfully")
            logger.info("🎯 Available tools: calculate_calories, meal_plan, explain_plan")
            logger.info("📚 Available resources: file://diet/foods")
            
            try:
                await server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="diet-coach-mcp",
                        server_version="2.0.0",
                    ),
                )
            except asyncio.CancelledError:
                logger.info("🛑 MCP server cancelled")
                raise
            except Exception as e:
                logger.error(f"❌ MCP server runtime error: {e}")
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                raise
                
    except KeyboardInterrupt:
        logger.info("🛑 MCP server stopped by user")
    except Exception as e:
        logger.error(f"💥 MCP Server error: {e}")
        logger.error(f"💥 Full traceback: {traceback.format_exc()}")
        print(f"MCP Server initialization error: {e}", file=sys.stderr)
        
        # Keep container alive briefly for debugging, but not indefinitely
        logger.info("🐛 Container will remain active for debugging (60 seconds)")
        await asyncio.sleep(60)
    finally:
        # Cleanup resources
        logger.info("🧹 Cleaning up resources...")
        try:
            await cleanup_session()
            logger.info("✅ Resource cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
if __name__ == "__main__":
    asyncio.run(main())
