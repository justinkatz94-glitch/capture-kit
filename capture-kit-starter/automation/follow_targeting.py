"""
Follow Targeting - Strategic follow/unfollow management

Tracks follows, monitors followbacks, and identifies unfollow candidates.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field

from .schemas import generate_id, now_iso, load_json, save_json
from .user_manager import get_active_user, get_active_profile

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"


@dataclass
class FollowTarget:
    """A follow target record."""
    handle: str
    added_at: str
    reason: str = ""
    source: str = ""  # Account we found them from

    # Status tracking
    followed_at: Optional[str] = None
    followed_back: Optional[bool] = None
    followback_checked_at: Optional[str] = None
    unfollowed_at: Optional[str] = None
    unfollow_reason: str = ""

    # Analytics
    follower_count: int = 0
    following_count: int = 0
    engagement_rate: float = 0.0
    niche_relevance: float = 0.0

    # Tags
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'FollowTarget':
        return cls(**data)

    @property
    def is_followed(self) -> bool:
        return self.followed_at is not None and self.unfollowed_at is None

    @property
    def days_since_follow(self) -> Optional[int]:
        if not self.followed_at:
            return None
        try:
            followed = datetime.fromisoformat(self.followed_at.replace('Z', '+00:00')).replace(tzinfo=None)
            return (datetime.now() - followed).days
        except ValueError:
            return None


class FollowTargetingManager:
    """
    Manages follow targeting strategy.
    """

    DEFAULT_SETTINGS = {
        "followback_check_days": 7,
        "auto_unfollow_after_days": 14,
        "max_daily_follows": 50,
        "max_daily_unfollows": 30,
        "min_follower_ratio": 0.5,  # Their followers / their following
        "prefer_engaged_accounts": True,
    }

    def __init__(self):
        """Initialize follow targeting manager."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_targets_path(self, user: str = None) -> Path:
        """Get the targets file path."""
        if user is None:
            user = get_active_user() or "default"
        return DATA_DIR / "targets.json"

    def _load_data(self) -> Dict[str, Any]:
        """Load targets data."""
        path = self._get_targets_path()
        if path.exists():
            return load_json(str(path))
        return self._empty_data()

    def _save_data(self, data: Dict[str, Any]):
        """Save targets data."""
        data["updated_at"] = now_iso()
        path = self._get_targets_path()
        save_json(str(path), data)

    def _empty_data(self) -> Dict[str, Any]:
        """Return empty data structure."""
        return {
            "targets": [],
            "settings": self.DEFAULT_SETTINGS.copy(),
            "daily_stats": [],
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }

    def add_target(self, handle: str, reason: str = "", source: str = "", tags: List[str] = None) -> Dict[str, Any]:
        """
        Add a follow target.

        Args:
            handle: Twitter handle (with or without @)
            reason: Why you want to follow them
            source: Account you found them from
            tags: Optional tags for categorization

        Returns:
            Status dict
        """
        handle = handle.lstrip('@').lower()
        data = self._load_data()

        # Check if already exists
        existing = [t for t in data["targets"] if t.get("handle", "").lower() == handle]
        if existing:
            return {"error": f"@{handle} is already in targets"}

        target = FollowTarget(
            handle=handle,
            added_at=now_iso(),
            reason=reason,
            source=source.lstrip('@') if source else "",
            tags=tags or [],
        )

        data["targets"].append(target.to_dict())
        self._save_data(data)

        return {"status": "added", "handle": handle, "reason": reason}

    def remove_target(self, handle: str) -> Dict[str, Any]:
        """Remove a target from the list."""
        handle = handle.lstrip('@').lower()
        data = self._load_data()

        original_count = len(data["targets"])
        data["targets"] = [t for t in data["targets"] if t.get("handle", "").lower() != handle]

        if len(data["targets"]) == original_count:
            return {"error": f"@{handle} not found in targets"}

        self._save_data(data)
        return {"status": "removed", "handle": handle}

    def list_targets(self, status: str = None) -> List[FollowTarget]:
        """
        List targets.

        Args:
            status: Filter by status (pending, followed, unfollowed, followback, no_followback)

        Returns:
            List of FollowTarget objects
        """
        data = self._load_data()
        targets = [FollowTarget.from_dict(t) for t in data["targets"]]

        if status == "pending":
            targets = [t for t in targets if not t.followed_at]
        elif status == "followed":
            targets = [t for t in targets if t.is_followed]
        elif status == "unfollowed":
            targets = [t for t in targets if t.unfollowed_at]
        elif status == "followback":
            targets = [t for t in targets if t.followed_back is True]
        elif status == "no_followback":
            targets = [t for t in targets if t.followed_back is False]

        return targets

    def track_follow(self, handle: str, source: str = "") -> Dict[str, Any]:
        """
        Mark a target as followed.

        Args:
            handle: Handle that was followed
            source: Where you found them (optional)

        Returns:
            Status dict
        """
        handle = handle.lstrip('@').lower()
        data = self._load_data()

        for target in data["targets"]:
            if target.get("handle", "").lower() == handle:
                target["followed_at"] = now_iso()
                if source:
                    target["source"] = source.lstrip('@')
                self._save_data(data)
                return {"status": "tracked", "handle": handle, "followed_at": target["followed_at"]}

        # Not in list - add and mark as followed
        target = FollowTarget(
            handle=handle,
            added_at=now_iso(),
            followed_at=now_iso(),
            source=source.lstrip('@') if source else "",
        )
        data["targets"].append(target.to_dict())
        self._save_data(data)

        return {"status": "added_and_tracked", "handle": handle}

    def record_followback(self, handle: str, followed_back: bool) -> Dict[str, Any]:
        """
        Record whether someone followed back.

        Args:
            handle: Handle to update
            followed_back: True if they followed back

        Returns:
            Status dict
        """
        handle = handle.lstrip('@').lower()
        data = self._load_data()

        for target in data["targets"]:
            if target.get("handle", "").lower() == handle:
                target["followed_back"] = followed_back
                target["followback_checked_at"] = now_iso()
                self._save_data(data)
                return {"status": "recorded", "handle": handle, "followed_back": followed_back}

        return {"error": f"@{handle} not found in targets"}

    def get_unfollow_candidates(self, days: int = None) -> List[FollowTarget]:
        """
        Get accounts that haven't followed back after X days.

        Args:
            days: Number of days to wait (default from settings)

        Returns:
            List of unfollow candidates
        """
        data = self._load_data()
        settings = data.get("settings", self.DEFAULT_SETTINGS)

        if days is None:
            days = settings.get("followback_check_days", 7)

        targets = [FollowTarget.from_dict(t) for t in data["targets"]]
        candidates = []

        for target in targets:
            # Must be followed and not unfollowed
            if not target.is_followed:
                continue

            # Check if enough days have passed
            days_since = target.days_since_follow
            if days_since is None or days_since < days:
                continue

            # Not followed back or unknown
            if target.followed_back is True:
                continue

            candidates.append(target)

        return candidates

    def record_unfollow(self, handle: str, reason: str = "") -> Dict[str, Any]:
        """
        Record an unfollow action.

        Args:
            handle: Handle that was unfollowed
            reason: Reason for unfollowing

        Returns:
            Status dict
        """
        handle = handle.lstrip('@').lower()
        data = self._load_data()

        for target in data["targets"]:
            if target.get("handle", "").lower() == handle:
                target["unfollowed_at"] = now_iso()
                target["unfollow_reason"] = reason
                self._save_data(data)
                return {"status": "unfollowed", "handle": handle, "reason": reason}

        return {"error": f"@{handle} not found in targets"}

    def suggest_targets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Suggest new follow targets based on current profile.

        Returns list of suggestions based on:
        - Watchlist accounts' followers/following
        - Successful followbacks' similar accounts
        - Niche keywords
        """
        profile = get_active_profile()
        if not profile:
            return []

        suggestions = []
        watchlist = profile.get("watchlist", [])

        # Suggest based on watchlist
        for account in watchlist[:5]:
            suggestions.append({
                "handle": account.lstrip('@'),
                "reason": f"From your watchlist",
                "source": "watchlist",
                "action": f"Check @{account.lstrip('@')}'s engaged followers",
            })

        # Suggest based on successful followbacks
        data = self._load_data()
        followbacks = [t for t in data["targets"] if t.get("followed_back") is True]

        for fb in followbacks[:3]:
            source = fb.get("handle", "")
            suggestions.append({
                "handle": f"followers of @{source}",
                "reason": f"@{source} followed back - similar accounts likely to engage",
                "source": source,
                "action": f"Find accounts that engage with @{source}",
            })

        return suggestions[:limit]

    def analyze_target(self, handle: str) -> Dict[str, Any]:
        """
        Analyze a potential follow target.

        Note: In production, this would call Twitter API.
        For now, returns structure for manual input.
        """
        handle = handle.lstrip('@').lower()

        return {
            "handle": handle,
            "analysis": {
                "recommendation": "Check manually",
                "factors_to_check": [
                    "Follower/following ratio",
                    "Recent engagement on posts",
                    "Content relevance to your niche",
                    "Do they reply to others?",
                    "Are they active (posted recently)?",
                ],
            },
            "scoring_guide": {
                "good_signs": [
                    "Ratio > 1 (more followers than following)",
                    "Replies to others frequently",
                    "Content aligns with your niche",
                    "Active in last 7 days",
                ],
                "red_flags": [
                    "Following >> Followers (likely doesn't follow back)",
                    "No replies, only posts",
                    "Inactive for weeks",
                    "Bot-like behavior",
                ],
            },
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get follow targeting statistics."""
        data = self._load_data()
        targets = [FollowTarget.from_dict(t) for t in data["targets"]]

        total = len(targets)
        pending = len([t for t in targets if not t.followed_at])
        followed = len([t for t in targets if t.is_followed])
        unfollowed = len([t for t in targets if t.unfollowed_at])
        followbacks = len([t for t in targets if t.followed_back is True])
        no_followbacks = len([t for t in targets if t.followed_back is False])
        unknown = len([t for t in targets if t.is_followed and t.followed_back is None])

        followback_rate = (followbacks / (followbacks + no_followbacks) * 100) if (followbacks + no_followbacks) > 0 else 0

        return {
            "total_targets": total,
            "pending": pending,
            "currently_followed": followed,
            "unfollowed": unfollowed,
            "followbacks": followbacks,
            "no_followbacks": no_followbacks,
            "unknown_status": unknown,
            "followback_rate": f"{followback_rate:.1f}%",
            "unfollow_candidates": len(self.get_unfollow_candidates()),
        }

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        data = self._load_data()
        return data.get("settings", self.DEFAULT_SETTINGS)

    def update_settings(self, **kwargs) -> Dict[str, Any]:
        """Update settings."""
        data = self._load_data()
        settings = data.get("settings", self.DEFAULT_SETTINGS.copy())

        for key, value in kwargs.items():
            if key in self.DEFAULT_SETTINGS:
                settings[key] = value

        data["settings"] = settings
        self._save_data(data)

        return {"status": "updated", "settings": settings}

    def get_followed_pending_check(self) -> List[FollowTarget]:
        """Get followed accounts that need followback status checked."""
        data = self._load_data()
        settings = data.get("settings", self.DEFAULT_SETTINGS)
        check_days = settings.get("followback_check_days", 7)

        targets = [FollowTarget.from_dict(t) for t in data["targets"]]
        pending = []

        for target in targets:
            if not target.is_followed:
                continue
            if target.followed_back is not None:
                continue

            days_since = target.days_since_follow
            if days_since is not None and days_since >= check_days:
                pending.append(target)

        return pending


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_manager: Optional[FollowTargetingManager] = None


def get_targeting_manager() -> FollowTargetingManager:
    """Get the singleton follow targeting manager."""
    global _manager
    if _manager is None:
        _manager = FollowTargetingManager()
    return _manager


def add_target(handle: str, reason: str = "", source: str = "") -> Dict[str, Any]:
    """Add a follow target."""
    return get_targeting_manager().add_target(handle, reason, source)


def list_targets(status: str = None) -> List[FollowTarget]:
    """List targets."""
    return get_targeting_manager().list_targets(status)


def track_follow(handle: str, source: str = "") -> Dict[str, Any]:
    """Track a follow."""
    return get_targeting_manager().track_follow(handle, source)


def get_unfollow_candidates(days: int = None) -> List[FollowTarget]:
    """Get unfollow candidates."""
    return get_targeting_manager().get_unfollow_candidates(days)


def get_stats() -> Dict[str, Any]:
    """Get targeting stats."""
    return get_targeting_manager().get_stats()
