"""
Recipe Database Management
Stores and manages bread recipes with their measured porosity outcomes
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class RecipeDatabase:
    """Manages storage and retrieval of bread recipes with porosity data"""
    
    def __init__(self, db_path: str = "recipes.json"):
        """
        Initialize recipe database
        
        Args:
            db_path: Path to JSON file storing recipes
        """
        self.db_path = Path(db_path)
        self.recipes = self._load_recipes()
    
    def _load_recipes(self) -> List[Dict]:
        """Load recipes from JSON file"""
        if not self.db_path.exists():
            return []
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_recipes(self):
        """Save recipes to JSON file"""
        with open(self.db_path, 'w') as f:
            json.dump(self.recipes, f, indent=2)
    
    def add_recipe(self, recipe_name: str, ingredients: Dict[str, float], 
                   mixing_time_min: float, proof_time_min: float, 
                   oven_temp_c: float, cooking_vessel: str, 
                   cook_time_min: float, measured_porosity: Optional[float] = None,
                   notes: str = "", room_temp_c: Optional[float] = None,
                   room_humidity_pct: Optional[float] = None, 
                   altitude_m: Optional[float] = None,
                   parent_recipe_id: Optional[int] = None,
                   steps: Optional[List[str]] = None,
                   bread_type: str = "other") -> Dict:
        """
        Add a new recipe to the database
        
        Args:
            recipe_name: Name of the bread recipe
            ingredients: Dict of ingredient names and amounts (e.g., {"flour": 500, "water": 350})
            mixing_time_min: Mixing time in minutes
            proof_time_min: Total proof time in minutes
            oven_temp_c: Oven temperature in Celsius
            cooking_vessel: Type of cooking vessel (e.g., "Dutch oven", "baking stone", "loaf pan")
            cook_time_min: Cooking time in minutes
            measured_porosity: Measured porosity percentage from analysis (optional)
            notes: Additional notes about the recipe
            room_temp_c: Ambient room temperature during fermentation (optional)
            room_humidity_pct: Ambient humidity during fermentation (optional)
            altitude_m: Altitude in meters (optional)
            parent_recipe_id: ID of parent recipe if this is a variant (optional)
        
        Returns:
            The created recipe dict
        """
        recipe = {
            "id": len(self.recipes) + 1,
            "name": recipe_name,
            "created_at": datetime.now().isoformat(),
            "ingredients": ingredients,
            "mixing_time_min": mixing_time_min,
            "proof_time_min": proof_time_min,
            "oven_temp_c": oven_temp_c,
            "cooking_vessel": cooking_vessel,
            "cook_time_min": cook_time_min,
            "measured_porosity": measured_porosity,
            "notes": notes,
            "room_temp_c": room_temp_c,
            "room_humidity_pct": room_humidity_pct,
            "altitude_m": altitude_m,
            "parent_recipe_id": parent_recipe_id,
            "version": 1,
            "quality_score": None,
            "steps": steps or [],
            "bread_type": bread_type
        }
        
        self.recipes.append(recipe)
        self._save_recipes()
        return recipe
    
    def update_recipe(self, recipe_id: int, measured_porosity: Optional[float] = None, 
                      notes: str = "", room_temp_c: Optional[float] = None,
                      room_humidity_pct: Optional[float] = None, 
                      altitude_m: Optional[float] = None) -> bool:
        """
        Update a recipe with measured porosity, notes, and environmental data
        
        Args:
            recipe_id: ID of the recipe to update
            measured_porosity: Measured porosity percentage from analysis
            notes: Additional notes
            room_temp_c: Ambient temperature in Celsius during fermentation
            room_humidity_pct: Ambient humidity percentage
            altitude_m: Altitude in meters where baking occurred
        
        Returns:
            True if successful, False if recipe not found
        """
        for recipe in self.recipes:
            if recipe["id"] == recipe_id:
                if measured_porosity is not None:
                    recipe["measured_porosity"] = measured_porosity
                if notes:
                    recipe["notes"] = notes
                if room_temp_c is not None:
                    recipe["room_temp_c"] = room_temp_c
                if room_humidity_pct is not None:
                    recipe["room_humidity_pct"] = room_humidity_pct
                if altitude_m is not None:
                    recipe["altitude_m"] = altitude_m
                recipe["porosity_measured_at"] = datetime.now().isoformat()
                self._save_recipes()
                return True
        return False
    
    def get_recipe(self, recipe_id: int) -> Optional[Dict]:
        """Get a specific recipe by ID"""
        for recipe in self.recipes:
            if recipe["id"] == recipe_id:
                return recipe
        return None
    
    def get_all_recipes(self) -> List[Dict]:
        """Get all recipes"""
        return self.recipes
    
    def get_recipes_with_porosity(self) -> List[Dict]:
        """Get only recipes that have measured porosity data"""
        return [r for r in self.recipes if r.get("measured_porosity") is not None]
    
    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe by ID"""
        for i, recipe in enumerate(self.recipes):
            if recipe["id"] == recipe_id:
                self.recipes.pop(i)
                self._save_recipes()
                return True
        return False
    
    def search_recipes(self, name_substring: str) -> List[Dict]:
        """Search recipes by name"""
        return [r for r in self.recipes if name_substring.lower() in r["name"].lower()]
    
    def get_recipe_summary(self, recipe_id: int) -> Optional[str]:
        """Get a human-readable summary of a recipe"""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None
        
        summary = f"""
RECIPE: {recipe['name']}
ID: {recipe['id']}
Created: {recipe['created_at']}

INGREDIENTS:
{self._format_ingredients(recipe['ingredients'])}

PROCESS:
  Mixing:        {recipe['mixing_time_min']:.0f} minutes
  Proofing:      {recipe['proof_time_min']:.0f} minutes
  Oven Temp:     {recipe['oven_temp_c']:.0f}°C
  Cooking Vessel: {recipe['cooking_vessel']}
  Cooking:       {recipe['cook_time_min']:.0f} minutes

RESULTS:
  Measured Porosity: {recipe.get('measured_porosity', 'Not measured')}
  Notes: {recipe.get('notes', 'None')}
"""
        return summary
    
    @staticmethod
    def _format_ingredients(ingredients: Dict[str, float]) -> str:
        """Format ingredients dict as readable string"""
        lines = []
        for ingredient, amount in ingredients.items():
            lines.append(f"  {ingredient}: {amount}")
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        all_recipes = self.recipes
        with_porosity = self.get_recipes_with_porosity()
        
        porosity_values = [r.get("measured_porosity") for r in with_porosity 
                          if r.get("measured_porosity") is not None]
        
        stats = {
            "total_recipes": len(all_recipes),
            "recipes_with_porosity": len(with_porosity),
            "avg_porosity": sum(porosity_values) / len(porosity_values) if porosity_values else None,
            "min_porosity": min(porosity_values) if porosity_values else None,
            "max_porosity": max(porosity_values) if porosity_values else None,
        }
        
        return stats
    
    def create_recipe_variant(self, parent_recipe_id: int, variant_name: str, 
                            modifications: Dict[str, any]) -> Optional[Dict]:
        """
        Create a variant of an existing recipe with tracked parent relationship
        
        Args:
            parent_recipe_id: ID of recipe to base variant on
            variant_name: Name for the variant
            modifications: Dict of fields to modify (e.g., {"mixing_time_min": 12})
        
        Returns:
            New recipe dict if successful, None if parent not found
        """
        parent = self.get_recipe(parent_recipe_id)
        if not parent:
            return None
        
        # Create new recipe based on parent
        variant = parent.copy()
        variant["id"] = len(self.recipes) + 1
        variant["name"] = variant_name
        variant["parent_recipe_id"] = parent_recipe_id
        variant["version"] = parent.get("version", 1) + 1
        variant["created_at"] = datetime.now().isoformat()
        
        # Apply modifications
        for field, value in modifications.items():
            if field in variant:
                variant[field] = value
        
        self.recipes.append(variant)
        self._save_recipes()
        return variant
    
    def get_recipe_variants(self, parent_recipe_id: int) -> List[Dict]:
        """Get all variants of a recipe"""
        return [r for r in self.recipes if r.get("parent_recipe_id") == parent_recipe_id]
    
    def get_recipe_family(self, recipe_id: int) -> Dict[str, any]:
        """Get recipe with all its variants and parent info"""
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return None
        
        return {
            "recipe": recipe,
            "parent": self.get_recipe(recipe.get("parent_recipe_id")) if recipe.get("parent_recipe_id") else None,
            "variants": self.get_recipe_variants(recipe_id)
        }
    
    def clone_recipe(self, recipe_id: int, clone_name: Optional[str] = None) -> Optional[Dict]:
        """
        Create an exact copy of a recipe with a new ID
        
        Args:
            recipe_id: ID of recipe to clone
            clone_name: Optional name for clone (defaults to "Recipe_name (Clone)")
        
        Returns:
            New cloned recipe dict if successful, None if recipe not found
        """
        original = self.get_recipe(recipe_id)
        if not original:
            return None
        
        # Create deep copy
        cloned = json.loads(json.dumps(original))
        cloned["id"] = len(self.recipes) + 1
        cloned["name"] = clone_name if clone_name else f"{original['name']} (Clone)"
        cloned["created_at"] = datetime.now().isoformat()
        cloned["parent_recipe_id"] = None  # Clone is independent
        cloned["version"] = 1  # Reset version to 1
        cloned["measured_porosity"] = None  # Reset porosity data
        cloned["porosity_measured_at"] = None  # Reset measurement timestamp
        
        self.recipes.append(cloned)
        self._save_recipes()
        return cloned
    
    def scale_recipe(self, recipe_id: int, scale_factor: float, 
                     scaled_name: Optional[str] = None) -> Optional[Dict]:
        """
        Scale all ingredients in a recipe by a given factor
        
        Args:
            recipe_id: ID of recipe to scale
            scale_factor: Factor to multiply ingredients by (e.g., 0.5 for half, 2.0 for double)
            scaled_name: Optional name for scaled recipe (defaults to "Recipe_name (scaled)")
        
        Returns:
            New scaled recipe dict if successful, None if recipe not found
        """
        if scale_factor <= 0:
            raise ValueError("Scale factor must be positive")
        
        original = self.get_recipe(recipe_id)
        if not original:
            return None
        
        # Create copy with scaled ingredients
        scaled = json.loads(json.dumps(original))
        scaled["id"] = len(self.recipes) + 1
        scaled["name"] = scaled_name if scaled_name else f"{original['name']} (×{scale_factor})"
        scaled["created_at"] = datetime.now().isoformat()
        scaled["parent_recipe_id"] = recipe_id  # Track original recipe
        scaled["version"] = 1
        scaled["measured_porosity"] = None
        scaled["porosity_measured_at"] = None
        
        # Scale all ingredients
        scaled_ingredients = {}
        for ingredient, amount in original.get("ingredients", {}).items():
            scaled_ingredients[ingredient] = round(float(amount) * scale_factor, 2)
        
        scaled["ingredients"] = scaled_ingredients
        
        # Note: Cooking times and temperatures generally don't scale
        # but we'll add a note about this
        if "notes" in scaled:
            scaled["notes"] = f"{scaled.get('notes', '')} [Scaled ×{scale_factor}]".strip()
        else:
            scaled["notes"] = f"[Scaled ×{scale_factor}]"
        
        self.recipes.append(scaled)
        self._save_recipes()
        return scaled

