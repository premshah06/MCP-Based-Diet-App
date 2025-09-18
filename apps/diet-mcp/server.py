#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import requests
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
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Configuration
API_BASE_URL = os.getenv("DIET_API_URL", "http://diet-api:8000")
FOODS_PATH = Path(__file__).parent.parent.parent / "foods.json"
# Load foods database for resource with better error handling
try:
    with open(FOODS_PATH, 'r', encoding='utf-8') as f:
        FOODS_DATA = json.load(f)
    logger.info(f"Loaded {len(FOODS_DATA.get('foods', []))} foods from {FOODS_PATH}")
except FileNotFoundError:
    logger.warning(f"Foods database not found at {FOODS_PATH}, using empty dataset")
    FOODS_DATA = {"foods": []}
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in foods database: {e}")
    FOODS_DATA = {"foods": []}
except Exception as e:
    logger.error(f"Error loading foods database: {e}")
    FOODS_DATA = {"foods": []}
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
# Tool implementations
async def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make HTTP request to the diet API with improved error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        logger.info(f"Making {method} request to {url}")
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            params = data if data else {}
            response = requests.get(url, params=params, timeout=30)
        logger.info(f"API response status: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to {url}: {e}")
        raise Exception(f"Could not connect to diet API at {API_BASE_URL}. Make sure the diet-api service is running and accessible.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error for {url}: {e}")
        raise Exception("Request to diet API timed out. The service may be overloaded.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error for {url}: {e}")
        if e.response.status_code == 422:
            try:
                error_detail = e.response.json().get('detail', 'Validation error')
            except:
                error_detail = 'Validation error - unable to parse response'
            raise Exception(f"Invalid input parameters: {error_detail}")
        else:
            raise Exception(f"Diet API error ({e.response.status_code}): {e.response.text}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {url}: {e}")
        raise Exception("Invalid JSON response from diet API")
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {e}")
        raise Exception(f"Unexpected error calling diet API: {str(e)}")
@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> List[TextContent]:
    """Handle MCP tool calls"""
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
        else:
            raise ValueError(f"Unknown tool: {request.name}")
    except Exception as e:
        error_text = f"Error executing {request.name}: {str(e)}"
        return [TextContent(type="text", text=error_text)]
async def main():
    """Run the MCP server with improved error handling and health checks"""
    logger.info("Starting Diet Coach MCP server...")
    # Basic health check
    try:
        logger.info("Performing initial health check...")
        # Check if foods data is available
        if not FOODS_DATA.get("foods"):
            logger.warning("No foods data available - this may affect functionality")
        # Test API connectivity (optional, non-blocking)
        try:
            test_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if test_response.status_code == 200:
                logger.info("Diet API is accessible")
            else:
                logger.warning(f"Diet API health check failed: {test_response.status_code}")
        except:
            logger.warning("Could not reach Diet API - will retry during actual requests")
        logger.info("Health check completed")
    except Exception as e:
        logger.warning(f"Health check failed: {e} - continuing with startup")
    try:
        logger.info("Initializing MCP server with stdio transport...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP server running successfully")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="diet-coach-mcp",
                    server_version="1.0.1",
                ),
            )
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP Server error: {e}")
        print(f"MCP Server initialization error: {e}", file=sys.stderr)
        # For debugging, keep container alive for a bit but don't loop forever
        logger.info("Container will remain active for 5 minutes for debugging")
        await asyncio.sleep(300)  # 5 minutes instead of infinite loop
if __name__ == "__main__":
    asyncio.run(main())
