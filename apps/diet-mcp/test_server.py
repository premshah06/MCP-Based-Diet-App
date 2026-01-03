from mcp.types import CallToolRequest, ListResourcesRequest, ReadResourceRequest
from unittest.mock import patch, Mock, AsyncMock

import asyncio
import json
import pytest
# Import the server components
from server import (
    handle_list_tools, 
    handle_list_resources, 
    handle_read_resource,
    handle_call_tool,
    make_api_request,
    CalculateCaloriesArgs,
    MealPlanArgs,
    ExplainPlanArgs
)
class TestSchemaValidation:
    """Test Pydantic schema validation"""
    def test_calculate_calories_args_valid(self, sample_calculate_calories_args):
        """Test valid calculate calories arguments"""
        args = CalculateCaloriesArgs.model_validate(sample_calculate_calories_args)
        assert args.sex == "male"
        assert args.age == 30
        assert args.height_cm == 175
        assert args.weight_kg == 70
        assert args.activity_level == "moderate"
        assert args.goal == "cut"
    def test_calculate_calories_args_invalid_age(self):
        """Test invalid age in calculate calories arguments"""
        args_data = {
            "sex": "male",
            "age": 5,  # Too young
            "height_cm": 175,
            "weight_kg": 70,
            "activity_level": "moderate",
            "goal": "cut"
        }
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CalculateCaloriesArgs.model_validate(args_data)
    def test_meal_plan_args_valid(self, sample_meal_plan_args):
        """Test valid meal plan arguments"""
        args = MealPlanArgs.model_validate(sample_meal_plan_args)
        assert args.calories == 2000
        assert args.protein_g == 150
        assert args.days == 3
        assert "veg" in args.diet_tags
    def test_meal_plan_args_defaults(self):
        """Test meal plan arguments with defaults"""
        args_data = {
            "calories": 1800,
            "protein_g": 120,
            "fat_g": 60,
            "carbs_g": 180
        }
        args = MealPlanArgs.model_validate(args_data)
        assert args.diet_tags == []  # Default empty list
        assert args.days == 7  # Default 7 days
    def test_explain_plan_args_minimal(self):
        """Test explain plan arguments with minimal data"""
        args_data = {"calories": 2000}
        args = ExplainPlanArgs.model_validate(args_data)
        assert args.calories == 2000
        assert args.protein_g is None
        assert args.constraints is None
class TestMCPHandlers:
    """Test MCP protocol handlers"""
    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        """Test listing available tools"""
        tools = await handle_list_tools()
        assert len(tools) == 3
        tool_names = [tool.name for tool in tools]
        assert "calculate_calories" in tool_names
        assert "meal_plan" in tool_names
        assert "explain_plan" in tool_names
        # Check that each tool has proper schema
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
    @pytest.mark.asyncio
    async def test_handle_list_resources(self):
        """Test listing available resources"""
        resources = await handle_list_resources()
        assert len(resources) == 1
        resource = resources[0]
        assert resource.uri == "file://diet/foods"
        assert resource.name == "Foods Database"
        assert resource.mimeType == "application/json"
    @pytest.mark.asyncio
    async def test_handle_read_resource_foods(self, test_foods_file, test_foods_data):
        """Test reading foods resource"""
        # Create mock request object
        class MockRequest:
            uri = "file://diet/foods"
        request = MockRequest()
        content = await handle_read_resource(request)
        # Should return JSON string
        assert isinstance(content, str)
        # Should be valid JSON containing foods data
        data = json.loads(content)
        assert "foods" in data
        assert len(data["foods"]) == len(test_foods_data["foods"])
    @pytest.mark.asyncio
    async def test_handle_read_resource_invalid(self):
        """Test reading invalid resource"""
        # Create mock request object
        class MockRequest:
            uri = "invalid/resource"
        request = MockRequest()
        with pytest.raises(ValueError, match="Unknown resource"):
            await handle_read_resource(request)
class TestAPIRequests:
    """Test API request functionality"""
    @pytest.mark.asyncio
    @patch('server.requests.post')
    async def test_make_api_request_post_success(self, mock_post):
        """Test successful POST API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        result = await make_api_request("/test", "POST", {"data": "test"})
        assert result == {"result": "success"}
        mock_post.assert_called_once_with(
            "http://diet-api:8000/test",
            json={"data": "test"},
            timeout=30
        )
    @pytest.mark.asyncio
    @patch('server.requests.get')
    async def test_make_api_request_get_success(self, mock_get):
        """Test successful GET API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        result = await make_api_request("/test", "GET", {"param": "value"})
        assert result == {"result": "success"}
        mock_get.assert_called_once_with(
            "http://diet-api:8000/test",
            params={"param": "value"},
            timeout=30
        )
    @pytest.mark.asyncio
    @patch('server.requests.post')
    async def test_make_api_request_connection_error(self, mock_post):
        """Test API request with connection error"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(Exception, match="Could not connect to diet API"):
            await make_api_request("/test", "POST", {})
    @pytest.mark.asyncio
    @patch('server.requests.post')
    async def test_make_api_request_timeout(self, mock_post):
        """Test API request timeout"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        with pytest.raises(Exception, match="Request to diet API timed out"):
            await make_api_request("/test", "POST", {})
    @pytest.mark.asyncio
    @patch('server.requests.post')
    async def test_make_api_request_http_error_422(self, mock_post):
        """Test API request with validation error"""
        import requests
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"detail": "Validation failed"}
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error
        with pytest.raises(Exception, match="Invalid input parameters"):
            await make_api_request("/test", "POST", {})
class TestToolExecution:
    """Test MCP tool execution"""
    @pytest.mark.asyncio
    @patch('server.make_api_request')
    async def test_calculate_calories_tool(self, mock_api, sample_calculate_calories_args, mock_api_success):
        """Test calculate_calories tool execution"""
        mock_api.return_value = mock_api_success("/tdee", "POST")
        # Create mock request object
        class MockRequest:
            name = "calculate_calories"
            arguments = sample_calculate_calories_args
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        assert result[0].type == "text"
        content = result[0].text
        # Check that response contains expected information
        assert "TDEE Calculation Results" in content
        assert "Male" in content
        assert "30 years" in content
        assert "175 cm" in content
        assert "70 kg" in content
        assert "Moderate" in content
        assert "Cut" in content
        assert "1800" in content  # BMR
        assert "2500" in content  # TDEE
        assert "2000" in content  # Target calories
        mock_api.assert_called_once_with("/tdee", "POST", sample_calculate_calories_args)
    @pytest.mark.asyncio
    @patch('server.make_api_request')
    async def test_meal_plan_tool(self, mock_api, sample_meal_plan_args, mock_api_success):
        """Test meal_plan tool execution"""
        mock_api.return_value = mock_api_success("/mealplan", "POST")
        # Create mock request object
        class MockRequest:
            name = "meal_plan"
            arguments = sample_meal_plan_args
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        assert result[0].type == "text"
        content = result[0].text
        # Check that response contains expected information
        assert "3-Day Meal Plan" in content
        assert "2000 calories" in content
        assert "150g protein" in content
        assert "veg" in content
        assert "Day 1:" in content
        assert "Breakfast:" in content
        assert "Chicken Breast" in content
        assert "Adherence Score: 85.0%" in content
        mock_api.assert_called_once_with("/mealplan", "POST", sample_meal_plan_args)
    @pytest.mark.asyncio
    @patch('server.make_api_request')
    async def test_explain_plan_tool(self, mock_api, sample_explain_plan_args, mock_api_success):
        """Test explain_plan tool execution"""
        mock_api.return_value = mock_api_success("/explain", "GET")
        # Create mock request object
        class MockRequest:
            name = "explain_plan"
            arguments = sample_explain_plan_args
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        assert result[0].type == "text"
        content = result[0].text
        # Check that response contains expected information
        assert "Nutrition Plan Explanation" in content
        assert "This is a test nutrition explanation" in content
        # Check that API was called with correct parameters
        expected_params = {
            "calories": 2000,
            "protein_g": 150,
            "fat_g": 67,
            "carbs_g": 200,
            "constraints": "lactose_free"
        }
        mock_api.assert_called_once_with("/explain", "GET", expected_params)
    @pytest.mark.asyncio
    @patch('server.make_api_request')
    async def test_explain_plan_tool_minimal(self, mock_api, mock_api_success):
        """Test explain_plan tool with minimal arguments"""
        mock_api.return_value = mock_api_success("/explain", "GET")
        args = {"calories": 1800}
        # Create mock request object
        class MockRequest:
            name = "explain_plan"
            arguments = args
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        # Check that API was called with minimal parameters
        expected_params = {"calories": 1800}
        mock_api.assert_called_once_with("/explain", "GET", expected_params)
    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool"""
        # Create mock request object
        class MockRequest:
            name = "unknown_tool"
            arguments = {}
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Unknown tool" in result[0].text
    @pytest.mark.asyncio
    @patch('server.make_api_request')
    async def test_tool_api_error(self, mock_api, sample_calculate_calories_args):
        """Test tool execution with API error"""
        mock_api.side_effect = Exception("API connection failed")
        # Create mock request object
        class MockRequest:
            name = "calculate_calories"
            arguments = sample_calculate_calories_args
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error executing calculate_calories" in result[0].text
        assert "API connection failed" in result[0].text
    @pytest.mark.asyncio
    async def test_tool_validation_error(self):
        """Test tool execution with invalid arguments"""
        invalid_args = {
            "sex": "invalid",
            "age": "not_a_number",
            "height_cm": 175,
            "weight_kg": 70,
            "activity_level": "moderate",
            "goal": "cut"
        }
        # Create mock request object
        class MockRequest:
            name = "calculate_calories"
            arguments = invalid_args
        request = MockRequest()
        result = await handle_call_tool(request)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error executing calculate_calories" in result[0].text
class TestEnvironmentConfiguration:
    """Test environment configuration"""
    @patch.dict('os.environ', {'DIET_API_URL': 'http://custom-api:9000'})
    def test_custom_api_url(self):
        """Test custom API URL configuration"""
        # Re-import to pick up new environment variable
        import importlib
        import server
        importlib.reload(server)
        assert server.API_BASE_URL == "http://custom-api:9000"
    @patch.dict('os.environ', {}, clear=True)
    def test_default_api_url(self):
        """Test default API URL when not configured"""
        # Re-import to pick up default
        import importlib
        import server
        importlib.reload(server)
        assert server.API_BASE_URL == "http://diet-api:8000"
class TestIntegration:
    """Integration tests"""
    @pytest.mark.asyncio
    @patch('server.make_api_request')
    async def test_full_workflow(self, mock_api, test_foods_file, mock_api_success):
        """Test complete workflow: list tools, read resources, execute tools"""
        # Test listing tools
        tools = await handle_list_tools()
        assert len(tools) == 3
        # Test listing resources
        resources = await handle_list_resources()
        assert len(resources) == 1
        # Test reading resource
        read_request = ReadResourceRequest(uri="diet/foods")
        content = await handle_read_resource(read_request)
        assert isinstance(content, str)
        # Test executing tool
        mock_api.return_value = mock_api_success("/tdee", "POST")
        # Create mock request object
        class MockRequest:
            name = "calculate_calories"
            arguments = {
                "sex": "female",
                "age": 25,
                "height_cm": 165,
                "weight_kg": 60,
                "activity_level": "active",
                "goal": "bulk"
            }
        tool_request = MockRequest()
        result = await handle_call_tool(tool_request)
        assert len(result) == 1
        assert "TDEE Calculation Results" in result[0].text
