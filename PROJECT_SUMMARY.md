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
│   │   └── voice_evolver.py  # Iterative voice improvement
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
│   ├── data/                 # Runtime data (post history, etc.)
│   ├── queue/                # Content queue pipeline
│   │   ├── pending/
│   │   ├── approved/
│   │   └── posted/
│   ├── niches/               # Niche configuration templates
│   │
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

### 4. Complete Automation System
**Folder:** `automation/`

Full-featured social media automation with these components:

#### 4.1 Data Schemas (`schemas.py`)
- **Enums:** Platform, Goal, HookType, Framework, Trigger, QueueStatus, ExperimentStatus
- **Dataclasses:** PostRecord, QueueItem, Experiment, WeeklySummary, ContentAnalysis
- **Configs:** PLATFORM_CONFIGS, GOAL_CONFIGS

#### 4.2 User Manager (`user_manager.py`)
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

**Profile Structure:**
- Platform handles (Twitter, LinkedIn, Instagram)
- Voice settings (tone, formality, vocabulary, emoji style)
- Style settings (sentence length, punctuation, capitalization)
- Platform-specific preferences
- Proven patterns
- Baseline metrics
- Milestones

#### 4.3 Content Analyzer (`content_analyzer.py`)
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

#### 4.4 LLM Generator (`llm_generator.py`)
Claude API integration for content generation.

```python
from automation import LLMGenerator

generator = LLMGenerator(api_key="...")
replies = generator.generate_replies(
    post_content="Market update...",
    post_author="spotgamma",
    count=3
)
```

**Features:**
- Builds system prompt from user voice profile
- Incorporates benchmark patterns
- Falls back to template-based generation if API unavailable
- Supports: replies, posts, content adaptation

#### 4.5 Queue Manager (`queue_manager.py`)
Content pipeline management: pending -> approved -> posted.

```python
from automation import QueueManager

queue = QueueManager()
item = queue.add_to_queue(
    content="My reply...",
    platform="twitter",
    reply_to_url="https://twitter.com/...",
    analysis=analysis_dict,
    scores={"voice_match": 0.85, "engagement_prediction": 0.72}
)
queue.approve(item.id)
queue.mark_posted(item.id, post_url="https://twitter.com/...")
```

#### 4.6 Post Tracker (`post_tracker.py`)
Track post performance over time.

```python
from automation import PostTracker

tracker = PostTracker()
record = tracker.log_post(
    content="My post...",
    url="https://twitter.com/...",
    platform="twitter"
)
tracker.update_engagement(record.id, {"likes": 50, "retweets": 10}, "24h")

# Analysis
top_posts = tracker.get_top_performing(limit=10)
by_technique = tracker.get_performance_by_technique()
by_hook = tracker.get_performance_by_hook()
baseline = tracker.calculate_baseline()
```

#### 4.7 Trending Scanner (`trending_scanner.py`)
Find trending content and reply opportunities.

```python
from automation import TrendingScanner

scanner = TrendingScanner()
watchlist = scanner.get_watchlist()  # From profile + niche config
keywords = scanner.get_keywords()

# Add posts from external scrape
scanner.add_posts_from_scrape(posts_data, platform="twitter")

# Get opportunities
opportunities = scanner.get_opportunities(min_score=50, limit=10)
scanner.mark_replied(post_id, reply_url="...")
```

#### 4.8 Feedback Loop (`feedback_loop.py`)
Weekly analysis and performance tracking.

```python
from automation import FeedbackLoop

loop = FeedbackLoop()
summary = loop.generate_weekly_report()

# Returns WeeklySummary with:
# - Posts count, total engagement, avg engagement rate
# - Top performing posts, successful techniques, best hooks
# - Worst performing posts, failed techniques
# - Comparison to benchmark
# - Gaps identified
# - Recommendations

trends = loop.get_trend_analysis(weeks=4)
insights = loop.get_technique_insights()
```

#### 4.9 Voice Evolver (`voice_evolver.py`)
Iterative voice profile improvement.

```python
from automation import VoiceEvolver

evolver = VoiceEvolver()
patterns = evolver.analyze_voice_patterns()  # From top posts
suggestions = evolver.suggest_voice_updates()

# Apply selected suggestions
result = evolver.apply_evolution(suggestions_to_apply=[0, 1, 2])

# Track versions
history = evolver.get_evolution_history()
evolver.compare_versions(version1=1, version2=2)
```

## Platform-Specific Optimization

### Twitter
- Reply length: 70-100 chars
- Post length: 200-280 chars
- Reply speed: < 30 minutes
- Hooks first
- Quote tweets preferred
- Strategy: Fast, short, insight not praise

### LinkedIn
- Post length: 1200-1500 chars
- Use line breaks
- First line critical
- Personal stories win
- Avoid external links
- Strategy: Depth > speed, 3-5 sentences, ask questions

### Instagram
- Caption length: 150-2200 chars
- Carousels preferred
- First slide hook
- Hashtags at end (5-15)
- Strategy: Very short, genuine, relationship-focused

## Goal-Based Optimization

### Grow Followers
- Optimize for: shares
- Metrics: retweets, shares, follower growth
- Content focus: Shareable insights, contrarian takes, data visualizations
- Priority: retweets > quotes > replies

### Drive Traffic
- Optimize for: clicks
- Metrics: link clicks, profile visits, website traffic
- Content focus: Curiosity gaps, clear CTAs, value teasers
- Priority: clicks > saves > shares

### Build Authority
- Optimize for: thoughtful engagement
- Metrics: quality replies, mentions, quote tweets
- Content focus: Deep analysis, original research, unique perspectives
- Priority: quality replies > saves > quotes

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

## CLI Commands Available

### Benchmark CLI (`benchmark_cli.py`)
```bash
python benchmark_cli.py analyze @account   # Analyze account
python benchmark_cli.py compare profile.json  # Compare to benchmark
python benchmark_cli.py show               # Show benchmark data
python benchmark_cli.py add-viral          # Add viral post
```

### FinTwit CLI (`fintwit_cli.py`)
```bash
python fintwit_cli.py scan              # Find trending posts
python fintwit_cli.py opportunities     # Show reply opportunities
python fintwit_cli.py draft @author     # Draft replies
python fintwit_cli.py brief             # Today's engagement brief
python fintwit_cli.py analyze           # Analyze content
```

## Data Files

| File | Purpose |
|------|---------|
| `data/active_user.json` | Current active user |
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
4. **Multi-platform awareness** - Each platform has specific optimization rules
5. **Goal alignment** - Content strategy adapts based on user goals

## Next Steps (Planned)

1. Create niche templates (fintwit.json, crypto.json, tech.json)
2. Build main CLI with unified commands
3. Add scheduling system
4. Implement A/B testing workflow
5. Add image/media analysis

---

Built with Claude Code
