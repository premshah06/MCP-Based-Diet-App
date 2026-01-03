#!/usr/bin/env python3
"""
Diet Recommendation Model Comparison System
This script compares three different machine learning models for diet and nutrition recommendations:
1. Random Forest Classifier
2. Gradient Boosting Classifier  
3. Neural Network (MLP)
The system evaluates models based on:
- Accuracy
- F1 Score
- Precision
- Recall
- Training Time
- Prediction Time
Dataset: Enhanced food dataset with nutritional features
Target: Diet suitability classification (1-5 scale)
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, 
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns
import time
import json
import warnings
warnings.filterwarnings('ignore')
class DietModelComparison:
    """
    Comprehensive model comparison system for diet recommendations
    """
    def __init__(self):
        self.models = {}
        self.results = {}
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
    def load_and_prepare_data(self, foods_json_path="foods.json"):
        """
        Load and prepare enhanced dataset for model training
        """
        print("📊 Loading and preparing dataset...")
        # Load existing foods data
        with open(foods_json_path, 'r') as f:
            foods_data = json.load(f)
        # Create enhanced dataset with additional features
        enhanced_data = []
        for food in foods_data['foods']:
            # Calculate additional nutritional metrics
            nutrition = food['per_100g']
            # Protein density (protein per calorie)
            protein_density = nutrition['protein'] / nutrition['calories'] if nutrition['calories'] > 0 else 0
            # Fat percentage
            fat_percentage = (nutrition['fat'] * 9) / nutrition['calories'] if nutrition['calories'] > 0 else 0
            # Carb percentage  
            carb_percentage = (nutrition['carbs'] * 4) / nutrition['calories'] if nutrition['calories'] > 0 else 0
            # Protein percentage
            protein_percentage = (nutrition['protein'] * 4) / nutrition['calories'] if nutrition['calories'] > 0 else 0
            # Calorie density
            calorie_density = nutrition['calories'] / 100  # per gram
            # Nutritional score (higher is better)
            nutritional_score = (
                nutrition['protein'] * 0.4 +  # High protein value
                (100 - nutrition['fat']) * 0.2 +  # Lower fat preference
                (100 - nutrition['calories']/10) * 0.3 +  # Lower calorie preference
                nutrition['carbs'] * 0.1  # Moderate carb value
            ) / 100
            # Diet suitability score (1-5 scale based on nutritional profile)
            if nutritional_score >= 0.8:
                diet_suitability = 5  # Excellent
            elif nutritional_score >= 0.6:
                diet_suitability = 4  # Good
            elif nutritional_score >= 0.4:
                diet_suitability = 3  # Average
            elif nutritional_score >= 0.2:
                diet_suitability = 2  # Poor
            else:
                diet_suitability = 1  # Very Poor
            # Cost level encoding
            cost_mapping = {'low': 1, 'medium': 2, 'high': 3}
            cost_encoded = cost_mapping.get(food.get('cost_level', 'medium'), 2)
            # Tag features
            is_veg = 1 if 'veg' in food.get('tags', []) else 0
            is_vegan = 1 if 'vegan' in food.get('tags', []) else 0
            is_non_veg = 1 if 'non_veg' in food.get('tags', []) else 0
            is_halal = 1 if 'halal' in food.get('tags', []) else 0
            is_budget = 1 if 'budget' in food.get('tags', []) else 0
            is_lactose_free = 1 if 'lactose_free' in food.get('tags', []) else 0
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
        # Convert to DataFrame
        df = pd.DataFrame(enhanced_data)
        # Add synthetic data for better model training
        df = self._add_synthetic_data(df)
        print(f"✅ Dataset prepared: {len(df)} samples with {len(df.columns)-3} features")
        print(f"📊 Diet suitability distribution:")
        print(df['diet_suitability'].value_counts().sort_index())
        return df
    def _add_synthetic_data(self, df):
        """
        Add synthetic data points to improve model training
        """
        synthetic_data = []
        # Generate synthetic food items based on existing patterns
        np.random.seed(42)
        for _ in range(200):  # Add 200 synthetic samples
            # Random nutritional values within realistic ranges
            calories = np.random.uniform(50, 800)
            protein = np.random.uniform(1, 80)
            fat = np.random.uniform(0.1, 100)
            carbs = np.random.uniform(0, 80)
            # Ensure nutritional consistency
            calculated_calories = protein * 4 + fat * 9 + carbs * 4
            if calculated_calories > 0:
                # Adjust to match calorie count
                factor = calories / calculated_calories
                protein *= factor
                fat *= factor
                carbs *= factor
            # Calculate derived features
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
            # Calculate diet suitability
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
        # Combine original and synthetic data
        synthetic_df = pd.DataFrame(synthetic_data)
        combined_df = pd.concat([df, synthetic_df], ignore_index=True)
        return combined_df
    def initialize_models(self):
        """
        Initialize the three ML models with optimized parameters
        """
        print("🤖 Initializing machine learning models...")
        self.models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'Neural Network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=500,
                random_state=42
            )
        }
        print("✅ Models initialized successfully")
    def train_and_evaluate(self, df):
        """
        Train and evaluate all models
        """
        print("🏋️ Training and evaluating models...")
        # Prepare features and target
        feature_columns = [
            'calories', 'protein', 'fat', 'carbs', 'protein_density',
            'fat_percentage', 'carb_percentage', 'protein_percentage',
            'calorie_density', 'nutritional_score', 'cost_encoded',
            'is_veg', 'is_vegan', 'is_non_veg', 'is_halal', 'is_budget', 'is_lactose_free'
        ]
        X = df[feature_columns]
        y = df['diet_suitability']
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.results = {}
        for name, model in self.models.items():
            print(f"\n🔄 Training {name}...")
            # Training time
            start_time = time.time()
            if name == 'Neural Network':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            training_time = time.time() - start_time
            # Prediction time
            start_time = time.time()
            if name == 'Neural Network':
                y_pred = model.predict(X_test_scaled)
            else:
                y_pred = model.predict(X_test)
            prediction_time = time.time() - start_time
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            # Cross-validation score
            if name == 'Neural Network':
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='f1_weighted')
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')
            self.results[name] = {
                'accuracy': accuracy,
                'f1_score': f1,
                'precision': precision,
                'recall': recall,
                'cv_score_mean': cv_scores.mean(),
                'cv_score_std': cv_scores.std(),
                'training_time': training_time,
                'prediction_time': prediction_time,
                'y_true': y_test,
                'y_pred': y_pred
            }
            print(f"✅ {name} completed:")
            print(f"   Accuracy: {accuracy:.4f}")
            print(f"   F1 Score: {f1:.4f}")
            print(f"   CV Score: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    def display_results(self):
        """
        Display comprehensive comparison results
        """
        print("\n" + "="*60)
        print("🏆 MODEL COMPARISON RESULTS")
        print("="*60)
        # Create results DataFrame
        results_df = pd.DataFrame({
            model: {
                'Accuracy': f"{metrics['accuracy']:.4f}",
                'F1 Score': f"{metrics['f1_score']:.4f}",
                'Precision': f"{metrics['precision']:.4f}",
                'Recall': f"{metrics['recall']:.4f}",
                'CV Score': f"{metrics['cv_score_mean']:.4f} (±{metrics['cv_score_std']:.4f})",
                'Training Time (s)': f"{metrics['training_time']:.3f}",
                'Prediction Time (s)': f"{metrics['prediction_time']:.4f}"
            }
            for model, metrics in self.results.items()
        }).T
        print(results_df.to_string())
        # Determine best model
        best_model = max(self.results.keys(), 
                        key=lambda x: self.results[x]['f1_score'])
        print(f"\n🥇 BEST MODEL: {best_model}")
        print(f"   F1 Score: {self.results[best_model]['f1_score']:.4f}")
        print(f"   Accuracy: {self.results[best_model]['accuracy']:.4f}")
        print(f"   Training Time: {self.results[best_model]['training_time']:.3f}s")
        return best_model
    def plot_results(self):
        """
        Create visualization plots for model comparison
        """
        print("\n📊 Creating visualization plots...")
        try:
            # Set matplotlib backend to avoid GUI issues
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            # Set up the plot style
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Diet Recommendation Model Comparison', fontsize=16, fontweight='bold')
        models = list(self.results.keys())
        # 1. Performance metrics comparison
        metrics = ['accuracy', 'f1_score', 'precision', 'recall']
        metric_data = {metric: [self.results[model][metric] for model in models] for metric in metrics}
        x = np.arange(len(models))
        width = 0.2
        for i, metric in enumerate(metrics):
            axes[0, 0].bar(x + i*width, metric_data[metric], width, 
                          label=metric.replace('_', ' ').title())
        axes[0, 0].set_xlabel('Models')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].set_title('Performance Metrics Comparison')
        axes[0, 0].set_xticks(x + width * 1.5)
        axes[0, 0].set_xticklabels(models)
        axes[0, 0].legend()
        axes[0, 0].set_ylim(0, 1)
        # 2. Training time comparison
        training_times = [self.results[model]['training_time'] for model in models]
        axes[0, 1].bar(models, training_times, color=['skyblue', 'lightgreen', 'coral'])
        axes[0, 1].set_ylabel('Time (seconds)')
        axes[0, 1].set_title('Training Time Comparison')
        axes[0, 1].tick_params(axis='x', rotation=45)
        # 3. F1 Score with CV
        f1_scores = [self.results[model]['f1_score'] for model in models]
        cv_scores = [self.results[model]['cv_score_mean'] for model in models]
        cv_stds = [self.results[model]['cv_score_std'] for model in models]
        x_pos = np.arange(len(models))
        axes[1, 0].bar(x_pos - 0.2, f1_scores, 0.4, label='Test F1 Score', color='skyblue')
        axes[1, 0].errorbar(x_pos + 0.2, cv_scores, yerr=cv_stds, 
                           fmt='o', capsize=5, label='CV F1 Score (±std)', color='red')
        axes[1, 0].set_xlabel('Models')
        axes[1, 0].set_ylabel('F1 Score')
        axes[1, 0].set_title('F1 Score: Test vs Cross-Validation')
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(models)
        axes[1, 0].legend()
        axes[1, 0].set_ylim(0, 1)
        # 4. Confusion matrix for best model
        best_model = max(self.results.keys(), 
                        key=lambda x: self.results[x]['f1_score'])
        cm = confusion_matrix(self.results[best_model]['y_true'], 
                             self.results[best_model]['y_pred'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1, 1])
            axes[1, 1].set_xlabel('Predicted')
            axes[1, 1].set_ylabel('Actual')
            axes[1, 1].set_title(f'Confusion Matrix - {best_model}')
            plt.tight_layout()
            plt.savefig('model_comparison_results.png', dpi=300, bbox_inches='tight')
            print("📊 Plots saved as 'model_comparison_results.png'")
            plt.close()  # Close figure instead of show
        except Exception as e:
            print(f"⚠️  Visualization skipped due to display issue: {str(e)}")
            print("📊 Results have been saved to JSON file instead")
    def save_results(self, filename='model_comparison_results.json'):
        """
        Save results to JSON file
        """
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = {}
        for model, metrics in self.results.items():
            serializable_results[model] = {
                k: v.tolist() if isinstance(v, np.ndarray) else v 
                for k, v in metrics.items() 
                if k not in ['y_true', 'y_pred']
            }
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f"💾 Results saved to {filename}")
    def get_recommendations(self):
        """
        Provide model recommendations based on results
        """
        print("\n" + "="*60)
        print("🎯 MODEL RECOMMENDATIONS")
        print("="*60)
        best_model = max(self.results.keys(), 
                        key=lambda x: self.results[x]['f1_score'])
        recommendations = {
            'Random Forest': {
                'pros': ['Fast training and prediction', 'Good interpretability', 'Handles mixed data types well'],
                'cons': ['May overfit with small datasets', 'Less accurate than ensemble methods'],
                'use_case': 'Best for quick prototyping and when interpretability is important'
            },
            'Gradient Boosting': {
                'pros': ['High accuracy', 'Good handling of complex patterns', 'Robust to outliers'],
                'cons': ['Longer training time', 'Can overfit', 'Less interpretable'],
                'use_case': 'Best for production systems where accuracy is paramount'
            },
            'Neural Network': {
                'pros': ['Can learn complex non-linear patterns', 'Scalable', 'Good for large datasets'],
                'cons': ['Requires more data', 'Longer training time', 'Black box model'],
                'use_case': 'Best for large-scale systems with abundant data'
            }
        }
        for model, info in recommendations.items():
            status = "🏆 RECOMMENDED" if model == best_model else "ℹ️ "
            print(f"\n{status} {model}:")
            print(f"  Pros: {', '.join(info['pros'])}")
            print(f"  Cons: {', '.join(info['cons'])}")
            print(f"  Use Case: {info['use_case']}")
            if model == best_model:
                print(f"  Performance: F1={self.results[model]['f1_score']:.4f}, Accuracy={self.results[model]['accuracy']:.4f}")
def main():
    """
    Main execution function
    """
    print("🍎 Diet Recommendation Model Comparison System")
    print("=" * 50)
    # Initialize comparison system
    comparison = DietModelComparison()
    try:
        # Load and prepare data
        df = comparison.load_and_prepare_data()
        # Initialize models
        comparison.initialize_models()
        # Train and evaluate
        comparison.train_and_evaluate(df)
        # Display results
        best_model = comparison.display_results()
        # Create visualizations
        comparison.plot_results()
        # Save results
        comparison.save_results()
        # Provide recommendations
        comparison.get_recommendations()
        print(f"\n🎉 Analysis complete! Best model: {best_model}")
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    main()
