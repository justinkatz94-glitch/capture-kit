"""
Trending Scanner - Find trending content in your niche

Scans watchlist accounts and keywords for engagement opportunities.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .schemas import load_json, save_json, now_iso
from .user_manager import get_active_user, get_active_profile

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
NICHES_DIR = BASE_DIR / "niches"


@dataclass
class TrendingPost:
    """A trending post found by the scanner."""
    id: str
    author: str
    content: str
    url: str
    platform: str
    posted_at: str

    # Engagement
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0

    # Analysis
    topics: List[str] = None
    reply_opportunity_score: float = 0.0
    why_reply: str = ""

    # Tracking
    found_at: str = ""
    replied: bool = False
    reply_url: str = ""

    def __post_init__(self):
        if self.topics is None:
            self.topics = []
        if not self.found_at:
            self.found_at = now_iso()

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'TrendingPost':
        return cls(**data)

    @property
    def total_engagement(self) -> int:
        return self.likes + self.retweets + self.replies + self.quotes


class TrendingScanner:
    """
    Scans for trending content and reply opportunities.
    """

    def __init__(self):
        """Initialize scanner."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, user: str) -> Path:
        """Get the trending cache file path for a user."""
        user_dir = DATA_DIR / user.lower().replace(' ', '_')
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "trending_cache.json"

    def _load_cache(self, user: str) -> Dict[str, Any]:
        """Load trending cache for a user."""
        path = self._get_cache_path(user)
        if path.exists():
            return load_json(str(path))
        return {
            "user": user,
            "posts": [],
            "last_scan": "",
            "scan_count": 0,
        }

    def _save_cache(self, user: str, cache: Dict[str, Any]):
        """Save trending cache for a user."""
        path = self._get_cache_path(user)
        save_json(str(path), cache)

    def _load_niche_config(self, niche: str) -> Dict[str, Any]:
        """Load niche configuration."""
        if not niche:
            return {}
        niche_path = NICHES_DIR / f"{niche.lower()}.json"
        if niche_path.exists():
            return load_json(str(niche_path))
        return {}

    def get_watchlist(self) -> List[str]:
        """Get the current user's watchlist."""
        profile = get_active_profile()
        if not profile:
            return []

        watchlist = profile.get("watchlist", [])

        # Also load from niche config
        niche = profile.get("niche", "")
        niche_config = self._load_niche_config(niche)
        niche_watchlist = niche_config.get("default_watchlist", [])

        # Combine and dedupe
        combined = list(set(watchlist + niche_watchlist))
        return combined

    def get_keywords(self) -> List[str]:
        """Get the current user's keywords."""
        profile = get_active_profile()
        if not profile:
            return []

        keywords = profile.get("keywords", [])

        # Also load from niche config
        niche = profile.get("niche", "")
        niche_config = self._load_niche_config(niche)
        niche_keywords = niche_config.get("keywords", [])

        # Combine and dedupe
        combined = list(set(keywords + niche_keywords))
        return combined

    def scan(self, platform: str = "twitter", limit: int = 20) -> List[TrendingPost]:
        """
        Scan for trending posts.

        Note: This method provides a framework for scanning. In production,
        you would integrate with actual APIs (Twitter API, scraper, etc.)

        Args:
            platform: Platform to scan
            limit: Maximum posts to return

        Returns:
            List of TrendingPost objects
        """
        user = get_active_user()
        if not user:
            return []

        watchlist = self.get_watchlist()
        keywords = self.get_keywords()

        # Update cache metadata
        cache = self._load_cache(user)
        cache["last_scan"] = now_iso()
        cache["scan_count"] = cache.get("scan_count", 0) + 1

        # In a real implementation, you would:
        # 1. Call Twitter API or use scraper to fetch recent posts from watchlist
        # 2. Filter by keywords
        # 3. Score for reply opportunity

        # For now, return cached posts
        posts = [TrendingPost.from_dict(p) for p in cache.get("posts", [])]

        # Filter to platform and non-replied
        posts = [p for p in posts if p.platform == platform and not p.replied]

        # Sort by opportunity score
        posts.sort(key=lambda x: x.reply_opportunity_score, reverse=True)

        self._save_cache(user, cache)

        return posts[:limit]

    def add_post(self, post: TrendingPost) -> Dict[str, Any]:
        """
        Add a post to the trending cache.

        Use this when you've scraped or found a post externally.
        """
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        cache = self._load_cache(user)

        # Check for duplicate
        existing_ids = [p.get("id") for p in cache.get("posts", [])]
        if post.id in existing_ids:
            return {"status": "duplicate", "post_id": post.id}

        # Score the post
        post.reply_opportunity_score = self._score_opportunity(post)

        cache["posts"].append(post.to_dict())
        self._save_cache(user, cache)

        return {"status": "added", "post_id": post.id, "score": post.reply_opportunity_score}

    def add_posts_from_scrape(self, posts_data: List[Dict[str, Any]], platform: str = "twitter") -> Dict[str, Any]:
        """
        Add multiple posts from a scrape result.

        Args:
            posts_data: List of post dicts with at minimum: author, content, url
            platform: Platform the posts are from

        Returns:
            Summary of added posts
        """
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        added = 0
        duplicates = 0

        for data in posts_data:
            # Generate ID from URL or content hash
            post_id = data.get("id") or str(hash(data.get("url", "") or data.get("content", "")))[:8]

            post = TrendingPost(
                id=post_id,
                author=data.get("author", "unknown"),
                content=data.get("content", ""),
                url=data.get("url", ""),
                platform=platform,
                posted_at=data.get("posted_at", now_iso()),
                likes=data.get("likes", 0),
                retweets=data.get("retweets", 0),
                replies=data.get("replies", 0),
                quotes=data.get("quotes", 0),
                topics=data.get("topics", []),
            )

            result = self.add_post(post)
            if result.get("status") == "added":
                added += 1
            else:
                duplicates += 1

        return {
            "status": "complete",
            "added": added,
            "duplicates": duplicates,
            "total": len(posts_data),
        }

    def _score_opportunity(self, post: TrendingPost) -> float:
        """Score a post for reply opportunity."""
        score = 0.0

        # Engagement score (0-40 points)
        engagement = post.total_engagement
        if engagement > 1000:
            score += 40
        elif engagement > 500:
            score += 30
        elif engagement > 100:
            score += 20
        elif engagement > 50:
            score += 10

        # Reply ratio (0-20 points) - fewer replies = more opportunity
        if post.likes > 0:
            reply_ratio = post.replies / post.likes
            if reply_ratio < 0.05:
                score += 20  # Few replies relative to likes = opportunity
            elif reply_ratio < 0.1:
                score += 15
            elif reply_ratio < 0.2:
                score += 10

        # Keyword relevance (0-20 points)
        keywords = self.get_keywords()
        content_lower = post.content.lower()
        keyword_matches = sum(1 for k in keywords if k.lower() in content_lower)
        score += min(keyword_matches * 5, 20)

        # Author importance (0-20 points) - on watchlist = bonus
        watchlist = self.get_watchlist()
        author_clean = post.author.lstrip('@').lower()
        if any(w.lstrip('@').lower() == author_clean for w in watchlist):
            score += 20

        return min(score, 100)

    def get_opportunities(self, min_score: float = 50, limit: int = 10) -> List[TrendingPost]:
        """Get high-scoring reply opportunities."""
        user = get_active_user()
        if not user:
            return []

        cache = self._load_cache(user)
        posts = [TrendingPost.from_dict(p) for p in cache.get("posts", [])]

        # Filter by score and not replied
        posts = [p for p in posts if p.reply_opportunity_score >= min_score and not p.replied]

        # Sort by score
        posts.sort(key=lambda x: x.reply_opportunity_score, reverse=True)

        return posts[:limit]

    def mark_replied(self, post_id: str, reply_url: str = "") -> Dict[str, Any]:
        """Mark a post as replied to."""
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        cache = self._load_cache(user)

        for post in cache.get("posts", []):
            if post["id"] == post_id:
                post["replied"] = True
                post["reply_url"] = reply_url
                self._save_cache(user, cache)
                return {"status": "marked", "post_id": post_id}

        return {"error": f"Post {post_id} not found"}

    def clear_old_posts(self, days: int = 7) -> Dict[str, Any]:
        """Clear posts older than specified days."""
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        cache = self._load_cache(user)
        cutoff = datetime.now() - timedelta(days=days)

        original_count = len(cache.get("posts", []))
        cache["posts"] = [
            p for p in cache.get("posts", [])
            if self._parse_date(p.get("found_at", "")) > cutoff
        ]
        removed = original_count - len(cache["posts"])

        self._save_cache(user, cache)

        return {"status": "cleared", "removed": removed}

    def _parse_date(self, date_str: str) -> datetime:
        """Parse an ISO date string."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except ValueError:
            return datetime.min

    def get_scan_stats(self) -> Dict[str, Any]:
        """Get scanning statistics."""
        user = get_active_user()
        if not user:
            return {}

        cache = self._load_cache(user)
        posts = cache.get("posts", [])

        return {
            "total_posts": len(posts),
            "replied": len([p for p in posts if p.get("replied")]),
            "pending": len([p for p in posts if not p.get("replied")]),
            "high_opportunity": len([p for p in posts if p.get("reply_opportunity_score", 0) >= 70]),
            "last_scan": cache.get("last_scan", "never"),
            "scan_count": cache.get("scan_count", 0),
            "watchlist_size": len(self.get_watchlist()),
            "keywords_count": len(self.get_keywords()),
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_scanner: Optional[TrendingScanner] = None


def get_scanner() -> TrendingScanner:
    """Get the singleton trending scanner."""
    global _scanner
    if _scanner is None:
        _scanner = TrendingScanner()
    return _scanner


def scan_trending(platform: str = "twitter", limit: int = 20) -> List[TrendingPost]:
    """Scan for trending posts."""
    return get_scanner().scan(platform, limit)


def get_opportunities(min_score: float = 50, limit: int = 10) -> List[TrendingPost]:
    """Get reply opportunities."""
    return get_scanner().get_opportunities(min_score, limit)


def add_posts(posts_data: List[Dict], platform: str = "twitter") -> Dict[str, Any]:
    """Add posts from scrape."""
    return get_scanner().add_posts_from_scrape(posts_data, platform)
