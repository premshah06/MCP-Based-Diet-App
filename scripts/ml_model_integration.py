#!/usr/bin/env python3
"""
ML Model Integration for Diet Recommendation System
This script integrates the best performing machine learning model 
(Gradient Boosting) into the existing diet recommendation system.
Features:
- Model training and persistence
- Real-time food recommendation scoring
- Integration with existing API endpoints
- Model performance monitoring
"""
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from datetime import datetime
import logging
from pathlib import Path
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class DietRecommendationModel:
    """
    Production-ready ML model for diet recommendations
    """
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'calories', 'protein', 'fat', 'carbs', 'protein_density',
            'fat_percentage', 'carb_percentage', 'protein_percentage',
            'calorie_density', 'nutritional_score', 'cost_encoded',
            'is_veg', 'is_vegan', 'is_non_veg', 'is_halal', 'is_budget', 'is_lactose_free'
        ]
        self.is_trained = False
        self.model_metadata = {}
    def prepare_training_data(self, foods_json_path="foods.json"):
        """
        Prepare training data from foods dataset
        """
        logger.info("Preparing training data...")
        # Load foods data
        with open(foods_json_path, 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        # Create enhanced dataset
        enhanced_data = []
        for food in foods_data['foods']:
            # Calculate additional features
            nutrition = food['per_100g']
            # Protein density (protein per calorie)
            protein_density = nutrition['protein'] / nutrition['calories'] if nutrition['calories'] > 0 else 0
            # Macronutrient percentages
            total_calories = nutrition['calories']
            if total_calories > 0:
                fat_percentage = (nutrition['fat'] * 9) / total_calories
                carb_percentage = (nutrition['carbs'] * 4) / total_calories
                protein_percentage = (nutrition['protein'] * 4) / total_calories
            else:
                fat_percentage = carb_percentage = protein_percentage = 0
            # Calorie density
            calorie_density = nutrition['calories'] / 100
            # Nutritional score
            nutritional_score = (
                nutrition['protein'] * 0.4 +
                (100 - nutrition['fat']) * 0.2 +
                (100 - nutrition['calories']/10) * 0.3 +
                nutrition['carbs'] * 0.1
            ) / 100
            # Diet suitability score (target variable)
            if nutritional_score >= 0.8:
                diet_suitability = 5
            elif nutritional_score >= 0.6:
                diet_suitability = 4
            elif nutritional_score >= 0.4:
                diet_suitability = 3
            elif nutritional_score >= 0.2:
                diet_suitability = 2
            else:
                diet_suitability = 1
            # Cost encoding
            cost_mapping = {'low': 1, 'medium': 2, 'high': 3}
            cost_encoded = cost_mapping.get(food.get('cost_level', 'medium'), 2)
            # Tag features
            tags = food.get('tags', [])
            is_veg = 1 if 'veg' in tags else 0
            is_vegan = 1 if 'vegan' in tags else 0
            is_non_veg = 1 if 'non_veg' in tags else 0
            is_halal = 1 if 'halal' in tags else 0
            is_budget = 1 if 'budget' in tags else 0
            is_lactose_free = 1 if 'lactose_free' in tags else 0
            enhanced_data.append({
                'food_id': food['id'],
                'name': food['name'],
                'calories': nutrition['calories'],
                'protein': nutrition['protein'],
                'fat': nutrition['fat'],
                'carbs': nutrition['carbs'],
                'protein_density': protein_density,
                'fat_percentage': fat_percentage,
                'carb_percentage': carb_percentage,
                'protein_percentage': protein_percentage,
                'calorie_density': calorie_density,
                'nutritional_score': nutritional_score,
                'cost_encoded': cost_encoded,
                'is_veg': is_veg,
                'is_vegan': is_vegan,
                'is_non_veg': is_non_veg,
                'is_halal': is_halal,
                'is_budget': is_budget,
                'is_lactose_free': is_lactose_free,
                'diet_suitability': diet_suitability
            })
        # Add synthetic data for better training
        enhanced_data.extend(self._generate_synthetic_data(200))
        df = pd.DataFrame(enhanced_data)
        logger.info(f"Training data prepared: {len(df)} samples")
        return df
    def _generate_synthetic_data(self, n_samples):
        """
        Generate synthetic training data
        """
        synthetic_data = []
        np.random.seed(42)
        for _ in range(n_samples):
            # Random nutritional values
            calories = np.random.uniform(50, 800)
            protein = np.random.uniform(1, 80)
            fat = np.random.uniform(0.1, 100)
            carbs = np.random.uniform(0, 80)
            # Ensure consistency
            calculated_calories = protein * 4 + fat * 9 + carbs * 4
            if calculated_calories > 0:
                factor = calories / calculated_calories
                protein *= factor
                fat *= factor
                carbs *= factor
            # Calculate features
            protein_density = protein / calories if calories > 0 else 0
            fat_percentage = (fat * 9) / calories if calories > 0 else 0
            carb_percentage = (carbs * 4) / calories if calories > 0 else 0
            protein_percentage = (protein * 4) / calories if calories > 0 else 0
            calorie_density = calories / 100
            nutritional_score = (
                protein * 0.4 + (100 - fat) * 0.2 + 
                (100 - calories/10) * 0.3 + carbs * 0.1
            ) / 100
            # Random tags
            is_veg = np.random.choice([0, 1], p=[0.6, 0.4])
            is_vegan = np.random.choice([0, 1], p=[0.8, 0.2]) if is_veg else 0
            is_non_veg = 1 - is_veg
            is_halal = np.random.choice([0, 1], p=[0.7, 0.3])
            is_budget = np.random.choice([0, 1], p=[0.6, 0.4])
            is_lactose_free = np.random.choice([0, 1], p=[0.8, 0.2])
            cost_encoded = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
            # Target variable
            if nutritional_score >= 0.8:
                diet_suitability = 5
            elif nutritional_score >= 0.6:
                diet_suitability = 4
            elif nutritional_score >= 0.4:
                diet_suitability = 3
            elif nutritional_score >= 0.2:
                diet_suitability = 2
            else:
                diet_suitability = 1
            synthetic_data.append({
                'food_id': f'synthetic_{len(synthetic_data)}',
                'name': f'Synthetic Food {len(synthetic_data)}',
                'calories': calories,
                'protein': protein,
                'fat': fat,
                'carbs': carbs,
                'protein_density': protein_density,
                'fat_percentage': fat_percentage,
                'carb_percentage': carb_percentage,
                'protein_percentage': protein_percentage,
                'calorie_density': calorie_density,
                'nutritional_score': nutritional_score,
                'cost_encoded': cost_encoded,
                'is_veg': is_veg,
                'is_vegan': is_vegan,
                'is_non_veg': is_non_veg,
                'is_halal': is_halal,
                'is_budget': is_budget,
                'is_lactose_free': is_lactose_free,
                'diet_suitability': diet_suitability
            })
        return synthetic_data
    def train_model(self, df):
        """
        Train the Gradient Boosting model
        """
        logger.info("Training Gradient Boosting model...")
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['diet_suitability']
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        # Scale features (though not strictly necessary for GB)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        # Initialize and train model
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        # Store metadata
        self.model_metadata = {
            'model_type': 'GradientBoostingClassifier',
            'training_date': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'feature_columns': self.feature_columns,
            'version': '1.0'
        }
        self.is_trained = True
        logger.info(f"Model trained successfully!")
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"F1 Score: {f1:.4f}")
        return self.model_metadata
    def predict_food_suitability(self, food_data):
        """
        Predict diet suitability for a single food item
        Args:
            food_data (dict): Food item with nutritional information
        Returns:
            dict: Prediction results with score and confidence
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        # Extract features
        features = self._extract_features(food_data)
        # Make prediction
        features_array = np.array([features])
        prediction = self.model.predict(features_array)[0]
        probabilities = self.model.predict_proba(features_array)[0]
        confidence = float(np.max(probabilities))
        return {
            'diet_suitability_score': int(prediction),
            'confidence': confidence,
            'recommendation': self._get_recommendation_text(prediction, confidence)
        }
    def predict_meal_suitability(self, foods_list):
        """
        Predict suitability for a complete meal (multiple foods)
        Args:
            foods_list (list): List of food items in the meal
        Returns:
            dict: Meal-level prediction and recommendations
        """
        if not foods_list:
            return {'error': 'No foods provided'}
        # Get predictions for each food
        food_predictions = []
        total_score = 0
        total_confidence = 0
        for food in foods_list:
            pred = self.predict_food_suitability(food)
            food_predictions.append({
                'food_name': food.get('name', 'Unknown'),
                'prediction': pred
            })
            total_score += pred['diet_suitability_score'] * food.get('weight', 1.0)
            total_confidence += pred['confidence']
        # Calculate meal-level metrics
        avg_score = total_score / len(foods_list)
        avg_confidence = total_confidence / len(foods_list)
        return {
            'meal_suitability_score': round(avg_score, 2),
            'meal_confidence': round(avg_confidence, 2),
            'food_predictions': food_predictions,
            'recommendation': self._get_meal_recommendation(avg_score, avg_confidence)
        }
    def _extract_features(self, food_data):
        """
        Extract model features from food data
        """
        nutrition = food_data.get('per_100g', {})
        tags = food_data.get('tags', [])
        # Basic nutrition
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein', 0)
        fat = nutrition.get('fat', 0)
        carbs = nutrition.get('carbs', 0)
        # Calculated features
        protein_density = protein / calories if calories > 0 else 0
        fat_percentage = (fat * 9) / calories if calories > 0 else 0
        carb_percentage = (carbs * 4) / calories if calories > 0 else 0
        protein_percentage = (protein * 4) / calories if calories > 0 else 0
        calorie_density = calories / 100
        nutritional_score = (
            protein * 0.4 + (100 - fat) * 0.2 + 
            (100 - calories/10) * 0.3 + carbs * 0.1
        ) / 100
        # Cost encoding
        cost_mapping = {'low': 1, 'medium': 2, 'high': 3}
        cost_encoded = cost_mapping.get(food_data.get('cost_level', 'medium'), 2)
        # Tag features
        is_veg = 1 if 'veg' in tags else 0
        is_vegan = 1 if 'vegan' in tags else 0
        is_non_veg = 1 if 'non_veg' in tags else 0
        is_halal = 1 if 'halal' in tags else 0
        is_budget = 1 if 'budget' in tags else 0
        is_lactose_free = 1 if 'lactose_free' in tags else 0
        return [
            calories, protein, fat, carbs, protein_density,
            fat_percentage, carb_percentage, protein_percentage,
            calorie_density, nutritional_score, cost_encoded,
            is_veg, is_vegan, is_non_veg, is_halal, is_budget, is_lactose_free
        ]
    def _get_recommendation_text(self, score, confidence):
        """
        Generate human-readable recommendation text
        """
        if confidence < 0.6:
            confidence_text = "Low confidence"
        elif confidence < 0.8:
            confidence_text = "Medium confidence"
        else:
            confidence_text = "High confidence"
        if score >= 4:
            return f"Excellent choice for your diet ({confidence_text})"
        elif score >= 3:
            return f"Good option for your meal plan ({confidence_text})"
        elif score >= 2:
            return f"Acceptable but consider alternatives ({confidence_text})"
        else:
            return f"Not recommended for your diet goals ({confidence_text})"
    def _get_meal_recommendation(self, avg_score, avg_confidence):
        """
        Generate meal-level recommendation
        """
        if avg_score >= 4:
            return "Excellent meal composition for your diet goals"
        elif avg_score >= 3:
            return "Well-balanced meal with good nutritional value"
        elif avg_score >= 2:
            return "Acceptable meal but could be improved"
        else:
            return "Consider replacing some foods for better nutrition"
    def save_model(self, filepath='diet_recommendation_model.pkl'):
        """
        Save the trained model to disk
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        model_package = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metadata': self.model_metadata
        }
        joblib.dump(model_package, filepath)
        logger.info(f"Model saved to {filepath}")
    def load_model(self, filepath='diet_recommendation_model.pkl'):
        """
        Load a trained model from disk
        """
        try:
            model_package = joblib.load(filepath)
            self.model = model_package['model']
            self.scaler = model_package['scaler']
            self.feature_columns = model_package['feature_columns']
            self.model_metadata = model_package['metadata']
            self.is_trained = True
            logger.info(f"Model loaded from {filepath}")
            logger.info(f"Model version: {self.model_metadata.get('version', 'Unknown')}")
        except FileNotFoundError:
            logger.error(f"Model file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    def get_feature_importance(self):
        """
        Get feature importance from the trained model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")
        importance_scores = self.model.feature_importances_
        feature_importance = list(zip(self.feature_columns, importance_scores))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        return {
            'feature_importance': [
                {'feature': feat, 'importance': float(imp)} 
                for feat, imp in feature_importance
            ],
            'top_features': [feat for feat, _ in feature_importance[:5]]
        }
def main():
    """
    Main function to train and save the model
    """
    print("🤖 ML Model Integration for Diet Recommendations")
    print("=" * 50)
    # Initialize model
    diet_model = DietRecommendationModel()
    # Prepare training data
    df = diet_model.prepare_training_data()
    # Train model
    metadata = diet_model.train_model(df)
    # Save model
    diet_model.save_model()
    # Display feature importance
    importance = diet_model.get_feature_importance()
    print("\n🏆 Top 5 Most Important Features:")
    for feature_data in importance['feature_importance'][:5]:
        print(f"  {feature_data['feature']}: {feature_data['importance']:.4f}")
    # Test prediction
    print("\n🧪 Testing Model Predictions:")
    # Example food item
    test_food = {
        "name": "Grilled Chicken Breast",
        "per_100g": {
            "calories": 165,
            "protein": 31.0,
            "fat": 3.6,
            "carbs": 0.0
        },
        "tags": ["non_veg", "high_protein", "lean"],
        "cost_level": "medium"
    }
    prediction = diet_model.predict_food_suitability(test_food)
    print(f"Food: {test_food['name']}")
    print(f"Suitability Score: {prediction['diet_suitability_score']}/5")
    print(f"Confidence: {prediction['confidence']:.2%}")
    print(f"Recommendation: {prediction['recommendation']}")
    print(f"\n✅ Model integration complete!")
    print(f"📊 Model Performance:")
    print(f"   Accuracy: {metadata['accuracy']:.4f}")
    print(f"   F1 Score: {metadata['f1_score']:.4f}")
    print(f"   Training Samples: {metadata['training_samples']}")
    print(f"\n💾 Model saved as 'diet_recommendation_model.pkl'")
    print(f"🚀 Ready for integration with FastAPI!")
if __name__ == "__main__":
    main()
