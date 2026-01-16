# Complete Feature Guide

## Quick Navigation
- [Core Analysis](#core-analysis)
- [Recipe Management](#recipe-management)
- [Statistics & Optimization](#statistics--optimization)
- [Quality Control](#quality-control)
- [Workflows](#workflows)

---

## Core Analysis

### Image Processing Pipeline
**Input:** Bread slice images (JPEG, PNG)  
**Output:** Porosity metrics, hole analysis, visualizations

**6-Step Processing:**
1. Grayscale conversion
2. Illumination normalization (CLAHE + morphology)
3. ROI detection (bread boundaries)
4. Threshold (Otsu or adaptive)
5. Morphological cleaning
6. Connected component analysis

### Measurements

| Metric | What It Measures | Typical Range |
|--------|-----------------|---------------|
| **Porosity %** | Hole area as % of crumb | 15-40% |
| **Hole Count** | Number of holes detected | 50-500 |
| **Mean Diameter** | Average hole size (mm) | 2-8mm |
| **Aspect Ratio** | Hole elongation (1.0=circle) | 1.0-3.0 |
| **CV (Holes)** | Hole size uniformity | 0.3-0.8 |
| **Orientation** | Hole directionality (entropy) | 0.0-1.0 |
| **Crumb Brightness** | Uniformity of color | 0-100% |

### Analysis Modes

**Single Image Mode:**
- Load image → Configure parameters → Analyze → View results

**Loaf Mode (Multi-Slice):**
- Name the loaf → Place slices in folder → Analyze all → Compare uniformity

---

## Recipe Management

### Core Functions

#### Log Recipe
- Save ingredients with quantities
- Input baking parameters (time, temp, vessel)
- Add optional environmental data (temp, humidity, altitude)
- Include custom notes
- Persistent JSON storage

#### Save Porosity
- Link measured porosity to recipe
- Auto-timestamp measurement
- Track measurement history

#### Predict Porosity
- Estimate porosity from recipe parameters
- Based on correlation with training data
- Shows confidence level and feature contributions

### Recipe Cloning
**Button:** "Clone Recipe"

Create exact independent copy:
- New unique ID
- All data copied (ingredients, parameters)
- Measured porosity cleared (ready for testing)
- No parent tracking
- Perfect for safe experimentation

**Use when:**
- Testing without affecting original
- Creating backup before changes
- Running parallel experiments

### Recipe Scaling
**Button:** "Scale Recipe"

Adjust batch size by scaling ingredients:
- Enter scale factor (0.5, 2.0, custom)
- All ingredients multiplied by factor
- Cooking times/temps preserved (usually don't scale)
- Shows ingredient comparison table
- Creates new recipe with scaled amounts

**Common scales:**
- 0.25× → Quarter batch (test)
- 0.5× → Half batch (save ingredients)
- 1.0× → Full (no change)
- 2.0× → Double (production)

### Recipe Variants
**Button:** "Create Variant"

Track intentional modifications with genealogy:
- Version-based tracking (v1, v2, v3...)
- Parent-child relationships
- Compare versions
- Document recipe evolution

**Use when:**
- Testing "what if" modifications
- Tracking progressive improvements
- Comparing different approaches

### Recipe Family Tree
**Button:** "Family Tree"

View recipe relationships:
- Parent recipe (if variant)
- All child variants
- Porosity comparison
- Complete genealogy

### Compare Recipes
**Button:** "Compare Recipes"

Side-by-side recipe analysis:
- All recipes in table format
- Porosity for each
- Statistical summary (avg/best/worst)
- Identify top performers

---

## Statistics & Optimization

### Statistics Dashboard
**Tab:** "Statistics Dashboard"

Model quality metrics for predictions:

#### R² (Coefficient of Determination)
- **Meaning:** How well model fits actual data
- **Range:** 0 (random) to 1 (perfect)
- **Interpretation:**
  - >0.7 = Good predictions
  - 0.5-0.7 = Fair, use cautiously
  - <0.5 = Poor, need more data

#### Confidence Intervals (95%)
- Statistical bounds for predictions
- Per-feature confidence ranges
- T-distribution based

#### Residual Analysis
- Prediction errors
- Mean error, standard deviation
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)

#### Feature Importance
- Which recipe factors most affect porosity
- Ranked by correlation + significance
- Helps focus optimization efforts

#### Correlations with P-values
- Pearson correlation with porosity
- Statistical significance (p-values)
- Identifies reliable factors

### What-If Analysis
**Feature:** "What-If Analysis"

Simulate changes and predict impacts:

**6 Default Scenarios:**
- Mixing time ±2 min
- Proof time ±10 min
- Oven temp ±10°C

**Shows:**
- Predicted porosity for each scenario
- Change from current recipe (Δ)
- Impact direction and magnitude

**Use for:**
- Testing before baking
- Quick feasibility checks
- Optimization without excessive testing

---

## Quality Control

### Loaf Consistency Tracking
**Tab:** "Loaf Consistency"

Analyze uniformity across multi-slice loaves:

#### Uniformity Metrics
- **CV (Coefficient of Variation)** = Std Dev / Mean × 100%
- **Industry benchmark:** CV < 15% excellent

#### Quality Grades
| Grade | CV Range | Assessment |
|-------|----------|------------|
| **Excellent** | <10% | Highly uniform |
| **Good** | 10-20% | Acceptable |
| **Fair** | 20-30% | Needs improvement |
| **Poor** | >30% | Significant issues |

#### Analysis
- Per-slice porosity
- Comparison to mean
- Problem slice identification
- Automatic recommendations

#### Recommendations
- Temperature/humidity adjustments
- Fermentation optimization
- Oven uniformity checks
- Specific improvement suggestions

**Auto-triggers after loaf analysis**

### Environmental Logging

Track conditions during fermentation:
- Room temperature (°C)
- Room humidity (%)
- Altitude (meters)

**Benefits:**
- Correlate environment with results
- Identify optimal conditions
- Account for seasonal variations
- Track external factors

---

## Workflows

### Optimization Workflow
```
1. Log recipe + environmental data
2. Analyze bread → save porosity
3. Dashboard → verify model quality
4. What-If → test scenarios
5. Create variant → with predictions
6. Test variant → save new porosity
7. Family Tree → compare results
8. Repeat until optimized
```

### Batch Scaling Workflow
```
1. Clone proven recipe (backup)
2. Scale ×2.0 (double)
3. Loaf Analysis → test new size
4. Loaf Consistency → check uniformity
5. If good: use for production
6. If not: adjust and retry
```

### Quality Control Workflow
```
1. Bake loaf
2. Loaf Analysis → multi-slice
3. Loaf Consistency → uniformity score
4. If CV > 20%:
   - Identify issue from recommendations
   - Adjust recipe/process
   - Rebake and compare
```

### Finding Optimal Batch Size
```
1. Clone base recipe
2. Create 3 scaled versions (0.5×, 1.0×, 2.0×)
3. Bake all three
4. Loaf Analysis on each
5. Compare consistency scores
6. Use Compare → side-by-side
7. Select best batch size
```

---

## Data Reference

### Tab Overview

| Tab | Purpose | Use When |
|-----|---------|----------|
| Preview | Image display | Check image quality |
| Results | Analysis output | View porosity metrics |
| Metrics | Raw JSON | Export/technical review |
| Recipes & Prediction | Recipe tools | Log/manage recipes |
| Statistics Dashboard | Model quality | Check prediction reliability |
| Loaf Consistency | Uniformity | Assess quality control |
| Comparison Tools | Optimization | Compare/simulate |

### Recipe Data Structure
```json
{
  "id": 1,
  "name": "Sourdough",
  "created_at": "2024-01-15T10:30:00",
  "ingredients": {"flour": 500, "water": 350},
  "mixing_time_min": 10,
  "proof_time_min": 480,
  "oven_temp_c": 450,
  "cooking_vessel": "dutch oven",
  "cook_time_min": 40,
  "measured_porosity": 25.5,
  "room_temp_c": 22.5,
  "room_humidity_pct": 65,
  "altitude_m": 100,
  "parent_recipe_id": null,
  "version": 1,
  "notes": "High hydration"
}
```

### Analysis Output
Per image:
- `comparison.png` - Processing pipeline (6 steps)
- `hole_distribution.png` - Histograms & stats
- `annotated.png` - Marked-up image
- `metrics.json` - Complete data export

---

## Key Metrics Explained

| Metric | Definition | Target | Notes |
|--------|-----------|--------|-------|
| Porosity | % of crumb that is air | 20-30% | Higher = more open |
| Hole Count | Number of holes | 100-300 | Affects texture feel |
| Mean Diameter | Average hole size (mm) | 4-6mm | Larger = more open |
| CV (Holes) | Hole size uniformity | <0.5 | Lower = more uniform |
| Aspect Ratio | Hole width/height | 1.0-2.0 | 1.0 = perfect circle |
| Anisotropy | Hole directionality | 0.0-1.0 | Higher = more aligned |
| Crumb CV | Brightness uniformity | <20% | Lower = more uniform |

---

## Common Parameters

### Baking Parameters
- **Mixing Time:** 5-15 minutes (dough development)
- **Proof Time:** 300-600 minutes (fermentation)
- **Oven Temp:** 400-500°C (crust development)
- **Cook Time:** 30-50 minutes (browning)

### Vessels & Impact
- Dutch oven: Closed, traps steam, more open crumb
- Loaf pan: Enclosed, confined, tighter crumb
- Baking stone: Open, less steam, varied structure

### Environmental Factors
- **Temperature:** Affects fermentation rate
- **Humidity:** Affects crust formation & crumb structure
- **Altitude:** Affects yeast activity & water content

---

## Tips & Best Practices

**Recipes:**
- ✅ Include all parameters when logging
- ✅ Add environmental data if available
- ✅ Use clear, descriptive names
- ✅ Document notes with reasoning
- ✅ Update with measured porosity

**Analysis:**
- ✅ Consistent lighting & camera angle
- ✅ Accurate pixel size calibration
- ✅ Test multiple slices per loaf
- ✅ Document analysis conditions
- ✅ Keep analysis logs

**Optimization:**
- ✅ Start with proven base recipe
- ✅ Change one parameter at a time
- ✅ Test at different scales
- ✅ Track environmental factors
- ✅ Document all iterations

**Quality Control:**
- ✅ Target CV < 15% for production
- ✅ Monitor consistency regularly
- ✅ Adjust when CV > 20%
- ✅ Document all changes
- ✅ Track seasonal variations

---

## Troubleshooting

**No statistics data displayed?**
→ Log 2-3 recipes with measured porosity first

**Low R² score?**
→ Need more training recipes (5-10+)

**High loaf CV?**
→ Check oven temperature, fermentation consistency, baking position

**Scaled predictions inaccurate?**
→ Cooking times may need adjustment; test empirically

**Can't find cloned recipe?**
→ New recipes added to end of list; scroll down

**What-If results don't match?**
→ Predictions are estimates; more data improves accuracy

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Single image analysis | 2-5 sec | Depends on image size |
| Loaf analysis (10 slices) | 20-50 sec | Parallel processing where possible |
| Statistics calc | <500ms | On-demand (not cached) |
| What-If analysis | <1 sec | 6 scenarios |
| Recipe comparison | <100ms | Table display |

**Memory:** Typical session 5-10MB | Handles 1000+ recipes

---

## Next Steps

1. **Setup** → Run calibration, verify settings
2. **Test** → Analyze sample images
3. **Build Data** → Log 5-10 recipes with porosity
4. **Analyze** → Check Statistics Dashboard
5. **Optimize** → Use What-If & Variants
6. **Scale** → Create scaled recipes, test uniformity
7. **Monitor** → Track quality with Loaf Consistency

---

See also: INSTALLATION.md | QUICK_START.md | README.md

