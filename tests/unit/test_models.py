"""
Unit tests for domain models
"""

import pytest
from datetime import datetime
from dataclasses import asdict
from models.recipe import Recipe
from models.analysis_result import AnalysisResult
from models.qc_profile import QCProfile


class TestRecipe:
    """Test cases for Recipe domain model"""

    def test_recipe_creation_minimal(self):
        """Test creating a recipe with minimal required fields"""
        recipe = Recipe(
            name="Test Recipe",
            ingredients={"flour": 500, "water": 350},
            mixing_time_min=10,
            proof_time_min=120,
            oven_temp_c=220,
            cooking_vessel="dutch oven",
            cook_time_min=45
        )

        assert recipe.name == "Test Recipe"
        assert recipe.ingredients == {"flour": 500, "water": 350}
        assert recipe.mixing_time_min == 10
        assert recipe.proof_time_min == 120
        assert recipe.oven_temp_c == 220
        assert recipe.cooking_vessel == "dutch oven"
        assert recipe.cook_time_min == 45
        assert recipe.measured_porosity is None
        assert recipe.id is None
        assert recipe.version == 1

    def test_recipe_creation_full(self):
        """Test creating a recipe with all fields"""
        recipe = Recipe(
            name="Full Recipe",
            ingredients={"flour": 500, "water": 350, "salt": 10},
            mixing_time_min=15,
            proof_time_min=180,
            oven_temp_c=230,
            cooking_vessel="baguette pan",
            cook_time_min=30,
            measured_porosity=75.5,
            notes="Test notes",
            room_temp_c=22.5,
            room_humidity_pct=65.0,
            altitude_m=150,
            parent_recipe_id=1,
            id=42,
            quality_score=8.5
        )

        assert recipe.name == "Full Recipe"
        assert recipe.ingredients == {"flour": 500, "water": 350, "salt": 10}
        assert recipe.measured_porosity == 75.5
        assert recipe.notes == "Test notes"
        assert recipe.room_temp_c == 22.5
        assert recipe.room_humidity_pct == 65.0
        assert recipe.altitude_m == 150
        assert recipe.parent_recipe_id == 1
        assert recipe.id == 42
        assert recipe.quality_score == 8.5

    def test_recipe_validation_valid(self):
        """Test validation of a valid recipe"""
        recipe = Recipe(
            name="Valid Recipe",
            ingredients={"flour": 500, "water": 350},
            mixing_time_min=10,
            proof_time_min=120,
            oven_temp_c=220,
            cooking_vessel="dutch oven",
            cook_time_min=45
        )

        is_valid, errors = recipe.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_recipe_validation_invalid_name(self):
        """Test validation with invalid name"""
        recipe = Recipe(
            name="",  # Invalid empty name
            ingredients={"flour": 500, "water": 350},
            mixing_time_min=10,
            proof_time_min=120,
            oven_temp_c=220,
            cooking_vessel="dutch oven",
            cook_time_min=45
        )

        is_valid, errors = recipe.validate()
        assert is_valid is False
        assert "Recipe name cannot be empty" in errors

    def test_recipe_validation_no_ingredients(self):
        """Test validation with no ingredients"""
        recipe = Recipe(
            name="Test Recipe",
            ingredients={},  # No ingredients
            mixing_time_min=10,
            proof_time_min=120,
            oven_temp_c=220,
            cooking_vessel="dutch oven",
            cook_time_min=45
        )

        is_valid, errors = recipe.validate()
        assert is_valid is False
        assert "Recipe must have at least one ingredient" in errors

    def test_recipe_to_dict(self):
        """Test converting recipe to dictionary"""
        recipe = Recipe(
            name="Dict Recipe",
            ingredients={"flour": 500, "water": 350},
            mixing_time_min=10,
            proof_time_min=120,
            oven_temp_c=220,
            cooking_vessel="dutch oven",
            cook_time_min=45,
            measured_porosity=70.0
        )

        recipe_dict = asdict(recipe)

        assert recipe_dict["name"] == "Dict Recipe"
        assert recipe_dict["ingredients"] == {"flour": 500, "water": 350}
        assert recipe_dict["measured_porosity"] == 70.0
        assert "created_at" in recipe_dict
        assert "version" in recipe_dict

    def test_recipe_created_at_auto_generated(self):
        """Test that created_at is auto-generated"""
        recipe = Recipe(
            name="Auto Recipe",
            ingredients={"flour": 500, "water": 350},
            mixing_time_min=10,
            proof_time_min=120,
            oven_temp_c=220,
            cooking_vessel="dutch oven",
            cook_time_min=45
        )

        # Should have a created_at timestamp
        assert recipe.created_at is not None
        assert isinstance(recipe.created_at, str)

        # Should be parseable as ISO format
        datetime.fromisoformat(recipe.created_at)


class TestQCProfile:
    """Test cases for QCProfile domain model"""

    def test_qc_profile_creation_minimal(self):
        """Test creating QC profile with minimal required fields"""
        profile = QCProfile(
            bread_type="sourdough",
            display_name="Sourdough Bread",
            porosity_target_min=20.0,
            porosity_target_max=35.0,
            porosity_warning_min=18.0,
            porosity_warning_max=37.0,
            hole_count_target_min=100,
            hole_count_target_max=400,
            hole_diameter_target_min=2.0,
            hole_diameter_target_max=8.0,
            uniformity_acceptable_min=0.7,
            consistency_cv_max=0.15
        )

        assert profile.bread_type == "sourdough"
        assert profile.display_name == "Sourdough Bread"
        assert profile.porosity_target_min == 20.0
        assert profile.porosity_target_max == 35.0
        assert profile.hole_count_target_min == 100
        assert profile.uniformity_acceptable_min == 0.7
        assert profile.consistency_cv_max == 0.15

    def test_qc_profile_creation_with_grades(self):
        """Test creating QC profile with quality grades"""
        quality_grades = {
            "excellent": {"porosity": [25, 32], "uniformity": [0.85, 1.0]},
            "good": {"porosity": [22, 35], "uniformity": [0.75, 0.95]},
            "fair": {"porosity": [18, 38], "uniformity": [0.65, 0.85]},
            "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]}
        }

        profile = QCProfile(
            bread_type="ciabatta",
            display_name="Ciabatta",
            porosity_target_min=30.0,
            porosity_target_max=45.0,
            porosity_warning_min=25.0,
            porosity_warning_max=50.0,
            hole_count_target_min=200,
            hole_count_target_max=600,
            hole_diameter_target_min=3.0,
            hole_diameter_target_max=10.0,
            uniformity_acceptable_min=0.6,
            consistency_cv_max=0.20,
            quality_grades=quality_grades,
            description="Open crumb Italian bread"
        )

        assert profile.bread_type == "ciabatta"
        assert profile.quality_grades == quality_grades
        assert profile.description == "Open crumb Italian bread"

    def test_qc_profile_validation_valid(self):
        """Test validation of a valid QC profile"""
        profile = QCProfile(
            bread_type="test",
            display_name="Test Bread",
            porosity_target_min=20.0,
            porosity_target_max=35.0,
            porosity_warning_min=18.0,
            porosity_warning_max=37.0,
            hole_count_target_min=100,
            hole_count_target_max=400,
            hole_diameter_target_min=2.0,
            hole_diameter_target_max=8.0,
            uniformity_acceptable_min=0.7,
            consistency_cv_max=0.15
        )

        is_valid, errors = profile.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_qc_profile_validation_invalid_ranges(self):
        """Test validation with invalid ranges"""
        profile = QCProfile(
            bread_type="test",
            display_name="Test Bread",
            porosity_target_min=40.0,  # Min > Max
            porosity_target_max=30.0,
            porosity_warning_min=18.0,
            porosity_warning_max=37.0,
            hole_count_target_min=100,
            hole_count_target_max=400,
            hole_diameter_target_min=2.0,
            hole_diameter_target_max=8.0,
            uniformity_acceptable_min=0.7,
            consistency_cv_max=0.15
        )

        is_valid, errors = profile.validate()
        assert is_valid is False
        assert any("porosity target min" in error.lower() for error in errors)

    def test_qc_profile_to_dict(self):
        """Test converting QC profile to dictionary"""
        profile = QCProfile(
            bread_type="test",
            display_name="Test Bread",
            porosity_target_min=20.0,
            porosity_target_max=35.0,
            porosity_warning_min=18.0,
            porosity_warning_max=37.0,
            hole_count_target_min=100,
            hole_count_target_max=400,
            hole_diameter_target_min=2.0,
            hole_diameter_target_max=8.0,
            uniformity_acceptable_min=0.7,
            consistency_cv_max=0.15,
            description="Test description"
        )

        profile_dict = asdict(profile)

        assert profile_dict["bread_type"] == "test"
        assert profile_dict["display_name"] == "Test Bread"
        assert profile_dict["porosity_target_min"] == 20.0
        assert profile_dict["description"] == "Test description"
        assert "quality_grades" in profile_dict

    def test_qc_profile_evaluate_result(self):
        """Test evaluating an analysis result against QC profile"""
        profile = QCProfile(
            bread_type="sourdough",
            display_name="Sourdough Bread",
            porosity_target_min=20.0,
            porosity_target_max=35.0,
            porosity_warning_min=18.0,
            porosity_warning_max=37.0,
            hole_count_target_min=100,
            hole_count_target_max=400,
            hole_diameter_target_min=2.0,
            hole_diameter_target_max=8.0,
            uniformity_acceptable_min=0.7,
            consistency_cv_max=0.15
        )

        # Test porosity evaluation
        assert profile.evaluate_porosity(28.0) == 'pass'  # Within target range
        assert profile.evaluate_porosity(15.0) == 'fail'  # Below warning min
        assert profile.evaluate_porosity(40.0) == 'fail'  # Above warning max

        # Test hole count evaluation
        assert profile.evaluate_hole_count(250) == 'pass'  # Within range
        assert profile.evaluate_hole_count(50) == 'fail'   # Below min
        assert profile.evaluate_hole_count(500) == 'fail'  # Above max

        # Test uniformity evaluation
        assert profile.evaluate_uniformity(0.85) == 'pass'  # Above threshold
        assert profile.evaluate_uniformity(0.5) == 'fail'   # Below threshold

        # Test quality grade
        grade = profile.get_quality_grade(porosity=28.0, uniformity=0.85)
        assert grade in ["excellent", "good", "fair", "poor"]


class TestAnalysisResult:
    """Test cases for AnalysisResult domain model"""

    def test_analysis_result_creation_minimal(self):
        """Test creating analysis result with minimal required fields"""
        result = AnalysisResult(
            image_path="/path/to/image.jpg",
            image_filename="image.jpg",
            porosity_percent=65.5,
            hole_count_total=150,
            hole_diameter_mean_mm=2.5,
            hole_diameter_std_mm=0.8,
            hole_diameter_min_mm=1.0,
            hole_diameter_max_mm=5.0,
            holes_per_cm2=25.0,
            anisotropy_ratio=1.2,
            orientation_mean_deg=45.0,
            uniformity_score=0.85
        )

        assert result.image_path == "/path/to/image.jpg"
        assert result.image_filename == "image.jpg"
        assert result.porosity_percent == 65.5
        assert result.hole_count_total == 150
        assert result.hole_diameter_mean_mm == 2.5
        assert result.uniformity_score == 0.85
        assert result.qc_passed is None
        assert result.quality_grade is None

    def test_analysis_result_creation_full(self):
        """Test creating analysis result with all fields"""
        result = AnalysisResult(
            image_path="/path/to/image.jpg",
            image_filename="image.jpg",
            porosity_percent=70.0,
            hole_count_total=200,
            hole_diameter_mean_mm=3.0,
            hole_diameter_std_mm=1.0,
            hole_diameter_min_mm=1.5,
            hole_diameter_max_mm=6.0,
            holes_per_cm2=30.0,
            anisotropy_ratio=1.1,
            orientation_mean_deg=30.0,
            uniformity_score=0.92,
            qc_passed=True,
            quality_grade="excellent",
            defects_detected={"uneven_rise": 0.3},
            pixel_size_mm=0.05,
            threshold_method="adaptive",
            normalization_method="morphology",
            processing_time_sec=2.5,
            output_comparison_path="/output/comparison.png",
            output_annotated_path="/output/annotated.png"
        )

        assert result.porosity_percent == 70.0
        assert result.qc_passed is True
        assert result.quality_grade == "excellent"
        assert result.defects_detected == {"uneven_rise": 0.3}
        assert result.pixel_size_mm == 0.05
        assert result.threshold_method == "adaptive"
        assert result.processing_time_sec == 2.5
        assert result.output_comparison_path == "/output/comparison.png"

    def test_analysis_result_to_dict(self):
        """Test converting analysis result to dictionary"""
        result = AnalysisResult(
            image_path="/path/to/image.jpg",
            image_filename="image.jpg",
            porosity_percent=65.5,
            hole_count_total=150,
            hole_diameter_mean_mm=2.5,
            hole_diameter_std_mm=0.8,
            hole_diameter_min_mm=1.0,
            hole_diameter_max_mm=5.0,
            holes_per_cm2=25.0,
            anisotropy_ratio=1.2,
            orientation_mean_deg=45.0,
            uniformity_score=0.85
        )

        result_dict = asdict(result)

        assert result_dict["image_path"] == "/path/to/image.jpg"
        assert result_dict["porosity_percent"] == 65.5
        assert result_dict["hole_count_total"] == 150
        assert result_dict["uniformity_score"] == 0.85
        assert "hole_size_distribution_data" in result_dict

    def test_analysis_result_metrics_validation(self):
        """Test that metrics are within expected ranges"""
        result = AnalysisResult(
            image_path="/path/to/image.jpg",
            image_filename="image.jpg",
            porosity_percent=75.0,
            hole_count_total=100,
            hole_diameter_mean_mm=2.0,
            hole_diameter_std_mm=0.5,
            hole_diameter_min_mm=1.0,
            hole_diameter_max_mm=4.0,
            holes_per_cm2=20.0,
            anisotropy_ratio=1.0,
            orientation_mean_deg=0.0,
            uniformity_score=1.0
        )

        # Test reasonable ranges
        assert 0 <= result.porosity_percent <= 100
        assert result.hole_count_total >= 0
        assert result.hole_diameter_mean_mm > 0
        assert result.hole_diameter_std_mm >= 0
        assert result.hole_diameter_min_mm >= 0
        assert result.hole_diameter_max_mm >= result.hole_diameter_min_mm
        assert result.anisotropy_ratio >= 1.0
        assert 0 <= result.orientation_mean_deg <= 180
        assert 0 <= result.uniformity_score <= 1.0