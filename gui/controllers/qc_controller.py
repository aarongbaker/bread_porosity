"""
Quality Control Controller
Handles quality control operations and coordinates with QualityControlService
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any, Callable, List
import json

from services.quality_control_service import QualityControlService
from models.analysis_result import AnalysisResult
from models.qc_profile import QCProfile
from utils.logger import get_logger

logger = get_logger(__name__)


class QCController:
    """Controller for quality control operations"""

    def __init__(self, qc_service: QualityControlService, view_callback: Optional[Callable] = None):
        """
        Initialize QC controller

        Args:
            qc_service: The quality control service to use
            view_callback: Callback to update the view (optional)
        """
        self.qc_service = qc_service
        self.view_callback = view_callback
        self.analysis_history: List[Dict[str, Any]] = []

    def evaluate_result(self, analysis_result: AnalysisResult, recipe_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Evaluate an analysis result against quality control criteria

        Args:
            analysis_result: The analysis result to evaluate
            recipe_id: Optional recipe ID for context

        Returns:
            QC evaluation results if successful, None otherwise
        """
        try:
            evaluation = self.qc_service.evaluate_result(analysis_result, recipe_id)

            # Add to history
            analysis_with_qc = analysis_result.to_dict()
            analysis_with_qc['qc_evaluation'] = evaluation.to_dict() if hasattr(evaluation, 'to_dict') else evaluation
            self.analysis_history.append(analysis_with_qc)

            logger.info(f"QC evaluation completed: {evaluation.grade}")

            if self.view_callback:
                self.view_callback('qc_evaluated', analysis_result, evaluation)

            return evaluation.to_dict() if hasattr(evaluation, 'to_dict') else evaluation

        except Exception as e:
            error_msg = f"QC evaluation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def get_current_profile(self) -> Optional[QCProfile]:
        """
        Get the current QC profile

        Returns:
            Current QC profile if available
        """
        try:
            return self.qc_service.get_current_profile()
        except Exception as e:
            logger.error(f"Failed to get current QC profile: {e}")
            return None

    def set_bread_type(self, bread_type: str) -> bool:
        """
        Set the current bread type for QC evaluation

        Args:
            bread_type: Bread type name

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.qc_service.set_bread_type(bread_type)
            if success:
                logger.info(f"QC bread type set to: {bread_type}")

                if self.view_callback:
                    self.view_callback('bread_type_changed', bread_type)

            return success

        except Exception as e:
            logger.error(f"Failed to set bread type to {bread_type}: {e}")
            return False

    def get_available_bread_types(self) -> List[str]:
        """
        Get list of available bread types

        Returns:
            List of bread type names
        """
        try:
            bread_types = self.qc_service.get_all_bread_types()
            return list(bread_types.keys())
        except Exception as e:
            logger.error(f"Failed to get available bread types: {e}")
            return []

    def get_available_bread_type_labels(self) -> Dict[str, str]:
        """
        Get available bread type labels.

        Returns:
            Dict mapping bread type keys to display labels
        """
        try:
            return self.qc_service.get_all_bread_types()
        except Exception as e:
            logger.error(f"Failed to get bread type labels: {e}")
            return {}

    def get_batch_statistics(self, results: List[AnalysisResult]) -> Optional[Dict[str, Any]]:
        """
        Calculate batch statistics for quality control

        Args:
            results: List of analysis results

        Returns:
            Batch statistics if successful, None otherwise
        """
        try:
            stats = self.qc_service.get_batch_statistics(results)
            logger.info(f"Batch statistics calculated for {len(results)} results")

            if self.view_callback:
                self.view_callback('batch_stats_calculated', stats)

            return stats

        except Exception as e:
            logger.error(f"Failed to calculate batch statistics: {e}")
            return None

    def get_spc_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get Statistical Process Control statistics

        Returns:
            SPC statistics if available, None otherwise
        """
        try:
            spc_stats = self.qc_service.get_spc_statistics()
            logger.info("SPC statistics retrieved")

            if self.view_callback:
                self.view_callback('spc_stats_retrieved', spc_stats)

            return spc_stats

        except Exception as e:
            logger.error(f"Failed to get SPC statistics: {e}")
            return None

    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get current quality control alerts

        Returns:
            List of active alerts
        """
        try:
            alerts = self.qc_service.get_alerts()
            logger.info(f"Retrieved {len(alerts)} QC alerts")

            if self.view_callback:
                self.view_callback('alerts_retrieved', alerts)

            return alerts

        except Exception as e:
            logger.error(f"Failed to get QC alerts: {e}")
            return []

    def configure_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Configure a QC profile

        Args:
            profile_data: Profile configuration data

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.qc_service.configure_profile(profile_data)
            if success:
                logger.info("QC profile configured successfully")

                if self.view_callback:
                    self.view_callback('profile_configured', profile_data)

            return success

        except Exception as e:
            error_msg = f"Failed to configure QC profile: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False

    def add_bread_type(self, bread_type: str, profile_data: Dict[str, Any]) -> bool:
        """
        Add a new bread type profile

        Args:
            bread_type: Name of the bread type
            profile_data: Profile configuration data

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.qc_service.add_bread_type(bread_type, profile_data)
            if success:
                logger.info(f"New bread type added: {bread_type}")

                if self.view_callback:
                    self.view_callback('bread_type_added', bread_type, profile_data)

            return success

        except Exception as e:
            error_msg = f"Failed to add bread type {bread_type}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False

    def get_profile_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the current profile configuration as a dictionary

        Returns:
            Profile configuration dictionary if available
        """
        try:
            profile = self.get_current_profile()
            if profile:
                return profile.to_dict() if hasattr(profile, 'to_dict') else {}
            return None
        except Exception as e:
            logger.error(f"Failed to get profile config: {e}")
            return None

    def reset_to_defaults(self) -> bool:
        """
        Reset QC configuration to defaults

        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.qc_service.reset_to_defaults()
            if success:
                logger.info("QC configuration reset to defaults")

                if self.view_callback:
                    self.view_callback('config_reset')

            return success

        except Exception as e:
            error_msg = f"Failed to reset QC configuration: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False

    def format_evaluation_display(self, evaluation: Dict[str, Any]) -> str:
        """
        Format QC evaluation results for display

        Args:
            evaluation: QC evaluation results

        Returns:
            Formatted display string
        """
        try:
            output = "QUALITY CONTROL EVALUATION\n"
            output += "=" * 70 + "\n\n"

            # Acceptance status
            output += "ACCEPTANCE STATUS:\n"
            output += "-" * 70 + "\n"
            acceptance = evaluation.get('acceptance', {})
            output += f"  Porosity:    {' PASS' if acceptance.get('porosity_ok') else ' FAIL'}\n"
            output += f"  Holes:       {' PASS' if acceptance.get('holes_ok') else ' FAIL'}\n"
            output += f"  Uniformity:  {' PASS' if acceptance.get('uniformity_ok') else ' FAIL'}\n"
            output += f"  OVERALL:     {' ACCEPT' if acceptance.get('overall_ok') else '⚠  REVIEW NEEDED'}\n\n"

            output += f"QUALITY GRADE: {evaluation.get('grade', 'Unknown')}\n\n"

            # Scores
            output += "QUALITY SCORES:\n"
            output += "-" * 70 + "\n"
            scores = evaluation.get('scores', {})
            for param, score in scores.items():
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                output += f"  {param:15} {score:.2f}  [{bar}]\n"
            output += "\n"

            # Alerts
            alerts = evaluation.get('alerts', [])
            if alerts:
                output += "⚠  ALERTS:\n"
                output += "-" * 70 + "\n"
                for alert in alerts:
                    output += f"  {alert}\n"
                output += "\n"

            # Recommendations
            recommendations = evaluation.get('recommendations', [])
            if recommendations:
                output += "💡 RECOMMENDATIONS:\n"
                output += "-" * 70 + "\n"
                for rec in recommendations:
                    output += f"  {rec}\n"

            return output

        except Exception as e:
            logger.error(f"Failed to format QC evaluation: {e}")
            return f"Error formatting evaluation: {str(e)}"

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """
        Get the analysis history with QC evaluations

        Returns:
            List of historical analysis results with QC data
        """
        return self.analysis_history.copy()

    def clear_history(self) -> None:
        """Clear the analysis history"""
        self.analysis_history.clear()
        logger.info("Analysis history cleared")

        if self.view_callback:
            self.view_callback('history_cleared')
