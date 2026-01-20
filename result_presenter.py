"""
Result Presenter
Formats analysis results for display in simple or advanced mode.
Includes interpretation guide and quality grading.
"""

from typing import Dict, Any


class ResultPresenter:
    """Format and present analysis results to users."""
    
    def __init__(self, simple_mode: bool = True):
        self.simple_mode = simple_mode
    
    def format_results(self, analysis_result: Dict[str, Any]) -> str:
        """
        Format analysis results for display.
        
        Args:
            analysis_result: Dict from analyze_bread_image()
        
        Returns:
            Formatted string for display
        """
        if self.simple_mode:
            return self._format_simple_view(analysis_result)
        else:
            return self._format_advanced_view(analysis_result)
    
    def _format_simple_view(self, result: Dict) -> str:
        """Format results for beginner users - simplified view."""
        metrics = result.get('metrics', {})
        porosity = metrics.get('porosity_percent', 0)
        holes = metrics.get('num_holes', 0)
        uniformity = metrics.get('uniformity_score', 0.5)
        
        # Grade the bread
        grade, grade_emoji = self._calculate_grade(porosity, holes, uniformity)
        
        # Interpret porosity
        porosity_interpretation = self._interpret_porosity(porosity)
        
        output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    BREAD POROSITY ANALYSIS RESULTS                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

OVERALL GRADE: {grade_emoji}  {grade}
{"─"*80}

📊 KEY MEASUREMENTS
  • Porosity:          {porosity:.1f}%  →  {porosity_interpretation}
  • Hole Count:        {holes}  holes
  • Uniformity Score:  {uniformity:.2f}  →  {self._interpret_uniformity(uniformity)}

{"─"*80}

💡 WHAT THIS MEANS

Porosity {porosity:.1f}%:
  {self._detailed_porosity_guide(porosity)}

Hole Count {holes}:
  {self._detailed_hole_count_guide(holes)}

Uniformity {uniformity:.2f}:
  {self._detailed_uniformity_guide(uniformity)}

{"─"*80}

✨ QUALITY ASSESSMENT

Grade:        {grade}  ({grade_emoji})
Classification: {self._classify_crumb_type(porosity, holes)}
Quality Level:  {self._quality_level(grade)}

{"─"*80}

📁 OUTPUT FILES
  ✓ Annotated image (holes highlighted)
  ✓ Processing comparison (6 stages)
  ✓ Hole distribution charts
  ✓ Detailed metrics JSON

See "Results" tab for detailed statistics.
"""
        return output
    
    def _format_advanced_view(self, result: Dict) -> str:
        """Format complete results with all metrics."""
        metrics = result.get('metrics', {})
        
        output = f"""
BREAD POROSITY ANALYSIS - COMPLETE RESULTS
{'='*80}

IMAGE: {result.get('image_path', 'Unknown')}
Pixel Size: {result.get('pixel_size_mm', 0.1):.2f} mm
Processing Method: {result.get('threshold_method', 'otsu')}

POROSITY & STRUCTURE
{'─'*80}
  Porosity:                  {metrics.get('porosity_percent', 0):.2f}%
  Hole pixels:               {metrics.get('hole_pixels', 0):,}
  Crumb pixels:              {metrics.get('crumb_pixels', 0):,}
  ROI area:                  {metrics.get('roi_area_cm2', 0):.2f} cm²

HOLE METRICS
{'─'*80}
  Total holes:               {metrics.get('num_holes', 0)}
  Holes per cm²:             {metrics.get('holes_per_cm2', 0):.1f}
  Mean diameter:             {metrics.get('mean_hole_diameter_mm', 0):.2f} mm
  Max diameter:              {metrics.get('largest_hole_diameter_mm', 0):.2f} mm
  Min diameter:              {metrics.get('smallest_hole_diameter_mm', 0):.2f} mm
  Diameter std dev:          {metrics.get('hole_diameter_std_mm', 0):.2f} mm
  Hole area CV:              {metrics.get('hole_area_cv', 0):.3f}

SHAPE ANALYSIS
{'─'*80}
  Mean aspect ratio:         {metrics.get('mean_aspect_ratio', 0):.2f}
  Aspect ratio std:          {metrics.get('aspect_ratio_std', 0):.2f}
  Mean orientation:          {metrics.get('mean_orientation_deg', 0):.1f}°
  Orientation entropy:       {metrics.get('orientation_entropy', 0):.2f} / 4.17

CRUMB UNIFORMITY
{'─'*80}
  Brightness mean:           {metrics.get('crumb_brightness_mean', 0):.1f}
  Brightness std:            {metrics.get('crumb_brightness_std', 0):.1f}
  Brightness CV:             {metrics.get('crumb_brightness_cv', 0):.3f}
  Brightness skewness:       {metrics.get('crumb_brightness_skewness', 0):.2f}
  Uniformity score:          {metrics.get('uniformity_score', 0):.2f}

OUTPUT FILES
{'─'*80}
  ✓ comparison.png          (processing stages)
  ✓ hole_distribution.png   (charts)
  ✓ annotated.png           (highlighted holes)
  ✓ metrics.json            (complete data)
"""
        return output
    
    def _calculate_grade(self, porosity: float, holes: int, uniformity: float) -> tuple:
        """
        Calculate bread quality grade.
        
        Returns:
            (grade_name, emoji)
        """
        # Scoring system
        porosity_score = self._score_porosity(porosity)
        holes_score = self._score_holes(holes)
        uniformity_score = min(uniformity, 1.0)
        
        # Average scores
        overall_score = (porosity_score + holes_score + uniformity_score) / 3
        
        if overall_score >= 0.85:
            return ("EXCELLENT", "⭐⭐⭐⭐⭐")
        elif overall_score >= 0.70:
            return ("GOOD", "⭐⭐⭐⭐")
        elif overall_score >= 0.55:
            return ("FAIR", "⭐⭐⭐")
        elif overall_score >= 0.40:
            return ("POOR", "⭐⭐")
        else:
            return ("VERY POOR", "⭐")
    
    def _score_porosity(self, porosity: float) -> float:
        """Score porosity (most breads want 20-45%)."""
        if 20 <= porosity <= 45:
            return 1.0
        elif 15 <= porosity <= 55:
            return 0.80
        elif 10 <= porosity <= 65:
            return 0.60
        else:
            return 0.30
    
    def _score_holes(self, hole_count: int) -> float:
        """Score hole count (most breads want 80-300 holes)."""
        if 80 <= hole_count <= 300:
            return 1.0
        elif 50 <= hole_count <= 400:
            return 0.80
        elif 30 <= hole_count <= 500:
            return 0.60
        else:
            return 0.30
    
    def _interpret_porosity(self, porosity: float) -> str:
        """One-line interpretation of porosity."""
        if porosity < 10:
            return "Very dense crumb"
        elif porosity < 20:
            return "Dense crumb structure"
        elif porosity < 35:
            return "Open, well-fermented crumb"
        elif porosity < 50:
            return "Very open crumb structure"
        else:
            return "Extremely open/airy crumb"
    
    def _interpret_uniformity(self, uniformity: float) -> str:
        """One-line interpretation of uniformity."""
        if uniformity < 0.6:
            return "Uneven crumb"
        elif uniformity < 0.75:
            return "Somewhat uneven"
        elif uniformity < 0.85:
            return "Mostly uniform"
        else:
            return "Very uniform crumb"
    
    def _detailed_porosity_guide(self, porosity: float) -> str:
        """Detailed explanation of what porosity means."""
        if porosity < 15:
            return ("Dense crumb. Fermentation may have been insufficient,\n  "
                   "or dough was mixed too much. Typical for sandwich breads.")
        elif porosity < 25:
            return ("Closed crumb. Good for sandwich/toast breads.\n  "
                   "Can improve with: longer fermentation, better shaping, less mixing.")
        elif porosity < 35:
            return ("Well-balanced open crumb. Typical for good artisan breads.\n  "
                   "This is the target for sourdough and baguettes.")
        elif porosity < 50:
            return ("Very open crumb. High fermentation/hydration.\n  "
                   "Typical for ciabatta or high-hydration sourdough.")
        else:
            return ("Extremely open crumb. Either very high hydration/fermentation,\n  "
                   "or image quality issues. Check if analysis is accurate.")
    
    def _detailed_hole_count_guide(self, holes: int) -> str:
        """Detailed explanation of hole count."""
        if holes < 50:
            return ("Few large holes. Dense fermentation or poor shaping.\n  "
                   "Expect more holes with better fermentation.")
        elif holes < 100:
            return ("Moderate hole count. Some fine crumb with larger holes.\n  "
                   "Typical for less fermented breads.")
        elif holes < 200:
            return ("Good hole distribution. Well-fermented.\n  "
                   "Typical for well-made sourdough and artisan breads.")
        elif holes < 400:
            return ("High hole count. Very well-fermented or high-hydration dough.\n  "
                   "Typical for ciabatta and very open breads.")
        else:
            return ("Extremely high hole count. Likely high hydration/fermentation.\n  "
                   "May indicate over-fermentation if crust is weak.")
    
    def _detailed_uniformity_guide(self, uniformity: float) -> str:
        """Detailed explanation of uniformity."""
        if uniformity < 0.6:
            return ("Uneven crumb - some areas tight, some areas open.\n  "
                   "Causes: uneven fermentation, cold spots in oven, poor shaping.")
        elif uniformity < 0.75:
            return ("Somewhat uneven - mostly consistent with some variation.\n  "
                   "Check: fermentation temperature, oven hot spots, shaping consistency.")
        elif uniformity < 0.85:
            return ("Mostly uniform crumb across the loaf.\n  "
                   "This is good for most artisan breads.")
        else:
            return ("Very uniform crumb - consistent throughout.\n  "
                   "Excellent consistency, typical of commercial/sandwich breads.")
    
    def _classify_crumb_type(self, porosity: float, holes: int) -> str:
        """Classify type of crumb based on metrics."""
        if porosity < 20 and holes < 80:
            return "Sandwich/Pan Bread (dense, fine crumb)"
        elif 20 <= porosity < 35 and 80 <= holes < 200:
            return "Artisan/Sourdough (balanced open crumb)"
        elif 35 <= porosity < 50 and 200 <= holes < 400:
            return "Ciabatta/Focaccia (very open crumb)"
        else:
            return "Non-standard crumb structure"
    
    def _quality_level(self, grade: str) -> str:
        """Map grade to production quality level."""
        grade_map = {
            "EXCELLENT": "Meets premium standards - excellent for sale/competition",
            "GOOD": "Acceptable quality - suitable for sale",
            "FAIR": "Acceptable but could improve",
            "POOR": "Below standard - needs process adjustment",
            "VERY POOR": "Unacceptable - significant process issues"
        }
        return grade_map.get(grade, "Unknown")
    
    def toggle_mode(self) -> None:
        """Toggle between simple and advanced view."""
        self.simple_mode = not self.simple_mode
