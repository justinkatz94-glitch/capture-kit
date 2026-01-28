"""
LinkedIn Platform Adapter - LinkedIn specific rules and optimization.
"""

import re
from typing import Dict, Any

from .base import PlatformAdapter, LengthConfig, TimeWindow
from . import register_adapter


@register_adapter
class LinkedInAdapter(PlatformAdapter):
    """
    LinkedIn platform adapter.

    Optimized for professional, story-driven content with depth.
    """

    platform_name = "linkedin"

    # Length configs
    comment_length = LengthConfig(
        min=50,
        optimal_min=100,
        optimal_max=300,
        max=500
    )

    reply_length = LengthConfig(
        min=50,
        optimal_min=100,
        optimal_max=300,
        max=500
    )

    post_length = LengthConfig(
        min=800,
        optimal_min=1200,
        optimal_max=1500,
        max=3000
    )

    # Best posting times (EST)
    best_times = [
        TimeWindow(8, 10, "EST", ["Tue", "Wed", "Thu"]),
        TimeWindow(12, 12, "EST", ["Tue", "Wed", "Thu"]),
    ]

    best_days = ["Tuesday", "Wednesday", "Thursday"]
    worst_days = ["Saturday", "Sunday"]

    # Effective hooks for LinkedIn
    effective_hooks = [
        "story_opener",     # Personal narrative start
        "bold_claim",       # Strong statement
        "question",         # Engagement driver
        "vulnerability",    # Authentic sharing
        "contrarian",       # Challenges assumptions
        "lesson_learned",   # Teaching moment
        "pattern_interrupt", # Unexpected opener
    ]

    # Platform rules
    rules = {
        "do": [
            "First line is EVERYTHING - it shows before 'see more'",
            "Line break after every 1-2 sentences for readability",
            "Personal stories beat corporate speak",
            "End with question or CTA to drive engagement",
            "Comment on others' posts before/after your own post",
            "Use document/carousel posts - they get 3x reach",
            "Share lessons learned, not just wins",
            "Be authentic - vulnerability resonates",
        ],
        "dont": [
            "NO external links in post body - kills reach by 50%+",
            "Don't use hashtags in body text - looks amateur",
            "Avoid corporate jargon and buzzwords",
            "Don't post on weekends - low engagement",
            "Don't just share content - add your perspective",
            "Avoid walls of text without line breaks",
            "Don't be salesy or promotional",
        ],
        "tips": [
            "Put links in FIRST COMMENT, not in post",
            "Hashtags at very end only, max 3-5",
            "Reply to every comment on your posts",
            "Use 'I' statements - personal > corporate",
            "Numbers in first line increase clicks",
            "Edit within first hour if needed (no penalty)",
            "Engage for 30 min after posting for algorithm boost",
            "Document posts (PDF carousels) get massive reach",
        ],
    }

    def format_for_platform(self, content: str, content_type: str = "post") -> str:
        """Format content for LinkedIn."""
        if content_type == "post":
            # Ensure line breaks after sentences for readability
            # Split into sentences and add line breaks
            sentences = re.split(r'(?<=[.!?])\s+', content)
            formatted_lines = []
            current_para = []

            for i, sentence in enumerate(sentences):
                current_para.append(sentence)
                # Add line break every 1-2 sentences
                if len(current_para) >= 2 or (len(current_para) == 1 and len(sentence) > 100):
                    formatted_lines.append(' '.join(current_para))
                    current_para = []

            if current_para:
                formatted_lines.append(' '.join(current_para))

            content = '\n\n'.join(formatted_lines)

            # Move hashtags to end if scattered throughout
            hashtags = re.findall(r'#\w+', content)
            if hashtags:
                # Remove hashtags from body
                for tag in hashtags:
                    content = content.replace(tag, '').strip()
                # Clean up multiple spaces/newlines
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = re.sub(r' +', ' ', content)
                # Add hashtags at end (max 5)
                unique_tags = list(dict.fromkeys(hashtags))[:5]
                content = content.strip() + '\n\n' + ' '.join(unique_tags)

        return content.strip()

    def score_platform_fit(self, content: str, content_type: str = "post") -> Dict[str, Any]:
        """Score content fit for LinkedIn."""
        result = super().score_platform_fit(content, content_type)
        score = result["score"]
        issues = result["issues"]

        # Check for external links in post body
        if content_type == "post" and re.search(r'https?://', content):
            issues.append("External links in post body reduce reach by 50%+ - put in first comment")
            score -= 30

        # Check first line length (shows before "see more")
        first_line = content.split('\n')[0].strip()
        if len(first_line) > 150:
            issues.append("First line too long - will be truncated before 'see more'")
            score -= 15

        # Check for line breaks in posts
        if content_type == "post":
            line_count = content.count('\n')
            word_count = len(content.split())
            if word_count > 100 and line_count < 3:
                issues.append("Add more line breaks for readability")
                score -= 10

        # Check hashtag placement
        hashtags = re.findall(r'#\w+', content)
        if hashtags:
            # Check if hashtags are scattered in body
            body_without_last_para = '\n'.join(content.split('\n')[:-1])
            if any(tag in body_without_last_para for tag in hashtags):
                issues.append("Move hashtags to end of post")
                score -= 5

            if len(hashtags) > 5:
                issues.append(f"Too many hashtags ({len(hashtags)}, max 5)")
                score -= 10

        # Check for CTA/question at end
        last_line = content.strip().split('\n')[-1].lower()
        has_cta = any(word in last_line for word in ['?', 'comment', 'share', 'thoughts', 'agree'])
        if content_type == "post" and not has_cta:
            issues.append("Consider ending with a question or CTA")
            score -= 5

        # Bonus for personal language
        if re.search(r'\bI\b|\bmy\b|\bme\b', content, re.IGNORECASE):
            score = min(100, score + 5)

        result["score"] = max(0, min(100, score))
        result["issues"] = issues
        return result
