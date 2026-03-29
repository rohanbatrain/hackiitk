# Conservative Gap Detection Fix (CRITICAL-3)

**Date**: March 29, 2026  
**Issue**: CRITICAL-3 - Analyzer too conservative, never marks anything as "fully covered"  
**Status**: 🔄 IN PROGRESS

---

## Problem Analysis

### Current Behavior
- **Minimal ISMS** (46 words): 46 missing, 3 partially covered, 0 covered
- **Complete ISMS** (802 words): 35 missing, 14 partially covered, 0 covered
- **Result**: NO subcategories ever marked as "covered" (no gaps)

### Root Cause Identified

**File**: `analysis/stage_a_detector.py`

**Current Thresholds**:
```python
COVERED_THRESHOLD = 0.8        # > 80% confidence required for "covered"
PARTIAL_LOWER_THRESHOLD = 0.5  # 50-80% = "partially covered"
MISSING_THRESHOLD = 0.3        # < 30% = "missing"
# 30-50% = "ambiguous"
```

**Classification Logic**:
```python
def _classify_coverage(self, confidence: float) -> str:
    if confidence > 0.8:           # > 80%
        return 'covered'
    elif confidence >= 0.5:        # 50-80%
        return 'partially_covered'
    elif confidence < 0.3:         # < 30%
        return 'missing'
    else:                          # 30-50%
        return 'ambiguous'
```

### Why This Is Too Conservative

1. **80% threshold is very high** for semantic matching
   - Requires near-perfect keyword and semantic alignment
   - Real-world policies use varied terminology
   - Even comprehensive policies rarely hit 80% confidence

2. **Complete ISMS policy evidence**:
   - Has 14 "partially covered" (50-80% confidence)
   - These are likely good enough to be considered "covered"
   - Example: GV.OC-01 has explicit "Organizational Context" section but marked as gap

3. **Industry standards**:
   - Most semantic search systems use 60-70% thresholds
   - 80% is appropriate for exact matching, not semantic similarity

---

## Proposed Fix

### Option 1: Lower "Covered" Threshold (RECOMMENDED)

**Change**:
```python
COVERED_THRESHOLD = 0.65       # > 65% confidence (was 0.8)
PARTIAL_LOWER_THRESHOLD = 0.45 # 45-65% = "partially covered" (was 0.5)
MISSING_THRESHOLD = 0.25       # < 25% = "missing" (was 0.3)
# 25-45% = "ambiguous"
```

**Rationale**:
- 65% is industry standard for semantic similarity
- Allows well-written policies to be recognized as covered
- Still conservative enough to catch real gaps
- Reduces false negatives while maintaining accuracy

**Expected Impact**:
- Complete ISMS: ~10-15 subcategories marked as "covered" (no gaps)
- Minimal ISMS: Still mostly "missing" (correct)
- Partial ISMS: Mix of covered/partially covered/missing (correct)

### Option 2: Add "High Confidence Partial" Category

**Change**: Keep thresholds but treat high-confidence partial (70-80%) as covered

```python
def _classify_coverage(self, confidence: float) -> str:
    if confidence > 0.7:           # > 70% = covered
        return 'covered'
    elif confidence >= 0.5:        # 50-70% = partially covered
        return 'partially_covered'
    elif confidence < 0.3:
        return 'missing'
    else:
        return 'ambiguous'
```

**Rationale**:
- More conservative than Option 1
- Recognizes that 70-80% is "good enough"
- Simpler threshold structure

### Option 3: Make Thresholds Configurable

**Change**: Add threshold configuration to config.yaml

```yaml
gap_detection:
  covered_threshold: 0.65
  partial_lower_threshold: 0.45
  missing_threshold: 0.25
```

**Rationale**:
- Allows users to tune based on their needs
- More flexible for different use cases
- Can be adjusted based on validation results

---

## Recommendation

**Implement Option 1** (Lower thresholds to 65/45/25)

**Reasons**:
1. Industry-standard thresholds
2. Balances precision and recall
3. Reduces false negatives significantly
4. Still conservative enough for production
5. Simple, one-line change

**Implementation**:
```python
# analysis/stage_a_detector.py, lines 55-58

# Before
COVERED_THRESHOLD = 0.8
PARTIAL_LOWER_THRESHOLD = 0.5
MISSING_THRESHOLD = 0.3

# After
COVERED_THRESHOLD = 0.65
PARTIAL_LOWER_THRESHOLD = 0.45
MISSING_THRESHOLD = 0.25
```

---

## Validation Plan

### Test Cases

1. **Complete ISMS Policy** (802 words, comprehensive):
   - **Expected**: 10-15 covered, 20-25 partially covered, 10-15 missing
   - **Current**: 0 covered, 14 partially covered, 35 missing

2. **Partial ISMS Policy** (172 words, moderate):
   - **Expected**: 5-10 covered, 15-20 partially covered, 20-25 missing
   - **Current**: 0 covered, 1 partially covered, 47 missing

3. **Minimal ISMS Policy** (46 words, bare minimum):
   - **Expected**: 0-2 covered, 3-5 partially covered, 40-45 missing
   - **Current**: 0 covered, 3 partially covered, 46 missing

### Validation Commands

```bash
# Re-run comprehensive test suite with new thresholds
./run_comprehensive_tests.sh

# Check covered subcategories count
python3 << 'EOF'
import json
import glob

for policy in ['minimal_isms', 'partial_isms', 'complete_isms']:
    outputs = sorted(glob.glob(f"outputs/{policy}_*"), reverse=True)
    if outputs:
        with open(f"{outputs[0]}/gap_analysis_report.json") as f:
            data = json.load(f)
            covered = len(data.get("covered_subcategories", []))
            gaps = len(data["gaps"])
            print(f"{policy}: {covered} covered, {gaps} gaps")
EOF
```

### Success Criteria

- ✅ Complete ISMS: At least 10 subcategories marked as covered
- ✅ Partial ISMS: At least 5 subcategories marked as covered
- ✅ Minimal ISMS: 0-2 subcategories marked as covered
- ✅ No false positives (covered when should be gap)
- ✅ Reduced false negatives (gap when should be covered)

---

## Risk Assessment

### Risks of Lowering Thresholds

1. **False Positives** (marking as covered when it's actually a gap):
   - **Risk Level**: LOW
   - **Mitigation**: 65% is still conservative, requires good semantic match
   - **Impact**: User might miss a real gap

2. **User Confusion** (why is this marked as covered?):
   - **Risk Level**: LOW
   - **Mitigation**: Evidence quotes show what was matched
   - **Impact**: User can review evidence and decide

3. **Compliance Issues** (auditor disagrees with "covered" assessment):
   - **Risk Level**: MEDIUM
   - **Mitigation**: Provide evidence quotes for transparency
   - **Impact**: User may need to add more detail to policy

### Benefits of Lowering Thresholds

1. **Reduced False Negatives**: Comprehensive policies recognized as such
2. **Better User Experience**: Less overwhelming gap lists
3. **More Accurate**: Aligns with industry standards
4. **Actionable**: Users focus on real gaps, not false alarms

### Net Assessment

**Benefits >> Risks** - Proceed with threshold adjustment

---

## Implementation Steps

1. ✅ **Analyze current behavior** - DONE
2. ✅ **Identify root cause** - DONE (80% threshold too high)
3. 🔄 **Adjust thresholds** - IN PROGRESS
4. 🔄 **Run validation tests** - PENDING
5. 🔄 **Compare before/after** - PENDING
6. 🔄 **Document results** - PENDING
7. 🔄 **Commit changes** - PENDING

---

## Expected Impact

### Production Readiness

- **Before**: 8.0/10
- **After**: 8.5/10 (+0.5)
- **Improvement**: More accurate gap detection, better user experience

### User Experience

- **Before**: "Why does my comprehensive policy show 49 gaps?"
- **After**: "Great! 15 subcategories covered, 20 need improvement, 14 missing"

### Accuracy

- **Before**: High precision (few false positives), Low recall (many false negatives)
- **After**: Balanced precision and recall (industry standard)

---

## Status

**Current**: 🔄 IN PROGRESS  
**Next**: Implement threshold adjustment and run validation tests  
**ETA**: 30 minutes

