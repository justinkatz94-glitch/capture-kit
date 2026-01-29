"""
User Manager - Multi-user profile management

Handles user creation, switching, and profile management.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .schemas import (
    USER_PROFILE_SCHEMA, Goal, Platform,
    generate_id, now_iso, load_json, save_json
)

# Paths
BASE_DIR = Path(__file__).parent.parent
PROFILES_DIR = BASE_DIR / "profiles"
DATA_DIR = BASE_DIR / "data"
NICHES_DIR = BASE_DIR / "niches"

# Active user state file
ACTIVE_USER_FILE = DATA_DIR / "active_user.json"


class UserManager:
    """
    Manages user profiles and active user state.
    """

    def __init__(self):
        """Initialize user manager."""
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._active_user: Optional[str] = None
        self._load_active_user()

    def _load_active_user(self):
        """Load the active user from state file."""
        if ACTIVE_USER_FILE.exists():
            data = load_json(str(ACTIVE_USER_FILE))
            self._active_user = data.get("active_user")

    def _save_active_user(self):
        """Save the active user to state file."""
        save_json(str(ACTIVE_USER_FILE), {
            "active_user": self._active_user,
            "updated_at": now_iso()
        })

    @property
    def active_user(self) -> Optional[str]:
        """Get the active user name."""
        return self._active_user

    def get_active_profile(self) -> Optional[Dict[str, Any]]:
        """Get the active user's profile."""
        if not self._active_user:
            return None
        return self.get_profile(self._active_user)

    def list_users(self) -> List[Dict[str, Any]]:
        """List all users with summary info."""
        users = []
        for profile_file in PROFILES_DIR.glob("*.json"):
            if profile_file.name.startswith("_"):
                continue
            profile = load_json(str(profile_file))
            if profile:
                users.append({
                    "name": profile.get("name", profile_file.stem),
                    "username": profile.get("username", ""),
                    "niche": profile.get("niche", ""),
                    "goal": profile.get("goal", ""),
                    "is_active": profile.get("name") == self._active_user,
                    "created_at": profile.get("created_at", ""),
                })
        return users

    def switch_user(self, name: str) -> Dict[str, Any]:
        """Switch to a different user."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        self._active_user = name
        self._save_active_user()

        return {
            "status": "success",
            "active_user": name,
            "niche": profile.get("niche"),
            "goal": profile.get("goal"),
        }

    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a user's profile by name."""
        profile_path = PROFILES_DIR / f"{name.lower().replace(' ', '_')}.json"
        if profile_path.exists():
            return load_json(str(profile_path))
        return None

    def save_profile(self, profile: Dict[str, Any]) -> str:
        """Save a user profile."""
        name = profile.get("name", "unknown")
        filename = name.lower().replace(' ', '_')
        profile_path = PROFILES_DIR / f"{filename}.json"
        save_json(str(profile_path), profile)
        return str(profile_path)

    def create_user(
        self,
        name: str,
        twitter_handle: str = "",
        linkedin_handle: str = "",
        instagram_handle: str = "",
        niche: str = "",
        niche_topics: List[str] = None,
        watchlist: List[str] = None,
        keywords: List[str] = None,
        goal: str = "grow_followers",
    ) -> Dict[str, Any]:
        """
        Create a new user profile.

        Args:
            name: User's name
            twitter_handle: Twitter username
            linkedin_handle: LinkedIn username
            instagram_handle: Instagram username
            niche: User's niche (fintwit, crypto, tech, etc.)
            niche_topics: Specific topics ["options", "dealer positioning", "market structure"]
            watchlist: Accounts to monitor
            keywords: Niche keywords
            goal: User's goal (grow_followers, drive_traffic, build_authority)

        Returns:
            Created profile summary
        """
        # Check if user exists
        if self.get_profile(name):
            return {"error": f"User '{name}' already exists"}

        # Load niche config if available
        niche_config = self._load_niche_config(niche)

        # Create profile
        profile = {
            "name": name,
            "username": twitter_handle.lstrip('@') if twitter_handle else name.lower().replace(' ', '_'),
            "created_at": now_iso(),
            "platform_handles": {
                "twitter": twitter_handle.lstrip('@') if twitter_handle else "",
                "linkedin": linkedin_handle if linkedin_handle else "",
                "instagram": instagram_handle.lstrip('@') if instagram_handle else "",
            },
            "niche": niche,
            "niche_topics": niche_topics or niche_config.get("default_topics", []),
            "niche_config": f"niches/{niche}.json" if niche else "",
            "goal": goal,
            "watchlist": watchlist or niche_config.get("default_watchlist", []),
            "keywords": keywords or niche_config.get("keywords", []),
            "benchmark_accounts": {
                "twitter": niche_config.get("benchmark_accounts", {}).get("twitter", []),
                "linkedin": niche_config.get("benchmark_accounts", {}).get("linkedin", []),
                "instagram": niche_config.get("benchmark_accounts", {}).get("instagram", []),
            },
            "voice": {
                "tone": niche_config.get("tone", "professional"),
                "formality": "balanced",
                "vocabulary": niche_config.get("vocabulary", "professional"),
                "emoji_style": "minimal",
                "signature_phrases": [],
                "common_openers": [],
                "avoided_phrases": [],
            },
            "style": {
                "sentence_length": "concise",
                "punctuation": "standard",
                "capitalization": "standard",
            },
            "platform_preferences": {
                "twitter": {
                    "reply_length": 80,
                    "post_length": 240,
                    "reply_speed_minutes": 30,
                },
                "linkedin": {
                    "post_length": 1300,
                    "use_line_breaks": True,
                },
                "instagram": {
                    "hashtag_count": 10,
                    "caption_length": 500,
                },
            },
            "proven_patterns": [],
            "baseline_metrics": {
                "followers": 0,
                "avg_engagement_rate": 0.0,
                "captured_at": "",
            },
            "milestones": [],
        }

        # Save profile
        self.save_profile(profile)

        # Set as active user
        self._active_user = name
        self._save_active_user()

        # Initialize user data files
        self._initialize_user_data(name)

        return {
            "status": "success",
            "name": name,
            "niche": niche,
            "goal": goal,
            "watchlist_count": len(profile["watchlist"]),
            "keywords_count": len(profile["keywords"]),
            "profile_path": str(PROFILES_DIR / f"{name.lower().replace(' ', '_')}.json"),
        }

    def _load_niche_config(self, niche: str) -> Dict[str, Any]:
        """Load niche configuration if available."""
        if not niche:
            return {}
        niche_path = NICHES_DIR / f"{niche.lower()}.json"
        if niche_path.exists():
            return load_json(str(niche_path))
        return {}

    def _initialize_user_data(self, name: str):
        """Initialize data files for a new user."""
        user_data_dir = DATA_DIR / name.lower().replace(' ', '_')
        user_data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize post history
        post_history = {
            "user": name,
            "posts": [],
            "weekly_summaries": [],
            "total_posts": 0,
            "avg_engagement_rate": 0.0,
            "best_performing": [],
            "worst_performing": [],
            "updated_at": now_iso(),
        }
        save_json(str(user_data_dir / "post_history.json"), post_history)

        # Initialize experiments
        experiments = {
            "user": name,
            "experiments": [],
            "completed": [],
            "updated_at": now_iso(),
        }
        save_json(str(user_data_dir / "experiments.json"), experiments)

    def update_profile(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user's profile."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        # Deep merge updates
        def deep_merge(base: Dict, updates: Dict) -> Dict:
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        profile = deep_merge(profile, updates)
        profile["updated_at"] = now_iso()

        self.save_profile(profile)

        return {"status": "success", "updated_fields": list(updates.keys())}

    def add_proven_pattern(self, name: str, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Add a proven pattern to user's profile."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        pattern["added_at"] = now_iso()
        profile.setdefault("proven_patterns", []).append(pattern)

        self.save_profile(profile)

        return {"status": "success", "pattern_count": len(profile["proven_patterns"])}

    def update_baseline(self, name: str, followers: int, avg_engagement_rate: float) -> Dict[str, Any]:
        """Update user's baseline metrics."""
        return self.update_profile(name, {
            "baseline_metrics": {
                "followers": followers,
                "avg_engagement_rate": avg_engagement_rate,
                "captured_at": now_iso(),
            }
        })

    def add_milestone(self, name: str, milestone: Dict[str, Any]) -> Dict[str, Any]:
        """Add a milestone to user's profile."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        milestone["created_at"] = now_iso()
        milestone["id"] = generate_id()
        profile.setdefault("milestones", []).append(milestone)

        self.save_profile(profile)

        return {"status": "success", "milestone_id": milestone["id"]}

    def delete_user(self, name: str) -> Dict[str, Any]:
        """Delete a user profile."""
        profile_path = PROFILES_DIR / f"{name.lower().replace(' ', '_')}.json"
        if not profile_path.exists():
            return {"error": f"User '{name}' not found"}

        profile_path.unlink()

        # Clear active user if deleted
        if self._active_user == name:
            self._active_user = None
            self._save_active_user()

        return {"status": "success", "deleted": name}

    # =========================================================================
    # BENCHMARK ACCOUNT MANAGEMENT
    # =========================================================================

    def add_benchmark_account(
        self,
        name: str,
        handle: str,
        platform: str = "linkedin"
    ) -> Dict[str, Any]:
        """
        Add a benchmark account to track.

        Args:
            name: User name
            handle: Account handle to add
            platform: Platform (twitter, linkedin, instagram)

        Returns:
            Result dict
        """
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        # Initialize benchmark_accounts if not present
        if "benchmark_accounts" not in profile:
            profile["benchmark_accounts"] = {
                "twitter": [],
                "linkedin": [],
                "instagram": [],
            }

        # Clean handle
        clean_handle = handle.lstrip('@').strip()

        # Check if already exists
        if clean_handle in profile["benchmark_accounts"].get(platform, []):
            return {"error": f"@{clean_handle} already in {platform} benchmarks"}

        # Add to list
        profile["benchmark_accounts"].setdefault(platform, []).append(clean_handle)
        profile["updated_at"] = now_iso()

        self.save_profile(profile)

        return {
            "status": "success",
            "added": clean_handle,
            "platform": platform,
            "total_benchmarks": len(profile["benchmark_accounts"][platform]),
        }

    def remove_benchmark_account(
        self,
        name: str,
        handle: str,
        platform: str = "linkedin"
    ) -> Dict[str, Any]:
        """Remove a benchmark account."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        clean_handle = handle.lstrip('@').strip()
        benchmarks = profile.get("benchmark_accounts", {}).get(platform, [])

        if clean_handle not in benchmarks:
            return {"error": f"@{clean_handle} not in {platform} benchmarks"}

        benchmarks.remove(clean_handle)
        profile["updated_at"] = now_iso()

        self.save_profile(profile)

        return {
            "status": "success",
            "removed": clean_handle,
            "platform": platform,
            "remaining": len(benchmarks),
        }

    def list_benchmark_accounts(
        self,
        name: str,
        platform: str = None
    ) -> Dict[str, Any]:
        """List benchmark accounts for a user."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        benchmarks = profile.get("benchmark_accounts", {})

        if platform:
            return {
                "platform": platform,
                "accounts": benchmarks.get(platform, []),
                "count": len(benchmarks.get(platform, [])),
            }

        return {
            "all_platforms": benchmarks,
            "counts": {p: len(accts) for p, accts in benchmarks.items()},
        }

    def set_niche_topics(
        self,
        name: str,
        topics: List[str]
    ) -> Dict[str, Any]:
        """Set niche topics for a user."""
        profile = self.get_profile(name)
        if not profile:
            return {"error": f"User '{name}' not found"}

        profile["niche_topics"] = topics
        profile["updated_at"] = now_iso()

        self.save_profile(profile)

        return {
            "status": "success",
            "niche_topics": topics,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_manager: Optional[UserManager] = None


def get_manager() -> UserManager:
    """Get the singleton user manager."""
    global _manager
    if _manager is None:
        _manager = UserManager()
    return _manager


def get_active_user() -> Optional[str]:
    """Get the active user name."""
    return get_manager().active_user


def get_active_profile() -> Optional[Dict[str, Any]]:
    """Get the active user's profile."""
    return get_manager().get_active_profile()


def switch_user(name: str) -> Dict[str, Any]:
    """Switch to a different user."""
    return get_manager().switch_user(name)


def list_users() -> List[Dict[str, Any]]:
    """List all users."""
    return get_manager().list_users()


def create_user(**kwargs) -> Dict[str, Any]:
    """Create a new user."""
    return get_manager().create_user(**kwargs)
