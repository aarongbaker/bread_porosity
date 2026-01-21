"""
Metrics computation for bread porosity analysis.
Calculates porosity, hole size distribution, anisotropy, uniformity, etc.
"""

import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from scipy import ndimage
from scipy.stats import skew

logger = logging.getLogger(__name__)


class PorometryMetrics:
    """Compute quantitative metrics from binary hole segmentation."""
    
    def __init__(self, pixel_size_mm: float = 0.1, verbose: bool = False):
        """
        Args:
            pixel_size_mm: Size of one pixel in mm (for converting pixel measurements to real units)
            verbose: Print progress messages
        """
        self.pixel_size_mm = pixel_size_mm
        self.verbose = verbose
        self.metrics = {}
    
    def compute_all_metrics(self, binary_holes: np.ndarray, roi_mask: np.ndarray, 
                           normalized_image: np.ndarray) -> Dict[str, Any]:
        """
        Compute all porosity and crumb metrics.
        
        Args:
            binary_holes: Binary image where 255 = holes, 0 = crumb
            roi_mask: Binary mask of bread ROI
            normalized_image: Normalized grayscale image (for uniformity analysis)
        
        Returns:
            Dictionary of all metrics
        """
        if binary_holes is None or roi_mask is None or normalized_image is None:
            logger.error("Missing required input images for metrics computation")
            raise ValueError("All input images (binary_holes, roi_mask, normalized_image) must be provided")
        
        try:
            self.metrics = {}
            
            # Basic porosity
            self.metrics.update(self._compute_porosity(binary_holes, roi_mask))
            
            # Hole-level metrics (size, count, distribution)
            self.metrics.update(self._compute_hole_metrics(binary_holes, roi_mask))
            
            # Shape and orientation metrics
            self.metrics.update(self._compute_anisotropy(binary_holes))
            
            # Crumb uniformity metrics
            self.metrics.update(self._compute_crumb_uniformity(normalized_image, roi_mask))
            
            logger.info(f"Computed metrics for porosity={self.metrics.get('porosity_percent', 0):.2f}%")
        except Exception as e:
            logger.error(f"Error computing metrics: {e}")
            raise
        
        return self.metrics
    
    def _compute_porosity(self, binary_holes: np.ndarray, roi_mask: np.ndarray) -> Dict[str, float]:
        """Basic porosity = hole_area / roi_area."""
        try:
            hole_pixels = cv2.countNonZero(binary_holes)
            roi_pixels = cv2.countNonZero(roi_mask)
            
            if roi_pixels == 0:
                logger.error("ROI has no pixels - invalid bread slice detection")
                raise ValueError("ROI has no pixels - bread slice may not be properly detected")
            
            porosity_fraction = hole_pixels / roi_pixels
            porosity_percent = porosity_fraction * 100
            
            logger.debug(f"Porosity: {porosity_percent:.2f}%")
            if self.verbose:
                print(f"✓ Porosity: {porosity_percent:.2f}%")
            
            return {
                "porosity_fraction": porosity_fraction,
                "porosity_percent": porosity_percent,
                "hole_pixels": hole_pixels,
                "roi_pixels": roi_pixels,
                "crumb_pixels": roi_pixels - hole_pixels,
            }
        except Exception as e:
            logger.error(f"Error computing porosity: {e}")
            raise
    
    def _compute_hole_metrics(self, binary_holes: np.ndarray, roi_mask: np.ndarray) -> Dict[str, Any]:
        """Compute hole size distribution, count, mean size, etc."""
        # Label connected components (non-zero pixels are holes)
        labeled_holes, num_holes = ndimage.label(binary_holes)
        
        if num_holes == 0:
            return {
                "num_holes": 0,
                "hole_count_total": 0,
                "mean_hole_area_pixels": 0,
                "mean_hole_area_mm2": 0,
                "mean_hole_diameter_mm": 0,
                "hole_diameter_mean_mm": 0,
                "hole_diameter_std_mm": 0,
                "hole_diameter_min_mm": 0,
                "hole_diameter_max_mm": 0,
                "largest_hole_area_pixels": 0,
                "largest_hole_diameter_mm": 0,
                "smallest_hole_area_pixels": 0,
                "smallest_hole_diameter_mm": 0,
                "holes_per_cm2": 0,
                "hole_area_distribution": [],
                "hole_area_std_pixels": 0,
                "hole_area_std_mm2": 0,
                "hole_size_distribution_data": {
                    "hole_area_pixels": [],
                    "hole_diameter_mm": [],
                },
            }
        
        # Get size of each hole (count pixels, not summed intensity)
        hole_areas = ndimage.sum(binary_holes > 0, labeled_holes, range(1, num_holes + 1))
        hole_areas = np.asarray(hole_areas, dtype=float)
        hole_areas = hole_areas[hole_areas > 0]
        
        roi_area_mm2 = cv2.countNonZero(roi_mask) * (self.pixel_size_mm ** 2)
        
        # Convert areas to mm²
        hole_areas_mm2 = hole_areas * (self.pixel_size_mm ** 2)
        
        # Convert to diameter (assuming circular holes: A = π*r² → d = 2*sqrt(A/π))
        hole_diameters_mm = 2 * np.sqrt(hole_areas_mm2 / np.pi)
        
        mean_diameter_mm = float(np.mean(hole_diameters_mm))
        std_diameter_mm = float(np.std(hole_diameters_mm))
        min_diameter_mm = float(np.min(hole_diameters_mm))
        max_diameter_mm = float(np.max(hole_diameters_mm))

        metrics = {
            "num_holes": int(num_holes),
            "hole_count_total": int(num_holes),
            "mean_hole_area_pixels": float(np.mean(hole_areas)),
            "mean_hole_area_mm2": float(np.mean(hole_areas_mm2)),
            "mean_hole_diameter_mm": mean_diameter_mm,
            "hole_diameter_mean_mm": mean_diameter_mm,
            "hole_diameter_std_mm": std_diameter_mm,
            "hole_diameter_min_mm": min_diameter_mm,
            "hole_diameter_max_mm": max_diameter_mm,
            "largest_hole_area_pixels": float(np.max(hole_areas)),
            "largest_hole_area_mm2": float(np.max(hole_areas_mm2)),
            "largest_hole_diameter_mm": max_diameter_mm,
            "smallest_hole_area_pixels": float(np.min(hole_areas)),
            "smallest_hole_diameter_mm": min_diameter_mm,
            "hole_area_std_pixels": float(np.std(hole_areas)),
            "hole_area_std_mm2": float(np.std(hole_areas_mm2)),
            "holes_per_cm2": float(num_holes / (roi_area_mm2 / 100)),
            "hole_area_distribution": hole_areas.tolist(),
            "hole_area_cv": float(np.std(hole_areas) / np.mean(hole_areas)) if np.mean(hole_areas) > 0 else 0,
            "hole_size_distribution_data": {
                "hole_area_pixels": hole_areas.tolist(),
                "hole_diameter_mm": hole_diameters_mm.tolist(),
            },
        }
        
        if self.verbose:
            print(f"✓ Hole analysis: {metrics['num_holes']} holes, "
                  f"mean diameter {metrics['mean_hole_diameter_mm']:.2f} mm, "
                  f"{metrics['holes_per_cm2']:.1f} holes/cm²")
        
        return metrics
    
    def _compute_anisotropy(self, binary_holes: np.ndarray) -> Dict[str, float]:
        """
        Compute anisotropy / orientation metrics.
        Uses PCA on hole centroids and major/minor axes of holes.
        """
        labeled_holes, num_holes = ndimage.label(binary_holes)
        
        if num_holes < 2:
            return {
                "mean_aspect_ratio": 1.0,
                "aspect_ratio_std": 0.0,
                "mean_orientation_deg": 0.0,
                "orientation_entropy": 0.0,
            }
        
        aspect_ratios = []
        orientations = []
        
        for i in range(1, num_holes + 1):
            hole_mask = (labeled_holes == i).astype(np.uint8) * 255
            
            # Get contour and fit ellipse
            contours, _ = cv2.findContours(hole_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue
            
            contour = contours[0]
            if len(contour) < 5:
                continue
            
            ellipse = cv2.fitEllipse(contour)
            (cx, cy), (width, height), angle = ellipse
            
            # Aspect ratio (major/minor axis)
            aspect_ratio = max(width, height) / (min(width, height) + 1e-6)
            aspect_ratios.append(aspect_ratio)
            
            # Orientation angle (0-180°)
            orientations.append(angle % 180)
        
        if not aspect_ratios:
            return {
                "mean_aspect_ratio": 1.0,
                "aspect_ratio_std": 0.0,
                "mean_orientation_deg": 0.0,
                "orientation_entropy": 0.0,
            }
        
        # Compute orientation entropy (how dispersed are hole orientations)
        hist, _ = np.histogram(orientations, bins=18, range=(0, 180))
        hist = hist / np.sum(hist)
        orientation_entropy = -np.sum(hist * np.log2(hist + 1e-10))
        
        mean_aspect_ratio = float(np.mean(aspect_ratios))
        mean_orientation_deg = float(np.mean(orientations))
        metrics = {
            "mean_aspect_ratio": mean_aspect_ratio,
            "anisotropy_ratio": mean_aspect_ratio,
            "aspect_ratio_std": float(np.std(aspect_ratios)),
            "mean_orientation_deg": mean_orientation_deg,
            "orientation_mean_deg": mean_orientation_deg,
            "orientation_entropy": float(orientation_entropy),  # 0=aligned, 4.17=random
        }
        
        if self.verbose:
            print(f"✓ Anisotropy: mean aspect ratio {metrics['mean_aspect_ratio']:.2f}, "
                  f"orientation entropy {metrics['orientation_entropy']:.2f}")
        
        return metrics
    
    def _compute_crumb_uniformity(self, normalized_image: np.ndarray, roi_mask: np.ndarray) -> Dict[str, float]:
        """
        Compute crumb cell uniformity metrics using brightness distribution.
        High variance = non-uniform crumb structure.
        """
        # Get only ROI region
        crumb_region = cv2.bitwise_and(normalized_image, normalized_image, mask=roi_mask)
        roi_pixels = crumb_region[roi_mask > 0]
        
        if len(roi_pixels) == 0:
            return {
                "crumb_brightness_mean": 0,
                "crumb_brightness_std": 0,
                "crumb_brightness_cv": 0,
                "crumb_brightness_skewness": 0,
                "uniformity_score": 0,
            }
        
        mean_brightness = float(np.mean(roi_pixels))
        std_brightness = float(np.std(roi_pixels))
        cv_brightness = std_brightness / (mean_brightness + 1e-6)
        skewness_brightness = float(skew(roi_pixels))
        
        uniformity_score = max(0.0, min(1.0, 1.0 - cv_brightness))
        metrics = {
            "crumb_brightness_mean": mean_brightness,
            "crumb_brightness_std": std_brightness,
            "crumb_brightness_cv": cv_brightness,  # Coefficient of variation (0=uniform)
            "crumb_brightness_skewness": skewness_brightness,
            "uniformity_score": uniformity_score,
        }
        
        if self.verbose:
            print(f"✓ Crumb uniformity: CV={cv_brightness:.3f}, skewness={skewness_brightness:.2f}")
        
        return metrics


def format_metrics_report(metrics: Dict[str, Any]) -> str:
    """Format metrics dictionary as a human-readable report."""
    report = []
    report.append("=" * 60)
    report.append("BREAD POROSITY ANALYSIS REPORT")
    report.append("=" * 60)
    
    report.append("\n[BASIC POROSITY]")
    report.append(f"  Porosity: {metrics.get('porosity_percent', 0):.2f}%")
    report.append(f"  Hole pixels: {metrics.get('hole_pixels', 0)}")
    report.append(f"  Crumb pixels: {metrics.get('crumb_pixels', 0)}")
    
    report.append("\n[HOLE METRICS]")
    report.append(f"  Number of holes: {metrics.get('num_holes', 0)}")
    report.append(f"  Mean hole diameter: {metrics.get('mean_hole_diameter_mm', 0):.2f} mm")
    report.append(f"  Largest hole diameter: {metrics.get('largest_hole_diameter_mm', 0):.2f} mm")
    report.append(f"  Smallest hole diameter: {metrics.get('smallest_hole_diameter_mm', 0):.2f} mm")
    report.append(f"  Hole diameter std: {metrics.get('hole_diameter_std_mm', 0):.2f} mm")
    report.append(f"  Coefficient of variation (size): {metrics.get('hole_area_cv', 0):.3f}")
    report.append(f"  Holes per cm²: {metrics.get('holes_per_cm2', 0):.1f}")
    
    report.append("\n[ANISOTROPY & DIRECTIONALITY]")
    report.append(f"  Mean aspect ratio: {metrics.get('mean_aspect_ratio', 1):.2f}")
    report.append(f"  Aspect ratio std: {metrics.get('aspect_ratio_std', 0):.2f}")
    report.append(f"  Mean orientation: {metrics.get('mean_orientation_deg', 0):.1f}°")
    report.append(f"  Orientation entropy: {metrics.get('orientation_entropy', 0):.2f} / 4.17")
    if metrics.get('orientation_entropy', 0) < 1.5:
        report.append("    → Holes are highly aligned/anisotropic")
    elif metrics.get('orientation_entropy', 0) > 3.5:
        report.append("    → Holes are randomly oriented/isotropic")
    
    report.append("\n[CRUMB UNIFORMITY]")
    report.append(f"  Mean brightness: {metrics.get('crumb_brightness_mean', 0):.1f}")
    report.append(f"  Brightness std: {metrics.get('crumb_brightness_std', 0):.1f}")
    report.append(f"  Coefficient of variation: {metrics.get('crumb_brightness_cv', 0):.3f}")
    report.append(f"  Brightness skewness: {metrics.get('crumb_brightness_skewness', 0):.2f}")
    
    report.append("\n" + "=" * 60)
    
    return "\n".join(report)
