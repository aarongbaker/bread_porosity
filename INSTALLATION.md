# Installation & Verification Checklist

## Before You Start

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Windows/Mac/Linux OS confirmed
- [ ] Sample bread images available (JPG or PNG)

## Step 1: Install Dependencies

```powershell
cd c:\Users\abaker\OneDrive - Factory Direct of Edison\Desktop\test\bread_porosity
pip install -r requirements.txt
```

Verify installation:
```powershell
python -c "import cv2, numpy, matplotlib, scipy; print('✓ All packages installed')"
```

Expected output: `✓ All packages installed`

## Step 2: Verify Tool Structure

Check that all files exist:

```powershell
$files = @(
    "__init__.py",
    "imaging_pipeline.py",
    "metrics.py",
    "visualization.py",
    "calibration.py",
    "analyze.py",
    "examples.py",
    "requirements.txt",
    "README.md",
    "QUICKSTART.md",
    "config_template.json"
)
foreach ($file in $files) {
    if (Test-Path $file) { Write-Host "✓ $file" } 
    else { Write-Host "✗ MISSING: $file" }
}
```

Expected: All files should show ✓

## Step 3: Test Import

```powershell
python -c "
from imaging_pipeline import ImagingPipeline
from metrics import PorometryMetrics
from visualization import VisualizationEngine
from calibration import ReferenceCalibration
print('✓ All modules import successfully')
"
```

Expected output: `✓ All modules import successfully`

## Step 4: View Setup Guide

```powershell
python analyze.py --setup
```

Expected: Displays comprehensive imaging setup checklist

## Step 5: Interactive Examples

```powershell
python examples.py
```

Menu will appear. Choose example 0 to see setup guide again.

## Step 6: Test with Sample Image

If you have a bread image:

```powershell
python analyze.py your_bread_image.jpg --pixel-size 0.1 --output test_results/
```

Check `test_results/` folder for:
- [ ] comparison.png (6-step pipeline visualization)
- [ ] hole_distribution.png (histograms and statistics)
- [ ] annotated.png (holes highlighted on original)
- [ ] metrics.json (raw metrics data)

## Step 7: Verify Outputs

```powershell
Get-ChildItem test_results/
```

Expected files:
- [ ] comparison.png
- [ ] hole_distribution.png
- [ ] annotated.png
- [ ] metrics.json

## Troubleshooting Installation

### Issue: "No module named cv2"
```powershell
pip install opencv-python
```

### Issue: "No module named numpy"
```powershell
pip install numpy
```

### Issue: "No module named matplotlib"
```powershell
pip install matplotlib
```

### Issue: All dependencies installed but still getting import errors
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Image file not found
- Check file path is correct
- Ensure file extension is .jpg, .png, or .JPG
- Use absolute path or copy image to bread_porosity/ folder

## Quick Functionality Test

Create a simple test script `test_tool.py`:

```python
from imaging_pipeline import ImagingPipeline
from metrics import PorometryMetrics
from visualization import VisualizationEngine
import numpy as np
import cv2

# Test 1: Create synthetic bread image
print("Test 1: Creating synthetic test image...")
img = np.ones((400, 400, 3), dtype=np.uint8) * 150  # Gray background
# Add some holes (bright spots)
cv2.circle(img, (100, 100), 20, (255, 255, 255), -1)
cv2.circle(img, (200, 150), 30, (255, 255, 255), -1)
cv2.circle(img, (300, 250), 25, (255, 255, 255), -1)
cv2.imwrite("test_synthetic.jpg", img)
print("✓ Test image created: test_synthetic.jpg")

# Test 2: Pipeline
print("\nTest 2: Running pipeline...")
pipeline = ImagingPipeline(verbose=True)
pipeline.read_image("test_synthetic.jpg")
pipeline.to_grayscale()
pipeline.normalize_illumination()
roi_mask, roi_stats = pipeline.find_bread_roi(threshold_value=100)
pipeline.threshold_holes()
pipeline.morphological_cleanup()
print("✓ Pipeline successful")

# Test 3: Metrics
print("\nTest 3: Computing metrics...")
metrics_comp = PorometryMetrics(pixel_size_mm=0.1)
metrics = metrics_comp.compute_all_metrics(
    pipeline.cleaned_binary,
    pipeline.roi_mask,
    pipeline.normalized
)
print(f"✓ Porosity: {metrics['porosity_percent']:.2f}%")
print(f"✓ Holes detected: {metrics['num_holes']}")

# Test 4: Visualization
print("\nTest 4: Generating visualization...")
visualizer = VisualizationEngine(output_dir="test_output")
images = pipeline.get_processing_images()
visualizer.create_comparison_image(images)
visualizer.create_hole_distribution_plots(metrics)
print("✓ Visualizations generated in test_output/")

print("\n" + "="*50)
print("ALL TESTS PASSED - Tool is ready to use!")
print("="*50)
```

Run it:
```powershell
python test_tool.py
```

Expected output: "ALL TESTS PASSED - Tool is ready to use!"

## Next Steps After Verification

1. **Read QUICKSTART.md** for 30-second usage guide
2. **Run examples.py** to try different workflows
3. **Set up your imaging** following QUICKSTART or examples
4. **Calibrate pixel_size_mm** for your camera
5. **Analyze your first bread** sample
6. **Review output files** to understand results

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.10+ |
| RAM | 2 GB | 4 GB+ |
| Disk space | 500 MB | 2 GB+ |
| Image size | 1 MP | 3-12 MP |
| Processing time | ~30s | ~5-10s |

## Performance Optimization

For faster processing:
- Use lower resolution images (downsize if >5000px)
- Use GPU-accelerated OpenCV if available
- Batch process multiple images

For better accuracy:
- Use high resolution images (3+ MP)
- Improve lighting setup
- Lock camera exposure/white balance

---

**Installation complete!** 
Next: Follow QUICKSTART.md for your first analysis.
