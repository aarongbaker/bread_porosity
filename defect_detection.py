"""
Defect Detection Module
Detects uneven rise and dense spots in bread crumb structure
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json


class DefectDetector:
    """Detect common bread defects: uneven rise and dense spots"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def detect_defects(self, image_path: str) -> Dict[str, Any]:
        """
        Detect defects in bread image
        
        Args:
            image_path: Path to bread slice image
            
        Returns:
            Dict with defect analysis
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": f"Could not read image: {image_path}"}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect uneven rise
        uneven_rise = self._detect_uneven_rise(gray)
        
        # Detect dense spots
        dense_spots = self._detect_dense_spots(gray)
        
        # Calculate overall severity
        severity = (uneven_rise['severity'] + dense_spots['severity']) / 2
        
        # Generate annotated image
        annotated = self._annotate_defects(image, uneven_rise, dense_spots)
        
        result = {
            'image_path': str(image_path),
            'overall_severity': float(severity),
            'defect_grade': self._grade_severity(severity),
            'uneven_rise': uneven_rise,
            'dense_spots': dense_spots,
            'annotated_image': annotated,
            'recommendations': self._get_recommendations(uneven_rise, dense_spots)
        }
        
        if self.verbose:
            print(f"Defect Detection: {result['defect_grade']} (severity: {severity:.1f}/100)")
        
        return result
    
    def _detect_uneven_rise(self, gray: np.ndarray) -> Dict[str, Any]:
        """
        Detect uneven rise by comparing edge vs. center brightness
        High variance indicates uneven fermentation
        """
        h, w = gray.shape
        
        # Get brightness in different zones
        center_h, center_w = h // 4, w // 4
        
        # Center region (should be brightest if well-risen)
        center = gray[center_h:center_h*3, center_w:center_w*3]
        center_brightness = np.mean(center)
        
        # Edge regions
        top_edge = gray[:h//4, :]
        bottom_edge = gray[-h//4:, :]
        left_edge = gray[:, :w//4]
        right_edge = gray[:, -w//4:]
        
        edge_brightness = np.mean([
            np.mean(top_edge),
            np.mean(bottom_edge),
            np.mean(left_edge),
            np.mean(right_edge)
        ])
        
        # Calculate variance (higher = more uneven)
        brightness_diff = abs(center_brightness - edge_brightness)
        severity = min(100, (brightness_diff / 255) * 100 * 2)  # Scale to 0-100
        
        return {
            'severity': float(severity),
            'center_brightness': float(center_brightness),
            'edge_brightness': float(edge_brightness),
            'difference': float(brightness_diff),
            'detected': severity > 30  # Threshold: 30+
        }
    
    def _detect_dense_spots(self, gray: np.ndarray) -> Dict[str, Any]:
        """
        Detect dense spots (local low-porosity areas)
        Uses local variance to find hard spots
        """
        h, w = gray.shape
        
        # Apply Gaussian blur for smoothing
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Calculate local variance using morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        dilated = cv2.dilate(blurred, kernel, iterations=1)
        eroded = cv2.erode(blurred, kernel, iterations=1)
        
        # Difference indicates dense regions
        variance_map = dilated - eroded
        
        # Find dense spots (below average brightness with low local variance)
        dense_threshold = np.percentile(variance_map, 25)
        dense_mask = variance_map < dense_threshold
        
        # Count dense pixels
        dense_pixels = np.sum(dense_mask)
        dense_percentage = (dense_pixels / (h * w)) * 100
        
        # Severity: more dense spots = higher severity
        severity = min(100, dense_percentage * 2)
        
        # Find connected components (clusters of dense spots)
        contours, _ = cv2.findContours(dense_mask.astype(np.uint8), 
                                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        num_clusters = len(contours)
        
        return {
            'severity': float(severity),
            'dense_percentage': float(dense_percentage),
            'num_clusters': int(num_clusters),
            'detected': dense_percentage > 5  # Threshold: 5%+
        }
    
    def _annotate_defects(self, image: np.ndarray, 
                         uneven_rise: Dict, dense_spots: Dict) -> np.ndarray:
        """
        Annotate image with detected defects
        """
        annotated = image.copy()
        h, w = image.shape[:2]
        
        # Red for uneven rise zones
        if uneven_rise['detected']:
            cv2.rectangle(annotated, (0, 0), (w//4, h//4), (0, 0, 255), 3)
            cv2.rectangle(annotated, (3*w//4, 0), (w, h//4), (0, 0, 255), 3)
            cv2.rectangle(annotated, (0, 3*h//4), (w//4, h), (0, 0, 255), 3)
            cv2.rectangle(annotated, (3*w//4, 3*h//4), (w, h), (0, 0, 255), 3)
        
        # Yellow circle for center (reference)
        center_x, center_y = w // 2, h // 2
        cv2.circle(annotated, (center_x, center_y), min(w, h) // 4, (0, 255, 255), 2)
        
        # Add text annotations
        severity_text = f"Severity: {(uneven_rise['severity'] + dense_spots['severity'])/2:.0f}/100"
        cv2.putText(annotated, severity_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (0, 255, 0), 2)
        
        if uneven_rise['detected']:
            cv2.putText(annotated, "Uneven Rise Detected", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 0, 255), 2)
        
        if dense_spots['detected']:
            cv2.putText(annotated, f"Dense Spots: {dense_spots['dense_percentage']:.1f}%", 
                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated
    
    def _grade_severity(self, severity: float) -> str:
        """Grade severity into categories"""
        if severity < 20:
            return "EXCELLENT"
        elif severity < 40:
            return "GOOD"
        elif severity < 60:
            return "FAIR"
        else:
            return "POOR"
    
    def _get_recommendations(self, uneven_rise: Dict, dense_spots: Dict) -> List[str]:
        """Generate recommendations based on detected defects"""
        recommendations = []
        
        if uneven_rise['detected']:
            recommendations.append("Uneven rise detected - check fermentation temperature uniformity")
            recommendations.append("Ensure consistent oven temperature throughout baking")
            recommendations.append("Consider adjusting proof time or temperature")
        
        if dense_spots['detected']:
            if dense_spots['dense_percentage'] > 10:
                recommendations.append("Significant dense spots detected - may indicate degassing issues")
                recommendations.append("Check fermentation duration - may be over-proofed")
                recommendations.append("Verify dough hydration and mixing consistency")
            else:
                recommendations.append("Minor dense spots - monitor in next batch")
        
        if not recommendations:
            recommendations.append("Excellent crumb structure - maintain current process")
        
        return recommendations
    
    def batch_detect(self, image_dir: str) -> Dict[str, Any]:
        """
        Run defect detection on batch of images
        
        Args:
            image_dir: Directory containing bread images
            
        Returns:
            Summary of defects across batch
        """
        image_dir = Path(image_dir)
        results = []
        
        for image_file in sorted(image_dir.glob('*.jpg')) + sorted(image_dir.glob('*.png')):
            result = self.detect_defects(str(image_file))
            if 'error' not in result:
                results.append(result)
        
        if not results:
            return {'error': 'No images found'}
        
        # Calculate batch statistics
        severities = [r['overall_severity'] for r in results]
        uneven_count = sum(1 for r in results if r['uneven_rise']['detected'])
        dense_count = sum(1 for r in results if r['dense_spots']['detected'])
        
        summary = {
            'num_images': len(results),
            'avg_severity': float(np.mean(severities)),
            'max_severity': float(np.max(severities)),
            'min_severity': float(np.min(severities)),
            'batch_grade': self._grade_severity(np.mean(severities)),
            'uneven_rise_count': uneven_count,
            'dense_spots_count': dense_count,
            'pass_rate': float((sum(1 for s in severities if s < 50) / len(severities)) * 100),
            'results': results
        }
        
        return summary


def demo_defect_detection():
    """Demonstrate defect detection on sample image"""
    print("Defect Detection Module")
    print("=" * 50)
    print("This module detects:")
    print("  - Uneven rise (brightness gradient from edge to center)")
    print("  - Dense spots (low-porosity clusters)")
    print()
    print("Usage:")
    print("  from defect_detection import DefectDetector")
    print("  detector = DefectDetector()")
    print("  result = detector.detect_defects('bread.jpg')")
    print("  result['overall_severity']  # 0-100")
    print("  result['defect_grade']      # EXCELLENT/GOOD/FAIR/POOR")
    print("  result['recommendations']   # List of suggestions")


if __name__ == "__main__":
    demo_defect_detection()
