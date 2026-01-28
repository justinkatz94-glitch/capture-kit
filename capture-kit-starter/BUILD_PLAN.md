# Capture Kit - BUILD PLAN

## Overview
Transform flat file structure into modular package architecture.
**Estimated steps:** 12 files to create/modify
**Test command:** `python run_tests.py`

---

## PHASE 1: Directory Structure & Init Files

### Step 1.1: Create extractors package
**Files:** `extractors/__init__.py`

```python
"""Core profile extractors for Capture Kit."""
from .writing_style import extract_writing_style
from .speaking_style import extract_speaking_style
from .work_patterns import extract_work_patterns
from .preferences import extract_preferences

__all__ = [
    'extract_writing_style',
    'extract_speaking_style', 
    'extract_work_patterns',
    'extract_preferences'
]
```

**Test:** `python -c "from extractors import extract_writing_style"` (will fail until step 2)

### Step 1.2: Create social package
**Files:** `social/__init__.py`

```python
"""Social media collection and analysis for Capture Kit."""
from .twitter_parser import parse_twitter_export
from .linkedin_parser import parse_linkedin_export
from .meta_parser import parse_instagram_export, parse_facebook_export
from .style_extractor import extract_social_style
from .collector import SocialCollector

__all__ = [
    'parse_twitter_export',
    'parse_linkedin_export',
    'parse_instagram_export',
    'parse_facebook_export',
    'extract_social_style',
    'SocialCollector'
]
```

### Step 1.3: Create test_data package
**Files:** `test_data/__init__.py`

```python
"""Test data and fixtures for Capture Kit."""
from .sample_data import (
    get_all_writing_samples,
    get_all_transcripts,
    get_screen_captures,
    get_daily_checkins,
    get_expected_profile,
    validate_profile
)
```

---

## PHASE 2: Core Extractors

### Step 2.1: Writing Style Extractor
**File:** `extractors/writing_style.py`

**Input:** `List[str]` - email/slack/doc text samples
**Output:** Dict with tone, formality, common_phrases, sign_off

**Key algorithms:**
1. Detect sign-offs by regex: `r'^(Best|Thanks|Cheers|Sarah|Regards)[,]?\s*$'`
2. Count exclamation marks for tone
3. Extract common phrases by n-gram frequency
4. Calculate formality from avg word length + formal markers

**Test:** 
```bash
python -c "
from extractors.writing_style import extract_writing_style
from test_data.sample_data import get_all_writing_samples
result = extract_writing_style(get_all_writing_samples())
assert 'tone' in result
assert 'formality' in result
print('✅ writing_style works')
"
```

### Step 2.2: Speaking Style Extractor
**File:** `extractors/speaking_style.py`

**Input:** `List[str]` - meeting transcripts
**Output:** Dict with directness, vocabulary_level, verbal_habits, filler_words

**Key algorithms:**
1. Count filler words: "um", "uh", "like", "you know", "so", "basically"
2. Detect verbal habits by phrase frequency
3. Calculate directness from hedging language ratio
4. Vocabulary level from avg word length

**Test:**
```bash
python -c "
from extractors.speaking_style import extract_speaking_style
from test_data.sample_data import get_all_transcripts
result = extract_speaking_style(get_all_transcripts())
assert 'directness' in result
assert 'verbal_habits' in result
print('✅ speaking_style works')
"
```

### Step 2.3: Work Patterns Extractor
**File:** `extractors/work_patterns.py`

**Input:** `List[Dict]` - screen captures with timestamp, app, window_title
**Output:** Dict with primary_tools, meeting_load, peak_hours

**Key algorithms:**
1. Count app usage frequency → primary_tools
2. Count Zoom entries → meeting_load (low/medium/high)
3. Group timestamps by hour → peak_hours
4. Detect task switching by consecutive different apps

**Test:**
```bash
python -c "
from extractors.work_patterns import extract_work_patterns
from test_data.sample_data import get_screen_captures
result = extract_work_patterns(get_screen_captures())
assert 'primary_tools' in result
assert 'Gmail' in result['primary_tools']
print('✅ work_patterns works')
"
```

### Step 2.4: Preferences Extractor
**File:** `extractors/preferences.py`

**Input:** `Dict` - daily check-in responses
**Output:** Dict with do[], never_do[], ask_first[]

**Key algorithms:**
1. Parse day_4 response for "never_do" (explicit constraints)
2. Parse day_2 response for "do" (desired help)
3. Parse day_1 for implicit preferences
4. Use keyword extraction: "hate", "don't", "never", "always", "without"

**Test:**
```bash
python -c "
from extractors.preferences import extract_preferences
from test_data.sample_data import get_daily_checkins
result = extract_preferences(get_daily_checkins())
assert 'never_do' in result
assert any('9am' in item.lower() or 'morning' in item.lower() for item in result['never_do'])
print('✅ preferences works')
"
```

---

## PHASE 3: Social Media Parsers

### Step 3.1: Twitter Parser
**File:** `social/twitter_parser.py`
**Source:** `social-media-collection-spec.md` lines 160-270

Copy verbatim and add error handling for:
- Missing zip file
- Malformed JSON
- Missing tweets.js

### Step 3.2: LinkedIn Parser
**File:** `social/linkedin_parser.py`
**Source:** `social-media-collection-spec.md` lines 275-340

### Step 3.3: Meta Parser (Instagram + Facebook)
**File:** `social/meta_parser.py`
**Source:** `social-media-collection-spec.md` lines 345-480

Combine Instagram and Facebook parsers into single file.

### Step 3.4: Move existing files to social/
**Files to move:**
- `style_extractor.py` → `social/style_extractor.py`
- `collector.py` → `social/collector.py`
- `direct_scraper.py` → `social/direct_scraper.py`

**Update collector.py imports:**
```python
# Change from:
from .twitter_parser import parse_twitter_export
# These are now correct (same package)
```

---

## PHASE 4: Generator & Integration

### Step 4.1: Profile Generator
**File:** `generator.py`

```python
def generate_profile(
    writing_samples: List[str] = None,
    transcripts: List[str] = None,
    screen_captures: List[Dict] = None,
    daily_checkins: Dict = None,
    social_exports: List[str] = None
) -> Dict[str, Any]:
    """Generate complete user profile from all data sources."""
    
    profile = {}
    
    if writing_samples:
        profile["communication"] = profile.get("communication", {})
        profile["communication"]["writing_style"] = extract_writing_style(writing_samples)
    
    if transcripts:
        profile["communication"] = profile.get("communication", {})
        profile["communication"]["speaking_style"] = extract_speaking_style(transcripts)
    
    if screen_captures:
        profile["work_patterns"] = extract_work_patterns(screen_captures)
    
    if daily_checkins:
        profile["preferences"] = extract_preferences(daily_checkins)
    
    if social_exports:
        # Parse and analyze social media
        from social import SocialCollector
        collector = SocialCollector()
        for export_path in social_exports:
            # Auto-detect platform from filename
            ...
        profile["social_presence"] = collector.analyze()
    
    return profile
```

### Step 4.2: Update run_tests.py imports
**File:** `run_tests.py` line 15

```python
# Change from:
from test_data.sample_data import (
# Already correct - just need test_data/ folder to exist
```

### Step 4.3: Move sample_data.py
**Action:** Copy `sample_data.py` → `test_data/sample_data.py`

---

## PHASE 5: Final Testing

### Step 5.1: Run full test suite
```bash
cd /path/to/capture-kit
python run_tests.py
```

**Expected output:**
```
TESTING: writing_style.py
✅ Extraction completed
✅ Tone: expected 'Professional but warm', got '...'
...

TESTING: speaking_style.py
✅ Extraction completed
...

TESTING: work_patterns.py
✅ Extraction completed
✅ Tools detected: {'Gmail', 'Slack', 'Figma', ...}
...

TESTING: preferences.py
✅ Extraction completed
✅ Detected morning meeting preference
✅ Detected approval requirement
...

TESTING: Full Profile Generation Pipeline
✅ Profile generation completed

TEST SUMMARY
  writing_style: ✅ PASS
  speaking_style: ✅ PASS
  work_patterns: ✅ PASS
  preferences: ✅ PASS
  full_profile: ✅ PASS

Total: 5/5 tests passed
```

---

## Execution Order

1. ☐ Create `extractors/__init__.py`
2. ☐ Create `social/__init__.py`
3. ☐ Create `test_data/__init__.py`
4. ☐ Copy `sample_data.py` → `test_data/sample_data.py`
5. ☐ Create `extractors/writing_style.py`
6. ☐ Create `extractors/speaking_style.py`
7. ☐ Create `extractors/work_patterns.py`
8. ☐ Create `extractors/preferences.py`
9. ☐ Create `social/twitter_parser.py`
10. ☐ Create `social/linkedin_parser.py`
11. ☐ Create `social/meta_parser.py`
12. ☐ Move `style_extractor.py` → `social/`
13. ☐ Move `collector.py` → `social/` (update imports)
14. ☐ Move `direct_scraper.py` → `social/`
15. ☐ Create `generator.py`
16. ☐ Run `python run_tests.py`

---

## Risk Mitigation

**If tests fail:**
1. Check import paths (relative vs absolute)
2. Verify function signatures match expected
3. Check output schema matches EXPECTED_PROFILE
4. Add debug prints to narrow failure point

**Common gotchas:**
- Python package needs `__init__.py` in each directory
- Relative imports (`.module`) only work inside packages
- Test runner adds parent to sys.path - may need adjustment
