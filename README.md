# Bread Porosity Analysis Tool

**Professional image processing software for measuring bread porosity, crumb structure, and quality metrics with real-time quality control.**

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Key Features

### Core Analysis
- **Porosity Measurement** - Calculate hole percentage of crumb structure
- **Hole Analysis** - Count, diameter, distribution, uniformity metrics
- **Shape Analysis** - Aspect ratio, orientation, anisotropy
- **Multi-slice Loaves** - Analyze entire loaf for consistency
- **Statistical Dashboard** - Comprehensive metrics and visualizations

### Recipe Management
- **Recipe Database** - Store bread recipes with formulas and steps
- **Recipe Comparison** - Compare multiple recipes side-by-side
- **Variant Creation** - Generate variants by scaling
- **Recipe Families** - Track recipe lineage

### Quality Control
- **Multi-Profile Support** - Different standards for different breads
- **5 Default Profiles** - Sourdough, Whole Wheat, Ciabatta, Sandwich, Baguette
- **SPC Statistics** - Statistical Process Control
- **Batch Consistency** - Monitor variation across batches
- **Alert System** - Real-time alerts for out-of-spec batches
- **Custom Profiles** - Define your own standards

### Export & Reporting
- **Multiple Formats** - CSV, Excel, PDF exports
- **Summary Charts** - Porosity trends, distributions
- **Batch Reports** - Comprehensive summaries
- **Professional Reports** - Ready to share

### Modern UI
- **Dark Professional Theme** - Material Design inspired
- **8 Organized Tabs** - Logical workflow
- **Real-time Status** - Live feedback
- **Responsive Design** - Clean and intuitive

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI
python gui.py
```

### First Analysis

1. **Open GUI**: `python gui.py`
2. **Load Image**: Click "Open Folder"
3. **Select Image**: Choose bread slice
4. **Analyze**: Click "▶ Analyze"
5. **View Results**: Check "Results" tab

### Multi-Slice Loaf

1. **Name slices**: `loaf_001.jpg`, `loaf_002.jpg`, etc.
2. **Select mode**: "Loaf (Multiple Slices)"
3. **Analyze**: Click "Analyze"
4. **Check uniformity**: Go to "Consistency" tab

---

## Project Structure

```
bread_porosity/
├── gui.py                 # Main GUI (2100+ lines)
├── analyze.py            # Analysis engine
├── quality_control.py    # QC with profiles
├── export_reporting.py   # Export functionality
├── recipe_*.py           # Recipe system
├── imaging_pipeline.py   # Image processing
├── unprocessed/          # Input images
├── processed/            # Output images
├── results/              # Analysis results
├── config.json           # Configuration
├── qc_config.json        # QC profiles
└── recipes.json          # Recipe database
```

---

## Configuration

### `config.json`
```json
{
  "pixel_size_mm": 0.1,
  "threshold_method": "otsu",
  "normalization_method": "clahe",
  "min_hole_diameter_mm": 1.0,
  "max_hole_diameter_mm": 30.0
}
```

### `qc_config.json` - Bread Type Profiles
```json
{
  "current_bread_type": "sourdough",
  "bread_types": {
    "sourdough": {
      "porosity_target_min": 20.0,
      "porosity_target_max": 35.0,
      "hole_count_target_min": 100,
      "hole_count_target_max": 400
    },
    "ciabatta": {
      "porosity_target_min": 30.0,
      "porosity_target_max": 45.0
    }
  }
}
```

---

## Bread Type Profiles

### Default Profiles

| Type | Porosity | Holes | Use Case |
|------|----------|-------|----------|
| Sourdough | 20-35% | 100-400 | Traditional artisan |
| Whole Wheat | 15-28% | 60-250 | Whole grain |
| Ciabatta | 30-45% | 200-600 | Very open crumb |
| Sandwich | 12-22% | 50-200 | Fine, uniform |
| Baguette | 25-40% | 150-500 | Crispy crust |
| Custom | User-defined | User-defined | Your recipe |

### Switch Profiles
1. Quality Control tab
2. Select type from dropdown
3. Click "👁 View Profile"
4. Analyze images - evaluated against profile

---

## GUI Tabs (11 Total)

| Tab | Purpose |
|-----|----------|
| Preview | Image preview |
| Results | Analysis results |
| Metrics | JSON metrics |
| Recipes | Recipe management |
| Statistics | Stats dashboard |
| Consistency | Loaf uniformity |
| Compare | Recipe comparison |
| Export | Data export |
| Quality Control | QC & profiles |

---

## Documentation

- **[Quick Start](QUICK_START.md)** - 5-minute guide
- **[Features](FEATURES.md)** - Complete feature reference
- **[Installation](INSTALLATION.md)** - Detailed setup
- **[Bread Type Profiles](BREAD_TYPE_PROFILES.md)** - Profile system
- **[GitHub Safe](GITHUB_SAFE.md)** - Production version

---

## What It Measures

**Porosity**
- Total hole percentage
- Uniformity across slices
- Distribution statistics

**Holes**
- Count and diameter
- Size distribution
- Aspect ratio & orientation
- Heterogeneity scoring

**Quality**
- Grade (Excellent/Good/Fair/Poor)
- Pass/fail against profile
- Recommendations

---

## Workflows

### Daily QC
```
Load batch → Select profile → Analyze each → 
Check consistency → Export CSV
```

### Recipe Development
```
Create recipe → Bake → Analyze → 
Log porosity → Predict → Create variant → 
Compare results
```

### Quality Investigation
```
Load batch → View SPC → Check alerts → 
Compare profiles → Export PDF
```

---

## Export Formats

- **CSV** - Spreadsheet analysis
- **Excel** - Formatted workbook
- **PDF** - Professional report
- **PNG Charts** - Visualizations

---

## Technical

**Requirements**
- Python 3.9+
- OpenCV, NumPy, SciPy
- Tkinter (GUI)
- Matplotlib, openpyxl, reportlab

**Dependencies**
```bash
pip install -r requirements.txt
```

**File Sizes**
- Total code: ~2500+ lines
- GUI: 2100+ lines
- QC engine: 571 lines
- Export: 380 lines

---

## Performance

- Single image: < 5 seconds
- Loaf (5 slices): < 30 seconds
- Export batch (100 images): < 2 minutes
- GUI responsive with dark theme

---

## Version

**Current**: 2.0.0 (Production Ready)

**Latest Features**
- Multi-profile QC system
- Export/reporting engine
- Modern dark theme UI
- Real-time predictions
- Statistical process control

---

## Common Tasks

### Analyze Single Image
File → Unprocessed → Select → Analyze → Results

### Measure Loaf Uniformity
Name files → Select Loaf mode → Analyze → Consistency tab

### Predict Porosity
Recipes tab → Log recipe → Click Predict

### Compare Recipes
Compare tab → Select recipes → View side-by-side

### Generate Report
Export tab → Select format → Click Export

---

## Troubleshooting

**GUI won't start**
- Check Python 3.9+
- Run: `pip install -r requirements.txt`

**Images not found**
- Place in `unprocessed/` folder
- Click "🔄 Refresh"

**Analysis slow**
- Reduce image resolution
- Use adaptive threshold

**Profile not found**
- Check `qc_config.json` exists
- Verify JSON syntax
- Restart GUI

---

##  License

MIT License - See LICENSE file

---

## 🎯 Start Now

```bash
python gui.py
```

**Ready to analyze bread! **

