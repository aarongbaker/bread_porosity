# Bread Porosity Analysis Tool

Comprehensive image processing tool for measuring bread porosity, hole distribution, uniformity, and crumb structure using standardized imaging techniques.

**Status:** ✅ Full-featured | Includes GUI, recipe system, statistics, quality control

---

## What It Does

- **Measure Porosity**: Calculate hole percentage of crumb
- **Analyze Holes**: Count, size, distribution, uniformity
- **Shape Analysis**: Aspect ratio, orientation, anisotropy
- **Track Quality**: Multi-slice uniformity assessment
- **Manage Recipes**: Log, predict, compare, optimize
- **Statistics**: Model quality metrics, feature importance
- **Scaling**: Adjust batch sizes by scaling ingredients

---

## Quick Start

### Install & Run
```bash
pip install -r requirements.txt
python gui.py
```

### First Time Setup
1. Click "Setup" button in GUI
2. Follow calibration instructions
3. Ready to analyze images

### Analyze an Image
1. Place bread slice image in `unprocessed/` folder
2. Select image in GUI
3. Click "Analyze"
4. View results

### Analyze Multi-Slice Loaf
1. Name slices: `loaf_name_001.jpg`, `loaf_name_002.jpg`, etc.
2. Place in `unprocessed/` folder
3. Select "Loaf Analysis" mode
4. Click "Analyze Loaf"
5. Check "Loaf Consistency" for uniformity

---

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **QUICK_START.md** | 5-min getting started | Everyone (start here) |
| **FEATURES.md** | Complete feature guide | All users |
| **INSTALLATION.md** | Detailed setup | New users |

---

## Key Features

### Image Analysis
- 6-step processing pipeline
- Automatic ROI detection
- Robust thresholding
- Morphological cleanup
- Connected-component analysis

### Measurements
- Porosity (%)
- Hole count & diameter distribution
- Aspect ratio & orientation
- Crumb brightness uniformity
- Full metrics JSON export

### Recipe System
- Log recipes with ingredients & parameters
- Track environmental conditions (temp, humidity, altitude)
- Link measured porosity to recipes
- Predict porosity from recipe parameters
- Clone recipes for experimentation
- Scale recipes for different batch sizes
- Create variants with version tracking

### Statistics
- R² (model quality metric)
- 95% confidence intervals
- Residual analysis (MAE, RMSE)
- Feature importance ranking
- Statistical significance testing

### Quality Control
- Multi-slice loaf analysis
- Uniformity scoring (CV-based)
- Quality grades (Excellent/Good/Fair/Poor)
- Automatic recommendations

### Optimization
- Side-by-side recipe comparison
- What-If scenario analysis
- Family tree visualization
- Recipe genealogy tracking

---

## File Organization

```
bread_porosity/
├── gui.py                 ← Main GUI application
├── analyze.py            ← Command-line analysis
├── recipe_database.py    ← Recipe storage system
├── recipe_predictor.py   ← Statistical predictions
├── imaging_pipeline.py   ← Image processing core
├── metrics.py            ← Metric calculations
├── loaf_analyzer.py      ← Multi-slice analysis
├── visualization.py      ← Result visualization
│
├── unprocessed/          ← Input images here
├── processed/            ← Analyzed images moved here
├── results/              ← Analysis outputs
│
├── recipes.json          ← Recipe database (auto-created)
├── requirements.txt      ← Python dependencies
├── config.json           ← Configuration
│
├── README.md             ← This file
├── QUICK_START.md        ← Quick reference
├── FEATURES.md           ← Complete guide
├── INSTALLATION.md       ← Setup details
└── GITHUB_SAFE.md        ← Distribution info
```

---

## System Requirements

- **Python:** 3.8+
- **OS:** Windows, macOS, Linux
- **Disk:** ~200MB (including dependencies)
- **RAM:** 2GB typical

### Dependencies
- OpenCV, NumPy, SciPy, Pillow (imaging)
- Tkinter (GUI)
- Matplotlib (visualization)

---

## Core Workflow

```
1. SETUP
   └─ Calibrate pixel size (one time)

2. ANALYZE IMAGES
   ├─ Single image → single porosity value
   └─ Loaf (multiple slices) → uniformity assessment

3. LOG RECIPES
   └─ Record ingredients, parameters, environmental data

4. TRACK RESULTS
   ├─ Link porosity to recipes
   └─ Build training data for predictions

5. OPTIMIZE
   ├─ Use Statistics Dashboard for model quality
   ├─ What-If Analysis for scenario testing
   ├─ Create Variants to track modifications
   └─ Compare recipes to find best approach

6. SCALE & PRODUCE
   ├─ Scale recipes for production
   └─ Use Loaf Consistency for quality control
```

---

## Key Concepts

### Porosity
The percentage of bread volume that is air (holes). Higher porosity = more open crumb. Typical range 15-40% depending on bread type.

### Coefficient of Variation (CV)
Uniformity metric = Standard Deviation / Mean × 100%
- CV < 10%: Excellent uniformity
- CV 10-20%: Good
- CV > 30%: Poor

### R² (Model Quality)
Ranges 0 to 1. Higher = better predictions.
- R² > 0.7: Good predictions
- R² 0.5-0.7: Fair predictions
- R² < 0.5: Poor, need more data

### Feature Importance
Which recipe factors most affect porosity. Ranked by correlation + statistical significance.

---

## Common Tasks

### Measure Porosity
```
1. Place image in unprocessed/
2. Select image
3. Click Analyze
→ Porosity % displayed in Results tab
```

### Predict Porosity
```
1. Log recipe
2. Click Predict button
→ Predicted porosity shown
→ Confidence level displayed
```

### Compare Recipes
```
1. Comparison Tools tab
2. Click Compare Recipes
→ All recipes side-by-side
→ Porosity for each shown
```

### Test What-If Scenarios
```
1. Select recipe
2. Comparison Tools tab
3. Click What-If Analysis
→ 6 scenarios shown
→ Predicted impacts displayed
```

### Scale for Production
```
1. Select recipe
2. Click Scale Recipe
3. Enter scale factor (2.0 for double)
→ New recipe created with scaled ingredients
→ Comparison table shown
```

### Analyze Loaf Uniformity
```
1. Place slice images in unprocessed/
2. Select Loaf Analysis mode
3. Enter loaf name
4. Click Analyze Loaf
→ Switch to Loaf Consistency tab
→ Uniformity score & recommendations
```

---

## Tabs Explained

| Tab | Shows | Use When |
|-----|-------|----------|
| **Preview** | Selected image | Check image quality |
| **Results** | Porosity & metrics | View analysis results |
| **Metrics** | Raw JSON data | Export or technical review |
| **Recipes & Prediction** | Recipe tools | Manage recipes, predict |
| **Statistics Dashboard** | Model quality | Check prediction reliability |
| **Loaf Consistency** | Uniformity analysis | Quality control (auto-shows) |
| **Comparison Tools** | Recipe comparison | Compare or simulate changes |

---

## Tips

✅ **Best Practices:**
- Use consistent lighting for all images
- Calibrate pixel size accurately
- Log environmental conditions
- Test one change at a time
- Analyze multiple slices per loaf
- Track all iterations

❌ **Common Mistakes:**
- Using poor-quality images
- Skipping calibration
- Multiple simultaneous changes
- Assuming cooking times scale linearly
- Low-quality lighting setup

---

## Getting Help

1. **Getting Started?** → See QUICK_START.md
2. **Need Details?** → See FEATURES.md
3. **Installation Issues?** → See INSTALLATION.md
4. **Questions?** → Check docstrings in code

---

## Version Info

- **Tool**: Bread Porosity Analysis
- **Status**: Production ready
- **Latest**: Includes GUI, full recipe system, advanced statistics
- **Python**: 3.8+

---

## License

See LICENSE file for details.

