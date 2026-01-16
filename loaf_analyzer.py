"""
Loaf Analysis Tool
Analyzes multiple slices from the same loaf and compares porosity throughout.
Automatically organizes slices and generates a loaf quality report.
"""

import json
import numpy as np
from pathlib import Path
from analyze import analyze_bread_image
import shutil


def analyze_loaf(loaf_name="loaf", pixel_size_mm=0.1, verbose=True, expected_slices=None):
    """
    Analyze all slices of a loaf (supports ANY number of slices).
    
    Folder structure:
    unprocessed/
    └── loaf_name/
        ├── slice_1.jpg
        ├── slice_2.jpg
        ├── slice_3.jpg
        ...
        └── slice_N.jpg  (N = any number)
    
    Args:
        loaf_name: Name of loaf folder in unprocessed/
        pixel_size_mm: Pixel size in mm
        verbose: Print progress
        expected_slices: Optional - expected number of slices (for validation)
    
    Returns:
        Dictionary with loaf analysis results
    """
    
    # Setup directories
    unprocessed_dir = Path("unprocessed")
    processed_dir = Path("processed")
    results_dir = Path("results")
    
    unprocessed_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    
    loaf_path = unprocessed_dir / loaf_name
    
    if not loaf_path.exists():
        print(f"✗ Loaf folder not found: {loaf_path}/")
        print(f"\nCreate folder structure:")
        print(f"  unprocessed/{loaf_name}/")
        print(f"  ├── slice_1.jpg")
        print(f"  ├── slice_2.jpg")
        print(f"  └── ... (up to 10 slices)")
        return None
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.PNG']
    image_files = sorted([
        f for f in loaf_path.glob('*')
        if f.suffix in image_extensions
    ])
    
    if not image_files:
        print(f"✗ No images found in {loaf_path}/")
        return None
    
    # Validate slice count if specified
    if expected_slices and len(image_files) != expected_slices:
        print(f"⚠️  Warning: Expected {expected_slices} slices but found {len(image_files)}")
    
    print(f"\n{'='*70}")
    print(f"LOAF ANALYSIS: {loaf_name}")
    print(f"Found {len(image_files)} slices to analyze")
    print(f"{'='*70}\n")
    
    # Create loaf results directory
    loaf_results_dir = results_dir / loaf_name
    loaf_results_dir.mkdir(exist_ok=True)
    
    all_metrics = []
    processed_files = []
    
    # Analyze each slice
    for idx, image_file in enumerate(image_files, 1):
        slice_name = image_file.stem
        print(f"[{idx}/{len(image_files)}] Analyzing {slice_name}...")
        
        try:
            # Analyze
            slice_results_dir = loaf_results_dir / slice_name
            result = analyze_bread_image(
                str(image_file),
                output_dir=str(slice_results_dir),
                pixel_size_mm=pixel_size_mm,
                verbose=False  # Keep output clean
            )
            
            metrics = result['metrics']
            all_metrics.append({
                'slice': idx,
                'filename': image_file.name,
                'porosity': metrics['porosity_percent'],
                'num_holes': metrics['num_holes'],
                'mean_diameter_mm': metrics['mean_hole_diameter_mm'],
                'holes_per_cm2': metrics['holes_per_cm2'],
                'aspect_ratio': metrics['mean_aspect_ratio'],
                'uniformity_cv': metrics['hole_area_cv'],
            })
            
            processed_files.append(image_file)
            print(f"  ✓ Porosity: {metrics['porosity_percent']:.1f}%")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Generate loaf report
    print(f"\n{'='*70}")
    print(f"LOAF REPORT: {loaf_name}")
    print(f"{'='*70}\n")
    
    if not all_metrics:
        print("✗ No slices processed successfully")
        return None
    
    # Extract data
    porosity_values = [m['porosity'] for m in all_metrics]
    hole_counts = [m['num_holes'] for m in all_metrics]
    diameters = [m['mean_diameter_mm'] for m in all_metrics]
    aspect_ratios = [m['aspect_ratio'] for m in all_metrics]
    
    # Calculate statistics
    report = {
        'loaf_name': loaf_name,
        'num_slices': len(all_metrics),
        'slices': all_metrics,
        'porosity': {
            'mean': float(np.mean(porosity_values)),
            'std': float(np.std(porosity_values)),
            'min': float(np.min(porosity_values)),
            'max': float(np.max(porosity_values)),
            'range': float(np.max(porosity_values) - np.min(porosity_values)),
        },
        'holes': {
            'mean_count': float(np.mean(hole_counts)),
            'std_count': float(np.std(hole_counts)),
            'mean_diameter_mm': float(np.mean(diameters)),
            'std_diameter_mm': float(np.std(diameters)),
        },
        'shape': {
            'mean_aspect_ratio': float(np.mean(aspect_ratios)),
            'std_aspect_ratio': float(np.std(aspect_ratios)),
        }
    }
    
    # Print report
    print(f"POROSITY ANALYSIS")
    print(f"  Mean porosity:     {report['porosity']['mean']:.1f}%")
    print(f"  Std deviation:     {report['porosity']['std']:.1f}%")
    print(f"  Range:             {report['porosity']['min']:.1f}% - {report['porosity']['max']:.1f}%")
    print(f"  Variation:         {report['porosity']['range']:.1f}%")
    
    print(f"\nHOLE ANALYSIS")
    print(f"  Mean hole count:   {report['holes']['mean_count']:.0f} holes")
    print(f"  Mean diameter:     {report['holes']['mean_diameter_mm']:.2f} mm")
    print(f"  Diameter range:    {np.min(diameters):.2f} - {np.max(diameters):.2f} mm")
    
    print(f"\nSHAPE ANALYSIS")
    print(f"  Mean aspect ratio: {report['shape']['mean_aspect_ratio']:.2f}")
    uniformity = "High (round)" if report['shape']['mean_aspect_ratio'] < 1.5 else \
                 "Moderate" if report['shape']['mean_aspect_ratio'] < 2.0 else "Low (elongated)"
    print(f"  Shape uniformity:  {uniformity}")
    
    # Slice-by-slice summary
    print(f"\nSLICE-BY-SLICE BREAKDOWN")
    print(f"{'Slice':<8} {'Porosity':<12} {'Holes':<10} {'Diameter':<12} {'Aspect':<10}")
    print(f"{'-'*60}")
    for m in all_metrics:
        print(f"{m['slice']:<8} {m['porosity']:<11.1f}% {m['num_holes']:<10.0f} "
              f"{m['mean_diameter_mm']:<11.2f}mm {m['aspect_ratio']:<10.2f}")
    
    # Quality assessment
    print(f"\n{'='*70}")
    print(f"LOAF QUALITY ASSESSMENT")
    print(f"{'='*70}")
    
    uniformity_score = 100 - (report['porosity']['range'] * 2)  # Penalty for variation
    if uniformity_score < 50:
        quality = "⚠️  POOR - High porosity variation across slices"
    elif uniformity_score < 75:
        quality = "⚠️  FAIR - Some porosity variation"
    elif uniformity_score < 90:
        quality = "✓ GOOD - Reasonably uniform porosity"
    else:
        quality = "✓ EXCELLENT - Very uniform porosity"
    
    print(f"\nUniformity Score: {uniformity_score:.0f}/100")
    print(f"Quality: {quality}")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS")
    if report['porosity']['range'] > 15:
        print(f"  • High porosity variation ({report['porosity']['range']:.1f}%)")
        print(f"    → Check fermentation uniformity")
        print(f"    → Verify even shaping and proofing")
    
    if report['holes']['mean_diameter_mm'] > 5:
        print(f"  • Large holes ({report['holes']['mean_diameter_mm']:.1f}mm average)")
        print(f"    → May indicate over-fermentation or degassing issues")
    
    if report['shape']['mean_aspect_ratio'] > 2:
        print(f"  • Elongated holes (aspect ratio {report['shape']['mean_aspect_ratio']:.2f})")
        print(f"    → Indicates directional fermentation/shaping effects")
    
    print(f"\n{'='*70}\n")
    
    # Save report
    report_path = loaf_results_dir / "loaf_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Full report saved: results/{loaf_name}/loaf_report.json")
    
    # Move processed slices to processed/ folder
    processed_loaf_dir = processed_dir / loaf_name
    processed_loaf_dir.mkdir(exist_ok=True)
    
    for image_file in processed_files:
        destination = processed_loaf_dir / image_file.name
        shutil.move(str(image_file), str(destination))
    
    print(f"✓ Processed slices moved to: processed/{loaf_name}/")
    print(f"✓ Analysis results: results/{loaf_name}/")
    
    return report


def create_loaf_comparison_csv(loaf_names, output_file="loaf_comparison.csv"):
    """
    Create CSV comparing multiple loaves.
    
    Args:
        loaf_names: List of loaf names to compare
        output_file: Output CSV filename
    """
    results_dir = Path("results")
    
    rows = []
    for loaf_name in loaf_names:
        report_path = results_dir / loaf_name / "loaf_report.json"
        if report_path.exists():
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            rows.append({
                'Loaf': loaf_name,
                'Slices': report['num_slices'],
                'Mean Porosity %': f"{report['porosity']['mean']:.1f}",
                'Porosity Std': f"{report['porosity']['std']:.1f}",
                'Porosity Range': f"{report['porosity']['range']:.1f}",
                'Mean Holes': f"{report['holes']['mean_count']:.0f}",
                'Mean Diameter mm': f"{report['holes']['mean_diameter_mm']:.2f}",
            })
    
    if rows:
        import csv
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"✓ Comparison saved: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze bread loaves (any number of slices)")
    parser.add_argument("--loaf", default="loaf", help="Loaf name (folder name in unprocessed/)")
    parser.add_argument("--pixel-size", type=float, default=0.1, help="Pixel size in mm")
    parser.add_argument("--expected-slices", type=int, help="Expected number of slices (optional validation)")
    parser.add_argument("--compare", nargs='+', help="Compare multiple loaves")
    
    args = parser.parse_args()
    
    if args.compare:
        # Compare multiple loaves
        print("\nComparing loaves...")
        create_loaf_comparison_csv(args.compare)
    else:
        # Analyze single loaf
        analyze_loaf(loaf_name=args.loaf, pixel_size_mm=args.pixel_size, 
                     expected_slices=args.expected_slices)
