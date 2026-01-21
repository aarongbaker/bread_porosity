"""
Defect Service
Business logic for defect detection in bread images
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import cv2
import numpy as np

from utils.exceptions import AnalysisError
from utils.logger import get_logger

# Import existing defect detector
try:
    from defect_detection import DefectDetector
    DEFECT_AVAILABLE = True
except ImportError:
    DEFECT_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("DefectDetector not available - defect detection features disabled")

logger = get_logger(__name__)


class DefectReport:
    """Report of detected defects in a bread image"""

    def __init__(self,
                 image_path: str,
                 overall_severity: float,
                 defect_grade: str,
                 uneven_rise: Dict[str, Any],
                 dense_spots: Dict[str, Any],
                 recommendations: List[str],
                 annotated_image: Optional[np.ndarray] = None):
        self.image_path = image_path
        self.overall_severity = overall_severity
        self.defect_grade = defect_grade
        self.uneven_rise = uneven_rise
        self.dense_spots = dense_spots
        self.recommendations = recommendations
        self.annotated_image = annotated_image

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding image data)"""
        return {
            "image_path": self.image_path,
            "overall_severity": self.overall_severity,
            "defect_grade": self.defect_grade,
            "uneven_rise": self.uneven_rise,
            "dense_spots": self.dense_spots,
            "recommendations": self.recommendations
        }


class DefectService:
    """
    Service for detecting defects in bread images.

    Provides business logic for:
    - Uneven rise detection
    - Dense spot detection
    - Defect severity assessment
    - Recommendations for improvement
    """

    def __init__(self):
        """Initialize the defect service."""
        if DEFECT_AVAILABLE:
            self.detector = DefectDetector(verbose=False)
        else:
            self.detector = None

    def detect_defects(self, image_path: str) -> DefectReport:
        """
        Detect defects in a bread image.

        Args:
            image_path: Path to the bread image file

        Returns:
            DefectReport with analysis results

        Raises:
            AnalysisError: If defect detection fails
        """
        if not DEFECT_AVAILABLE or not self.detector:
            raise AnalysisError("Defect detection not available - DefectDetector not found")

        try:
            # Validate image path
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                raise AnalysisError(f"Image file not found: {image_path}")

            # Run defect detection
            result = self.detector.detect_defects(str(image_path))

            if "error" in result:
                raise AnalysisError(f"Defect detection failed: {result['error']}")

            # Create DefectReport
            report = DefectReport(
                image_path=str(image_path),
                overall_severity=result.get('overall_severity', 0.0),
                defect_grade=result.get('defect_grade', 'unknown'),
                uneven_rise=result.get('uneven_rise', {}),
                dense_spots=result.get('dense_spots', {}),
                recommendations=result.get('recommendations', []),
                annotated_image=result.get('annotated_image')
            )

            logger.info(f"Defect detection complete: {report.defect_grade} "
                       f"(severity: {report.overall_severity:.1f}/100)")

            return report

        except Exception as e:
            logger.error(f"Defect detection failed for {image_path}: {e}")
            raise AnalysisError(f"Failed to detect defects: {e}") from e

    def analyze_defect_patterns(self, reports: List[DefectReport]) -> Dict[str, Any]:
        """
        Analyze patterns across multiple defect reports.

        Args:
            reports: List of DefectReport objects

        Returns:
            Dictionary with pattern analysis
        """
        if not reports:
            return {"error": "No reports to analyze"}

        # Aggregate statistics
        severities = [r.overall_severity for r in reports]
        uneven_severities = [r.uneven_rise.get('severity', 0) for r in reports]
        dense_severities = [r.dense_spots.get('severity', 0) for r in reports]

        # Grade distribution
        grades = {}
        for report in reports:
            grade = report.defect_grade
            grades[grade] = grades.get(grade, 0) + 1

        analysis = {
            "count": len(reports),
            "severity_stats": {
                "overall_mean": np.mean(severities) if severities else 0,
                "overall_std": np.std(severities) if severities else 0,
                "overall_range": {
                    "min": min(severities) if severities else 0,
                    "max": max(severities) if severities else 0
                }
            },
            "defect_types": {
                "uneven_rise": {
                    "mean_severity": np.mean(uneven_severities) if uneven_severities else 0,
                    "prevalence": sum(1 for r in reports if r.uneven_rise.get('detected', False))
                },
                "dense_spots": {
                    "mean_severity": np.mean(dense_severities) if dense_severities else 0,
                    "prevalence": sum(1 for r in reports if r.dense_spots.get('detected', False))
                }
            },
            "grade_distribution": grades,
            "insights": self._generate_pattern_insights(analysis)
        }

        return analysis

    def _generate_pattern_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate insights from defect pattern analysis.

        Args:
            analysis: Pattern analysis dictionary

        Returns:
            List of insight strings
        """
        insights = []

        overall_mean = analysis["severity_stats"]["overall_mean"]

        if overall_mean < 20:
            insights.append("Overall defect severity is low - good baking consistency")
        elif overall_mean < 40:
            insights.append("Moderate defect severity - room for improvement in fermentation")
        else:
            insights.append("High defect severity - significant issues with fermentation or baking process")

        # Check specific defect types
        uneven_prevalence = analysis["defect_types"]["uneven_rise"]["prevalence"]
        dense_prevalence = analysis["defect_types"]["dense_spots"]["prevalence"]
        total_count = analysis["count"]

        if uneven_prevalence > total_count * 0.5:
            insights.append("Uneven rise is common - check fermentation temperature consistency")

        if dense_prevalence > total_count * 0.5:
            insights.append("Dense spots are prevalent - review dough mixing and hydration")

        # Grade distribution insights
        grades = analysis["grade_distribution"]
        if grades.get("severe", 0) > total_count * 0.3:
            insights.append("Many samples have severe defects - immediate process review needed")

        return insights

    def get_defect_types(self) -> List[Dict[str, Any]]:
        """
        Get information about detectable defect types.

        Returns:
            List of defect type information
        """
        return [
            {
                "type": "uneven_rise",
                "name": "Uneven Rise",
                "description": "Inconsistent crumb structure due to uneven fermentation",
                "causes": ["Temperature fluctuations", "Inconsistent dough handling", "Poor yeast distribution"],
                "severity_range": "0-100 (higher = more uneven)",
                "threshold": "30+ indicates significant unevenness"
            },
            {
                "type": "dense_spots",
                "name": "Dense Spots",
                "description": "Localized areas of low porosity indicating under-fermentation",
                "causes": ["Cold spots in proofing", "Uneven salt distribution", "Over-mixing"],
                "severity_range": "0-100 (higher = more dense areas)",
                "threshold": "5%+ dense area indicates issues"
            }
        ]

    def get_severity_grades(self) -> Dict[str, Dict[str, Any]]:
        """
        Get defect severity grade definitions.

        Returns:
            Dictionary mapping grades to severity ranges and descriptions
        """
        return {
            "none": {
                "range": "0-10",
                "description": "No significant defects detected",
                "color": "green"
            },
            "minor": {
                "range": "10-30",
                "description": "Minor defects, generally acceptable",
                "color": "yellow"
            },
            "moderate": {
                "range": "30-60",
                "description": "Moderate defects affecting quality",
                "color": "orange"
            },
            "severe": {
                "range": "60-100",
                "description": "Severe defects requiring process changes",
                "color": "red"
            }
        }

    def save_annotated_image(self, report: DefectReport, output_path: str) -> bool:
        """
        Save the annotated defect image to file.

        Args:
            report: DefectReport with annotated image
            output_path: Path to save the image

        Returns:
            True if saved successfully, False otherwise
        """
        if report.annotated_image is None:
            logger.warning("No annotated image available in report")
            return False

        try:
            success = cv2.imwrite(output_path, report.annotated_image)
            if success:
                logger.info(f"Annotated image saved: {output_path}")
            else:
                logger.error(f"Failed to save annotated image: {output_path}")
            return success
        except Exception as e:
            logger.error(f"Error saving annotated image: {e}")
            return False