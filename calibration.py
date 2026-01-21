"""
Calibration helpers for bread porosity analysis.
Provides pixel size estimation and simple setup checks.
"""

from dataclasses import dataclass
from typing import Dict, Any, Iterable

import cv2
import numpy as np


@dataclass
class ReferenceCalibration:
    """Store calibration details for converting pixels to mm."""

    pixel_size_mm: float
    reference_length_mm: float
    reference_length_pixels: float
    method: str = "manual"
    notes: str = ""

    @classmethod
    def from_reference(cls,
                       reference_length_mm: float,
                       reference_length_pixels: float,
                       method: str = "manual",
                       notes: str = "") -> "ReferenceCalibration":
        """Create calibration from a known-length reference."""
        if reference_length_pixels <= 0:
            raise ValueError("reference_length_pixels must be > 0")
        pixel_size_mm = reference_length_mm / reference_length_pixels
        return cls(
            pixel_size_mm=pixel_size_mm,
            reference_length_mm=reference_length_mm,
            reference_length_pixels=reference_length_pixels,
            method=method,
            notes=notes,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return calibration as a serializable dict."""
        return {
            "pixel_size_mm": self.pixel_size_mm,
            "reference_length_mm": self.reference_length_mm,
            "reference_length_pixels": self.reference_length_pixels,
            "method": self.method,
            "notes": self.notes,
        }


class CameraSetupHelper:
    """Compute simple setup quality metrics from images."""

    @staticmethod
    def estimate_sharpness(image: np.ndarray) -> float:
        """
        Estimate sharpness using variance of Laplacian.
        Higher values indicate sharper focus.
        """
        if image is None:
            raise ValueError("image must be provided")
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    @staticmethod
    def estimate_uniformity(image: np.ndarray) -> float:
        """
        Estimate lighting uniformity as (1 - CV) * 100.
        Higher values indicate more uniform illumination.
        """
        if image is None:
            raise ValueError("image must be provided")
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        mean = float(np.mean(gray))
        std = float(np.std(gray))
        cv = std / (mean + 1e-6)
        uniformity = max(0.0, min(1.0, 1.0 - cv))
        return uniformity * 100


class SetupChecklist:
    """Simple checklist helper for capture setup."""

    @staticmethod
    def default_items() -> Iterable[Dict[str, str]]:
        """Return a default checklist for setup validation."""
        return [
            {"item": "Backlit setup", "target": "Uniform white light behind sample"},
            {"item": "Focus locked", "target": "No motion blur, sharp edges"},
            {"item": "Exposure locked", "target": "No blown highlights"},
            {"item": "Reference patch", "target": "Gray card or ruler in frame"},
        ]
