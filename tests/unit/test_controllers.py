"""
Unit tests for controllers
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from gui.controllers.analysis_controller import AnalysisController
from gui.controllers.recipe_controller import RecipeController
from gui.controllers.qc_controller import QCController
from gui.controllers.prediction_controller import PredictionController
from gui.controllers.defect_controller import DefectController
from gui.controllers.export_controller import ExportController
from services.analysis_service import AnalysisService
from services.recipe_service import RecipeService
from services.quality_control_service import QualityControlService
from services.prediction_service import PredictionService
from services.defect_service import DefectService
from services.export_service import ExportService
from models.analysis_result import AnalysisResult
from models.recipe import Recipe


class TestAnalysisController:
    """Test cases for AnalysisController"""

    def test_init(self):
        """Test initialization"""
        mock_service = Mock(spec=AnalysisService)
        mock_callback = Mock()

        controller = AnalysisController(mock_service, mock_callback)

        assert controller.analysis_service == mock_service
        assert controller.view_callback == mock_callback
        assert controller.current_result is None
        assert controller.is_analyzing is False

    @patch('gui.controllers.analysis_controller.threading.Thread')
    def test_analyze_single_image_async(self, mock_thread):
        """Test asynchronous single image analysis"""
        mock_service = Mock(spec=AnalysisService)
        mock_result = Mock(spec=AnalysisResult)
        mock_service.analyze_image.return_value = mock_result

        controller = AnalysisController(mock_service)

        # Mock thread to run synchronously for testing
        def mock_start():
            controller._analyze_single_image_sync(
                "/path/to/image.jpg",
                0.1, "otsu", "clahe", None, None, None
            )

        mock_thread_instance = Mock()
        mock_thread_instance.start = mock_start
        mock_thread.return_value = mock_thread_instance

        controller.analyze_single_image_async(
            "/path/to/image.jpg",
            pixel_size_mm=0.1,
            threshold_method="otsu",
            normalize_method="clahe"
        )

        # Verify service was called
        mock_service.analyze_image.assert_called_once()
        assert controller.current_result == mock_result

    def test_analyze_single_image_sync(self):
        """Test synchronous single image analysis"""
        mock_service = Mock(spec=AnalysisService)
        mock_result = Mock(spec=AnalysisResult)
        mock_service.analyze_image.return_value = mock_result

        controller = AnalysisController(mock_service)

        result = controller._analyze_single_image_sync(
            "/path/to/image.jpg",
            0.1, "otsu", "clahe", None, None, None
        )

        assert result == mock_result
        mock_service.analyze_image.assert_called_once()

    def test_analyze_single_image_invalid_path(self):
        """Test analysis with invalid image path"""
        mock_service = Mock(spec=AnalysisService)
        mock_service.analyze_image.side_effect = FileNotFoundError("File not found")

        controller = AnalysisController(mock_service)

        result = controller._analyze_single_image_sync(
            "/invalid/path.jpg",
            0.1, "otsu", "clahe", None, None, None
        )

        assert result is None

    def test_batch_analyze(self):
        """Test batch analysis"""
        mock_service = Mock(spec=AnalysisService)
        mock_result = Mock(spec=AnalysisResult)
        mock_service.analyze_image.return_value = mock_result

        controller = AnalysisController(mock_service)

        image_paths = ["/path/to/image1.jpg", "/path/to/image2.jpg"]

        results = controller.batch_analyze(
            image_paths,
            pixel_size_mm=0.1,
            threshold_method="otsu",
            normalize_method="clahe"
        )

        assert len(results) == 2
        assert all(r == mock_result for r in results)
        assert mock_service.analyze_image.call_count == 2

    def test_get_current_result(self):
        """Test getting current result"""
        controller = AnalysisController(Mock(spec=AnalysisService))
        mock_result = Mock(spec=AnalysisResult)

        controller.current_result = mock_result
        result = controller.get_current_result()

        assert result == mock_result

    def test_clear_current_result(self):
        """Test clearing current result"""
        controller = AnalysisController(Mock(spec=AnalysisService))
        mock_result = Mock(spec=AnalysisResult)

        controller.current_result = mock_result
        controller.clear_current_result()

        assert controller.current_result is None


class TestRecipeController:
    """Test cases for RecipeController"""

    def test_init(self):
        """Test initialization"""
        mock_service = Mock(spec=RecipeService)
        mock_callback = Mock()

        controller = RecipeController(mock_service, mock_callback)

        assert controller.recipe_service == mock_service
        assert controller.view_callback == mock_callback

    def test_create_recipe(self):
        """Test creating a recipe"""
        mock_service = Mock(spec=RecipeService)
        mock_recipe = Mock(spec=Recipe)
        mock_service.create_recipe.return_value = mock_recipe

        controller = RecipeController(mock_service)

        recipe_data = {
            "name": "Test Recipe",
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }

        result = controller.create_recipe(recipe_data)

        assert result == mock_recipe
        mock_service.create_recipe.assert_called_once_with(recipe_data)

    def test_create_recipe_invalid(self):
        """Test creating invalid recipe"""
        mock_service = Mock(spec=RecipeService)
        mock_service.create_recipe.side_effect = ValueError("Invalid recipe")

        controller = RecipeController(mock_service)

        invalid_data = {"name": ""}  # Invalid

        result = controller.create_recipe(invalid_data)

        assert result is None
        mock_service.create_recipe.assert_called_once_with(invalid_data)

    def test_get_all_recipes(self):
        """Test getting all recipes"""
        mock_service = Mock(spec=RecipeService)
        mock_recipes = [Mock(spec=Recipe), Mock(spec=Recipe)]
        mock_service.get_all_recipes.return_value = mock_recipes

        controller = RecipeController(mock_service)

        recipes = controller.get_all_recipes()

        assert recipes == mock_recipes
        mock_service.get_all_recipes.assert_called_once()

    def test_update_recipe(self):
        """Test updating a recipe"""
        mock_service = Mock(spec=RecipeService)
        mock_recipe = Mock(spec=Recipe)
        mock_service.update_recipe.return_value = mock_recipe

        controller = RecipeController(mock_service)

        update_data = {"name": "Updated Name"}
        result = controller.update_recipe(1, update_data)

        assert result == mock_recipe
        mock_service.update_recipe.assert_called_once_with(1, update_data)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        mock_service = Mock(spec=RecipeService)
        mock_service.delete_recipe.return_value = True

        controller = RecipeController(mock_service)

        result = controller.delete_recipe(1)

        assert result is True
        mock_service.delete_recipe.assert_called_once_with(1)


class TestQCController:
    """Test cases for QCController"""

    def test_init(self):
        """Test initialization"""
        mock_service = Mock(spec=QualityControlService)
        mock_callback = Mock()

        controller = QCController(mock_service, mock_callback)

        assert controller.qc_service == mock_service
        assert controller.view_callback == mock_callback

    def test_evaluate_result(self):
        """Test evaluating analysis result"""
        mock_service = Mock(spec=QualityControlService)
        mock_service.evaluate_analysis.return_value = (True, "good", ["All checks passed"])

        controller = QCController(mock_service)

        mock_result = Mock(spec=AnalysisResult)
        passed, grade, reasons = controller.evaluate_result(mock_result)

        assert passed is True
        assert grade == "good"
        assert reasons == ["All checks passed"]
        mock_service.evaluate_analysis.assert_called_once_with(mock_result)

    def test_get_current_profile(self):
        """Test getting current QC profile"""
        mock_service = Mock(spec=QualityControlService)
        mock_profile = Mock()
        mock_service.get_current_profile.return_value = mock_profile

        controller = QCController(mock_service)

        profile = controller.get_current_profile()

        assert profile == mock_profile
        mock_service.get_current_profile.assert_called_once()

    def test_set_bread_type(self):
        """Test setting bread type"""
        mock_service = Mock(spec=QualityControlService)
        mock_service.set_bread_type.return_value = True

        controller = QCController(mock_service)

        result = controller.set_bread_type("sourdough")

        assert result is True
        mock_service.set_bread_type.assert_called_once_with("sourdough")


class TestPredictionController:
    """Test cases for PredictionController"""

    def test_init(self):
        """Test initialization"""
        mock_service = Mock(spec=PredictionService)
        mock_callback = Mock()

        controller = PredictionController(mock_service, mock_callback)

        assert controller.prediction_service == mock_service
        assert controller.view_callback == mock_callback

    def test_predict_porosity(self):
        """Test porosity prediction"""
        mock_service = Mock(spec=PredictionService)
        mock_service.predict_porosity.return_value = (75.5, 0.85)

        controller = PredictionController(mock_service)

        recipe_data = {
            "ingredients": {"flour": 500, "water": 350},
            "mixing_time_min": 10,
            "proof_time_min": 120,
            "oven_temp_c": 220,
            "cooking_vessel": "dutch oven",
            "cook_time_min": 45
        }

        prediction, confidence = controller.predict_porosity(recipe_data)

        assert prediction == 75.5
        assert confidence == 0.85
        mock_service.predict_porosity.assert_called_once_with(recipe_data)

    def test_predict_porosity_error(self):
        """Test porosity prediction with error"""
        mock_service = Mock(spec=PredictionService)
        mock_service.predict_porosity.side_effect = ValueError("Invalid data")

        controller = PredictionController(mock_service)

        recipe_data = {"invalid": "data"}
        prediction, confidence = controller.predict_porosity(recipe_data)

        assert prediction is None
        assert confidence is None


class TestDefectController:
    """Test cases for DefectController"""

    def test_init(self):
        """Test initialization"""
        mock_service = Mock(spec=DefectService)
        mock_callback = Mock()

        controller = DefectController(mock_service, mock_callback)

        assert controller.defect_service == mock_service
        assert controller.view_callback == mock_callback

    def test_detect_defects(self):
        """Test defect detection"""
        mock_service = Mock(spec=DefectService)
        mock_defects = {"severity_score": 25, "defects": []}
        mock_service.detect_defects.return_value = mock_defects

        controller = DefectController(mock_service)

        defects = controller.detect_defects("/path/to/image.jpg")

        assert defects == mock_defects
        mock_service.detect_defects.assert_called_once_with("/path/to/image.jpg")


class TestExportController:
    """Test cases for ExportController"""

    def test_init(self):
        """Test initialization"""
        mock_service = Mock(spec=ExportService)
        mock_callback = Mock()

        controller = ExportController(mock_service, mock_callback)

        assert controller.export_service == mock_service
        assert controller.view_callback == mock_callback

    def test_export_csv(self):
        """Test CSV export"""
        mock_service = Mock(spec=ExportService)
        mock_service.export_to_csv.return_value = True

        controller = ExportController(mock_service)

        results = [Mock(spec=AnalysisResult)]
        result = controller.export_csv(results, "/path/to/export.csv")

        assert result is True
        mock_service.export_to_csv.assert_called_once_with(results, "/path/to/export.csv")

    def test_export_excel(self):
        """Test Excel export"""
        mock_service = Mock(spec=ExportService)
        mock_service.export_to_excel.return_value = True

        controller = ExportController(mock_service)

        results = [Mock(spec=AnalysisResult)]
        result = controller.export_excel(results, "/path/to/export.xlsx")

        assert result is True
        mock_service.export_to_excel.assert_called_once_with(results, "/path/to/export.xlsx")