"""
Twitter Platform Adapter - Twitter/X specific rules and optimization.
"""

import re
from typing import Dict, Any

from .base import PlatformAdapter, LengthConfig, TimeWindow
from . import register_adapter


@register_adapter
class TwitterAdapter(PlatformAdapter):
    """
    Twitter/X platform adapter.

    Optimized for fast, punchy content with strong hooks.
    """

    platform_name = "twitter"

    # Length configs
    reply_length = LengthConfig(
        min=40,
        optimal_min=70,
        optimal_max=100,
        max=280
    )

    post_length = LengthConfig(
        min=100,
        optimal_min=200,
        optimal_max=280,
        max=280
    )

    # Best posting times (EST)
    best_times = [
        TimeWindow(8, 9, "EST"),      # Morning commute
        TimeWindow(12, 13, "EST"),    # Lunch break
        TimeWindow(17, 18, "EST"),    # End of workday
        TimeWindow(19, 20, "EST"),    # Evening wind-down
    ]

    best_days = ["Tuesday", "Wednesday", "Thursday"]
    worst_days = ["Saturday", "Sunday"]

    # Effective hooks for Twitter
    effective_hooks = [
        "contrarian",      # Hot takes perform well
        "data",            # Numbers grab attention
        "question",        # Drives engagement
        "urgency",         # Breaking news style
        "breaking",        # News hooks
        "bold_claim",      # Strong statements
    ]

    # Platform rules
    rules = {
        "do": [
            "Hook in first 5 words - attention spans are short",
            "One idea per tweet - clarity wins",
            "Quote tweet > retweet for reach and visibility",
            "Reply within 30 min of viral posts",
            "Use threads for complex topics (number them 1/, 2/, etc)",
            "Add value in replies - insight, not just agreement",
            "Engage with larger accounts via quality replies",
        ],
        "dont": [
            "No links in replies - kills visibility in algorithm",
            "Don't start with @ mention (makes it a reply, not visible)",
            "Avoid walls of text - use line breaks",
            "Don't be generic - specificity wins",
            "Don't over-hashtag (1-2 max, none is often better)",
            "Don't quote tweet to criticize - bad look",
        ],
        "tips": [
            "Contrarian takes get 10x more engagement than agreement",
            "Data-driven posts outperform opinion posts",
            "Reply speed matters - first quality reply often wins",
            "Build relationships through consistent engagement",
            "Screenshot interesting content for quote tweets",
            "Use thread emoji to signal thread",
        ],
    }

    def format_for_platform(self, content: str, content_type: str = "post") -> str:
        """Format content for Twitter."""
        # Ensure under character limit
        if len(content) > 280:
            # Try to truncate at sentence boundary
            truncated = content[:277]
            last_period = truncated.rfind('.')
            last_question = truncated.rfind('?')
            last_exclaim = truncated.rfind('!')
            cut_point = max(last_period, last_question, last_exclaim)

            if cut_point > 200:
                content = content[:cut_point + 1]
            else:
                content = content[:277] + "..."

        # Remove excessive hashtags (keep max 2)
        hashtags = re.findall(r'#\w+', content)
        if len(hashtags) > 2:
            for tag in hashtags[2:]:
                content = content.replace(tag, '').strip()

        # Clean up multiple spaces
        content = re.sub(r' +', ' ', content)

        return content.strip()

    def score_platform_fit(self, content: str, content_type: str = "post") -> Dict[str, Any]:
        """Score content fit for Twitter."""
        result = super().score_platform_fit(content, content_type)
        score = result["score"]
        issues = result["issues"]

        # Check for links in replies
        if content_type == "reply" and re.search(r'https?://', content):
            issues.append("Links in replies hurt visibility")
            score -= 20

        # Check hashtag count
        hashtag_count = len(re.findall(r'#\w+', content))
        if hashtag_count > 2:
            issues.append(f"Too many hashtags ({hashtag_count}, max 2 recommended)")
            score -= 10

        # Check if starts with @ (hidden reply)
        if content.strip().startswith('@'):
            issues.append("Starting with @ makes tweet less visible")
            score -= 15

        # Check hook strength (first 5 words)
        first_words = ' '.join(content.split()[:5]).lower()
        hook_words = ['why', 'how', 'what', 'breaking', 'just', 'new', 'stop', 'never', 'always']
        has_strong_start = any(word in first_words for word in hook_words)
        if not has_strong_start and content_type == "post":
            issues.append("Consider stronger hook in first 5 words")
            score -= 5

        # Bonus for data
        if re.search(r'\d+%|\$[\d,]+|\d+x', content):
            score = min(100, score + 5)

        result["score"] = max(0, min(100, score))
        result["issues"] = issues
        return result
