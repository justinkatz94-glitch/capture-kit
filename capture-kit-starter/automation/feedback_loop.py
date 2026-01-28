"""
Feedback Loop - Weekly analysis and performance tracking

Analyzes post performance and generates actionable insights.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .schemas import (
    WeeklySummary, PostRecord, generate_id, now_iso, load_json, save_json
)
from .user_manager import get_active_user, get_active_profile
from .post_tracker import PostTracker

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
BENCHMARKS_DIR = BASE_DIR / "benchmarks"


class FeedbackLoop:
    """
    Analyzes performance and provides feedback for improvement.
    """

    def __init__(self):
        """Initialize feedback loop."""
        self.tracker = PostTracker()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _get_summaries_path(self, user: str) -> Path:
        """Get the summaries file path for a user."""
        user_dir = DATA_DIR / user.lower().replace(' ', '_')
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "weekly_summaries.json"

    def _load_summaries(self, user: str) -> List[Dict[str, Any]]:
        """Load weekly summaries for a user."""
        path = self._get_summaries_path(user)
        if path.exists():
            data = load_json(str(path))
            return data.get("summaries", [])
        return []

    def _save_summaries(self, user: str, summaries: List[Dict[str, Any]]):
        """Save weekly summaries for a user."""
        path = self._get_summaries_path(user)
        save_json(str(path), {
            "user": user,
            "summaries": summaries,
            "updated_at": now_iso(),
        })

    def _load_benchmark(self, niche: str) -> Dict[str, Any]:
        """Load benchmark data for a niche."""
        if not niche:
            return {}
        benchmark_path = BENCHMARKS_DIR / f"{niche.lower()}_twitter.json"
        if benchmark_path.exists():
            return load_json(str(benchmark_path))
        return {}

    def generate_weekly_report(self, week_offset: int = 0) -> WeeklySummary:
        """
        Generate a weekly performance report.

        Args:
            week_offset: 0 for current week, -1 for last week, etc.

        Returns:
            WeeklySummary object
        """
        user = get_active_user()
        if not user:
            raise ValueError("No active user")

        profile = get_active_profile()
        niche = profile.get("niche", "") if profile else ""
        benchmark = self._load_benchmark(niche)

        # Calculate week boundaries
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday() + 7 * abs(week_offset))
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Get posts from this week
        all_posts = self.tracker.get_recent_posts(limit=500)
        week_posts = []

        for post in all_posts:
            try:
                post_date = datetime.fromisoformat(post.posted_at.replace('Z', '+00:00')).replace(tzinfo=None)
                if week_start <= post_date <= week_end:
                    week_posts.append(post)
            except ValueError:
                continue

        # Calculate metrics
        total_engagement = 0
        velocities = []
        hook_performance = defaultdict(list)
        technique_performance = defaultdict(list)
        posting_hours = []

        for post in week_posts:
            # Total engagement from 24h snapshot
            eng_24h = post.engagement_24h or {}
            total_engagement += sum(eng_24h.values())
            velocities.append(post.engagement_velocity)

            # Track hook performance
            if post.hook_type:
                hook_performance[post.hook_type].append(post.engagement_velocity)

            # Track technique performance
            for technique in post.techniques:
                technique_performance[technique].append(post.engagement_velocity)

            # Track posting times
            try:
                post_time = datetime.fromisoformat(post.posted_at.replace('Z', '+00:00'))
                posting_hours.append(post_time.hour)
            except ValueError:
                pass

        # Calculate averages
        avg_velocity = sum(velocities) / len(velocities) if velocities else 0.0

        # Find best hooks
        best_hooks = []
        for hook, vels in sorted(hook_performance.items(), key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0, reverse=True):
            best_hooks.append(hook)

        # Find best techniques
        successful_techniques = []
        failed_techniques = []
        for technique, vels in technique_performance.items():
            avg = sum(vels) / len(vels) if vels else 0
            if avg > avg_velocity:
                successful_techniques.append({"technique": technique, "avg_velocity": avg, "count": len(vels)})
            else:
                failed_techniques.append({"technique": technique, "avg_velocity": avg, "count": len(vels)})

        # Find best posting times
        hour_counts = defaultdict(int)
        for hour in posting_hours:
            hour_counts[hour] += 1
        best_hours = sorted(hour_counts.keys(), key=lambda x: hour_counts[x], reverse=True)[:3]

        # Top and worst performing posts
        sorted_posts = sorted(week_posts, key=lambda x: x.engagement_velocity, reverse=True)
        top_posts = [p.id for p in sorted_posts[:5]]
        worst_posts = [p.id for p in sorted_posts[-3:]] if len(sorted_posts) >= 3 else []

        # Compare to benchmark
        vs_benchmark = {}
        gaps = []

        if benchmark:
            benchmark_patterns = benchmark.get("patterns", {})
            benchmark_velocity = benchmark_patterns.get("avg_engagement_velocity", 0)

            if benchmark_velocity > 0:
                vs_benchmark["velocity_ratio"] = avg_velocity / benchmark_velocity
                if avg_velocity < benchmark_velocity * 0.8:
                    gaps.append(f"Engagement velocity {(1 - avg_velocity/benchmark_velocity)*100:.0f}% below benchmark")

            benchmark_length = benchmark_patterns.get("optimal_length", {}).get("avg", 0)
            if benchmark_length > 0:
                avg_length = sum(p.word_count for p in week_posts) / len(week_posts) if week_posts else 0
                vs_benchmark["length_ratio"] = avg_length / benchmark_length
                if abs(avg_length - benchmark_length) > benchmark_length * 0.2:
                    gaps.append(f"Word count differs from optimal ({avg_length:.0f} vs {benchmark_length})")

        # Generate recommendations
        recommendations = self._generate_recommendations(
            week_posts, best_hooks, successful_techniques, failed_techniques, gaps, benchmark
        )

        # Create summary
        summary = WeeklySummary(
            user=user,
            week_start=week_start.isoformat(),
            week_end=week_end.isoformat(),
            posts_count=len(week_posts),
            total_engagement=total_engagement,
            avg_engagement_rate=avg_velocity,
            top_performing_posts=top_posts,
            successful_techniques=successful_techniques[:5],
            best_hook_types=best_hooks[:3],
            best_posting_times=best_hours,
            worst_performing_posts=worst_posts,
            failed_techniques=failed_techniques[:3],
            vs_benchmark=vs_benchmark,
            gaps_identified=gaps,
            recommendations=recommendations,
            next_week_focus=recommendations[0] if recommendations else "",
        )

        # Save summary
        summaries = self._load_summaries(user)
        summaries.append(summary.to_dict())
        self._save_summaries(user, summaries)

        return summary

    def _generate_recommendations(
        self,
        posts: List[PostRecord],
        best_hooks: List[str],
        successful_techniques: List[Dict],
        failed_techniques: List[Dict],
        gaps: List[str],
        benchmark: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Hook recommendations
        if best_hooks:
            recommendations.append(f"Continue using {best_hooks[0]} hooks - they perform best for you")
        else:
            recommendations.append("Experiment with different hook types to find what works")

        # Technique recommendations
        if successful_techniques:
            top_tech = successful_techniques[0]["technique"]
            recommendations.append(f"Double down on '{top_tech}' - it's your highest performer")

        if failed_techniques:
            worst_tech = failed_techniques[0]["technique"]
            recommendations.append(f"Consider dropping or improving '{worst_tech}' - underperforming")

        # Gap recommendations
        for gap in gaps[:2]:
            recommendations.append(f"Address gap: {gap}")

        # Volume recommendation
        if len(posts) < 5:
            recommendations.append("Increase posting volume - more data helps optimization")
        elif len(posts) > 30:
            recommendations.append("Good volume! Focus on quality over quantity now")

        # Benchmark-based recommendations
        if benchmark:
            patterns = benchmark.get("patterns", {})

            # Timing recommendation
            peak_hours = patterns.get("peak_hours", [])
            if peak_hours:
                recommendations.append(f"Post more during peak hours: {', '.join(str(h) for h in peak_hours[:3])}")

        return recommendations[:5]  # Limit to top 5

    def get_trend_analysis(self, weeks: int = 4) -> Dict[str, Any]:
        """Analyze trends over multiple weeks."""
        user = get_active_user()
        if not user:
            return {}

        summaries = self._load_summaries(user)

        if len(summaries) < 2:
            return {"error": "Need at least 2 weeks of data for trend analysis"}

        # Get recent summaries
        recent = sorted(summaries, key=lambda x: x.get("week_start", ""), reverse=True)[:weeks]

        # Calculate trends
        velocities = [s.get("avg_engagement_rate", 0) for s in recent]
        post_counts = [s.get("posts_count", 0) for s in recent]

        velocity_trend = "improving" if len(velocities) >= 2 and velocities[0] > velocities[-1] else "declining"
        volume_trend = "increasing" if len(post_counts) >= 2 and post_counts[0] > post_counts[-1] else "decreasing"

        # Find consistent winners
        all_techniques = defaultdict(int)
        all_hooks = defaultdict(int)

        for summary in recent:
            for tech in summary.get("successful_techniques", []):
                all_techniques[tech.get("technique", "")] += 1
            for hook in summary.get("best_hook_types", []):
                all_hooks[hook] += 1

        consistent_techniques = [t for t, count in all_techniques.items() if count >= len(recent) / 2]
        consistent_hooks = [h for h, count in all_hooks.items() if count >= len(recent) / 2]

        return {
            "weeks_analyzed": len(recent),
            "velocity_trend": velocity_trend,
            "volume_trend": volume_trend,
            "avg_velocity": sum(velocities) / len(velocities) if velocities else 0,
            "avg_posts_per_week": sum(post_counts) / len(post_counts) if post_counts else 0,
            "consistent_techniques": consistent_techniques,
            "consistent_hooks": consistent_hooks,
            "recommendation": self._get_trend_recommendation(velocity_trend, volume_trend),
        }

    def _get_trend_recommendation(self, velocity_trend: str, volume_trend: str) -> str:
        """Get recommendation based on trends."""
        if velocity_trend == "improving" and volume_trend == "increasing":
            return "Great progress! Keep up the momentum."
        elif velocity_trend == "improving" and volume_trend == "decreasing":
            return "Quality is improving - consider increasing volume."
        elif velocity_trend == "declining" and volume_trend == "increasing":
            return "Volume up but engagement down - focus on quality."
        else:
            return "Review your strategy - both metrics need attention."

    def get_technique_insights(self) -> Dict[str, Any]:
        """Get detailed insights on technique performance."""
        user = get_active_user()
        if not user:
            return {}

        # Get all posts
        posts = self.tracker.get_recent_posts(limit=500)

        # Analyze by technique
        technique_data = defaultdict(lambda: {"posts": 0, "total_velocity": 0, "examples": []})

        for post in posts:
            for technique in post.techniques:
                data = technique_data[technique]
                data["posts"] += 1
                data["total_velocity"] += post.engagement_velocity
                if len(data["examples"]) < 3:
                    data["examples"].append({
                        "id": post.id,
                        "content": post.content[:100],
                        "velocity": post.engagement_velocity,
                    })

        # Calculate averages and rank
        insights = {}
        for technique, data in technique_data.items():
            if data["posts"] > 0:
                insights[technique] = {
                    "posts": data["posts"],
                    "avg_velocity": data["total_velocity"] / data["posts"],
                    "examples": data["examples"],
                }

        # Sort by avg velocity
        sorted_insights = dict(sorted(
            insights.items(),
            key=lambda x: x[1]["avg_velocity"],
            reverse=True
        ))

        return sorted_insights

    def get_recent_summaries(self, limit: int = 4) -> List[Dict[str, Any]]:
        """Get recent weekly summaries."""
        user = get_active_user()
        if not user:
            return []

        summaries = self._load_summaries(user)
        return sorted(summaries, key=lambda x: x.get("week_start", ""), reverse=True)[:limit]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_loop: Optional[FeedbackLoop] = None


def get_feedback_loop() -> FeedbackLoop:
    """Get the singleton feedback loop."""
    global _loop
    if _loop is None:
        _loop = FeedbackLoop()
    return _loop


def generate_report(week_offset: int = 0) -> WeeklySummary:
    """Generate weekly report."""
    return get_feedback_loop().generate_weekly_report(week_offset)


def get_trends(weeks: int = 4) -> Dict[str, Any]:
    """Get trend analysis."""
    return get_feedback_loop().get_trend_analysis(weeks)


def get_insights() -> Dict[str, Any]:
    """Get technique insights."""
    return get_feedback_loop().get_technique_insights()
