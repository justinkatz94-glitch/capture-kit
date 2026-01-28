"""
Voice Evolver - Iterative voice profile improvement

Evolves user voice profile based on performance data.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

from .schemas import generate_id, now_iso, load_json, save_json
from .user_manager import get_active_user, get_active_profile, get_manager
from .post_tracker import PostTracker
from .feedback_loop import FeedbackLoop

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"


class VoiceEvolver:
    """
    Evolves voice profile based on performance feedback.
    """

    def __init__(self):
        """Initialize voice evolver."""
        self.tracker = PostTracker()
        self.feedback = FeedbackLoop()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_evolution_path(self, user: str) -> Path:
        """Get the evolution history file path for a user."""
        user_dir = DATA_DIR / user.lower().replace(' ', '_')
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "voice_evolution.json"

    def _load_evolution_history(self, user: str) -> Dict[str, Any]:
        """Load evolution history for a user."""
        path = self._get_evolution_path(user)
        if path.exists():
            return load_json(str(path))
        return {
            "user": user,
            "evolutions": [],
            "current_version": 1,
            "created_at": now_iso(),
        }

    def _save_evolution_history(self, user: str, history: Dict[str, Any]):
        """Save evolution history for a user."""
        history["updated_at"] = now_iso()
        path = self._get_evolution_path(user)
        save_json(str(path), history)

    def analyze_voice_patterns(self) -> Dict[str, Any]:
        """Analyze voice patterns from successful posts."""
        user = get_active_user()
        if not user:
            return {}

        profile = get_active_profile()
        if not profile:
            return {}

        # Get top performing posts
        top_posts = self.tracker.get_top_performing(limit=20)

        if not top_posts:
            return {"error": "No posts to analyze"}

        # Analyze patterns
        patterns = {
            "openers": defaultdict(int),
            "closers": defaultdict(int),
            "phrases": defaultdict(int),
            "word_lengths": [],
            "sentence_structures": [],
            "tone_indicators": defaultdict(int),
        }

        # Signature phrases from profile
        signature_phrases = profile.get("voice", {}).get("signature_phrases", [])

        for post in top_posts:
            content = post.content

            # Analyze opener (first 10 words)
            words = content.split()
            if len(words) >= 3:
                opener = " ".join(words[:3])
                patterns["openers"][opener.lower()] += 1

            # Analyze closer (last 10 words)
            if len(words) >= 3:
                closer = " ".join(words[-3:])
                patterns["closers"][closer.lower()] += 1

            # Track word count
            patterns["word_lengths"].append(len(words))

            # Check for signature phrases
            for phrase in signature_phrases:
                if phrase.lower() in content.lower():
                    patterns["phrases"][phrase] += 1

            # Tone indicators
            if "!" in content:
                patterns["tone_indicators"]["exclamation"] += 1
            if "?" in content:
                patterns["tone_indicators"]["question"] += 1
            if any(c.isupper() for c in content if c.isalpha()):
                patterns["tone_indicators"]["caps_emphasis"] += 1
            if content.startswith(("I ", "I'm", "I've")):
                patterns["tone_indicators"]["first_person"] += 1

        # Calculate averages and most common
        avg_word_length = sum(patterns["word_lengths"]) / len(patterns["word_lengths"]) if patterns["word_lengths"] else 0

        return {
            "posts_analyzed": len(top_posts),
            "avg_word_count": round(avg_word_length, 1),
            "top_openers": dict(sorted(patterns["openers"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_closers": dict(sorted(patterns["closers"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "effective_phrases": dict(sorted(patterns["phrases"].items(), key=lambda x: x[1], reverse=True)[:5]),
            "tone_patterns": dict(patterns["tone_indicators"]),
        }

    def suggest_voice_updates(self) -> Dict[str, Any]:
        """Suggest updates to voice profile based on performance."""
        user = get_active_user()
        if not user:
            return {}

        profile = get_active_profile()
        if not profile:
            return {}

        # Analyze patterns
        patterns = self.analyze_voice_patterns()
        if "error" in patterns:
            return patterns

        # Get technique insights
        insights = self.feedback.get_technique_insights()

        suggestions = []

        # Word count suggestion
        current_style = profile.get("style", {})
        current_length = current_style.get("sentence_length", "medium")
        optimal_length = patterns.get("avg_word_count", 0)

        if optimal_length > 0:
            if optimal_length < 20 and current_length != "concise":
                suggestions.append({
                    "field": "style.sentence_length",
                    "current": current_length,
                    "suggested": "concise",
                    "reason": f"Top posts average {optimal_length:.0f} words - shorter content performs better",
                })
            elif optimal_length > 40 and current_length != "elaborate":
                suggestions.append({
                    "field": "style.sentence_length",
                    "current": current_length,
                    "suggested": "elaborate",
                    "reason": f"Top posts average {optimal_length:.0f} words - detailed content performs better",
                })

        # Opener suggestions
        top_openers = list(patterns.get("top_openers", {}).keys())
        current_openers = profile.get("voice", {}).get("common_openers", [])
        new_openers = [o for o in top_openers if o not in current_openers]

        if new_openers:
            suggestions.append({
                "field": "voice.common_openers",
                "action": "add",
                "values": new_openers[:3],
                "reason": "These openers appear frequently in top-performing posts",
            })

        # Phrase suggestions
        effective_phrases = list(patterns.get("effective_phrases", {}).keys())
        current_phrases = profile.get("voice", {}).get("signature_phrases", [])

        # Find phrases that work but aren't tracked
        for phrase, count in patterns.get("effective_phrases", {}).items():
            if phrase not in current_phrases and count >= 2:
                suggestions.append({
                    "field": "voice.signature_phrases",
                    "action": "add",
                    "values": [phrase],
                    "reason": f"'{phrase}' appears in {count} top posts",
                })

        # Tone suggestions based on tone patterns
        tone_patterns = patterns.get("tone_patterns", {})
        current_tone = profile.get("voice", {}).get("tone", "professional")

        if tone_patterns.get("exclamation", 0) > len(patterns.get("posts_analyzed", 0)) / 2:
            if current_tone not in ["enthusiastic", "energetic"]:
                suggestions.append({
                    "field": "voice.tone",
                    "current": current_tone,
                    "suggested": "enthusiastic",
                    "reason": "High-performing posts frequently use exclamations",
                })

        if tone_patterns.get("question", 0) > len(patterns.get("posts_analyzed", 0)) / 2:
            suggestions.append({
                "field": "voice.common_openers",
                "action": "prioritize_questions",
                "reason": "Questions perform well - consider leading with questions more often",
            })

        # Hook type suggestions based on technique insights
        hook_insights = {k: v for k, v in insights.items() if k.startswith("hook:")}
        if hook_insights:
            best_hook = max(hook_insights.items(), key=lambda x: x[1]["avg_velocity"])[0]
            suggestions.append({
                "field": "proven_patterns",
                "action": "add",
                "values": [{"type": "hook", "value": best_hook, "velocity": hook_insights[best_hook]["avg_velocity"]}],
                "reason": f"{best_hook} is your highest-performing hook type",
            })

        return {
            "user": user,
            "patterns_analyzed": patterns,
            "suggestions": suggestions,
            "generated_at": now_iso(),
        }

    def apply_evolution(self, suggestions_to_apply: List[int] = None) -> Dict[str, Any]:
        """
        Apply suggested voice updates to profile.

        Args:
            suggestions_to_apply: List of suggestion indices to apply (0-based).
                                  If None, applies all suggestions.

        Returns:
            Summary of changes made
        """
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        # Get suggestions
        suggestions_data = self.suggest_voice_updates()
        if "error" in suggestions_data:
            return suggestions_data

        all_suggestions = suggestions_data.get("suggestions", [])

        if not all_suggestions:
            return {"status": "no_changes", "reason": "No suggestions to apply"}

        # Filter to selected suggestions
        if suggestions_to_apply is not None:
            to_apply = [all_suggestions[i] for i in suggestions_to_apply if i < len(all_suggestions)]
        else:
            to_apply = all_suggestions

        if not to_apply:
            return {"status": "no_changes", "reason": "No valid suggestions selected"}

        # Load current profile
        profile = get_active_profile()
        if not profile:
            return {"error": "Could not load profile"}

        changes_made = []
        manager = get_manager()

        for suggestion in to_apply:
            field = suggestion.get("field", "")
            action = suggestion.get("action", "update")

            if "." in field:
                # Nested field like "voice.common_openers"
                parts = field.split(".")
                parent = parts[0]
                child = parts[1]

                if parent not in profile:
                    profile[parent] = {}

                if action == "add":
                    # Add to list
                    current = profile[parent].get(child, [])
                    values = suggestion.get("values", [])
                    profile[parent][child] = list(set(current + values))
                    changes_made.append(f"Added {len(values)} items to {field}")

                elif action == "update" or "suggested" in suggestion:
                    # Update value
                    old_value = profile[parent].get(child)
                    new_value = suggestion.get("suggested")
                    if new_value:
                        profile[parent][child] = new_value
                        changes_made.append(f"Updated {field}: {old_value} -> {new_value}")

            elif field == "proven_patterns" and action == "add":
                # Add proven patterns
                current = profile.get("proven_patterns", [])
                values = suggestion.get("values", [])
                profile["proven_patterns"] = current + values
                changes_made.append(f"Added {len(values)} proven patterns")

        # Save updated profile
        if changes_made:
            manager.save_profile(profile)

            # Record evolution
            history = self._load_evolution_history(user)
            history["evolutions"].append({
                "id": generate_id(),
                "version": history["current_version"] + 1,
                "changes": changes_made,
                "suggestions_applied": len(to_apply),
                "timestamp": now_iso(),
            })
            history["current_version"] += 1
            self._save_evolution_history(user, history)

        return {
            "status": "success",
            "changes_made": changes_made,
            "version": history["current_version"],
        }

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get the voice evolution history."""
        user = get_active_user()
        if not user:
            return []

        history = self._load_evolution_history(user)
        return history.get("evolutions", [])

    def compare_versions(self, version1: int = None, version2: int = None) -> Dict[str, Any]:
        """
        Compare performance between voice versions.

        Args:
            version1: First version to compare (default: previous)
            version2: Second version to compare (default: current)

        Returns:
            Comparison data
        """
        user = get_active_user()
        if not user:
            return {}

        history = self._load_evolution_history(user)
        evolutions = history.get("evolutions", [])

        if len(evolutions) < 2:
            return {"error": "Need at least 2 versions to compare"}

        # Default to comparing last two versions
        if version1 is None:
            version1 = history["current_version"] - 1
        if version2 is None:
            version2 = history["current_version"]

        # Find evolution timestamps
        v1_evolution = next((e for e in evolutions if e.get("version") == version1), None)
        v2_evolution = next((e for e in evolutions if e.get("version") == version2), None)

        if not v1_evolution or not v2_evolution:
            return {"error": "Could not find specified versions"}

        # Get posts from each period
        # This is a simplified comparison - in production, you'd track post->version mapping
        return {
            "version1": version1,
            "version2": version2,
            "v1_timestamp": v1_evolution.get("timestamp"),
            "v2_timestamp": v2_evolution.get("timestamp"),
            "v1_changes": v1_evolution.get("changes", []),
            "v2_changes": v2_evolution.get("changes", []),
            "note": "For detailed performance comparison, use the feedback loop's trend analysis",
        }

    def rollback(self, to_version: int) -> Dict[str, Any]:
        """
        Rollback to a previous voice version.

        Note: This creates a new version with reversed changes,
        it doesn't actually restore the old profile state.
        """
        user = get_active_user()
        if not user:
            return {"error": "No active user"}

        history = self._load_evolution_history(user)
        current = history["current_version"]

        if to_version >= current:
            return {"error": f"Cannot rollback to version {to_version} (current: {current})"}

        # Record rollback
        history["evolutions"].append({
            "id": generate_id(),
            "version": current + 1,
            "changes": [f"Rollback requested to version {to_version}"],
            "rollback_from": current,
            "rollback_to": to_version,
            "timestamp": now_iso(),
        })
        history["current_version"] += 1
        self._save_evolution_history(user, history)

        return {
            "status": "rollback_recorded",
            "from_version": current,
            "to_version": to_version,
            "new_version": current + 1,
            "note": "Manual profile review recommended to fully restore previous state",
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_evolver: Optional[VoiceEvolver] = None


def get_evolver() -> VoiceEvolver:
    """Get the singleton voice evolver."""
    global _evolver
    if _evolver is None:
        _evolver = VoiceEvolver()
    return _evolver


def analyze_patterns() -> Dict[str, Any]:
    """Analyze voice patterns."""
    return get_evolver().analyze_voice_patterns()


def suggest_updates() -> Dict[str, Any]:
    """Suggest voice updates."""
    return get_evolver().suggest_voice_updates()


def evolve_voice(suggestions: List[int] = None) -> Dict[str, Any]:
    """Apply voice evolution."""
    return get_evolver().apply_evolution(suggestions)


def get_history() -> List[Dict[str, Any]]:
    """Get evolution history."""
    return get_evolver().get_evolution_history()
