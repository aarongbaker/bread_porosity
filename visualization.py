"""
Visualization and output generation for bread porosity analysis.
Creates comparison images, histograms, and detailed reports.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional
from pathlib import Path


class VisualizationEngine:
    """Generate visualizations and reports from analysis results."""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_comparison_image(self, images_dict: Dict[str, np.ndarray], 
                               output_filename: str = "comparison.png") -> Path:
        """
        Create a grid comparison of processing steps.
        
        Args:
            images_dict: Dict with keys like 'original', 'grayscale', 'normalized', etc.
            output_filename: Output filename
        
        Returns:
            Path to saved image
        """
        # Select and order images to display
        display_order = ['original', 'grayscale', 'normalized', 'roi_mask', 'threshold', 'cleaned']
        images_to_show = {k: images_dict[k] for k in display_order if k in images_dict and images_dict[k] is not None}
        
        num_images = len(images_to_show)
        cols = min(3, num_images)
        rows = (num_images + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
        if num_images == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes.flatten() if num_images > 1 else [axes]
        else:
            axes = axes.flatten()
        
        for idx, (name, img) in enumerate(images_to_show.items()):
            ax = axes[idx]
            
            # Convert BGR to RGB for color images, keep grayscale as-is
            if len(img.shape) == 3:
                img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                ax.imshow(img_display)
            else:
                ax.imshow(img, cmap='gray')
            
            ax.set_title(name.replace('_', ' ').title(), fontsize=12, fontweight='bold')
            ax.axis('off')
        
        # Hide unused subplots
        for idx in range(num_images, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        output_path = self.output_dir / output_filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_hole_distribution_plots(self, metrics: Dict[str, Any], 
                                       output_filename: str = "hole_distribution.png") -> Path:
        """
        Create histograms of hole size and orientation distribution.
        
        Args:
            metrics: Metrics dictionary from PorometryMetrics
            output_filename: Output filename
        
        Returns:
            Path to saved image
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Hole area distribution
        hole_areas = metrics.get('hole_area_distribution', [])
        if hole_areas:
            ax = axes[0, 0]
            ax.hist(hole_areas, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
            ax.axvline(metrics.get('mean_hole_area_pixels', 0), color='red', 
                       linestyle='--', linewidth=2, label='Mean')
            ax.set_xlabel('Hole Area (pixels)')
            ax.set_ylabel('Frequency')
            ax.set_title('Hole Size Distribution')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Hole diameter distribution (in mm)
        ax = axes[0, 1]
        mean_diam = metrics.get('mean_hole_diameter_mm', 0)
        largest_diam = metrics.get('largest_hole_diameter_mm', 0)
        num_holes = metrics.get('num_holes', 0)
        if num_holes > 0 and hole_areas:
            # Approximate diameter distribution
            diameters_mm = 2 * np.sqrt(np.array(hole_areas) * 0.01 / np.pi)  # rough conversion
            ax.hist(diameters_mm, bins=20, color='coral', edgecolor='black', alpha=0.7)
            ax.axvline(mean_diam, color='red', linestyle='--', linewidth=2, label='Mean')
            ax.set_xlabel('Hole Diameter (mm)')
            ax.set_ylabel('Frequency')
            ax.set_title('Hole Diameter Distribution')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Summary statistics box
        ax = axes[1, 0]
        ax.axis('off')
        summary_text = f"""
        HOLE STATISTICS
        ─────────────────────
        Total holes: {metrics.get('num_holes', 0)}
        Mean diameter: {metrics.get('mean_hole_diameter_mm', 0):.2f} mm
        Largest: {metrics.get('largest_hole_diameter_mm', 0):.2f} mm
        Smallest: {metrics.get('smallest_hole_diameter_mm', 0):.2f} mm
        
        Size uniformity (CV): {metrics.get('hole_area_cv', 0):.3f}
        Holes per cm²: {metrics.get('holes_per_cm2', 0):.1f}
        
        Aspect ratio: {metrics.get('mean_aspect_ratio', 1):.2f}
        Orientation entropy: {metrics.get('orientation_entropy', 0):.2f}
        """
        ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=11,
               verticalalignment='top', family='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Porosity gauge
        ax = axes[1, 1]
        porosity = metrics.get('porosity_percent', 0)
        ax.barh(['Porosity'], [porosity], color='green', alpha=0.7, height=0.3)
        ax.barh(['Crumb'], [100 - porosity], left=[porosity], color='brown', alpha=0.7, height=0.3)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage (%)')
        ax.set_title('Porosity vs Crumb')
        ax.text(porosity/2, 0, f'{porosity:.1f}%', ha='center', va='center', fontweight='bold', color='white')
        ax.text(porosity + (100-porosity)/2, 0, f'{100-porosity:.1f}%', ha='center', va='center', fontweight='bold')
        
        plt.tight_layout()
        output_path = self.output_dir / output_filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_annotated_image(self, original: np.ndarray, cleaned_binary: np.ndarray,
                              roi_mask: np.ndarray, metrics: Dict[str, Any],
                              output_filename: str = "annotated.png") -> Path:
        """
        Create annotated image with holes highlighted and labels.
        
        Args:
            original: Original color image
            cleaned_binary: Cleaned binary holes mask
            roi_mask: ROI mask
            metrics: Metrics dictionary
            output_filename: Output filename
        
        Returns:
            Path to saved image
        """
        annotated = original.copy()
        
        # Highlight holes in red
        holes_colored = np.zeros_like(annotated)
        holes_colored[:, :, 2] = cleaned_binary  # Red channel for holes
        
        # Blend with original
        alpha = 0.6
        annotated = cv2.addWeighted(annotated, 1-alpha, holes_colored, alpha, 0)
        
        # Label holes with contours
        labeled, num_holes = cv2.connectedComponents(cleaned_binary)
        
        for i in range(1, min(num_holes + 1, 50)):  # Limit labels to avoid clutter
            contours, _ = cv2.findContours((labeled == i).astype(np.uint8) * 255,
                                          cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cv2.drawContours(annotated, contours, -1, (0, 255, 255), 1)
        
        # Add text annotations
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = 30
        line_height = 30
        
        text_lines = [
            f"Porosity: {metrics.get('porosity_percent', 0):.2f}%",
            f"Holes: {metrics.get('num_holes', 0)} ({metrics.get('holes_per_cm2', 0):.1f} per cm²)",
            f"Mean diameter: {metrics.get('mean_hole_diameter_mm', 0):.2f} mm",
            f"Aspect ratio: {metrics.get('mean_aspect_ratio', 1):.2f}",
        ]
        
        for line in text_lines:
            cv2.putText(annotated, line, (15, y_offset), font, 0.6, (255, 255, 255), 2)
            y_offset += line_height
        
        # Save
        output_path = self.output_dir / output_filename
        cv2.imwrite(str(output_path), annotated)
        
        return output_path
    
    def save_metrics_json(self, metrics: Dict[str, Any], 
                         output_filename: str = "metrics.json") -> Path:
        """Save metrics to JSON file."""
        import json
        
        # Convert numpy types to native Python types for JSON serialization
        metrics_json = {}
        for key, value in metrics.items():
            if isinstance(value, np.ndarray):
                metrics_json[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                metrics_json[key] = float(value)
            else:
                metrics_json[key] = value
        
        output_path = self.output_dir / output_filename
        with open(output_path, 'w') as f:
            json.dump(metrics_json, f, indent=2)
        
        return output_path
