"""
Prediction Service
Business logic for porosity prediction from recipes
"""

from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

from models.recipe import Recipe
from repositories.recipe_repository import RecipeRepository
from utils.exceptions import ValidationError
from utils.logger import get_logger

# Import existing predictor
try:
    from recipe_predictor import RecipePredictor
    PREDICTOR_AVAILABLE = True
except ImportError:
    PREDICTOR_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("RecipePredictor not available - prediction features disabled")

logger = get_logger(__name__)


class PredictionResult:
    """Result of a porosity prediction"""

    def __init__(self,
                 predicted_porosity: Optional[float],
                 confidence_info: Dict[str, Any],
                 recipe_id: Optional[int] = None,
                 recipe_name: str = ""):
        self.predicted_porosity = predicted_porosity
        self.confidence_info = confidence_info
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "predicted_porosity": self.predicted_porosity,
            "confidence_info": self.confidence_info,
            "recipe_id": self.recipe_id,
            "recipe_name": self.recipe_name
        }


class PredictionService:
    """
    Service for predicting bread porosity from recipe parameters.

    Provides business logic for:
    - Porosity prediction from recipes
    - Model training and validation
    - Prediction confidence analysis
    - Recipe optimization suggestions
    """

    def __init__(self, recipe_repo: Optional[RecipeRepository] = None):
        """
        Initialize the prediction service.

        Args:
            recipe_repo: Repository for recipe data (optional)
        """
        self.recipe_repo = recipe_repo or RecipeRepository()
        self.predictor = None
        self._initialize_predictor()

    def _initialize_predictor(self) -> None:
        """Initialize the recipe predictor with available data"""
        if not PREDICTOR_AVAILABLE:
            logger.warning("RecipePredictor not available")
            return

        try:
            # Get recipes with measured porosity for training
            recipes_with_porosity = self.recipe_repo.find_all_with_porosity()

            if len(recipes_with_porosity) >= 3:  # Minimum for meaningful predictions
                recipe_dicts = [r.to_dict() for r in recipes_with_porosity]
                self.predictor = RecipePredictor(recipe_dicts, use_advanced_ml=True)
                logger.info(f"Initialized predictor with {len(recipes_with_porosity)} training recipes")
            else:
                logger.info(f"Only {len(recipes_with_porosity)} recipes with porosity data - need at least 3 for predictions")

        except Exception as e:
            logger.error(f"Failed to initialize predictor: {e}")
            self.predictor = None

    def predict_porosity(self, recipe: Recipe) -> PredictionResult:
        """
        Predict porosity for a recipe.

        Args:
            recipe: Recipe object to predict for

        Returns:
            PredictionResult with prediction and confidence info

        Raises:
            ValidationError: If recipe is invalid for prediction
        """
        if not PREDICTOR_AVAILABLE:
            raise ValidationError("Prediction service not available - RecipePredictor not found")

        if not self.predictor:
            raise ValidationError("Predictor not trained - need recipes with measured porosity")

        try:
            # Convert recipe to dict format expected by predictor
            recipe_dict = recipe.to_dict()

            # Make prediction
            predicted_porosity, confidence_info = self.predictor.predict_porosity(recipe_dict)

            result = PredictionResult(
                predicted_porosity=predicted_porosity,
                confidence_info=confidence_info,
                recipe_id=recipe.id,
                recipe_name=recipe.name
            )

            porosity_text = (
                f"{predicted_porosity:.1f}%" if predicted_porosity is not None else "N/A"
            )
            logger.info(
                f"Predicted porosity for {recipe.name}: {porosity_text} "
                f"(confidence: {confidence_info.get('confidence', 'unknown')})"
            )

            return result

        except Exception as e:
            logger.error(f"Prediction failed for recipe {recipe.name}: {e}")
            raise ValidationError(f"Failed to predict porosity: {e}") from e

    def predict_for_recipe_id(self, recipe_id: int) -> PredictionResult:
        """
        Predict porosity for a recipe by ID.

        Args:
            recipe_id: Recipe ID

        Returns:
            PredictionResult

        Raises:
            ValidationError: If recipe not found or invalid
        """
        recipe = self.recipe_repo.find_by_id(recipe_id)
        if not recipe:
            raise ValidationError(f"Recipe {recipe_id} not found")

        return self.predict_porosity(recipe)

    def get_prediction_report(self, recipe: Recipe) -> str:
        """
        Generate a detailed prediction report for a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Formatted text report
        """
        if not PREDICTOR_AVAILABLE or not self.predictor:
            return "Prediction service not available"

        try:
            recipe_dict = recipe.to_dict()
            return self.predictor.get_detailed_prediction_report(recipe_dict)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return f"Error generating report: {e}"

    def analyze_recipe_factors(self, recipe: Recipe) -> Dict[str, Any]:
        """
        Analyze the factors that influence porosity in a recipe.

        Args:
            recipe: Recipe to analyze

        Returns:
            Dictionary with factor analysis
        """
        analysis = {
            "hydration_ratio": recipe.get_hydration_ratio(),
            "total_time_hours": recipe.get_total_time_hours(),
            "ingredients_count": len(recipe.ingredients),
            "factors": []
        }

        # Hydration analysis
        if analysis["hydration_ratio"]:
            hydration = analysis["hydration_ratio"]
            if hydration < 0.6:
                analysis["factors"].append("Low hydration may result in denser crumb")
            elif hydration > 0.8:
                analysis["factors"].append("High hydration may increase porosity")
            else:
                analysis["factors"].append("Hydration ratio is in optimal range")

        # Time analysis
        total_time = analysis["total_time_hours"]
        if total_time < 8:
            analysis["factors"].append("Short fermentation time may limit porosity development")
        elif total_time > 24:
            analysis["factors"].append("Long fermentation may increase porosity")

        # Temperature analysis
        if recipe.oven_temp_c > 250:
            analysis["factors"].append("High oven temperature may create larger holes")
        elif recipe.oven_temp_c < 200:
            analysis["factors"].append("Low oven temperature may result in denser crumb")

        return analysis

    def get_training_status(self) -> Dict[str, Any]:
        """
        Get status of the prediction model training.

        Returns:
            Dictionary with training status information
        """
        if not PREDICTOR_AVAILABLE:
            return {"available": False, "error": "RecipePredictor not found"}

        recipes_with_porosity = self.recipe_repo.find_all_with_porosity()

        status = {
            "available": PREDICTOR_AVAILABLE,
            "trained": self.predictor is not None,
            "training_samples": len(recipes_with_porosity),
            "minimum_samples": 3,
            "sufficient_data": len(recipes_with_porosity) >= 3
        }

        if self.predictor and hasattr(self.predictor, 'feature_correlations'):
            status["features_analyzed"] = len(self.predictor.feature_correlations)

        return status

    def retrain_model(self) -> bool:
        """
        Retrain the prediction model with current recipe data.

        Returns:
            True if retraining successful, False otherwise
        """
        try:
            self._initialize_predictor()
            success = self.predictor is not None
            if success:
                logger.info("Prediction model retrained successfully")
            return success
        except Exception as e:
            logger.error(f"Failed to retrain model: {e}")
            return False

    def train_model(self, recipes: Optional[List[Recipe]] = None) -> Dict[str, Any]:
        """
        Train or retrain the prediction model.

        Args:
            recipes: Optional list of Recipe objects to train on

        Returns:
            Training status dictionary
        """
        if not PREDICTOR_AVAILABLE:
            return {"success": False, "error": "RecipePredictor not available"}

        try:
            if recipes:
                recipe_dicts = [
                    r.to_dict() if isinstance(r, Recipe) else r
                    for r in recipes
                ]
                self.predictor = RecipePredictor(recipe_dicts, use_advanced_ml=True)
            else:
                self._initialize_predictor()

            return {
                "success": self.predictor is not None,
                "trained": self.predictor is not None,
                "training_samples": len(recipes) if recipes else len(self.recipe_repo.find_all_with_porosity())
            }
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            return {"success": False, "error": str(e)}

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current prediction model.

        Returns:
            Dictionary with model information
        """
        info = {
            "available": PREDICTOR_AVAILABLE,
            "trained": self.predictor is not None
        }

        if self.predictor:
            info["features_analyzed"] = len(getattr(self.predictor, "feature_correlations", {}))
            info["use_advanced_ml"] = getattr(self.predictor, "use_advanced_ml", False)
            info["mean_porosity"] = getattr(self.predictor, "mean_porosity", None)

        return info

    def get_similar_recipes(self, recipe: Recipe, limit: int = 5) -> List[Tuple[Recipe, float]]:
        """
        Find recipes similar to the given recipe.

        Args:
            recipe: Recipe to find similar recipes for
            limit: Maximum number of similar recipes to return

        Returns:
            List of (recipe, similarity_score) tuples
        """
        all_recipes = self.recipe_repo.find_all()
        similar = []

        for other_recipe in all_recipes:
            if other_recipe.id == recipe.id:
                continue

            # Simple similarity based on hydration ratio
            recipe_hydration = recipe.get_hydration_ratio()
            other_hydration = other_recipe.get_hydration_ratio()

            if recipe_hydration and other_hydration:
                similarity = 1.0 - abs(recipe_hydration - other_hydration)
                if similarity > 0.7:  # Only include reasonably similar
                    similar.append((other_recipe, similarity))

        # Sort by similarity and return top matches
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:limit]
