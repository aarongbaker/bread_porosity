"""
Recipe Service
Business logic for recipe management and operations
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

from models.recipe import Recipe
from repositories.recipe_repository import RecipeRepository
from utils.exceptions import RecipeError, ValidationError
from utils.logger import get_logger
from utils.validators import Validator
from services.prediction_service import PredictionService

logger = get_logger(__name__)


class RecipeService:
    """
    Service for managing bread recipes.

    Provides business logic for:
    - Recipe CRUD operations
    - Recipe validation
    - Variant creation
    - Recipe analysis and comparison
    """

    def __init__(self,
                 recipe_repo: Optional[RecipeRepository] = None,
                 prediction_service: Optional[PredictionService] = None):
        """
        Initialize the recipe service.

        Args:
            recipe_repo: Repository for recipe persistence (optional)
            prediction_service: Optional prediction service instance
        """
        self.recipe_repo = recipe_repo or RecipeRepository()
        self.prediction_service = prediction_service

    def create_recipe(self, recipe_data: Dict[str, Any]) -> Recipe:
        """
        Create a new recipe.

        Args:
            recipe_data: Dictionary with recipe information

        Returns:
            Created Recipe object

        Raises:
            ValidationError: If recipe data is invalid
            RecipeError: If creation fails
        """
        try:
            # Validate input
            is_valid, errors = Validator.validate_recipe_dict(recipe_data)
            if not is_valid:
                raise ValidationError(f"Invalid recipe data: {', '.join(errors)}")

            # Create Recipe object
            recipe = Recipe(
                name=recipe_data["name"],
                ingredients=recipe_data["ingredients"],
                mixing_time_min=recipe_data["mixing_time_min"],
                proof_time_min=recipe_data["proof_time_min"],
                oven_temp_c=recipe_data["oven_temp_c"],
                cooking_vessel=recipe_data["cooking_vessel"],
                cook_time_min=recipe_data["cook_time_min"],
                measured_porosity=recipe_data.get("measured_porosity"),
                notes=recipe_data.get("notes", ""),
                room_temp_c=recipe_data.get("room_temp_c"),
                room_humidity_pct=recipe_data.get("room_humidity_pct"),
                altitude_m=recipe_data.get("altitude_m"),
                parent_recipe_id=recipe_data.get("parent_recipe_id")
            )

            # Validate the recipe object
            is_valid, errors = recipe.validate()
            if not is_valid:
                raise ValidationError(f"Recipe validation failed: {', '.join(errors)}")

            # Save to repository
            saved_recipe = self.recipe_repo.save(recipe)

            logger.info(f"Created recipe: {saved_recipe.name} (ID: {saved_recipe.id})")
            return saved_recipe

        except Exception as e:
            logger.error(f"Failed to create recipe: {e}")
            raise RecipeError(f"Failed to create recipe: {e}") from e

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        """
        Get a recipe by ID.

        Args:
            recipe_id: Recipe ID

        Returns:
            Recipe object or None if not found
        """
        return self.recipe_repo.find_by_id(recipe_id)

    def get_all_recipes(self) -> List[Recipe]:
        """
        Get all recipes.

        Returns:
            List of all recipes
        """
        return self.recipe_repo.find_all()

    def update_recipe_porosity(self, recipe_id: int, measured_porosity: float) -> bool:
        """
        Update a recipe with measured porosity data.

        Args:
            recipe_id: Recipe ID
            measured_porosity: Measured porosity percentage

        Returns:
            True if updated, False if recipe not found

        Raises:
            ValidationError: If porosity value is invalid
        """
        if not (0 <= measured_porosity <= 100):
            raise ValidationError("Porosity must be between 0 and 100")

        recipe = self.recipe_repo.find_by_id(recipe_id)
        if not recipe:
            return False

        recipe.measured_porosity = measured_porosity
        self.recipe_repo.save(recipe)

        logger.info(f"Updated porosity for recipe {recipe_id}: {measured_porosity:.2f}%")
        return True

    def create_variant(self, parent_recipe_id: int, scale_factor: float, name_suffix: str = "") -> Recipe:
        """
        Create a scaled variant of an existing recipe.

        Args:
            parent_recipe_id: ID of the parent recipe
            scale_factor: Scaling factor (e.g., 0.5 for half, 2.0 for double)
            name_suffix: Optional suffix for the variant name

        Returns:
            New Recipe object (variant)

        Raises:
            RecipeError: If parent recipe not found or scaling fails
        """
        parent_recipe = self.recipe_repo.find_by_id(parent_recipe_id)
        if not parent_recipe:
            raise RecipeError(f"Parent recipe {parent_recipe_id} not found")

        try:
            # Create scaled variant
            variant = parent_recipe.scale(scale_factor)

            # Update name if suffix provided
            if name_suffix:
                variant.name = f"{parent_recipe.name} {name_suffix}"
            elif scale_factor != 1.0:
                variant.name = f"{parent_recipe.name} (×{scale_factor})"

            # Set parent relationship
            variant.parent_recipe_id = parent_recipe.id

            # Save the variant
            saved_variant = self.recipe_repo.save(variant)

            logger.info(f"Created recipe variant: {saved_variant.name} (ID: {saved_variant.id}) from {parent_recipe.name}")
            return saved_variant

        except Exception as e:
            logger.error(f"Failed to create recipe variant: {e}")
            raise RecipeError(f"Failed to create recipe variant: {e}") from e

    def scale_recipe(self, recipe_id: int, scale_factor: float, name_suffix: str = "") -> Recipe:
        """
        Scale a recipe and save it as a new variant.

        Args:
            recipe_id: ID of the recipe to scale
            scale_factor: Scaling factor (e.g., 0.5 for half, 2.0 for double)
            name_suffix: Optional suffix for the variant name

        Returns:
            New scaled Recipe object
        """
        if scale_factor <= 0:
            raise ValidationError("Scale factor must be greater than 0")

        return self.create_variant(recipe_id, scale_factor, name_suffix)

    def predict_porosity(self, recipe: Recipe) -> Dict[str, Any]:
        """
        Predict porosity for a recipe using the prediction service.

        Args:
            recipe: Recipe object to predict for

        Returns:
            Prediction result dictionary
        """
        try:
            if not self.prediction_service:
                self.prediction_service = PredictionService(self.recipe_repo)

            prediction = self.prediction_service.predict_porosity(recipe)
            return prediction.to_dict()

        except Exception as e:
            logger.error(f"Failed to predict porosity for recipe {recipe.name}: {e}")
            raise RecipeError(f"Failed to predict porosity for recipe {recipe.name}: {e}") from e

    def delete_recipe(self, recipe_id: int) -> bool:
        """
        Delete a recipe.

        Args:
            recipe_id: Recipe ID to delete

        Returns:
            True if deleted, False if not found
        """
        deleted = self.recipe_repo.delete(recipe_id)
        if deleted:
            logger.info(f"Deleted recipe {recipe_id}")
        return deleted

    def get_recipes_with_porosity_data(self) -> List[Recipe]:
        """
        Get all recipes that have measured porosity data.

        Returns:
            List of recipes with porosity measurements
        """
        return self.recipe_repo.find_all_with_porosity()

    def get_recipe_family(self, recipe_id: int) -> List[Recipe]:
        """
        Get all recipes in the same family (parent and variants).

        Args:
            recipe_id: Recipe ID to start from

        Returns:
            List of related recipes
        """
        recipe = self.recipe_repo.find_by_id(recipe_id)
        if not recipe:
            return []

        family = [recipe]

        # Find parent if this is a variant
        if recipe.parent_recipe_id:
            parent = self.recipe_repo.find_by_id(recipe.parent_recipe_id)
            if parent:
                family.append(parent)

        # Find all variants of this recipe or its parent
        root_id = recipe.parent_recipe_id or recipe.id
        all_recipes = self.recipe_repo.find_all()

        for r in all_recipes:
            if r.parent_recipe_id == root_id and r.id != recipe.id:
                family.append(r)

        return family

    def compare_recipes(self, recipe_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple recipes.

        Args:
            recipe_ids: List of recipe IDs to compare

        Returns:
            Dictionary with comparison data
        """
        recipes = []
        for recipe_id in recipe_ids:
            recipe = self.recipe_repo.find_by_id(recipe_id)
            if recipe:
                recipes.append(recipe)

        if not recipes:
            return {"error": "No valid recipes found"}

        comparison = {
            "recipes": [r.to_dict() for r in recipes],
            "summary": {
                "count": len(recipes),
                "with_porosity": sum(1 for r in recipes if r.measured_porosity is not None),
                "avg_porosity": None,
                "porosity_range": None
            }
        }

        # Calculate porosity statistics
        porosities = [r.measured_porosity for r in recipes if r.measured_porosity is not None]
        if porosities:
            comparison["summary"]["avg_porosity"] = sum(porosities) / len(porosities)
            comparison["summary"]["porosity_range"] = {
                "min": min(porosities),
                "max": max(porosities)
            }

        return comparison
