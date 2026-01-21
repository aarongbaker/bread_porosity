"""
Defect Controller
Handles defect detection operations and coordinates with DefectService
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any, Callable, List, Union
import json

from services.defect_service import DefectService
from models.analysis_result import AnalysisResult
from utils.logger import get_logger

logger = get_logger(__name__)


class DefectController:
    """Controller for defect detection operations"""

    def __init__(self, defect_service: DefectService, view_callback: Optional[Callable] = None):
        """
        Initialize defect controller

        Args:
            defect_service: The defect service to use
            view_callback: Callback to update the view (optional)
        """
        self.defect_service = defect_service
        self.view_callback = view_callback
        self.last_defect_report: Optional[Dict[str, Any]] = None

    def detect_defects(self, analysis_result: Union[AnalysisResult, str]) -> Optional[Dict[str, Any]]:
        """
        Detect defects in an analysis result

        Args:
            analysis_result: The analysis result or image path to check for defects

        Returns:
            Defect report if successful, None otherwise
        """
        try:
            image_path = (
                analysis_result.image_path
                if isinstance(analysis_result, AnalysisResult)
                else analysis_result
            )
            defect_report = self.defect_service.detect_defects(image_path)
            report_dict = defect_report.to_dict() if hasattr(defect_report, 'to_dict') else defect_report
            self.last_defect_report = report_dict

            if report_dict:
                defect_count = len(report_dict.get('defects', []))
                logger.info(f"Defect detection completed: {defect_count} defects found")

                if self.view_callback:
                    self.view_callback('defects_detected', analysis_result, report_dict)

            return report_dict

        except Exception as e:
            error_msg = f"Defect detection failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def analyze_defect_patterns(self, results: List[AnalysisResult]) -> Optional[Dict[str, Any]]:
        """
        Analyze defect patterns across multiple results

        Args:
            results: List of analysis results to analyze

        Returns:
            Pattern analysis results if successful, None otherwise
        """
        try:
            pattern_analysis = self.defect_service.analyze_defect_patterns(results)

            if pattern_analysis:
                logger.info(f"Defect pattern analysis completed for {len(results)} results")

                if self.view_callback:
                    self.view_callback('patterns_analyzed', pattern_analysis)

            return pattern_analysis

        except Exception as e:
            error_msg = f"Defect pattern analysis failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def get_defect_types(self) -> List[Dict[str, str]]:
        """
        Get available defect types

        Returns:
            List of defect type dictionaries
        """
        return [
            {'id': 'uneven_rise', 'name': 'Uneven Rise', 'description': 'Inconsistent crumb development'},
            {'id': 'dense_spots', 'name': 'Dense Spots', 'description': 'Under-fermented areas'},
            {'id': 'large_holes', 'name': 'Large Holes', 'description': 'Oversized air pockets'},
            {'id': 'collapsed_structure', 'name': 'Collapsed Structure', 'description': 'Structural failure'},
            {'id': 'crust_separation', 'name': 'Crust Separation', 'description': 'Crust detaching from crumb'}
        ]

    def get_last_defect_report(self) -> Optional[Dict[str, Any]]:
        """
        Get the last defect detection report

        Returns:
            Last defect report
        """
        return self.last_defect_report

    def format_defect_display(self, defect_report: Dict[str, Any]) -> str:
        """
        Format defect report for display

        Args:
            defect_report: Defect detection results

        Returns:
            Formatted display string
        """
        try:
            output = "DEFECT DETECTION REPORT\n"
            output += "=" * 50 + "\n\n"

            # Overall assessment
            severity_score = defect_report.get('severity_score', 0)
            severity_level = self._get_severity_level(severity_score)

            output += f"OVERALL SEVERITY: {severity_level} ({severity_score:.1f}/100)\n\n"

            # Individual defects
            defects = defect_report.get('defects', [])
            if defects:
                output += f"DETECTED DEFECTS ({len(defects)}):\n"
                output += "-" * 50 + "\n"

                for i, defect in enumerate(defects, 1):
                    defect_type = defect.get('type', 'Unknown')
                    confidence = defect.get('confidence', 0)
                    severity = defect.get('severity', 0)

                    output += f"{i}. {defect_type}\n"
                    output += f"   Confidence: {confidence:.1f}%\n"
                    output += f"   Severity: {severity:.1f}/10\n"

                    location = defect.get('location')
                    if location:
                        output += f"   Location: {location}\n"

                    description = defect.get('description')
                    if description:
                        output += f"   Description: {description}\n"

                    output += "\n"
            else:
                output += "✅ No significant defects detected\n\n"

            # Recommendations
            recommendations = defect_report.get('recommendations', [])
            if recommendations:
                output += "RECOMMENDATIONS:\n"
                output += "-" * 50 + "\n"
                for rec in recommendations:
                    output += f"• {rec}\n"
                output += "\n"

            # Pattern analysis if available
            patterns = defect_report.get('patterns', {})
            if patterns:
                output += "PATTERN ANALYSIS:\n"
                output += "-" * 50 + "\n"

                common_defects = patterns.get('common_defects', [])
                if common_defects:
                    output += "Most common defects:\n"
                    for defect_type, count in common_defects[:3]:
                        output += f"  {defect_type}: {count} occurrences\n"

                trends = patterns.get('trends', [])
                if trends:
                    output += "\nDetected trends:\n"
                    for trend in trends:
                        output += f"  • {trend}\n"

            return output

        except Exception as e:
            logger.error(f"Failed to format defect display: {e}")
            return f"Error formatting defect report: {str(e)}"

    def _get_severity_level(self, score: float) -> str:
        """
        Convert severity score to level description

        Args:
            score: Severity score (0-100)

        Returns:
            Severity level description
        """
        if score < 20:
            return "Excellent"
        elif score < 40:
            return "Good"
        elif score < 60:
            return "Fair"
        elif score < 80:
            return "Poor"
        else:
            return "Critical"

    def get_defect_statistics(self, results: List[AnalysisResult]) -> Optional[Dict[str, Any]]:
        """
        Calculate defect statistics across multiple results

        Args:
            results: List of analysis results

        Returns:
            Defect statistics if successful, None otherwise
        """
        try:
            # Detect defects for all results
            defect_reports = []
            for result in results:
                report = self.detect_defects(result)
                if report:
                    defect_reports.append(report)

            if not defect_reports:
                return None

            # Calculate statistics
            total_defects = sum(len(r.get('defects', [])) for r in defect_reports)
            avg_severity = sum(r.get('severity_score', 0) for r in defect_reports) / len(defect_reports)

            # Count defect types
            defect_type_counts = {}
            for report in defect_reports:
                for defect in report.get('defects', []):
                    defect_type = defect.get('type', 'Unknown')
                    defect_type_counts[defect_type] = defect_type_counts.get(defect_type, 0) + 1

            stats = {
                'total_results': len(results),
                'results_with_defects': len([r for r in defect_reports if r.get('defects')]),
                'total_defects': total_defects,
                'average_severity': avg_severity,
                'defect_types': defect_type_counts,
                'most_common_defect': max(defect_type_counts.items(), key=lambda x: x[1]) if defect_type_counts else None
            }

            logger.info(f"Defect statistics calculated for {len(results)} results")
            return stats

        except Exception as e:
            logger.error(f"Failed to calculate defect statistics: {e}")
            return None

    def export_defect_report(self, defect_report: Dict[str, Any], filename: str) -> bool:
        """
        Export defect report to file

        Args:
            defect_report: Defect report to export
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                json.dump(defect_report, f, indent=2)

            logger.info(f"Defect report exported to: {filename}")

            if self.view_callback:
                self.view_callback('defect_report_exported', filename)

            return True

        except Exception as e:
            logger.error(f"Failed to export defect report: {e}")
            return False

    def clear_last_report(self) -> None:
        """Clear the last defect report"""
        self.last_defect_report = None

        if self.view_callback:
            self.view_callback('defect_report_cleared')
