"""
Post Tracker - Track post performance over time

Tracks engagement snapshots and calculates performance metrics.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .schemas import (
    PostRecord, generate_id, now_iso, load_json, save_json
)
from .user_manager import get_active_user, get_active_profile
from .content_analyzer import ContentAnalyzer

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"


class PostTracker:
    """
    Tracks posted content and engagement metrics.
    """

    def __init__(self):
        """Initialize post tracker."""
        self.analyzer = ContentAnalyzer()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_history_path(self, user: str) -> Path:
        """Get the post history file path for a user."""
        user_dir = DATA_DIR / user.lower().replace(' ', '_')
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "post_history.json"

    def _load_history(self, user: str) -> Dict[str, Any]:
        """Load post history for a user."""
        path = self._get_history_path(user)
        if path.exists():
            return load_json(str(path))
        return {
            "user": user,
            "posts": [],
            "weekly_summaries": [],
            "total_posts": 0,
            "avg_engagement_rate": 0.0,
            "best_performing": [],
            "worst_performing": [],
            "updated_at": now_iso(),
        }

    def _save_history(self, user: str, history: Dict[str, Any]):
        """Save post history for a user."""
        history["updated_at"] = now_iso()
        path = self._get_history_path(user)
        save_json(str(path), history)

    def log_post(
        self,
        content: str,
        url: str,
        platform: str = "twitter",
        initial_engagement: Dict[str, int] = None,
    ) -> PostRecord:
        """
        Log a new post.

        Args:
            content: The posted content
            url: URL of the post
            platform: Platform posted to
            initial_engagement: Initial engagement metrics

        Returns:
            PostRecord
        """
        user = get_active_user()
        if not user:
            raise ValueError("No active user. Create or switch to a user first.")

        # Analyze content
        analysis = self.analyzer.analyze(content, platform)

        # Create record
        record = PostRecord(
            id=generate_id(),
            user=user,
            platform=platform,
            content=content,
            url=url,
            posted_at=now_iso(),
            hook_type=analysis.hook_type,
            framework=analysis.framework,
            triggers=analysis.triggers,
            specificity=analysis.specificity,
            word_count=analysis.word_count,
            techniques=analysis.techniques,
            initial_engagement=initial_engagement or {},
        )

        # Save to history
        history = self._load_history(user)
        history["posts"].append(record.to_dict())
        history["total_posts"] = len(history["posts"])
        self._save_history(user, history)

        return record

    def update_engagement(
        self,
        post_id: str,
        engagement: Dict[str, int],
        snapshot_type: str = "24h"
    ) -> Dict[str, Any]:
        """
        Update engagement metrics for a post.

        Args:
            post_id: Post ID
            engagement: Engagement metrics (likes, retweets, replies, etc.)
            snapshot_type: Type of snapshot (24h, 48h, 7d)

        Returns:
            Status dict
        """
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        history = self._load_history(user)

        # Find post
        for post in history["posts"]:
            if post["id"] == post_id:
                field = f"engagement_{snapshot_type}"
                post[field] = engagement

                # Calculate velocity if we have 24h data
                if snapshot_type == "24h" and engagement:
                    total = sum(engagement.values())
                    post["engagement_velocity"] = total / 24

                self._save_history(user, history)
                return {"status": "updated", "post_id": post_id, "snapshot": snapshot_type}

        return {"error": f"Post {post_id} not found"}

    def get_post(self, post_id: str) -> Optional[PostRecord]:
        """Get a post by ID."""
        user = get_active_user()
        if not user:
            return None

        history = self._load_history(user)
        for post in history["posts"]:
            if post["id"] == post_id:
                return PostRecord.from_dict(post)
        return None

    def get_recent_posts(self, limit: int = 20, platform: str = None) -> List[PostRecord]:
        """Get recent posts."""
        user = get_active_user()
        if not user:
            return []

        history = self._load_history(user)
        posts = history["posts"]

        if platform:
            posts = [p for p in posts if p.get("platform") == platform]

        # Sort by posted_at descending
        posts.sort(key=lambda x: x.get("posted_at", ""), reverse=True)

        return [PostRecord.from_dict(p) for p in posts[:limit]]

    def get_top_performing(self, limit: int = 10, platform: str = None) -> List[PostRecord]:
        """Get top performing posts."""
        user = get_active_user()
        if not user:
            return []

        history = self._load_history(user)
        posts = history["posts"]

        if platform:
            posts = [p for p in posts if p.get("platform") == platform]

        # Score by engagement velocity
        posts.sort(key=lambda x: x.get("engagement_velocity", 0), reverse=True)

        return [PostRecord.from_dict(p) for p in posts[:limit]]

    def get_performance_by_technique(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by technique."""
        user = get_active_user()
        if not user:
            return {}

        history = self._load_history(user)
        posts = history["posts"]

        technique_stats = {}

        for post in posts:
            for technique in post.get("techniques", []):
                if technique not in technique_stats:
                    technique_stats[technique] = {
                        "count": 0,
                        "total_velocity": 0,
                        "posts": [],
                    }

                stats = technique_stats[technique]
                stats["count"] += 1
                stats["total_velocity"] += post.get("engagement_velocity", 0)
                stats["posts"].append(post["id"])

        # Calculate averages
        for technique, stats in technique_stats.items():
            stats["avg_velocity"] = stats["total_velocity"] / stats["count"] if stats["count"] > 0 else 0
            del stats["total_velocity"]

        # Sort by average velocity
        sorted_techniques = dict(sorted(
            technique_stats.items(),
            key=lambda x: x[1]["avg_velocity"],
            reverse=True
        ))

        return sorted_techniques

    def get_performance_by_hook(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by hook type."""
        user = get_active_user()
        if not user:
            return {}

        history = self._load_history(user)
        posts = history["posts"]

        hook_stats = {}

        for post in posts:
            hook = post.get("hook_type", "none") or "none"
            if hook not in hook_stats:
                hook_stats[hook] = {
                    "count": 0,
                    "total_velocity": 0,
                }

            hook_stats[hook]["count"] += 1
            hook_stats[hook]["total_velocity"] += post.get("engagement_velocity", 0)

        # Calculate averages
        for hook, stats in hook_stats.items():
            stats["avg_velocity"] = stats["total_velocity"] / stats["count"] if stats["count"] > 0 else 0
            del stats["total_velocity"]

        return dict(sorted(hook_stats.items(), key=lambda x: x[1]["avg_velocity"], reverse=True))

    def calculate_baseline(self) -> Dict[str, Any]:
        """Calculate baseline metrics from post history."""
        user = get_active_user()
        if not user:
            return {}

        history = self._load_history(user)
        posts = history["posts"]

        if not posts:
            return {"error": "No posts to calculate baseline from"}

        # Calculate averages
        velocities = [p.get("engagement_velocity", 0) for p in posts]
        word_counts = [p.get("word_count", 0) for p in posts]

        # Get engagement totals from 24h snapshots
        total_engagement = 0
        posts_with_engagement = 0
        for post in posts:
            engagement = post.get("engagement_24h", {})
            if engagement:
                total_engagement += sum(engagement.values())
                posts_with_engagement += 1

        avg_engagement = total_engagement / posts_with_engagement if posts_with_engagement > 0 else 0

        return {
            "total_posts": len(posts),
            "avg_engagement_velocity": sum(velocities) / len(velocities) if velocities else 0,
            "avg_word_count": sum(word_counts) / len(word_counts) if word_counts else 0,
            "avg_engagement_per_post": avg_engagement,
            "top_hooks": list(self.get_performance_by_hook().keys())[:3],
            "top_techniques": list(self.get_performance_by_technique().keys())[:5],
            "calculated_at": now_iso(),
        }

    def annotate_post(self, post_id: str, what_worked: List[str] = None, what_failed: List[str] = None) -> Dict[str, Any]:
        """Annotate a post with learnings."""
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        history = self._load_history(user)

        for post in history["posts"]:
            if post["id"] == post_id:
                if what_worked:
                    post["what_worked"] = what_worked
                if what_failed:
                    post["what_failed"] = what_failed

                self._save_history(user, history)
                return {"status": "annotated", "post_id": post_id}

        return {"error": f"Post {post_id} not found"}

    def get_posts_needing_engagement_update(self, snapshot_type: str = "24h") -> List[PostRecord]:
        """Get posts that need engagement updates."""
        user = get_active_user()
        if not user:
            return []

        history = self._load_history(user)
        posts = history["posts"]

        now = datetime.now()
        field = f"engagement_{snapshot_type}"

        # Time thresholds
        thresholds = {
            "24h": timedelta(hours=24),
            "48h": timedelta(hours=48),
            "7d": timedelta(days=7),
        }

        threshold = thresholds.get(snapshot_type, timedelta(hours=24))
        needs_update = []

        for post in posts:
            # Check if already has this snapshot
            if post.get(field):
                continue

            # Check if enough time has passed
            posted_at = post.get("posted_at", "")
            if posted_at:
                try:
                    post_time = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                    if now - post_time.replace(tzinfo=None) >= threshold:
                        needs_update.append(PostRecord.from_dict(post))
                except ValueError:
                    pass

        return needs_update


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_tracker: Optional[PostTracker] = None


def get_tracker() -> PostTracker:
    """Get the singleton post tracker."""
    global _tracker
    if _tracker is None:
        _tracker = PostTracker()
    return _tracker


def log_post(**kwargs) -> PostRecord:
    """Log a new post."""
    return get_tracker().log_post(**kwargs)


def get_recent_posts(limit: int = 20) -> List[PostRecord]:
    """Get recent posts."""
    return get_tracker().get_recent_posts(limit)


def get_top_posts(limit: int = 10) -> List[PostRecord]:
    """Get top performing posts."""
    return get_tracker().get_top_performing(limit)
