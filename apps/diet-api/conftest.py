from fastapi.testclient import TestClient
from pathlib import Path

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
                "id": "brown_rice_cooked",
                "name": "Brown Rice (cooked)",
                "per_100g": {
                    "calories": 111,
                    "protein": 2.6,
                    "fat": 0.9,
                    "carbs": 22.0
                },
                "tags": ["veg", "vegan", "budget"],
                "cost_level": "low"
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
            },
            {
                "id": "broccoli",
                "name": "Broccoli (steamed)",
                "per_100g": {
                    "calories": 35,
                    "protein": 2.8,
                    "fat": 0.4,
                    "carbs": 7.0
                },
                "tags": ["veg", "vegan", "budget"],
                "cost_level": "low"
            },
            {
                "id": "olive_oil",
                "name": "Olive Oil (extra virgin)",
                "per_100g": {
                    "calories": 884,
                    "protein": 0.0,
                    "fat": 100.0,
                    "carbs": 0.0
                },
                "tags": ["veg", "vegan"],
                "cost_level": "medium"
            }
        ]
    }
@pytest.fixture
def test_foods_file(test_foods_data, monkeypatch):
    """Create a temporary foods.json file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_foods_data, f)
        temp_path = Path(f.name)
    # Patch the FOODS_PATH in main module
    import main
    monkeypatch.setattr(main, 'FOODS_PATH', temp_path)
    # Reload the foods database
    with open(temp_path, 'r') as f:
        foods_data = json.load(f)
    monkeypatch.setattr(main, 'FOODS_DB', foods_data)
    yield temp_path
    # Cleanup
    temp_path.unlink()
@pytest.fixture
def client(test_foods_file):
    """Create a test client for the FastAPI app"""
    from main import app
    return TestClient(app)
@pytest.fixture
def sample_tdee_request():
    """Sample TDEE calculation request"""
    return {
        "sex": "male",
        "age": 30,
        "height_cm": 175,
        "weight_kg": 70,
        "activity_level": "moderate",
        "goal": "cut"
    }
@pytest.fixture
def sample_mealplan_request():
    """Sample meal plan request"""
    return {
        "calories": 2000,
        "protein_g": 150,
        "fat_g": 67,
        "carbs_g": 200,
        "diet_tags": ["veg"],
        "days": 3
    }
