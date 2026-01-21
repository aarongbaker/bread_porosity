"""
Analysis Controller
Handles image analysis workflow and coordinates with AnalysisService
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import threading
import shutil

from services.analysis_service import AnalysisService
from models.analysis_result import AnalysisResult
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisController:
    """Controller for image analysis operations"""

    def __init__(self, analysis_service: AnalysisService, view_callback: Optional[Callable] = None):
        """
        Initialize analysis controller

        Args:
            analysis_service: The analysis service to use
            view_callback: Callback to update the view (optional)
        """
        self.analysis_service = analysis_service
        self.view_callback = view_callback
        self.current_result: Optional[AnalysisResult] = None
        self.is_analyzing = False

    def analyze_single_image(
        self,
        image_path: str,
        pixel_size_mm: float = 0.1,
        threshold_method: str = "otsu",
        normalize_method: str = "clahe",
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> Optional[AnalysisResult]:
        """
        Analyze a single bread image

        Args:
            image_path: Path to the image file
            pixel_size_mm: Pixel size in millimeters
            threshold_method: Thresholding method
            normalize_method: Normalization method
            output_dir: Output directory for results
            progress_callback: Callback for progress updates
            completion_callback: Callback when analysis completes

        Returns:
            AnalysisResult if successful, None if failed
        """
        if self.is_analyzing:
            logger.warning("Analysis already in progress")
            return None

        try:
            self.is_analyzing = True

            if progress_callback:
                progress_callback("Starting analysis...", "warning")

            # Perform analysis using service
            result = self.analysis_service.analyze_image(
                image_path=image_path,
                pixel_size_mm=pixel_size_mm,
                threshold_method=threshold_method,
                normalize_method=normalize_method,
                output_dir=output_dir
            )

            self.current_result = result

            if progress_callback:
                progress_callback("Analysis complete!", "success")

            if completion_callback:
                completion_callback(result)

            if self.view_callback:
                self.view_callback('analysis_completed', result)

            # Log success
            porosity = result.porosity_percent
            hole_count = result.hole_count_total
            logger.info(f"Analysis completed: {porosity:.1f}% porosity, {hole_count} holes")

            return result

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)

            if progress_callback:
                progress_callback("Analysis failed", "error")

            if self.view_callback:
                self.view_callback('analysis_failed', error_msg)

            return None

        finally:
            self.is_analyzing = False

    def analyze_single_image_async(
        self,
        image_path: str,
        pixel_size_mm: float = 0.1,
        threshold_method: str = "otsu",
        normalize_method: str = "clahe",
        output_dir: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> None:
        """
        Analyze a single image asynchronously

        Args:
            image_path: Path to the image file
            pixel_size_mm: Pixel size in millimeters
            threshold_method: Thresholding method
            normalize_method: Normalization method
            output_dir: Output directory for results
            progress_callback: Callback for progress updates
            completion_callback: Callback when analysis completes
        """
        def analysis_thread():
            result = self.analyze_single_image(
                image_path=image_path,
                pixel_size_mm=pixel_size_mm,
                threshold_method=threshold_method,
                normalize_method=normalize_method,
                output_dir=output_dir,
                progress_callback=progress_callback,
                completion_callback=completion_callback
            )

            if result and completion_callback:
                # Schedule callback on main thread
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, lambda: completion_callback(result))

        thread = threading.Thread(target=analysis_thread, daemon=True)
        thread.start()

    def analyze_loaf_images(
        self,
        loaf_name: str,
        image_paths: list,
        pixel_size_mm: float = 0.1,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze multiple images from a loaf

        Args:
            loaf_name: Name of the loaf
            image_paths: List of image paths
            pixel_size_mm: Pixel size in millimeters
            progress_callback: Callback for progress updates
            completion_callback: Callback when analysis completes

        Returns:
            Loaf analysis results if successful, None if failed
        """
        if self.is_analyzing:
            logger.warning("Analysis already in progress")
            return None

        try:
            self.is_analyzing = True

            if progress_callback:
                progress_callback(f"Analyzing loaf: {loaf_name}...", "warning")

            # For now, analyze each image individually
            # TODO: Implement proper loaf analysis in service layer
            results = []
            for i, image_path in enumerate(image_paths):
                if progress_callback:
                    progress_callback(f"Analyzing slice {i+1}/{len(image_paths)}...", "warning")

                result = self.analyze_single_image(
                    image_path=image_path,
                    pixel_size_mm=pixel_size_mm,
                    progress_callback=None,  # Don't show individual progress
                    completion_callback=None
                )

                if result:
                    results.append(result)

            if not results:
                raise ValueError("No images could be analyzed")

            # Calculate loaf statistics
            loaf_result = self._calculate_loaf_statistics(loaf_name, results)

            if progress_callback:
                progress_callback("Loaf analysis complete!", "success")

            if completion_callback:
                completion_callback(loaf_result)

            logger.info(f"Loaf analysis completed: {len(results)} slices analyzed")
            return loaf_result

        except Exception as e:
            error_msg = f"Loaf analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)

            if progress_callback:
                progress_callback("Loaf analysis failed", "error")

            return None

        finally:
            self.is_analyzing = False

    def _calculate_loaf_statistics(self, loaf_name: str, results: list) -> Dict[str, Any]:
        """Calculate statistics for a loaf from individual slice results"""
        porosities = [r.porosity_percent for r in results]
        hole_counts = [r.hole_count_total for r in results]
        diameters = [r.hole_diameter_mean_mm for r in results]

        return {
            'loaf_name': loaf_name,
            'num_slices': len(results),
            'porosity': {
                'mean': sum(porosities) / len(porosities),
                'std': (sum((x - sum(porosities)/len(porosities))**2 for x in porosities) / len(porosities))**0.5,
                'min': min(porosities),
                'max': max(porosities),
                'range': max(porosities) - min(porosities)
            },
            'holes': {
                'mean_count': sum(hole_counts) / len(hole_counts),
                'mean_diameter_mm': sum(diameters) / len(diameters)
            },
            'shape': {
                'mean_aspect_ratio': sum(r.anisotropy_ratio for r in results) / len(results)
            },
            'slices': [
                {
                    'slice': f"{i+1:02d}",
                    'porosity': r.porosity_percent,
                    'num_holes': r.hole_count_total,
                    'mean_diameter_mm': r.hole_diameter_mean_mm
                }
                for i, r in enumerate(results)
            ]
        }

    def get_current_result(self) -> Optional[AnalysisResult]:
        """Get the current analysis result"""
        return self.current_result

    def validate_image_quality(self, image_path: str) -> bool:
        """
        Validate image quality before analysis

        Args:
            image_path: Path to the image file

        Returns:
            True if image quality is acceptable
        """
        # TODO: Implement image quality validation
        # For now, just check if file exists and is readable
        path = Path(image_path)
        return path.exists() and path.is_file()

    def move_image_to_processed(self, image_path: str, processed_dir: str) -> bool:
        """
        Move analyzed image to processed directory

        Args:
            image_path: Source image path
            processed_dir: Processed directory path

        Returns:
            True if move was successful
        """
        try:
            source = Path(image_path)
            destination = Path(processed_dir) / source.name
            shutil.move(str(source), str(destination))
            return True
        except Exception as e:
            logger.error(f"Failed to move image to processed: {e}")
            return False
