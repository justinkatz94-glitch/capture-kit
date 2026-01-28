# CLAUDE.md - AI Assistant Guide for Capture Kit

## Project Overview

**Capture Kit** is an AI-powered social media automation and engagement platform that:
- Extracts and analyzes user communication styles from multiple sources
- Benchmarks content performance against top performers in specific niches
- Generates AI-optimized replies and posts matching the user's authentic voice
- Tracks post performance and provides data-driven recommendations

**Primary Domain**: FinTwit (Finance Twitter), with extensibility to crypto and tech niches.

## Repository Structure

```
capture-kit/
├── capture-kit-starter/          # Main application directory
│   ├── automation/               # Core automation system (9 modules)
│   │   ├── schemas.py            # Data models, enums, constants
│   │   ├── user_manager.py       # Multi-user profile management
│   │   ├── content_analyzer.py   # Content analysis (hooks, triggers, etc.)
│   │   ├── llm_generator.py      # Claude API integration
│   │   ├── queue_manager.py      # Content pipeline (pending/approved/posted)
│   │   ├── post_tracker.py       # Post performance tracking
│   │   ├── trending_scanner.py   # Trending content detection
│   │   ├── feedback_loop.py      # Weekly analysis and recommendations
│   │   └── voice_evolver.py      # Iterative voice profile improvement
│   ├── engagement/               # FinTwit engagement tools
│   │   ├── scanner.py            # Scans finance accounts for trending posts
│   │   ├── reply_generator.py    # Generates voice-matched replies
│   │   └── scoring.py            # Scores replies (voice match, engagement, length)
│   ├── social/                   # Social media parsers/scrapers
│   │   ├── twitter_public_scraper.py  # No-auth Twitter scraper
│   │   ├── twitter_parser.py     # Twitter export parser
│   │   ├── linkedin_parser.py    # LinkedIn export parser
│   │   ├── meta_parser.py        # Instagram/Facebook parser
│   │   ├── style_extractor.py    # Cross-platform style analysis
│   │   ├── collector.py          # Orchestrates multi-platform collection
│   │   └── direct_scraper.py     # Playwright-based browser scraping
│   ├── extractors/               # Profile extraction modules
│   │   ├── writing_style.py      # Email/Slack/doc analysis
│   │   ├── speaking_style.py     # Meeting transcript analysis
│   │   ├── work_patterns.py      # Screen capture metadata analysis
│   │   └── preferences.py        # Daily check-in parsing
│   ├── benchmarks/               # Benchmark data and analysis
│   │   ├── benchmark_manager.py  # Manages benchmark operations
│   │   └── finance_twitter.json  # Pre-built FinTwit benchmark
│   ├── niches/                   # Niche configuration templates
│   │   ├── fintwit.json          # Finance traders configuration
│   │   ├── crypto.json           # Cryptocurrency configuration
│   │   └── tech.json             # Tech industry configuration
│   ├── profiles/                 # User voice profiles (JSON)
│   ├── data/                     # Runtime user data storage
│   ├── queue/                    # Content pipeline directories
│   │   ├── pending/
│   │   ├── approved/
│   │   └── posted/
│   ├── test_data/                # Test fixtures
│   │   └── sample_data.py        # Sarah Chen test persona
│   ├── automation_cli.py         # Main unified CLI
│   ├── fintwit_cli.py            # FinTwit-specific CLI
│   ├── benchmark_cli.py          # Benchmark analysis CLI
│   ├── generator.py              # Profile generation pipeline
│   └── run_tests.py              # Test suite runner
├── README.md                     # User-facing documentation
├── PROJECT_SUMMARY.md            # Detailed architecture documentation
├── BUILD_PLAN.md                 # Development roadmap
└── RESEARCH.md                   # Technical specifications
```

## Key Commands

### Development & Testing

```bash
# Run tests
cd capture-kit-starter
python run_tests.py

# Optional: Install browser scraping dependencies
pip install playwright
playwright install chromium
```

### CLI Usage

**Main Automation CLI (`automation_cli.py`)**:
```bash
# User management
python automation_cli.py user create "Name" --twitter @handle --niche fintwit --goal grow_followers
python automation_cli.py user switch "Name"
python automation_cli.py user list
python automation_cli.py user profile

# Content operations
python automation_cli.py scan                                    # Scan for trending
python automation_cli.py opportunities --min-score 50            # Find reply opportunities
python automation_cli.py draft --author @handle --content "..."  # Generate replies
python automation_cli.py analyze --content "..." --platform twitter

# Queue management
python automation_cli.py queue add --content "..." --platform twitter
python automation_cli.py queue list --status pending
python automation_cli.py queue approve <item_id>
python automation_cli.py queue post <item_id> --url <url>

# Analytics
python automation_cli.py report --week 0       # Weekly report
python automation_cli.py trends --weeks 4      # Trend analysis
python automation_cli.py evolve                # Suggest voice updates
python automation_cli.py evolve --apply        # Apply suggestions
```

**FinTwit CLI (`fintwit_cli.py`)**:
```bash
python fintwit_cli.py scan                        # Find trending posts
python fintwit_cli.py scan --category options     # Filter by category
python fintwit_cli.py draft -c "Post text" -a @author
python fintwit_cli.py brief                       # Daily engagement brief
python fintwit_cli.py analyze -t "Reply text"     # Score a reply
```

**Benchmark CLI (`benchmark_cli.py`)**:
```bash
python benchmark_cli.py analyze @username -b finance_twitter
python benchmark_cli.py compare @yourusername -b finance_twitter
python benchmark_cli.py show finance_twitter
python benchmark_cli.py add-viral <URL> -b finance_twitter
```

## Code Architecture

### Core Patterns

1. **Manager Pattern**: `UserManager`, `QueueManager`, `PostTracker`, `BenchmarkManager`
   - Central responsibility for state and persistence
   - JSON file-based storage

2. **Analyzer Pattern**: `ContentAnalyzer`, `FeedbackLoop`, `VoiceEvolver`
   - Extract structured insights from unstructured data

3. **Generator Pattern**: `ReplyGenerator`, `LLMGenerator`
   - Claude API integration with template fallbacks

4. **Scanner Pattern**: `FinTwitScanner`, `TrendingScanner`
   - Multi-criteria filtering and scoring

### Data Flow

```
TrendingScanner.scan()
    → Fetch posts from watchlist
    → Filter by keywords
    ↓
ReplyGenerator.generate_reply()
    → Load voice profile
    → Auto-target optimal length (26 words for FinTwit)
    → Generate options
    ↓
Scoring.score_reply()
    → Voice Match (35%)
    → Engagement Potential (45%)
    → Length Score (20%)
    ↓
QueueManager → PostTracker → FeedbackLoop → VoiceEvolver
```

### Key Data Schemas (automation/schemas.py)

**Enums**:
- `Platform`: TWITTER, LINKEDIN, INSTAGRAM
- `Goal`: GROW_FOLLOWERS, DRIVE_TRAFFIC, BUILD_AUTHORITY
- `HookType`: QUESTION, CONTRARIAN, DATA, STORY, CALLOUT, BOLD_CLAIM, HOW_TO, LIST
- `Framework`: SINGLE, THREAD, QUOTE_TWEET, REPLY, CAROUSEL
- `Trigger`: FEAR, GREED, CURIOSITY, FOMO, VALIDATION, URGENCY, EXCLUSIVITY
- `QueueStatus`: PENDING, APPROVED, POSTED, REJECTED

**Dataclasses**:
- `PostRecord`: Individual post tracking with engagement snapshots
- `QueueItem`: Content queue item with scores and status
- `Experiment`: A/B testing structure
- `WeeklySummary`: Performance analysis
- `ContentAnalysis`: Deep content analysis result

**Helper Functions**:
```python
generate_id()   # Returns 8-char UUID
now_iso()       # Current time in ISO format
load_json(path) # Load JSON or return empty dict
save_json(path, data)  # Save JSON with auto-mkdir
```

### Platform Configuration Constants

```python
PLATFORM_CONFIGS = {
    "twitter": {
        "reply_length_chars": (70, 100),
        "post_length_chars": (200, 280),
        "strategy": "Fast, short, insight not praise"
    },
    "linkedin": {
        "post_length_chars": (1200, 1500),
        "strategy": "Depth > speed, 3-5 sentences"
    },
    "instagram": {
        "caption_length_chars": (150, 2200),
        "strategy": "Very short, genuine, relationship-focused"
    }
}
```

## File Storage Conventions

### Directory Organization
```
data/
└── {username}/
    ├── post_history.json
    ├── experiments.json
    ├── trending_cache.json
    ├── weekly_summaries.json
    └── voice_evolution.json

profiles/
└── {username_lowercase}.json

queue/
├── pending/
├── approved/
└── posted/
```

### User Profile Structure
```json
{
  "name": "User Name",
  "username": "@handle",
  "niche": "fintwit",
  "goal": "grow_followers",
  "platform_handles": {"twitter": "@handle", "linkedin": "..."},
  "watchlist": ["@account1", "@account2"],
  "keywords": ["options", "gamma", "positioning"],
  "voice": {
    "tone": "Professional",
    "formality": 3,
    "vocabulary": "Professional",
    "emoji_style": "Minimal",
    "signature_phrases": ["key here is", "factor in positioning"],
    "common_openers": ["The", "Here's"],
    "avoided_phrases": []
  },
  "style": {
    "sentence_length": "concise",
    "punctuation": "standard",
    "capitalization": "standard"
  }
}
```

## Coding Conventions

### Naming

- **Modules**: lowercase with underscores: `content_analyzer.py`, `voice_evolver.py`
- **Classes**: PascalCase: `ContentAnalyzer`, `UserManager`
- **Functions**: verb-first action: `analyze_content()`, `generate_reply()`
- **Private methods**: underscore prefix: `_load_profile()`, `_parse_date()`
- **JSON files**: lowercase with underscores: `post_history.json`

### Code Patterns

**Dataclass with serialization**:
```python
@dataclass
class PostRecord:
    id: str
    content: str
    engagement: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PostRecord':
        return cls(**data)
```

**Enum usage for type safety**:
```python
class Platform(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"

# Usage: Platform.TWITTER.value == "twitter"
```

**Safe JSON loading**:
```python
def load_json(path: str) -> Dict:
    p = Path(path)
    return json.load(p.open()) if p.exists() else {}
```

### Import Organization

Standard imports at top, then local imports:
```python
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

# Local imports
from automation.schemas import PostRecord, Platform
from automation import UserManager, ContentAnalyzer
```

## Extension Points

### Adding a New Niche

1. Create `niches/{niche_name}.json`:
```json
{
  "name": "niche_name",
  "default_watchlist": ["@account1", "@account2"],
  "keywords": ["keyword1", "keyword2"],
  "optimal_length": {"twitter_reply": 26, "twitter_post": 45},
  "best_posting_times": {"twitter": [9, 14, 16, 19]},
  "tone": "professional",
  "vocabulary": "technical",
  "benchmark_name": "niche_benchmark"
}
```

2. Optionally create `benchmarks/{niche_benchmark}.json` with benchmark data

### Adding a New Platform

1. Add to `Platform` enum in `automation/schemas.py`
2. Add parser in `social/` directory
3. Add to `PLATFORM_CONFIGS` in `schemas.py`
4. Update `SocialCollector` in `social/collector.py`

### Adding New Content Types

1. Add to relevant enum in `schemas.py` (e.g., `HookType`, `Framework`)
2. Update detection patterns in `ContentAnalyzer`
3. Update scoring weights if needed

## Dependencies

**Core** (Python stdlib only):
- json, pathlib, dataclasses, enum, typing, datetime, re, collections, uuid

**Optional**:
- `playwright`: Browser scraping (`pip install playwright && playwright install chromium`)
- `anthropic`: Claude API integration for LLM generation

## Testing

Run all tests:
```bash
cd capture-kit-starter
python run_tests.py
```

Test data uses the Sarah Chen persona with:
- 10 email samples
- 15 Slack messages
- 5 meeting transcripts
- 65 screen capture records
- 5 daily check-in responses

## Important Notes for AI Assistants

1. **No external dependencies for core**: The main functionality uses only Python stdlib
2. **JSON-based persistence**: All data stored as JSON files, not databases
3. **File paths**: Use `Path` from `pathlib` for cross-platform compatibility
4. **Voice profiles**: Located in `profiles/` - never modify user voice profiles without explicit request
5. **Benchmark data**: Located in `benchmarks/` - treat as read-only reference data
6. **The main entry point**: `automation_cli.py` is the unified CLI; prefer using it over individual CLIs
7. **Content generation**: Falls back to templates if Claude API unavailable
8. **Reply scoring**: Weighted average of voice match (35%), engagement potential (45%), length (20%)
9. **FinTwit optimal length**: 26 words for replies (from benchmark data)

## Common Tasks

### Analyze content before posting
```bash
python automation_cli.py analyze --content "Your draft post" --platform twitter
```

### Generate replies that match user voice
```bash
python automation_cli.py draft --author @targetaccount --content "Original post text"
```

### Track post performance
```bash
python automation_cli.py log --content "Posted content" --url "https://..." --likes 10
python automation_cli.py report  # Generate weekly report
```

### Evolve voice based on performance
```bash
python automation_cli.py evolve          # See suggestions
python automation_cli.py evolve --apply  # Apply changes
```
