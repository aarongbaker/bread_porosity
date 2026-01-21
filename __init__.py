"""
Bread Porosity Analysis Tool
Standardized measurement of bread structure using transmitted light and image processing.

Main modules:
- imaging_pipeline: Image processing pipeline
- metrics: Porosity and structure metrics computation
- visualization: Output generation and visualization
- calibration: Standardization and calibration utilities
- analyze: Main analysis script and batch processing

Quick start:
    from services.analysis_service import AnalysisService
    result = AnalysisService().analyze_image("bread.jpg", pixel_size_mm=0.1)
"""

__version__ = "1.0"
__author__ = "Bread Porosity Analysis Team"

from .imaging_pipeline import ImagingPipeline
from .metrics import PorometryMetrics, format_metrics_report
from .visualization import VisualizationEngine
from .calibration import ReferenceCalibration, CameraSetupHelper, SetupChecklist

__all__ = [
    'ImagingPipeline',
    'PorometryMetrics',
    'format_metrics_report',
    'VisualizationEngine',
    'ReferenceCalibration',
    'CameraSetupHelper',
    'SetupChecklist',
]
