"""
Image Quality Validator
Checks if images meet analysis requirements before processing.
"""

import cv2
import numpy as np
from typing import Dict, Tuple
from pathlib import Path


class ImageQualityValidator:
    """Validate bread images for analysis readiness."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.quality_score = 0
        self.checks = {}
    
    def validate_image(self, image_path: str) -> Dict:
        """
        Comprehensive image quality validation.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dict with validation results and recommendations
        """
        self.checks = {}
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            return {
                "valid": False,
                "score": 0,
                "overall_status": "❌ CANNOT ANALYZE",
                "issues": ["File cannot be read or is not an image"],
                "recommendations": ["Check file format and file is not corrupted"]
            }
        
        # Run checks
        self._check_resolution(image)
        self._check_focus(image)
        self._check_exposure(image)
        self._check_lighting_uniformity(image)
        self._check_contrast(image)
        self._check_rotation(image)
        
        # Calculate overall score
        scores = [v.get("score", 0) for v in self.checks.values()]
        self.quality_score = np.mean(scores) if scores else 0
        
        # Determine status
        if self.quality_score >= 0.85:
            status = "✅ EXCELLENT"
        elif self.quality_score >= 0.70:
            status = "✔️ GOOD"
        elif self.quality_score >= 0.50:
            status = "⚠️ MARGINAL"
        else:
            status = "❌ POOR"
        
        # Get recommendations
        recommendations = self._get_recommendations()
        issues = [k for k, v in self.checks.items() if v.get("score", 0) < 0.6]
        
        return {
            "valid": self.quality_score >= 0.50,
            "score": round(self.quality_score, 2),
            "overall_status": status,
            "checks": self.checks,
            "issues": issues,
            "recommendations": recommendations,
            "can_proceed": self.quality_score >= 0.50
        }
    
    def _check_resolution(self, image: np.ndarray):
        """Check if image resolution is sufficient."""
        height, width = image.shape[:2]
        megapixels = (width * height) / 1e6
        
        # Need at least 2MP for reasonable detail
        if megapixels >= 4:
            score = 1.0
        elif megapixels >= 2:
            score = 0.85
        elif megapixels >= 1:
            score = 0.60
        else:
            score = 0.2
        
        self.checks["Resolution"] = {
            "score": score,
            "value": f"{width}x{height} ({megapixels:.1f}MP)",
            "required": "≥2MP recommended"
        }
    
    def _check_focus(self, image: np.ndarray):
        """Check focus sharpness using Laplacian variance."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Threshold from literature: ~500 for well-focused images
        if variance >= 800:
            score = 1.0
        elif variance >= 500:
            score = 0.90
        elif variance >= 250:
            score = 0.60
        elif variance >= 100:
            score = 0.30
        else:
            score = 0.1
        
        self.checks["Focus"] = {
            "score": score,
            "value": f"Variance: {variance:.0f}",
            "required": "≥500 (well-focused)"
        }
    
    def _check_exposure(self, image: np.ndarray):
        """Check exposure levels (not too dark, not too blown out)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_intensity = gray.mean()
        
        # Ideal exposure is in mid-range (100-200 for 0-255 scale)
        if 100 <= mean_intensity <= 200:
            score = 1.0
        elif 80 <= mean_intensity <= 220:
            score = 0.85
        elif 60 <= mean_intensity <= 240:
            score = 0.60
        else:
            score = 0.30
        
        # Check for blown out areas (255) and pure black (0)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        blown_out = hist[255][0]
        pure_black = hist[0][0]
        total_pixels = image.shape[0] * image.shape[1]
        
        blown_percent = (blown_out / total_pixels) * 100
        black_percent = (pure_black / total_pixels) * 100
        
        if blown_percent > 5 or black_percent > 5:
            score *= 0.7  # Penalize
        
        self.checks["Exposure"] = {
            "score": score,
            "value": f"Mean: {mean_intensity:.0f}, Blown: {blown_percent:.1f}%, Black: {black_percent:.1f}%",
            "required": "100-200 mean intensity"
        }
    
    def _check_lighting_uniformity(self, image: np.ndarray):
        """Check if lighting is uniform across image (for backlit setup)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Divide into quadrants and compare
        h, w = gray.shape
        q1 = gray[:h//2, :w//2].mean()
        q2 = gray[:h//2, w//2:].mean()
        q3 = gray[h//2:, :w//2].mean()
        q4 = gray[h//2:, w//2:].mean()
        
        quadrant_means = [q1, q2, q3, q4]
        overall_mean = np.mean(quadrant_means)
        quadrant_std = np.std(quadrant_means)
        uniformity_cv = (quadrant_std / overall_mean) * 100
        
        # Lower CV is better (more uniform)
        if uniformity_cv < 10:
            score = 1.0
        elif uniformity_cv < 15:
            score = 0.85
        elif uniformity_cv < 25:
            score = 0.60
        else:
            score = 0.30
        
        self.checks["Lighting Uniformity"] = {
            "score": score,
            "value": f"CV: {uniformity_cv:.1f}% (std of quadrants)",
            "required": "<15% for uniform lighting"
        }
    
    def _check_contrast(self, image: np.ndarray):
        """Check image contrast (dynamic range)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        
        # Want good contrast (high std dev)
        if contrast >= 60:
            score = 1.0
        elif contrast >= 40:
            score = 0.85
        elif contrast >= 25:
            score = 0.60
        elif contrast >= 15:
            score = 0.30
        else:
            score = 0.1
        
        self.checks["Contrast"] = {
            "score": score,
            "value": f"Std Dev: {contrast:.1f}",
            "required": "≥40 for good contrast"
        }
    
    def _check_rotation(self, image: np.ndarray):
        """Check if image appears to be rotated (bread should be roughly horizontal)."""
        # Simple heuristic: image should be roughly landscape or square
        h, w = image.shape[:2]
        aspect_ratio = w / h
        
        # Accept 0.7 to 1.4 ratio (not too rotated)
        if 0.7 <= aspect_ratio <= 1.4:
            score = 1.0
        elif 0.6 <= aspect_ratio <= 1.5:
            score = 0.80
        else:
            score = 0.50
        
        self.checks["Orientation"] = {
            "score": score,
            "value": f"Aspect ratio: {aspect_ratio:.2f}",
            "required": "≈1.0 (landscape or square)"
        }
    
    def _get_recommendations(self) -> list:
        """Generate user-friendly recommendations based on failed checks."""
        recommendations = []
        
        # Focus issues
        if self.checks.get("Focus", {}).get("score", 0) < 0.6:
            recommendations.append("🔍 Focus: Ensure camera is in focus. Check autofocus or manual focus.")
            recommendations.append("   → Clean lens, ensure sharp focus, avoid camera shake/movement")
        
        # Exposure issues
        if self.checks.get("Exposure", {}).get("score", 0) < 0.6:
            recommendations.append("☀️ Exposure: Image is too dark or too bright.")
            recommendations.append("   → Adjust backlight intensity or camera exposure settings")
        
        # Lighting uniformity
        if self.checks.get("Lighting Uniformity", {}).get("score", 0) < 0.6:
            recommendations.append("💡 Lighting: Lighting is uneven across image.")
            recommendations.append("   → Use diffuser (frosted glass/paper) between light and bread")
            recommendations.append("   → Ensure backlight is evenly positioned")
        
        # Contrast issues
        if self.checks.get("Contrast", {}).get("score", 0) < 0.6:
            recommendations.append("🎨 Contrast: Low contrast between holes and crumb.")
            recommendations.append("   → Increase backlight intensity or reduce front lighting")
        
        # Resolution issues
        if self.checks.get("Resolution", {}).get("score", 0) < 0.6:
            recommendations.append("📱 Resolution: Image resolution is too low.")
            recommendations.append("   → Use higher resolution camera (≥2MP)")
        
        # Rotation issues
        if self.checks.get("Orientation", {}).get("score", 0) < 0.6:
            recommendations.append("🔄 Orientation: Image may be rotated.")
            recommendations.append("   → Keep bread slice horizontal in frame")
        
        if not recommendations:
            recommendations.append("✅ Image quality is good! You can proceed with analysis.")
        
        return recommendations
    
    def print_report(self, validation_result: Dict):
        """Print human-readable validation report."""
        if not self.verbose:
            return
        
        print("\n" + "="*70)
        print("IMAGE QUALITY VALIDATION REPORT")
        print("="*70)
        print(f"\nOverall Status: {validation_result['overall_status']}")
        print(f"Quality Score: {validation_result['score']}/1.0")
        print(f"Can Proceed: {'YES ✓' if validation_result['can_proceed'] else 'NO ✗'}")
        
        print("\nDETAILED CHECKS:")
        print("-"*70)
        for check_name, check_data in validation_result['checks'].items():
            score = check_data.get("score", 0)
            value = check_data.get("value", "")
            required = check_data.get("required", "")
            
            # Visual indicator
            if score >= 0.85:
                indicator = "✓ "
            elif score >= 0.60:
                indicator = "⚠ "
            else:
                indicator = "✗ "
            
            print(f"{indicator} {check_name:25} {score:.2f}  ({value})")
            print(f"  Required: {required}\n")
        
        if validation_result['recommendations']:
            print("\nRECOMMENDATIONS:")
            print("-"*70)
            for rec in validation_result['recommendations']:
                print(f"  {rec}")
        
        print("\n" + "="*70 + "\n")
