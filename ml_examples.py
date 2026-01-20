"""
Example usage of the revamped ML-based recipe porosity prediction system
Demonstrates advanced ingredient and instruction analysis with ensemble learning
"""

import json
from pathlib import Path
from recipe_ml_advanced import RecipeFeatureEngineer, IngredientAnalyzer, InstructionAnalyzer
from recipe_ml_trainer import MLModelTrainer
from recipe_predictor import RecipePredictor


def load_example_recipes():
    """Load example recipes from recipes_example.json"""
    recipes_file = Path("recipes_example.json")
    if not recipes_file.exists():
        print("Warning: recipes_example.json not found. Using built-in examples.")
        return []
    
    try:
        with open(recipes_file, 'r') as f:
            return json.load(f)
    except:
        return []


def demonstrate_ingredient_analysis():
    """Demonstrate ingredient analysis capabilities"""
    print("\n" + "=" * 70)
    print("INGREDIENT ANALYSIS DEMONSTRATION")
    print("=" * 70)
    
    analyzer = IngredientAnalyzer(verbose=True)
    
    # Example recipes with different ingredient compositions
    recipes = [
        {
            "name": "Classic Sourdough",
            "ingredients": {
                "bread flour": 500,
                "water": 325,
                "salt": 10,
                "sourdough starter": 100
            }
        },
        {
            "name": "High Hydration Loaf",
            "ingredients": {
                "bread flour": 500,
                "water": 380,
                "salt": 10,
                "sourdough starter": 100
            }
        },
        {
            "name": "Whole Wheat Blend",
            "ingredients": {
                "bread flour": 350,
                "whole wheat": 150,
                "water": 330,
                "salt": 10,
                "honey": 10,
                "sourdough starter": 100
            }
        }
    ]
    
    for recipe in recipes:
        print(f"\n{recipe['name']}:")
        print("-" * 70)
        
        analysis = analyzer.analyze_ingredients(recipe['ingredients'])
        
        print(f"  Hydration Ratio: {analysis.get('hydration_ratio', 0):.2f}")
        print(f"  Gluten Score: {analysis.get('gluten_development_score', 0):.2f}")
        print(f"  Fermentation Score: {analysis.get('enzymatic_activity_score', 0):.2f}")
        print(f"  Hydrophilic Score: {analysis.get('hydrophilic_score', 0):.2f}")
        print(f"  Salt %: {analysis.get('salt_percentage', 0):.2f}%")
        print(f"  Starter %: {analysis.get('starter_percentage', 0):.2f}%")
        print(f"  Sugar %: {analysis.get('sugar_percentage', 0):.2f}%")


def demonstrate_instruction_analysis():
    """Demonstrate instruction analysis capabilities"""
    print("\n" + "=" * 70)
    print("INSTRUCTION ANALYSIS DEMONSTRATION")
    print("=" * 70)
    
    analyzer = InstructionAnalyzer(verbose=True)
    
    instructions_examples = [
        {
            "name": "Quick Fermentation",
            "text": "Mix dough. Let rise at room temperature for 4 hours. Shape and bake at 450°C."
        },
        {
            "name": "Traditional Cold Fermentation",
            "text": "Mix dough with autolyse. Perform stretch and fold every 30 minutes for 2 hours. "
                   "Cold ferment overnight in fridge (12 hours). Shape and proof for 2 hours at room temperature. "
                   "Bake in preheated Dutch oven at 450°C."
        },
        {
            "name": "Long Bulk Fermentation",
            "text": "Mix dough using slap and fold technique. Perform 4 sets of coil folds during bulk fermentation. "
                   "Bulk ferment at room temperature for 5 hours. Final proof for 2 hours. Bake on baking stone."
        }
    ]
    
    for example in instructions_examples:
        print(f"\n{example['name']}:")
        print("-" * 70)
        
        analysis = analyzer.analyze_instructions(example['text'])
        
        print(f"  Mixing Intensity: {analysis.get('mixing_intensity', 0):.2f}")
        print(f"  Fermentation Temp Factor: {analysis.get('fermentation_temperature_factor', 0):.2f}")
        print(f"  Process Complexity: {analysis.get('process_complexity', 0):.2f}")
        print(f"  Has Autolyse: {analysis.get('has_autolyse', False)}")
        print(f"  Has Bulk Ferment: {analysis.get('has_bulk_ferment', False)}")
        print(f"  Has Cold Ferment: {analysis.get('has_cold_ferment', False)}")
        print(f"  Has Stretch & Fold: {analysis.get('has_stretch_fold', False)}")


def demonstrate_feature_engineering():
    """Demonstrate feature engineering from complete recipes"""
    print("\n" + "=" * 70)
    print("FEATURE ENGINEERING DEMONSTRATION")
    print("=" * 70)
    
    engineer = RecipeFeatureEngineer()
    
    recipe = {
        "name": "Exemplary Sourdough",
        "ingredients": {
            "bread flour": 500,
            "water": 350,
            "salt": 10,
            "sourdough starter": 100
        },
        "mixing_time_min": 10,
        "proof_time_min": 480,
        "oven_temp_c": 450,
        "cooking_vessel": "dutch oven",
        "cook_time_min": 40,
        "room_temp_c": 22,
        "room_humidity_pct": 60,
        "instructions": "Autolyse for 1 hour. Perform stretch and fold 4 times over 2 hours. "
                       "Bulk ferment 4 hours at room temperature. Cold ferment overnight (12 hours). "
                       "Final proof 2 hours. Bake in Dutch oven at 450°C."
    }
    
    print(f"\nRecipe: {recipe['name']}")
    print("-" * 70)
    
    features = engineer.engineer_features(recipe)
    
    print("\nCore Features:")
    print(f"  Hydration Ratio: {features.hydration_ratio:.2f}")
    print(f"  Baker Percentage: {features.baker_percentage:.1f}%")
    print(f"  Total Fermentation: {features.total_fermentation_hours:.1f} hours")
    
    print("\nQuality Scores:")
    print(f"  Gluten Development: {features.gluten_development_score:.2f}")
    print(f"  Hydrophilic Score: {features.hydrophilic_score:.2f}")
    print(f"  Enzymatic Activity: {features.enzymatic_activity_score:.2f}")
    print(f"  Dough Extensibility: {features.dough_extensibility:.2f}")
    print(f"  Fermentation Power: {features.fermentation_power:.2f}")
    print(f"  Crumb Potential: {features.crumb_potential_score:.2f}")
    
    print("\nProcess Parameters:")
    print(f"  Mixing Intensity: {features.mixing_intensity:.2f}")
    print(f"  Oven Temp (normalized): {features.oven_temperature_norm:.2f}")
    print(f"  Vessel Openness: {features.cooking_vessel_openness:.2f}")
    print(f"  Total Cook Time: {features.total_cook_time_min:.1f} minutes")


def demonstrate_ml_training_and_prediction():
    """Demonstrate ML model training and prediction"""
    print("\n" + "=" * 70)
    print("ML TRAINING & PREDICTION DEMONSTRATION")
    print("=" * 70)
    
    # Load example recipes
    recipes = load_example_recipes()
    
    if not recipes:
        print("Loading built-in example recipes...")
        recipes = [
            {
                "id": 1,
                "name": "Classic Sourdough",
                "ingredients": {"bread flour": 500, "water": 325, "salt": 10, "sourdough starter": 100},
                "mixing_time_min": 10,
                "proof_time_min": 480,
                "oven_temp_c": 450,
                "cooking_vessel": "dutch oven",
                "cook_time_min": 40,
                "measured_porosity": 28.5,
                "room_temp_c": 21,
            },
            {
                "id": 2,
                "name": "High Hydration",
                "ingredients": {"bread flour": 500, "water": 380, "salt": 10, "sourdough starter": 100},
                "mixing_time_min": 15,
                "proof_time_min": 540,
                "oven_temp_c": 460,
                "cooking_vessel": "dutch oven",
                "cook_time_min": 38,
                "measured_porosity": 32.1,
                "room_temp_c": 22,
            },
        ]
    
    print(f"Loaded {len(recipes)} example recipes")
    
    # Filter recipes with measured porosity
    training_recipes = [r for r in recipes if r.get("measured_porosity")]
    print(f"Training recipes (with measured porosity): {len(training_recipes)}")
    
    if not training_recipes:
        print("No recipes with measured porosity. Skipping ML training.")
        return
    
    # Initialize trainer
    print("\nTraining ML models...")
    trainer = MLModelTrainer(verbose=False)
    training_results = trainer.train_models(training_recipes)
    
    print(trainer.get_training_report())
    print(trainer.get_feature_importance_report())
    
    # Make predictions
    print("\n" + "=" * 70)
    print("SAMPLE PREDICTIONS")
    print("=" * 70)
    
    for recipe in training_recipes[:3]:
        prediction, confidence = trainer.predict(recipe)
        actual = recipe.get("measured_porosity")
        
        print(f"\n{recipe.get('name', 'Unknown Recipe')}:")
        print(f"  Actual Porosity: {actual}%")
        print(f"  Predicted Porosity: {prediction:.1f}%")
        actual_val = actual if actual is not None else 0
        print(f"  Error: {abs(prediction - actual_val):.1f}%")
        print(f"  Prediction Method: {confidence.get('method', 'Ensemble ML')}")
        
        if "model_performance" in confidence:
            perf = confidence["model_performance"]
            print(f"  Best Model: {perf.get('best_model')}")
            print(f"  Model R²: {perf.get('r2_score', 0):.3f}")


def demonstrate_advanced_predictor():
    """Demonstrate the advanced RecipePredictor with new features"""
    print("\n" + "=" * 70)
    print("ADVANCED RECIPE PREDICTOR DEMONSTRATION")
    print("=" * 70)
    
    recipes = load_example_recipes()
    
    if not recipes:
        print("No example recipes found. Skipping predictor demonstration.")
        return
    
    print(f"Initializing predictor with {len(recipes)} recipes...")
    predictor = RecipePredictor(recipes, use_advanced_ml=True)
    
    # Make predictions for each recipe
    print("\n" + "-" * 70)
    for recipe in recipes[:3]:
        print(predictor.get_detailed_prediction_report(recipe))


def main():
    """Run all demonstrations"""
    print("\n")
    print("█" * 70)
    print("ADVANCED BREAD POROSITY ML SYSTEM - DEMONSTRATION".center(70))
    print("█" * 70)
    
    try:
        demonstrate_ingredient_analysis()
    except Exception as e:
        print(f"Error in ingredient analysis: {e}")
    
    try:
        demonstrate_instruction_analysis()
    except Exception as e:
        print(f"Error in instruction analysis: {e}")
    
    try:
        demonstrate_feature_engineering()
    except Exception as e:
        print(f"Error in feature engineering: {e}")
    
    try:
        demonstrate_ml_training_and_prediction()
    except Exception as e:
        print(f"Error in ML training: {e}")
    
    try:
        demonstrate_advanced_predictor()
    except Exception as e:
        print(f"Error in advanced predictor: {e}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nThe new ML system provides:")
    print("  ✓ Ingredient analysis (hydration, gluten, fermentation potential)")
    print("  ✓ Instruction parsing (mixing, fermentation, temperature factors)")
    print("  ✓ Advanced feature engineering (20+ computed features)")
    print("  ✓ Ensemble ML models (Random Forest, Gradient Boosting, Linear, Ridge)")
    print("  ✓ Cross-validation and statistical rigor")
    print("  ✓ Detailed prediction explanations")
    print("  ✓ Feature importance analysis")
    print()


if __name__ == "__main__":
    main()
