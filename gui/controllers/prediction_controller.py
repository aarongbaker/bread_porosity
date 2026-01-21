"""
Prediction Controller
Handles porosity prediction operations and coordinates with PredictionService
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any, Callable
import json

from services.prediction_service import PredictionService
from models.recipe import Recipe
from utils.logger import get_logger

logger = get_logger(__name__)


class PredictionController:
    """Controller for porosity prediction operations"""

    def __init__(self, prediction_service: PredictionService, view_callback: Optional[Callable] = None):
        """
        Initialize prediction controller

        Args:
            prediction_service: The prediction service to use
            view_callback: Callback to update the view (optional)
        """
        self.prediction_service = prediction_service
        self.view_callback = view_callback
        self.last_prediction: Optional[Dict[str, Any]] = None

    def predict_porosity(self, recipe: Recipe) -> Optional[Dict[str, Any]]:
        """
        Predict porosity for a recipe

        Args:
            recipe: Recipe to predict porosity for

        Returns:
            Prediction results if successful, None otherwise
        """
        try:
            prediction_result = self.prediction_service.predict_porosity(recipe)
            prediction = (
                prediction_result.to_dict()
                if hasattr(prediction_result, 'to_dict')
                else prediction_result
            )
            self.last_prediction = prediction

            if prediction:
                predicted_porosity = prediction.get('predicted_porosity', 'N/A')
                logger.info(f"Porosity predicted: {predicted_porosity}% for recipe {recipe.name}")

                if self.view_callback:
                    self.view_callback('porosity_predicted', recipe, prediction)

            return prediction

        except Exception as e:
            error_msg = f"Porosity prediction failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def predict_from_recipe_data(self, recipe_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predict porosity from recipe data dictionary

        Args:
            recipe_data: Recipe data dictionary

        Returns:
            Prediction results if successful, None otherwise
        """
        try:
            # Convert to Recipe object
            recipe = Recipe.from_dict(recipe_data)
            return self.predict_porosity(recipe)

        except Exception as e:
            logger.error(f"Failed to predict from recipe data: {e}")
            return None

    def train_model(self, recipes: list) -> Optional[Dict[str, Any]]:
        """
        Train the prediction model with recipe data

        Args:
            recipes: List of recipes with measured porosity

        Returns:
            Training results if successful, None otherwise
        """
        try:
            training_result = self.prediction_service.train_model(recipes)

            if training_result:
                logger.info("Prediction model trained successfully")

                if self.view_callback:
                    self.view_callback('model_trained', training_result)

            return training_result

        except Exception as e:
            error_msg = f"Model training failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def retrain_model(self) -> bool:
        """Retrain the prediction model using repository data."""
        try:
            return self.prediction_service.retrain_model()
        except Exception as e:
            logger.error(f"Failed to retrain model: {e}")
            return False

    def get_training_status(self) -> Dict[str, Any]:
        """
        Get the current training status of the model

        Returns:
            Training status information
        """
        try:
            return self.prediction_service.get_training_status()
        except Exception as e:
            logger.error(f"Failed to get training status: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current prediction model

        Returns:
            Model information if available
        """
        try:
            return self.prediction_service.get_model_info()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None

    def get_last_prediction(self) -> Optional[Dict[str, Any]]:
        """
        Get the last prediction result

        Returns:
            Last prediction results
        """
        return self.last_prediction

    def format_prediction_display(self, prediction: Dict[str, Any], recipe_name: str = "Unknown") -> str:
        """
        Format prediction results for display

        Args:
            prediction: Prediction results
            recipe_name: Name of the recipe

        Returns:
            Formatted display string
        """
        try:
            output = f"POROSITY PREDICTION FOR: {recipe_name}\n"
            output += "=" * 50 + "\n\n"

            predicted_porosity = prediction.get('predicted_porosity', 'N/A')
            output += f"PREDICTED POROSITY: {predicted_porosity}"

            if isinstance(predicted_porosity, (int, float)):
                output += ".1f"
            output += "%\n\n"

            # Confidence information
            confidence_info = prediction.get('confidence_info', {})
            if confidence_info:
                output += "CONFIDENCE LEVEL:\n"
                output += f"  {confidence_info.get('confidence_level', 'Unknown')}\n"
                output += f"  Training samples: {confidence_info.get('training_samples', 0)}\n"

                mean_porosity = confidence_info.get('mean_porosity')
                if mean_porosity is not None:
                    output += f"  Mean porosity: {mean_porosity:.1f}%\n"

                output += "\n"

            # Feature contributions
            contributions = confidence_info.get('feature_contributions', {})
            if contributions:
                output += "FEATURE CONTRIBUTIONS:\n"
                for feature, contribution in contributions.items():
                    output += f"  {feature:20} {contribution:+.3f}\n"
                output += "\n"

            # Actual vs predicted comparison
            actual_porosity = prediction.get('actual_porosity')
            if actual_porosity is not None:
                output += f"ACTUAL MEASURED: {actual_porosity:.1f}%\n"
                if isinstance(predicted_porosity, (int, float)):
                    error = abs(predicted_porosity - actual_porosity)
                    output += f"PREDICTION ERROR: {error:.1f}%\n"

            return output

        except Exception as e:
            logger.error(f"Failed to format prediction display: {e}")
            return f"Error formatting prediction: {str(e)}"

    def validate_prediction_data(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate recipe data for prediction

        Args:
            recipe_data: Recipe data to validate

        Returns:
            Validation result with 'valid' boolean and 'issues' list
        """
        issues = []

        # Check required fields
        required_fields = ['ingredients', 'mixing_time_min', 'proof_time_min',
                          'oven_temp_c', 'cook_time_min']

        for field in required_fields:
            if field not in recipe_data or recipe_data[field] is None:
                issues.append(f"Missing required field: {field}")

        # Check ingredients
        ingredients = recipe_data.get('ingredients', {})
        if not ingredients:
            issues.append("No ingredients specified")
        elif not any(isinstance(v, (int, float)) and v > 0 for v in ingredients.values()):
            issues.append("No valid ingredient quantities found")

        # Check numeric fields
        numeric_fields = ['mixing_time_min', 'proof_time_min', 'oven_temp_c', 'cook_time_min']
        for field in numeric_fields:
            value = recipe_data.get(field)
            if value is not None and not isinstance(value, (int, float)):
                issues.append(f"Field {field} must be numeric")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def get_prediction_history(self) -> list:
        """
        Get prediction history

        Returns:
            List of previous predictions
        """
        # TODO: Implement prediction history storage
        return []

    def clear_last_prediction(self) -> None:
        """Clear the last prediction result"""
        self.last_prediction = None

        if self.view_callback:
            self.view_callback('prediction_cleared')
