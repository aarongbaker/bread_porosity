"""
Analysis Service
Business logic for bread porosity analysis
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional

from models.analysis_result import AnalysisResult
from repositories.results_repository import ResultsRepository
from utils.exceptions import AnalysisError
from utils.logger import get_logger
from utils.validators import Validator

# Import existing modules
from imaging_pipeline import ImagingPipeline
from metrics import PorometryMetrics
from visualization import VisualizationEngine

logger = get_logger(__name__)


class AnalysisService:
    """
    Service for analyzing bread porosity from images.

    Orchestrates the complete analysis pipeline:
    1. Image processing (pipeline)
    2. Metrics computation
    3. Result storage
    4. Visualization generation
    """

    def __init__(self,
                 results_repo: Optional[ResultsRepository] = None,
                 output_dir: str = "./output"):
        """
        Initialize the analysis service.

        Args:
            results_repo: Repository for storing results (optional)
            output_dir: Default output directory
        """
        self.results_repo = results_repo or ResultsRepository()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_image(self,
                     image_path: str,
                     pixel_size_mm: float = 0.1,
                     threshold_method: str = "otsu",
                     normalize_method: str = "clahe",
                     output_dir: Optional[str] = None,
                     save_results: bool = True,
                     generate_visualizations: bool = True) -> AnalysisResult:
        """
        Analyze a single bread image for porosity.

        Args:
            image_path: Path to the bread image file
            pixel_size_mm: Size of one pixel in millimeters
            threshold_method: Thresholding method ("otsu" or "adaptive")
            normalize_method: Normalization method ("clahe", "morphology", "gaussian")
            output_dir: Optional output directory override for this analysis
            save_results: Whether to save results to repository
            generate_visualizations: Whether to create output images

        Returns:
            AnalysisResult object with all computed metrics

        Raises:
            AnalysisError: If analysis fails
        """
        start_time = time.time()

        try:
            # Validate inputs
            self._validate_inputs(image_path, pixel_size_mm, threshold_method, normalize_method)

            logger.info(f"Starting analysis: {image_path}")

            # Initialize components
            pipeline = ImagingPipeline(verbose=False)
            metrics_computer = PorometryMetrics(pixel_size_mm=pixel_size_mm, verbose=False)

            # Process image through pipeline
            image = pipeline.read_image(image_path)
            gray = pipeline.to_grayscale()
            normalized = pipeline.normalize_illumination(method=normalize_method)
            roi_mask, roi_stats = pipeline.find_bread_roi(threshold_value=30)
            binary_holes = pipeline.threshold_holes(method=threshold_method)
            cleaned = pipeline.morphological_cleanup(remove_small_holes=50, fill_small_gaps=50)

            # Compute metrics
            metrics = metrics_computer.compute_all_metrics(cleaned, roi_mask, normalized)

            # Create AnalysisResult object
            result = AnalysisResult(
                image_path=image_path,
                image_filename=Path(image_path).name,
                porosity_percent=metrics['porosity_percent'],
                hole_count_total=metrics['hole_count_total'],
                hole_diameter_mean_mm=metrics['hole_diameter_mean_mm'],
                hole_diameter_std_mm=metrics['hole_diameter_std_mm'],
                hole_diameter_min_mm=metrics['hole_diameter_min_mm'],
                hole_diameter_max_mm=metrics['hole_diameter_max_mm'],
                holes_per_cm2=metrics['holes_per_cm2'],
                anisotropy_ratio=metrics['anisotropy_ratio'],
                orientation_mean_deg=metrics['orientation_mean_deg'],
                uniformity_score=metrics['uniformity_score'],
                hole_size_distribution_data=metrics.get('hole_size_distribution_data', {}),
                pixel_size_mm=pixel_size_mm,
                threshold_method=threshold_method,
                normalization_method=normalize_method,
                processing_time_sec=time.time() - start_time
            )

            # Generate visualizations if requested
            if generate_visualizations:
                active_output_dir = Path(output_dir) if output_dir else self.output_dir
                active_output_dir.mkdir(parents=True, exist_ok=True)
                visualizer = VisualizationEngine(output_dir=str(active_output_dir))
                images_dict = pipeline.get_processing_images()

                result.output_comparison_path = str(visualizer.create_comparison_image(images_dict))
                result.output_distribution_path = str(visualizer.create_hole_distribution_plots(metrics))
                result.output_annotated_path = str(visualizer.create_annotated_image(image, cleaned, roi_mask, metrics))

                # Save metrics JSON
                metrics_json_path = visualizer.save_metrics_json(metrics)
                # Note: We don't store this path in result since it's redundant with the metrics

            # Save to repository if requested
            if save_results and self.results_repo:
                self.results_repo.save(result)

            logger.info(
                f"Analysis completed in {result.processing_time_sec:.2f}s for {result.image_filename}"
            )
            return result

        except Exception as e:
            logger.error(f"Analysis failed for {image_path}: {e}")
            raise AnalysisError(f"Failed to analyze image {image_path}: {e}") from e

    def analyze_multiple_images(self,
                               image_paths: list[str],
                               pixel_size_mm: float = 0.1,
                               threshold_method: str = "otsu",
                               normalize_method: str = "clahe",
                               output_dir: Optional[str] = None,
                               save_results: bool = True,
                               generate_visualizations: bool = True) -> list[AnalysisResult]:
        """
        Analyze multiple bread images.

        Args:
            image_paths: List of paths to bread images
            pixel_size_mm: Size of one pixel in millimeters
            threshold_method: Thresholding method
            normalize_method: Normalization method
            output_dir: Optional output directory override for this batch
            save_results: Whether to save results
            generate_visualizations: Whether to create outputs

        Returns:
            List of AnalysisResult objects
        """
        results = []
        for path in image_paths:
            try:
                result = self.analyze_image(
                    path, pixel_size_mm, threshold_method, normalize_method,
                    output_dir, save_results, generate_visualizations
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Skipping {path} due to error: {e}")
                continue

        logger.info(f"Batch analysis complete: {len(results)}/{len(image_paths)} images processed")
        return results

    def _validate_inputs(self,
                        image_path: str,
                        pixel_size_mm: float,
                        threshold_method: str,
                        normalize_method: str) -> None:
        """
        Validate analysis inputs.

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate image path
        is_valid, error_msg = Validator.validate_image_path(image_path)
        if not is_valid:
            raise ValueError(error_msg)

        # Validate pixel size
        is_valid, error_msg = Validator.validate_pixel_size(pixel_size_mm)
        if not is_valid:
            raise ValueError(error_msg)

        # Validate threshold method
        is_valid, error_msg = Validator.validate_threshold_method(threshold_method)
        if not is_valid:
            raise ValueError(error_msg)

        # Validate normalization method
        is_valid, error_msg = Validator.validate_normalize_method(normalize_method)
        if not is_valid:
            raise ValueError(error_msg)
