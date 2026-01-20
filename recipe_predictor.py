"""
Recipe Porosity Predictor
Predicts bread porosity based on recipe parameters using trained ML models
Integrates advanced ingredient and instruction analysis with ensemble ML
"""

import json
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
from pathlib import Path
import logging

try:
    try:
        from .recipe_ml_trainer import MLModelTrainer
        from .recipe_ml_advanced import IngredientAnalyzer, InstructionAnalyzer
    except (ImportError, ValueError):
        from recipe_ml_trainer import MLModelTrainer
        from recipe_ml_advanced import IngredientAnalyzer, InstructionAnalyzer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from .shared_utils import encode_vessel_openness
except (ImportError, ValueError):
    from shared_utils import encode_vessel_openness

logger = logging.getLogger(__name__)


class RecipePredictor:
    """Predicts porosity from recipe parameters using correlation analysis and advanced ML"""
    
    def __init__(self, recipes: List[Dict], use_advanced_ml: bool = True):
        """
        Initialize predictor with recipe data
        
        Args:
            recipes: List of recipe dicts with measured porosity
            use_advanced_ml: Use advanced ML models if available (default True)
        """
        self.recipes = recipes
        self.trained = False
        self.feature_correlations = {}
        self.mean_porosity = None
        self.normalization_params = {}
        
        # Advanced ML components
        self.use_advanced_ml = use_advanced_ml and ML_AVAILABLE
        self.ml_trainer = None
        self.ingredient_analyzer = None
        self.instruction_analyzer = None
        
        if self.use_advanced_ml:
            try:
                self.ml_trainer = MLModelTrainer(verbose=False)
                self.ingredient_analyzer = IngredientAnalyzer()
                self.instruction_analyzer = InstructionAnalyzer()
                
                # Train advanced models
                training_results = self.ml_trainer.train_models(recipes)
                if "error" not in training_results:
                    logger.info("✓ Advanced ML models trained successfully")
            except Exception as e:
                logger.warning(f"Advanced ML initialization failed, using legacy mode: {e}")
                self.use_advanced_ml = False
        
        # Feature extraction mappings
        self.numeric_features = [
            "mixing_time_min",
            "proof_time_min", 
            "oven_temp_c",
            "cook_time_min"
        ]
        
        self.categorical_features = ["cooking_vessel"]
        
        # Train on available data
        self._train()
    
    def _train(self):
        """Train the predictor on available recipe data"""
        # Get recipes with porosity measurements
        training_recipes = [r for r in self.recipes 
                           if r.get("measured_porosity") is not None]
        
        if not training_recipes:
            print("Warning: No training data available (no recipes with measured porosity)")
            return
        
        # Extract features and targets
        features_list = []
        targets = []
        
        for recipe in training_recipes:
            try:
                features = self._extract_features(recipe)
                if features is not None:
                    features_list.append(features)
                    targets.append(recipe["measured_porosity"])
            except:
                continue
        
        if not features_list:
            print("Warning: Could not extract features from any recipe")
            return
        
        # Compute correlations with porosity
        targets_array = np.array(targets)
        self.mean_porosity = np.mean(targets_array)
        
        # Correlate each feature with porosity
        feature_names = self._get_feature_names()
        features_array = np.array(features_list)
        
        for i, feature_name in enumerate(feature_names):
            correlation, p_value = stats.pearsonr(features_array[:, i], targets_array)
            self.feature_correlations[feature_name] = {
                "correlation": correlation,
                "p_value": p_value
            }
        
        # Normalize features for scaling
        self.normalization_params = {}
        for i, feature_name in enumerate(feature_names):
            self.normalization_params[feature_name] = {
                "mean": np.mean(features_array[:, i]),
                "std": np.std(features_array[:, i])
            }
        
        self.trained = True
    
    def _extract_features(self, recipe: Dict) -> Optional[np.ndarray]:
        """
        Extract numeric features from a recipe
        
        Args:
            recipe: Recipe dict
            
        Returns:
            Numpy array of feature values or None if extraction fails
        """
        features = []
        
        # Numeric features
        for feature_name in self.numeric_features:
            if feature_name not in recipe:
                return None
            features.append(float(recipe[feature_name]))
        
        # Categorical features (encoded)
        vessel = recipe.get("cooking_vessel", "").lower()
        vessel_score = encode_vessel_openness(vessel)
        features.append(vessel_score)
        
        # Ingredient-based features
        ingredients = recipe.get("ingredients", {})
        water_content = ingredients.get("water", 0) or ingredients.get("Water", 0)
        flour_content = ingredients.get("flour", 0) or ingredients.get("Flour", 0)
        
        if flour_content > 0:
            hydration = water_content / flour_content
        else:
            hydration = 0.5  # Default hydration
        
        features.append(hydration)
        
        return np.array(features)
    
    def _get_feature_names(self) -> List[str]:
        """Get list of feature names in order"""
        return self.numeric_features + ["cooking_vessel", "hydration"]
    
    def predict_porosity(self, recipe: Dict) -> Tuple[Optional[float], Dict]:
        """
        Predict porosity for a recipe based on its parameters
        Uses advanced ML if available, otherwise falls back to legacy method
        
        Args:
            recipe: Recipe dict to predict for
            
        Returns:
            Tuple of (predicted_porosity, confidence_info)
        """
        # Try advanced ML first
        if self.use_advanced_ml and self.ml_trainer:
            try:
                pred, conf_info = self.ml_trainer.predict(recipe, use_ensemble=True)
                if pred is not None:
                    # Combine with legacy confidence
                    conf_info["method"] = "Advanced ML (Ensemble)"
                    conf_info["legacy_prediction"] = self._predict_legacy(recipe)[0]
                    return pred, conf_info
            except Exception as e:
                logger.debug(f"Advanced ML prediction failed: {e}")
        
        # Fall back to legacy correlation-based method
        return self._predict_legacy(recipe)
    
    def _predict_legacy(self, recipe: Dict) -> Tuple[Optional[float], Dict]:
        """Legacy prediction method for recipes without ML models."""
        # Simple correlation-based estimation
        features = self._extract_features(recipe)
        if features is None or len(features) == 0:
            return None, {"error": "Could not extract features"}
        
        # Basic formula: hydration * gluten * fermentation factors
        hydration = features[-1] if len(features) > 0 else 0.65
        base_porosity = 20 + (hydration * 100 - 60) * 0.5
        base_porosity = max(10, min(50, base_porosity))
        
        return base_porosity, {"method": "legacy_correlation", "confidence": 0.5}
    
    def analyze_recipe_ingredients(self, recipe: Dict) -> Optional[Dict]:
        """
        Analyze recipe ingredients for porosity factors
        
        Args:
            recipe: Recipe dictionary
        
        Returns:
            Analysis of ingredients and their effects on porosity
        """
        if not self.ingredient_analyzer:
            return None
        
        try:
            ingredients = recipe.get("ingredients", {})
            analysis = self.ingredient_analyzer.analyze_ingredients(ingredients)
            return analysis
        except Exception as e:
            logger.debug(f"Ingredient analysis error: {e}")
            return None
    
    def analyze_recipe_instructions(self, recipe: Dict) -> Optional[Dict]:
        """
        Analyze recipe instructions for process factors
        
        Args:
            recipe: Recipe dictionary
        
        Returns:
            Analysis of process factors and their effects on porosity
        """
        if not self.instruction_analyzer:
            return None
        
        try:
            instructions = recipe.get("instructions", "")
            analysis = self.instruction_analyzer.analyze_instructions(instructions)
            return analysis
        except Exception as e:
            logger.debug(f"Instruction analysis error: {e}")
            return None
    
    def get_detailed_prediction_report(self, recipe: Dict) -> str:
        """
        Generate detailed report explaining the porosity prediction
        
        Args:
            recipe: Recipe dictionary
        
        Returns:
            Formatted text report
        """
        prediction, conf_info = self.predict_porosity(recipe)
        
        report = f"\nPOROSITY PREDICTION REPORT\n"
        report += "=" * 70 + "\n"
        report += f"Recipe: {recipe.get('name', 'Unknown')}\n"
        report += f"Prediction Method: {conf_info.get('method', 'Unknown')}\n"
        report += f"\nPREDICTED POROSITY: {prediction:.1f}%\n"
        
        if "prediction_std" in conf_info:
            report += f"Prediction Uncertainty: ±{conf_info['prediction_std']:.1f}%\n"
        
        report += f"Training Samples: {conf_info.get('training_samples', 'Unknown')}\n"
        report += f"Confidence Level: {conf_info.get('confidence_level', 'Unknown')}\n"
        
        # Feature analysis
        if "prediction_factors" in conf_info:
            factors = conf_info["prediction_factors"]
            report += "\nKEY FACTORS:\n"
            report += "-" * 70 + "\n"
            for factor in factors.get("factors", []):
                report += f"  • {factor}\n"
        
        # Ingredient analysis
        ingredient_analysis = self.analyze_recipe_ingredients(recipe)
        if ingredient_analysis:
            report += "\nINGREDIENT COMPOSITION:\n"
            report += "-" * 70 + "\n"
            report += f"  Hydration Ratio: {ingredient_analysis.get('hydration_ratio', 0):.2f}\n"
            report += f"  Gluten Development Score: {ingredient_analysis.get('gluten_development_score', 0):.2f}\n"
            report += f"  Enzymatic Activity Score: {ingredient_analysis.get('enzymatic_activity_score', 0):.2f}\n"
            report += f"  Salt %: {ingredient_analysis.get('salt_percentage', 0):.2f}%\n"
            report += f"  Sugar %: {ingredient_analysis.get('sugar_percentage', 0):.2f}%\n"
            report += f"  Fat %: {ingredient_analysis.get('fat_percentage', 0):.2f}%\n"
        
        # Instruction analysis
        instruction_analysis = self.analyze_recipe_instructions(recipe)
        if instruction_analysis:
            report += "\nPROCESS ANALYSIS:\n"
            report += "-" * 70 + "\n"
            report += f"  Mixing Intensity: {instruction_analysis.get('mixing_intensity', 0):.2f}\n"
            report += f"  Fermentation Temperature Factor: {instruction_analysis.get('fermentation_temperature_factor', 0):.2f}\n"
            if instruction_analysis.get("has_bulk_ferment"):
                report += "  ✓ Has bulk fermentation\n"
            if instruction_analysis.get("has_cold_ferment"):
                report += "  ✓ Has cold fermentation (slow fermentation = finer crumb)\n"
            if instruction_analysis.get("has_stretch_fold"):
                report += "  ✓ Uses stretch and fold (develops gluten)\n"
        
        report += "\n" + "=" * 70 + "\n"
        return report
    
    def get_ml_training_report(self) -> Optional[str]:
        """Get comprehensive ML training report"""
        if not self.ml_trainer:
            return None
        
        return self.ml_trainer.get_training_report()
    
    def get_feature_importance_report(self) -> Optional[str]:
        """Get feature importance report from ML models"""
        if not self.ml_trainer:
            return None
        
        return self.ml_trainer.get_feature_importance_report()
    
    def _get_feature_contributions(self, normalized_features: np.ndarray, 
                                   feature_names: List[str]) -> Dict[str, float]:
        """Get contribution of each feature to prediction"""
        contributions = {}
        for i, feature_name in enumerate(feature_names):
            corr_info = self.feature_correlations.get(feature_name, {})
            correlation = corr_info.get("correlation", 0)
            contribution = normalized_features[i] * correlation
            contributions[feature_name] = round(contribution, 3)
        return contributions
    
    def _calculate_confidence(self) -> str:
        """Calculate overall prediction confidence"""
        num_features_significant = sum(
            1 for info in self.feature_correlations.values()
            if info.get("p_value", 1) < 0.05
        )
        
        num_training = len([r for r in self.recipes if r.get("measured_porosity")])
        
        if num_training < 3:
            return "Low (< 3 training samples)"
        elif num_training < 10:
            return "Medium (few training samples)"
        elif num_features_significant < 2:
            return "Low (weak feature correlations)"
        else:
            return "High (good training data)"
    
    def get_correlations_report(self) -> str:
        """Get a report of feature correlations"""
        report = "FEATURE CORRELATIONS WITH POROSITY\n"
        report += "=" * 50 + "\n"
        
        for feature_name, info in self.feature_correlations.items():
            corr = info.get("correlation", 0)
            p_val = info.get("p_value", 1)
            significance = "***" if p_val < 0.05 else ("**" if p_val < 0.1 else "")
            report += f"{feature_name:20} {corr:+.3f}  (p={p_val:.3f}) {significance}\n"
        
        report += "\n*** p < 0.05 (significant)\n"
        report += "**  p < 0.1  (marginally significant)\n"
        return report
    
    def get_training_stats(self) -> Dict:
        """Get training statistics"""
        training_recipes = [r for r in self.recipes if r.get("measured_porosity")]
        porosity_values = [r["measured_porosity"] for r in training_recipes]
        
        if not porosity_values:
            return {
                "training_samples": 0,
                "mean_porosity": None,
                "porosity_std": None,
                "porosity_range": None
            }
        
        return {
            "training_samples": len(training_recipes),
            "mean_porosity": round(np.mean(porosity_values), 2),
            "porosity_std": round(np.std(porosity_values), 2),
            "porosity_min": round(min(porosity_values), 2),
            "porosity_max": round(max(porosity_values), 2),
            "porosity_range": (round(min(porosity_values), 2), round(max(porosity_values), 2))
        }
    
    def compute_r_squared(self) -> float:
        """
        Compute R² (coefficient of determination) for model quality
        Measures how well predictions match actual porosity values
        
        Returns:
            R² value between 0 and 1 (higher is better)
        """
        training_recipes = [r for r in self.recipes if r.get("measured_porosity")]
        if len(training_recipes) < 2:
            return 0.0
        
        actuals = []
        predictions = []
        
        for recipe in training_recipes:
            actual_porosity = recipe.get("measured_porosity")
            pred_porosity, _ = self.predict_porosity(recipe)
            
            if pred_porosity is not None:
                actuals.append(actual_porosity)
                predictions.append(pred_porosity)
        
        if not actuals:
            return 0.0
        
        actuals = np.array(actuals)
        predictions = np.array(predictions)
        
        ss_res = np.sum((actuals - predictions) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return max(0.0, min(1.0, r_squared))  # Clamp to [0, 1]
    
    def compute_confidence_intervals(self, confidence_level: float = 0.95) -> Dict[str, Tuple[float, float]]:
        """
        Compute confidence intervals for predictions
        
        Args:
            confidence_level: Confidence level (default 0.95 for 95% CI)
        
        Returns:
            Dict mapping feature names to (lower, upper) bounds
        """
        training_recipes = [r for r in self.recipes if r.get("measured_porosity")]
        if len(training_recipes) < 2:
            return {}
        
        porosity_values = np.array([r["measured_porosity"] for r in training_recipes])
        
        mean_porosity = np.mean(porosity_values)
        std_porosity = np.std(porosity_values, ddof=1)  # Sample std
        n = len(porosity_values)
        
        # T-distribution critical value
        t_value = stats.t.ppf((1 + confidence_level) / 2, n - 1)
        margin_error = t_value * (std_porosity / np.sqrt(n))
        
        ci_porosity = (mean_porosity - margin_error, mean_porosity + margin_error)
        
        # Feature-specific CIs
        intervals = {
            "porosity": (round(ci_porosity[0], 2), round(ci_porosity[1], 2)),
        }
        
        # Add CI for each feature
        for feature_name in self._get_feature_names():
            feature_values = []
            for recipe in training_recipes:
                features = self._extract_features(recipe)
                if features is not None:
                    for i, fname in enumerate(self._get_feature_names()):
                        if fname == feature_name:
                            feature_values.append(features[i])
                            break
            
            if feature_values and len(feature_values) > 1:
                fv = np.array(feature_values)
                f_mean = np.mean(fv)
                f_std = np.std(fv, ddof=1)
                f_t = stats.t.ppf((1 + confidence_level) / 2, len(fv) - 1)
                f_margin = f_t * (f_std / np.sqrt(len(fv)))
                intervals[feature_name] = (round(f_mean - f_margin, 2), round(f_mean + f_margin, 2))
        
        return intervals
    
    def compute_residuals(self) -> Dict:
        """
        Compute residuals (prediction errors) for model analysis
        
        Returns:
            Dict with residual statistics and lists
        """
        training_recipes = [r for r in self.recipes if r.get("measured_porosity")]
        if len(training_recipes) < 2:
            return {"residuals": [], "statistics": {}}
        
        residuals = []
        for recipe in training_recipes:
            actual = recipe.get("measured_porosity")
            predicted, _ = self.predict_porosity(recipe)
            
            if predicted is not None:
                residual = actual - predicted
                residuals.append({
                    "recipe_name": recipe.get("name", "Unknown"),
                    "actual": round(actual, 2),
                    "predicted": round(predicted, 2),
                    "residual": round(residual, 2),
                    "abs_error": round(abs(residual), 2)
                })
        
        if not residuals:
            return {"residuals": [], "statistics": {}}
        
        residual_values = [r["residual"] for r in residuals]
        
        return {
            "residuals": residuals,
            "statistics": {
                "mean_residual": round(np.mean(residual_values), 3),
                "std_residual": round(np.std(residual_values), 3),
                "mean_abs_error": round(np.mean([abs(r) for r in residual_values]), 2),
                "max_error": round(max([abs(r) for r in residual_values]), 2),
                "rmse": round(np.sqrt(np.mean(np.array(residual_values) ** 2)), 2)
            }
        }
    
    def compute_feature_importance(self) -> List[Tuple[str, float, float]]:
        """
        Compute feature importance rankings
        Based on correlation strength and statistical significance
        
        Returns:
            List of (feature_name, correlation, importance_score) tuples, sorted by importance
        """
        importance_scores = []
        
        for feature_name, info in self.feature_correlations.items():
            correlation = info.get("correlation", 0)
            p_value = info.get("p_value", 1)
            
            # Importance = |correlation| * significance_weight
            significance_weight = max(0, (0.05 - p_value) / 0.05) if p_value < 0.05 else 0
            importance = abs(correlation) * (1 + 2 * significance_weight)
            
            importance_scores.append((feature_name, correlation, importance))
        
        # Sort by importance descending
        importance_scores.sort(key=lambda x: x[2], reverse=True)
        return importance_scores
    
    def get_statistics_dashboard(self) -> Dict:
        """Get all statistics for dashboard display"""
        return {
            "training_stats": self.get_training_stats(),
            "r_squared": round(self.compute_r_squared(), 3),
            "confidence_intervals": self.compute_confidence_intervals(),
            "residuals": self.compute_residuals(),
            "feature_importance": self.compute_feature_importance(),
            "correlations": self.feature_correlations
        }
