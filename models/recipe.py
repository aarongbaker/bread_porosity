"""
Recipe Domain Model
Represents a bread recipe with all related properties
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Recipe:
    """Domain model for a bread recipe"""
    
    name: str
    ingredients: Dict[str, float]
    mixing_time_min: float
    proof_time_min: float
    oven_temp_c: float
    cooking_vessel: str
    cook_time_min: float
    
    # Optional fields
    measured_porosity: Optional[float] = None
    notes: str = ""
    room_temp_c: Optional[float] = None
    room_humidity_pct: Optional[float] = None
    altitude_m: Optional[float] = None
    parent_recipe_id: Optional[int] = None
    
    # Metadata
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    quality_score: Optional[float] = None
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate recipe data
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Recipe name cannot be empty")
        
        if not self.ingredients or len(self.ingredients) == 0:
            errors.append("Recipe must have at least one ingredient")
        
        for name, amount in self.ingredients.items():
            if not isinstance(amount, (int, float)) or amount < 0:
                errors.append(f"Ingredient '{name}' amount must be a non-negative number")
        
        if self.mixing_time_min < 0:
            errors.append("Mixing time cannot be negative")
        
        if self.proof_time_min < 0:
            errors.append("Proof time cannot be negative")
        
        if self.oven_temp_c <= 0:
            errors.append("Oven temperature must be positive")
        
        if self.cook_time_min <= 0:
            errors.append("Cook time must be positive")
        
        if not self.cooking_vessel or not self.cooking_vessel.strip():
            errors.append("Cooking vessel cannot be empty")
        
        if self.measured_porosity is not None:
            if not (0 <= self.measured_porosity <= 100):
                errors.append("Measured porosity must be between 0 and 100")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict:
        """Convert recipe to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Recipe':
        """Create recipe from dictionary"""
        return cls(**data)
    
    def get_total_time_hours(self) -> float:
        """Get total preparation and cooking time in hours"""
        total_minutes = self.mixing_time_min + self.proof_time_min + self.cook_time_min
        return total_minutes / 60
    
    def get_hydration_ratio(self) -> Optional[float]:
        """
        Calculate hydration ratio (water / flour)
        Returns None if flour or water not in ingredients
        """
        flour = self.ingredients.get("flour")
        water = self.ingredients.get("water")
        
        if flour and water:
            return water / flour
        
        return None
    
    def scale(self, factor: float) -> 'Recipe':
        """
        Create a scaled variant of this recipe
        
        Args:
            factor: Scale factor (e.g., 0.5 for half, 2.0 for double)
        
        Returns:
            New scaled Recipe object
        """
        scaled_ingredients = {
            name: amount * factor
            for name, amount in self.ingredients.items()
        }
        
        return Recipe(
            name=f"{self.name} (×{factor})",
            ingredients=scaled_ingredients,
            mixing_time_min=self.mixing_time_min,  # Times don't scale
            proof_time_min=self.proof_time_min,
            oven_temp_c=self.oven_temp_c,
            cooking_vessel=self.cooking_vessel,
            cook_time_min=self.cook_time_min,
            measured_porosity=self.measured_porosity,
            notes=f"{self.notes}\nScaled ×{factor} from recipe {self.name}",
            room_temp_c=self.room_temp_c,
            room_humidity_pct=self.room_humidity_pct,
            altitude_m=self.altitude_m,
            parent_recipe_id=self.id,
            version=1
        )
