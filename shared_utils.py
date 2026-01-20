"""
Shared Utilities Module
Centralized helper functions used across multiple modules to eliminate redundancy.
Contains: vessel encoding, statistical utilities, and common converters.
"""

from typing import Dict, Optional, List, Any
import numpy as np
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# VESSEL ENCODING (Consolidated from recipe_predictor.py and recipe_ml_advanced.py)
# ============================================================================

VESSEL_OPENNESS_MAP: Dict[str, float] = {
    """Map of cooking vessels to their 'openness' score (0=closed, 1=open)
    Used to determine steam retention and moisture loss during baking
    """
    "dutch oven": 0.3,      # Closed, traps steam, less airflow
    "loaf pan": 0.2,        # Enclosed, minimal airflow, most insulated
    "baking stone": 0.7,    # Open, good airflow, most moisture loss
    "banneton": 0.5,        # Semi-open (proofing basket)
    "bread cloche": 0.4,    # Covered, some airflow, similar to dutch oven
    "cloche": 0.35,         # Covered variant
    "covered": 0.35,        # Generic covered
    "oven": 0.6,            # Open oven (direct heat)
    "cast iron": 0.5,       # Medium openness (cast iron pot)
    "air fryer": 0.4,       # Forced convection, enclosed
}

DEFAULT_VESSEL_SCORE = 0.5  # Default for unknown vessels


def encode_vessel_openness(vessel: str) -> float:
    """
    Convert cooking vessel name to openness score (0-1).
    
    Args:
        vessel: Cooking vessel name (e.g., "dutch oven", "baking stone")
        
    Returns:
        float: Openness score between 0 (closed) and 1 (open)
        
    Examples:
        >>> encode_vessel_openness("dutch oven")
        0.3
        >>> encode_vessel_openness("baking stone")
        0.7
        >>> encode_vessel_openness("unknown vessel")
        0.5  # Default for unknown vessels
    """
    if not vessel or not isinstance(vessel, str):
        return DEFAULT_VESSEL_SCORE
    
    vessel_lower = vessel.lower().strip()
    
    # Exact match first
    if vessel_lower in VESSEL_OPENNESS_MAP:
        return VESSEL_OPENNESS_MAP[vessel_lower]
    
    # Partial match (check if key is contained in vessel name)
    for key, value in VESSEL_OPENNESS_MAP.items():
        if key in vessel_lower:
            return value
    
    # Default for unknown vessels
    return DEFAULT_VESSEL_SCORE


# ============================================================================
# STATISTICAL UTILITIES
# ============================================================================

def calculate_std_dev(values: List[float]) -> float:
    """
    Calculate standard deviation of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Standard deviation
    """
    if not values or len(values) < 2:
        return 0.0
    return float(np.std(values, ddof=1))


def calculate_variance(values: List[float]) -> float:
    """
    Calculate variance of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Variance
    """
    if not values or len(values) < 2:
        return 0.0
    return float(np.var(values, ddof=1))


def calculate_coefficient_of_variation(values: List[float]) -> float:
    """
    Calculate coefficient of variation (CV = std_dev / mean).
    Useful for comparing variability across different scales.
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Coefficient of variation (0-1 range typically)
    """
    if not values or len(values) < 2:
        return 0.0
    
    mean = np.mean(values)
    if mean == 0:
        return 0.0
    
    std_dev = calculate_std_dev(values)
    return float(std_dev / mean)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate the specified percentile of values.
    
    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        float: Value at the specified percentile
    """
    if not values:
        return 0.0
    return float(np.percentile(values, percentile))


def calculate_iqr(values: List[float]) -> float:
    """
    Calculate interquartile range (IQR = Q3 - Q1).
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Interquartile range
    """
    if not values or len(values) < 4:
        return 0.0
    
    q1 = calculate_percentile(values, 25)
    q3 = calculate_percentile(values, 75)
    return float(q3 - q1)


# ============================================================================
# RECIPE/INGREDIENT UTILITIES
# ============================================================================

def normalize_ingredient_name(ingredient: str) -> str:
    """
    Normalize ingredient name for consistent comparison.
    
    Args:
        ingredient: Raw ingredient name
        
    Returns:
        str: Normalized ingredient name (lowercase, stripped)
    """
    return ingredient.lower().strip() if ingredient else ""


def parse_json_safely(json_str: str, default: Optional[Dict] = None) -> Dict:
    """
    Safely parse JSON string with default fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        dict: Parsed JSON or default value
    """
    try:
        return json.loads(json_str) if json_str else (default or {})
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {json_str}")
        return default or {}


def ensure_file_path(path: str, create_parent: bool = True) -> Path:
    """
    Ensure file path is valid and parent directories exist if needed.
    
    Args:
        path: File path string
        create_parent: Whether to create parent directories
        
    Returns:
        Path: Pathlib Path object
    """
    file_path = Path(path)
    
    if create_parent:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    return file_path


def clamp_value(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Clamp value to specified range.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        float: Clamped value
    """
    return float(max(min_val, min(max_val, value)))


# ============================================================================
# BATCH PROCESSING UTILITIES
# ============================================================================

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of lists (chunks)
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """
    Flatten a list of lists into a single list.
    
    Args:
        nested_list: List of lists
        
    Returns:
        Flattened list
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_recipe_dict(recipe: Dict[str, Any]) -> bool:
    """
    Validate that recipe dictionary has required fields.
    
    Args:
        recipe: Recipe dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["ingredients", "instructions", "name"]
    
    if not isinstance(recipe, dict):
        return False
    
    return all(field in recipe for field in required_fields)


def validate_numeric_range(value: float, min_val: float, max_val: float) -> bool:
    """
    Validate that value is within specified range.
    
    Args:
        value: Value to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
        
    Returns:
        bool: True if value is in range, False otherwise
    """
    return min_val <= value <= max_val


if __name__ == "__main__":
    # Quick tests
    print("Testing vessel encoding:")
    print(f"Dutch oven: {encode_vessel_openness('dutch oven')}")
    print(f"Baking stone: {encode_vessel_openness('baking stone')}")
    print(f"Unknown: {encode_vessel_openness('unknown vessel')}")
    
    print("\nTesting statistics:")
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    print(f"Std dev: {calculate_std_dev(values)}")
    print(f"IQR: {calculate_iqr(values)}")
    
    print("\nAll utilities working correctly!")
