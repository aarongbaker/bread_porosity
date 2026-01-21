"""
Unit tests for GUI components
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from gui.components.image_preview import ImagePreview
from gui.components.results_display import ResultsDisplay


@pytest.mark.gui
class TestImagePreview:
    """Test cases for ImagePreview component"""

    @patch('gui.components.image_preview.ttk.Frame')
    def test_init(self, mock_frame):
        """Test initialization"""
        mock_parent = Mock()
        mock_controller = Mock()

        component = ImagePreview(mock_parent, mock_controller, width=500, height=400)

        # Verify initialization
        assert component.controller == mock_controller
        assert component.width == 500
        assert component.height == 400
        assert component.original_image is None
        assert component.display_image is None
        assert component.zoom_factor == 1.0
        assert component.pan_x == 0
        assert component.pan_y == 0

    @patch('gui.components.image_preview.ttk.Frame')
    @patch('gui.components.image_preview.Image')
    def test_load_image(self, mock_image_class, mock_frame):
        """Test loading an image"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        # Mock PIL Image
        mock_image = Mock()
        mock_image_class.open.return_value = mock_image
        mock_image.size = (800, 600)

        # Load image
        component.load_image("/path/to/test.jpg")

        assert component.image_path == "/path/to/test.jpg"
        assert component.original_image == mock_image
        mock_image_class.open.assert_called_once_with("/path/to/test.jpg")

    @patch('gui.components.image_preview.ttk.Frame')
    @patch('gui.components.image_preview.Image')
    def test_load_image_invalid_path(self, mock_image_class, mock_frame):
        """Test loading image with invalid path"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        # Mock PIL Image to raise exception
        mock_image_class.open.side_effect = FileNotFoundError("File not found")

        # Load image
        component.load_image("/invalid/path.jpg")

        assert component.image_path is None
        assert component.original_image is None

    @patch('gui.components.image_preview.ttk.Frame')
    def test_zoom_in(self, mock_frame):
        """Test zoom in functionality"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        initial_zoom = component.zoom_factor
        component.zoom_in()

        assert component.zoom_factor > initial_zoom

    @patch('gui.components.image_preview.ttk.Frame')
    def test_zoom_out(self, mock_frame):
        """Test zoom out functionality"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        # Set initial zoom > 1
        component.zoom_factor = 2.0
        component.zoom_out()

        assert component.zoom_factor < 2.0

    @patch('gui.components.image_preview.ttk.Frame')
    def test_zoom_out_minimum(self, mock_frame):
        """Test zoom out doesn't go below minimum"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        # Set zoom to minimum
        component.zoom_factor = 0.1
        component.zoom_out()

        assert component.zoom_factor >= 0.1

    @patch('gui.components.image_preview.ttk.Frame')
    def test_reset_zoom(self, mock_frame):
        """Test reset zoom functionality"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        component.zoom_factor = 2.5
        component.pan_x = 100
        component.pan_y = 50

        component.reset_zoom()

        assert component.zoom_factor == 1.0
        assert component.pan_x == 0
        assert component.pan_y == 0

    @patch('gui.components.image_preview.ttk.Frame')
    def test_get_image_info_no_image(self, mock_frame):
        """Test getting image info when no image is loaded"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        info = component.get_image_info()

        assert info["loaded"] is False
        assert info["path"] is None
        assert info["size"] is None

    @patch('gui.components.image_preview.ttk.Frame')
    @patch('gui.components.image_preview.Image')
    def test_get_image_info_with_image(self, mock_image_class, mock_frame):
        """Test getting image info when image is loaded"""
        mock_parent = Mock()
        component = ImagePreview(mock_parent)

        # Mock PIL Image
        mock_image = Mock()
        mock_image_class.open.return_value = mock_image
        mock_image.size = (1024, 768)

        component.load_image("/path/to/test.jpg")
        info = component.get_image_info()

        assert info["loaded"] is True
        assert info["path"] == "/path/to/test.jpg"
        assert info["size"] == (1024, 768)


@pytest.mark.gui
class TestResultsDisplay:
    """Test cases for ResultsDisplay component"""

    @patch('gui.components.results_display.ttk.Frame')
    def test_init(self, mock_frame):
        """Test initialization"""
        mock_parent = Mock()
        mock_controller = Mock()

        component = ResultsDisplay(mock_parent, mock_controller)

        assert component.controller == mock_controller
        assert component.current_result is None

    @patch('gui.components.results_display.ttk.Frame')
    def test_display_result(self, mock_frame):
        """Test displaying analysis result"""
        mock_parent = Mock()
        component = ResultsDisplay(mock_parent)

        # Mock analysis result
        mock_result = Mock()
        mock_result.porosity_percent = 65.5
        mock_result.hole_count_total = 150
        mock_result.uniformity_score = 0.85
        mock_result.qc_passed = True
        mock_result.quality_grade = "good"

        component.display_result(mock_result)

        assert component.current_result == mock_result

    @patch('gui.components.results_display.ttk.Frame')
    def test_display_result_none(self, mock_frame):
        """Test displaying None result (clear display)"""
        mock_parent = Mock()
        component = ResultsDisplay(mock_parent)

        # Set a result first
        mock_result = Mock()
        component.current_result = mock_result

        # Clear display
        component.display_result(None)

        assert component.current_result is None

    @patch('gui.components.results_display.ttk.Frame')
    def test_get_display_data_no_result(self, mock_frame):
        """Test getting display data when no result"""
        mock_parent = Mock()
        component = ResultsDisplay(mock_parent)

        data = component.get_display_data()

        assert data["has_result"] is False
        assert data["porosity_percent"] == "N/A"

    @patch('gui.components.results_display.ttk.Frame')
    def test_get_display_data_with_result(self, mock_frame):
        """Test getting display data when result exists"""
        mock_parent = Mock()
        component = ResultsDisplay(mock_parent)

        # Mock analysis result
        mock_result = Mock()
        mock_result.porosity_percent = 65.5
        mock_result.hole_count_total = 150
        mock_result.uniformity_score = 0.85
        mock_result.qc_passed = True
        mock_result.quality_grade = "good"

        component.current_result = mock_result
        data = component.get_display_data()

        assert data["has_result"] is True
        assert data["porosity_percent"] == "65.5%"
        assert data["hole_count_total"] == "150"
        assert data["uniformity_score"] == "0.85"
        assert data["qc_passed"] is True
        assert data["quality_grade"] == "good"

    @patch('gui.components.results_display.ttk.Frame')
    def test_format_metric(self, mock_frame):
        """Test metric formatting"""
        mock_parent = Mock()
        component = ResultsDisplay(mock_parent)

        # Test percentage formatting
        assert component._format_metric(65.5, "percent") == "65.5%"
        assert component._format_metric(None, "percent") == "N/A"

        # Test integer formatting
        assert component._format_metric(150, "int") == "150"
        assert component._format_metric(None, "int") == "N/A"

        # Test float formatting
        assert component._format_metric(0.85, "float") == "0.85"
        assert component._format_metric(None, "float") == "N/A"

        # Test default formatting
        assert component._format_metric("test", "unknown") == "test"