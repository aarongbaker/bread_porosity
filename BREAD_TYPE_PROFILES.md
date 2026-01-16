# Bread Type Profiles - Quality Control Feature

## Overview

The Bread Porosity Analysis Tool now supports **multiple quality control profiles for different bread types**. Each bread type has its own customized quality standards, allowing you to maintain appropriate quality criteria for:

- **Sourdough** - Higher porosity, rustic crumb
- **Whole Wheat** - Lower porosity, denser crumb
- **Baguette** - High porosity, open crumb
- **Sandwich Bread** - Low porosity, fine crumb
- **Ciabatta** - Very high porosity, large irregular holes
- **Custom** - User-defined profile

---

## Default Bread Type Profiles

### 1. Sourdough
**Characteristics**: Traditional European-style with moderate porosity and balanced holes

| Parameter | Target | Warning |
|-----------|--------|---------|
| Porosity | 20-35% | 18-37% |
| Hole Count | 100-400 | - |
| Hole Diameter | 2.0-8.0 mm | - |
| Uniformity Min | 0.70 | - |
| Batch CV Max | 15% | - |

**Quality Grades**:
- **Excellent**: Porosity 25-32%, Uniformity 0.85+
- **Good**: Porosity 22-35%, Uniformity 0.75+
- **Fair**: Porosity 18-38%, Uniformity 0.65+

---

### 2. Whole Wheat
**Characteristics**: Denser crumb structure with smaller holes

| Parameter | Target | Warning |
|-----------|--------|---------|
| Porosity | 15-28% | 12-32% |
| Hole Count | 60-250 | - |
| Hole Diameter | 1.5-6.0 mm | - |
| Uniformity Min | 0.65 | - |
| Batch CV Max | 18% | - |

**Quality Grades**:
- **Excellent**: Porosity 20-26%, Uniformity 0.80+
- **Good**: Porosity 16-28%, Uniformity 0.70+
- **Fair**: Porosity 12-32%, Uniformity 0.60+

---

### 3. Ciabatta
**Characteristics**: Very open, irregular crumb with large holes

| Parameter | Target | Warning |
|-----------|--------|---------|
| Porosity | 30-45% | 28-48% |
| Hole Count | 200-600 | - |
| Hole Diameter | 3.0-12.0 mm | - |
| Uniformity Min | 0.60 | - |
| Batch CV Max | 20% | - |

**Quality Grades**:
- **Excellent**: Porosity 35-42%, Uniformity 0.80+
- **Good**: Porosity 30-45%, Uniformity 0.70+
- **Fair**: Porosity 28-48%, Uniformity 0.60+

---

### 4. Sandwich Bread
**Characteristics**: Fine, uniform crumb for slicing

| Parameter | Target | Warning |
|-----------|--------|---------|
| Porosity | 12-22% | 10-25% |
| Hole Count | 50-200 | - |
| Hole Diameter | 1.0-4.0 mm | - |
| Uniformity Min | 0.75 | - |
| Batch CV Max | 12% | - |

**Quality Grades**:
- **Excellent**: Porosity 15-20%, Uniformity 0.85+
- **Good**: Porosity 12-22%, Uniformity 0.75+
- **Fair**: Porosity 10-25%, Uniformity 0.65+

---

### 5. Baguette
**Characteristics**: Open crumb with elongated holes

| Parameter | Target | Warning |
|-----------|--------|---------|
| Porosity | 25-40% | 22-43% |
| Hole Count | 150-500 | - |
| Hole Diameter | 2.5-10.0 mm | - |
| Uniformity Min | 0.65 | - |
| Batch CV Max | 16% | - |

**Quality Grades**:
- **Excellent**: Porosity 30-37%, Uniformity 0.80+
- **Good**: Porosity 25-40%, Uniformity 0.70+
- **Fair**: Porosity 22-43%, Uniformity 0.60+

---

### 6. Custom
**Characteristics**: User-defined standards (defaults to sourdough)

Customize all parameters to match your specific requirements.

---

## Using Bread Type Profiles in the GUI

### Workflow: Switch Bread Types and Evaluate

1. **Go to Quality Control Tab**
   - Click on "Quality Control" tab in the GUI

2. **Select Bread Type**
   - Drop-down menu shows all available bread types
   - Select the type you're currently analyzing
   - Standards immediately update

3. **View Current Profile**
   - Click "View Profile" to see all standards
   - Shows all thresholds and quality grades

4. **Analyze and Evaluate**
   - Analyze your images normally
   - Click "Evaluate Current Analysis"
   - Results judged against selected bread type standards

5. **Edit Profile** (Optional)
   - Click "Edit Profile" to customize standards
   - Modify thresholds as needed
   - Changes saved automatically

### Example Session

```
1. Analyzing sourdough:
   - Select "Sourdough" from bread type dropdown
   - View Profile shows: Porosity 20-35%, etc.
   - Analyze images
   - Evaluate: Results compared to sourdough standards

2. Switch to ciabatta:
   - Select "Ciabatta" from dropdown
   - Standards update (now Porosity 30-45%)
   - View Profile shows updated thresholds
   - Evaluate: Results compared to ciabatta standards
```

---

## Configuring Custom Profiles

### Method 1: GUI Editor
1. Go to Quality Control → "Edit Profile"
2. Modify values in text editor
3. Save changes

### Method 2: Direct Configuration
Edit `qc_config.json` directly:

```json
{
  "current_bread_type": "sourdough",
  "bread_types": {
    "my_bread": {
      "display_name": "My Special Bread",
      "porosity_target_min": 22.0,
      "porosity_target_max": 38.0,
      "porosity_warning_min": 20.0,
      "porosity_warning_max": 40.0,
      ...
    }
  }
}
```

### Adding a New Bread Type

```python
from quality_control import QualityControlManager

qc = QualityControlManager()

# Define your profile
my_profile = {
    "display_name": "Italian Semolina",
    "porosity_target_min": 18.0,
    "porosity_target_max": 32.0,
    "porosity_warning_min": 16.0,
    "porosity_warning_max": 35.0,
    "hole_count_target_min": 80,
    "hole_count_target_max": 350,
    "hole_diameter_target_min": 1.8,
    "hole_diameter_target_max": 7.0,
    "uniformity_acceptable_min": 0.72,
    "consistency_cv_max": 0.14,
    "quality_grades": {
        "excellent": {"porosity": [24, 30], "uniformity": [0.85, 1.0]},
        "good": {"porosity": [20, 32], "uniformity": [0.75, 0.95]},
        "fair": {"porosity": [16, 35], "uniformity": [0.65, 0.85]},
        "poor": {"porosity": [0, 100], "uniformity": [0.0, 1.0]},
    }
}

# Add to QC manager
qc.add_bread_type("italian_semolina", my_profile)

# Now use it
qc.set_bread_type("italian_semolina")
evaluation = qc.evaluate_analysis(metrics)
```

---

## Quality Evaluation with Bread Types

### Understanding Evaluation Results

Each bread type evaluation includes:

1. **Acceptance Status**
   -  Porosity: Within/outside target range
   -  Holes: Within/outside count/size range
   -  Uniformity: Above/below minimum score

2. **Quality Grade**
   -  Excellent
   -  Good
   -  Fair
   -  Poor

3. **Bread-Type-Specific Alerts**
   - Examples for Ciabatta (high porosity bread):
     - "⚠ Porosity 28% below target 30-45%"
   - Examples for Sandwich Bread (low porosity bread):
     - " Porosity 35% way above target 12-22%"

4. **Targeted Recommendations**
   - Different advice for different bread types
   - "For Ciabatta: Increase fermentation for higher porosity"
   - "For Sandwich: Reduce hydration for denser crumb"

---

## Batch Consistency with Bread Types

### Checking Consistency

When checking batch consistency, the tool:
- Uses the **current bread type's CV limit** (default: 15-20%)
- Provides verdict: PASS or FAIL
- Shows statistics specific to bread type

### Example Batch Check

```
BATCH CONSISTENCY ANALYSIS
Samples Analyzed: 10
Status: PASS 
Message: Batch is consistent (CV: 12.3% < 15%)

POROSITY STATISTICS:
  Mean:          32.5%
  Std Dev:       4.0%
  CV (Target <15%): 12.3%  ← Bread type specific limit
  Range:         28.2% - 37.1%
```

---

## SPC (Statistical Process Control) with Bread Types

### Control Limits by Bread Type

Control limits automatically adjust based on selected bread type:

| Bread Type | Mean | UCL (±3σ) | LCL (±3σ) | Target |
|-----------|------|-----------|-----------|--------|
| Sourdough | 27% | 35% | 19% | 20-35% |
| Whole Wheat | 22% | 30% | 14% | 15-28% |
| Ciabatta | 37% | 45% | 29% | 30-45% |
| Sandwich | 17% | 25% | 9% | 12-22% |

---

## API Reference

### Setting Bread Type

```python
# Switch to a bread type
qc.set_bread_type("ciabatta")

# Returns True if successful
success = qc.set_bread_type("my_custom_type")
```

### Getting Bread Type Info

```python
# Get current profile
profile = qc.get_current_profile()

# Get all available bread types
bread_types = qc.get_all_bread_types()
# Returns: {"sourdough": "Sourdough", "ciabatta": "Ciabatta", ...}
```

### Evaluate with Bread Type

```python
# Use current bread type
evaluation = qc.evaluate_analysis(metrics)

# Explicitly specify bread type
evaluation = qc.evaluate_analysis(metrics, bread_type="baguette")
```

### Update Thresholds per Bread Type

```python
# Update sourdough thresholds
qc.update_threshold("porosity_target", min_val=22, max_val=36, 
                   bread_type="sourdough")

# Update current bread type
qc.update_threshold("hole_count_target", min_val=80, max_val=420)
```

---

## Configuration File Structure

### qc_config.json

```json
{
  "current_bread_type": "sourdough",
  "bread_types": {
    "sourdough": {
      "display_name": "Sourdough",
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
    },
    "whole_wheat": { ... },
    "ciabatta": { ... },
    ...
  }
}
```

---

## Best Practices

### 1. Set Correct Bread Type Before Analysis
```
 DO: Select "Ciabatta" → Analyze → Evaluate
 DON'T: Analyze as sourdough, then change to ciabatta
```

### 2. Customize Standards for Your Recipe
- Adjust profiles to match your specific formulas
- Save separate profiles for different recipes
- Keep detailed notes in profile names

### 3. Monitor Trends by Bread Type
- Track SPC statistics separately for each type
- Compare batch consistency within bread type
- Don't mix different bread types in batch analysis

### 4. Use Recommendations Wisely
- Recommendations are tailored to bread type
- Sourdough: "Increase fermentation for porosity"
- Sandwich: "Reduce fermentation for density"

---

## Troubleshooting

### "Bread type not found"
```
→ Check bread type name (case-sensitive)
→ Verify in qc_config.json
→ Use GUI dropdown to see available types
```

### "Standards not updating"
```
→ Ensure bread type selector is properly updated
→ Restart GUI or re-click "View Profile"
→ Check qc_config.json for syntax
```

### "Custom profile won't save"
```
→ Use GUI editor (simpler than JSON editing)
→ Check JSON syntax in config file
→ Ensure all required fields present
```

---

## Summary

**Bread Type Profiles** allow you to:
-  Set quality standards specific to each bread type
-  Automatically adjust evaluation criteria
-  Track different breads with appropriate thresholds
-  Create custom profiles for specialty breads
-  Maintain consistent quality within each type

**Default Profiles**: Sourdough, Whole Wheat, Ciabatta, Sandwich, Baguette, Custom

**Get Started**:
1. Open Quality Control tab
2. Select your bread type
3. Click "View Profile" to see standards
4. Analyze images - standards automatically applied

---

**Status:  Bread Type Profiles Feature Complete**
