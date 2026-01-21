"""
Unit tests for services
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from services.analysis_service import AnalysisService
from services.recipe_service import RecipeService
from services.quality_control_service import QualityControlService
from services.prediction_service import PredictionService
from services.defect_service import DefectService
from services.export_service import ExportService
from models.recipe import Recipe
from models.analysis_result import AnalysisResult
from models.qc_profile import QCProfile
from repositories.recipe_repository import RecipeRepository
from repositories.results_repository import ResultsRepository
from repositories.config_repository import ConfigRepository


class TestAnalysisService:
    """Test cases for AnalysisService"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        service = AnalysisService()
        assert isinstance(service.results_repo, ResultsRepository)
        assert service.output_dir == Path("./output")

    def test_init_with_custom_repo(self):
        """Test initialization with custom repository"""
        mock_repo = Mock(spec=ResultsRepository)
        service = AnalysisService(results_repo=mock_repo)
        assert service.results_repo == mock_repo

    @patch('services.analysis_service.ImagingPipeline')
    @patch('services.analysis_service.PorometryMetrics')
    @patch('services.analysis_service.VisualizationEngine')
    def test_analyze_image_success(self, mock_viz, mock_metrics, mock_pipeline):
        """Test successful image analysis"""
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

        # Create service
        service = AnalysisService()

        # Analyze image
        result = service.analyze_image(
            image_path="/path/to/test.jpg",
            pixel_size_mm=0.1,
            save_visualizations=True
        )

        # Verify result
        assert isinstance(result, AnalysisResult)
        assert result.porosity_percent == 65.5
        assert result.hole_count_total == 150
        assert result.image_path == "/path/to/test.jpg"

        # Verify mocks were called
        mock_pipeline.assert_called_once()
        mock_metrics.assert_called_once()
        mock_viz.assert_called_once()

    def test_analyze_image_invalid_path(self):
        """Test analysis with invalid image path"""
        service = AnalysisService()

        with pytest.raises(FileNotFoundError):
            service.analyze_image("/nonexistent/path.jpg")

    @patch('services.analysis_service.ImagingPipeline')
    def test_analyze_image_pipeline_error(self, mock_pipeline):
        """Test analysis when pipeline fails"""
        mock_pipeline_instance = Mock()
        mock_pipeline_instance.process_image.side_effect = Exception("Pipeline error")
        mock_pipeline.return_value = mock_pipeline_instance

        service = AnalysisService()

        with pytest.raises(Exception):
            service.analyze_image("/path/to/test.jpg")


class TestRecipeService:
    """Test cases for RecipeService"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        service = RecipeService()
        assert isinstance(service.recipe_repo, RecipeRepository)

    def test_init_with_custom_repo(self):
        """Test initialization with custom repository"""
        mock_repo = Mock(spec=RecipeRepository)
        service = RecipeService(recipe_repo=mock_repo)
        assert service.recipe_repo == mock_repo

    def test_create_recipe(self):
        """Test creating a new recipe"""
        service = RecipeService()

        recipe_data = {
            "name": "Test Recipe",
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }

        recipe = service.create_recipe(recipe_data)

        assert isinstance(recipe, Recipe)
        assert recipe.name == "Test Recipe"
        assert recipe.ingredients == {"flour": 500, "water": 350}
        assert recipe.id is not None

    def test_create_recipe_invalid_data(self):
        """Test creating recipe with invalid data"""
        service = RecipeService()

        invalid_data = {
            "name": "",  # Invalid empty name
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }

        with pytest.raises(ValueError):
            service.create_recipe(invalid_data)

    def test_get_recipe_by_id(self):
        """Test getting recipe by ID"""
        service = RecipeService()

        # Create a recipe first
        recipe_data = {
            "name": "Test Recipe",
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }
        created_recipe = service.create_recipe(recipe_data)

        # Retrieve it
        retrieved = service.get_recipe_by_id(created_recipe.id)
        assert retrieved is not None
        assert retrieved.name == "Test Recipe"

    def test_get_recipe_by_id_not_found(self):
        """Test getting non-existent recipe"""
        service = RecipeService()
        retrieved = service.get_recipe_by_id(999)
        assert retrieved is None

    def test_update_recipe(self):
        """Test updating a recipe"""
        service = RecipeService()

        # Create a recipe
        recipe_data = {
            "name": "Original Recipe",
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }
        recipe = service.create_recipe(recipe_data)

        # Update it
        update_data = {"name": "Updated Recipe", "measured_porosity": 75.0}
        updated = service.update_recipe(recipe.id, update_data)

        assert updated.name == "Updated Recipe"
        assert updated.measured_porosity == 75.0

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        service = RecipeService()

        # Create a recipe
        recipe_data = {
            "name": "Test Recipe",
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }
        recipe = service.create_recipe(recipe_data)

        # Delete it
        result = service.delete_recipe(recipe.id)
        assert result is True

        # Verify it's gone
        retrieved = service.get_recipe_by_id(recipe.id)
        assert retrieved is None


class TestQualityControlService:
    """Test cases for QualityControlService"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        service = QualityControlService()
        assert isinstance(service.config_repo, ConfigRepository)

    def test_init_with_custom_repo(self):
        """Test initialization with custom repository"""
        mock_repo = Mock(spec=ConfigRepository)
        service = QualityControlService(config_repo=mock_repo)
        assert service.config_repo == mock_repo

    def test_evaluate_analysis_valid(self):
        """Test evaluating a valid analysis result"""
        service = QualityControlService()

        # Create mock analysis result
        result = Mock()
        result.porosity_percent = 28.0
        result.hole_count_total = 250
        result.uniformity_score = 0.85

        # Evaluate
        passed, grade, reasons = service.evaluate_analysis(result)

        assert isinstance(passed, bool)
        assert grade in ["excellent", "good", "fair", "poor"]
        assert isinstance(reasons, list)

    def test_evaluate_analysis_invalid(self):
        """Test evaluating an invalid analysis result"""
        service = QualityControlService()

        # Create mock analysis result with invalid data
        result = Mock()
        result.porosity_percent = -10  # Invalid negative porosity
        result.hole_count_total = 250
        result.uniformity_score = 0.85

        passed, grade, reasons = service.evaluate_analysis(result)

        assert passed is False
        assert "porosity" in str(reasons).lower()

    def test_get_current_profile(self):
        """Test getting current QC profile"""
        service = QualityControlService()
        profile = service.get_current_profile()

        assert isinstance(profile, QCProfile)
        assert hasattr(profile, 'bread_type')

    def test_set_bread_type(self):
        """Test setting bread type"""
        service = QualityControlService()
        result = service.set_bread_type("ciabatta")

        assert result is True

    def test_set_bread_type_invalid(self):
        """Test setting invalid bread type"""
        service = QualityControlService()
        result = service.set_bread_type("nonexistent_type")

        assert result is False


class TestPredictionService:
    """Test cases for PredictionService"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        service = PredictionService()
        assert isinstance(service.recipe_repo, RecipeRepository)

    def test_predict_porosity(self):
        """Test porosity prediction"""
        service = PredictionService()

        recipe_data = {
            "ingredients": {"bread flour": 500, "water": 350, "salt": 10},
            "mixing_time_min": 10,
            "proof_time_min": 480,
            "oven_temp_c": 450,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 40
        }

        prediction, confidence = service.predict_porosity(recipe_data)

        assert isinstance(prediction, (int, float))
        assert 0 <= prediction <= 100
        assert isinstance(confidence, (int, float))
        assert 0 <= confidence <= 1

    def test_predict_porosity_invalid_data(self):
        """Test porosity prediction with invalid data"""
        service = PredictionService()

        invalid_data = {
            "ingredients": {},  # No ingredients
            "mixing_time_min": 10,
            "proof_time_min": 480,
            "oven_temp_c": 450,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 40
        }

        with pytest.raises(ValueError):
            service.predict_porosity(invalid_data)


class TestDefectService:
    """Test cases for DefectService"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        service = DefectService()
        assert service.config is not None

    @patch('services.defect_service.cv2')
    def test_detect_defects(self, mock_cv2):
        """Test defect detection"""
        # Mock OpenCV
        mock_image = Mock()
        mock_cv2.imread.return_value = mock_image
        mock_cv2.GaussianBlur.return_value = mock_image
        mock_cv2.threshold.return_value = (None, mock_image)
        mock_cv2.findContours.return_value = ([], None)

        service = DefectService()

        defects = service.detect_defects("/path/to/image.jpg")

        assert isinstance(defects, dict)
        assert "severity_score" in defects
        assert "defects" in defects


class TestExportService:
    """Test cases for ExportService"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        service = ExportService()
        assert service.config is not None

    def test_export_to_csv(self):
        """Test CSV export"""
        service = ExportService()

        # Create mock data
        results = [
            Mock(porosity_percent=65.0, hole_count_total=150, uniformity_score=0.85),
            Mock(porosity_percent=70.0, hole_count_total=200, uniformity_score=0.90)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.csv"

            service.export_to_csv(results, str(output_path))

            assert output_path.exists()

            # Check file contents
            with open(output_path, 'r') as f:
                content = f.read()
                assert "porosity_percent" in content
                assert "65.0" in content
                assert "70.0" in content

    def test_export_to_excel(self):
        """Test Excel export"""
        service = ExportService()

        # Create mock data
        results = [
            Mock(porosity_percent=65.0, hole_count_total=150, uniformity_score=0.85)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_export.xlsx"

            service.export_to_excel(results, str(output_path))

            assert output_path.exists()