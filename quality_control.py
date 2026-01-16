"""
Quality Control Module for Bread Porosity Analysis Tool
Statistical process control, thresholds, alerts, and acceptance criteria.
Supports multiple bread type profiles with different quality standards.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class QualityControlManager:
    """Manage quality control thresholds, alerts, and acceptance criteria."""
    
    def __init__(self, config_file: str = "qc_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.current_bread_type = "sourdough"  # Default bread type
        self.alerts = deque(maxlen=100)  # Keep last 100 alerts
        self.history = deque(maxlen=500)  # Keep last 500 measurements
    
    def _load_config(self) -> Dict[str, Any]:
        """Load quality control configuration with bread type profiles."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load QC config: {e}. Using defaults.")
        
        # Default configuration with multiple bread type profiles
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with bread type profiles."""
        return {
            "current_bread_type": "sourdough",
            "bread_types": {
                "sourdough": {
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
                        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                    }
                },
                "whole_wheat": {
                    "display_name": "Whole Wheat",
                    "porosity_target_min": 15.0,
                    "porosity_target_max": 28.0,
                    "porosity_warning_min": 12.0,
                    "porosity_warning_max": 32.0,
                    "hole_count_target_min": 60,
                    "hole_count_target_max": 250,
                    "hole_diameter_target_min": 1.5,
                    "hole_diameter_target_max": 6.0,
                    "uniformity_acceptable_min": 0.65,
                    "consistency_cv_max": 0.18,
                    "quality_grades": {
                        "excellent": {"porosity": [20, 26], "uniformity": [0.80, 1.0]},
                        "good": {"porosity": [16, 28], "uniformity": [0.70, 0.90]},
                        "fair": {"porosity": [12, 32], "uniformity": [0.60, 0.80]},
                        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                    }
                },
                "ciabatta": {
                    "display_name": "Ciabatta",
                    "porosity_target_min": 30.0,
                    "porosity_target_max": 45.0,
                    "porosity_warning_min": 28.0,
                    "porosity_warning_max": 48.0,
                    "hole_count_target_min": 200,
                    "hole_count_target_max": 600,
                    "hole_diameter_target_min": 3.0,
                    "hole_diameter_target_max": 12.0,
                    "uniformity_acceptable_min": 0.6,
                    "consistency_cv_max": 0.20,
                    "quality_grades": {
                        "excellent": {"porosity": [35, 42], "uniformity": [0.80, 1.0]},
                        "good": {"porosity": [30, 45], "uniformity": [0.70, 0.90]},
                        "fair": {"porosity": [28, 48], "uniformity": [0.60, 0.80]},
                        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                    }
                },
                "sandwich": {
                    "display_name": "Sandwich Bread",
                    "porosity_target_min": 12.0,
                    "porosity_target_max": 22.0,
                    "porosity_warning_min": 10.0,
                    "porosity_warning_max": 25.0,
                    "hole_count_target_min": 50,
                    "hole_count_target_max": 200,
                    "hole_diameter_target_min": 1.0,
                    "hole_diameter_target_max": 4.0,
                    "uniformity_acceptable_min": 0.75,
                    "consistency_cv_max": 0.12,
                    "quality_grades": {
                        "excellent": {"porosity": [15, 20], "uniformity": [0.85, 1.0]},
                        "good": {"porosity": [12, 22], "uniformity": [0.75, 0.95]},
                        "fair": {"porosity": [10, 25], "uniformity": [0.65, 0.85]},
                        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                    }
                },
                "baguette": {
                    "display_name": "Baguette",
                    "porosity_target_min": 25.0,
                    "porosity_target_max": 40.0,
                    "porosity_warning_min": 22.0,
                    "porosity_warning_max": 43.0,
                    "hole_count_target_min": 150,
                    "hole_count_target_max": 500,
                    "hole_diameter_target_min": 2.5,
                    "hole_diameter_target_max": 10.0,
                    "uniformity_acceptable_min": 0.65,
                    "consistency_cv_max": 0.16,
                    "quality_grades": {
                        "excellent": {"porosity": [30, 37], "uniformity": [0.80, 1.0]},
                        "good": {"porosity": [25, 40], "uniformity": [0.70, 0.90]},
                        "fair": {"porosity": [22, 43], "uniformity": [0.60, 0.80]},
                        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                    }
                },
                "custom": {
                    "display_name": "Custom Profile",
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
                        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
                    }
                }
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"QC config saved: {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving QC config: {e}")
    
    def set_bread_type(self, bread_type: str) -> bool:
        """
        Set the current bread type for quality standards.
        
        Args:
            bread_type: Bread type key (sourdough, whole_wheat, ciabatta, etc.)
            
        Returns:
            True if successful, False if bread type not found
        """
        bread_types = self.config.get('bread_types', {})
        if bread_type not in bread_types:
            logger.warning(f"Bread type '{bread_type}' not found. Available: {list(bread_types.keys())}")
            return False
        
        self.current_bread_type = bread_type
        self.config['current_bread_type'] = bread_type
        logger.info(f"Bread type switched to: {bread_type}")
        return True
    
    def get_current_profile(self) -> Dict[str, Any]:
        """Get the current bread type profile."""
        bread_types = self.config.get('bread_types', {})
        return bread_types.get(self.current_bread_type, bread_types.get('sourdough'))
    
    def get_all_bread_types(self) -> Dict[str, str]:
        """Get all available bread types and their display names."""
        bread_types = self.config.get('bread_types', {})
        return {key: profile.get('display_name', key) for key, profile in bread_types.items()}
    
    def add_bread_type(self, bread_type_key: str, profile: Dict[str, Any]) -> bool:
        """
        Add a new custom bread type profile.
        
        Args:
            bread_type_key: Key for the new bread type
            profile: Profile configuration dictionary
            
        Returns:
            True if successful
        """
        if 'bread_types' not in self.config:
            self.config['bread_types'] = {}
        
        if bread_type_key in self.config['bread_types']:
            logger.warning(f"Bread type '{bread_type_key}' already exists")
            return False
        
        # Ensure required fields
        if 'display_name' not in profile:
            profile['display_name'] = bread_type_key.replace('_', ' ').title()
        
        self.config['bread_types'][bread_type_key] = profile
        self.save_config()
        logger.info(f"Added new bread type: {bread_type_key}")
        return True
    
    def update_threshold(self, parameter: str, min_val: Optional[float] = None, 
                        max_val: Optional[float] = None, bread_type: Optional[str] = None):
        """
        Update a quality threshold for a specific bread type.
        
        Args:
            parameter: Parameter name (e.g., 'porosity_target_min')
            min_val: Minimum acceptable value
            max_val: Maximum acceptable value
            bread_type: Bread type to update (None = current bread type)
        """
        if bread_type is None:
            bread_type = self.current_bread_type
        
        if 'bread_types' not in self.config:
            self.config['bread_types'] = {}
        
        if bread_type not in self.config['bread_types']:
            logger.error(f"Bread type '{bread_type}' not found")
            return
        
        profile = self.config['bread_types'][bread_type]
        
        if min_val is not None:
            profile[f"{parameter}_min"] = min_val
        if max_val is not None:
            profile[f"{parameter}_max"] = max_val
        
        self.save_config()
        logger.info(f"Updated {bread_type} threshold {parameter}: min={min_val}, max={max_val}")
    
    def evaluate_analysis(self, metrics: Dict[str, Any], 
                         recipe_id: Optional[int] = None, 
                         bread_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive quality evaluation of an analysis.
        
        Args:
            metrics: Metrics dictionary from analysis
            recipe_id: Optional recipe ID for tracking
            bread_type: Bread type profile to use (None = current bread type)
            
        Returns:
            Dictionary with acceptance status, grade, and alerts
        """
        # Use specified bread type or current default
        if bread_type is not None:
            self.set_bread_type(bread_type)
        
        # Get the profile for this bread type
        profile = self.get_current_profile()
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "recipe_id": recipe_id,
            "bread_type": self.current_bread_type,
            "metrics": metrics,
            "acceptance": {
                "porosity_ok": False,
                "holes_ok": False,
                "uniformity_ok": False,
                "overall_ok": False,
            },
            "grade": "unknown",
            "alerts": [],
            "scores": {},
            "recommendations": [],
        }
        
        try:
            # Check porosity
            porosity = metrics.get('porosity_percent', 0)
            porosity_target_min = profile['porosity_target_min']
            porosity_target_max = profile['porosity_target_max']
            porosity_warning_min = profile['porosity_warning_min']
            porosity_warning_max = profile['porosity_warning_max']
            
            if porosity_target_min <= porosity <= porosity_target_max:
                evaluation['acceptance']['porosity_ok'] = True
                evaluation['scores']['porosity'] = 1.0
            elif porosity_warning_min <= porosity <= porosity_warning_max:
                evaluation['alerts'].append(
                    f"⚠️  Porosity {porosity:.1f}% outside target [{porosity_target_min}, {porosity_target_max}], "
                    f"but within warning range [{porosity_warning_min}, {porosity_warning_max}]"
                )
                evaluation['scores']['porosity'] = 0.7
            else:
                evaluation['alerts'].append(
                    f"❌ Porosity {porosity:.1f}% outside acceptable range [{porosity_warning_min}, {porosity_warning_max}]"
                )
                evaluation['scores']['porosity'] = 0.3
            
            # Check hole metrics
            hole_count = metrics.get('num_holes', 0)
            hole_count_min = profile['hole_count_target_min']
            hole_count_max = profile['hole_count_target_max']
            
            if hole_count_min <= hole_count <= hole_count_max:
                evaluation['acceptance']['holes_ok'] = True
                evaluation['scores']['holes'] = 1.0
            else:
                if hole_count < hole_count_min:
                    evaluation['alerts'].append(
                        f"⚠️  Hole count {hole_count} below target minimum {hole_count_min}"
                    )
                else:
                    evaluation['alerts'].append(
                        f"⚠️  Hole count {hole_count} above target maximum {hole_count_max}"
                    )
                evaluation['scores']['holes'] = 0.6
            
            # Check uniformity
            uniformity = metrics.get('uniformity_score', 0.5)
            uniformity_min = profile['uniformity_acceptable_min']
            
            if uniformity >= uniformity_min:
                evaluation['acceptance']['uniformity_ok'] = True
                evaluation['scores']['uniformity'] = min(uniformity, 1.0)
            else:
                evaluation['alerts'].append(
                    f"⚠️  Uniformity score {uniformity:.2f} below minimum {uniformity_min}"
                )
                evaluation['scores']['uniformity'] = uniformity
            
            # Overall acceptance
            evaluation['acceptance']['overall_ok'] = (
                evaluation['acceptance']['porosity_ok'] and
                evaluation['acceptance']['holes_ok']
            )
            
            # Assign quality grade
            evaluation['grade'] = self._assign_grade(metrics, profile)
            
            # Generate recommendations
            evaluation['recommendations'] = self._generate_recommendations(metrics, evaluation, profile)
            
            # Add to history
            self.history.append(evaluation)
            
            # Check for alerts
            if evaluation['alerts']:
                self.alerts.extend(evaluation['alerts'])
            
            logger.info(f"Quality evaluation: grade={evaluation['grade']}, "
                       f"overall={'PASS' if evaluation['acceptance']['overall_ok'] else 'FAIL'}")
            
            return evaluation
        
        except Exception as e:
            logger.error(f"Error evaluating analysis: {e}")
            evaluation['alerts'].append(f"Error during evaluation: {e}")
            return evaluation
    
    def _assign_grade(self, metrics: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> str:
        """Assign quality grade (Excellent/Good/Fair/Poor)."""
        if profile is None:
            profile = self.get_current_profile()
        
        grades = profile['quality_grades']
        porosity = metrics.get('porosity_percent', 0)
        uniformity = metrics.get('uniformity_score', 0.5)
        
        # Check grades in order of preference
        for grade_name in ['excellent', 'good', 'fair', 'poor']:
            grade_spec = grades[grade_name]
            p_min, p_max = grade_spec['porosity']
            u_min, u_max = grade_spec['uniformity']
            
            if (p_min <= porosity <= p_max) and (u_min <= uniformity <= u_max):
                return grade_name.capitalize()
        
        return "Poor"
    
    def _generate_recommendations(self, metrics: Dict[str, Any], 
                                 evaluation: Dict[str, Any],
                                 profile: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate actionable recommendations based on evaluation."""
        if profile is None:
            profile = self.get_current_profile()
        
        recommendations = []
        
        # Porosity recommendations
        if not evaluation['acceptance']['porosity_ok']:
            porosity = metrics.get('porosity_percent', 0)
            if porosity < profile['porosity_target_min']:
                recommendations.append(
                    "💡 Porosity too low: Try longer fermentation or higher hydration"
                )
            elif porosity > profile['porosity_target_max']:
                recommendations.append(
                    "💡 Porosity too high: Try shorter fermentation or lower hydration"
                )
        
        # Hole size recommendations
        if not evaluation['acceptance']['holes_ok']:
            mean_diam = metrics.get('mean_hole_diameter_mm', 0)
            if mean_diam < profile['hole_diameter_target_min']:
                recommendations.append(
                    "💡 Holes too small: Increase fermentation temperature or time"
                )
            elif mean_diam > profile['hole_diameter_target_max']:
                recommendations.append(
                    "💡 Holes too large: Reduce fermentation time or temperature"
                )
        
        # Uniformity recommendations
        if not evaluation['acceptance']['uniformity_ok']:
            recommendations.append(
                "💡 Low uniformity: Check even fermentation and oven temperature"
            )
        
        return recommendations
    
    def check_batch_consistency(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate consistency across batch of loaves/slices.
        
        Args:
            analyses: List of analysis results
            
        Returns:
            Batch consistency report
        """
        if not analyses:
            return {"status": "no_data", "message": "No analyses provided"}
        
        porosities = [a.get('metrics', {}).get('porosity_percent', 0) for a in analyses]
        hole_counts = [a.get('metrics', {}).get('num_holes', 0) for a in analyses]
        uniformities = [a.get('metrics', {}).get('uniformity_score', 0.5) for a in analyses]
        
        try:
            porosity_mean = statistics.mean(porosities)
            porosity_stdev = statistics.stdev(porosities) if len(porosities) > 1 else 0
            porosity_cv = (porosity_stdev / porosity_mean * 100) if porosity_mean > 0 else 0
            
            hole_mean = statistics.mean(hole_counts)
            hole_stdev = statistics.stdev(hole_counts) if len(hole_counts) > 1 else 0
            
            uniformity_mean = statistics.mean(uniformities)
            uniformity_min = min(uniformities)
            uniformity_max = max(uniformities)
            
            consistency_limit = self.config['consistency_cv_max'] * 100  # Convert to percent
            is_consistent = porosity_cv <= consistency_limit
            
            report = {
                "num_samples": len(analyses),
                "porosity": {
                    "mean": porosity_mean,
                    "stdev": porosity_stdev,
                    "cv_percent": porosity_cv,
                    "min": min(porosities),
                    "max": max(porosities),
                },
                "holes": {
                    "mean": hole_mean,
                    "stdev": hole_stdev,
                    "min": min(hole_counts),
                    "max": max(hole_counts),
                },
                "uniformity": {
                    "mean": uniformity_mean,
                    "min": uniformity_min,
                    "max": uniformity_max,
                },
                "is_consistent": is_consistent,
                "consistency_verdict": "PASS" if is_consistent else "FAIL",
                "consistency_limit_cv_percent": consistency_limit,
            }
            
            if is_consistent:
                report["message"] = f"✅ Batch is consistent (CV: {porosity_cv:.2f}% < {consistency_limit:.2f}%)"
            else:
                report["message"] = f"⚠️  Batch variation high (CV: {porosity_cv:.2f}% > {consistency_limit:.2f}%)"
            
            logger.info(f"Batch consistency check: {report['consistency_verdict']}")
            return report
        
        except Exception as e:
            logger.error(f"Error checking batch consistency: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_spc_statistics(self) -> Dict[str, Any]:
        """
        Get Statistical Process Control statistics from history.
        
        Returns:
            Dictionary with SPC metrics (mean, control limits, etc.)
        """
        if not self.history:
            return {"status": "no_data", "message": "No historical data"}
        
        porosities = [h.get('metrics', {}).get('porosity_percent', 0) for h in self.history]
        
        try:
            mean = statistics.mean(porosities)
            stdev = statistics.stdev(porosities) if len(porosities) > 1 else 0
            
            # Control limits (±3 sigma)
            ucl = mean + (3 * stdev)
            lcl = mean - (3 * stdev)
            
            # Warning limits (±2 sigma)
            uwl = mean + (2 * stdev)
            lwl = mean - (2 * stdev)
            
            spc = {
                "samples": len(porosities),
                "mean": mean,
                "stdev": stdev,
                "control_limits": {"ucl": ucl, "lcl": lcl},
                "warning_limits": {"uwl": uwl, "lwl": lwl},
                "recent_trend": self._analyze_trend(porosities[-10:]),
            }
            
            return spc
        
        except Exception as e:
            logger.error(f"Error calculating SPC statistics: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend in recent values."""
        if len(values) < 2:
            return "insufficient_data"
        
        recent = values[-5:]
        if len(recent) < 2:
            return "insufficient_data"
        
        # Simple trend analysis
        increases = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i-1])
        decreases = sum(1 for i in range(1, len(recent)) if recent[i] < recent[i-1])
        
        if increases > decreases:
            return "increasing"
        elif decreases > increases:
            return "decreasing"
        else:
            return "stable"
    
    def get_alerts(self, limit: int = 10) -> List[str]:
        """Get recent alerts."""
        return list(self.alerts)[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
        logger.info("Alerts cleared")
