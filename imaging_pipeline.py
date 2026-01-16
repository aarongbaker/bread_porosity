"""
Core image processing pipeline for bread porosity analysis.
Implements the classical CV approach: read → grayscale → normalize → threshold → cleanup → metrics.
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ImagingPipeline:
    """Standardized imaging pipeline for bread porosity measurement."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.original_image = None
        self.grayscale = None
        self.normalized = None
        self.roi_mask = None
        self.threshold_binary = None
        self.cleaned_binary = None
        
    def read_image(self, image_path: str) -> np.ndarray:
        """Read image from file."""
        if not Path(image_path).exists():
            logger.error(f"Image file not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            logger.error(f"Cannot read image - file may be corrupted or unsupported format: {image_path}")
            raise ValueError(f"Cannot read image - file may be corrupted or unsupported format: {image_path}")
        
        logger.info(f"Loaded image: {image_path} (shape: {self.original_image.shape})")
        if self.verbose:
            print(f"✓ Loaded image: {image_path} (shape: {self.original_image.shape})")
        return self.original_image
    
    def to_grayscale(self) -> np.ndarray:
        """Convert to grayscale."""
        if self.original_image is None:
            logger.error("No image loaded. Call read_image first.")
            raise ValueError("No image loaded. Call read_image first.")
        self.grayscale = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        logger.debug("Converted image to grayscale")
        if self.verbose:
            print(f"✓ Converted to grayscale")
        return self.grayscale
    
    def normalize_illumination(self, method: str = "clahe") -> np.ndarray:
        """
        Normalize illumination to handle uneven lighting.
        
        Args:
            method: "clahe" (Contrast Limited Adaptive Histogram Equalization),
                   "morphology" (morphological opening to remove gradients), 
                   or "gaussian" (Gaussian blur subtraction)
        """
        if self.grayscale is None:
            logger.error("Call to_grayscale first.")
            raise ValueError("Call to_grayscale first.")
        
        valid_methods = {"clahe", "morphology", "gaussian"}
        if method not in valid_methods:
            logger.error(f"Unknown normalization method: {method}. Valid: {valid_methods}")
            raise ValueError(f"Unknown normalization method: {method}. Valid: {valid_methods}")
        
        try:
            if method == "clahe":
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                self.normalized = clahe.apply(self.grayscale)
            elif method == "morphology":
                # Remove slow gradients via morphological opening
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
                bg = cv2.morphologyEx(self.grayscale, cv2.MORPH_OPEN, kernel)
                self.normalized = cv2.subtract(self.grayscale, bg)
            elif method == "gaussian":
                # Subtract Gaussian blur to remove gradients
                blurred = cv2.GaussianBlur(self.grayscale, (101, 101), 50)
                self.normalized = cv2.subtract(self.grayscale, blurred)
            
            logger.info(f"Illumination normalized using {method}")
            if self.verbose:
                print(f"✓ Illumination normalized ({method})")
        except Exception as e:
            logger.error(f"Error during illumination normalization: {e}")
            raise
        
        return self.normalized
    
    def find_bread_roi(self, threshold_value: int = 30) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Find region of interest (bread slice) by detecting non-background pixels.
        
        Args:
            threshold_value: pixels below this in normalized image are considered background
        
        Returns:
            roi_mask, roi_stats dict
        """
        if self.normalized is None:
            logger.error("Call normalize_illumination first.")
            raise ValueError("Call normalize_illumination first.")
        
        try:
            # Simple threshold to find bread area (non-background)
            _, self.roi_mask = cv2.threshold(self.normalized, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            self.roi_mask = cv2.morphologyEx(self.roi_mask, cv2.MORPH_CLOSE, kernel)
            self.roi_mask = cv2.morphologyEx(self.roi_mask, cv2.MORPH_OPEN, kernel)
            
            # Get largest contour (bread slice)
            contours, _ = cv2.findContours(self.roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                logger.warning("Could not find bread contours - image may not contain bread slice")
                raise ValueError("Could not find bread slice in image - check input image")
            
            # Use largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            self.roi_mask.fill(0)
            cv2.drawContours(self.roi_mask, [largest_contour], 0, 255, -1)
            
            roi_area = cv2.countNonZero(self.roi_mask)
            roi_stats = {
                "area_pixels": roi_area,
                "area_mm2": None,  # Set if pixel_size_mm is known
            }
            
            logger.info(f"Bread ROI detected: {roi_area} pixels")
            if self.verbose:
                print(f"✓ Bread ROI detected: {roi_area} pixels")
        except Exception as e:
            logger.error(f"Error finding bread ROI: {e}")
            raise
        
        return self.roi_mask, roi_stats
    
    def threshold_holes(self, method: str = "otsu") -> np.ndarray:
        """
        Threshold to segment holes from crumb.
        
        Args:
            method: "otsu" (global Otsu threshold) or "adaptive" (adaptive threshold)
        
        Returns:
            binary image where 255 = holes, 0 = crumb
        """
        if self.normalized is None:
            logger.error("Call normalize_illumination first.")
            raise ValueError("Call normalize_illumination first.")
        if self.roi_mask is None:
            logger.error("Call find_bread_roi first.")
            raise ValueError("Call find_bread_roi first.")
        
        valid_methods = {"otsu", "adaptive"}
        if method not in valid_methods:
            logger.error(f"Unknown threshold method: {method}. Valid: {valid_methods}")
            raise ValueError(f"Unknown threshold method: {method}. Valid: {valid_methods}")
        
        try:
            if method == "otsu":
                _, binary = cv2.threshold(self.normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif method == "adaptive":
                binary = cv2.adaptiveThreshold(self.normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY, 11, 2)
            
            # Apply ROI mask (only consider inside bread)
            binary = cv2.bitwise_and(binary, binary, mask=self.roi_mask)
            self.threshold_binary = binary
            
            logger.info(f"Holes thresholded using {method} method")
            if self.verbose:
                print(f"✓ Holes thresholded ({method})")
        except Exception as e:
            logger.error(f"Error during thresholding: {e}")
            raise
        
        return self.threshold_binary
    
    def morphological_cleanup(self, remove_small_holes: int = 50, fill_small_gaps: int = 50) -> np.ndarray:
        """
        Morphological operations to clean up threshold result.
        
        Args:
            remove_small_holes: remove holes smaller than this (area in pixels)
            fill_small_gaps: fill gaps smaller than this
        """
        if self.threshold_binary is None:
            logger.error("Call threshold_holes first.")
            raise ValueError("Call threshold_holes first.")
        
        try:
            self.cleaned_binary = self.threshold_binary.copy()
            
            # Remove small noise holes
            if remove_small_holes > 0:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                self.cleaned_binary = cv2.morphologyEx(self.cleaned_binary, cv2.MORPH_OPEN, kernel)
            
            # Fill small gaps
            if fill_small_gaps > 0:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                self.cleaned_binary = cv2.morphologyEx(self.cleaned_binary, cv2.MORPH_CLOSE, kernel)
            
            # Remove small isolated components
            contours, _ = cv2.findContours(self.cleaned_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.cleaned_binary.fill(0)
            removed_count = 0
            for contour in contours:
                if cv2.contourArea(contour) > remove_small_holes:
                    cv2.drawContours(self.cleaned_binary, [contour], 0, 255, -1)
                else:
                    removed_count += 1
            
            # Re-apply ROI mask
            self.cleaned_binary = cv2.bitwise_and(self.cleaned_binary, self.cleaned_binary, mask=self.roi_mask)
            
            logger.info(f"Morphological cleanup applied (removed {removed_count} small components)")
            if self.verbose:
                print(f"✓ Morphological cleanup applied")
        except Exception as e:
            logger.error(f"Error during morphological cleanup: {e}")
            raise
        
        return self.cleaned_binary
    
    def get_processing_images(self) -> Dict[str, np.ndarray]:
        """Return all intermediate processing images for visualization."""
        return {
            "original": self.original_image,
            "grayscale": self.grayscale,
            "normalized": self.normalized,
            "roi_mask": self.roi_mask,
            "threshold": self.threshold_binary,
            "cleaned": self.cleaned_binary,
        }
