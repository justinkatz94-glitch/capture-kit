# Capture Kit

An AI profile extraction system that learns about a user's communication style, work patterns, and preferences by analyzing multiple data sources. Capture Kit builds comprehensive digital profiles to enable AI assistants to interact with users in a more personalized and context-aware manner.

## Features

### Profile Extraction
- **Writing Style Analysis** - Analyzes emails, Slack messages, and documents to extract tone, formality, common phrases, and signature expressions
- **Speaking Style Analysis** - Processes meeting transcripts to detect verbal patterns, filler words, and confidence markers
- **Work Patterns Analysis** - Examines screen capture metadata to understand peak hours, primary tools, and task switching habits
- **Preferences Extraction** - Parses daily check-ins to identify what users want help with and their hard constraints

### Social Media Collection
- **Platform Parsers** - Twitter/X, LinkedIn, Instagram, and Facebook export parsers
- **Style Analyzer** - Cross-platform analysis of emoji usage, hashtags, vocabulary, and tone
- **Multiple Collection Methods**:
  - Official data exports (recommended)
  - Optional direct scraping via Playwright (transparent, visible browser)
  - Unified collector for multi-source orchestration

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/capture-kit.git
cd capture-kit/capture-kit-starter

# Run tests (no external dependencies needed for core functionality)
python run_tests.py

# Optional: For direct scraping capabilities
pip install playwright
playwright install chromium
```

## Usage

### Profile Generation

```python
from generator import generate_profile, generate_profile_summary
from test_data.sample_data import (
    get_all_writing_samples,
    get_all_transcripts,
    get_screen_captures,
    get_daily_checkins
)

profile = generate_profile(
    writing_samples=get_all_writing_samples(),
    transcripts=get_all_transcripts(),
    screen_captures=get_screen_captures(),
    daily_checkins=get_daily_checkins()
)

print(generate_profile_summary(profile))
```

### Social Media Analysis (CLI)

```bash
# Analyze a single export
python -m social.collector export --twitter /path/to/twitter-archive.zip --output result.json

# Analyze multiple exports
python -m social.collector export --twitter twitter.zip --linkedin linkedin.zip --output analysis.json

# Auto-detect exports in a folder
python -m social.collector export --folder ./exports --output analysis.json
```

### Social Media Analysis (API)

```python
from social import SocialCollector

collector = SocialCollector()
collector.add_export("twitter", "/path/to/twitter-archive.zip")
collector.add_export("linkedin", "/path/to/linkedin-export.zip")

analysis = collector.analyze()
print(collector.summary())
```

## Project Structure

```
capture-kit/
└── capture-kit-starter/
    ├── extractors/           # Core profile extractors
    │   ├── writing_style.py
    │   ├── speaking_style.py
    │   ├── work_patterns.py
    │   └── preferences.py
    ├── social/               # Social media collection
    │   ├── twitter_parser.py
    │   ├── linkedin_parser.py
    │   ├── meta_parser.py
    │   ├── collector.py
    │   ├── style_extractor.py
    │   └── direct_scraper.py
    ├── test_data/            # Test fixtures
    ├── generator.py          # Profile generation pipeline
    └── run_tests.py          # Test suite
```

## Output Format

Profiles are generated as JSON with this structure:

```json
{
  "communication": {
    "writing_style": {
      "tone": "Professional but warm",
      "formality": 3,
      "common_phrases": ["let me know", "at the end of the day"],
      "sign_off": {"most_common": "Best,", "frequency": 0.7}
    },
    "speaking_style": { ... }
  },
  "work_patterns": { ... },
  "preferences": { ... },
  "social_presence": { ... }
}
```

## Design Principles

- **Privacy-First** - Analyzes only the user's own exported data
- **Transparent Scraping** - Browser window visible during direct scraping
- **Graceful Degradation** - Optional features don't break core functionality
- **No External Dependencies** - Core uses only Python stdlib

## License

MIT
