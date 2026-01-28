"""
Database Schemas and Data Models

Defines all data structures used in the automation system.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json


# =============================================================================
# ENUMS
# =============================================================================

class Platform(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"


class Goal(Enum):
    GROW_FOLLOWERS = "grow_followers"
    DRIVE_TRAFFIC = "drive_traffic"
    BUILD_AUTHORITY = "build_authority"


class HookType(Enum):
    QUESTION = "question"
    CONTRARIAN = "contrarian"
    DATA = "data"
    STORY = "story"
    CALLOUT = "callout"
    BOLD_CLAIM = "bold_claim"
    HOW_TO = "how_to"
    LIST = "list"


class Framework(Enum):
    SINGLE = "single"
    THREAD = "thread"
    QUOTE_TWEET = "quote_tweet"
    REPLY = "reply"
    CAROUSEL = "carousel"


class Trigger(Enum):
    FEAR = "fear"
    GREED = "greed"
    CURIOSITY = "curiosity"
    FOMO = "fomo"
    VALIDATION = "validation"
    URGENCY = "urgency"
    EXCLUSIVITY = "exclusivity"


class QueueStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    POSTED = "posted"
    REJECTED = "rejected"


class ExperimentStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# =============================================================================
# USER PROFILE SCHEMA
# =============================================================================

USER_PROFILE_SCHEMA = {
    "name": str,
    "username": str,
    "created_at": str,
    "platform_handles": {
        "twitter": str,
        "linkedin": str,
        "instagram": str,
    },
    "niche": str,
    "niche_config": str,  # Path to niche config file
    "goal": str,  # Goal enum value
    "watchlist": List[str],  # Accounts to monitor
    "keywords": List[str],  # Niche keywords
    "voice": {
        "tone": str,
        "formality": str,
        "vocabulary": str,
        "emoji_style": str,
        "signature_phrases": List[str],
        "common_openers": List[str],
        "avoided_phrases": List[str],
    },
    "style": {
        "sentence_length": str,
        "punctuation": str,
        "capitalization": str,
    },
    "platform_preferences": {
        "twitter": {
            "reply_length": int,
            "post_length": int,
            "reply_speed_minutes": int,
        },
        "linkedin": {
            "post_length": int,
            "use_line_breaks": bool,
        },
        "instagram": {
            "hashtag_count": int,
            "caption_length": int,
        },
    },
    "proven_patterns": List[Dict],  # Patterns that worked for this user
    "baseline_metrics": {
        "followers": int,
        "avg_engagement_rate": float,
        "captured_at": str,
    },
    "milestones": List[Dict],
}


# =============================================================================
# POST HISTORY SCHEMA
# =============================================================================

@dataclass
class PostRecord:
    """Individual post tracking record."""
    id: str
    user: str
    platform: str
    content: str
    url: str
    posted_at: str

    # Content analysis
    hook_type: str = ""
    framework: str = ""
    triggers: List[str] = field(default_factory=list)
    specificity: str = ""  # vague, moderate, concrete
    word_count: int = 0

    # Techniques used
    techniques: List[str] = field(default_factory=list)

    # Engagement snapshots
    initial_engagement: Dict[str, int] = field(default_factory=dict)
    engagement_24h: Dict[str, int] = field(default_factory=dict)
    engagement_48h: Dict[str, int] = field(default_factory=dict)
    engagement_7d: Dict[str, int] = field(default_factory=dict)

    # Performance
    engagement_velocity: float = 0.0  # Engagement per hour
    performance_score: float = 0.0  # Compared to user's average

    # Learning
    what_worked: List[str] = field(default_factory=list)
    what_failed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PostRecord':
        return cls(**data)


POST_HISTORY_SCHEMA = {
    "user": str,
    "posts": List[PostRecord],
    "weekly_summaries": List[Dict],
    "total_posts": int,
    "avg_engagement_rate": float,
    "best_performing": List[str],  # Post IDs
    "worst_performing": List[str],  # Post IDs
    "updated_at": str,
}


# =============================================================================
# QUEUE ITEM SCHEMA
# =============================================================================

@dataclass
class QueueItem:
    """Content queue item."""
    id: str
    user: str
    platform: str
    content: str
    status: str  # QueueStatus value
    created_at: str

    # Context
    reply_to_url: Optional[str] = None
    reply_to_author: Optional[str] = None
    reply_to_content: Optional[str] = None

    # Analysis
    hook_type: str = ""
    framework: str = ""
    triggers: List[str] = field(default_factory=list)
    techniques: List[str] = field(default_factory=list)

    # Scores
    voice_match: float = 0.0
    engagement_prediction: float = 0.0
    combined_score: float = 0.0

    # Explanation
    why: str = ""

    # Tracking
    approved_at: Optional[str] = None
    posted_at: Optional[str] = None
    post_url: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'QueueItem':
        return cls(**data)


# =============================================================================
# EXPERIMENT SCHEMA
# =============================================================================

@dataclass
class Experiment:
    """A/B testing experiment."""
    id: str
    user: str
    hypothesis: str
    variable: str  # What we're testing (hook_type, length, timing, etc.)
    control: str  # Control value
    variant: str  # Test value

    status: str = "active"  # ExperimentStatus value
    started_at: str = ""
    ended_at: Optional[str] = None

    # Results
    control_posts: List[str] = field(default_factory=list)
    variant_posts: List[str] = field(default_factory=list)
    control_avg_engagement: float = 0.0
    variant_avg_engagement: float = 0.0

    winner: Optional[str] = None  # "control" or "variant"
    confidence: float = 0.0
    conclusion: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Experiment':
        return cls(**data)


# =============================================================================
# WEEKLY SUMMARY SCHEMA
# =============================================================================

@dataclass
class WeeklySummary:
    """Weekly performance summary."""
    user: str
    week_start: str
    week_end: str

    # Metrics
    posts_count: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    follower_change: int = 0

    # What worked
    top_performing_posts: List[str] = field(default_factory=list)
    successful_techniques: List[Dict] = field(default_factory=list)
    best_hook_types: List[str] = field(default_factory=list)
    best_posting_times: List[int] = field(default_factory=list)

    # What didn't work
    worst_performing_posts: List[str] = field(default_factory=list)
    failed_techniques: List[Dict] = field(default_factory=list)

    # Comparison to benchmark
    vs_benchmark: Dict = field(default_factory=dict)
    gaps_identified: List[str] = field(default_factory=list)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    next_week_focus: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'WeeklySummary':
        return cls(**data)


# =============================================================================
# NICHE CONFIG SCHEMA
# =============================================================================

NICHE_CONFIG_SCHEMA = {
    "name": str,
    "description": str,
    "platforms": List[str],

    # Monitoring
    "default_watchlist": List[str],
    "keywords": List[str],
    "hashtags": List[str],

    # Benchmarks
    "benchmark_name": str,  # Reference to benchmarks/[name].json

    # Content patterns
    "successful_hooks": List[Dict],
    "optimal_length": {
        "twitter_reply": int,
        "twitter_post": int,
        "linkedin": int,
        "instagram": int,
    },
    "best_posting_times": {
        "twitter": List[int],
        "linkedin": List[int],
        "instagram": List[int],
    },
    "tone": str,
    "vocabulary": str,

    # Platform-specific
    "twitter_tips": List[str],
    "linkedin_tips": List[str],
    "instagram_tips": List[str],
}


# =============================================================================
# PLATFORM OPTIMIZATION CONFIGS
# =============================================================================

PLATFORM_CONFIGS = {
    "twitter": {
        "reply_length_chars": (70, 100),
        "post_length_chars": (200, 280),
        "reply_speed_minutes": 30,
        "hooks_first": True,
        "quote_tweets_preferred": True,
        "strategy": "Fast, short, insight not praise",
    },
    "linkedin": {
        "post_length_chars": (1200, 1500),
        "use_line_breaks": True,
        "first_line_critical": True,
        "personal_stories_win": True,
        "avoid_external_links": True,
        "strategy": "Depth > speed, 3-5 sentences, ask questions",
    },
    "instagram": {
        "caption_length_chars": (150, 2200),
        "carousels_preferred": True,
        "first_slide_hook": True,
        "hashtags_at_end": True,
        "hashtag_count": (5, 15),
        "strategy": "Very short, genuine, relationship-focused",
    },
}


# =============================================================================
# GOAL OPTIMIZATION CONFIGS
# =============================================================================

GOAL_CONFIGS = {
    "grow_followers": {
        "optimize_for": "shares",
        "metrics": ["retweets", "shares", "follower_growth"],
        "content_focus": "Shareable insights, contrarian takes, data visualizations",
        "engagement_priority": ["retweets", "quotes", "replies"],
    },
    "drive_traffic": {
        "optimize_for": "clicks",
        "metrics": ["link_clicks", "profile_visits", "website_traffic"],
        "content_focus": "Curiosity gaps, clear CTAs, value teasers",
        "engagement_priority": ["clicks", "saves", "shares"],
    },
    "build_authority": {
        "optimize_for": "thoughtful_engagement",
        "metrics": ["quality_replies", "mentions", "quote_tweets"],
        "content_focus": "Deep analysis, original research, unique perspectives",
        "engagement_priority": ["quality_replies", "saves", "quotes"],
    },
}


# =============================================================================
# CONTENT ANALYSIS SCHEMA
# =============================================================================

@dataclass
class ContentAnalysis:
    """Deep content analysis result."""
    content: str
    platform: str

    # Structure
    word_count: int = 0
    char_count: int = 0
    sentence_count: int = 0
    line_count: int = 0

    # Hook analysis
    hook_type: str = ""
    hook_text: str = ""
    hook_strength: float = 0.0

    # Framework
    framework: str = ""

    # Triggers
    triggers: List[str] = field(default_factory=list)
    trigger_strength: float = 0.0

    # Specificity
    specificity: str = ""  # vague, moderate, concrete
    has_numbers: bool = False
    has_data: bool = False
    has_examples: bool = False

    # Authority signals
    authority_signals: List[str] = field(default_factory=list)

    # Platform fit
    platform_score: float = 0.0
    platform_issues: List[str] = field(default_factory=list)

    # Overall
    techniques: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_id() -> str:
    """Generate a unique ID."""
    import uuid
    return str(uuid.uuid4())[:8]


def now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.now().isoformat()


def load_json(path: str) -> Dict:
    """Load JSON file."""
    from pathlib import Path
    p = Path(path)
    if p.exists():
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_json(path: str, data: Dict):
    """Save JSON file."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
