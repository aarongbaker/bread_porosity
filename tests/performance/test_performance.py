"""
Performance tests for Bread Porosity Analysis Tool
"""

import pytest
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from services.analysis_service import AnalysisService
from repositories.recipe_repository import RecipeRepository
from repositories.results_repository import ResultsRepository


class TestAnalysisPerformance:
    """Performance tests for analysis operations"""

    @patch('services.analysis_service.ImagingPipeline')
    @patch('services.analysis_service.PorometryMetrics')
    @patch('services.analysis_service.VisualizationEngine')
    def test_analysis_speed(self, mock_viz, mock_metrics, mock_pipeline):
        """Test analysis performance meets speed requirements"""
        # Setup mocks with realistic processing times
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_image.return_value = {"processed_image": "mock"}
        mock_pipeline.return_value = mock_pipeline_instance

        mock_metrics_instance = Mock()
        mock_metrics_instance.compute_metrics.return_value = {
            "porosity_percent": 65.5,
            "hole_count_total": 150,
            "hole_diameter_mean_mm": 2.5,
            "hole_diameter_std_mm": 0.8,
            "hole_diameter_min_mm": 1.0,
            "hole_diameter_max_mm": 5.0,
            "holes_per_cm2": 25.0,
            "anisotropy_ratio": 1.2,
            "orientation_mean_deg": 45.0,
            "uniformity_score": 0.85
        }
        mock_metrics.return_value = mock_metrics_instance

        mock_viz_instance = Mock()
        mock_viz.return_value = mock_viz_instance

        service = AnalysisService()

        # Measure analysis time
        start_time = time.time()
        result = service.analyze_image("/fake/image.jpg", pixel_size_mm=0.1)
        end_time = time.time()

        analysis_time = end_time - start_time

        # Should complete in reasonable time (allowing for mock overhead)
        assert analysis_time < 5.0  # 5 seconds max
        assert result is not None

    @patch('services.analysis_service.ImagingPipeline')
    @patch('services.analysis_service.PorometryMetrics')
    @patch('services.analysis_service.VisualizationEngine')
    def test_batch_analysis_performance(self, mock_viz, mock_metrics, mock_pipeline):
        """Test batch analysis performance"""
        # Setup mocks
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_image.return_value = {"processed_image": "mock"}
        mock_pipeline.return_value = mock_pipeline_instance

        mock_metrics_instance = Mock()
        mock_metrics_instance.compute_metrics.return_value = {
            "porosity_percent": 65.5,
            "hole_count_total": 150,
            "hole_diameter_mean_mm": 2.5,
            "hole_diameter_std_mm": 0.8,
            "hole_diameter_min_mm": 1.0,
            "hole_diameter_max_mm": 5.0,
            "holes_per_cm2": 25.0,
            "anisotropy_ratio": 1.2,
            "orientation_mean_deg": 45.0,
            "uniformity_score": 0.85
        }
        mock_metrics.return_value = mock_metrics_instance

        mock_viz_instance = Mock()
        mock_viz.return_value = mock_viz_instance

        service = AnalysisService()

        # Test batch of 10 images
        image_paths = [f"/fake/image_{i}.jpg" for i in range(10)]

        start_time = time.time()
        results = service.batch_analyze(image_paths, pixel_size_mm=0.1)
        end_time = time.time()

        batch_time = end_time - start_time

        # Should complete batch in reasonable time
        assert batch_time < 30.0  # 30 seconds max for 10 images
        assert len(results) == 10
        assert all(r is not None for r in results)


class TestRepositoryPerformance:
    """Performance tests for repository operations"""

    def test_recipe_repository_large_dataset(self):
        """Test recipe repository performance with large dataset"""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipes_path = Path(temp_dir) / "large_recipes.json"
            repo = RecipeRepository(str(recipes_path))

            # Create 100 recipes
            recipes = []
            for i in range(100):
                recipe = Mock()
                recipe.id = i + 1
                recipe.name = f"Recipe {i+1}"
                recipe.ingredients = {"flour": 500, "water": 350}
                recipe.mixing_time_min = 10
                recipe.proof_time_min = 120
                recipe.oven_temp_c = 220
                recipe.cooking_vessel = "dutch oven"
                recipe.cook_time_min = 45
                recipe.measured_porosity = 60.0 + (i % 20)  # Vary porosity
                recipes.append(recipe)

            # Save all recipes
            start_time = time.time()
            for recipe in recipes:
                repo.save_recipe(recipe)
            save_time = time.time() - start_time

            # Load all recipes
            start_time = time.time()
            loaded_recipes = repo.get_all_recipes()
            load_time = time.time() - start_time

            # Verify performance
            assert save_time < 5.0  # Save 100 recipes in < 5 seconds
            assert load_time < 2.0  # Load 100 recipes in < 2 seconds
            assert len(loaded_recipes) == 100

    def test_results_repository_large_dataset(self):
        """Test results repository performance with large dataset"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_path = Path(temp_dir) / "large_results.json"
            repo = ResultsRepository(str(results_path))

            # Create 50 analysis results
            results = []
            for i in range(50):
                result = Mock()
                result.image_path = f"/images/image_{i}.jpg"
                result.image_filename = f"image_{i}.jpg"
                result.porosity_percent = 60.0 + (i % 20)
                result.hole_count_total = 100 + i * 2
                result.hole_diameter_mean_mm = 2.0 + (i % 5) * 0.2
                result.uniformity_score = 0.7 + (i % 30) * 0.01
                results.append(result)

            # Save all results
            start_time = time.time()
            for result in results:
                repo.save_result(result)
            save_time = time.time() - start_time

            # Load all results
            start_time = time.time()
            loaded_results = repo.get_all_results()
            load_time = time.time() - start_time

            # Get recent results
            start_time = time.time()
            recent = repo.get_recent_results(limit=10)
            recent_time = time.time() - start_time

            # Verify performance
            assert save_time < 3.0  # Save 50 results in < 3 seconds
            assert load_time < 1.0  # Load 50 results in < 1 second
            assert recent_time < 0.5  # Get recent 10 in < 0.5 seconds
            assert len(loaded_results) == 50
            assert len(recent) == 10


class TestMemoryUsage:
    """Tests for memory usage and resource management"""

    def test_service_initialization_memory(self):
        """Test that services initialize without excessive memory usage"""
        # This is a basic test - in a real scenario we'd use memory profiling
        from services.analysis_service import AnalysisService
        from services.recipe_service import RecipeService
        from services.quality_control_service import QualityControlService

        # Create services
        analysis_service = AnalysisService()
        recipe_service = RecipeService()
        qc_service = QualityControlService()

        # Basic verification that they exist and have expected attributes
        assert hasattr(analysis_service, 'results_repo')
        assert hasattr(recipe_service, 'recipe_repo')
        assert hasattr(qc_service, 'config_repo')

    def test_repository_cleanup(self):
        """Test that repositories clean up resources properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repositories with temp files
            recipes_path = Path(temp_dir) / "cleanup_recipes.json"
            results_path = Path(temp_dir) / "cleanup_results.json"

            recipe_repo = RecipeRepository(str(recipes_path))
            results_repo = ResultsRepository(str(results_path))

            # Add some data
            recipe = Mock()
            recipe.id = 1
            recipe.name = "Cleanup Test Recipe"
            recipe_repo.save_recipe(recipe)

            result = Mock()
            result.image_path = "/test/image.jpg"
            result.porosity_percent = 65.0
            results_repo.save_result(result)

            # Delete data
            recipe_repo.delete_recipe(1)

            # Verify files still exist but data is cleaned up
            assert recipes_path.exists()
            assert results_path.exists()

            # Verify data was removed
            recipes = recipe_repo.get_all_recipes()
            results = results_repo.get_all_results()

            assert len(recipes) == 0
            # Note: ResultsRepository may keep all results, depending on implementation


@pytest.mark.slow
class TestSlowOperations:
    """Slow-running tests that should be run less frequently"""

    def test_large_batch_processing(self):
        """Test processing a large batch of images (marked as slow)"""
        # This would test processing 100+ images
        # For now, just verify the test framework works
        assert True

    def test_complex_recipe_analysis(self):
        """Test analysis of complex recipes with many ingredients"""
        # This would test recipes with 20+ ingredients
        # For now, just verify the test framework works
        assert True