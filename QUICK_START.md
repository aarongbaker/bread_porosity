# Quick Start Guide

## 5-Minute Setup

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run
```bash
python gui.py
```

### 3. Calibrate (First Time Only)
- Click "Setup" button
- Follow on-screen calibration instructions
- Measure your reference object pixel size

---

## First Analysis

1. **Prepare Image**
   - Place bread slice image in `unprocessed/` folder
   - Ensure consistent lighting
   - Use transmitted light if possible

2. **Analyze**
   - Select image in GUI
   - Click "Analyze"
   - Wait for results (2-5 seconds)

3. **View Results**
   - Porosity percentage
   - Hole count and sizes
   - Processing pipeline visualizations

---

## Tabs Overview

| Tab | What It Does |
|-----|--------------|
| **Preview** | Shows selected image |
| **Results** | Porosity, holes, metrics |
| **Metrics** | Raw JSON data (export) |
| **Recipes & Prediction** | Manage recipes |
| **Statistics Dashboard** | Model quality |
| **Loaf Consistency** | Quality control |
| **Comparison Tools** | Compare recipes |

---

## Essential Features

### Log a Recipe
1. Click "Recipes & Prediction" tab
2. Edit JSON template (fill in ingredients, times, etc.)
3. Click "Log Recipe"
4. Done! Recipe saved

### Analyze Loaf (Multiple Slices)
1. Select "Loaf Analysis" mode
2. Name your loaf
3. Place slice images (numbered) in `unprocessed/`
4. Click "Analyze Loaf"
5. Check "Loaf Consistency" tab for uniformity

### Scale a Recipe
1. Select recipe from list
2. Click "Scale Recipe"
3. Enter scale factor (0.5 for half, 2.0 for double)
4. New scaled recipe created

### Clone a Recipe
1. Select recipe from list
2. Click "Clone Recipe"
3. Enter custom name (optional)
4. Independent copy created

### Compare Recipes
1. Click "Comparison Tools" tab
2. Click "Compare Recipes"
3. View all recipes side-by-side
4. See porosity for each

---

## Key Metrics

| Metric | What It Means | Typical |
|--------|---------------|---------|
| **Porosity %** | % of crumb that is air | 20-30% |
| **Hole Count** | Number of holes | 100-300 |
| **Mean Diameter** | Average hole size (mm) | 4-6mm |
| **CV (Uniformity)** | Consistency (lower=better) | 0.3-0.7 |

---

## Common Workflows

### Test Before Baking
```
1. Log recipe
2. Use "What-If Analysis" (click "Comparison Tools" tab)
3. See predicted impact of changes
4. Create variant with best changes
5. Bake and verify
```

### Scale for Production
```
1. Clone proven recipe (backup)
2. Click "Scale Recipe" → enter 2.0
3. Bake test batch with scaled amounts
4. Use Loaf Analysis to check uniformity
5. If good: use for production
```

### Optimize Recipe
```
1. Log recipe + analyze bread
2. Check Statistics Dashboard (model quality)
3. Create variants with modifications
4. Compare results using Family Tree
5. Repeat until satisfied
```

---

## Tips

✅ **DO:**
- Use consistent lighting for images
- Calibrate pixel size accurately
- Log environmental conditions (temperature, humidity)
- Analyze multiple slices per loaf
- Test changes one at a time

❌ **DON'T:**
- Assume cooking times scale with recipes
- Test multiple changes simultaneously
- Skip calibration
- Use low-quality images
- Forget to save porosity after analysis

---

## File Organization

```
project/
├── unprocessed/        ← Put images here
├── processed/          ← Analyzed images moved here
├── results/            ← Analysis outputs
├── gui.py             ← Run this
├── recipes.json       ← Recipe database (auto-created)
└── README.md          ← Full documentation
```

---

## Folder Mode

### Single Image
- Place image in `unprocessed/`
- Select image in GUI
- Click Analyze

### Multi-Slice Loaf
- Name slices: `loaf_name_001.jpg`, `loaf_name_002.jpg`, etc.
- Place all in `unprocessed/`
- Select "Loaf Analysis" mode
- Enter loaf name
- Click Analyze Loaf
- System auto-processes all slices

---

## Parameters to Know

### Recipe Parameters
- **Mixing Time** (min): How long to mix dough
- **Proof Time** (min): Fermentation duration
- **Oven Temp** (°C): Baking temperature
- **Cook Time** (min): Baking duration
- **Cooking Vessel**: Dutch oven, loaf pan, stone, etc.

### Environmental Data (Optional)
- **Room Temp** (°C): Temperature during fermentation
- **Room Humidity** (%): Humidity during fermentation
- **Altitude** (m): Elevation where baking occurs

### Analysis Settings
- **Pixel Size** (mm): Calibrated during setup
- **Threshold Method**: Otsu, Adaptive, Sauvola
- **Normalization**: Image contrast adjustment

---

## Troubleshooting

**Q: GUI won't start**
A: Check Python version (3.8+) and install requirements: `pip install -r requirements.txt`

**Q: No image selected**
A: Put images in `unprocessed/` folder and refresh list

**Q: Analysis is slow**
A: Reduce image size or simplify threshold method

**Q: Statistics show no data**
A: Log and analyze 2-3 recipes first to build training data

**Q: What-If results seem wrong**
A: Predictions improve with more recipes; log 5-10 recipes for better accuracy

---

## Next Steps

1. ✅ Run setup calibration
2. ✅ Analyze sample images
3. ✅ Log 3-5 recipes with measured porosity
4. ✅ Check Statistics Dashboard
5. ✅ Use What-If to test scenarios
6. ✅ Create and test recipe variants
7. ✅ Compare results

---

## Need Help?

- **Full Feature Guide**: See FEATURES.md
- **Installation Issues**: See INSTALLATION.md
- **Recipe Details**: See README.md

