# Capture Kit

An AI profile extraction and social media engagement system. Capture Kit learns your communication style, benchmarks against top performers, and helps you create optimized content in your authentic voice.

## Features

### Profile Extraction
- **Writing Style Analysis** - Analyzes emails, Slack messages, and documents to extract tone, formality, common phrases, and signature expressions
- **Speaking Style Analysis** - Processes meeting transcripts to detect verbal patterns, filler words, and confidence markers
- **Work Patterns Analysis** - Examines screen capture metadata to understand peak hours, primary tools, and task switching habits
- **Preferences Extraction** - Parses daily check-ins to identify what users want help with and their hard constraints

### Social Media Collection
- **Platform Parsers** - Twitter/X, LinkedIn, Instagram, and Facebook export parsers
- **Twitter Public Scraper** - Fetch public profiles using Twitter's syndication API (no auth required)
- **Style Analyzer** - Cross-platform analysis of emoji usage, hashtags, vocabulary, and tone

### Benchmarking System
- **Top Performer Analysis** - Analyze successful accounts in your niche
- **Viral Post Patterns** - Track what makes posts successful (hooks, structure, timing)
- **Profile Comparison** - Compare your style to benchmarks with gap analysis
- **Actionable Recommendations** - Get specific suggestions to improve engagement

### FinTwit Engagement System
- **Daily Scanner** - Find trending posts from finance Twitter accounts
- **Reply Generator** - Draft replies in YOUR voice, optimized for engagement
- **Voice Matching** - Uses your profile to maintain authentic voice
- **Benchmark Optimization** - Auto-targets optimal length and style from benchmark data

## Installation

```bash
# Clone the repository
git clone https://github.com/justinkatz94-glitch/capture-kit.git
cd capture-kit/capture-kit-starter

# Run tests (no external dependencies needed for core functionality)
python run_tests.py

# Optional: For browser scraping capabilities
pip install playwright
playwright install chromium
```

## Quick Start

### Scan FinTwit for Trending Posts

```bash
python fintwit_cli.py scan
python fintwit_cli.py scan --category options --limit 10
python fintwit_cli.py opportunities
```

### Draft Replies in Your Voice

```bash
python fintwit_cli.py draft -c "Gamma flip incoming. Dealers short below 5900." -a spotgamma
```

### Get Daily Engagement Brief

```bash
python fintwit_cli.py brief
```

### Benchmark Analysis

```bash
# Analyze a top account
python benchmark_cli.py analyze @unusual_whales -b finance_twitter

# Compare your profile to benchmark
python benchmark_cli.py compare @yourusername -b finance_twitter

# Show benchmark summary
python benchmark_cli.py show finance_twitter
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
    │   ├── twitter_public_scraper.py
    │   ├── linkedin_parser.py
    │   ├── collector.py
    │   └── style_extractor.py
    ├── benchmarks/           # Benchmark data and analysis
    │   ├── benchmark_manager.py
    │   └── finance_twitter.json
    ├── engagement/           # FinTwit engagement tools
    │   ├── scanner.py
    │   ├── reply_generator.py
    │   └── scoring.py
    ├── profiles/             # Voice profiles
    │   └── justin_katz.json
    ├── benchmark_cli.py      # Benchmark CLI
    ├── fintwit_cli.py        # FinTwit engagement CLI
    ├── generator.py          # Profile generation pipeline
    └── run_tests.py          # Test suite
```

## CLI Commands

### FinTwit CLI (`fintwit_cli.py`)

| Command | Description |
|---------|-------------|
| `scan` | Find trending posts in finance Twitter |
| `scan --category options` | Filter by category (options, dealer_positioning, market_structure) |
| `opportunities` | Find best posts to reply to |
| `draft -c "post content"` | Generate reply options in your voice |
| `brief` | Daily engagement brief |
| `analyze -t "reply text"` | Score a reply for quality |

### Benchmark CLI (`benchmark_cli.py`)

| Command | Description |
|---------|-------------|
| `analyze @username -b benchmark` | Add top account to benchmark |
| `compare @username -b benchmark` | Compare profile to benchmark |
| `show benchmark` | Display benchmark summary |
| `add-viral URL -b benchmark` | Add viral post for analysis |

## Benchmark Data

The `finance_twitter` benchmark includes patterns from top performers:

- **Optimal post length**: ~26 words
- **Best posting hours**: 4-8 PM
- **Best days**: Tuesday, Friday, Thursday
- **Vocabulary**: Professional
- **Tone**: Measured
- **Emoji usage**: Minimal

## Reply Scoring

Replies are scored on three dimensions:

| Metric | Weight | Description |
|--------|--------|-------------|
| Voice Match | 35% | How much it sounds like you |
| Engagement Potential | 45% | Based on benchmark patterns |
| Length Score | 20% | Proximity to optimal length |

## Output Examples

### Profile JSON
```json
{
  "communication": {
    "writing_style": {
      "tone": "Professional but warm",
      "formality": 3,
      "common_phrases": ["let me know", "at the end of the day"]
    }
  },
  "work_patterns": { ... },
  "preferences": { ... }
}
```

### Generated Reply
```
#1 [INSIGHT] (Score: 87.5/100)
   Voice Match: 89% | Engagement: 83% | Length: 95%
   Words: 24 (target: 26)

   "The key here is the options market is signaling direction.
    When you factor in positioning, it paints a clearer picture."
```

## Design Principles

- **Privacy-First** - Analyzes only your own data
- **Voice Authenticity** - Maintains your unique style
- **Data-Driven** - Recommendations based on benchmark patterns
- **No External Dependencies** - Core uses only Python stdlib

## License

MIT
