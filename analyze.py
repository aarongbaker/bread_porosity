"""
CLI entry point for bread porosity analysis.
Runs analysis on a single image or a batch directory.
"""

import argparse
from pathlib import Path
from typing import List

from services.analysis_service import AnalysisService
from utils.logger import setup_logging


def _collect_images(image_dir: Path) -> List[str]:
    patterns = ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff")
    images = []
    for pattern in patterns:
        images.extend(sorted(image_dir.glob(pattern)))
    return [str(p) for p in images]


def main() -> None:
    parser = argparse.ArgumentParser(description="Bread porosity analysis")
    parser.add_argument("image", nargs="?", help="Path to a bread image")
    parser.add_argument("--batch", help="Directory of images to analyze")
    parser.add_argument("--pixel-size", type=float, default=0.1, help="Pixel size in mm")
    parser.add_argument("--threshold", default="otsu", choices=["otsu", "adaptive"])
    parser.add_argument("--normalize", default="clahe", choices=["clahe", "morphology", "gaussian"])
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--no-visuals", action="store_true", help="Skip visualization outputs")
    parser.add_argument("--no-save", action="store_true", help="Skip saving results to repository")

    args = parser.parse_args()

    if not args.image and not args.batch:
        parser.error("Provide an image path or --batch directory")

    setup_logging()
    service = AnalysisService(output_dir=args.output)

    if args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.exists():
            raise SystemExit(f"Batch directory not found: {batch_dir}")
        image_paths = _collect_images(batch_dir)
        if not image_paths:
            raise SystemExit(f"No images found in: {batch_dir}")
        results = service.analyze_multiple_images(
            image_paths=image_paths,
            pixel_size_mm=args.pixel_size,
            threshold_method=args.threshold,
            normalize_method=args.normalize,
            output_dir=args.output,
            save_results=not args.no_save,
            generate_visualizations=not args.no_visuals,
        )
        print(f"Processed {len(results)} images")
    else:
        result = service.analyze_image(
            image_path=args.image,
            pixel_size_mm=args.pixel_size,
            threshold_method=args.threshold,
            normalize_method=args.normalize,
            output_dir=args.output,
            save_results=not args.no_save,
            generate_visualizations=not args.no_visuals,
        )
        print(f"Porosity: {result.porosity_percent:.2f}%")
        print(f"Holes: {result.hole_count_total}")
        print(f"Mean diameter: {result.hole_diameter_mean_mm:.2f} mm")


if __name__ == "__main__":
    main()
