# AI & Defect Detection Features

This document describes the new machine learning and defect detection capabilities added to the Bread Porosity Analysis Tool.

## Overview

Two new tabs have been added for Quality Assurance:
1. **Defects Tab** - Automated defect detection
2. **ML Training Tab** - Simple machine learning classifier

---

## Defect Detection

### What It Detects

**Uneven Rise**
- Compares center brightness vs. edge brightness
- Indicates uneven fermentation or proofing
- High variation = poor quality score
- Causes: Temperature gradient, inconsistent dough, uneven shaping

**Dense Spots**
- Finds low-porosity clusters in crumb
- Indicates hard/compressed areas
- Common in over-fermented or degassed dough
- Shows location and severity of clusters

### How to Use

1. **Analyze Single Image**
   - Go to "Defects" tab
   - Select image in Image Library
   - Click "Analyze Current Image"
   - View severity score (0-100) and recommendations

2. **Batch Analysis**
   - Click "Batch Analysis"
   - Analyzes all images in `unprocessed/` folder
   - Shows pass rate, average severity, problem count
   - Identifies which images need attention

### Severity Grading

- **EXCELLENT** (0-20) - No defects detected
- **GOOD** (20-40) - Minor defects, acceptable
- **FAIR** (40-60) - Moderate defects, needs attention
- **POOR** (60-100) - Significant defects, investigate

### Output

Results include:
- Overall severity score
- Uneven rise analysis (center vs. edge brightness)
- Dense spot analysis (percentage affected, cluster count)
- Actionable recommendations
- Annotated image (for visual inspection)

### Example Workflow

```
1. Bake test batch
2. Analyze with porosity tool
3. Go to Defects tab
4. Click "Batch Analysis"
5. Review results:
   - If pass rate > 80%: Process is good
   - If 50-80%: Investigate fermentation
   - If < 50%: Major issues, redesign recipe
6. Use recommendations to adjust next batch
```

---

## Machine Learning Classifier

### What It Does

Builds a simple ML model that learns to classify bread as "Good" or "Problem" based on image features. 

No external dataset needed - your own images become the training data.

### Features Extracted (Automatic)

The ML classifier automatically extracts 11 features from each image:
1. Mean brightness
2. Brightness uniformity (std dev)
3. Brightness distribution shape
4. Edge density (crumb structure complexity)
5. Dark pixel ratio
6. Mid-tone pixel ratio
7. Bright pixel ratio
8. Porosity estimate
9. Local texture variance
10. Contrast
11. Center brightness (rise indicator)

### How to Use

#### Phase 1: Build Training Data

1. Go to **ML Training** tab
2. Select an image you consider "Good" quality
   - Click "Add Good Image"
   - Image added to training set
3. Select an image you consider "Problem"
   - Click "Add Problem Image"
   - Image added to training set
4. **Repeat until you have:**
   - At least 5-10 "good" images
   - At least 5-10 "problem" images
   - More data = better accuracy

Training Status shows:
- Good: 8
- Problem: 6
- Total: 14

#### Phase 2: Train Model

1. Once you have enough training images:
   - Click "Train Model"
   - Wait for completion message
   - Status changes to "Model: TRAINED"

The model learns the patterns of "good" vs. "problem" bread.

#### Phase 3: Make Predictions

1. Select any new bread image
2. Click "Predict Current"
3. Result shows:
   - **Prediction**: GOOD or PROBLEM
   - **Confidence**: 0-100% (higher = more certain)
   - Breakdown of match scores

### Example Workflow

```
SETUP PHASE (First Time)
========================
1. Analyze 10 images you know are good quality
   - Add each to training set as "good"
2. Analyze 10 images with known quality issues
   - Add each as "problem"
3. Train model (1-2 seconds)
4. Status shows "Model: TRAINED"

DAILY USE
=========
1. Bake new loaves
2. Take photos
3. In GUI:
   - Load image
   - Go to ML Training tab
   - Click "Predict Current"
4. Get instant quality prediction
5. 85%+ confidence = trust the prediction
```

### Interpreting Results

**Confidence Levels**
- **90-100%**: Very confident - trust this prediction
- **70-90%**: Confident - likely correct
- **60-70%**: Moderate - use with other QC methods
- **50-60%**: Low - probably random guess

**Accuracy Improvement**
- Accuracy improves as you add more training images
- Aim for 20+ training images per category for good results
- Model works best when training images are similar to new images

### Where Data Stored

- Training images metadata: `ml_models/training_data.json`
- Trained model: `ml_models/model_stats.json`
- Both auto-saved when you add images or train

### Building Better Models

**Good Training Data Characteristics:**
- Representative of your actual production
- Diverse lighting conditions (if applicable)
- Different camera angles if using multiple cameras
- Both good and problem examples well-balanced

**Improving Accuracy:**
1. Start with obvious good/problem images
2. Make predictions on new images
3. If wrong, add to training set opposite label
4. Re-train model (retrain with corrected images)
5. Repeat - model improves with feedback

### Advanced: Exporting Data

Training data can be:
- Shared with other users (copy `ml_models/` folder)
- Used in external ML tools (JSON format)
- Integrated into production systems
- Backed up for record-keeping

---

## Combining Defect Detection + ML

### Workflow

```
QC WORKFLOW WITH BOTH TOOLS
============================

1. AUTOMATIC DEFECT CHECK
   - Go to Defects tab
   - Click "Batch Analysis"
   - Get severity scores and recommendations
   - Identifies WHAT went wrong

2. ML CLASSIFICATION
   - Go to ML Training tab
   - Click "Predict Current"
   - Get good/problem prediction
   - Identifies WHICH IMAGES ARE GOOD

3. ANALYSIS
   - If predicted PROBLEM:
     - Check Defects tab
     - See severity breakdown (uneven rise vs. dense spots)
     - Apply recommendations to next batch
   
   - If predicted GOOD but defects show issues:
     - Your definition of "good" may differ
     - Retrain model with more examples
     - Or trust defect detection over ML

4. ITERATE
   - Apply recommendations
   - Bake next batch
   - Analyze again
   - Model improves over time
```

### When to Use Which

**Use Defect Detection When:**
- You want objective, rule-based analysis
- Consistent metrics across all batches
- You need specific issue identification
- Building documentation/reports

**Use ML Classifier When:**
- You want fast go/no-go decisions
- You have labeled training data
- You want pattern recognition
- Making production decisions quickly

**Use Both When:**
- Validating each other
- Investigating failures
- Training new QC staff
- Building process documentation

---

## Example Use Cases

### Case 1: Quality Assurance

```
Morning: Run batch analysis
1. Use Defects tab → Batch Analysis
2. Get pass rate and severity scores
3. Any failures? Click ML Prediction on suspicious images
4. Results inform whether to release batch
```

### Case 2: Recipe Development

```
Testing new fermentation time:
1. Bake with different fermentation hours
2. Label images: 8hr=good, 10hr=problem, 12hr=problem
3. Train ML model on these examples
4. Future test batches → predict automatically
5. Find optimal fermentation time
```

### Case 3: Process Improvement

```
Investigating uneven rise issues:
1. Batch Analysis → "Uneven Rise detected"
2. Check recommendation: "fermentation temperature uniformity"
3. Adjust oven/proof box temperature
4. Next batch → use ML to predict improvement
```

---

## Technical Details

### Defect Detection Algorithm

**Uneven Rise:**
- Divide image into center + 4 edge regions
- Calculate average brightness in each
- Deviation from center = severity score
- Threshold: 30+ = detected

**Dense Spots:**
- Apply Gaussian blur for smoothing
- Calculate local variance map
- Find pixels below variance threshold
- Count clusters using connected components
- Threshold: 5% dense pixels = detected

### ML Classification Algorithm

**Type:** Euclidean Distance Classifier
**Method:** Simple machine learning that learns the average "fingerprint" of good vs. problem images

**How It Works:**
1. Extract 11 features from each training image
2. Calculate average feature vector for "good" class
3. Calculate average feature vector for "problem" class
4. For new image: find which class is closer
5. Distance difference = confidence level

**Why Euclidean Distance:**
- Fast (< 100ms per prediction)
- Simple (no complex dependencies)
- Interpretable (easy to debug)
- Works well with small datasets (5-20 images)
- No internet required

---

## Troubleshooting

**"Model not trained" error:**
- Need at least 1 good + 1 problem image in training data
- Status shows: Good: 0, Problem: 0
- Solution: Add training images

**Low prediction confidence (<60%):**
- Not enough training data
- Training images too different from new image
- Add more diverse training examples
- Retrain model

**Predictions seem wrong:**
- Model learning from mislabeled images
- Solution: Review training data, remove mislabeled images
- Re-add with correct label
- Retrain

**Defect detection not detecting problems:**
- Severity thresholds may be conservative
- Check actual severity score (even if "EXCELLENT")
- Use ML prediction as secondary check
- Consider adjusting thresholds in `defect_detection.py`

---

## Future Enhancements

Possible additions (not yet implemented):
- Automated image labeling suggestions
- Model performance metrics (accuracy, precision, recall)
- Multi-class classification (more than just good/problem)
- Deep learning integration
- Defect region highlighting on images
- Cross-validation for better accuracy

---

## References

See also:
- [README.md](README.md) - Main documentation
- [FEATURES.md](FEATURES.md) - Full feature guide
- [QUICK_START.md](QUICK_START.md) - Getting started
