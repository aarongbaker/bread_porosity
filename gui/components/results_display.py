"""
Results Display Component
Reusable component for displaying analysis results and metrics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Dict, Any, List
import json

from gui.theme import get_theme


class ResultsDisplay(ttk.Frame):
    """Component for displaying analysis results in various formats"""

    def __init__(self, parent, controller=None):
        """
        Initialize results display component

        Args:
            parent: Parent widget
            controller: Optional controller for handling events
        """
        super().__init__(parent)
        self.controller = controller
        self.theme = get_theme()
        colors = self.theme.colors

        # UI elements
        self.results_text: Optional[scrolledtext.ScrolledText] = None
        self.metrics_text: Optional[scrolledtext.ScrolledText] = None
        self.notebook: Optional[ttk.Notebook] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface"""
        colors = self.theme.colors
        
        # Create notebook for different result views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Results tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")

        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=colors.bg_secondary,
            fg=colors.text_primary,
            insertbackground=colors.bg_accent
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Metrics tab
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="Metrics")

        # Metrics text area
        self.metrics_text = scrolledtext.ScrolledText(
            metrics_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=colors.bg_secondary,
            fg=colors.text_primary,
            insertbackground=colors.bg_accent
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Set default content
        self.clear_results()

    def display_results(self, results: Dict[str, Any]) -> None:
        """
        Display analysis results

        Args:
            results: Analysis results dictionary
        """
        try:
            # Format results for display
            formatted_results = self._format_results(results)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_results)

            # Display metrics as JSON
            metrics_json = json.dumps(results.get('metrics', {}), indent=2)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, metrics_json)

            # Switch to results tab
            self.notebook.select(0)

        except Exception as e:
            self._show_error(f"Failed to display results: {str(e)}")

    def display_loaf_results(self, results: Dict[str, Any]) -> None:
        """
        Display loaf analysis results

        Args:
            results: Loaf analysis results dictionary
        """
        try:
            formatted_results = self._format_loaf_results(results)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_results)

            # Display full results as JSON
            results_json = json.dumps(results, indent=2)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, results_json)

            self.notebook.select(0)

        except Exception as e:
            self._show_error(f"Failed to display loaf results: {str(e)}")

    def display_qc_results(self, qc_results: Dict[str, Any]) -> None:
        """
        Display quality control results

        Args:
            qc_results: Quality control evaluation results
        """
        try:
            formatted_qc = self._format_qc_results(qc_results)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_qc)

            # Display QC data as JSON
            qc_json = json.dumps(qc_results, indent=2)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, qc_json)

            self.notebook.select(0)

        except Exception as e:
            self._show_error(f"Failed to display QC results: {str(e)}")

    def display_prediction_results(self, prediction: Dict[str, Any]) -> None:
        """
        Display prediction results

        Args:
            prediction: Prediction results dictionary
        """
        try:
            formatted_prediction = self._format_prediction_results(prediction)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_prediction)

            # Display prediction data as JSON
            pred_json = json.dumps(prediction, indent=2)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, pred_json)

            self.notebook.select(0)

        except Exception as e:
            self._show_error(f"Failed to display prediction results: {str(e)}")

    def display_defect_results(self, defect_report: Dict[str, Any]) -> None:
        """
        Display defect detection results

        Args:
            defect_report: Defect detection results
        """
        try:
            formatted_defects = self._format_defect_results(defect_report)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_defects)

            # Display defect data as JSON
            defect_json = json.dumps(defect_report, indent=2)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, defect_json)

            self.notebook.select(0)

        except Exception as e:
            self._show_error(f"Failed to display defect results: {str(e)}")

    def clear_results(self) -> None:
        """Clear all displayed results"""
        placeholder = "No results to display\n\nSelect an image and run analysis to see results here."

        if self.results_text:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, placeholder)

        if self.metrics_text:
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, "No metrics available")

    def _show_error(self, message: str) -> None:
        """Show error message"""
        error_text = f"ERROR: {message}"

        if self.results_text:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, error_text)

        if self.metrics_text:
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, error_text)

    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format single image analysis results"""
        try:
            output = "BREAD POROSITY ANALYSIS RESULTS\n"
            output += "=" * 50 + "\n\n"

            # Basic info
            image_path = results.get('image_path', 'Unknown')
            output += f"Image: {image_path}\n"
            processing_time = results.get('processing_time_sec')
            if isinstance(processing_time, (int, float)):
                output += f"Analysis Time: {processing_time:.2f}s\n\n"
            else:
                output += "Analysis Time: N/A\n\n"

            # Metrics
            metrics = results.get('metrics', {})
            if metrics:
                output += "POROSITY METRICS:\n"
                output += "-" * 30 + "\n"
                output += f"Porosity:     {metrics.get('porosity_percent', 'N/A'):.1f}%\n"
                output += f"Hole Count:   {metrics.get('hole_count_total', 'N/A')}\n"
                output += f"Mean Diameter: {metrics.get('hole_diameter_mean_mm', 'N/A'):.2f} mm\n"
                output += f"Std Diameter:  {metrics.get('hole_diameter_std_mm', 'N/A'):.2f} mm\n"
                output += f"Min Diameter:  {metrics.get('hole_diameter_min_mm', 'N/A'):.2f} mm\n"
                output += f"Max Diameter:  {metrics.get('hole_diameter_max_mm', 'N/A'):.2f} mm\n"
                output += f"Holes/cm²:     {metrics.get('holes_per_cm2', 'N/A'):.1f}\n\n"

                # Shape analysis
                output += "SHAPE ANALYSIS:\n"
                output += "-" * 30 + "\n"
                output += f"Anisotropy:   {metrics.get('anisotropy_ratio', 'N/A'):.2f}\n"
                output += f"Orientation:  {metrics.get('orientation_mean_deg', 'N/A'):.1f}°\n"
                output += f"Uniformity:   {metrics.get('uniformity_score', 'N/A'):.2f}\n\n"

            return output

        except Exception as e:
            return f"Error formatting results: {str(e)}"

    def _format_loaf_results(self, results: Dict[str, Any]) -> str:
        """Format loaf analysis results"""
        try:
            output = f"LOAF ANALYSIS RESULTS\n{'='*50}\n\n"
            output += f"Loaf: {results.get('loaf_name', 'Unknown')}\n"
            output += f"Slices analyzed: {results.get('num_slices', 0)}\n\n"

            # Porosity analysis
            porosity = results.get('porosity', {})
            if porosity:
                output += "POROSITY ANALYSIS\n────────────────────────────────\n"
                output += f"  Mean:           {porosity.get('mean', 'N/A'):.1f}%\n"
                output += f"  Std deviation:  {porosity.get('std', 'N/A'):.1f}%\n"
                output += f"  Min:            {porosity.get('min', 'N/A'):.1f}%\n"
                output += f"  Max:            {porosity.get('max', 'N/A'):.1f}%\n"
                output += f"  Range:          {porosity.get('range', 'N/A'):.1f}%\n\n"

            # Hole analysis
            holes = results.get('holes', {})
            if holes:
                output += "HOLE ANALYSIS\n────────────────────────────────\n"
                output += f"  Mean hole count:    {holes.get('mean_count', 'N/A'):.0f}\n"
                output += f"  Mean diameter:      {holes.get('mean_diameter_mm', 'N/A'):.2f} mm\n\n"

            # Shape analysis
            shape = results.get('shape', {})
            if shape:
                output += "SHAPE ANALYSIS\n────────────────────────────────\n"
                output += f"  Mean aspect ratio:  {shape.get('mean_aspect_ratio', 'N/A'):.2f}\n\n"

            # Slice-by-slice
            slices = results.get('slices', [])
            if slices:
                output += "SLICE-BY-SLICE\n────────────────────────────────\n"
                output += f"{'Slice':<8} {'Porosity':<12} {'Holes':<10} {'Diameter':<12}\n"
                output += "-" * 50 + "\n"

                for slice_data in slices:
                    output += f"{slice_data.get('slice', ''):<8} "
                    output += f"{slice_data.get('porosity', 0):<11.1f}% "
                    output += f"{slice_data.get('num_holes', 0):<10.0f} "
                    output += f"{slice_data.get('mean_diameter_mm', 0):<11.2f}mm\n"

            return output

        except Exception as e:
            return f"Error formatting loaf results: {str(e)}"

    def _format_qc_results(self, qc_results: Dict[str, Any]) -> str:
        """Format QC evaluation results"""
        try:
            output = "QUALITY CONTROL EVALUATION\n"
            output += "=" * 70 + "\n\n"

            output += f"QUALITY GRADE: {qc_results.get('grade', 'Unknown')}\n"
            output += f"PASSED: {'YES' if qc_results.get('passed') else 'NO'}\n"
            output += f"BREAD TYPE: {qc_results.get('bread_type', 'Unknown')}\n\n"

            # Scores
            scores = qc_results.get('scores', {})
            if scores:
                output += "QUALITY SCORES:\n"
                output += "-" * 70 + "\n"
                for param, score in scores.items():
                    bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                    output += f"  {param:15} {score:.2f}  [{bar}]\n"
                output += "\n"

            # Alerts
            alerts = qc_results.get('alerts', [])
            if alerts:
                output += "⚠  ALERTS:\n"
                output += "-" * 70 + "\n"
                for alert in alerts:
                    output += f"  {alert}\n"
                output += "\n"

            # Recommendations
            recommendations = qc_results.get('recommendations', [])
            if recommendations:
                output += "💡 RECOMMENDATIONS:\n"
                output += "-" * 70 + "\n"
                for rec in recommendations:
                    output += f"  {rec}\n"

            return output

        except Exception as e:
            return f"Error formatting QC results: {str(e)}"

    def _format_prediction_results(self, prediction: Dict[str, Any]) -> str:
        """Format prediction results"""
        try:
            recipe_name = prediction.get('recipe_name', 'Unknown')
            output = f"POROSITY PREDICTION FOR: {recipe_name}\n"
            output += "=" * 50 + "\n\n"

            predicted_porosity = prediction.get('predicted_porosity', 'N/A')
            output += "PREDICTED POROSITY: "
            if isinstance(predicted_porosity, (int, float)):
                output += f"{predicted_porosity:.1f}%\n\n"
            else:
                output += f"{predicted_porosity}%\n\n"

            # Confidence information
            confidence_info = prediction.get('confidence_info', {})
            if confidence_info:
                output += "CONFIDENCE LEVEL:\n"
                output += f"  {confidence_info.get('confidence_level', 'Unknown')}\n"
                output += f"  Training samples: {confidence_info.get('training_samples', 0)}\n"

                mean_porosity = confidence_info.get('mean_porosity')
                if mean_porosity is not None:
                    output += f"  Mean porosity: {mean_porosity:.1f}%\n"

                output += "\n"

            # Feature contributions
            contributions = confidence_info.get('feature_contributions', {})
            if contributions:
                output += "FEATURE CONTRIBUTIONS:\n"
                for feature, contribution in contributions.items():
                    output += f"  {feature:20} {contribution:+.3f}\n"
                output += "\n"

            # Actual vs predicted comparison
            actual_porosity = prediction.get('actual_porosity')
            if actual_porosity is not None:
                output += f"ACTUAL MEASURED: {actual_porosity:.1f}%\n"
                if isinstance(predicted_porosity, (int, float)):
                    error = abs(predicted_porosity - actual_porosity)
                    output += f"PREDICTION ERROR: {error:.1f}%\n"

            return output

        except Exception as e:
            return f"Error formatting prediction results: {str(e)}"

    def _format_defect_results(self, defect_report: Dict[str, Any]) -> str:
        """Format defect detection results"""
        try:
            output = "DEFECT DETECTION REPORT\n"
            output += "=" * 50 + "\n\n"

            severity_score = defect_report.get('severity_score')
            if severity_score is None:
                severity_score = defect_report.get('overall_severity', 0)
            severity_level = self._get_severity_level(severity_score)

            output += f"OVERALL SEVERITY: {severity_level} ({severity_score:.1f}/100)\n\n"

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
                uneven_rise = defect_report.get('uneven_rise', {})
                dense_spots = defect_report.get('dense_spots', {})
                if uneven_rise or dense_spots:
                    output += "DEFECT SUMMARY:\n"
                    output += "-" * 50 + "\n"
                    output += f"Uneven rise detected: {uneven_rise.get('detected', False)}\n"
                    output += f"Dense spots detected: {dense_spots.get('detected', False)}\n\n"
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

            return output

        except Exception as e:
            return f"Error formatting defect results: {str(e)}"

    def _get_severity_level(self, score: float) -> str:
        """Convert severity score to level description"""
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
