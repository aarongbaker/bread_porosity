"""
Main analysis script for bread porosity measurement.
Simple pipeline: image → processing → metrics → visualization.
"""

from imaging_pipeline import ImagingPipeline
from metrics import PorometryMetrics, format_metrics_report
from visualization import VisualizationEngine
from calibration import ReferenceCalibration, CameraSetupHelper, SetupChecklist
import argparse
import logging
import json
from pathlib import Path

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configure logging for the application."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)


def analyze_bread_image(image_path: str, 
                       output_dir: str = "./output",
                       pixel_size_mm: float = 0.1,
                       threshold_method: str = "otsu",
                       normalize_method: str = "clahe",
                       verbose: bool = True) -> dict:
    """
    Complete bread porosity analysis pipeline.
    
    Args:
        image_path: Path to bread slice image
        output_dir: Output directory for results
        pixel_size_mm: Size of one pixel in millimeters
        threshold_method: "otsu" or "adaptive"
        normalize_method: "clahe", "morphology", or "gaussian"
        verbose: Print progress messages
    
    Returns:
        Dictionary with results and output paths
    
    Raises:
        FileNotFoundError: If image file does not exist
        ValueError: If processing fails
    """
    
    logger.info(f"Starting analysis on {image_path}")
    print("\n" + "="*70)
    print("BREAD POROSITY ANALYSIS")
    print("="*70)
    
    try:
        # Validate inputs
        if not Path(image_path).exists():
            logger.error(f"Image file not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if pixel_size_mm <= 0:
            logger.error(f"Invalid pixel size: {pixel_size_mm}")
            raise ValueError(f"Pixel size must be positive, got {pixel_size_mm}")
        
        # Initialize
        pipeline = ImagingPipeline(verbose=verbose)
        metrics_computer = PorometryMetrics(pixel_size_mm=pixel_size_mm, verbose=verbose)
        visualizer = VisualizationEngine(output_dir=output_dir)
        
        # 1. Read image
        print("\n[1/6] Loading image...")
        image = pipeline.read_image(image_path)
        
        # 2. Convert to grayscale
        print("[2/6] Converting to grayscale...")
        gray = pipeline.to_grayscale()
        
        # 3. Normalize illumination
        print(f"[3/6] Normalizing illumination ({normalize_method})...")
        normalized = pipeline.normalize_illumination(method=normalize_method)
        
        # 4. Find bread ROI
        print("[4/6] Finding bread region...")
        roi_mask, roi_stats = pipeline.find_bread_roi(threshold_value=30)
        
        # 5. Threshold holes
        print(f"[5/6] Thresholding holes ({threshold_method})...")
        binary_holes = pipeline.threshold_holes(method=threshold_method)
        
        # 6. Morphological cleanup
        print("[6/6] Cleaning up segmentation...")
        cleaned = pipeline.morphological_cleanup(remove_small_holes=50, fill_small_gaps=50)
        
        # Compute metrics
        print("\n[COMPUTING METRICS]")
        metrics = metrics_computer.compute_all_metrics(cleaned, roi_mask, normalized)
        
        # Generate visualizations
        print("\n[GENERATING OUTPUTS]")
        images_dict = pipeline.get_processing_images()
        
        comparison_path = visualizer.create_comparison_image(images_dict)
        distribution_path = visualizer.create_hole_distribution_plots(metrics)
        annotated_path = visualizer.create_annotated_image(image, cleaned, roi_mask, metrics)
        metrics_json_path = visualizer.save_metrics_json(metrics)
        
        # Print report
        print("\n" + format_metrics_report(metrics))
        
        # Summary
        results = {
            "metrics": metrics,
            "output_files": {
                "comparison": str(comparison_path),
                "distributions": str(distribution_path),
                "annotated": str(annotated_path),
                "metrics_json": str(metrics_json_path),
            },
            "image_path": str(image_path),
            "pixel_size_mm": pixel_size_mm,
        }
        
        print("\n[OUTPUT FILES]")
        print(f"  Comparison: {comparison_path.name}")
        print(f"  Distributions: {distribution_path.name}")
        print(f"  Annotated: {annotated_path.name}")
        print(f"  Metrics JSON: {metrics_json_path.name}")
        print(f"\n  → All output in: {visualizer.output_dir}/")
        
        logger.info(f"Analysis complete: {image_path} → porosity={metrics['porosity_percent']:.2f}%")
        
        return results
    
    except Exception as e:
        logger.error(f"Analysis failed for {image_path}: {e}")
        raise


def batch_analyze(image_directory: str, 
                 output_dir: str = "./batch_output",
                 pixel_size_mm: float = 0.1) -> list:
    """
    Analyze all images in a directory.
    
    Args:
        image_directory: Directory containing bread slice images
        output_dir: Output directory for results
        pixel_size_mm: Size of one pixel in mm
    
    Returns:
        List of results for each image
    """
    logger.info(f"Starting batch analysis on directory: {image_directory}")
    
    image_dir = Path(image_directory)
    if not image_dir.exists():
        logger.error(f"Image directory not found: {image_directory}")
        raise FileNotFoundError(f"Image directory not found: {image_directory}")
    
    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png")) + list(image_dir.glob("*.JPG"))
    
    if not image_files:
        logger.warning(f"No images found in {image_directory}")
        print(f"No images found in {image_directory}")
        return []
    
    results = []
    for idx, image_file in enumerate(image_files, 1):
        print(f"\n{'='*70}")
        print(f"Processing {idx}/{len(image_files)}: {image_file.name}")
        print(f"{'='*70}")
        
        try:
            result = analyze_bread_image(
                str(image_file),
                output_dir=str(Path(output_dir) / image_file.stem),
                pixel_size_mm=pixel_size_mm,
                verbose=False
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing {image_file.name}: {e}")
            print(f"✗ Error processing {image_file.name}: {e}")
    
    # Save batch summary
    try:
        summary_path = Path(output_dir) / "batch_summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        summary = {
            "num_images": len(image_files),
            "num_successful": len(results),
            "images": [r["image_path"] for r in results],
            "mean_porosity": sum(r["metrics"]["porosity_percent"] for r in results) / len(results) if results else 0,
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Batch complete: {len(results)}/{len(image_files)} images processed")
        print(f"\n\n{'='*70}")
        print(f"BATCH COMPLETE: {len(results)}/{len(image_files)} images processed")
        print(f"Mean porosity: {summary['mean_porosity']:.2f}%")
        print(f"Summary: {summary_path}")
    except Exception as e:
        logger.error(f"Error saving batch summary: {e}")
    
    return results


def print_setup_guide():
    """Print imaging setup guide."""
    SetupChecklist.print_setup_guide()


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description="Bread Porosity Analysis Tool")
    parser.add_argument("image", nargs="?", help="Path to bread slice image")
    parser.add_argument("--batch", help="Batch process directory of images")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--pixel-size", type=float, default=0.1, 
                       help="Pixel size in mm (default: 0.1)")
    parser.add_argument("--threshold", default="otsu", choices=["otsu", "adaptive"],
                       help="Thresholding method")
    parser.add_argument("--normalize", default="clahe", choices=["clahe", "morphology", "gaussian"],
                       help="Illumination normalization method")
    parser.add_argument("--setup", action="store_true", help="Print setup checklist and exit")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    parser.add_argument("--log-file", help="Log file path (optional)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)
    logger.info(f"Started bread porosity analyzer")
    
    try:
        if args.setup:
            print_setup_guide()
        elif args.batch:
            batch_analyze(args.batch, output_dir=args.output, pixel_size_mm=args.pixel_size)
        elif args.image:
            analyze_bread_image(args.image, output_dir=args.output, 
                               pixel_size_mm=args.pixel_size,
                               threshold_method=args.threshold,
                               normalize_method=args.normalize)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
