"""
Recipe Repository
Data access for recipes
"""

import json
from pathlib import Path
from typing import List, Optional
from models.recipe import Recipe
from utils.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


class RecipeRepository:
    """Manages persistence of Recipe domain objects"""
    
    def __init__(self, db_path: str = "recipes.json"):
        self.db_path = Path(db_path)
        self._recipes_cache: List[Recipe] = []
        self._load_from_file()
    
    def _load_from_file(self) -> None:
        """Load recipes from JSON file"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self._recipes_cache = [Recipe.from_dict(r) for r in data]
            else:
                self._recipes_cache = []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load recipes: {e}")
            self._recipes_cache = []
    
    def _save_to_file(self) -> None:
        """Save recipes to JSON file"""
        try:
            with open(self.db_path, 'w') as f:
                data = [r.to_dict() for r in self._recipes_cache]
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self._recipes_cache)} recipes to {self.db_path}")
        except IOError as e:
            logger.error(f"Failed to save recipes: {e}")
            raise DatabaseError(f"Failed to save recipes: {e}")
    
    def find_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Find recipe by ID"""
        for recipe in self._recipes_cache:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def find_all(self) -> List[Recipe]:
        """Get all recipes"""
        return self._recipes_cache.copy()
    
    def find_all_with_porosity(self) -> List[Recipe]:
        """Get all recipes that have measured porosity"""
        return [r for r in self._recipes_cache if r.measured_porosity is not None]
    
    def find_by_name(self, name: str) -> Optional[Recipe]:
        """Find recipe by name"""
        for recipe in self._recipes_cache:
            if recipe.name == name:
                return recipe
        return None
    
    def save(self, recipe: Recipe) -> Recipe:
        """
        Save a recipe (insert or update)
        
        Args:
            recipe: Recipe to save
        
        Returns:
            Saved recipe (with ID set)
        """
        # Assign ID if new
        if recipe.id is None:
            max_id = max([r.id for r in self._recipes_cache] or [0])
            recipe.id = max_id + 1
        
        # Check if updating existing
        existing_index = None
        for i, r in enumerate(self._recipes_cache):
            if r.id == recipe.id:
                existing_index = i
                break
        
        if existing_index is not None:
            self._recipes_cache[existing_index] = recipe
            logger.debug(f"Updated recipe {recipe.id}: {recipe.name}")
        else:
            self._recipes_cache.append(recipe)
            logger.debug(f"Created new recipe {recipe.id}: {recipe.name}")
        
        self._save_to_file()
        return recipe
    
    def delete(self, recipe_id: int) -> bool:
        """
        Delete a recipe by ID
        
        Returns:
            True if deleted, False if not found
        """
        original_len = len(self._recipes_cache)
        self._recipes_cache = [r for r in self._recipes_cache if r.id != recipe_id]
        
        if len(self._recipes_cache) < original_len:
            self._save_to_file()
            logger.debug(f"Deleted recipe {recipe_id}")
            return True
        
        return False
    
    def count(self) -> int:
        """Get total number of recipes"""
        return len(self._recipes_cache)
