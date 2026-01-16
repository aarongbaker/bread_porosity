"""
Example: Setting up and using the bread porosity tool.
This script demonstrates the typical workflow.
"""

import cv2
import numpy as np
from pathlib import Path

# Import tool modules
from imaging_pipeline import ImagingPipeline
from metrics import PorometryMetrics, format_metrics_report
from visualization import VisualizationEngine
from calibration import ReferenceCalibration, CameraSetupHelper, SetupChecklist


def example_1_basic_analysis():
    """
    Example 1: Basic single-image analysis workflow.
    Shows the standard pipeline step-by-step.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Bread Porosity Analysis")
    print("="*70)
    
    # --- SETUP ---
    image_path = "bread_sample.jpg"  # Replace with your image
    pixel_size_mm = 0.1  # Adjust based on your camera setup
    output_dir = "./output"
    
    # --- VERIFY SETUP ---
    print("\n1. Checking image quality...")
    image = cv2.imread(image_path)
    if image is None:
        print("✗ Could not load image. Check file path.")
        return
    
    # Check sharpness
    sharpness = CameraSetupHelper.check_image_sharpness(image)
    print(f"   Sharpness: {sharpness['sharpness_level']}")
    print(f"   Laplacian variance: {sharpness['laplacian_variance']:.1f}")
    if sharpness['laplacian_variance'] < 500:
        print("   ⚠ Warning: Image may be out of focus. Improve setup and retry.")
    
    # Check lighting uniformity
    uniformity = CameraSetupHelper.estimate_lighting_uniformity(image)
    print(f"   Lighting uniformity: {uniformity['uniformity_score']:.1f}/100")
    if uniformity['uniformity_score'] < 70:
        print("   ⚠ Warning: Uneven lighting detected. Adjust setup for better results.")
    
    # --- PROCESSING PIPELINE ---
    print("\n2. Running image processing pipeline...")
    pipeline = ImagingPipeline(verbose=True)
    
    pipeline.read_image(image_path)
    pipeline.to_grayscale()
    pipeline.normalize_illumination(method="clahe")
    roi_mask, roi_stats = pipeline.find_bread_roi(threshold_value=30)
    pipeline.threshold_holes(method="otsu")
    pipeline.morphological_cleanup()
    
    # --- COMPUTE METRICS ---
    print("\n3. Computing metrics...")
    metrics_computer = PorometryMetrics(pixel_size_mm=pixel_size_mm, verbose=True)
    metrics = metrics_computer.compute_all_metrics(
        pipeline.cleaned_binary,
        pipeline.roi_mask,
        pipeline.normalized
    )
    
    # --- VISUALIZATION ---
    print("\n4. Generating visualizations...")
    visualizer = VisualizationEngine(output_dir=output_dir)
    
    images = pipeline.get_processing_images()
    visualizer.create_comparison_image(images)
    visualizer.create_hole_distribution_plots(metrics)
    visualizer.create_annotated_image(image, pipeline.cleaned_binary, roi_mask, metrics)
    visualizer.save_metrics_json(metrics)
    
    # --- RESULTS ---
    print("\n" + format_metrics_report(metrics))
    print(f"\nResults saved to: {output_dir}/")


def example_2_with_reference_calibration():
    """
    Example 2: Analysis with reference patch calibration.
    Use this when including a gray card in images.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Analysis with Reference Calibration")
    print("="*70)
    
    image_path = "bread_with_gray_card.jpg"  # Image with gray reference patch
    
    print("\n1. Detecting reference patch in image...")
    image = cv2.imread(image_path)
    if image is None:
        print("✗ Image not found")
        return
    
    # Detect reference patch
    calib = ReferenceCalibration(verbose=True)
    ref_info = calib.detect_reference_patch(image, patch_type="gray", 
                                             search_region=(10, 10, 200, 200))  # Search in corner
    
    if not ref_info.get("detected"):
        print("✗ Could not detect reference patch. Check image and patch placement.")
        return
    
    print(f"✓ Found reference patch:")
    print(f"  Value: {ref_info['mean_value']:.1f} ± {ref_info['std_value']:.1f}")
    print(f"  Area: {ref_info['area_pixels']} pixels")
    
    # Now use reference for normalization
    print("\n2. Using reference for brightness normalization...")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    normalized = calib.normalize_by_reference(gray, reference_value=128)
    
    print("✓ Image normalized to reference")
    
    # Continue with standard pipeline
    print("\n3. Running analysis...")
    from analyze import analyze_bread_image
    result = analyze_bread_image(image_path, pixel_size_mm=0.1)
    
    print(f"\nReference-normalized result: {result['metrics']['porosity_percent']:.2f}%")


def example_3_batch_processing():
    """
    Example 3: Batch processing multiple bread samples.
    Useful for quality control or comparing multiple recipes.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Processing Multiple Samples")
    print("="*70)
    
    from analyze import batch_analyze
    
    # Assuming you have multiple bread images in a folder
    image_dir = "bread_samples/"
    
    print(f"\nProcessing all images in: {image_dir}")
    results = batch_analyze(image_dir, output_dir="batch_results/", pixel_size_mm=0.1)
    
    if not results:
        print("✗ No images found or all processing failed")
        return
    
    # Print summary
    print("\n[BATCH SUMMARY]")
    porosity_values = [r["metrics"]["porosity_percent"] for r in results]
    hole_counts = [r["metrics"]["num_holes"] for r in results]
    
    print(f"Samples processed: {len(results)}")
    print(f"Mean porosity: {np.mean(porosity_values):.2f}% (±{np.std(porosity_values):.2f}%)")
    print(f"Mean hole count: {np.mean(hole_counts):.0f} (±{np.std(hole_counts):.0f})")
    print(f"Porosity range: {min(porosity_values):.2f}% - {max(porosity_values):.2f}%")


def example_4_custom_parameters():
    """
    Example 4: Fine-tuning parameters for specific bread types.
    Shows how to adjust algorithm parameters.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Parameters for Different Bread Types")
    print("="*70)
    
    # Example: Sourdough (large, irregular holes)
    print("\nSourdough Bread (large, irregular holes):")
    config_sourdough = {
        "threshold_method": "adaptive",  # Better for varied hole sizes
        "normalize_method": "gaussian",  # Handle strong lighting gradients
        "remove_small_holes": 100,  # Ignore noise
        "fill_small_gaps": 30,
        "pixel_size_mm": 0.12,
    }
    
    # Example: Sandwich bread (fine, uniform holes)
    print("\nSandwich Bread (fine, uniform holes):")
    config_sandwich = {
        "threshold_method": "otsu",  # Works well with uniform holes
        "normalize_method": "clahe",  # Standard normalization
        "remove_small_holes": 20,  # Keep even small holes
        "fill_small_gaps": 10,
        "pixel_size_mm": 0.08,
    }
    
    print("\nTo use custom config:")
    print("  result = analyze_bread_image(image_path, **config_sourdough)")
    print("\nAdjust parameters based on your bread type and imaging setup.")


def example_5_troubleshooting():
    """
    Example 5: Troubleshooting common issues.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Troubleshooting Guide")
    print("="*70)
    
    print("""
ISSUE: Porosity numbers don't match expectations
→ First: Check your pixel_size_mm calibration
→ Verify lighting setup (uniformity score > 70)
→ Try different normalization method (adaptive or gaussian)
→ Check image sharpness (Laplacian variance > 500)

ISSUE: Too many small noise holes detected
→ Increase remove_small_holes parameter
→ Improve image quality and lighting
→ Try adaptive threshold instead of Otsu

ISSUE: Large holes not being detected
→ Decrease remove_small_holes parameter
→ Try threshold method "adaptive" instead of "otsu"
→ Check that holes are actually brighter than crumb

ISSUE: Results vary too much between photos
→ Lock camera exposure and white balance
→ Use reference patch for normalization
→ Fix camera position on tripod
→ Use consistent lighting setup
→ Record pixel_size_mm and use same value for all images

ISSUE: Image looks blurry in output
→ Use higher resolution source image
→ Improve focus (check with sharpness metric)
→ Increase lighting

Remember: Setup matters more than algorithm tweaks!
Control lighting, focus, and exposure first.
""")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("BREAD POROSITY ANALYSIS - EXAMPLE SCRIPTS")
    print("="*70)
    print("\nChoose an example to run:")
    print("  1. Basic analysis (requires bread_sample.jpg)")
    print("  2. With reference calibration (requires bread_with_gray_card.jpg)")
    print("  3. Batch processing (requires bread_samples/ folder)")
    print("  4. Custom parameters")
    print("  5. Troubleshooting guide")
    print("  0. Print full setup checklist")
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    if choice == "1":
        example_1_basic_analysis()
    elif choice == "2":
        example_2_with_reference_calibration()
    elif choice == "3":
        example_3_batch_processing()
    elif choice == "4":
        example_4_custom_parameters()
    elif choice == "5":
        example_5_troubleshooting()
    elif choice == "0":
        SetupChecklist.print_setup_guide()
    else:
        print("Invalid choice")
