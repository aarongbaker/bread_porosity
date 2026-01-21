"""
Quality Control Service
Business logic for quality control evaluation and profile management
"""

from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime

from models.analysis_result import AnalysisResult
from models.qc_profile import QCProfile
from repositories.config_repository import ConfigRepository
from utils.exceptions import QCError, ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)


class QCEvaluation:
    """Result of a quality control evaluation"""

    def __init__(self,
                 passed: bool,
                 grade: str,
                 alerts: List[str],
                 scores: Dict[str, float],
                 recommendations: List[str],
                 bread_type: str,
                 timestamp: str = None):
        self.passed = passed
        self.grade = grade
        self.alerts = alerts
        self.scores = scores
        self.recommendations = recommendations
        self.bread_type = bread_type
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "passed": self.passed,
            "grade": self.grade,
            "alerts": self.alerts,
            "scores": self.scores,
            "recommendations": self.recommendations,
            "bread_type": self.bread_type,
            "timestamp": self.timestamp
        }


class QualityControlService:
    """
    Service for quality control evaluation and profile management.

    Provides business logic for:
    - Quality evaluation against profiles
    - Profile management
    - Statistical process control
    - Alert generation
    """

    def __init__(self, config_repo: Optional[ConfigRepository] = None):
        """
        Initialize the QC service.

        Args:
            config_repo: Repository for configuration persistence (optional)
        """
        self.config_repo = config_repo or ConfigRepository("qc_config.json")
        self.current_bread_type = "sourdough"  # Default
        self.alerts = deque(maxlen=100)  # Keep last 100 alerts
        self.history = deque(maxlen=500)  # Keep last 500 evaluations
        self._load_current_profile()

    def _load_current_profile(self) -> None:
        """Load current bread type from config"""
        config = self.config_repo.get_all()
        self.current_bread_type = config.get("current_bread_type", "sourdough")

    def _save_current_profile(self) -> None:
        """Save current bread type to config"""
        config = self.config_repo.get_all()
        config["current_bread_type"] = self.current_bread_type
        self.config_repo.update(config)
        self.config_repo.save()

    def set_bread_type(self, bread_type: str) -> bool:
        """
        Set the current bread type profile.

        Args:
            bread_type: Bread type key

        Returns:
            True if successful, False if profile not found
        """
        # Check if profile exists
        config = self.config_repo.get_all()
        bread_types = config.get("bread_types", {})

        if bread_type not in bread_types:
            logger.warning(f"Bread type '{bread_type}' not found")
            return False

        self.current_bread_type = bread_type
        self._save_current_profile()
        logger.info(f"Bread type set to: {bread_type}")
        return True

    def get_current_profile(self) -> QCProfile:
        """
        Get the current QC profile.

        Returns:
            QCProfile object for current bread type
        """
        config = self.config_repo.get_all()
        bread_types = config.get("bread_types", {})
        profile_data = bread_types.get(self.current_bread_type)

        if not profile_data:
            # Return default sourdough profile
            profile_data = bread_types.get("sourdough", self._get_default_profile())

        return QCProfile.from_dict(profile_data)

    def get_all_bread_types(self) -> Dict[str, str]:
        """
        Get all available bread types.

        Returns:
            Dict mapping bread type keys to display names
        """
        config = self.config_repo.get_all()
        bread_types = config.get("bread_types", {})
        return {key: profile.get("display_name", key) for key, profile in bread_types.items()}

    def add_bread_type(self, bread_type: str, profile: QCProfile) -> None:
        """
        Add a new bread type profile.

        Args:
            bread_type: Profile key
            profile: QCProfile object

        Raises:
            ValidationError: If profile is invalid
        """
        # Validate profile
        is_valid, errors = profile.validate()
        if not is_valid:
            raise ValidationError(f"Invalid profile: {', '.join(errors)}")

        # Save to config
        config = self.config_repo.get_all()
        if "bread_types" not in config:
            config["bread_types"] = {}

        config["bread_types"][bread_type] = profile.to_dict()
        self.config_repo.update(config)
        self.config_repo.save()

        logger.info(f"Added bread type profile: {bread_type}")

    def evaluate_result(self,
                       result: AnalysisResult,
                       bread_type: Optional[str] = None) -> QCEvaluation:
        """
        Evaluate an analysis result against quality standards.

        Args:
            result: AnalysisResult to evaluate
            bread_type: Optional bread type override

        Returns:
            QCEvaluation with results
        """
        try:
            # Set bread type if specified
            if bread_type:
                self.set_bread_type(bread_type)

            # Get current profile
            profile = self.get_current_profile()

            # Perform evaluation
            evaluation = self._evaluate_against_profile(result, profile)

            # Add to history
            self.history.append(evaluation)

            # Add alerts to queue
            if evaluation.alerts:
                self.alerts.extend(evaluation.alerts)

            logger.info(f"QC evaluation: {evaluation.grade}, "
                       f"{'PASS' if evaluation.passed else 'FAIL'}")

            return evaluation

        except Exception as e:
            logger.error(f"QC evaluation failed: {e}")
            raise QCError(f"Failed to evaluate result: {e}") from e

    def _evaluate_against_profile(self, result: AnalysisResult, profile: QCProfile) -> QCEvaluation:
        """
        Evaluate result against a specific profile.

        Args:
            result: AnalysisResult to evaluate
            profile: QCProfile to evaluate against

        Returns:
            QCEvaluation result
        """
        alerts = []
        scores = {}
        recommendations = []

        # Evaluate porosity
        porosity_status = profile.evaluate_porosity(result.porosity_percent)
        if porosity_status == "pass":
            scores["porosity"] = 1.0
        elif porosity_status == "warning":
            scores["porosity"] = 0.7
            alerts.append(
                f"Porosity {result.porosity_percent:.1f}% outside target range "
                f"({profile.porosity_target_min:.1f}-{profile.porosity_target_max:.1f}%) "
                f"but within warning bounds ({profile.porosity_warning_min:.1f}-"
                f"{profile.porosity_warning_max:.1f}%)"
            )
        else:  # fail
            scores["porosity"] = 0.3
            alerts.append(
                f"Porosity {result.porosity_percent:.1f}% outside warning range "
                f"({profile.porosity_warning_min:.1f}-{profile.porosity_warning_max:.1f}%)"
            )

        # Evaluate hole count
        hole_count_status = profile.evaluate_hole_count(result.hole_count_total)
        if hole_count_status == "pass":
            scores["holes"] = 1.0
        else:
            scores["holes"] = 0.6
            if result.hole_count_total < profile.hole_count_target_min:
                alerts.append(
                    f"Low hole count: {result.hole_count_total} "
                    f"(target: {profile.hole_count_target_min}-{profile.hole_count_target_max})"
                )
            else:
                alerts.append(
                    f"High hole count: {result.hole_count_total} "
                    f"(target: {profile.hole_count_target_min}-{profile.hole_count_target_max})"
                )

        # Evaluate uniformity
        uniformity_status = profile.evaluate_uniformity(result.uniformity_score)
        if uniformity_status == "pass":
            scores["uniformity"] = result.uniformity_score
        else:
            scores["uniformity"] = result.uniformity_score
            alerts.append(
                f"Low uniformity: {result.uniformity_score:.2f} "
                f"(min: {profile.uniformity_acceptable_min:.2f})"
            )

        # Overall pass/fail
        passed = (porosity_status in ["pass", "warning"] and
                 hole_count_status == "pass" and
                 uniformity_status == "pass")

        # Determine grade
        grade = profile.get_quality_grade(result.porosity_percent, result.uniformity_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(result, alerts, profile)

        return QCEvaluation(
            passed=passed,
            grade=grade,
            alerts=alerts,
            scores=scores,
            recommendations=recommendations,
            bread_type=self.current_bread_type
        )

    def _generate_recommendations(self,
                                result: AnalysisResult,
                                alerts: List[str],
                                profile: QCProfile) -> List[str]:
        """
        Generate recommendations based on evaluation results.

        Args:
            result: Analysis result
            alerts: List of alerts generated
            profile: QC profile used

        Returns:
            List of recommendations
        """
        recommendations = []

        # Porosity recommendations
        if result.porosity_percent < profile.porosity_target_min:
            recommendations.append("Increase fermentation time or hydration for better porosity")
        elif result.porosity_percent > profile.porosity_target_max:
            recommendations.append("Reduce fermentation time or increase oven temperature")

        # Hole count recommendations
        if result.hole_count_total < profile.hole_count_target_min:
            recommendations.append("Improve gluten development or increase mixing time")
        elif result.hole_count_total > profile.hole_count_target_max:
            recommendations.append("Reduce mixing time or adjust flour type")

        # Uniformity recommendations
        if result.uniformity_score < profile.uniformity_acceptable_min:
            recommendations.append("Improve dough handling consistency and baking conditions")

        # General recommendations
        if not recommendations:
            recommendations.append("Recipe parameters are within acceptable ranges")

        return recommendations

    def get_batch_statistics(self, evaluations: List[QCEvaluation]) -> Dict[str, Any]:
        """
        Calculate batch statistics from multiple evaluations.

        Args:
            evaluations: List of QCEvaluation objects

        Returns:
            Statistics dictionary
        """
        if not evaluations:
            return {"error": "No evaluations provided"}

        # Extract scores
        porosity_scores = [e.scores.get("porosity", 0) for e in evaluations]
        uniformity_scores = [e.scores.get("uniformity", 0) for e in evaluations]

        # Calculate statistics
        stats = {
            "count": len(evaluations),
            "passed": sum(1 for e in evaluations if e.passed),
            "pass_rate": sum(1 for e in evaluations if e.passed) / len(evaluations),
            "grades": {},
            "scores": {
                "porosity": {
                    "mean": sum(porosity_scores) / len(porosity_scores) if porosity_scores else 0,
                    "min": min(porosity_scores) if porosity_scores else 0,
                    "max": max(porosity_scores) if porosity_scores else 0
                },
                "uniformity": {
                    "mean": sum(uniformity_scores) / len(uniformity_scores) if uniformity_scores else 0,
                    "min": min(uniformity_scores) if uniformity_scores else 0,
                    "max": max(uniformity_scores) if uniformity_scores else 0
                }
            }
        }

        # Grade distribution
        for evaluation in evaluations:
            grade = evaluation.grade
            stats["grades"][grade] = stats["grades"].get(grade, 0) + 1

        return stats

    def get_recent_alerts(self, limit: int = 10) -> List[str]:
        """
        Get recent alerts.

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of recent alerts
        """
        return list(self.alerts)[-limit:]

    def _get_default_profile(self) -> Dict[str, Any]:
        """Get default sourdough profile"""
        return {
            "bread_type": "sourdough",
            "display_name": "Sourdough",
            "porosity_target_min": 20.0,
            "porosity_target_max": 35.0,
            "porosity_warning_min": 18.0,
            "porosity_warning_max": 37.0,
            "hole_count_target_min": 100,
            "hole_count_target_max": 400,
            "hole_diameter_target_min": 2.0,
            "hole_diameter_target_max": 8.0,
            "uniformity_acceptable_min": 0.7,
            "consistency_cv_max": 0.15,
            "quality_grades": {
                "excellent": {"porosity": [25, 32], "uniformity": [0.85, 1.0]},
                "good": {"porosity": [22, 35], "uniformity": [0.75, 0.95]},
                "fair": {"porosity": [18, 38], "uniformity": [0.65, 0.85]},
                "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]}
            }
        }
