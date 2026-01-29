"""
LinkedIn Benchmark Manager - Per-user benchmark tracking and analysis

Tracks top performers in user's niche and extracts patterns for content generation.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

from .schemas import generate_id, now_iso, load_json, save_json
from .user_manager import get_active_profile, UserManager

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
BENCHMARKS_DIR = DATA_DIR / "benchmarks"


@dataclass
class BenchmarkPost:
    """A benchmark post from a top performer."""
    id: str
    author: str
    platform: str
    content: str
    url: str = ""
    posted_at: str = ""

    # Engagement
    likes: int = 0
    comments: int = 0
    shares: int = 0

    # Analysis
    word_count: int = 0
    hook_type: str = ""
    has_line_breaks: bool = False
    has_emoji: bool = False
    has_hashtags: bool = False
    topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'BenchmarkPost':
        return cls(**data)


@dataclass
class BenchmarkAccount:
    """A tracked benchmark account."""
    handle: str
    platform: str
    name: str = ""
    bio: str = ""
    followers: int = 0

    # Tracking
    added_at: str = ""
    last_scanned: str = ""

    # Stats
    posts_analyzed: int = 0
    avg_engagement: float = 0.0
    top_posts: List[Dict] = field(default_factory=list)

    # Patterns extracted
    patterns: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'BenchmarkAccount':
        return cls(**data)


@dataclass
class UserBenchmark:
    """Benchmark data for a specific user."""
    user: str
    niche: str
    niche_topics: List[str]
    platform: str

    # Accounts
    accounts: List[BenchmarkAccount] = field(default_factory=list)

    # Aggregated patterns
    patterns: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: str = ""
    updated_at: str = ""
    total_posts_analyzed: int = 0

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['accounts'] = [a if isinstance(a, dict) else a.to_dict() for a in self.accounts]
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserBenchmark':
        accounts = [
            BenchmarkAccount.from_dict(a) if isinstance(a, dict) else a
            for a in data.get('accounts', [])
        ]
        data['accounts'] = accounts
        return cls(**data)


class LinkedInBenchmarkManager:
    """
    Manages LinkedIn benchmarks per user.

    Each user has their own benchmark data based on their niche and
    the accounts they choose to track.
    """

    def __init__(self, user_name: str = None):
        """
        Initialize benchmark manager.

        Args:
            user_name: User name (uses active user if None)
        """
        BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

        self.user_manager = UserManager()

        if user_name:
            self.profile = self.user_manager.get_profile(user_name)
        else:
            self.profile = get_active_profile()

        self.user_name = self.profile.get("name") if self.profile else None
        self._benchmark: Optional[UserBenchmark] = None

        if self.user_name:
            self._load_benchmark()

    def _get_benchmark_path(self) -> Path:
        """Get path to user's LinkedIn benchmark file."""
        filename = self.user_name.lower().replace(' ', '_')
        return BENCHMARKS_DIR / f"{filename}_linkedin.json"

    def _load_benchmark(self):
        """Load user's benchmark data."""
        path = self._get_benchmark_path()
        if path.exists():
            data = load_json(str(path))
            self._benchmark = UserBenchmark.from_dict(data)
        else:
            # Initialize new benchmark
            self._benchmark = UserBenchmark(
                user=self.user_name,
                niche=self.profile.get("niche", ""),
                niche_topics=self.profile.get("niche_topics", []),
                platform="linkedin",
                created_at=now_iso(),
                updated_at=now_iso(),
            )
            self._save_benchmark()

    def _save_benchmark(self):
        """Save user's benchmark data."""
        if not self._benchmark:
            return
        self._benchmark.updated_at = now_iso()
        path = self._get_benchmark_path()
        save_json(str(path), self._benchmark.to_dict())

    @property
    def benchmark(self) -> Optional[UserBenchmark]:
        """Get current benchmark data."""
        return self._benchmark

    def add_account(self, handle: str, name: str = "") -> Dict[str, Any]:
        """
        Add a benchmark account to track.

        Args:
            handle: LinkedIn handle/username
            name: Display name (optional)

        Returns:
            Result dict
        """
        if not self._benchmark:
            return {"error": "No active user"}

        clean_handle = handle.lstrip('@').strip()

        # Check if already tracked
        existing = [a for a in self._benchmark.accounts if a.handle == clean_handle]
        if existing:
            return {"error": f"@{clean_handle} already tracked"}

        # Add new account
        account = BenchmarkAccount(
            handle=clean_handle,
            platform="linkedin",
            name=name or clean_handle,
            added_at=now_iso(),
        )

        self._benchmark.accounts.append(account)

        # Also add to user profile
        self.user_manager.add_benchmark_account(
            self.user_name,
            clean_handle,
            platform="linkedin"
        )

        self._save_benchmark()

        return {
            "status": "success",
            "added": clean_handle,
            "total_accounts": len(self._benchmark.accounts),
        }

    def remove_account(self, handle: str) -> Dict[str, Any]:
        """Remove a benchmark account."""
        if not self._benchmark:
            return {"error": "No active user"}

        clean_handle = handle.lstrip('@').strip()

        # Find and remove
        original_count = len(self._benchmark.accounts)
        self._benchmark.accounts = [
            a for a in self._benchmark.accounts
            if a.handle != clean_handle
        ]

        if len(self._benchmark.accounts) == original_count:
            return {"error": f"@{clean_handle} not found"}

        # Also remove from user profile
        self.user_manager.remove_benchmark_account(
            self.user_name,
            clean_handle,
            platform="linkedin"
        )

        self._save_benchmark()

        return {
            "status": "success",
            "removed": clean_handle,
            "remaining": len(self._benchmark.accounts),
        }

    def list_accounts(self) -> List[Dict[str, Any]]:
        """List all tracked benchmark accounts."""
        if not self._benchmark:
            return []

        return [
            {
                "handle": a.handle,
                "name": a.name,
                "followers": a.followers,
                "posts_analyzed": a.posts_analyzed,
                "avg_engagement": a.avg_engagement,
                "last_scanned": a.last_scanned,
            }
            for a in self._benchmark.accounts
        ]

    def add_post(self, post: BenchmarkPost) -> Dict[str, Any]:
        """
        Add a post to benchmark data (manual entry).

        Args:
            post: BenchmarkPost object

        Returns:
            Result dict
        """
        if not self._benchmark:
            return {"error": "No active user"}

        # Find the account
        account = None
        for a in self._benchmark.accounts:
            if a.handle == post.author:
                account = a
                break

        if not account:
            # Auto-add the account
            self.add_account(post.author)
            for a in self._benchmark.accounts:
                if a.handle == post.author:
                    account = a
                    break

        if not account:
            return {"error": f"Could not add account @{post.author}"}

        # Analyze the post
        analyzed_post = self._analyze_post(post)

        # Add to account's top posts (keep top 20)
        account.top_posts.append(analyzed_post.to_dict())
        account.top_posts = sorted(
            account.top_posts,
            key=lambda p: p.get('likes', 0) + p.get('comments', 0) * 2,
            reverse=True
        )[:20]

        account.posts_analyzed += 1
        account.last_scanned = now_iso()

        # Update aggregated patterns
        self._update_patterns()

        self._save_benchmark()

        return {
            "status": "success",
            "post_id": analyzed_post.id,
            "author": post.author,
            "hook_type": analyzed_post.hook_type,
        }

    def _analyze_post(self, post: BenchmarkPost) -> BenchmarkPost:
        """Analyze a post and extract patterns."""
        content = post.content

        # Word count
        post.word_count = len(content.split())

        # Line breaks
        post.has_line_breaks = '\n' in content

        # Emoji detection
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+"
        )
        post.has_emoji = bool(emoji_pattern.search(content))

        # Hashtags
        post.has_hashtags = '#' in content

        # Hook type detection
        first_line = content.split('\n')[0].strip()
        post.hook_type = self._detect_hook_type(first_line)

        # Topic detection
        post.topics = self._extract_topics(content)

        # Generate ID if not present
        if not post.id:
            post.id = generate_id()

        return post

    def _detect_hook_type(self, first_line: str) -> str:
        """Detect the hook type from the first line."""
        first_lower = first_line.lower()

        # Question hook
        if '?' in first_line:
            return "question"

        # Number/data hook
        if re.search(r'^\d|%|\$', first_line):
            return "data"

        # Personal story hook
        if first_lower.startswith(('i ', "i've", "i'm", 'my ', 'when i')):
            return "personal_story"

        # Bold claim
        if first_lower.startswith(('the ', 'this ', 'here\'s', "here's")):
            return "bold_claim"

        # Contrarian
        contrarian_signals = ['unpopular', 'controversial', 'nobody', 'everyone', 'stop', "don't"]
        if any(s in first_lower for s in contrarian_signals):
            return "contrarian"

        # List hook
        if re.search(r'^\d+\s*(things?|ways?|tips?|lessons?|reasons?)', first_lower):
            return "list"

        # How-to
        if first_lower.startswith(('how to', 'how i')):
            return "how_to"

        return "statement"

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content based on user's niche."""
        if not self.profile:
            return []

        niche_topics = self.profile.get("niche_topics", [])
        keywords = self.profile.get("keywords", [])

        all_topics = niche_topics + keywords
        content_lower = content.lower()

        found = []
        for topic in all_topics:
            if topic.lower() in content_lower:
                found.append(topic)

        return found[:5]  # Max 5 topics

    def _update_patterns(self):
        """Update aggregated patterns from all accounts."""
        if not self._benchmark:
            return

        all_posts = []
        for account in self._benchmark.accounts:
            all_posts.extend(account.top_posts)

        if not all_posts:
            return

        # Aggregate stats
        patterns = {
            "total_posts": len(all_posts),
            "avg_word_count": 0,
            "avg_engagement": 0,
            "hook_types": {},
            "line_break_usage": 0,
            "emoji_usage": 0,
            "hashtag_usage": 0,
            "top_topics": {},
            "optimal_length": {
                "min": 0,
                "max": 0,
                "avg": 0,
            },
            "best_performing": [],
        }

        word_counts = []
        engagements = []
        line_break_count = 0
        emoji_count = 0
        hashtag_count = 0

        for post in all_posts:
            # Word counts
            wc = post.get('word_count', 0)
            if wc > 0:
                word_counts.append(wc)

            # Engagement
            eng = post.get('likes', 0) + post.get('comments', 0) * 2 + post.get('shares', 0) * 3
            engagements.append(eng)

            # Hook types
            hook = post.get('hook_type', 'unknown')
            patterns["hook_types"][hook] = patterns["hook_types"].get(hook, 0) + 1

            # Features
            if post.get('has_line_breaks'):
                line_break_count += 1
            if post.get('has_emoji'):
                emoji_count += 1
            if post.get('has_hashtags'):
                hashtag_count += 1

            # Topics
            for topic in post.get('topics', []):
                patterns["top_topics"][topic] = patterns["top_topics"].get(topic, 0) + 1

        # Calculate averages
        if word_counts:
            patterns["avg_word_count"] = round(sum(word_counts) / len(word_counts))
            patterns["optimal_length"]["min"] = min(word_counts)
            patterns["optimal_length"]["max"] = max(word_counts)
            patterns["optimal_length"]["avg"] = patterns["avg_word_count"]

        if engagements:
            patterns["avg_engagement"] = round(sum(engagements) / len(engagements))

        n = len(all_posts)
        if n > 0:
            patterns["line_break_usage"] = round(line_break_count / n * 100)
            patterns["emoji_usage"] = round(emoji_count / n * 100)
            patterns["hashtag_usage"] = round(hashtag_count / n * 100)

        # Sort hook types
        patterns["hook_types"] = dict(
            sorted(patterns["hook_types"].items(), key=lambda x: x[1], reverse=True)
        )

        # Sort topics
        patterns["top_topics"] = dict(
            sorted(patterns["top_topics"].items(), key=lambda x: x[1], reverse=True)[:10]
        )

        # Best performing posts
        sorted_posts = sorted(all_posts, key=lambda p: p.get('likes', 0), reverse=True)
        patterns["best_performing"] = sorted_posts[:5]

        self._benchmark.patterns = patterns
        self._benchmark.total_posts_analyzed = len(all_posts)

    def get_patterns(self) -> Dict[str, Any]:
        """Get aggregated patterns for content generation."""
        if not self._benchmark:
            return {}

        return self._benchmark.patterns

    def get_generation_context(self) -> Dict[str, Any]:
        """
        Get context for LLM content generation.

        Returns a dict optimized for use in prompts.
        """
        if not self._benchmark or not self._benchmark.patterns:
            return {
                "has_data": False,
                "message": "No benchmark data yet. Add posts with: benchmark add-post"
            }

        patterns = self._benchmark.patterns

        # Get example posts
        examples = []
        for post in patterns.get("best_performing", [])[:3]:
            examples.append({
                "author": post.get("author", ""),
                "content": post.get("content", "")[:500],
                "engagement": post.get("likes", 0),
                "hook_type": post.get("hook_type", ""),
            })

        return {
            "has_data": True,
            "niche": self._benchmark.niche,
            "niche_topics": self._benchmark.niche_topics,
            "optimal_length": patterns.get("optimal_length", {}),
            "effective_hooks": list(patterns.get("hook_types", {}).keys())[:5],
            "top_topics": list(patterns.get("top_topics", {}).keys())[:5],
            "style_notes": {
                "use_line_breaks": patterns.get("line_break_usage", 0) > 50,
                "use_emoji": patterns.get("emoji_usage", 0) > 30,
                "use_hashtags": patterns.get("hashtag_usage", 0) > 30,
            },
            "examples": examples,
            "accounts_tracked": len(self._benchmark.accounts),
            "total_posts_analyzed": self._benchmark.total_posts_analyzed,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get benchmark statistics."""
        if not self._benchmark:
            return {"error": "No active user"}

        return {
            "user": self._benchmark.user,
            "niche": self._benchmark.niche,
            "niche_topics": self._benchmark.niche_topics,
            "accounts_tracked": len(self._benchmark.accounts),
            "total_posts_analyzed": self._benchmark.total_posts_analyzed,
            "patterns": self._benchmark.patterns,
            "updated_at": self._benchmark.updated_at,
        }


# =============================================================================
# DEFAULT LINKEDIN ACCOUNTS BY NICHE
# =============================================================================

LINKEDIN_NICHE_DEFAULTS = {
    "fintwit": {
        "accounts": [
            "peraborstrom",
            "kaborstrom",
            "volsignals",
        ],
        "topics": [
            "options",
            "dealer positioning",
            "market structure",
            "institutional flow",
            "volatility",
            "gamma",
        ],
    },
    "crypto": {
        "accounts": [],
        "topics": [
            "bitcoin",
            "ethereum",
            "defi",
            "web3",
            "blockchain",
        ],
    },
    "tech": {
        "accounts": [],
        "topics": [
            "AI",
            "machine learning",
            "startups",
            "product management",
            "engineering",
        ],
    },
}


def get_niche_defaults(niche: str) -> Dict[str, Any]:
    """Get default accounts and topics for a niche."""
    return LINKEDIN_NICHE_DEFAULTS.get(niche, {"accounts": [], "topics": []})


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_linkedin_benchmark(user_name: str = None) -> LinkedInBenchmarkManager:
    """Get LinkedIn benchmark manager for a user."""
    return LinkedInBenchmarkManager(user_name)


def get_generation_context(user_name: str = None) -> Dict[str, Any]:
    """Get LinkedIn benchmark context for content generation."""
    manager = LinkedInBenchmarkManager(user_name)
    return manager.get_generation_context()
