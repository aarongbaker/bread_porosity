"""
Recipe Controller
Handles recipe management operations and coordinates with RecipeService
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any, Callable, List
import json

from services.recipe_service import RecipeService
from models.recipe import Recipe
from utils.logger import get_logger

logger = get_logger(__name__)


class RecipeController:
    """Controller for recipe management operations"""

    def __init__(self, recipe_service: RecipeService, view_callback: Optional[Callable] = None):
        """
        Initialize recipe controller

        Args:
            recipe_service: The recipe service to use
            view_callback: Callback to update the view (optional)
        """
        self.recipe_service = recipe_service
        self.view_callback = view_callback
        self.current_recipe: Optional[Recipe] = None
        self.current_recipe_id: Optional[int] = None

    def create_recipe(self, recipe_data: Dict[str, Any]) -> Optional[Recipe]:
        """
        Create a new recipe

        Args:
            recipe_data: Recipe data dictionary

        Returns:
            Created Recipe if successful, None if failed
        """
        try:
            recipe = self.recipe_service.create_recipe(recipe_data)
            logger.info(f"Recipe created: {recipe.name} (ID: {recipe.id})")

            if self.view_callback:
                self.view_callback('recipe_created', recipe)

            return recipe

        except Exception as e:
            error_msg = f"Failed to create recipe: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        Get a recipe by ID

        Args:
            recipe_id: Recipe ID

        Returns:
            Recipe if found, None otherwise
        """
        try:
            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return None

            recipe = self.recipe_service.get_recipe(recipe_id_int)
            if recipe:
                self.current_recipe = recipe
                self.current_recipe_id = recipe_id_int
            return recipe

        except Exception as e:
            logger.error(f"Failed to get recipe {recipe_id}: {e}")
            return None

    def update_recipe_porosity(self, recipe_id: str, porosity: float) -> bool:
        """
        Update measured porosity for a recipe

        Args:
            recipe_id: Recipe ID
            porosity: Measured porosity percentage

        Returns:
            True if successful, False otherwise
        """
        try:
            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return False

            success = self.recipe_service.update_recipe_porosity(recipe_id_int, porosity)
            if success:
                logger.info(f"Updated porosity for recipe {recipe_id_int}: {porosity:.1f}%")

                if self.view_callback:
                    self.view_callback('porosity_updated', recipe_id_int, porosity)

            return success

        except Exception as e:
            logger.error(f"Failed to update porosity for recipe {recipe_id}: {e}")
            return False

    def create_variant(self, parent_recipe_id: str, scale_factor: float,
                      name_suffix: str = "") -> Optional[Recipe]:
        """
        Create a recipe variant

        Args:
            parent_recipe_id: Parent recipe ID
            scale_factor: Scaling factor for ingredients
            name_suffix: Optional suffix for the variant name

        Returns:
            Created variant Recipe if successful, None if failed
        """
        try:
            parent_recipe_id_int = self._coerce_recipe_id(parent_recipe_id)
            if parent_recipe_id_int is None:
                return None

            variant = self.recipe_service.create_variant(
                parent_recipe_id=parent_recipe_id_int,
                scale_factor=scale_factor,
                name_suffix=name_suffix
            )

            if variant:
                logger.info(f"Variant created: {variant.name} (parent: {parent_recipe_id_int})")

                if self.view_callback:
                    self.view_callback('variant_created', variant)

            return variant

        except Exception as e:
            error_msg = f"Failed to create variant: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def clone_recipe(self, recipe_id: str, new_name: str) -> Optional[Recipe]:
        """
        Clone a recipe with a new name

        Args:
            recipe_id: Recipe ID to clone
            new_name: New name for the cloned recipe

        Returns:
            Cloned Recipe if successful, None if failed
        """
        try:
            # Get the original recipe
            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return None

            original = self.recipe_service.get_recipe(recipe_id_int)
            if not original:
                return None

            # Create clone data
            clone_data = original.to_dict()
            clone_data['name'] = new_name
            clone_data.pop('id', None)  # Remove ID so it gets a new one
            clone_data.pop('created_at', None)  # Remove timestamp

            # Create the clone
            clone = self.recipe_service.create_recipe(clone_data)
            if clone:
                logger.info(f"Recipe cloned: {original.name} -> {clone.name}")

                if self.view_callback:
                    self.view_callback('recipe_cloned', clone)

            return clone

        except Exception as e:
            error_msg = f"Failed to clone recipe: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def scale_recipe(self, recipe_id: str, scale_factor: float) -> Optional[Recipe]:
        """
        Scale a recipe by a factor

        Args:
            recipe_id: Recipe ID to scale
            scale_factor: Scaling factor (e.g., 2.0 for double batch)

        Returns:
            Scaled Recipe if successful, None if failed
        """
        try:
            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return None

            scaled = self.recipe_service.scale_recipe(recipe_id_int, scale_factor)
            if scaled:
                logger.info(f"Recipe scaled: {recipe_id_int} by factor {scale_factor}")

                if self.view_callback:
                    self.view_callback('recipe_scaled', scaled)

            return scaled

        except Exception as e:
            error_msg = f"Failed to scale recipe: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def delete_recipe(self, recipe_id: str) -> bool:
        """
        Delete a recipe

        Args:
            recipe_id: Recipe ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Confirm deletion
            if not self._confirm_deletion(recipe_id):
                return False

            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return False

            success = self.recipe_service.delete_recipe(recipe_id_int)
            if success:
                logger.info(f"Recipe deleted: {recipe_id_int}")

                if self.view_callback:
                    self.view_callback('recipe_deleted', recipe_id_int)

                # Clear current recipe if it was deleted
                if self.current_recipe_id == recipe_id_int:
                    self.current_recipe = None
                    self.current_recipe_id = None

            return success

        except Exception as e:
            error_msg = f"Failed to delete recipe {recipe_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False

    def get_all_recipes(self) -> List[Recipe]:
        """
        Get all recipes

        Returns:
            List of all recipes
        """
        try:
            return self.recipe_service.get_all_recipes()
        except Exception as e:
            logger.error(f"Failed to get all recipes: {e}")
            return []

    def predict_porosity(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Predict porosity for a recipe

        Args:
            recipe_id: Recipe ID

        Returns:
            Prediction results if successful, None otherwise
        """
        try:
            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return None

            recipe = self.recipe_service.get_recipe(recipe_id_int)
            if not recipe:
                return None

            prediction = self.recipe_service.predict_porosity(recipe)
            if prediction:
                logger.info(
                    f"Porosity predicted for recipe {recipe_id_int}: "
                    f"{prediction.get('predicted_porosity', 'N/A')}%"
                )

                if self.view_callback:
                    self.view_callback('porosity_predicted', recipe_id_int, prediction)

            return prediction

        except Exception as e:
            logger.error(f"Failed to predict porosity for recipe {recipe_id}: {e}")
            return None

    def get_recipe_family(self, recipe_id: str) -> List[Recipe]:
        """
        Get the family tree for a recipe (variants and parent)

        Args:
            recipe_id: Recipe ID

        Returns:
            List of related recipes in the family
        """
        try:
            recipe_id_int = self._coerce_recipe_id(recipe_id)
            if recipe_id_int is None:
                return []

            return self.recipe_service.get_recipe_family(recipe_id_int)
        except Exception as e:
            logger.error(f"Failed to get recipe family for {recipe_id}: {e}")
            return []

    def _confirm_deletion(self, recipe_id: str) -> bool:
        """
        Confirm recipe deletion with user

        Args:
            recipe_id: Recipe ID

        Returns:
            True if user confirms deletion
        """
        recipe_id_int = self._coerce_recipe_id(recipe_id)
        if recipe_id_int is None:
            return False

        recipe = self.recipe_service.get_recipe(recipe_id_int)
        if not recipe:
            return False

        # Check if recipe has variants
        family = self.recipe_service.get_recipe_family(recipe_id_int)
        has_variants = len(family) > 1

        message = f"Are you sure you want to delete recipe '{recipe.name}'?"
        if has_variants:
            message += f"\n\nWarning: This recipe has {len(family)-1} variant(s) that will also be affected."

        return messagebox.askyesno("Confirm Deletion", message)

    def set_current_recipe(self, recipe_id: Optional[str]) -> None:
        """
        Set the current active recipe

        Args:
            recipe_id: Recipe ID or None to clear
        """
        if recipe_id:
            recipe = self.get_recipe(recipe_id)
            if recipe:
                self.current_recipe = recipe
                self.current_recipe_id = recipe.id
        else:
            self.current_recipe = None
            self.current_recipe_id = None

    def get_current_recipe(self) -> Optional[Recipe]:
        """Get the current active recipe"""
        return self.current_recipe

    def get_current_recipe_id(self) -> Optional[int]:
        """Get the current active recipe ID"""
        return self.current_recipe_id

    def _coerce_recipe_id(self, recipe_id: Optional[str]) -> Optional[int]:
        """Convert recipe IDs from UI input to integers."""
        try:
            return int(recipe_id) if recipe_id is not None else None
        except (TypeError, ValueError):
            logger.error(f"Invalid recipe ID: {recipe_id}")
            return None
