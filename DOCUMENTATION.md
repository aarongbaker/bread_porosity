# Bread Porosity Analysis Tool - Complete Documentation

**Professional image processing software for measuring bread porosity, crumb structure, and quality metrics with machine learning predictions and real-time quality control.**

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Features Overview](#features-overview)
4. [Core Analysis](#core-analysis)
5. [Recipe Management & ML Prediction](#recipe-management--ml-prediction)
6. [Quality Control Profiles](#quality-control-profiles)
7. [Export & Reporting](#export--reporting)
8. [Project Structure](#project-structure)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run GUI
python gui.py
```

### First Analysis

1. **Open GUI**: `python gui.py`
2. **Load Image**: Click "Open Folder" 
3. **Select Image**: Choose a bread slice image (JPEG or PNG)
4. **Analyze**: Click "▶ Analyze"
5. **View Results**: Check the "Results" tab for metrics and visualizations

### Multi-Slice Loaf Analysis

1. **Name slices**: `loaf_001.jpg`, `loaf_002.jpg`, etc. (numerical suffix required)
2. **Select mode**: "Loaf (Multiple Slices)"
3. **Analyze**: Click "Analyze"
4. **Check uniformity**: Go to "Consistency" tab to see variation across slices

---

## Installation

### System Requirements

- [ ] Python 3.9 or newer
- [ ] Windows, macOS, or Linux OS
- [ ] 2GB RAM minimum (4GB recommended)
- [ ] Sample bread images (JPG or PNG format)

### Windows Installation

**Step 1: Install Python**
1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify: `python --version`

**Step 2: Navigate to Project**
```powershell
cd C:\Users\YourUsername\Desktop\bread_porosity
```

**Step 3: Create Virtual Environment (Recommended)**
```powershell
# Create virtual environment
python -m venv venv

# Activate (if execution policy error, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)
.\venv\Scripts\Activate.ps1

# Verify (should see (venv) in prompt)
```

**Step 4: Install Dependencies**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Step 5: Run GUI**
```powershell
python gui.py
```

### macOS Installation

**Step 1: Install Python & Homebrew**
```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9

# Verify
python3 --version
```

**Step 2: Navigate to Project**
```bash
cd ~/Desktop/bread_porosity
```

**Step 3: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 4: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 5: Run GUI**
```bash
python gui.py
```

### Linux Installation

**Step 1: Install Python**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3.9 python3-pip
```

**Step 2: Navigate to Project**
```bash
cd ~/Desktop/bread_porosity
```

**Step 3: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 4: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 5: Run GUI**
```bash
python gui.py
```

### Verify Installation

```bash
python -c "import cv2, numpy, matplotlib, scipy; print('All packages installed successfully')"
```

---

## Features Overview

### Core Analysis Features
- **Porosity Measurement** - Calculate hole percentage of crumb structure
- **Hole Analysis** - Count, diameter, distribution, uniformity metrics
- **Shape Analysis** - Aspect ratio, orientation, anisotropy
- **Multi-slice Loaves** - Analyze entire loaf for consistency
- **Statistical Dashboard** - Comprehensive metrics and visualizations

### Recipe Management
- **Recipe Database** - Store bread recipes with formulas
- **Porosity Prediction** - ML predictions from recipe parameters
- **Recipe Comparison** - Compare multiple recipes side-by-side
- **Variant Creation** - Generate variants by scaling ingredients
- **Recipe Families** - Track recipe lineage and variations

### Quality Control
- **Multi-Profile Support** - Different standards for different breads
- **5 Default Profiles** - Sourdough, Whole Wheat, Ciabatta, Sandwich, Baguette
- **SPC Statistics** - Statistical Process Control tracking
- **Batch Consistency** - Monitor variation across batches
- **Alert System** - Real-time alerts for out-of-spec batches
- **Custom Profiles** - Define your own standards

### AI & Defect Detection
- **Automated Defect Detection** - Identifies uneven rise and dense spots
- **Simple ML Classifier** - Train on your own images to classify good/problem bread
- **No Dataset Required** - Build training data as you analyze bread
- **Batch Analysis** - Analyze multiple images at once
- **Confidence Scoring** - Know how certain predictions are

### Export & Reporting
- **Multiple Formats** - CSV, Excel, PDF exports
- **Summary Charts** - Porosity trends and distributions
- **Batch Reports** - Comprehensive summaries with statistics
- **Professional Reports** - Ready-to-share formatted output

### User Interface
- **Dark Professional Theme** - Material Design inspired
- **9 Organized Tabs** - Logical workflow organization
- **Real-time Status** - Live feedback and progress
- **Responsive Design** - Clean and intuitive controls

---

## Core Analysis

### Image Processing Pipeline

**Input:** Bread slice images (JPEG, PNG)  
**Output:** Porosity metrics, hole analysis, visualizations

**6-Step Processing:**
1. **Grayscale Conversion** - Simplifies image to intensity values
2. **Illumination Normalization** - Uses CLAHE + morphological operations to handle uneven lighting
3. **ROI Detection** - Identifies bread boundaries automatically
4. **Threshold** - Uses Otsu or adaptive thresholding to separate air from crumb
5. **Morphological Cleaning** - Removes noise and fills small holes
6. **Connected Component Analysis** - Identifies and measures individual holes

### Measurement Metrics

| Metric | What It Measures | Typical Range | Formula |
|--------|-----------------|---------------|---------|
| **Porosity %** | Hole area as % of crumb area | 15-40% | (Total hole area / Total crumb area) × 100 |
| **Hole Count** | Number of holes detected | 50-500 | Connected components > min size |
| **Mean Diameter** | Average hole size | 2-8 mm | √(4×Area/π) per hole, then averaged |
| **Aspect Ratio** | Hole elongation (1.0=circle) | 1.0-3.0 | Major axis / Minor axis |
| **Coefficient of Variation** | Hole size uniformity | 0.3-0.8 | StdDev(hole sizes) / Mean(hole size) |
| **Orientation Entropy** | Hole directionality | 0.0-1.0 | Shannon entropy of angle distribution |
| **Crumb Brightness** | Crumb color uniformity | 0-100% | Pixel intensity variation |

### Analysis Modes

**Single Image Mode:**
- Load image → Configure parameters → Analyze → View results
- Best for: Quick analysis, recipe testing, single bread slices

**Loaf Mode (Multi-Slice):**
- Name slices sequentially (e.g., loaf_001.jpg, loaf_002.jpg)
- Analyze all slices together
- Compare uniformity across the entire loaf
- Best for: Quality consistency monitoring, batch analysis

### Processing Parameters

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| **Min Hole Size (mm²)** | 10 | 1-100 | Smaller = detects tiny holes; Larger = ignores noise |
| **Threshold Method** | Otsu | Otsu/Adaptive | Otsu = global; Adaptive = local sensitivity |
| **CLAHE Clip Limit** | 2.0 | 1-5 | Higher = more contrast enhancement |
| **Morph Kernel Size** | 5 | 3-11 | Larger = more aggressive cleaning |
| **ROI Margin** | 10 px | 0-50 | Pixels to exclude from bread edge |

---

## Recipe Management & ML Prediction

### Recipe Database System

**Storage:** `recipes.json` - Standard JSON format with recipes and measured porosity

**Recipe Structure:**
```json
{
  "name": "My Sourdough",
  "ingredients": {
    "bread flour": 500,
    "water": 350,
    "salt": 10,
    "sourdough starter": 100,
    "olive oil": 10
  },
  "mixing_time_min": 10,
  "proof_time_min": 480,
  "oven_temp_c": 450,
  "cooking_vessel": "dutch oven",
  "cook_time_min": 40,
  "measured_porosity": 28.5
}
```

### ML Porosity Prediction System

#### Quick Start (5 Minutes)

```python
from recipe_database import RecipeDatabase
from recipe_predictor import RecipePredictor

# Load recipes
db = RecipeDatabase("recipes_example.json")
recipes = db.get_all_recipes()
print(f"Loaded {len(recipes)} recipes")

# Create predictor (auto-trains models)
predictor = RecipePredictor(recipes, use_advanced_ml=True)
# Automatically:
# - Analyzes ingredients
# - Parses instructions
# - Engineers 20+ features
# - Trains 4 ML models with cross-validation
# - Takes ~2-5 seconds for 50-100 recipes

# Make predictions
new_recipe = {
    "name": "Test Sourdough",
    "ingredients": {
        "bread flour": 500,
        "water": 350,
        "salt": 10,
        "sourdough starter": 100
    },
    "mixing_time_min": 10,
    "proof_time_min": 480,
    "oven_temp_c": 450,
    "cooking_vessel": "dutch oven",
    "cook_time_min": 40
}

predicted_porosity, details = predictor.predict_porosity(new_recipe)
print(f"Predicted porosity: {predicted_porosity:.1f}%")
print(f"Model confidence: {details.get('confidence', 'N/A')}")
```

#### How the ML System Works

**Component 1: Ingredient Analyzer**

Extracts porosity-relevant factors from ingredients:

| Feature | Purpose | Impact on Porosity |
|---------|---------|-------------------|
| **Hydration Ratio** | Dough consistency | >75% → Larger holes; <60% → Fine crumb |
| **Gluten Score** | Dough strength | Bread flour (0.95) > AP (0.80) > Whole Wheat (0.70) |
| **Enzymatic Activity** | Fermentation power | Whole grains & starters rate higher |
| **Hydrophilic Score** | Water-binding capacity | Hydrocolloids & whole grains score higher |
| **Salt %** (baker's %) | Fermentation control | 1-3% typical; slows fermentation |
| **Starter %** | Fermentation source | Higher % = faster fermentation |
| **Sugar %** | Fermentation fuel | Higher % = more gas production |
| **Fat %** | Crumb structure | Affects gas retention |

**Component 2: Instruction Analyzer**

Detects process factors from baking instructions:

| Technique | Effect | Description |
|-----------|--------|-------------|
| **Autolyse** | Dough relaxation | Pre-mixing water+flour hydration (30+ min) |
| **Long Fermentation** | Gas development | Bulk ferment >4 hours or overnight cold ferment |
| **Lamination** | Gluten development | Strengthens dough, affects crumb |
| **High-Temp Bake** | Oven spring | >450°C correlates with more open crumb |
| **Covered Bake** | Steam retention | Dutch oven → tighter crumb initially |
| **Multiple Folds** | Gluten layering | Multiple stretch-and-folds increase strength |
| **Cold Fermentation** | Flavor & enzyme activity | Lower temp = slower fermentation = finer crumb |
| **Mixing Method** | Gluten development | Hand/stretch-fold vs. machine mixer |

**Component 3: Feature Engineering**

Combines 20+ features engineered from ingredients and instructions:
- Hydration ratio, gluten score, enzymatic activity, salt percentage
- Fermentation time, proof temperature, oven temperature
- Cooking vessel type and bake time
- Advanced interaction terms between features

**Component 4: Ensemble ML Models**

Trains 4 different models with cross-validation:
- Random Forest
- Gradient Boosting
- Support Vector Machine (SVM)
- Neural Network (if enough data)

Each model votes on the final prediction, with confidence calculated from model agreement.

#### Using ML in the GUI

1. **Navigate to** "Recipes & Prediction" tab
2. **Add recipes** with measured porosity data
3. **Train models** - Click "Train" button (auto-trains on app startup if data available)
4. **Make predictions** - Enter new recipe and click "Predict"
5. **View confidence** - See how certain the system is in its prediction

---

## Quality Control Profiles

### Overview

The Quality Control system supports **multiple bread type profiles** with customized standards for:

- **Sourdough** - Higher porosity, rustic crumb (20-35%)
- **Whole Wheat** - Lower porosity, denser crumb (15-28%)
- **Baguette** - High porosity, open crumb (25-40%)
- **Sandwich Bread** - Low porosity, fine crumb (12-22%)
- **Ciabatta** - Very high porosity, large holes (30-45%)
- **Custom** - User-defined profile

### Default Bread Type Profiles

#### Sourdough
**Characteristics:** Traditional European-style with moderate porosity and balanced holes

| Parameter | Target | Warning Range |
|-----------|--------|----------------|
| Porosity | 20-35% | 18-37% |
| Hole Count | 100-400 | - |
| Hole Diameter | 2.0-8.0 mm | - |
| Uniformity Minimum | 0.70 | - |
| Batch CV Maximum | 15% | - |

**Quality Grades:**
- **Excellent**: Porosity 25-32%, Uniformity 0.85+
- **Good**: Porosity 22-35%, Uniformity 0.75+
- **Fair**: Porosity 18-38%, Uniformity 0.65+

#### Whole Wheat
**Characteristics:** Denser crumb structure with smaller holes

| Parameter | Target | Warning Range |
|-----------|--------|----------------|
| Porosity | 15-28% | 12-32% |
| Hole Count | 60-250 | - |
| Hole Diameter | 1.5-6.0 mm | - |
| Uniformity Minimum | 0.65 | - |
| Batch CV Maximum | 18% | - |

**Quality Grades:**
- **Excellent**: Porosity 20-26%, Uniformity 0.80+
- **Good**: Porosity 16-28%, Uniformity 0.70+
- **Fair**: Porosity 12-32%, Uniformity 0.60+

#### Ciabatta
**Characteristics:** Very open, irregular crumb with large holes

| Parameter | Target | Warning Range |
|-----------|--------|----------------|
| Porosity | 30-45% | 28-48% |
| Hole Count | 200-600 | - |
| Hole Diameter | 3.0-12.0 mm | - |
| Uniformity Minimum | 0.60 | - |
| Batch CV Maximum | 20% | - |

**Quality Grades:**
- **Excellent**: Porosity 35-42%, Uniformity 0.80+
- **Good**: Porosity 30-45%, Uniformity 0.70+
- **Fair**: Porosity 28-48%, Uniformity 0.60+

#### Sandwich Bread
**Characteristics:** Fine, uniform crumb for slicing

| Parameter | Target | Warning Range |
|-----------|--------|----------------|
| Porosity | 12-22% | 10-25% |
| Hole Count | 50-200 | - |
| Hole Diameter | 1.0-4.0 mm | - |
| Uniformity Minimum | 0.75 | - |
| Batch CV Maximum | 12% | - |

**Quality Grades:**
- **Excellent**: Porosity 15-20%, Uniformity 0.85+
- **Good**: Porosity 12-22%, Uniformity 0.75+
- **Fair**: Porosity 10-25%, Uniformity 0.65+

#### Baguette
**Characteristics:** Open crumb with elongated holes

| Parameter | Target | Warning Range |
|-----------|--------|----------------|
| Porosity | 25-40% | 22-43% |
| Hole Count | 150-500 | - |
| Hole Diameter | 2.5-10.0 mm | - |
| Uniformity Minimum | 0.65 | - |
| Batch CV Maximum | 16% | - |

**Quality Grades:**
- **Excellent**: Porosity 32-38%, Uniformity 0.80+
- **Good**: Porosity 25-40%, Uniformity 0.70+
- **Fair**: Porosity 22-43%, Uniformity 0.60+

### Using Quality Control in the GUI

1. **Navigate to** "Loaf Consistency" tab
2. **Select bread type** from dropdown (or create custom)
3. **Analyze loaf** - Multi-slice analysis compares against profile standards
4. **View results** - See if each slice meets quality targets
5. **Track batches** - Historical data shows trends over time

### Creating Custom Profiles

1. Click **"Edit Profiles"** button (in QC tab)
2. **Add new profile** with your standards
3. **Set parameters** based on your quality targets
4. **Save** - Profile automatically saved to `qc_config.json`
5. **Use** - Select your custom profile in analysis

---

## Export & Reporting

### Export Formats

The tool supports multiple export formats:

| Format | Use Case | Contents |
|--------|----------|----------|
| **CSV** | Data analysis in Excel/spreadsheet | Porosity %, metrics, hole data |
| **Excel** | Professional reports | Multiple sheets with charts |
| **PDF** | Print/archive | Formatted summary with visualizations |
| **JSON** | Data integration | Raw measurement data |

### Export Features

- **Summary Statistics** - Mean, std dev, min/max for all metrics
- **Charts & Graphs** - Porosity distributions, hole size histograms
- **Batch Reports** - Compare multiple loaves side-by-side
- **Time Series** - Track quality trends across production
- **Custom Fields** - Add notes, batch ID, date, operator

### Exporting from GUI

1. **Analyze images** as normal
2. **Click "Export"** button in Results tab
3. **Select format** (CSV, Excel, PDF)
4. **Configure options** - Choose what to include
5. **Save file** - Choose location and filename

---

## Project Structure

```
bread_porosity/
├── Core Modules
│   ├── gui.py                      # Main GUI interface (2100+ lines)
│   ├── analyze.py                  # Core analysis engine
│   ├── imaging_pipeline.py         # Image processing pipeline
│   ├── metrics.py                  # Measurement calculations
│   └── calibration.py              # Camera calibration tools
│
├── Recipe & ML System
│   ├── recipe_database.py          # Recipe storage and retrieval
│   ├── recipe_predictor.py         # ML prediction engine
│   ├── recipe_ml_trainer.py        # Model training
│   ├── recipe_ml_advanced.py       # Advanced feature engineering
│   ├── ml_simple.py                # Simple classification
│   ├── ml_examples.py              # ML usage examples
│   └── recipes_example.json        # Sample recipes
│
├── Quality Control & Export
│   ├── quality_control.py          # QC profiles and checks
│   ├── defect_detection.py         # Defect identification
│   ├── export_reporting.py         # Export functionality
│   ├── visualization.py            # Chart generation
│   └── shared_utils.py             # Shared utility functions
│
├── Configuration
│   ├── config.json                 # Application settings
│   ├── config_template.json        # Configuration template
│   ├── qc_config.json              # Quality control profiles
│   └── requirements.txt            # Python dependencies
│
├── Data Folders (created at runtime)
│   ├── unprocessed/                # Input images
│   ├── processed/                  # Output images
│   └── results/                    # Analysis results
│
└── Documentation
    ├── README.md                   # Main documentation
    ├── DOCUMENTATION.md            # This consolidated guide
    ├── QUICK_START.md              # Quick reference
    ├── INSTALLATION.md             # Detailed installation
    ├── FEATURES.md                 # Feature details
    ├── ML_COMPLETE_GUIDE.md        # ML system guide
    └── BREAD_TYPE_PROFILES.md      # QC profiles
```

### Key File Responsibilities

| File | Responsibility |
|------|-----------------|
| **gui.py** | User interface, tab management, user interaction |
| **analyze.py** | Image analysis pipeline coordination |
| **imaging_pipeline.py** | Low-level image processing operations |
| **quality_control.py** | QC profile management and checking |
| **recipe_predictor.py** | Porosity prediction from recipes |
| **shared_utils.py** | Shared utilities (vessel encoding, statistics) |
| **export_reporting.py** | Export to CSV/Excel/PDF formats |

---

## Troubleshooting

### Import Errors

**Problem:** `ImportError: attempted relative import with no known parent package`

**Solution:** Ensure you're running from the correct directory:
```bash
cd bread_porosity
python gui.py
```

### Image Analysis Issues

**Problem:** "No ROI detected" or "Cannot find bread in image"

**Causes:**
- Image too small (use 1000+ px width)
- Very poor lighting conditions
- Bread at extreme angle
- Background similar color to bread

**Solutions:**
1. Ensure good lighting, especially transmitted light
2. Keep bread relatively flat/straight
3. Use crop tool to isolate bread area
4. Increase "ROI Margin" parameter if bread edges cut off

### ML Prediction Issues

**Problem:** "Only 0 recipes with porosity data. Need at least 5 for reliable training"

**Causes:** Not enough recipes with measured porosity values

**Solution:**
1. Analyze several bread images (get measured porosity)
2. Create recipes for them
3. Add measured_porosity field to recipes
4. Save to recipes.json
5. Restart GUI - ML will auto-train

### GUI Display Issues

**Problem:** Status or content boxes are cut off

**Solution:**
- Resize window to larger size
- Check wraplength parameters in gui.py
- Try different display scaling settings

### Performance Issues

**Problem:** Analysis or ML training is slow

**Causes:**
- Large image resolution
- Too many holes to analyze
- Slow computer/limited RAM

**Solutions:**
1. Use 1000-2000 px wide images (not larger)
2. Reduce image resolution if possible
3. Close other programs
4. Add more RAM if consistently slow
5. Check "Min Hole Size" parameter - increase to skip tiny holes

### File Not Found Errors

**Problem:** "Cannot find config.json" or "recipes.json not found"

**Solutions:**
1. Ensure you're in correct directory: `cd bread_porosity`
2. Copy from template: `cp config_template.json config.json`
3. Restart GUI
4. Files will be created in correct location

---

## Next Steps

- **New to the tool?** → Start with Quick Start section above
- **Want to understand analysis?** → See Core Analysis section
- **Want to use ML?** → See Recipe Management & ML Prediction section
- **Setting up QC?** → See Quality Control Profiles section
- **Need help?** → See Troubleshooting section

---

**For the latest updates and support, check the project repository and documentation.**
