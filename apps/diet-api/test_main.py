from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


import json
import pytest
class TestHealthEndpoint:
    """Test health check endpoint"""
    def test_health_check(self, client):
        """Test health check returns successful response"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "diet-api"
class TestTDEEEndpoint:
    """Test TDEE calculation endpoint"""
    def test_calculate_tdee_male_cut(self, client, sample_tdee_request):
        """Test TDEE calculation for male cutting"""
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 200
        data = response.json()
        assert "tdee" in data
        assert "target_calories" in data
        assert "macro_targets" in data
        assert "bmr" in data
        assert "activity_factor" in data
        # Verify calculations make sense
        assert data["bmr"] > 0
        assert data["tdee"] > data["bmr"]
        assert data["target_calories"] < data["tdee"]  # Cut should be deficit
        assert data["activity_factor"] == 1.55  # moderate activity
        # Check macro targets
        macros = data["macro_targets"]
        assert macros["protein_g"] > 0
        assert macros["fat_g"] > 0
        assert macros["carbs_g"] > 0
    def test_calculate_tdee_female_bulk(self, client):
        """Test TDEE calculation for female bulking"""
        request_data = {
            "sex": "female",
            "age": 25,
            "height_cm": 165,
            "weight_kg": 60,
            "activity_level": "active",
            "goal": "bulk"
        }
        response = client.post("/tdee", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["target_calories"] > data["tdee"]  # Bulk should be surplus
        assert data["activity_factor"] == 1.725  # active
    def test_calculate_tdee_maintain(self, client):
        """Test TDEE calculation for maintenance"""
        request_data = {
            "sex": "female",
            "age": 35,
            "height_cm": 160,
            "weight_kg": 65,
            "activity_level": "light",
            "goal": "maintain"
        }
        response = client.post("/tdee", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert abs(data["target_calories"] - data["tdee"]) < 1  # Maintain should be ~equal
    def test_invalid_sex(self, client, sample_tdee_request):
        """Test invalid sex parameter"""
        sample_tdee_request["sex"] = "invalid"
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 400
        assert "Sex must be 'male' or 'female'" in response.json()["detail"]
    def test_invalid_activity_level(self, client, sample_tdee_request):
        """Test invalid activity level"""
        sample_tdee_request["activity_level"] = "invalid"
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 400
        assert "Invalid activity level" in response.json()["detail"]
    def test_invalid_goal(self, client, sample_tdee_request):
        """Test invalid goal"""
        sample_tdee_request["goal"] = "invalid"
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 400
        assert "Goal must be 'cut', 'maintain', or 'bulk'" in response.json()["detail"]
    def test_age_validation(self, client, sample_tdee_request):
        """Test age validation"""
        sample_tdee_request["age"] = 5  # Too young
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 422  # Pydantic validation error
        sample_tdee_request["age"] = 150  # Too old
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 422
    def test_weight_validation(self, client, sample_tdee_request):
        """Test weight validation"""
        sample_tdee_request["weight_kg"] = 20  # Too light
        response = client.post("/tdee", json=sample_tdee_request)
        assert response.status_code == 422
class TestMealPlanEndpoint:
    """Test meal plan generation endpoint"""
    def test_generate_meal_plan_basic(self, client, sample_mealplan_request):
        """Test basic meal plan generation"""
        response = client.post("/mealplan", json=sample_mealplan_request)
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert "plan_totals" in data
        assert "adherence_score" in data
        # Check we got the right number of days
        assert len(data["days"]) == sample_mealplan_request["days"]
        # Check each day has meals
        for day in data["days"]:
            assert "day" in day
            assert "meals" in day
            assert "daily_totals" in day
            assert len(day["meals"]) == 3  # Breakfast, lunch, dinner
            # Check each meal has foods
            for meal in day["meals"]:
                assert "name" in meal
                assert "foods" in meal
                assert "totals" in meal
                assert len(meal["foods"]) > 0
                # Check food items
                for food in meal["foods"]:
                    assert "name" in food
                    assert "amount_g" in food
                    assert "calories" in food
                    assert "protein" in food
                    assert "fat" in food
                    assert "carbs" in food
        # Check adherence score is valid
        assert 0 <= data["adherence_score"] <= 1
    def test_meal_plan_vegan_filter(self, client):
        """Test meal plan with vegan dietary restriction"""
        request_data = {
            "calories": 1800,
            "protein_g": 120,
            "fat_g": 60,
            "carbs_g": 180,
            "diet_tags": ["vegan"],
            "days": 2
        }
        response = client.post("/mealplan", json=request_data)
        assert response.status_code == 200
        data = response.json()
        # Check that only vegan foods are included
        for day in data["days"]:
            for meal in day["meals"]:
                for food in meal["foods"]:
                    # Should not contain chicken (non-vegan)
                    assert "chicken" not in food["name"].lower()
    def test_meal_plan_budget_filter(self, client):
        """Test meal plan with budget dietary restriction"""
        request_data = {
            "calories": 2000,
            "protein_g": 130,
            "fat_g": 70,
            "carbs_g": 200,
            "diet_tags": ["budget"],
            "days": 1
        }
        response = client.post("/mealplan", json=request_data)
        assert response.status_code == 200
        # Just verify it doesn't crash with budget filter
    def test_meal_plan_multiple_tags(self, client):
        """Test meal plan with multiple dietary restrictions"""
        request_data = {
            "calories": 1900,
            "protein_g": 140,
            "fat_g": 63,
            "carbs_g": 190,
            "diet_tags": ["veg", "budget"],
            "days": 1
        }
        response = client.post("/mealplan", json=request_data)
        assert response.status_code == 200
    def test_meal_plan_invalid_calories(self, client, sample_mealplan_request):
        """Test meal plan with invalid calories"""
        sample_mealplan_request["calories"] = 500  # Too low
        response = client.post("/mealplan", json=sample_mealplan_request)
        assert response.status_code == 422
        sample_mealplan_request["calories"] = 7000  # Too high
        response = client.post("/mealplan", json=sample_mealplan_request)
        assert response.status_code == 422
    def test_meal_plan_invalid_days(self, client, sample_mealplan_request):
        """Test meal plan with invalid number of days"""
        sample_mealplan_request["days"] = 0  # Too low
        response = client.post("/mealplan", json=sample_mealplan_request)
        assert response.status_code == 422
        sample_mealplan_request["days"] = 20  # Too high
        response = client.post("/mealplan", json=sample_mealplan_request)
        assert response.status_code == 422
class TestExplainEndpoint:
    """Test nutrition explanation endpoint"""
    def test_explain_basic(self, client):
        """Test basic explanation without OLLAMA"""
        params = {
            "calories": 2000,
            "protein_g": 150,
            "fat_g": 67,
            "carbs_g": 200
        }
        response = client.get("/explain", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert len(data["explanation"]) > 0
        # Should contain nutritional analysis
        explanation = data["explanation"].lower()
        assert "protein" in explanation
        assert "fat" in explanation
        assert "carb" in explanation
    def test_explain_with_constraints(self, client):
        """Test explanation with constraints"""
        params = {
            "calories": 1800,
            "protein_g": 140,
            "fat_g": 60,
            "carbs_g": 160,
            "constraints": "lactose_free, high_protein"
        }
        response = client.get("/explain", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "lactose_free" in data["explanation"] or "high_protein" in data["explanation"]
    @patch('requests.post')
    def test_explain_with_ollama_success(self, mock_post, client):
        """Test explanation with successful OLLAMA response"""
        # Mock successful OLLAMA response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is an AI-generated nutrition explanation."
        }
        mock_post.return_value = mock_response
        with patch.dict('os.environ', {'OLLAMA_URL': 'http://test-ollama:11434'}):
            params = {
                "calories": 2200,
                "protein_g": 160,
                "fat_g": 73,
                "carbs_g": 220
            }
            response = client.get("/explain", params=params)
            assert response.status_code == 200
            data = response.json()
            assert "explanation" in data
            assert "AI-generated" in data["explanation"]
    @patch('requests.post')
    def test_explain_with_ollama_failure(self, mock_post, client):
        """Test explanation with OLLAMA failure (fallback to rule-based)"""
        # Mock failed OLLAMA response
        mock_post.side_effect = Exception("Connection failed")
        with patch.dict('os.environ', {'OLLAMA_URL': 'http://test-ollama:11434'}):
            params = {
                "calories": 2200,
                "protein_g": 160,
                "fat_g": 73,
                "carbs_g": 220
            }
            response = client.get("/explain", params=params)
            assert response.status_code == 200
            data = response.json()
            assert "explanation" in data
            # Should fall back to rule-based explanation
            assert "Nutrition Analysis" in data["explanation"]
    def test_explain_minimal_params(self, client):
        """Test explanation with minimal parameters"""
        params = {"calories": 1500}
        response = client.get("/explain", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
class TestCalculationFunctions:
    """Test internal calculation functions"""
    def test_calculate_bmr_male(self):
        """Test BMR calculation for males"""
        from main import calculate_bmr
        bmr = calculate_bmr("male", 30, 175, 70)
        expected = 10 * 70 + 6.25 * 175 - 5 * 30 + 5
        assert bmr == expected
    def test_calculate_bmr_female(self):
        """Test BMR calculation for females"""
        from main import calculate_bmr
        bmr = calculate_bmr("female", 25, 165, 60)
        expected = 10 * 60 + 6.25 * 165 - 5 * 25 - 161
        assert bmr == expected
    def test_get_activity_factor(self):
        """Test activity factor retrieval"""
        from main import get_activity_factor
        assert get_activity_factor("sedentary") == 1.2
        assert get_activity_factor("light") == 1.375
        assert get_activity_factor("moderate") == 1.55
        assert get_activity_factor("active") == 1.725
        assert get_activity_factor("very_active") == 1.9
        assert get_activity_factor("invalid") == 1.55  # default
    def test_get_calorie_adjustment(self):
        """Test calorie adjustment for goals"""
        from main import get_calorie_adjustment
        assert get_calorie_adjustment("cut") == -0.20
        assert get_calorie_adjustment("maintain") == 0.0
        assert get_calorie_adjustment("bulk") == 0.15
        assert get_calorie_adjustment("invalid") == 0.0  # default
    def test_calculate_macro_targets_cut(self):
        """Test macro target calculation for cutting"""
        from main import calculate_macro_targets
        macros = calculate_macro_targets(2000, "cut")
        # Cut should have higher protein ratio
        protein_calories = macros["protein_g"] * 4
        protein_ratio = protein_calories / 2000
        assert protein_ratio == 0.35
        fat_calories = macros["fat_g"] * 9
        fat_ratio = fat_calories / 2000
        assert fat_ratio == 0.25
    def test_calculate_macro_targets_bulk(self):
        """Test macro target calculation for bulking"""
        from main import calculate_macro_targets
        macros = calculate_macro_targets(2500, "bulk")
        # Bulk should have more carbs
        protein_calories = macros["protein_g"] * 4
        protein_ratio = protein_calories / 2500
        assert protein_ratio == 0.25
class TestFoodFiltering:
    """Test food filtering functions"""
    def test_filter_foods_no_tags(self, test_foods_data):
        """Test filtering with no dietary restrictions"""
        from main import filter_foods
        # Mock the FOODS_DB
        with patch('main.FOODS_DB', test_foods_data):
            filtered = filter_foods([])
            assert len(filtered) == len(test_foods_data["foods"])
    def test_filter_foods_vegan(self, test_foods_data):
        """Test filtering for vegan foods"""
        from main import filter_foods
        with patch('main.FOODS_DB', test_foods_data):
            filtered = filter_foods(["vegan"])
            # Should not include chicken
            food_names = [food["name"] for food in filtered]
            assert not any("chicken" in name.lower() for name in food_names)
            # Should include tofu and broccoli
            assert any("tofu" in name.lower() for name in food_names)
            assert any("broccoli" in name.lower() for name in food_names)
    def test_filter_foods_vegetarian(self, test_foods_data):
        """Test filtering for vegetarian foods"""
        from main import filter_foods
        with patch('main.FOODS_DB', test_foods_data):
            filtered = filter_foods(["veg"])
            # Should not include chicken
            food_names = [food["name"] for food in filtered]
            assert not any("chicken" in name.lower() for name in food_names)
            # Should include vegetarian options
            veg_foods = [food for food in filtered if "veg" in food.get("tags", [])]
            assert len(veg_foods) > 0
    def test_filter_foods_budget(self, test_foods_data):
        """Test filtering for budget foods"""
        from main import filter_foods
        with patch('main.FOODS_DB', test_foods_data):
            filtered = filter_foods(["budget"])
            # All filtered foods should be low or medium cost
            for food in filtered:
                assert food.get("cost_level") in ["low", "medium"]
