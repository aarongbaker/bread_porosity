# Usability Improvement Roadmap

## Executive Summary
After analyzing the codebase, here are features that need improvement or completion to make the tool truly "download & run" simple for non-technical users.

---

## 🔴 **CRITICAL - Block New Users**

### 1. **First-Run Setup Wizard is Missing**
**Problem**: Users open GUI with no guidance on calibrating pixel_size_mm or setting up imaging
- GUI initializes with hardcoded `pixel_size_mm=0.1` (default)
- No validation that this matches user's actual camera setup
- New users don't know what this parameter means or how to measure it
- Results are wrong but users don't realize it

**Impact**: High - produces invalid measurements

**Solution**:
- Create interactive first-run wizard (appears on first launch)
- Guide: camera distance → reference object → capture → automatic calibration
- Store result in `config.json` as default
- Add "Recalibrate" button for future adjustments
- Show pixel_size_mm prominently in GUI with validation badge ✓/✗

**Files to modify**: `gui.py` (add `FirstRunWizard` class), `calibration.py` (add auto-calibration helper)

---

### 2. **Image Input Requirements Completely Undocumented in GUI**
**Problem**: Users don't know:
- Where to place images (folder structure)
- What image requirements are (size, format, lighting)
- How to set up backlit imaging
- Why their results are bad

**Impact**: High - 80% of failures are due to poor image quality, not algorithm

**Solution**:
- Add "Setup Guide" tab with:
  - Checklist for backlit setup
  - Sample lighting uniformity test
  - Image quality validator (Laplacian variance, exposure, etc.)
  - Camera setup instructions with photos/videos
- Create visual feedback: ✓ Good image, ⚠ Suboptimal, ✗ Cannot analyze
- Auto-run image quality check before analysis
- Store sample images in `examples/` with expected results

**Files to modify**: `gui.py` (add Setup tab), `calibration.py` (add `ImageQualityValidator`), create `examples/` folder

---

### 3. **Folder Structure is Confusing**
**Problem**: 
- `unprocessed/`, `processed/`, `output/`, `results/` folders - confusing what each does
- No clear "Import images here" guidance
- Files disappear after analysis (moved to processed/)

**Impact**: Medium - users lose their original images

**Solution**:
- Single clear "My Images" folder (read-only source)
- Auto-create and explain folder structure on first run
- Add README files in each folder explaining purpose
- Add "Open Folder" buttons in GUI showing exactly where to place images
- Option to NOT move original images after analysis

**Files to modify**: `gui.py`, add `create_initial_directories()` with inline help

---

## 🟠 **HIGH - Major Gaps**

### 4. **Pixel Calibration Process is Undocumented**
**Problem**: Users have no way to determine correct `pixel_size_mm` for their camera
- No clear method documented
- No calibration tool in GUI
- Impacts all measurements directly

**Solution**:
- Add "Calibration" tab with step-by-step wizard:
  1. Photograph known-size object (ruler, business card)
  2. Select object in image (click corners)
  3. Enter known size in mm
  4. Auto-compute pixel_size_mm
  5. Save to config
- Create calibration validation: analyze test image with known ground truth
- Store calibration history with date

**Files to create**: `calibration_wizard.py`, update `gui.py`

---

### 5. **Default Parameters Need Sensible Presets**
**Problem**: Dropdowns show `clahe`, `otsu`, `adaptive` with no explanation
- Users don't know what these do
- No way to know which to choose
- One wrong choice ruins all results

**Solution**:
- Rename to plain English: "Smart Lighting Fix", "Standard Thresholding", "Adaptive Thresholding"
- Add tooltip icons that explain each (hover or ?)
- Show preview of processing stages in real-time as you change settings
- Add "Auto (Recommended)" option that picks best based on image quality
- Save "Last Used" settings

**Files to modify**: `gui.py` (add tooltips, preview mode)

---

### 6. **Analysis Results are Overwhelming for Beginners**
**Problem**: 30+ metrics displayed, users don't know what matters
- JSON output with field names like `hole_area_cv`, `crumb_brightness_skewness`
- No interpretation guidance
- No clear "PASS" or "FAIL" without Quality Control setup

**Solution**:
- Create "Simple View" and "Advanced View" toggle
- Simple shows: Porosity %, Hole Count, Grade (Excellent/Good/Fair/Poor)
- Advanced shows everything
- Add interpretation guide: "High porosity = open crumb structure" etc.
- Highlight key numbers (large font, color-coded status)

**Files to modify**: `gui.py` (results display), create `result_interpreter.py`

---

### 7. **Quality Control Profiles Require Prior Knowledge**
**Problem**: 
- Users must understand their bread type to select profile
- No clear explanation of what each profile means
- No guidance on when to use which

**Solution**:
- Add profile selection dialog with photos of each bread type
- Show expected porosity ranges with real examples
- Allow users to upload their own image and match to type
- Create "Auto-Detect Profile" based on measured characteristics
- Add "Custom Profile" wizard for non-standard breads

**Files to modify**: `gui.py` (QC tab redesign), `quality_control.py`

---

## 🟡 **MEDIUM - Usability Polish**

### 8. **Recipe Management Has Steep Learning Curve**
**Problem**: JSON format shown to users; no validation feedback
- Users can't tell if recipe is valid until they click save
- Error messages are technical (JSON decode errors)
- No help text explaining recipe fields

**Solution**:
- Add "Recipe Builder" form (no JSON editing for beginners)
- Fields with units clearly labeled and validated
- Show examples: "Typical sourdough: 500g flour, 350g water"
- Real-time validation with helpful error messages
- Import from common recipe websites (future)

**Files to modify**: `gui.py` (recipes tab redesign), create `recipe_builder.py`

---

### 9. **ML Training is Confusing**
**Problem**: Users don't understand:
- What "good" vs "problem" means
- How many samples needed
- How accurate the model will be
- When it's ready to use

**Solution**:
- Add guidance: "Select 5-10 images of GOOD bread, 5-10 of PROBLEM"
- Show training progress: "3 good, 2 problem - need at least 5 of each"
- Display model confidence before predictions
- Show confusion matrix or accuracy metrics
- Save model with date, performance stats

**Files to modify**: `gui.py` (ML tab redesign), `ml_simple.py`

---

### 10. **Export is Hidden and Unclear**
**Problem**: Users don't know what they can export or why
- Tabs for CSV/Excel/PDF but no explanation
- No preview of output format
- No indication of where files go

**Solution**:
- Simplify to single "Export" button
- Show preview of what will be exported (first few rows)
- Option to select format, open folder automatically after export
- Show file size, number of samples
- Add "Email Report" option (future)

**Files to modify**: `gui.py` (export tab simplification), `export_reporting.py`

---

## 🟢 **LOW - Nice-to-Have Enhancements**

### 11. **Multi-Language Support**
- Create i18n framework for UI strings
- Start with Spanish, French (bread is international!)

### 12. **Dark/Light Theme Toggle**
- Users might prefer light theme (currently dark-only)

### 13. **Batch Processing Progress UI**
- Currently shows percentage bar but could be more informative
- Show: "Analyzing: image_3.jpg (3/10)"

### 14. **Undo/Redo for Parameters**
- Quick A/B comparison of different settings

### 15. **Recipe Scaling Calculator**
- Currently requires manual ingredient scaling
- Visual ingredient comparison when scaling

---

## 🛠️ **Implementation Priority**

### **Phase 1 (Critical - Block Users)**
```
Week 1-2:
  1. First-run setup wizard with pixel calibration
  2. Image input folder guidance (single import folder)
  3. Image quality validator before analysis
  
Result: Users can correctly calibrate and input images
```

### **Phase 2 (High - Major Gaps)**
```
Week 3-4:
  4. English-friendly parameter names + tooltips + preview
  5. Simple vs Advanced results view
  6. Recipe builder form (no JSON)
  
Result: Users understand what they're doing and see sensible output
```

### **Phase 3 (Medium - Polish)**
```
Week 5-6:
  7. Bread type profile selection with photos
  8. ML training guidance (progress, validation)
  9. Export simplification + preview
  
Result: All features are accessible and well-guided
```

### **Phase 4 (Nice-to-Have)**
```
Ongoing:
  - Dark/light theme
  - Batch progress UI
  - Multi-language
```

---

## 📋 **Specific Implementation Details**

### First-Run Wizard (Priority 1)
```python
class FirstRunWizard:
    """Interactive first-run setup"""
    
    def __init__(self, root, config_path):
        # Sequence:
        # 1. Welcome screen with overview
        # 2. Calibration step: guide user through pixel_size measurement
        # 3. Setup verification: analyze test image, validate quality
        # 4. Configuration: ask about bread types they bake
        # 5. Complete: set default config
```

### Image Quality Validator
```python
class ImageQualityValidator:
    """Check if image meets requirements"""
    
    def validate(self, image_path):
        checks = {
            "resolution": image >= 2MP,
            "focus": laplacian_variance > 500,
            "exposure": hist_well_distributed,
            "lighting_uniformity": std < 15%,
            "contrast": dynamic_range > 50%
        }
        return {check: status for check, status in checks.items()}
    
    def provide_feedback(self):
        # Show visual: ✓ OK, ⚠ Suboptimal, ✗ Fail
        # Suggest fix: "Increase backlight intensity"
```

### Simple Results View
```python
# CURRENT (Advanced):
Porosity: 42.34%
Hole Count: 127
Mean Diameter: 3.45mm
Aspect Ratio CV: 0.412
Crumb Brightness Mean: 128.3
...

# PROPOSED (Simple):
═════════════════════════════
BREAD QUALITY: EXCELLENT ✓
═════════════════════════════

Porosity:     42% (Open crumb)
Hole Count:   127 (Well-distributed)
Overall Grade: Excellent

👉 Next: Analyze another slice or export results
```

---

## 📊 **Success Metrics**

After implementing these improvements, measure:

1. **Time to first analysis**: <5 min (currently ???)
2. **Successful first analysis**: >80% (currently unknown)
3. **Correct calibration**: >95% follow wizard
4. **User satisfaction**: NPS > 50
5. **Support requests drop**: Track GitHub issues

---

## 💡 **Design Principles**

1. **Progressive Disclosure**: Simple by default, advanced on demand
2. **Affordances**: UI tells user what to do next
3. **Validation**: Prevent errors before they happen
4. **Feedback**: Show status and results clearly
5. **Documentation**: Inline help, not separate manuals
6. **Recovery**: Easy to recalibrate or redo

---

## 📝 **Quick Checklist for Developers**

- [ ] Create FirstRunWizard that appears on first launch
- [ ] Add image quality validator with visual feedback
- [ ] Reorganize folder structure: single "My Images" input folder
- [ ] Rename parameters to plain English with tooltips
- [ ] Create simple vs advanced results view
- [ ] Add recipe builder form (no JSON editing)
- [ ] Add profile selector with bread photos
- [ ] Simplify export UI with preview
- [ ] Add calibration wizard with validation
- [ ] Test with non-technical user (family member?)

---

## 🎯 **Outcome**

**Before**: User downloads, opens GUI, confused by 9 tabs, 20+ parameters, gets bad results, gives up

**After**: User downloads, runs setup wizard (5 min), captures test image, gets "PASS ✓", analyzes bread, sees clear grade, exports report → SUCCESS

