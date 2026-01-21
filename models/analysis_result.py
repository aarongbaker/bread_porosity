"""
Analysis Result Domain Model
Represents the results of bread porosity analysis
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class AnalysisResult:
    """Domain model for analysis results"""
    
    # Image info
    image_path: str
    image_filename: str
    
    # Metrics
    porosity_percent: float
    hole_count_total: int
    hole_diameter_mean_mm: float
    hole_diameter_std_mm: float
    hole_diameter_min_mm: float
    hole_diameter_max_mm: float
    holes_per_cm2: float
    
    # Shape analysis
    anisotropy_ratio: float  # 1 = circle, >1 = elongated
    orientation_mean_deg: float  # Mean orientation in degrees
    
    # Uniformity
    uniformity_score: float  # 0-1, higher = more uniform
    hole_size_distribution_data: Dict[str, Any] = field(default_factory=dict)
    
    # Quality assessment (optional)
    qc_passed: Optional[bool] = None
    quality_grade: Optional[str] = None  # excellent, good, fair, poor
    defects_detected: Optional[Dict[str, Any]] = None
    
    # Processing info
    pixel_size_mm: float = 0.1
    threshold_method: str = "otsu"
    normalization_method: str = "clahe"
    processing_time_sec: float = 0.0
    
    # Output paths
    output_comparison_path: Optional[str] = None
    output_annotated_path: Optional[str] = None
    
    # Timestamp (default last)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    output_distribution_path: Optional[str] = None
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate analysis result data
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.image_path:
            errors.append("Image path cannot be empty")
        
        if not (0 <= self.porosity_percent <= 100):
            errors.append("Porosity must be between 0 and 100")
        
        if self.hole_count_total < 0:
            errors.append("Hole count cannot be negative")
        
        if self.hole_diameter_mean_mm < 0:
            errors.append("Mean hole diameter cannot be negative")
        
        if self.holes_per_cm2 < 0:
            errors.append("Holes per cm2 cannot be negative")
        
        if not (0 <= self.uniformity_score <= 1):
            errors.append("Uniformity score must be between 0 and 1")
        
        if self.anisotropy_ratio < 1:
            errors.append("Anisotropy ratio must be >= 1")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisResult':
        """Create result from dictionary"""
        return cls(**data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of key metrics"""
        return {
            'image': self.image_filename,
            'porosity': f"{self.porosity_percent:.1f}%",
            'holes': self.hole_count_total,
            'mean_diameter': f"{self.hole_diameter_mean_mm:.2f}mm",
            'uniformity': f"{self.uniformity_score:.2f}",
            'quality_grade': self.quality_grade or 'Not assessed',
            'qc_passed': self.qc_passed
        }
