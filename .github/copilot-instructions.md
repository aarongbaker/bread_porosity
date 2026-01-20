# AI Agent Instructions for Bread Porosity Analysis Tool

## Project Summary
Professional image processing tool for measuring bread crumb structure using **classical computer vision** (not ML). Analyzes porosity %, hole size/distribution, uniformity, and shape metrics. Includes GUI, recipe database, ML-based defect detection, and quality control with multiple bread type profiles.

## Architecture Overview

### Core Components (Processing Pipeline)
- **`imaging_pipeline.py`** - Classical CV processing: read → grayscale → normalize illumination → ROI detection → thresholding → morphological cleanup
- **`metrics.py`** - Computes porosity, hole count/size/distribution, anisotropy, uniformity from binary segmentation
- **`visualization.py`** - Generates annotated images, plots, JSON output
- **`analyze.py`** - Main orchestration script; entry point for batch processing

**Key principle**: Image quality and standardized setup matter MORE than algorithm tweaks. Lighting consistency, focus, exposure are foundational.

### User Interface
- **`gui.py`** (2300+ lines) - Dark theme Material Design GUI with 9 tabs:
  - **Analysis**: Single image or multi-slice loaf mode
  - **Results**: Metrics display and visualization
  - **Consistency**: Batch uniformity metrics (loaf-level)
  - **Quality Control**: Profile-based acceptance criteria with alerts
  - **Recipe Management**: Database CRUD, variant generation
  - **Prediction**: ML porosity prediction from recipe parameters
  - **Defect Detection**: Automated uneven rise/dense spot detection
  - **ML Classifier**: Train custom good/bad bread classifier
  - **Export**: CSV, Excel, PDF reporting

### Domain-Specific Modules
- **`quality_control.py`** - QC profiles for 5 bread types (sourdough, whole wheat, ciabatta, sandwich, baguette) with thresholds, SPC statistics, alert system
- **`recipe_database.py`** - Recipe CRUD, porosity tracking, variant scaling
- **`recipe_predictor.py`** - ML predictions of porosity from recipe parameters
- **`defect_detection.py`** - Detects structural defects (uneven rise, dense spots)
- **`ml_simple.py`** - Custom classifier training on user's bread images
- **`export_reporting.py`** - Multi-format exports with charts

## Data Flow

```
Image Input → ImagingPipeline (normalize) → Thresholding → Metrics → Results
    ↓                                                          ↓
Stored in `unprocessed/`                           Output to `output/` or `processed/`
                                                   + Stored in results DB + QC checks
```

**Config files**: `config.json` (general settings), `qc_config.json` (QC thresholds), `recipes.json` (recipe database)

## Critical Patterns & Conventions

### Metric Naming
- `porosity_percent` - percentage of holes vs crumb (0-100)
- `hole_count_total` - connected component count
- `hole_diameter_mean_mm` - average size in millimeters
- `anisotropy_ratio` - elongation (1 = circle, >1 = stretched)
- `uniformity_score` - 0-1, measures consistency across image regions
- **Always convert pixels to mm using `pixel_size_mm` parameter** (typically 0.05-0.2 mm/pixel for bread)

### Normalization Methods
Three approaches in `imaging_pipeline.normalize_illumination()`:
- `"clahe"` - Contrast Limited Adaptive Histogram Equalization (default, robust)
- `"morphology"` - Morphological opening (removes lighting gradients)
- `"gaussian"` - Gaussian blur background subtraction (simpler)
Use **CLAHE** for uneven backlit setups; experiment if results are poor.

### Thresholding
- `"otsu"` - Global threshold (default, works with good normalized images)
- `"adaptive"` - Local thresholding (better for shadows/gradients)
Threshold method selection in `analyze_bread_image()` and GUI.

### Output Structure
Standard outputs to `output/` directory:
- `comparison.png` - Side-by-side processing steps (original → grayscale → normalized → threshold → cleaned)
- `hole_distribution.png` - Histogram and size/uniformity plots
- `annotated.png` - Segmented holes highlighted with bounding ellipses
- `metrics.json` - Raw metric data (all fields accessible programmatically)

## Development Workflows

### Analyzing a Single Image
```bash
python analyze.py bread.jpg --pixel-size 0.1 --output-dir results/
```
Defaults: Otsu thresholding, CLAHE normalization, outputs to `./output/`

### Batch Processing
```bash
python analyze.py --batch image_folder/ --pixel-size 0.1 --output-dir batch_results/
```
Processes all `.jpg`/`.png` in folder, generates per-image results + batch summary.

### Running GUI
```bash
python gui.py
```
Creates SQLite-backed recipe database automatically; config files generated on first run.

### Testing & Validation
- **Setup verification**: `analyze.py --setup` runs checklist (focus, lighting uniformity, exposure stability)
- **Calibration**: `calibration.py` - Gray reference card validation for normalization tuning
- **Example workflows**: `python examples.py` - Interactive demos with sample images

## Important Integration Points

### Multi-Slice Loaf Analysis
- **Convention**: Name slices `loaf_001.jpg`, `loaf_002.jpg`, etc. (numeric suffix required)
- **Module**: `loaf_analyzer.py` analyzes consistency across slices, computes uniformity metrics
- **Results**: Per-slice metrics + batch statistics (mean, std dev, CV)

### Recipe-to-Porosity Prediction
- **Flow**: Recipe ingredients/parameters → `recipe_predictor.py` → ML model → predicted_porosity
- **Training data**: Built from actual measurements stored in recipe database
- **Use case**: Predict porosity before baking to inform adjustments

### QC Profile Selection
- **In GUI**: Dropdown selects bread type profile from `qc_config.json`
- **Alert thresholds**: Each profile has warning (yellow) and fail (red) ranges
- **SPC stats**: Tracks batch mean/StdDev; alerts on trends or out-of-spec measurements
- **Custom profiles**: Add new bread type with `QualityControlManager.add_bread_type()`

### Defect Detection
- **Uneven rise**: Spatial gradient analysis to detect asymmetric crumb development
- **Dense spots**: Low-threshold region detection for under-fermented zones
- **Output**: Severity score (0-100) + annotated image with marked defect regions

## Common Gotchas & Solutions

| Issue | Solution |
|-------|----------|
| Metrics seem wrong (porosity too high/low) | Check `pixel_size_mm` - must match camera calibration. Test with `--setup` command. |
| Blurry hole edges / poor segmentation | Increase `--pixel-size` tolerance or switch to `adaptive` thresholding in GUI. Verify focus (Laplacian variance >500). |
| Lighting artifacts in results | Try `morphology` or `gaussian` normalization instead of CLAHE. Ensure backlit setup is uniform. |
| GUI won't start | Verify tkinter installed: `pip install tk` (often missing on Linux). Check Python version >=3.9. |
| Recipe predictions inaccurate | Need >20 training samples in database. Check that `measured_porosity` is populated when adding recipes. |

## Adding New Bread Type Profiles

### Understanding Profile Structure
Each bread type profile in `qc_config.json` defines acceptance criteria and quality grades. The essential fields are:

```json
{
  "custom_bread": {
    "display_name": "Custom Bread",
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
      "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]}
    }
  }
}
```

### Method 1: Programmatic Addition (Python Code)
Use `QualityControlManager.add_bread_type()` to add profiles dynamically:

```python
from quality_control import QualityControlManager

qc = QualityControlManager()

my_profile = {
    "display_name": "Rye Bread",
    "porosity_target_min": 18.0,
    "porosity_target_max": 30.0,
    "porosity_warning_min": 15.0,
    "porosity_warning_max": 33.0,
    "hole_count_target_min": 80,
    "hole_count_target_max": 300,
    "hole_diameter_target_min": 1.8,
    "hole_diameter_target_max": 7.0,
    "uniformity_acceptable_min": 0.68,
    "consistency_cv_max": 0.17,
    "quality_grades": {
        "excellent": {"porosity": [22, 28], "uniformity": [0.82, 1.0]},
        "good": {"porosity": [18, 30], "uniformity": [0.72, 0.92]},
        "fair": {"porosity": [15, 33], "uniformity": [0.62, 0.82]},
        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]}
    }
}

qc.add_bread_type("rye", my_profile)  # Automatically saves to qc_config.json
qc.set_bread_type("rye")  # Switch to new profile
```

### Method 2: Direct JSON Editing
Edit `qc_config.json` directly. Keys to remember:
- **target_** ranges: Pass = within these bounds (green in GUI)
- **warning_** ranges: Caution = outside target but within warning (yellow in GUI)
- Quality grades: Nested [min, max] arrays for porosity and uniformity scoring
- **consistency_cv_max**: Coefficient of variation threshold for batch uniformity (typically 0.12-0.20)

### Method 3: GUI-Based Creation
1. **Quality Control tab** → Click **"Custom Profile"** dropdown
2. Edit JSON in the configuration editor
3. Click **"💾 Save Config"** to persist to `qc_config.json`

### Key Considerations for New Profiles

**Porosity Ranges** (use measured data as reference):
- Dense breads (sandwich, pan loaves): 12-22%
- Medium breads (sourdough, baguette): 20-40%
- Open crumb (ciabatta, focaccia): 30-50%

**Hole Count/Diameter** should correlate:
- Fine texture → more holes, smaller diameter
- Open crumb → fewer holes, larger diameter
- Example: `hole_count_target_max / hole_diameter_target_max ≈ 50-100`

**Uniformity & Consistency:**
- `uniformity_acceptable_min`: Set to 0.6-0.8 (lower = more variation allowed)
- `consistency_cv_max`: Set to 0.12-0.20 (for slice-to-slice or batch uniformity)
- Stricter for commercial (sandwich bread); looser for artisan (ciabatta)

**Quality Grades:**
- Use historical data from `recipes.json` measured_porosity field
- Excellent: ±2-3% from your target midpoint
- Good: ±5-8% from target
- Fair: ±10-15% from target
- Ensure ranges don't overlap (good includes excellent range is acceptable)

### Validation Workflow
After adding a profile:

1. **Test with known samples**: Analyze images of that bread type; verify grade assignment matches visual inspection
2. **Check thresholds**: Use `qc.get_current_profile()` to verify all fields loaded
3. **Update recipes**: Add actual loaves to recipe database with `measured_porosity` field to train predictions
4. **Monitor SPC stats**: After 10+ measurements, check batch CV and mean for outliers

### Extending Beyond Profiles

If you need custom logic (e.g., different acceptance rules for fermented vs. non-fermented):
- **Override `evaluate_analysis()`** in a subclass of `QualityControlManager`
- **Add fields to profile** (non-standard keys are preserved in JSON) for metadata
- **Update `quality_control.py`** to handle new fields in evaluation logic

## Code Style & Patterns

- **Logging**: Use `logging` module, not `print()` (except for user-facing progress in CLI)
- **Error handling**: Raise `ValueError` for invalid inputs, `FileNotFoundError` for missing files, `json.JSONDecodeError` for config errors
- **Type hints**: All function signatures use `typing` annotations (required for GUI thread safety)
- **Config loading**: Always provide sensible defaults if JSON missing (see `quality_control.py` example)
- **Vectorization**: Use NumPy/OpenCV for image ops, NOT loops (critical for performance on large batches)

## Key Files to Read First

1. **[README.md](../README.md)** - Feature overview, quick start
2. **[PROJECT_OVERVIEW.py](../PROJECT_OVERVIEW.py)** - Philosophy and architecture summary
3. **[analyze.py](../analyze.py#L30)** - Entry point for understanding data flow
4. **[imaging_pipeline.py](../imaging_pipeline.py#L15)** - Core CV pipeline logic
5. **[metrics.py](../metrics.py#L25)** - Metric computation definitions
6. **[quality_control.py](../quality_control.py#L35)** - QC profile structure

