"""
QC Profile Domain Model
Represents quality control profile for a bread type
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class QCProfile:
    """Domain model for quality control profile"""
    
    # Identity
    bread_type: str  # e.g., 'sourdough', 'ciabatta'
    display_name: str
    
    # Porosity targets
    porosity_target_min: float
    porosity_target_max: float
    porosity_warning_min: float
    porosity_warning_max: float
    
    # Hole count targets
    hole_count_target_min: int
    hole_count_target_max: int
    
    # Hole diameter targets (mm)
    hole_diameter_target_min: float
    hole_diameter_target_max: float
    
    # Uniformity and consistency
    uniformity_acceptable_min: float
    consistency_cv_max: float  # Coefficient of variation
    
    # Quality grades
    quality_grades: Dict[str, Dict[str, List[float]]] = field(default_factory=dict)
    
    # Description/notes
    description: str = ""
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate QC profile data
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.bread_type:
            errors.append("Bread type cannot be empty")
        
        if not self.display_name:
            errors.append("Display name cannot be empty")
        
        if self.porosity_target_min >= self.porosity_target_max:
            errors.append("Porosity target min must be less than max")
        
        if self.porosity_warning_min >= self.porosity_warning_max:
            errors.append("Porosity warning min must be less than max")
        
        if self.hole_count_target_min >= self.hole_count_target_max:
            errors.append("Hole count target min must be less than max")
        
        if self.hole_diameter_target_min >= self.hole_diameter_target_max:
            errors.append("Hole diameter target min must be less than max")
        
        if not (0 <= self.uniformity_acceptable_min <= 1):
            errors.append("Uniformity acceptable must be between 0 and 1")
        
        if self.consistency_cv_max <= 0:
            errors.append("Consistency CV max must be positive")
        
        return len(errors) == 0, errors
    
    def evaluate_porosity(self, value: float) -> str:
        """
        Evaluate porosity value against profile
        
        Args:
            value: Porosity percentage (0-100)
        
        Returns:
            'pass', 'warning', or 'fail'
        """
        if self.porosity_target_min <= value <= self.porosity_target_max:
            return 'pass'
        elif self.porosity_warning_min <= value <= self.porosity_warning_max:
            return 'warning'
        else:
            return 'fail'
    
    def evaluate_hole_count(self, value: int) -> str:
        """
        Evaluate hole count against profile
        
        Returns:
            'pass' or 'fail'
        """
        if self.hole_count_target_min <= value <= self.hole_count_target_max:
            return 'pass'
        else:
            return 'fail'
    
    def evaluate_uniformity(self, value: float) -> str:
        """
        Evaluate uniformity score against profile
        
        Returns:
            'pass' or 'fail'
        """
        if value >= self.uniformity_acceptable_min:
            return 'pass'
        else:
            return 'fail'
    
    def get_quality_grade(self, porosity: float, uniformity: float) -> str:
        """
        Determine quality grade from metrics
        
        Args:
            porosity: Porosity percentage
            uniformity: Uniformity score (0-1)
        
        Returns:
            Quality grade string (excellent, good, fair, poor)
        """
        for grade in ['excellent', 'good', 'fair', 'poor']:
            grade_spec = self.quality_grades.get(grade, {})
            
            porosity_range = grade_spec.get('porosity', [0, 100])
            uniformity_range = grade_spec.get('uniformity', [0, 1])
            
            if (porosity_range[0] <= porosity <= porosity_range[1] and
                uniformity_range[0] <= uniformity <= uniformity_range[1]):
                return grade
        
        return 'poor'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QCProfile':
        """Create profile from dictionary"""
        return cls(**data)
