"""
Calibration and setup utilities for standardized imaging.
Handles reference patch normalization and camera setup helpers.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from pathlib import Path


class ReferenceCalibration:
    """
    Utilities for reference patch-based calibration.
    
    Typical workflow:
    1. Place a reference patch (gray card or printed square) in the image
    2. Detect/specify its location
    3. Use it to normalize brightness across images for consistency
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.reference_value = None
        self.reference_region = None
    
    def detect_reference_patch(self, image: np.ndarray, patch_type: str = "gray",
                               search_region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, any]:
        """
        Detect reference patch in image.
        
        Args:
            image: Color image
            patch_type: "gray" (neutral gray card), "white" (white patch), "black" (black patch)
            search_region: Optional ROI to search (x1, y1, x2, y2)
        
        Returns:
            Dict with detected patch info: 'mean_value', 'region', 'confidence'
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Define expected brightness based on patch type
        if patch_type == "gray":
            target_range = (100, 150)
        elif patch_type == "white":
            target_range = (180, 255)
        elif patch_type == "black":
            target_range = (0, 80)
        else:
            raise ValueError(f"Unknown patch type: {patch_type}")
        
        # Search for patch
        if search_region:
            x1, y1, x2, y2 = search_region
            search_area = gray[y1:y2, x1:x2]
        else:
            search_area = gray
        
        # Find bright/dark region matching patch type
        mask = cv2.inRange(search_area, target_range[0], target_range[1])
        
        if cv2.countNonZero(mask) == 0:
            if self.verbose:
                print(f"⚠ Warning: Could not detect {patch_type} reference patch")
            return {"detected": False}
        
        # Get largest blob
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {"detected": False}
        
        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        
        if search_region:
            x += search_region[0]
            y += search_region[1]
        
        # Measure mean value in patch
        patch_region = gray[y:y+h, x:x+w]
        mean_value = np.mean(patch_region)
        std_value = np.std(patch_region)
        
        self.reference_value = mean_value
        self.reference_region = (x, y, w, h)
        
        result = {
            "detected": True,
            "type": patch_type,
            "mean_value": float(mean_value),
            "std_value": float(std_value),
            "region": (x, y, w, h),
            "area_pixels": w * h,
        }
        
        if self.verbose:
            print(f"✓ Detected {patch_type} reference patch: {mean_value:.1f} ± {std_value:.1f}")
        
        return result
    
    def normalize_by_reference(self, image: np.ndarray, reference_value: float = 128) -> np.ndarray:
        """
        Normalize image brightness using reference patch value.
        
        Args:
            image: Grayscale image
            reference_value: Target reference value (typically 128 for mid-gray)
        
        Returns:
            Normalized image
        """
        if self.reference_value is None:
            if self.verbose:
                print("⚠ No reference value set. Run detect_reference_patch first.")
            return image
        
        # Scale image so reference patch reaches target value
        scale_factor = reference_value / (self.reference_value + 1e-6)
        normalized = np.clip(image.astype(np.float32) * scale_factor, 0, 255).astype(np.uint8)
        
        if self.verbose:
            print(f"✓ Applied reference normalization (scale factor: {scale_factor:.3f})")
        
        return normalized


class CameraSetupHelper:
    """Utilities to help standardize camera setup for repeatable measurements."""
    
    @staticmethod
    def estimate_pixel_size(reference_object_size_mm: float, 
                           object_pixels: int) -> float:
        """
        Estimate pixel size in mm based on known reference object.
        
        Args:
            reference_object_size_mm: Known size of reference object in mm
            object_pixels: Size of object in pixels in image
        
        Returns:
            Pixel size in mm
        """
        pixel_size = reference_object_size_mm / object_pixels
        return pixel_size
    
    @staticmethod
    def check_image_sharpness(image: np.ndarray) -> Dict[str, float]:
        """
        Estimate image sharpness using Laplacian variance.
        Higher variance = sharper image. Useful for focus verification.
        
        Returns:
            Dict with 'laplacian_var' and 'sharpness_level' (low/medium/high)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:
            level = "low (out of focus)"
        elif laplacian_var < 500:
            level = "medium"
        else:
            level = "high (sharp)"
        
        return {
            "laplacian_variance": float(laplacian_var),
            "sharpness_level": level,
        }
    
    @staticmethod
    def estimate_lighting_uniformity(image: np.ndarray) -> Dict[str, float]:
        """
        Estimate how uniform the lighting is across the image.
        Lower variance of brightness = more uniform lighting.
        
        Returns:
            Dict with uniformity metrics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Divide image into grid and check brightness variation
        h, w = gray.shape
        grid_size = 4
        cell_h, cell_w = h // grid_size, w // grid_size
        
        cell_means = []
        for i in range(grid_size):
            for j in range(grid_size):
                cell = gray[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                cell_means.append(np.mean(cell))
        
        cell_means = np.array(cell_means)
        uniformity_score = 100 - (np.std(cell_means) / np.mean(cell_means) * 100)
        
        return {
            "mean_brightness": float(np.mean(gray)),
            "grid_brightness_std": float(np.std(cell_means)),
            "uniformity_score": float(max(0, uniformity_score)),  # 0-100, higher=more uniform
        }


class SetupChecklist:
    """Interactive checklist for proper imaging setup."""
    
    @staticmethod
    def print_setup_guide():
        guide = """
╔════════════════════════════════════════════════════════════════════╗
║           BREAD POROSITY IMAGING SETUP CHECKLIST                   ║
╚════════════════════════════════════════════════════════════════════╝

LIGHTING & ILLUMINATION:
  ☐ Place bread slice directly against diffuser (frosted acrylic or printer paper)
  ☐ Provide uniform backlight (tablet at max white, or diffuser + bright lamp)
  ☐ Avoid shadows and uneven illumination
  ☐ Check uniformity score > 70 using estimate_lighting_uniformity()

CAMERA & POSITIONING:
  ☐ Mount camera on tripod (fixed position & distance)
  ☐ Lock focal length (set to macro/close focus if available)
  ☐ Ensure camera is perpendicular to bread slice (no angle)
  ☐ Use autofocus lock or manual focus for consistency

IMAGE PARAMETERS:
  ☐ Lock exposure (Manual mode recommended)
  ☐ Lock white balance (daylight or custom)
  ☐ Use consistent ISO (lower is better to reduce noise)
  ☐ Use high resolution for better hole detection

STANDARDIZATION (Critical for repeatable results):
  ☐ Use same slice thickness for all samples
  ☐ Include reference patch in image (neutral gray card recommended)
  ☐ Place reference patch in consistent location
  ☐ Document pixel_size_mm for accurate measurements
  ☐ Check sharpness score: should be "high"

VALIDATION:
  ☐ Test with known sample (measure multiple times, should be consistent)
  ☐ porosity variation < 5% across repeated measurements = good setup
  ☐ If porosity varies >5%, adjust lighting or focus

REFERENCE PATCH RECOMMENDATION:
  For best results, include a gray card (Kodak 18% gray, or similar):
  - Shows up well in backlit images
  - Provides normalization reference
  - Helps with white balance verification

═════════════════════════════════════════════════════════════════════
"""
        print(guide)
