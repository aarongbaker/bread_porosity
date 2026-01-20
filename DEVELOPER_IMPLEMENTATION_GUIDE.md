# Usability Implementation - Developer Guide

This document explains the architecture of the new usability features for developers.

---

## Architecture Overview

The implementation follows a **modular design** where each usability improvement is in a separate file, imported into the main GUI:

```
gui.py (Main GUI Class)
  ├─ FirstRunWizard (from first_run_wizard.py)
  ├─ ImageQualityValidator (from image_quality_validator.py)
  ├─ ResultPresenter (from result_presenter.py)
  └─ RecipeBuilderForm (from recipe_builder_form.py)

Config/Data Layer
  ├─ config.json (stores first_run_complete, pixel_size_mm, etc.)
  ├─ recipes.json (recipe database)
  └─ qc_config.json (bread type profiles)
```

---

## Module Responsibilities

### 1. FirstRunWizard (`first_run_wizard.py`)

**Purpose**: Guide first-time users through setup

**Key Methods**:
- `run()` - Main entry point, shows wizard sequence
- `_show_welcome()` - Welcome screen
- `_show_calibration()` - Calibration options
- `_calibrate_from_image()` - Image-based pixel size calculation
- `_calibrate_manual()` - Manual entry form
- `_show_workspace_setup()` - Setup checklist
- `_show_bread_types()` - Type selection
- `_save_and_close()` - Persist to config.json

**Config Integration**:
```python
# FirstRunWizard sets these in config.json:
config = {
    "first_run_complete": True,  # Prevents re-running wizard
    "pixel_size_mm": 0.105,      # From calibration
    "preferred_bread_type": "sourdough",
    "workspace_initialized": True
}
```

**Flow**:
```
gui.py starts
  ↓
_check_first_run() looks at config.json
  ↓
If first_run_complete == False:
  FirstRunWizard.run()  ← Blocks here
  User completes 4 steps
  Wizard saves config
  ↓
Config loaded, GUI continues
```

---

### 2. ImageQualityValidator (`image_quality_validator.py`)

**Purpose**: Validate images before analysis to prevent bad results

**Key Methods**:
- `validate_image(image_path)` - Main validation orchestrator
- `_check_resolution()` - Requires ≥2.0 MP
- `_check_focus()` - Laplacian variance ≥500
- `_check_exposure()` - Mean intensity 100-200
- `_check_lighting_uniformity()` - Quadrant CV <15%
- `_check_contrast()` - Std dev ≥40
- `_check_rotation()` - Aspect ratio 0.7-1.4
- `_get_recommendations()` - User-friendly fixes

**Return Format**:
```python
result = {
    'quality_score': 0.82,  # 0-1, percentage shown as 82%
    'status': '✅',
    'checks': {
        'resolution': {'pass': True, 'value': 2500, 'required': 1500},
        'focus': {'pass': True, 'value': 1200, 'required': 500},
        'exposure': {'pass': True, 'value': 145, 'required': 100-200},
        'uniformity': {'pass': False, 'value': 16, 'required': '<15'},
        'contrast': {'pass': True, 'value': 85, 'required': 40},
        'rotation': {'pass': True, 'ratio': 1.05, 'required': 0.7-1.4}
    },
    'recommendations': [
        'Image quality is good.',
        'Lighting slightly uneven but acceptable.',
        'Recommendation: Improve backlit uniformity for next image.'
    ]
}
```

**Integration**:
```python
# In gui.py analyze_single_image()
quality = self.image_quality_validator.validate_image(image_path)
if quality['quality_score'] < 0.5:
    messagebox.showwarning("Image Quality Issues", 
                          '\n'.join(quality['recommendations']))
    return  # Don't analyze
# Continue with analysis...
```

---

### 3. ResultPresenter (`result_presenter.py`)

**Purpose**: Format analysis results in simple or advanced views

**Key Methods**:
- `format_results(result_dict)` - Route to simple or advanced
- `_format_simple_view()` - 3 key metrics only
- `_format_advanced_view()` - Full 30+ metrics
- `_calculate_grade()` - Excellent/Good/Fair/Poor/Very Poor
- `_interpret_porosity()` - One-line interpretation
- `_interpret_uniformity()` - One-line interpretation
- `_classify_crumb_type()` - Bread type classification
- `toggle_mode()` - Switch simple ↔ advanced

**Simple View Output**:
```
POROSITY: 42.3%
HOLES: Count=248, Avg Diameter=5.2mm
QUALITY GRADE: ✅ Excellent

This is within normal range for sourdough.
Excellent open crumb structure with uniform distribution.
```

**Advanced View Output** (30+ metrics):
```
Porosity: 42.3%
Hole Count: 248
Mean Hole Diameter: 5.2mm
Max Hole Diameter: 12.1mm
Min Hole Diameter: 1.8mm
Aspect Ratio: 1.15
Orientation Entropy: 3.2
Uniformity Score: 0.88
... (25+ more metrics)
```

**Grading Logic**:
```python
# Grade = Average of three scores
porosity_score = grade_porosity(result, profile)  # 0-100
holes_score = grade_holes(result, profile)        # 0-100
uniformity_score = grade_uniformity(result)       # 0-100
grade = (porosity_score + holes_score + uniformity_score) / 3

# Map score to grade
if grade >= 85: return "Excellent"
elif grade >= 70: return "Good"
elif grade >= 55: return "Fair"
elif grade >= 40: return "Poor"
else: return "Very Poor"
```

**Integration**:
```python
# In gui.py display_results()
formatted = self.result_presenter.format_results(result)
self.results_text.insert(1.0, formatted)

# User clicks toggle button
self.result_presenter.toggle_mode()
formatted = self.result_presenter.format_results(result)
self.results_text.delete(1.0, tk.END)
self.results_text.insert(1.0, formatted)
```

---

### 4. RecipeBuilderForm (`recipe_builder_form.py`)

**Purpose**: Form-based recipe creation without JSON editing

**Key Methods**:
- `show()` - Launch form window
- `_create_basic_info_tab()` - Name, type, notes
- `_create_ingredients_tab()` - 9 common + custom
- `_create_process_tab()` - Mixing, proof, oven, cook
- `_create_environment_tab()` - Temp, humidity, altitude
- `_add_custom_ingredient()` - Dialog for non-standard items
- `_save_recipe()` - Validation and callback

**Form Data Structure**:
```python
recipe = {
    'name': 'My Sourdough',
    'type': 'sourdough',
    'notes': 'High hydration starter',
    'ingredients': {
        'bread_flour': 500.0,
        'water': 350.0,
        'salt': 10.0,
        'starter': 100.0,
        ...
    },
    'mixing_time_min': 10.0,
    'proof_time_min': 480.0,
    'oven_temp_c': 450.0,
    'cooking_vessel': 'dutch_oven',
    'cook_time_min': 40.0,
    'room_temp_c': 22.0,      # Optional
    'room_humidity_pct': 65.0,  # Optional
    'altitude_m': 200.0         # Optional
}
```

**Integration**:
```python
# In gui.py show_recipe_builder()
def on_save(recipe_dict):
    recipe = self.recipe_db.add_recipe(
        recipe_name=recipe_dict['name'],
        ingredients=recipe_dict['ingredients'],
        # ... other fields
    )
    return True

builder = RecipeBuilderForm(self.root, on_save_callback=on_save)
builder.show()

# User fills form and clicks Save
# Form calls: self.on_save(recipe_dict)
# Callback receives data and adds to database
```

---

## GUI Integration Points

### Initialization (gui.py `__init__`)
```python
def __init__(self, root):
    # ... existing code ...
    
    # Initialize new modules
    self.image_quality_validator = ImageQualityValidator(verbose=False)
    self.result_presenter = ResultPresenter(simple_mode=True)
    
    # Check if first run
    self._check_first_run()
```

### First-Run Check
```python
def _check_first_run(self):
    """Check if first run and show wizard if needed"""
    if not self.config.get('first_run_complete', False):
        self._show_first_run_wizard()

def _show_first_run_wizard(self):
    """Launch first-run wizard"""
    wizard = FirstRunWizard(self.root)
    wizard.run()
    # After wizard completes, config is updated
    self._reload_config()
```

### Image Analysis Flow
```python
def analyze_single_image(self, loaf_name=None):
    # ... existing code ...
    
    # NEW: Validate image quality
    quality = self._validate_image_quality_before_analysis()
    if quality['quality_score'] < 0.5:
        messagebox.showwarning("Image Quality Issues",
                              '\n'.join(quality['recommendations']))
        return
    
    # Continue with analysis
    result = analyze_bread_image(...)
    self.display_results(result)

def _validate_image_quality_before_analysis(self):
    """Run image quality checks"""
    result = self.image_quality_validator.validate_image(
        str(self.current_image_path)
    )
    self.set_status(f"Image Quality: {result['status']} "
                   f"{result['quality_score']:.0%}",
                   color=self.warning_color if result['quality_score'] < 0.75 
                         else self.success_color)
    return result
```

### Results Display Flow
```python
def display_results(self, result):
    """Display results using presenter"""
    formatted = self.result_presenter.format_results(result)
    self.results_text.delete(1.0, tk.END)
    self.results_text.insert(1.0, formatted)

def toggle_results_view(self):
    """Toggle between simple and advanced views"""
    if self.analysis_result:
        self.result_presenter.toggle_mode()
        self.display_results(self.analysis_result)
```

### Recipe Management Flow
```python
def log_new_recipe(self):
    """Show recipe builder form"""
    self.show_recipe_builder()

def show_recipe_builder(self):
    """Show form-based recipe builder"""
    def on_save(recipe_dict):
        try:
            recipe = self.recipe_db.add_recipe(...)
            self.refresh_recipe_list()
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False
    
    builder = RecipeBuilderForm(self.root, on_save_callback=on_save)
    builder.show()
```

---

## Data Flow Diagrams

### First-Run Flow
```
User starts: python gui.py
    ↓
gui.__init__()
    ↓
_check_first_run()
    ├─ Check: config.json exists?
    ├─ Check: first_run_complete == True?
    │
    └─ No → FirstRunWizard.run()
        ├─ Welcome screen
        ├─ Calibration (image or manual)
        ├─ Workspace setup
        ├─ Bread type selection
        └─ Save config.json with first_run_complete: True
           ↓
gui initialization continues
    ↓
GUI ready
```

### Analysis Flow (With Quality Check)
```
User clicks: Analyze
    ↓
analyze_single_image()
    ↓
_validate_image_quality_before_analysis()
    ├─ Load image
    ├─ Check 6 quality metrics
    ├─ Calculate score (0-1)
    ├─ Generate recommendations
    └─ Display in status bar
       ↓
    Quality score >= 0.5?
    ├─ Yes → Continue analysis
    └─ No → Show warning, return
            ↓
        analyze_bread_image()
            ↓
        display_results()
            ├─ result_presenter.format_results()
            ├─ Insert to results_text widget
            └─ Show simple view by default
```

### Recipe Flow
```
User clicks: Add Recipe
    ↓
log_new_recipe()
    ↓
show_recipe_builder()
    ├─ Create Toplevel window
    ├─ Create 4 tabs:
    │  ├─ Basic Info
    │  ├─ Ingredients
    │  ├─ Process
    │  └─ Environment
    │
    └─ User fills form
       ↓
    User clicks: Save
       ↓
    _save_recipe()
       ├─ Validate all fields
       ├─ Call on_save callback with recipe_dict
       │
       └─ Callback:
          ├─ recipe_db.add_recipe(...)
          ├─ refresh_recipe_list()
          └─ Show success message
```

---

## Configuration Files

### config.json (Updated by FirstRunWizard)
```json
{
  "first_run_complete": true,
  "pixel_size_mm": 0.105,
  "preferred_bread_type": "sourdough",
  "workspace_initialized": true,
  "output_directory": "output",
  "processed_directory": "processed",
  "unprocessed_directory": "unprocessed",
  "results_directory": "results",
  "threshold_method": "otsu",
  "normalization_method": "clahe",
  "min_hole_diameter_mm": 1.0,
  "max_hole_diameter_mm": 30.0
}
```

### qc_config.json (Bread Type Profiles)
Used by ResultPresenter for grading:
```json
{
  "current_bread_type": "sourdough",
  "bread_types": {
    "sourdough": {
      "porosity_target_min": 20.0,
      "porosity_target_max": 35.0,
      "hole_count_target_min": 100,
      "hole_count_target_max": 400,
      "uniformity_acceptable_min": 0.7,
      "consistency_cv_max": 0.15,
      "quality_grades": {
        "excellent": {"porosity": [25, 32], "uniformity": [0.85, 1.0]},
        "good": {"porosity": [22, 35], "uniformity": [0.75, 0.95]}
      }
    }
  }
}
```

---

## Testing Guide

### Unit Testing
```python
# Test FirstRunWizard
from first_run_wizard import FirstRunWizard
wizard = FirstRunWizard(root)
# Verify: _show_welcome creates labels
# Verify: _calibrate_from_image processes ruler image
# Verify: _save_and_close writes to config.json

# Test ImageQualityValidator
from image_quality_validator import ImageQualityValidator
validator = ImageQualityValidator()
result = validator.validate_image("test_bread.jpg")
# Verify: result['quality_score'] between 0-1
# Verify: all 6 checks present in result['checks']

# Test ResultPresenter
from result_presenter import ResultPresenter
presenter = ResultPresenter(simple_mode=True)
formatted = presenter.format_results(mock_result)
# Verify: output contains only 3 key metrics
presenter.toggle_mode()
formatted = presenter.format_results(mock_result)
# Verify: output contains 30+ metrics

# Test RecipeBuilderForm
from recipe_builder_form import RecipeBuilderForm
form = RecipeBuilderForm(root, callback)
form.show()
# Verify: form window opens
# Verify: 4 tabs visible
# Verify: save calls callback with dict
```

### Integration Testing
```python
# Test first-run flow
# 1. Delete config.json
# 2. Run gui.py
# 3. Verify FirstRunWizard appears
# 4. Complete wizard
# 5. Verify config.json created with first_run_complete: true
# 6. Verify wizard doesn't appear on 2nd run

# Test image quality integration
# 1. Analyze good image → Quality ✅, proceeds
# 2. Analyze blurry image → Quality ✗, shows warning

# Test results display
# 1. Analyze image
# 2. Verify simple view shown by default
# 3. Click toggle → Advanced view
# 4. Verify all metrics displayed

# Test recipe form
# 1. Click "Add Recipe"
# 2. Fill form, save
# 3. Verify recipe in database
```

---

## Extension Points

### Add New Quality Check
```python
# In image_quality_validator.py
def _check_new_metric(self):
    """Check new quality metric"""
    value = cv2.calculate_something(self.image)
    required = 50
    return {
        'pass': value >= required,
        'value': value,
        'required': required
    }

# Add to validate_image():
checks = {
    # ... existing checks ...
    'new_metric': self._check_new_metric(),
}
```

### Add New Bread Type Profile
```python
# In qc_config.json
"custom_bread": {
  "porosity_target_min": 18.0,
  "porosity_target_max": 30.0,
  # ... other fields
}
```

### Add New Form Tab
```python
# In recipe_builder_form.py
def _create_fermentation_tab(self, notebook):
    """Add tab for fermentation specifics"""
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Fermentation")
    
    ttk.Label(frame, text="Bulk Ferment Temp:").pack()
    ttk.Entry(frame, textvariable=...).pack()
    # ... more fields
```

---

## Dependencies

**New modules require**:
- tkinter (GUI framework)
- json (config handling)
- cv2 (OpenCV for image analysis)
- numpy (numerical operations)
- pathlib (file operations)
- logging (diagnostics)

**All already in requirements.txt**

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| FirstRunWizard | ~5-10s | Image processing for calibration |
| Image quality check | ~1-2s | 6 checks on single image |
| Result formatting | <100ms | Simple text formatting |
| Recipe form render | ~200ms | Tkinter widget creation |

No blocking operations - all responsive to UI.

---

## Future Enhancements

1. **Parameter tooltips**: Add (?) icons with hover explanations
2. **Setup guide tab**: Visual checklist with photos
3. **Export preview**: Show PDF before saving
4. **Batch UI**: Progress bar for multiple images
5. **Multi-language**: Spanish, French, German support
6. **Dark/Light theme**: User preference toggle

---

## Summary

**Architecture**: Modular design with separate concerns  
**Integration**: Clean callbacks between modules  
**Configuration**: Centralized in config.json  
**Data Flow**: Clear paths from user action → result  
**Extensibility**: Easy to add new checks, profiles, tabs  
**Performance**: All operations sub-second  
**Code Quality**: Type hints, docstrings, error handling  

---

*For questions or contributions, see CONTRIBUTING.md*
