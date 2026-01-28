"""
Instagram Platform Adapter - Instagram specific rules and optimization.
"""

import re
from typing import Dict, Any

from .base import PlatformAdapter, LengthConfig, TimeWindow
from . import register_adapter


@register_adapter
class InstagramAdapter(PlatformAdapter):
    """
    Instagram platform adapter.

    Optimized for visual-first content with engaging captions.
    """

    platform_name = "instagram"

    # Length configs
    caption_length = LengthConfig(
        min=50,
        optimal_min=150,
        optimal_max=200,
        max=2200
    )

    post_length = LengthConfig(
        min=50,
        optimal_min=150,
        optimal_max=200,
        max=2200
    )

    comment_length = LengthConfig(
        min=5,
        optimal_min=20,
        optimal_max=50,
        max=200
    )

    reply_length = LengthConfig(
        min=5,
        optimal_min=20,
        optimal_max=50,
        max=200
    )

    # Best posting times (EST)
    best_times = [
        TimeWindow(11, 13, "EST"),    # Lunch break
        TimeWindow(19, 21, "EST"),    # Evening scroll
    ]

    best_days = ["Tuesday", "Wednesday", "Thursday", "Friday"]
    worst_days = ["Sunday"]

    # Effective hooks for Instagram
    effective_hooks = [
        "scroll_stopper",    # Visual hook description
        "question",          # Engagement driver
        "bold_statement",    # Strong opener
        "curiosity_gap",     # Tease content
        "relatable",         # Connect with audience
    ]

    # Platform rules
    rules = {
        "do": [
            "First line = scroll stopper (shows before 'more')",
            "Use carousels - they get 3x more reach than single images",
            "Put 5-10 relevant hashtags at end of caption",
            "Reply to every comment within 1 hour",
            "Use Stories for engagement, Posts for followers",
            "Reels for discovery, Posts for community",
            "Add CTA - 'Save this', 'Share with someone'",
            "Use emojis to add personality (but don't overdo)",
        ],
        "dont": [
            "Don't use irrelevant hashtags for reach",
            "Avoid more than 10-15 hashtags",
            "Don't ignore comments - hurts algorithm",
            "Don't post blurry or low-quality images",
            "Avoid engagement bait ('like if you agree')",
            "Don't use banned hashtags",
        ],
        "tips": [
            "Carousels > single images > video for reach",
            "First slide of carousel needs strong hook",
            "Add location tags for local discovery",
            "Use 'Add Yours' stickers in Stories",
            "Collaborate with others using Collab feature",
            "Mix Reels, Posts, and Stories for best results",
            "Batch content creation for consistency",
        ],
    }

    def format_for_platform(self, content: str, content_type: str = "post") -> str:
        """Format content for Instagram."""
        if content_type in ["post", "caption"]:
            # Collect hashtags
            hashtags = re.findall(r'#\w+', content)

            if hashtags:
                # Remove hashtags from body
                for tag in hashtags:
                    content = content.replace(tag, '').strip()

                # Clean up
                content = re.sub(r' +', ' ', content)
                content = re.sub(r'\n{3,}', '\n\n', content)

                # Add hashtags at end (keep 5-10)
                unique_tags = list(dict.fromkeys(hashtags))[:10]
                content = content.strip() + '\n\n' + ' '.join(unique_tags)

        # Ensure within limit
        if len(content) > 2200:
            content = content[:2197] + "..."

        return content.strip()

    def score_platform_fit(self, content: str, content_type: str = "post") -> Dict[str, Any]:
        """Score content fit for Instagram."""
        result = super().score_platform_fit(content, content_type)
        score = result["score"]
        issues = result["issues"]

        # Check first line (shows before "more")
        first_line = content.split('\n')[0].strip()
        if len(first_line) > 125:
            issues.append("First line too long - will be truncated")
            score -= 10

        # Check hashtag count for posts
        if content_type in ["post", "caption"]:
            hashtag_count = len(re.findall(r'#\w+', content))
            if hashtag_count < 5:
                issues.append(f"Add more hashtags ({hashtag_count}, aim for 5-10)")
                score -= 10
            elif hashtag_count > 15:
                issues.append(f"Too many hashtags ({hashtag_count}, max 15)")
                score -= 15

        # Check for CTA
        cta_words = ['save', 'share', 'comment', 'tag', 'follow', 'link', 'bio', 'dm']
        has_cta = any(word in content.lower() for word in cta_words)
        if content_type in ["post", "caption"] and not has_cta:
            issues.append("Consider adding a CTA (save, share, comment, etc.)")
            score -= 5

        # Check for emoji usage
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        emoji_count = len(emoji_pattern.findall(content))
        if emoji_count == 0 and content_type in ["post", "caption"]:
            issues.append("Consider adding emojis for personality")
            score -= 3
        elif emoji_count > 10:
            issues.append("Too many emojis - keep it balanced")
            score -= 5

        result["score"] = max(0, min(100, score))
        result["issues"] = issues
        return result
