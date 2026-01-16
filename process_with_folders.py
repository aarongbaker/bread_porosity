"""
Bread porosity analyzer with automatic folder management.
Processes images from 'unprocessed/' folder and moves them to 'processed/' after analysis.
"""

import shutil
import os
from pathlib import Path
from analyze import analyze_bread_image


def setup_folders():
    """Create unprocessed and processed folders if they don't exist."""
    unprocessed_dir = Path("unprocessed")
    processed_dir = Path("processed")
    results_dir = Path("results")
    
    unprocessed_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)
    results_dir.mkdir(exist_ok=True)
    
    return unprocessed_dir, processed_dir, results_dir


def process_all_images(pixel_size_mm=0.1, verbose=True):
    """
    Process all images in unprocessed/ folder, then move to processed/ folder.
    
    Args:
        pixel_size_mm: Pixel size in mm (adjust for your camera)
        verbose: Print progress messages
    
    Returns:
        Count of processed images
    """
    unprocessed_dir, processed_dir, results_dir = setup_folders()
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.PNG']
    image_files = []
    for ext in image_extensions:
        image_files.extend(unprocessed_dir.glob(f'*{ext}'))
    
    if not image_files:
        print(f"✗ No images found in {unprocessed_dir}/ folder")
        return 0
    
    print(f"\n{'='*70}")
    print(f"Found {len(image_files)} image(s) to process")
    print(f"{'='*70}\n")
    
    processed_count = 0
    failed_count = 0
    
    for idx, image_file in enumerate(image_files, 1):
        print(f"\n[{idx}/{len(image_files)}] Processing: {image_file.name}")
        print("-" * 70)
        
        try:
            # Analyze image
            output_subdir = results_dir / image_file.stem
            result = analyze_bread_image(
                str(image_file),
                output_dir=str(output_subdir),
                pixel_size_mm=pixel_size_mm,
                verbose=verbose
            )
            
            # Move to processed folder
            destination = processed_dir / image_file.name
            shutil.move(str(image_file), str(destination))
            
            print(f"✓ Moved to: processed/{image_file.name}")
            print(f"✓ Results: results/{image_file.stem}/")
            
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Error processing {image_file.name}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"✓ Successfully processed: {processed_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"\nFolders:")
    print(f"  Unprocessed: unprocessed/")
    print(f"  Processed:   processed/")
    print(f"  Results:     results/")
    print(f"{'='*70}\n")
    
    return processed_count


def process_single_image(image_path, pixel_size_mm=0.1):
    """
    Process a single image from unprocessed/ and move to processed/.
    
    Args:
        image_path: Filename or path to image
        pixel_size_mm: Pixel size in mm
    """
    unprocessed_dir, processed_dir, results_dir = setup_folders()
    
    # Handle path
    if isinstance(image_path, str):
        image_file = Path(image_path)
        if not image_file.is_absolute():
            image_file = unprocessed_dir / image_path
    else:
        image_file = image_path
    
    if not image_file.exists():
        print(f"✗ Image not found: {image_file}")
        return False
    
    print(f"\nProcessing: {image_file.name}")
    
    try:
        # Analyze
        output_subdir = results_dir / image_file.stem
        result = analyze_bread_image(
            str(image_file),
            output_dir=str(output_subdir),
            pixel_size_mm=pixel_size_mm,
            verbose=True
        )
        
        # Move to processed
        destination = processed_dir / image_file.name
        shutil.move(str(image_file), str(destination))
        
        print(f"\n✓ Successfully processed and moved to: processed/{image_file.name}")
        print(f"✓ Results saved to: results/{image_file.stem}/")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process bread images with automatic folder management"
    )
    parser.add_argument("--pixel-size", type=float, default=0.1,
                       help="Pixel size in mm (default: 0.1)")
    parser.add_argument("--image", help="Process single image from unprocessed/ folder")
    parser.add_argument("--verbose", action="store_true", help="Print detailed progress")
    
    args = parser.parse_args()
    
    # Setup folders
    unprocessed_dir, processed_dir, results_dir = setup_folders()
    print(f"\n✓ Folders ready:")
    print(f"  • unprocessed/ - Put bread images here")
    print(f"  • processed/   - Images moved here after analysis")
    print(f"  • results/     - Analysis output (plots, JSON)")
    
    if args.image:
        # Process single image
        process_single_image(args.image, pixel_size_mm=args.pixel_size)
    else:
        # Process all images in unprocessed folder
        process_all_images(pixel_size_mm=args.pixel_size, verbose=args.verbose)
