"""
ML Model Training and Management for Bread Porosity Prediction
Handles model training, evaluation, cross-validation, and persistence
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
import logging
import pickle

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    cross_val_score, cross_validate, train_test_split, KFold
)
from sklearn.metrics import (
    mean_squared_error, r2_score, mean_absolute_error, 
    mean_absolute_percentage_error
)

try:
    from .recipe_ml_advanced import (
        RecipeFeatureEngineer, IngredientAnalyzer, InstructionAnalyzer
    )
except (ImportError, ValueError):
    from recipe_ml_advanced import (
        RecipeFeatureEngineer, IngredientAnalyzer, InstructionAnalyzer
    )

logger = logging.getLogger(__name__)


class MLModelTrainer:
    """Trains ML models for porosity prediction"""
    
    def __init__(self, model_dir: str = "./ml_models", verbose: bool = True):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.verbose = verbose
        self.feature_engineer = RecipeFeatureEngineer()
        
        # Multiple models for ensemble
        self.models = {
            "random_forest": RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            "linear": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
        }
        
        self.scaler = StandardScaler()
        self.feature_names = []
        self.training_stats = {}
        self.model_metadata = {}
        self._load_models()
    
    def train_models(self, recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train all models on recipe data
        
        Args:
            recipes: List of recipe dicts with measured_porosity
        
        Returns:
            Training results and metrics
        """
        # Filter recipes with porosity measurements
        training_recipes = [r for r in recipes if r.get("measured_porosity") is not None]
        
        if len(training_recipes) < 5:
            logger.warning(f"Only {len(training_recipes)} recipes with porosity data. Need at least 5 for reliable training.")
            if len(training_recipes) == 0:
                return {"error": "No training data available", "trained_models": []}
        
        if self.verbose:
            print(f"Training on {len(training_recipes)} recipes with measured porosity...")
        
        # Extract features
        X, y = self._extract_training_data(training_recipes)
        
        if X is None or len(X) < 5:
            return {"error": "Could not extract features from recipes", "trained_models": []}
        
        # Store feature names
        self.feature_names = self._get_feature_names()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train all models
        results = {
            "timestamp": datetime.now().isoformat(),
            "n_training_samples": len(X),
            "models": {},
        }
        
        # Cross-validation setup
        kfold = KFold(n_splits=min(5, len(X) - 1), shuffle=True, random_state=42)
        
        for model_name, model in self.models.items():
            if self.verbose:
                print(f"  Training {model_name}...")
            
            try:
                # Cross-validation
                cv_scores = cross_validate(
                    model, X_scaled, y,
                    cv=kfold,
                    scoring={'r2': 'r2', 'mae': 'neg_mean_absolute_error', 'mse': 'neg_mean_squared_error'},
                    n_jobs=-1 if model_name != 'linear' else 1
                )
                
                # Train on full training set
                model.fit(X_scaled, y)
                
                # Evaluate on training set
                y_pred = model.predict(X_scaled)
                train_r2 = r2_score(y, y_pred)
                train_mae = mean_absolute_error(y, y_pred)
                train_rmse = np.sqrt(mean_squared_error(y, y_pred))
                
                # Store results
                results["models"][model_name] = {
                    "trained": True,
                    "cv_r2_mean": float(cv_scores['test_r2'].mean()),
                    "cv_r2_std": float(cv_scores['test_r2'].std()),
                    "cv_mae_mean": float(-cv_scores['test_mae'].mean()),
                    "cv_mae_std": float(cv_scores['test_mae'].std()),
                    "train_r2": float(train_r2),
                    "train_mae": float(train_mae),
                    "train_rmse": float(train_rmse),
                }
                
                if self.verbose:
                    print(f"    CV R²: {cv_scores['r2'].mean():.3f} ± {cv_scores['r2'].std():.3f}")
                    print(f"    CV MAE: {-cv_scores['mae'].mean():.2f} ± {cv_scores['mae'].std():.2f}%")
            
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                results["models"][model_name] = {"trained": False, "error": str(e)}
        
        # Save models
        self._save_models()
        
        # Store metadata
        self.model_metadata = results
        
        if self.verbose:
            print("✓ Training complete")
        
        return results
    
    def predict(self, recipe: Dict[str, Any], use_ensemble: bool = True) -> Tuple[float, Dict]:
        """
        Predict porosity for a recipe
        
        Args:
            recipe: Recipe dictionary
            use_ensemble: Average predictions from multiple models
        
        Returns:
            Tuple of (predicted_porosity, confidence_info)
        """
        try:
            # Engineer features
            features = self.feature_engineer.engineer_features(recipe)
            X = np.array([self._features_to_array(features)])
            X_scaled = self.scaler.transform(X)
            
            if use_ensemble:
                # Ensemble prediction
                predictions = []
                valid_models = 0
                
                for model_name, model in self.models.items():
                    try:
                        pred = model.predict(X_scaled)[0]
                        predictions.append(pred)
                        valid_models += 1
                    except:
                        pass
                
                if valid_models == 0:
                    return 0.0, {"error": "No trained models available"}
                
                predicted_porosity = np.mean(predictions)
                prediction_std = np.std(predictions)
            else:
                # Use best model (random forest)
                try:
                    predicted_porosity = self.models['random_forest'].predict(X_scaled)[0]
                    prediction_std = 0.0
                except:
                    return 0.0, {"error": "Random Forest model not available"}
            
            # Clamp to reasonable range
            predicted_porosity = max(10, min(45, predicted_porosity))
            
            # Generate confidence info
            confidence_info = {
                "predicted_porosity": round(float(predicted_porosity), 1),
                "prediction_std": round(float(prediction_std), 1),
                "n_training_samples": self.model_metadata.get("n_training_samples", 0),
                "model_performance": self._get_model_performance_summary(),
                "feature_contributions": self._get_top_features(X[0]),
                "prediction_factors": self._explain_prediction(features),
            }
            
            return float(predicted_porosity), confidence_info
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 0.0, {"error": str(e)}
    
    def _extract_training_data(self, recipes: List[Dict]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Extract features and targets from training recipes"""
        X_list = []
        y_list = []
        
        for recipe in recipes:
            try:
                features = self.feature_engineer.engineer_features(recipe)
                X = self._features_to_array(features)
                y = recipe.get("measured_porosity")
                
                if y is not None and 5 <= y <= 50:  # Reasonable porosity range
                    X_list.append(X)
                    y_list.append(y)
            except Exception as e:
                logger.debug(f"Skipping recipe: {e}")
                continue
        
        if not X_list:
            return None, None
        
        return np.array(X_list), np.array(y_list)
    
    def _features_to_array(self, features) -> np.ndarray:
        """Convert RecipeFeatures to numpy array"""
        feature_dict = features.__dict__ if hasattr(features, '__dict__') else features
        return np.array([
            feature_dict.get('hydration_ratio', 0.65),
            feature_dict.get('baker_percentage', 100),
            feature_dict.get('total_fermentation_hours', 8),
            feature_dict.get('bulk_fermentation_ratio', 0.5),
            feature_dict.get('fermentation_temperature_factor', 0.6),
            feature_dict.get('gluten_development_score', 0.7),
            feature_dict.get('hydrophilic_score', 0.6),
            feature_dict.get('enzymatic_activity_score', 0.6),
            feature_dict.get('salt_percentage', 2.0),
            feature_dict.get('starter_percentage', 20),
            feature_dict.get('sugar_percentage', 0),
            feature_dict.get('fat_percentage', 0),
            feature_dict.get('whole_grain_percentage', 0),
            feature_dict.get('mixing_intensity', 0.5),
            feature_dict.get('oven_temperature_norm', 0.4),
            feature_dict.get('cooking_vessel_openness', 0.5),
            feature_dict.get('total_cook_time_min', 200),
            feature_dict.get('dough_extensibility', 0.7),
            feature_dict.get('fermentation_power', 0.6),
            feature_dict.get('crumb_potential_score', 0.65),
        ])
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names in order"""
        return [
            'hydration_ratio',
            'baker_percentage',
            'total_fermentation_hours',
            'bulk_fermentation_ratio',
            'fermentation_temperature_factor',
            'gluten_development_score',
            'hydrophilic_score',
            'enzymatic_activity_score',
            'salt_percentage',
            'starter_percentage',
            'sugar_percentage',
            'fat_percentage',
            'whole_grain_percentage',
            'mixing_intensity',
            'oven_temperature_norm',
            'cooking_vessel_openness',
            'total_cook_time_min',
            'dough_extensibility',
            'fermentation_power',
            'crumb_potential_score',
        ]
    
    def _get_model_performance_summary(self) -> Dict[str, Any]:
        """Get summary of model performance"""
        best_model = None
        best_r2 = -1
        
        for model_name, metrics in self.model_metadata.get("models", {}).items():
            if metrics.get("trained"):
                r2 = metrics.get("cv_r2_mean", -1)
                if r2 > best_r2:
                    best_r2 = r2
                    best_model = model_name
        
        if best_model:
            metrics = self.model_metadata["models"][best_model]
            return {
                "best_model": best_model,
                "r2_score": float(metrics.get("cv_r2_mean", 0)),
                "mae": float(metrics.get("cv_mae_mean", 0)),
            }
        return {"best_model": None, "r2_score": 0.0, "mae": 0.0}
    
    def _get_top_features(self, X: np.ndarray) -> List[Tuple[str, float]]:
        """Get top contributing features"""
        try:
            model = self.models['random_forest']
            importances = model.feature_importances_
            top_indices = np.argsort(importances)[-5:][::-1]
            
            top_features = [
                (self.feature_names[i], float(X[i]))
                for i in top_indices
            ]
            return top_features
        except:
            return []
    
    def _explain_prediction(self, features) -> Dict[str, str]:
        """Generate human-readable explanation of prediction factors"""
        feature_dict = features.__dict__ if hasattr(features, '__dict__') else features
        
        hydration = feature_dict.get('hydration_ratio', 0.65)
        fermentation = feature_dict.get('fermentation_power', 0.6)
        gluten = feature_dict.get('gluten_development_score', 0.7)
        
        explanations = []
        
        # Hydration analysis
        if hydration > 0.75:
            explanations.append("High hydration → larger holes potential")
        elif hydration < 0.60:
            explanations.append("Low hydration → finer, more uniform crumb")
        else:
            explanations.append("Moderate hydration → balanced crumb structure")
        
        # Fermentation analysis
        if fermentation > 0.75:
            explanations.append("Strong fermentation power → good oven spring")
        elif fermentation < 0.50:
            explanations.append("Weak fermentation → denser crumb")
        
        # Gluten analysis
        if gluten > 0.85:
            explanations.append("High gluten flour → strong dough, open crumb")
        elif gluten < 0.65:
            explanations.append("Low gluten flour → weaker structure")
        
        return {
            "factors": ", ".join(explanations) if explanations else "Analysis unavailable",
            "primary_factor": explanations[0] if explanations else "Analysis unavailable",
        }
    
    def _save_models(self):
        """Save trained models to disk"""
        for model_name, model in self.models.items():
            try:
                model_path = self.model_dir / f"{model_name}_model.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            except Exception as e:
                logger.error(f"Error saving {model_name} model: {e}")
        
        # Save scaler
        try:
            scaler_path = self.model_dir / "scaler.pkl"
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
        except Exception as e:
            logger.error(f"Error saving scaler: {e}")
        
        # Save metadata
        try:
            metadata_path = self.model_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump({
                    **self.model_metadata,
                    "feature_names": self.feature_names
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _load_models(self):
        """Load trained models from disk"""
        for model_name in self.models.keys():
            try:
                model_path = self.model_dir / f"{model_name}_model.pkl"
                if model_path.exists():
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
            except Exception as e:
                logger.debug(f"Could not load {model_name} model: {e}")
        
        # Load scaler
        try:
            scaler_path = self.model_dir / "scaler.pkl"
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
        except Exception as e:
            logger.debug(f"Could not load scaler: {e}")
        
        # Load metadata
        try:
            metadata_path = self.model_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.model_metadata = metadata
                    self.feature_names = metadata.get("feature_names", [])
        except Exception as e:
            logger.debug(f"Could not load metadata: {e}")
    
    def get_training_report(self) -> str:
        """Generate comprehensive training report"""
        report = "ML MODEL TRAINING REPORT\n"
        report += "=" * 70 + "\n"
        report += f"Timestamp: {self.model_metadata.get('timestamp', 'Unknown')}\n"
        report += f"Training Samples: {self.model_metadata.get('n_training_samples', 0)}\n"
        report += f"Number of Features: {len(self.feature_names)}\n"
        report += "\n" + "MODEL PERFORMANCE".center(70) + "\n"
        report += "-" * 70 + "\n"
        
        for model_name, metrics in self.model_metadata.get("models", {}).items():
            if metrics.get("trained"):
                report += f"\n{model_name.upper()}\n"
                report += f"  Cross-Val R²:  {metrics.get('cv_r2_mean', 0):.3f} ± {metrics.get('cv_r2_std', 0):.3f}\n"
                report += f"  Cross-Val MAE: {metrics.get('cv_mae_mean', 0):.2f} ± {metrics.get('cv_mae_std', 0):.2f}%\n"
                report += f"  Train R²:      {metrics.get('train_r2', 0):.3f}\n"
                report += f"  Train RMSE:    {metrics.get('train_rmse', 0):.2f}%\n"
            else:
                report += f"\n{model_name.upper()}: Not trained\n"
        
        return report
    
    def get_feature_importance_report(self) -> str:
        """Generate feature importance report from random forest"""
        report = "FEATURE IMPORTANCE FOR POROSITY PREDICTION\n"
        report += "=" * 70 + "\n"
        
        try:
            model = self.models['random_forest']
            importances = model.feature_importances_
            
            # Sort features by importance
            indices = np.argsort(importances)[::-1]
            
            for rank, idx in enumerate(indices[:15], 1):
                feature_name = self.feature_names[idx] if idx < len(self.feature_names) else f"Feature {idx}"
                importance = importances[idx]
                pct = importance * 100
                bar = "█" * int(pct / 2.5) + "░" * (40 - int(pct / 2.5))
                report += f"{rank:2}. {feature_name:30} {pct:5.1f}% {bar}\n"
            
            return report
        except:
            return report + "Feature importance not available\n"
