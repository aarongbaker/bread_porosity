"""
Integration tests for Bread Porosity Analysis Tool
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from services.analysis_service import AnalysisService
from services.recipe_service import RecipeService
from services.quality_control_service import QualityControlService
from repositories.recipe_repository import RecipeRepository
from repositories.results_repository import ResultsRepository
from repositories.config_repository import ConfigRepository
from models.recipe import Recipe
from models.analysis_result import AnalysisResult


class TestAnalysisWorkflow:
    """Integration tests for complete analysis workflow"""

    @patch('services.analysis_service.ImagingPipeline')
    @patch('services.analysis_service.PorometryMetrics')
    @patch('services.analysis_service.VisualizationEngine')
    def test_full_analysis_workflow(self, mock_viz, mock_metrics, mock_pipeline):
        """Test complete analysis workflow from image to results"""
        # Setup mocks
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_image.return_value = {"processed_image": "mock"}
        mock_pipeline.return_value = mock_pipeline_instance

        mock_metrics_instance = Mock()
        mock_metrics_instance.compute_metrics.return_value = {
            "porosity_percent": 68.5,
            "hole_count_total": 180,
            "hole_diameter_mean_mm": 2.8,
            "hole_diameter_std_mm": 0.9,
            "hole_diameter_min_mm": 1.2,
            "hole_diameter_max_mm": 6.1,
            "holes_per_cm2": 28.0,
            "anisotropy_ratio": 1.15,
            "orientation_mean_deg": 42.0,
            "uniformity_score": 0.88
        }
        mock_metrics.return_value = mock_metrics_instance

        mock_viz_instance = Mock()
        mock_viz.return_value = mock_viz_instance

        # Create service
        service = AnalysisService()

        # Run analysis
        result = service.analyze_image(
            image_path="/fake/path/image.jpg",
            pixel_size_mm=0.1,
            save_visualizations=True
        )

        # Verify result
        assert isinstance(result, AnalysisResult)
        assert result.porosity_percent == 68.5
        assert result.hole_count_total == 180
        assert result.uniformity_score == 0.88
        assert result.image_path == "/fake/path/image.jpg"

    def test_recipe_to_analysis_integration(self):
        """Test integration between recipe creation and analysis"""
        # Create recipe service
        recipe_service = RecipeService()

        # Create a recipe
        recipe_data = {
            "name": "Integration Test Recipe",
            "ingredients": {"flour": 500, "water": 375, "salt": 10, "yeast": 5},
            "mixing_time_min": 12,
            "proof_time_min": 180,
            "oven_temp_c": 230,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 35
        }

        recipe = recipe_service.create_recipe(recipe_data)
        assert recipe is not None
        assert recipe.name == "Integration Test Recipe"

        # Retrieve the recipe
        retrieved = recipe_service.get_recipe_by_id(recipe.id)
        assert retrieved is not None
        assert retrieved.ingredients == {"flour": 500, "water": 375, "salt": 10, "yeast": 5}

    def test_qc_evaluation_integration(self):
        """Test integration of QC evaluation with analysis results"""
        # Create QC service
        qc_service = QualityControlService()

        # Create mock analysis result
        result = Mock()
        result.porosity_percent = 72.0
        result.hole_count_total = 220
        result.uniformity_score = 0.91

        # Evaluate
        passed, grade, reasons = qc_service.evaluate_analysis(result)

        # Verify evaluation worked
        assert isinstance(passed, bool)
        assert grade in ["excellent", "good", "fair", "poor"]
        assert isinstance(reasons, list)


class TestRepositoryIntegration:
    """Integration tests for repository interactions"""

    def test_recipe_persistence_workflow(self):
        """Test complete recipe persistence workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repository with temp file
            recipes_path = Path(temp_dir) / "test_recipes.json"
            repo = RecipeRepository(str(recipes_path))

            # Create and save multiple recipes
            recipes_data = [
                {
                    "name": "Sourdough Recipe",
                    "ingredients": {"flour": 500, "water": 350, "starter": 100},
                    "mixing_time_min": 10,
                    "proof_time_min": 480,
                    "oven_temp_c": 450,
                    "cooking_vessel": "dutch oven",
                    "cook_time_min": 40,
                    "measured_porosity": 75.0
                },
                {
                    "name": "Ciabatta Recipe",
                    "ingredients": {"flour": 500, "water": 400, "salt": 10, "yeast": 2},
                    "mixing_time_min": 8,
                    "proof_time_min": 120,
                    "oven_temp_c": 220,
                    "cooking_vessel": "baking stone",
                    "cook_time_min": 25,
                    "measured_porosity": 82.0
                }
            ]

            saved_recipes = []
            for data in recipes_data:
                recipe = Recipe(**data)
                repo.save_recipe(recipe)
                saved_recipes.append(recipe)

            # Load and verify
            loaded_recipes = repo.get_all_recipes()
            assert len(loaded_recipes) == 2

            # Check specific recipes
            sourdough = next(r for r in loaded_recipes if r.name == "Sourdough Recipe")
            assert sourdough.measured_porosity == 75.0
            assert sourdough.ingredients["starter"] == 100

            ciabatta = next(r for r in loaded_recipes if r.name == "Ciabatta Recipe")
            assert ciabatta.measured_porosity == 82.0
            assert ciabatta.cooking_vessel == "baking stone"

    def test_results_persistence_workflow(self):
        """Test complete results persistence workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repository with temp file
            results_path = Path(temp_dir) / "test_results.json"
            repo = ResultsRepository(str(results_path))

            # Create and save analysis results
            results_data = [
                {
                    "image_path": "/images/loaf_001.jpg",
                    "image_filename": "loaf_001.jpg",
                    "porosity_percent": 68.5,
                    "hole_count_total": 180,
                    "hole_diameter_mean_mm": 2.8,
                    "hole_diameter_std_mm": 0.9,
                    "hole_diameter_min_mm": 1.2,
                    "hole_diameter_max_mm": 6.1,
                    "holes_per_cm2": 28.0,
                    "anisotropy_ratio": 1.15,
                    "orientation_mean_deg": 42.0,
                    "uniformity_score": 0.88
                },
                {
                    "image_path": "/images/loaf_002.jpg",
                    "image_filename": "loaf_002.jpg",
                    "porosity_percent": 71.2,
                    "hole_count_total": 195,
                    "hole_diameter_mean_mm": 3.1,
                    "hole_diameter_std_mm": 1.1,
                    "hole_diameter_min_mm": 1.4,
                    "hole_diameter_max_mm": 7.2,
                    "holes_per_cm2": 31.0,
                    "anisotropy_ratio": 1.08,
                    "orientation_mean_deg": 38.0,
                    "uniformity_score": 0.92
                }
            ]

            saved_results = []
            for data in results_data:
                result = AnalysisResult(**data)
                repo.save_result(result)
                saved_results.append(result)

            # Load and verify
            loaded_results = repo.get_all_results()
            assert len(loaded_results) == 2

            # Check specific results
            result1 = next(r for r in loaded_results if r.image_filename == "loaf_001.jpg")
            assert result1.porosity_percent == 68.5
            assert result1.hole_count_total == 180

            result2 = next(r for r in loaded_results if r.image_filename == "loaf_002.jpg")
            assert result2.porosity_percent == 71.2
            assert result2.uniformity_score == 0.92


class TestServiceIntegration:
    """Integration tests for service interactions"""

    def test_recipe_service_with_repository(self):
        """Test recipe service working with repository"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repository
            recipes_path = Path(temp_dir) / "test_recipes.json"
            repo = RecipeRepository(str(recipes_path))

            # Create service with repository
            service = RecipeService(repo)

            # Create recipe through service
            recipe_data = {
                "name": "Service Integration Recipe",
                "ingredients": {"flour": 500, "water": 350, "salt": 10},
                "mixing_time_min": 10,
                "proof_time_min": 120,
                "oven_temp_c": 220,
                "cooking_vessel": "dutch oven",
                "cook_time_min": 45
            }

            recipe = service.create_recipe(recipe_data)
            assert recipe is not None

            # Retrieve through service
            retrieved = service.get_recipe_by_id(recipe.id)
            assert retrieved is not None
            assert retrieved.name == "Service Integration Recipe"

            # Update through service
            update_data = {"measured_porosity": 78.5}
            updated = service.update_recipe(recipe.id, update_data)
            assert updated.measured_porosity == 78.5

    def test_cross_service_integration(self):
        """Test integration between multiple services"""
        # Create services
        recipe_service = RecipeService()
        qc_service = QualityControlService()

        # Create a recipe
        recipe_data = {
            "name": "Cross-Service Recipe",
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }
        recipe = recipe_service.create_recipe(recipe_data)

        # Create mock analysis result
        result = Mock()
        result.porosity_percent = 65.0
        result.hole_count_total = 150
        result.uniformity_score = 0.85

        # Evaluate with QC service
        passed, grade, reasons = qc_service.evaluate_analysis(result)

        # Verify integration works
        assert isinstance(passed, bool)
        assert grade in ["excellent", "good", "fair", "poor"]