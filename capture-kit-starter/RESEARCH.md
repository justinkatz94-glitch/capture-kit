# Capture Kit - Research Document

## Current State Analysis

### Existing Files (Complete)
| File | Status | Purpose |
|------|--------|---------|
| `style_extractor.py` | ✅ Complete | Analyzes social posts for communication patterns |
| `direct_scraper.py` | ✅ Complete | Playwright-based scraper (Twitter, LinkedIn, Instagram) |
| `collector.py` | ⚠️ Broken imports | Orchestrator - imports parsers that don't exist |
| `sample_data.py` | ✅ Complete | Test data for Sarah Chen persona |
| `run_tests.py` | ⚠️ Broken imports | Test runner - imports extractors that don't exist |
| `social-media-collection-spec.md` | ✅ Spec | Contains all parser code to extract |

### Missing Files (To Create)

**Core Extractors (`extractors/`):**
- `__init__.py`
- `writing_style.py` → `extract_writing_style(samples: List[str]) -> Dict`
- `speaking_style.py` → `extract_speaking_style(transcripts: List[str]) -> Dict`
- `work_patterns.py` → `extract_work_patterns(screen_data: List[Dict]) -> Dict`
- `preferences.py` → `extract_preferences(checkins: Dict) -> Dict`

**Generator:**
- `generator.py` → `generate_profile(**inputs) -> Dict`

**Test Data (reorganize):**
- `test_data/__init__.py`
- `test_data/sample_data.py` (move from root)

**Social Media Parsers (`social/`):**
- `__init__.py`
- `twitter_parser.py` → `parse_twitter_export(zip_path: str) -> Dict`
- `linkedin_parser.py` → `parse_linkedin_export(zip_path: str) -> Dict`
- `meta_parser.py` → `parse_instagram_export()`, `parse_facebook_export()`
- Move: `collector.py`, `style_extractor.py`, `direct_scraper.py`

---

## Expected Output Schemas

### writing_style (from sample_data.py lines 433-444)
```python
{
    "tone": "Professional but warm",       # string
    "formality": 3,                        # 1-5 scale
    "formality_label": "Balanced Professional",
    "avg_sentence_length": "medium",       # short/medium/long
    "punctuation_patterns": ["uses_exclamations", "occasional_emoji"],
    "common_phrases": ["let me know", "at the end of the day", ...],
    "sign_off": {
        "most_common": "Best,",
        "frequency": 0.7,
        "alternatives": ["Sarah", "Thanks,"]
    }
}
```

### speaking_style (from sample_data.py lines 446-457)
```python
{
    "pace": "medium",
    "filler_words": [
        {"word": "um", "per_100_words": 1.2},
        {"word": "like", "per_100_words": 0.8}
    ],
    "vocabulary_level": "moderate",        # simple/moderate/advanced
    "directness": 4,                       # 1-5 scale
    "directness_label": "Direct but Diplomatic",
    "verbal_habits": ["at the end of the day", "let's circle back"]
}
```

### work_patterns (from sample_data.py lines 459-468)
```python
{
    "peak_hours": ["07:00-08:00", "09:00-11:00"],
    "primary_tools": ["Gmail", "Slack", "Figma", ...],
    "meeting_load": "medium",              # low/medium/high
    "email_habits": {
        "batch_times": ["morning", "late_afternoon"],
        "avg_response_length": "medium"
    },
    "task_switching_frequency": "moderate"
}
```

### preferences (from sample_data.py lines 469-490)
```python
{
    "do": ["Draft client emails for review", ...],
    "never_do": ["Send anything to clients without approval", ...],
    "ask_first": ["Before rescheduling client meetings", ...]
}
```

---

## Key Integration Points

### run_tests.py expects (lines 15-22, 32, 42):
```python
from test_data.sample_data import (
    get_all_writing_samples,   # Returns List[str]
    get_all_transcripts,       # Returns List[str]  
    get_screen_captures,       # Returns List[Dict]
    get_daily_checkins,        # Returns Dict
    get_expected_profile,      # Returns Dict
    validate_profile           # Returns Dict
)

from extractors.writing_style import extract_writing_style
# extract_writing_style(samples: List[str]) -> Dict
```

### collector.py expects (lines 26-29):
```python
from .twitter_parser import parse_twitter_export
from .linkedin_parser import parse_linkedin_export
from .meta_parser import parse_instagram_export, parse_facebook_export
from .style_extractor import extract_social_style
```

---

## Test Data Summary (Sarah Chen Persona)

- **10 email samples** - Range from formal client to casual team
- **15 Slack messages** - Short, informal
- **3 document snippets** - Proposals, notes, briefs
- **5 transcripts** - Meetings, calls, conversations
- **65 screen captures** - 5 days of activity
- **5 daily check-ins** - Explicit preferences

**Expected signals to detect:**
- Sign-off: "Best," (70% frequency)
- Phrases: "let me know", "at the end of the day", "let's circle back"
- Verbal habits: "um", "like", "you know"
- Tools: Gmail, Slack, Figma, Zoom, Google Docs, Notion
- Constraints: No meetings before 9am, no sending without approval

---

## Spec Code Locations

| Parser | Spec Lines | Key Function |
|--------|-----------|--------------|
| Twitter | 160-270 | `parse_twitter_export()`, `_parse_twitter_date()`, `_get_date_range()` |
| LinkedIn | 275-340 | `parse_linkedin_export()` |
| Instagram | 345-410 | `parse_instagram_export()` |
| Facebook | 415-480 | `parse_facebook_export()` |

---

## Final Directory Structure

```
capture-kit/
├── extractors/
│   ├── __init__.py
│   ├── writing_style.py
│   ├── speaking_style.py
│   ├── work_patterns.py
│   └── preferences.py
├── social/
│   ├── __init__.py
│   ├── twitter_parser.py
│   ├── linkedin_parser.py
│   ├── meta_parser.py
│   ├── style_extractor.py
│   ├── collector.py
│   └── direct_scraper.py
├── test_data/
│   ├── __init__.py
│   └── sample_data.py
├── generator.py
└── run_tests.py
```
