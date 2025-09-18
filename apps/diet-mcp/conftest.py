from pathlib import Path
from unittest.mock import patch, Mock

import json
import pytest
import tempfile
@pytest.fixture
def test_foods_data():
    """Sample foods data for testing"""
    return {
        "foods": [
            {
                "id": "chicken_breast",
                "name": "Chicken Breast (skinless)",
                "per_100g": {
                    "calories": 165,
                    "protein": 31.0,
                    "fat": 3.6,
                    "carbs": 0.0
                },
                "tags": ["halal"],
                "cost_level": "medium"
            },
            {
                "id": "tofu_firm",
                "name": "Firm Tofu",
                "per_100g": {
                    "calories": 144,
                    "protein": 17.3,
                    "fat": 8.7,
                    "carbs": 2.8
                },
                "tags": ["veg", "vegan", "budget"],
                "cost_level": "low"
            }
        ]
    }
@pytest.fixture
def test_foods_file(test_foods_data, monkeypatch):
    """Create a temporary foods.json file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_foods_data, f)
        temp_path = Path(f.name)
    # Patch the FOODS_PATH in server module
    import server
    monkeypatch.setattr(server, 'FOODS_PATH', temp_path)
    monkeypatch.setattr(server, 'FOODS_DATA', test_foods_data)
    yield temp_path
    # Cleanup
    temp_path.unlink()
@pytest.fixture
def mock_api_success():
    """Mock successful API responses"""
    def _mock_response(endpoint, method="GET", data=None):
        if endpoint == "/tdee":
            return {
                "tdee": 2500.0,
                "target_calories": 2000.0,
                "macro_targets": {
                    "protein_g": 175.0,
                    "fat_g": 55.6,
                    "carbs_g": 200.0
                },
                "bmr": 1800.0,
                "activity_factor": 1.55
            }
        elif endpoint == "/mealplan":
            return {
                "days": [
                    {
                        "day": 1,
                        "meals": [
                            {
                                "name": "Breakfast",
                                "foods": [
                                    {
                                        "name": "Chicken Breast",
                                        "amount_g": 100.0,
                                        "calories": 165.0,
                                        "protein": 31.0,
                                        "fat": 3.6,
                                        "carbs": 0.0
                                    }
                                ],
                                "totals": {
                                    "calories": 165.0,
                                    "protein": 31.0,
                                    "fat": 3.6,
                                    "carbs": 0.0
                                }
                            }
                        ],
                        "daily_totals": {
                            "calories": 500.0,
                            "protein": 93.0,
                            "fat": 10.8,
                            "carbs": 0.0
                        }
                    }
                ],
                "plan_totals": {
                    "calories": 1500.0,
                    "protein": 279.0,
                    "fat": 32.4,
                    "carbs": 0.0,
                    "avg_daily_calories": 500.0
                },
                "adherence_score": 0.85
            }
        elif endpoint == "/explain":
            return {
                "explanation": "This is a test nutrition explanation."
            }
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
    return _mock_response
@pytest.fixture
def sample_calculate_calories_args():
    """Sample arguments for calculate_calories tool"""
    return {
        "sex": "male",
        "age": 30,
        "height_cm": 175,
        "weight_kg": 70,
        "activity_level": "moderate",
        "goal": "cut"
    }
@pytest.fixture
def sample_meal_plan_args():
    """Sample arguments for meal_plan tool"""
    return {
        "calories": 2000,
        "protein_g": 150,
        "fat_g": 67,
        "carbs_g": 200,
        "diet_tags": ["veg"],
        "days": 3
    }
@pytest.fixture
def sample_explain_plan_args():
    """Sample arguments for explain_plan tool"""
    return {
        "calories": 2000,
        "protein_g": 150,
        "fat_g": 67,
        "carbs_g": 200,
        "constraints": "lactose_free"
    }
