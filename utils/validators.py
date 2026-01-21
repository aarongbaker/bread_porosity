"""
Validators
Input validation and data checking
"""

from typing import List, Tuple, Dict, Any
import re


class Validator:
    """Collection of validation methods"""
    
    @staticmethod
    def validate_recipe_dict(recipe_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate recipe dictionary
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not recipe_dict.get("name"):
            errors.append("Recipe must have a name")
        
        if not recipe_dict.get("ingredients") or not isinstance(recipe_dict["ingredients"], dict):
            errors.append("Recipe must have ingredients dict")
        
        mixing_time = recipe_dict.get("mixing_time_min")
        if mixing_time is not None and (not isinstance(mixing_time, (int, float)) or mixing_time < 0):
            errors.append("Mixing time must be a positive number")
        
        proof_time = recipe_dict.get("proof_time_min")
        if proof_time is not None and (not isinstance(proof_time, (int, float)) or proof_time < 0):
            errors.append("Proof time must be a positive number")
        
        oven_temp = recipe_dict.get("oven_temp_c")
        if oven_temp is not None and (not isinstance(oven_temp, (int, float)) or oven_temp < 0):
            errors.append("Oven temperature must be a positive number")
        
        cook_time = recipe_dict.get("cook_time_min")
        if cook_time is not None and (not isinstance(cook_time, (int, float)) or cook_time < 0):
            errors.append("Cook time must be a positive number")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_pixel_size(pixel_size: float) -> Tuple[bool, str]:
        """
        Validate pixel size parameter
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(pixel_size, (int, float)):
            return False, "Pixel size must be a number"
        
        if pixel_size <= 0:
            return False, "Pixel size must be positive"
        
        if pixel_size > 1.0:
            return False, "Pixel size seems too large (>1.0mm)"
        
        if pixel_size < 0.01:
            return False, "Pixel size seems too small (<0.01mm)"
        
        return True, ""
    
    @staticmethod
    def validate_image_path(path: str) -> Tuple[bool, str]:
        """
        Validate image file path
        
        Returns:
            (is_valid, error_message)
        """
        from pathlib import Path
        
        p = Path(path)
        
        if not p.exists():
            return False, f"File does not exist: {path}"
        
        if not p.is_file():
            return False, f"Path is not a file: {path}"
        
        suffix = p.suffix.lower()
        if suffix not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return False, f"Unsupported image format: {suffix}"
        
        return True, ""
    
    @staticmethod
    def validate_threshold_method(method: str) -> Tuple[bool, str]:
        """
        Validate threshold method
        
        Returns:
            (is_valid, error_message)
        """
        valid_methods = ['otsu', 'adaptive']
        
        if method not in valid_methods:
            return False, f"Invalid threshold method. Must be one of: {', '.join(valid_methods)}"
        
        return True, ""
    
    @staticmethod
    def validate_normalize_method(method: str) -> Tuple[bool, str]:
        """
        Validate normalization method
        
        Returns:
            (is_valid, error_message)
        """
        valid_methods = ['clahe', 'morphology', 'gaussian']
        
        if method not in valid_methods:
            return False, f"Invalid normalization method. Must be one of: {', '.join(valid_methods)}"
        
        return True, ""
