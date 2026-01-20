"""
Advanced ML Module for Bread Porosity Prediction
Analyzes recipes, ingredients, and instructions to predict porosity
Uses Random Forest, feature engineering, and cross-validation
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

# scikit-learn for ML
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle

try:
    from .shared_utils import encode_vessel_openness
except (ImportError, ValueError):
    from shared_utils import encode_vessel_openness

logger = logging.getLogger(__name__)


@dataclass
class RecipeFeatures:
    """Extracted and engineered features from a recipe"""
    # Hydration & Water Science
    hydration_ratio: float
    baker_percentage: float
    
    # Fermentation & Time
    total_fermentation_hours: float
    bulk_fermentation_ratio: float  # proof_time / mixing_time
    fermentation_temperature_factor: float
    
    # Ingredients Composition
    gluten_development_score: float
    hydrophilic_score: float  # Water-binding capacity
    enzymatic_activity_score: float  # Fermentation potential
    salt_percentage: float
    starter_percentage: float
    sugar_percentage: float
    fat_percentage: float
    whole_grain_percentage: float
    
    # Process Parameters
    mixing_intensity: float
    oven_temperature_norm: float
    cooking_vessel_openness: float
    total_cook_time_min: float
    
    # Derived Features
    dough_extensibility: float
    fermentation_power: float
    crumb_potential_score: float


class IngredientAnalyzer:
    """Analyzes ingredients for their contribution to bread porosity"""
    
    # Ingredient database with properties
    INGREDIENT_DATABASE = {
        # Flours
        "bread flour": {"gluten": 0.95, "water_absorption": 0.65, "fermentation": 0.7, "category": "flour"},
        "all-purpose flour": {"gluten": 0.80, "water_absorption": 0.60, "fermentation": 0.6, "category": "flour"},
        "whole wheat": {"gluten": 0.70, "water_absorption": 0.75, "fermentation": 0.8, "category": "flour"},
        "rye": {"gluten": 0.50, "water_absorption": 0.80, "fermentation": 0.9, "category": "flour"},
        "spelt": {"gluten": 0.75, "water_absorption": 0.70, "fermentation": 0.65, "category": "flour"},
        "einkorn": {"gluten": 0.60, "water_absorption": 0.68, "fermentation": 0.7, "category": "flour"},
        "ancient grain": {"gluten": 0.65, "water_absorption": 0.72, "fermentation": 0.75, "category": "flour"},
        "pastry flour": {"gluten": 0.65, "water_absorption": 0.55, "fermentation": 0.5, "category": "flour"},
        "cake flour": {"gluten": 0.50, "water_absorption": 0.50, "fermentation": 0.45, "category": "flour"},
        
        # Starters & Leavening
        "sourdough starter": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 1.0, "category": "leaven"},
        "yeast": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.9, "category": "leaven"},
        "commercial yeast": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.85, "category": "leaven"},
        "bakers yeast": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.85, "category": "leaven"},
        "wild yeast": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.8, "category": "leaven"},
        "levain": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.95, "category": "leaven"},
        "preferment": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.85, "category": "leaven"},
        
        # Salts
        "salt": {"gluten": 0.0, "water_absorption": 0.1, "fermentation": -0.3, "category": "salt"},
        "sea salt": {"gluten": 0.0, "water_absorption": 0.1, "fermentation": -0.3, "category": "salt"},
        
        # Fats & Oils
        "butter": {"gluten": 0.0, "water_absorption": 0.05, "fermentation": -0.2, "category": "fat"},
        "oil": {"gluten": 0.0, "water_absorption": 0.02, "fermentation": -0.1, "category": "fat"},
        "olive oil": {"gluten": 0.0, "water_absorption": 0.02, "fermentation": -0.1, "category": "fat"},
        "vegetable oil": {"gluten": 0.0, "water_absorption": 0.02, "fermentation": -0.1, "category": "fat"},
        
        # Sweeteners
        "sugar": {"gluten": 0.0, "water_absorption": 0.2, "fermentation": 0.5, "category": "sugar"},
        "honey": {"gluten": 0.0, "water_absorption": 0.3, "fermentation": 0.6, "category": "sugar"},
        "malt": {"gluten": 0.0, "water_absorption": 0.25, "fermentation": 0.7, "category": "sugar"},
        "diastatic malt": {"gluten": 0.0, "water_absorption": 0.25, "fermentation": 0.85, "category": "sugar"},
        
        # Hydrocolloids & Additives
        "vital wheat gluten": {"gluten": 1.0, "water_absorption": 0.3, "fermentation": 0.4, "category": "additive"},
        "ascorbic acid": {"gluten": 0.0, "water_absorption": 0.0, "fermentation": 0.3, "category": "additive"},
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def normalize_ingredient_name(self, name: str) -> str:
        """Normalize ingredient name for lookup"""
        return name.lower().strip()
    
    def get_ingredient_properties(self, ingredient_name: str) -> Dict[str, float]:
        """
        Get properties for an ingredient
        
        Returns dict with gluten, water_absorption, fermentation scores
        """
        normalized = self.normalize_ingredient_name(ingredient_name)
        
        # Exact match
        if normalized in self.INGREDIENT_DATABASE:
            return self.INGREDIENT_DATABASE[normalized].copy()
        
        # Partial match
        for db_name, props in self.INGREDIENT_DATABASE.items():
            if db_name in normalized or normalized in db_name:
                return props.copy()
        
        # Default for unknown ingredients
        if self.verbose:
            print(f"Warning: Unknown ingredient '{ingredient_name}', using neutral defaults")
        return {
            "gluten": 0.5,
            "water_absorption": 0.5,
            "fermentation": 0.5
        }
    
    def analyze_ingredients(self, ingredients: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze ingredient composition
        
        Args:
            ingredients: Dict of ingredient names and amounts (e.g., {"flour": 500, "water": 350})
        
        Returns:
            Analysis with scores and percentages
        """
        total_weight = sum(ingredients.values()) if ingredients else 1
        
        analysis = {
            "total_weight": total_weight,
            "ingredients_detail": {},
            "category_totals": {},
            "gluten_development_score": 0.0,
            "hydrophilic_score": 0.0,
            "enzymatic_activity_score": 0.0,
            "hydration_ratio": 0.0,
        }
        
        flour_weight = 0
        water_weight = 0
        salt_weight = 0
        sugar_weight = 0
        fat_weight = 0
        starter_weight = 0
        
        # Analyze each ingredient
        for ingredient_name, amount in ingredients.items():
            if amount <= 0:
                continue
            
            props = self.get_ingredient_properties(ingredient_name)
            category = props.get("category", "unknown")
            pct = amount / total_weight
            
            analysis["ingredients_detail"][ingredient_name] = {
                "amount": amount,
                "percentage": pct,
                "gluten": props["gluten"],
                "water_absorption": props["water_absorption"],
                "fermentation": props["fermentation"],
                "category": category
            }
            
            # Aggregate by category
            if category not in analysis["category_totals"]:
                analysis["category_totals"][category] = 0
            analysis["category_totals"][category] += pct
            
            # Accumulate weighted scores
            analysis["gluten_development_score"] += props["gluten"] * pct
            analysis["hydrophilic_score"] += props["water_absorption"] * pct
            analysis["enzymatic_activity_score"] += props["fermentation"] * pct
            
            # Track specific ingredients
            if category == "flour":
                flour_weight += amount
            elif ingredient_name.lower() in ["water", "aqua"]:
                water_weight += amount
            elif category == "salt":
                salt_weight += amount
            elif category == "sugar":
                sugar_weight += amount
            elif category == "fat":
                fat_weight += amount
            elif category == "leaven":
                starter_weight += amount
        
        # Calculate ratios
        if flour_weight > 0:
            analysis["hydration_ratio"] = water_weight / flour_weight
            analysis["salt_percentage"] = (salt_weight / flour_weight) * 100
            analysis["sugar_percentage"] = (sugar_weight / flour_weight) * 100
            analysis["fat_percentage"] = (fat_weight / flour_weight) * 100
            analysis["starter_percentage"] = (starter_weight / flour_weight) * 100
        else:
            analysis["hydration_ratio"] = 0.0
            analysis["salt_percentage"] = 0.0
            analysis["sugar_percentage"] = 0.0
            analysis["fat_percentage"] = 0.0
            analysis["starter_percentage"] = 0.0
        
        analysis["flour_weight"] = flour_weight
        analysis["water_weight"] = water_weight
        
        return analysis


class InstructionAnalyzer:
    """Analyzes baking instructions for process factors affecting porosity"""
    
    # Keywords for instruction analysis
    FERMENTATION_KEYWORDS = {
        "bulk ferment": 1.0, "bulk fermentation": 1.0,
        "first rise": 0.8, "bulk rise": 0.9,
        "overnight": 0.9, "cold ferment": 0.8,
        "room temperature": 0.7, "ambient": 0.6,
        "proof": 0.7, "proofing": 0.7,
        "rise": 0.6, "rising": 0.6,
    }
    
    MIXING_KEYWORDS = {
        "knead": 0.7, "kneading": 0.7,
        "massage": 0.6, "rubaud": 0.5,
        "autolyse": 0.4, "rest": 0.3,
        "fold": 0.5, "folding": 0.5, "coil fold": 0.6,
        "stretch and fold": 0.7,
        "slap and fold": 0.8,
        "high-speed": 0.9, "machine": 0.8,
    }
    
    TEMPERATURE_KEYWORDS = {
        "warm": 0.7, "cool": 0.4,
        "cold": 0.3, "room temperature": 0.6,
        "warm water": 0.75, "cool water": 0.35,
        "ambient": 0.6,
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def analyze_instructions(self, instructions_text: Optional[str]) -> Dict[str, Any]:
        """
        Analyze baking instructions for porosity-affecting factors
        
        Args:
            instructions_text: Text description of baking process
        
        Returns:
            Analysis with scores for mixing, fermentation, temperature factors
        """
        analysis = {
            "mixing_intensity": 0.5,
            "fermentation_temperature_factor": 0.6,
            "process_complexity": 0.0,
            "has_autolyse": False,
            "has_bulk_ferment": False,
            "has_cold_ferment": False,
            "has_stretch_fold": False,
            "fermentation_steps": [],
        }
        
        if not instructions_text:
            return analysis
        
        text_lower = instructions_text.lower()
        
        # Detect fermentation techniques
        for keyword, score in self.FERMENTATION_KEYWORDS.items():
            if keyword in text_lower:
                analysis["fermentation_temperature_factor"] += score * 0.15
                if "bulk" in keyword:
                    analysis["has_bulk_ferment"] = True
                if "cold" in keyword or "overnight" in keyword:
                    analysis["has_cold_ferment"] = True
                analysis["fermentation_steps"].append(keyword)
        
        # Detect mixing techniques
        for keyword, score in self.MIXING_KEYWORDS.items():
            if keyword in text_lower:
                analysis["mixing_intensity"] += score * 0.15
                if "autolyse" in keyword:
                    analysis["has_autolyse"] = True
                if "stretch and fold" in keyword or "coil fold" in keyword:
                    analysis["has_stretch_fold"] = True
        
        # Detect temperature preferences
        temp_factor = 0.6
        for keyword, score in self.TEMPERATURE_KEYWORDS.items():
            if keyword in text_lower:
                temp_factor = max(0.3, min(0.9, score))
        analysis["fermentation_temperature_factor"] = temp_factor
        
        # Complexity scoring
        step_count = len([s for s in text_lower.split('\n') if s.strip()])
        analysis["process_complexity"] = min(1.0, step_count / 10)
        
        # Clamp scores to 0-1
        analysis["mixing_intensity"] = min(1.0, analysis["mixing_intensity"])
        analysis["fermentation_temperature_factor"] = min(1.0, analysis["fermentation_temperature_factor"])
        
        return analysis


class RecipeFeatureEngineer:
    """Engineers features from recipes for ML prediction"""
    
    def __init__(self):
        self.ingredient_analyzer = IngredientAnalyzer()
        self.instruction_analyzer = InstructionAnalyzer()
    
    def engineer_features(self, recipe: Dict[str, Any]) -> RecipeFeatures:
        """
        Extract and engineer features from a recipe
        
        Args:
            recipe: Recipe dictionary
        
        Returns:
            RecipeFeatures dataclass
        """
        # Analyze ingredients
        ingredients = recipe.get("ingredients", {})
        ingredient_analysis = self.ingredient_analyzer.analyze_ingredients(ingredients)
        
        # Analyze instructions
        instructions = recipe.get("instructions", "")
        instruction_analysis = self.instruction_analyzer.analyze_instructions(instructions)
        
        # Extract process parameters
        mixing_time = float(recipe.get("mixing_time_min", 10))
        proof_time = float(recipe.get("proof_time_min", 480))
        oven_temp = float(recipe.get("oven_temp_c", 450))
        cook_time = float(recipe.get("cook_time_min", 40))
        vessel = recipe.get("cooking_vessel", "dutch oven").lower()
        
        # Room temperature factor (if available)
        room_temp = recipe.get("room_temp_c", 21.0) or 21.0
        room_humidity = recipe.get("room_humidity_pct", 50.0) or 50.0
        
        # Hydration ratio
        hydration = ingredient_analysis.get("hydration_ratio", 0.65)
        
        # Baker's percentage (total ingredients / flour * 100)
        flour_weight = ingredient_analysis.get("flour_weight", 500)
        total_weight = ingredient_analysis.get("total_weight", 1000)
        baker_pct = (total_weight / flour_weight * 100) if flour_weight > 0 else 100
        
        # Fermentation parameters
        total_fermentation_hours = proof_time / 60.0
        bulk_fermentation_ratio = proof_time / mixing_time if mixing_time > 0 else 0
        
        # Temperature factor: optimal around 25-27C (0.8-1.0)
        # Lower temp = slower fermentation = finer crumb
        # Higher temp = faster fermentation = larger holes
        temp_factor = 1.0 - abs(room_temp - 25) * 0.02
        temp_factor = max(0.3, min(1.0, temp_factor))
        fermentation_temperature_factor = temp_factor
        
        # Cooking vessel openness (affects crust/crumb balance)
        vessel_openness = encode_vessel_openness(vessel)
        
        # Gluten development and hydration interaction
        gluten_score = ingredient_analysis.get("gluten_development_score", 0.7)
        hydrophilic_score = ingredient_analysis.get("hydrophilic_score", 0.6)
        enzymatic_score = ingredient_analysis.get("enzymatic_activity_score", 0.6)
        
        # Dough extensibility (higher hydration + higher gluten = more extensible = larger holes)
        dough_extensibility = (hydration / 0.75) * gluten_score  # Normalize to 75% as baseline
        dough_extensibility = min(1.0, dough_extensibility)
        
        # Fermentation power (starter % + enzymatic activity + time)
        starter_pct = ingredient_analysis.get("starter_percentage", 20.0)
        fermentation_power = (starter_pct / 20.0 * 0.3 + enzymatic_score * 0.4 + 
                            min(total_fermentation_hours / 20, 1.0) * 0.3)
        fermentation_power = min(1.0, fermentation_power)
        
        # Crumb potential (combination of factors)
        salt_pct = ingredient_analysis.get("salt_percentage", 2.0)
        sugar_pct = ingredient_analysis.get("sugar_percentage", 0.0)
        fat_pct = ingredient_analysis.get("fat_percentage", 0.0)
        
        # Salt inhibits fermentation but adds flavor
        # Sugar and fat can affect crumb structure
        salt_factor = max(0.7, 1.0 - salt_pct / 5.0)
        sugar_factor = min(1.0, 1.0 + sugar_pct * 0.1)
        fat_factor = max(0.8, 1.0 - fat_pct * 0.1)
        
        crumb_potential = (gluten_score * 0.3 + fermentation_power * 0.3 + 
                          dough_extensibility * 0.2 + salt_factor * fat_factor * sugar_factor * 0.2)
        
        # Oven temperature normalization (325-500C typical)
        oven_temp_norm = (oven_temp - 325) / (500 - 325)
        oven_temp_norm = max(0.0, min(1.0, oven_temp_norm))
        
        # Total cook time
        total_cook_time = cook_time + (proof_time / 60)
        
        # Mixing intensity from instructions
        mixing_intensity = instruction_analysis.get("mixing_intensity", 0.5)
        
        return RecipeFeatures(
            hydration_ratio=hydration,
            baker_percentage=baker_pct,
            total_fermentation_hours=total_fermentation_hours,
            bulk_fermentation_ratio=bulk_fermentation_ratio,
            fermentation_temperature_factor=fermentation_temperature_factor,
            gluten_development_score=gluten_score,
            hydrophilic_score=hydrophilic_score,
            enzymatic_activity_score=enzymatic_score,
            salt_percentage=ingredient_analysis.get("salt_percentage", 2.0),
            starter_percentage=ingredient_analysis.get("starter_percentage", 20.0),
            sugar_percentage=ingredient_analysis.get("sugar_percentage", 0.0),
            fat_percentage=ingredient_analysis.get("fat_percentage", 0.0),
            whole_grain_percentage=(ingredient_analysis.get("category_totals", {}).get("flour", 0.5) * 0.3),  # Simplified
            mixing_intensity=mixing_intensity,
            oven_temperature_norm=oven_temp_norm,
            cooking_vessel_openness=vessel_openness,
            total_cook_time_min=total_cook_time,
            dough_extensibility=dough_extensibility,
            fermentation_power=fermentation_power,
            crumb_potential_score=crumb_potential,
        )


class PorositySensitivityAnalyzer:
    """Analyzes feature importance and sensitivity for porosity prediction"""
    
    def __init__(self, model: RandomForestRegressor, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get importance of each feature"""
        importances = self.model.feature_importances_
        importance_dict = {name: imp for name, imp in zip(self.feature_names, importances)}
        # Sort by importance
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def get_feature_importance_report(self) -> str:
        """Generate text report of feature importance"""
        report = "FEATURE IMPORTANCE FOR POROSITY PREDICTION\n"
        report += "=" * 60 + "\n\n"
        
        importance_dict = self.get_feature_importance()
        total_importance = sum(importance_dict.values())
        
        for rank, (feature, importance) in enumerate(importance_dict.items(), 1):
            pct = (importance / total_importance * 100) if total_importance > 0 else 0
            bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
            report += f"{rank:2}. {feature:30} {pct:5.1f}% {bar}\n"
        
        return report
