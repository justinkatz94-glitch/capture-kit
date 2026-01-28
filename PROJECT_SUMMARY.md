# Capture Kit - Project Summary

A comprehensive AI-powered social media automation system for content creation, optimization, and growth tracking.

## Project Structure

```
capture-kit/
├── capture-kit-starter/
│   ├── automation/           # Core automation system
│   │   ├── __init__.py       # Package exports
│   │   ├── schemas.py        # Data models and enums
│   │   ├── user_manager.py   # Multi-user profile management
│   │   ├── content_analyzer.py # Deep content analysis
│   │   ├── llm_generator.py  # Claude API integration
│   │   ├── queue_manager.py  # Content pipeline management
│   │   ├── post_tracker.py   # Post performance tracking
│   │   ├── trending_scanner.py # Trending content detection
│   │   ├── feedback_loop.py  # Weekly analysis & insights
│   │   ├── voice_evolver.py  # Iterative voice improvement
│   │   ├── follow_targeting.py # Follow/unfollow management
│   │   │
│   │   └── platforms/        # Platform adapters
│   │       ├── __init__.py   # Registry & factory
│   │       ├── base.py       # Abstract base class
│   │       ├── twitter.py    # Twitter rules & scoring
│   │       ├── linkedin.py   # LinkedIn rules & scoring
│   │       └── instagram.py  # Instagram rules & scoring
│   │
│   ├── benchmarks/           # Benchmark system
│   │   ├── benchmark_manager.py
│   │   └── finance_twitter.json
│   │
│   ├── engagement/           # FinTwit engagement system
│   │   ├── scanner.py        # Trending post scanner
│   │   ├── reply_generator.py # Voice-matched reply generation
│   │   └── scoring.py        # Reply scoring system
│   │
│   ├── social/               # Social media scrapers
│   │   └── twitter_public_scraper.py  # No-auth Twitter scraper
│   │
│   ├── profiles/             # User voice profiles
│   ├── data/                 # Runtime data
│   │   ├── targets.json      # Follow targeting data
│   │   └── {user}/           # Per-user data
│   ├── queue/                # Content queue pipeline
│   │   ├── pending/
│   │   ├── approved/
│   │   └── posted/
│   ├── niches/               # Niche configuration templates
│   │   ├── fintwit.json
│   │   ├── crypto.json
│   │   └── tech.json
│   │
│   ├── automation_cli.py     # Main unified CLI (14 command groups)
│   ├── benchmark_cli.py      # Benchmark CLI
│   ├── fintwit_cli.py        # FinTwit engagement CLI
│   └── run_tests.py          # Test runner
│
└── PROJECT_SUMMARY.md        # This file
```

## Core Systems Built

### 1. Twitter Scraper (No Authentication)
**File:** `social/twitter_public_scraper.py`

Scrapes public Twitter profiles using Twitter's syndication API - no authentication required.

```python
from social.twitter_public_scraper import fetch_twitter_profile

profile = fetch_twitter_profile("bluedeerc")
# Returns: name, bio, followers, following, tweets[]
```

### 2. Benchmarking System
**Files:** `benchmarks/benchmark_manager.py`, `benchmarks/finance_twitter.json`

Analyzes top performers in your niche to extract winning patterns.

**Features:**
- Analyze top accounts (vocabulary, tone, timing)
- Extract optimal content length (26 words for FinTwit)
- Identify peak posting hours
- Track viral post patterns
- Compare your performance to benchmarks

```python
from benchmarks.benchmark_manager import BenchmarkManager

bm = BenchmarkManager("finance_twitter")
gaps = bm.compare_to_benchmark(my_posts)
recommendations = bm.get_benchmark_recommendations()
```

### 3. FinTwit Engagement System
**Files:** `engagement/scanner.py`, `engagement/reply_generator.py`, `engagement/scoring.py`

Automated system for finding and drafting replies to trending posts.

**Features:**
- Scan watchlist accounts for opportunities
- Filter by keywords (options, dealer positioning, market structure)
- Generate voice-matched replies
- Auto-target optimal length from benchmark data
- Score replies for engagement potential

```python
from engagement.scanner import FinTwitScanner
from engagement.reply_generator import ReplyGenerator

scanner = FinTwitScanner()
posts = scanner.get_trending_posts()

generator = ReplyGenerator(profile_path="profiles/justin_katz.json")
reply = generator.generate_reply(post)  # Auto-targets 26 words
```

### 4. Platform Adapter Framework
**Folder:** `automation/platforms/`

Multi-platform support with platform-specific rules, scoring, and optimization.

```python
from automation.platforms import get_adapter, list_platforms

# List available platforms
platforms = list_platforms()  # ['twitter', 'linkedin', 'instagram']

# Get platform-specific adapter
adapter = get_adapter("linkedin")

# Score content for platform fit
result = adapter.score_platform_fit(content, "post")
# Returns: {"score": 85, "issues": ["First line too long"]}

# Get rules for LLM prompts
rules = adapter.get_system_prompt_rules()
```

**Platform Configurations:**

| Platform | Post Length | Reply Length | Best Times | Key Rules |
|----------|-------------|--------------|------------|-----------|
| Twitter | 200-280 chars | 70-100 chars | 8-9am, 12-1pm, 5-6pm EST | No links in replies, hook in first 5 words |
| LinkedIn | 1200-1500 chars | 100-300 chars | Tue-Thu 8-10am, 12pm | No links in body, line breaks, end with CTA |
| Instagram | 150-200 chars | 20-50 chars | 11am-1pm, 7-9pm | 5-10 hashtags at end, carousels preferred |

### 5. Follow Targeting System
**File:** `automation/follow_targeting.py`

Strategic follow/unfollow management with tracking.

```python
from automation.follow_targeting import FollowTargetingManager

manager = FollowTargetingManager()

# Add targets
manager.add_target("@spotgamma", reason="Great options analysis")

# Track follows
manager.track_follow("@spotgamma", source="@unusual_whales")

# Record followback status
manager.record_followback("@spotgamma", followed_back=True)

# Get unfollow candidates (no followback after 7 days)
candidates = manager.get_unfollow_candidates(days=7)

# Get stats
stats = manager.get_stats()
# Returns: total, pending, followed, followback_rate, etc.
```

### 6. Complete Automation System
**Folder:** `automation/`

Full-featured social media automation with these components:

#### 6.1 Data Schemas (`schemas.py`)
- **Enums:** Platform, Goal, HookType, Framework, Trigger, QueueStatus, ExperimentStatus
- **Dataclasses:** PostRecord, QueueItem, Experiment, WeeklySummary, ContentAnalysis
- **Configs:** PLATFORM_CONFIGS, GOAL_CONFIGS

#### 6.2 User Manager (`user_manager.py`)
Multi-user profile management with voice settings.

```python
from automation import UserManager

manager = UserManager()
manager.create_user(
    name="Justin Katz",
    twitter_handle="@justinkatz",
    niche="fintwit",
    goal="grow_followers"
)
manager.switch_user("Justin Katz")
profile = manager.get_active_profile()
```

#### 6.3 Content Analyzer (`content_analyzer.py`)
Deep analysis of social media content.

```python
from automation import ContentAnalyzer

analyzer = ContentAnalyzer()
analysis = analyzer.analyze(content, platform="twitter")

# Returns:
# - Hook type (question, contrarian, data, story, callout, bold_claim, how_to, list)
# - Framework (single, thread, quote_tweet, reply, carousel)
# - Triggers (fear, greed, curiosity, fomo, validation, urgency, exclusivity)
# - Specificity (vague, moderate, concrete)
# - Authority signals
# - Platform fit score
# - Strengths and weaknesses
```

#### 6.4 LLM Generator (`llm_generator.py`)
Claude API integration for content generation with platform-aware prompts.

```python
from automation import LLMGenerator

generator = LLMGenerator(api_key="...")
replies = generator.generate_replies(
    original_post={"content": "...", "author": "spotgamma"},
    platform="linkedin",  # Uses platform-specific rules
    num_replies=3
)
```

**Features:**
- Builds system prompt from user voice profile
- Incorporates benchmark patterns
- Includes platform-specific rules from adapters
- Falls back to template-based generation if API unavailable

#### 6.5 Queue Manager (`queue_manager.py`)
Content pipeline management: pending -> approved -> posted.

#### 6.6 Post Tracker (`post_tracker.py`)
Track post performance over time with engagement snapshots.

#### 6.7 Trending Scanner (`trending_scanner.py`)
Find trending content and reply opportunities.

#### 6.8 Feedback Loop (`feedback_loop.py`)
Weekly analysis and performance tracking.

#### 6.9 Voice Evolver (`voice_evolver.py`)
Iterative voice profile improvement based on performance data.

## Main CLI Commands (`automation_cli.py`)

### User Management
```bash
python automation_cli.py user create "Name" --twitter @handle --niche fintwit
python automation_cli.py user switch "Name"
python automation_cli.py user list
python automation_cli.py user profile
```

### Content Analysis
```bash
python automation_cli.py analyze --content "Your content" --platform twitter
python automation_cli.py analyze --content "Your content" --platform linkedin
```

### Content Drafting
```bash
python automation_cli.py draft --content "Post to reply to" --platform twitter
python automation_cli.py draft --content "Post to reply to" --platform linkedin --count 5
```

### Platform Information
```bash
python automation_cli.py platforms list
python automation_cli.py platforms show twitter
python automation_cli.py platforms show linkedin
```

### Scanning & Opportunities
```bash
python automation_cli.py scan --limit 10
python automation_cli.py opportunities --min-score 50
python automation_cli.py add-post --author @handle --content "..." --likes 500
```

### Queue Management
```bash
python automation_cli.py queue list --status pending
python automation_cli.py queue add --content "..." --platform twitter
python automation_cli.py queue approve <item_id>
python automation_cli.py queue post <item_id> --url "https://..."
```

### Post Tracking
```bash
python automation_cli.py log --content "..." --url "https://..." --platform twitter
python automation_cli.py history --limit 20
```

### Analytics & Reporting
```bash
python automation_cli.py report --week 0
python automation_cli.py trends --weeks 4
python automation_cli.py evolve
python automation_cli.py evolve --apply
```

### Follow Targeting
```bash
python automation_cli.py targets add @handle --reason "why"
python automation_cli.py targets remove @handle
python automation_cli.py targets list --status pending
python automation_cli.py targets track @handle --source @account
python automation_cli.py targets followback @handle --yes
python automation_cli.py targets followback @handle --no
python automation_cli.py targets check --days 7
python automation_cli.py targets unfollow @handle --reason "why"
python automation_cli.py targets suggest
python automation_cli.py targets analyze @handle
python automation_cli.py targets stats
python automation_cli.py targets followed --pending
python automation_cli.py targets settings --days 7
```

## Platform-Specific Rules

### Twitter
| Rule | Description |
|------|-------------|
| No links in replies | Kills algorithm visibility |
| Hook in first 5 words | Attention spans are short |
| One idea per tweet | Clarity wins |
| Quote tweet > retweet | Better for reach |
| Reply within 30 min | Speed matters for viral posts |
| Max 1-2 hashtags | Or none at all |

### LinkedIn
| Rule | Description |
|------|-------------|
| No links in post body | Kills reach by 50%+ |
| Links go in first comment | Algorithm hack |
| Line breaks every 1-2 sentences | Readability |
| First line is everything | Shows before "see more" |
| End with question/CTA | Drives engagement |
| Hashtags at very end | Max 3-5 |
| Best days: Tue-Thu | Avoid weekends |

### Instagram
| Rule | Description |
|------|-------------|
| First line = scroll stopper | Shows before "more" |
| Carousels > single images | 3x more reach |
| 5-10 hashtags at end | Discovery |
| Reply to comments in 1 hour | Algorithm boost |
| Reels for discovery | Posts for community |

## Hook Types Detected

| Hook Type | Description | Example Pattern |
|-----------|-------------|-----------------|
| Question | Opens with a question | "What if...?", "Why do...?" |
| Contrarian | Against popular opinion | "Unpopular opinion:", "Everyone is wrong about..." |
| Data | Leads with statistics | "87% of traders...", "$50M in..." |
| Story | Personal narrative | "I once...", "Last week..." |
| Callout | Direct address | "@username", "Hey founders" |
| Bold Claim | Strong statement | "This will change...", "The secret to..." |
| How-To | Educational | "How to...", "5 steps to..." |
| List | Numbered format | "1)", "Thread:", "5 things..." |

## Emotional Triggers Detected

| Trigger | Keywords |
|---------|----------|
| Fear | warning, danger, risk, mistake, avoid |
| Greed | profit, gain, money, wealth, rich |
| Curiosity | secret, hidden, revealed, discover |
| FOMO | limited, exclusive, last chance |
| Validation | you're right, smart people, top 1% |
| Urgency | now, today, immediately, deadline |
| Exclusivity | insider, members only, few know |

## Benchmark Data (FinTwit)

From `benchmarks/finance_twitter.json`:

- **Optimal length:** 26 words
- **Peak hours:** 7-8 PM, 4 PM EST
- **Peak days:** Tuesday, Friday, Thursday
- **Vocabulary:** Professional
- **Tone:** Measured
- **Emoji style:** Minimal

## Data Files

| File | Purpose |
|------|---------|
| `data/active_user.json` | Current active user |
| `data/targets.json` | Follow targeting data |
| `data/{user}/post_history.json` | User's post history |
| `data/{user}/experiments.json` | A/B test experiments |
| `data/{user}/trending_cache.json` | Cached trending posts |
| `data/{user}/weekly_summaries.json` | Weekly reports |
| `data/{user}/voice_evolution.json` | Voice version history |
| `profiles/{user}.json` | User voice profile |
| `queue/pending/*.json` | Pending content |
| `queue/approved/*.json` | Approved content |
| `queue/posted/*.json` | Posted content |

## Key Patterns Learned

1. **Benchmark-driven optimization** - All content generation targets metrics from actual top performers
2. **Voice matching** - Replies and posts match user's established voice profile
3. **Iterative improvement** - Feedback loop identifies what works, voice evolver applies learnings
4. **Multi-platform awareness** - Each platform has specific optimization rules via adapters
5. **Goal alignment** - Content strategy adapts based on user goals
6. **Follow strategy** - Track followbacks, identify unfollow candidates systematically

## Architecture Highlights

- **14 CLI command groups** in unified `automation_cli.py`
- **3 platform adapters** with extensible base class
- **Fallback generation** when Claude API unavailable
- **Per-user data isolation** in `data/{user}/` folders
- **JSON-based persistence** for portability

---

Built with Claude Code
