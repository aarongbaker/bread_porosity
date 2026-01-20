# New Features - Quick Start Guide

Welcome to the improved Bread Porosity Tool! Here's what's new and how to use it.

---

## 🚀 First Time Using the Tool?

### What Happens on First Launch
When you run `python gui.py` for the first time, you'll see a **Setup Wizard**:

1. **Welcome Screen** - Overview of what the tool does
2. **Calibration** - Two options:
   - **Image-based** (Recommended): Take a photo of a ruler, tool calculates pixel size automatically
   - **Manual**: Enter pixel size (0.05-0.2 mm/pixel based on your camera)
3. **Workspace Setup** - Checklist for your backlit bread imaging setup
4. **Bread Type Selection** - Choose what type of bread you'll analyze

**After Setup**: All settings saved to `config.json`, wizard won't show again unless you delete the config file.

---

## 📸 Image Quality Feedback

### Before Analysis
When you select an image and click **Analyze**, the tool now checks image quality:

**Quality Score: 82% ✅**
- ✅ Resolution good (2500×1800)
- ✅ Focus sharp (Laplacian: 1200)
- ⚠️ Lighting slightly uneven (CV: 16%)
- ✅ Exposure correct
- ✅ Contrast good
- ✅ Image not rotated

**Recommendations:**
- "Image quality is good. Lighting slightly uneven but acceptable."

---

## 📊 Simpler Results Display

### Before
Results showed 30+ metrics - overwhelming for casual users.

### After
**Simple View** (Default):
```
ANALYSIS RESULTS
════════════════════════════

POROSITY:  42.3%
Quality:   ✅ Excellent

HOLES:
  Count:     248
  Average:   5.2 mm
  Uniformity: Good

INTERPRETATION:
This is within normal range for sourdough.
Excellent open crumb structure with uniform hole distribution.
```

**View Full Metrics** (Button to toggle):
```
Advanced View with all 30+ technical metrics...
```

### How to Use
- **Simple View**: Good for quick quality checks
- **Toggle to Advanced**: Click button for full technical data
- No re-analysis needed - just switch views

---

## 🍞 Recipe Management - No More JSON!

### Old Way
Paste JSON:
```json
{
  "name": "My Sourdough",
  "ingredients": {"bread_flour": 500, "water": 350, ...},
  "mixing_time_min": 10,
  ...
}
```

### New Way
Click **"Add Recipe"** button → **Form opens with 4 tabs**:

#### Tab 1: Basic Info
- Recipe Name: `_________________`
- Bread Type: [Sourdough ▼]
- Notes: `_________________`

#### Tab 2: Ingredients (in grams)
```
Bread Flour:  500
Water:        350
Salt:         10
Yeast:        0.5
(+ "Add Custom Ingredient" button for others)
```

#### Tab 3: Process
```
Mixing Time:      10 minutes
Proof Time:       480 minutes
Oven Temp:        450 °C
Cooking Vessel:   [Dutch Oven ▼]
Cook Time:        40 minutes
```

#### Tab 4: Environment (Optional)
```
Room Temp:     22 °C
Room Humidity: 65 %
Altitude:      200 meters
(Leave blank if not tracking)
```

**Click Save** → Recipe stored in database automatically!

---

## 🎯 Workflow Examples

### Example 1: Analyze Your First Loaf
1. **First time?** Setup wizard runs automatically
2. **Load image**: Click "Open Folder"
3. **Select image**: Click on bread slice in list
4. **Analyze**: Click "Analyze" button
5. **View results**: See simple view with 3 key metrics
6. **Save porosity**: Click "Log Result" to save measurement

### Example 2: Compare Two Recipes
1. **Add Recipe 1**: Click "Add Recipe", fill form, save
2. **Bake loaf with Recipe 1**: Analyze and log porosity
3. **Add Recipe 2**: Click "Add Recipe" again
4. **Bake loaf with Recipe 2**: Analyze and log porosity
5. **Compare**: Go to "Recipes" tab, select both, click "Compare"
6. See which recipe gave better porosity

### Example 3: Investigate Image Quality Issues
1. **Analyze image**: Gets low quality score
2. **Check feedback**: "Exposure too dark - increase lighting"
3. **Fix issue**: Adjust backlit setup
4. **Try again**: Re-analyze with improved setup
5. **Success**: Quality score improves, results more reliable

---

## 🔧 Settings (How to Access)

### First-Run Configuration
- **Automatic**: Setup wizard on first launch
- **Manual**: Delete `config.json`, restart, re-run wizard

### Change Pixel Size
1. Go to **Analysis Tab**
2. Edit "Pixel Size (mm/pixel)" field
3. Click "Recalibrate" (if available) or just enter value

### Switch Bread Type Profile
1. Go to **Quality Control Tab**
2. Click bread type dropdown: [Sourdough ▼]
3. Select different type (Whole Wheat, Ciabatta, etc.)
4. Current analysis evaluated against new profile

### Switch Result View
1. In **Results Tab**
2. Click **"[Simple]"** or **"[Advanced]"** button at top
3. Display updates instantly

---

## 📱 Status Messages Explained

### Green ✅
- Analysis complete
- Image quality good
- Recipe saved successfully

### Yellow ⚠️
- Image quality borderline
- Results outside normal range
- Measurement may be less reliable

### Red ✗
- Analysis failed
- Image too poor quality
- Recipe missing required fields

---

## 🆘 Common Issues

**Q: Image quality score is 45% - what should I do?**  
A: Check the recommendations. Usually it's lighting or focus. Adjust setup and try again.

**Q: Recipe form won't let me save - why?**  
A: Recipe needs: name, at least one ingredient, all process fields filled. Check for red X marks.

**Q: Simple view missing some metrics I need**  
A: Click "Advanced" view button. All 30+ metrics available there.

**Q: First-run wizard doesn't appear anymore**  
A: It won't - wizard only shows once. If you need to recalibrate: delete `config.json` and restart.

---

## 💡 Tips for Best Results

1. **Calibration**: Use image-based calibration with clear ruler photo
2. **Lighting**: Backlit setup is critical - wizard gives setup guide
3. **Focus**: Keep camera steady, focus on bread holes
4. **Results**: Simple view good for daily QC, advanced view for research
5. **Recipes**: Fill all process fields even if optional (helps with prediction)

---

## 📞 Getting Help

- **Setup issues**: Run wizard again (delete `config.json`)
- **Image quality**: Check feedback recommendations
- **Results questions**: Toggle to Advanced view for full data
- **Recipe problems**: Form validation shows what's missing

---

## 🎓 What's Next?

After you're comfortable with basics:

1. **Log multiple recipes**: Build database for predictions
2. **Run batch analysis**: Analyze multiple images at once
3. **Use predictions**: Predict porosity from recipe before baking
4. **Export data**: Create reports and share results
5. **Train classifier**: Teach ML model your good vs bad bread

---

**Ready?** Launch the tool:
```bash
python gui.py
```

**First time?** Setup wizard guides you through everything!

---

*Questions? Check the main README.md for advanced features.*
