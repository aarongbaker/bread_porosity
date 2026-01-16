"""
Recipe Porosity Predictor
Predicts bread porosity based on recipe parameters using trained models
"""

import json
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
from pathlib import Path


class RecipePredictor:
    """Predicts porosity from recipe parameters using correlation analysis"""
    
    def __init__(self, recipes: List[Dict]):
        """
        Initialize predictor with recipe data
        
        Args:
            recipes: List of recipe dicts with measured porosity
        """
        self.recipes = recipes
        self.trained = False
        self.feature_correlations = {}
        self.mean_porosity = None
        self.normalization_params = {}
        
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
        vessel_score = self._encode_vessel(vessel)
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
    
    def _encode_vessel(self, vessel: str) -> float:
        """Encode cooking vessel type as numeric value"""
        # Higher values correlate with more open-system cooking
        vessel_map = {
            "dutch oven": 0.3,      # Closed, less airflow
            "loaf pan": 0.2,        # Enclosed, minimal airflow
            "baking stone": 0.7,    # Open, good airflow
            "banneton": 0.5,        # Semi-open
            "bread cloche": 0.4,    # Covered, some airflow
            "oven": 0.6,            # Open oven
            "air fryer": 0.4,       # Forced convection
            "cast iron": 0.5        # Medium openness
        }
        
        # Find best match
        for key, value in vessel_map.items():
            if key in vessel.lower():
                return value
        
        return 0.5  # Default neutral value
    
    def predict_porosity(self, recipe: Dict) -> Tuple[Optional[float], Dict]:
        """
        Predict porosity for a recipe based on its parameters
        
        Args:
            recipe: Recipe dict to predict for
            
        Returns:
            Tuple of (predicted_porosity, confidence_info)
        """
        if not self.trained or self.mean_porosity is None:
            return None, {"error": "Predictor not trained. Need recipes with measured porosity."}
        
        try:
            features = self._extract_features(recipe)
            if features is None:
                return None, {"error": "Could not extract features from recipe"}
            
            # Normalize features
            feature_names = self._get_feature_names()
            normalized_features = []
            for i, feature_val in enumerate(features):
                feature_name = feature_names[i]
                params = self.normalization_params.get(feature_name, {"mean": 0, "std": 1})
                std = params["std"]
                if std == 0:
                    std = 1
                normalized = (feature_val - params["mean"]) / std
                normalized_features.append(normalized)
            
            normalized_features = np.array(normalized_features)
            
            # Weighted prediction based on correlations
            prediction = self.mean_porosity
            total_weight = 0
            
            for i, feature_name in enumerate(feature_names):
                corr_info = self.feature_correlations.get(feature_name, {})
                correlation = corr_info.get("correlation", 0)
                p_value = corr_info.get("p_value", 1)
                
                # Weight by correlation strength and statistical significance
                weight = abs(correlation) * (1 - min(p_value, 1))
                prediction += weight * normalized_features[i]
                total_weight += weight
            
            # Normalize prediction
            if total_weight > 0:
                prediction = self.mean_porosity + (prediction - self.mean_porosity) * 0.5
            
            # Clamp to reasonable range (0-50%)
            prediction = max(5, min(50, prediction))
            
            # Calculate confidence
            confidence_info = {
                "predicted_porosity": round(prediction, 2),
                "mean_porosity": round(self.mean_porosity, 2),
                "training_samples": len([r for r in self.recipes if r.get("measured_porosity")]),
                "feature_contributions": self._get_feature_contributions(normalized_features, feature_names),
                "confidence_level": self._calculate_confidence()
            }
            
            return prediction, confidence_info
        
        except Exception as e:
            return None, {"error": f"Prediction error: {str(e)}"}
    
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
