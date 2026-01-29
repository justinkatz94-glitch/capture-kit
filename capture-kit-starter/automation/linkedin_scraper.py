"""
LinkedIn Content Scraper

Scrapes a user's LinkedIn posts and articles to:
1. Build their voice profile from actual content
2. Extract patterns and style
3. Import benchmark posts from top performers

Note: LinkedIn doesn't have a public API, so this module supports:
- Manual post entry
- RSS feed parsing (if available)
- Future: Browser automation integration
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .schemas import generate_id, now_iso, load_json, save_json

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VOICE_DATA_DIR = DATA_DIR / "voice_samples"


@dataclass
class LinkedInContent:
    """A piece of LinkedIn content (post or article)."""
    id: str
    author: str
    content_type: str  # "post", "article", "newsletter", "comment"
    content: str
    url: str = ""
    posted_at: str = ""

    # Engagement
    likes: int = 0
    comments: int = 0
    shares: int = 0

    # Article-specific
    title: str = ""  # For articles
    read_time: int = 0  # Minutes

    # Analysis (filled after import)
    word_count: int = 0
    hook_type: str = ""
    has_line_breaks: bool = False
    has_emoji: bool = False
    has_hashtags: bool = False
    has_images: bool = False
    topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'LinkedInContent':
        return cls(**data)


class LinkedInVoiceBuilder:
    """
    Builds a voice profile from a user's LinkedIn content.

    Analyzes their posts and articles to extract:
    - Writing patterns
    - Common phrases
    - Tone and style
    - Content structure preferences
    """

    def __init__(self, user_name: str):
        """Initialize voice builder for a user."""
        VOICE_DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.user_name = user_name
        self.content: List[LinkedInContent] = []
        self._load_content()

    def _get_data_path(self) -> Path:
        """Get path to user's voice data file."""
        filename = self.user_name.lower().replace(' ', '_')
        return VOICE_DATA_DIR / f"{filename}_linkedin_content.json"

    def _load_content(self):
        """Load existing content."""
        path = self._get_data_path()
        if path.exists():
            data = load_json(str(path))
            self.content = [
                LinkedInContent.from_dict(c) for c in data.get("content", [])
            ]

    def _save_content(self):
        """Save content data."""
        path = self._get_data_path()
        save_json(str(path), {
            "user": self.user_name,
            "content": [c.to_dict() for c in self.content],
            "updated_at": now_iso(),
        })

    def add_post(
        self,
        content: str,
        url: str = "",
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
        posted_at: str = ""
    ) -> Dict[str, Any]:
        """
        Add a LinkedIn post from this user.

        Args:
            content: Post text
            url: LinkedIn post URL
            likes: Like count
            comments: Comment count
            shares: Share count
            posted_at: When posted (ISO format)

        Returns:
            Result with analysis
        """
        post = LinkedInContent(
            id=generate_id(),
            author=self.user_name,
            content_type="post",
            content=content,
            url=url,
            posted_at=posted_at or now_iso(),
            likes=likes,
            comments=comments,
            shares=shares,
        )

        # Analyze
        post = self._analyze_content(post)

        self.content.append(post)
        self._save_content()

        return {
            "status": "success",
            "id": post.id,
            "type": "post",
            "word_count": post.word_count,
            "hook_type": post.hook_type,
            "total_posts": len(self.content),
        }

    def add_article(
        self,
        title: str,
        content: str,
        url: str = "",
        likes: int = 0,
        comments: int = 0,
        read_time: int = 0,
        posted_at: str = ""
    ) -> Dict[str, Any]:
        """
        Add a LinkedIn article from this user.

        Args:
            title: Article title
            content: Article body (or excerpt)
            url: Article URL
            likes: Like count
            comments: Comment count
            read_time: Read time in minutes
            posted_at: When published

        Returns:
            Result with analysis
        """
        article = LinkedInContent(
            id=generate_id(),
            author=self.user_name,
            content_type="article",
            content=content,
            title=title,
            url=url,
            posted_at=posted_at or now_iso(),
            likes=likes,
            comments=comments,
            read_time=read_time,
        )

        article = self._analyze_content(article)

        self.content.append(article)
        self._save_content()

        return {
            "status": "success",
            "id": article.id,
            "type": "article",
            "title": title,
            "word_count": article.word_count,
            "total_content": len(self.content),
        }

    def _analyze_content(self, item: LinkedInContent) -> LinkedInContent:
        """Analyze content and fill in analysis fields."""
        content = item.content

        # Word count
        item.word_count = len(content.split())

        # Line breaks
        item.has_line_breaks = '\n\n' in content or content.count('\n') > 3

        # Emoji
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "]+"
        )
        item.has_emoji = bool(emoji_pattern.search(content))

        # Hashtags
        item.has_hashtags = '#' in content

        # Hook type
        first_line = content.split('\n')[0].strip()
        item.hook_type = self._detect_hook(first_line)

        return item

    def _detect_hook(self, first_line: str) -> str:
        """Detect hook type from first line."""
        first_lower = first_line.lower()

        if '?' in first_line:
            return "question"
        if re.search(r'^\d|%|\$', first_line):
            return "data"
        if first_lower.startswith(('i ', "i've", "i'm", 'my ', 'when i', 'last ')):
            return "personal_story"
        if first_lower.startswith(('the ', 'this ', "here's")):
            return "bold_claim"
        if any(s in first_lower for s in ['unpopular', 'controversial', 'nobody', 'stop']):
            return "contrarian"
        if re.search(r'^\d+\s*(things?|ways?|tips?|lessons?)', first_lower):
            return "list"

        return "statement"

    def extract_voice_profile(self) -> Dict[str, Any]:
        """
        Extract voice profile from all content.

        Returns patterns, phrases, and style characteristics.
        """
        if not self.content:
            return {"error": "No content to analyze. Add posts first."}

        posts = [c for c in self.content if c.content_type == "post"]
        articles = [c for c in self.content if c.content_type == "article"]

        # Aggregate stats
        all_text = " ".join([c.content for c in self.content])
        words = all_text.split()

        # Find common phrases (2-4 word sequences that appear multiple times)
        common_phrases = self._extract_common_phrases(all_text)

        # Hook type distribution
        hook_types = {}
        for c in self.content:
            hook_types[c.hook_type] = hook_types.get(c.hook_type, 0) + 1

        # Style patterns
        line_break_pct = sum(1 for c in self.content if c.has_line_breaks) / len(self.content) * 100
        emoji_pct = sum(1 for c in self.content if c.has_emoji) / len(self.content) * 100
        hashtag_pct = sum(1 for c in self.content if c.has_hashtags) / len(self.content) * 100

        # Word count stats
        word_counts = [c.word_count for c in self.content]
        avg_word_count = sum(word_counts) / len(word_counts)

        # Common sentence starters
        sentence_starters = self._extract_sentence_starters(all_text)

        return {
            "user": self.user_name,
            "content_analyzed": {
                "posts": len(posts),
                "articles": len(articles),
                "total": len(self.content),
            },
            "voice_characteristics": {
                "avg_word_count": round(avg_word_count),
                "preferred_hooks": dict(sorted(hook_types.items(), key=lambda x: x[1], reverse=True)),
                "uses_line_breaks": line_break_pct > 50,
                "uses_emoji": emoji_pct > 30,
                "uses_hashtags": hashtag_pct > 30,
            },
            "signature_phrases": common_phrases[:10],
            "common_openers": sentence_starters[:10],
            "style_metrics": {
                "line_break_usage": f"{line_break_pct:.0f}%",
                "emoji_usage": f"{emoji_pct:.0f}%",
                "hashtag_usage": f"{hashtag_pct:.0f}%",
            },
        }

    def _extract_common_phrases(self, text: str) -> List[str]:
        """Extract commonly used phrases."""
        # Simple approach: find repeated 3-4 word sequences
        words = text.lower().split()
        phrases = {}

        for n in [3, 4]:
            for i in range(len(words) - n):
                phrase = " ".join(words[i:i+n])
                # Skip if contains common stop words only
                if any(w in phrase for w in ['the', 'a', 'an', 'is', 'are', 'was', 'were']):
                    continue
                phrases[phrase] = phrases.get(phrase, 0) + 1

        # Filter to phrases that appear multiple times
        repeated = [(p, c) for p, c in phrases.items() if c >= 2]
        repeated.sort(key=lambda x: x[1], reverse=True)

        return [p for p, _ in repeated[:20]]

    def _extract_sentence_starters(self, text: str) -> List[str]:
        """Extract common sentence starters."""
        sentences = re.split(r'[.!?]\s+', text)
        starters = {}

        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) >= 2:
                starter = " ".join(words[:2])
                starters[starter] = starters.get(starter, 0) + 1

        sorted_starters = sorted(starters.items(), key=lambda x: x[1], reverse=True)
        return [s for s, c in sorted_starters if c >= 2][:10]

    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about imported content."""
        posts = [c for c in self.content if c.content_type == "post"]
        articles = [c for c in self.content if c.content_type == "article"]

        total_engagement = sum(c.likes + c.comments + c.shares for c in self.content)

        return {
            "user": self.user_name,
            "posts": len(posts),
            "articles": len(articles),
            "total": len(self.content),
            "total_engagement": total_engagement,
            "avg_engagement": total_engagement / max(len(self.content), 1),
        }


# =============================================================================
# LINKEDIN CONTENT TYPE BEST PRACTICES
# =============================================================================

LINKEDIN_CONTENT_TYPES = {
    "post": {
        "name": "LinkedIn Post",
        "max_length": 3000,
        "optimal_length": {"min": 150, "max": 300, "ideal": 200},
        "best_practices": [
            "First line is critical - it shows in feed preview",
            "Use line breaks every 1-2 sentences",
            "Include a hook in the first line",
            "End with a question or call to engagement",
            "Avoid external links (algorithm penalty)",
            "Personal stories outperform generic advice",
        ],
        "effective_hooks": ["personal_story", "contrarian", "question", "data"],
        "posting_times": ["7-8am", "12pm", "5-6pm"],
        "best_days": ["Tuesday", "Wednesday", "Thursday"],
    },
    "article": {
        "name": "LinkedIn Article",
        "max_length": 125000,
        "optimal_length": {"min": 1000, "max": 3000, "ideal": 1500},
        "best_practices": [
            "Strong headline is essential",
            "Include a compelling cover image",
            "Use headers to break up sections",
            "Include actionable takeaways",
            "Cross-promote in a post",
            "Longer articles rank better in search",
        ],
        "effective_hooks": ["how_to", "list", "case_study", "contrarian"],
        "posting_times": ["Tuesday morning", "Thursday morning"],
        "best_days": ["Tuesday", "Thursday"],
    },
    "newsletter": {
        "name": "LinkedIn Newsletter",
        "max_length": 125000,
        "optimal_length": {"min": 500, "max": 2000, "ideal": 1000},
        "best_practices": [
            "Consistent publishing schedule is key",
            "Build email-like relationship with subscribers",
            "Include exclusive insights",
            "Use a conversational tone",
            "Repurpose top posts into newsletter content",
        ],
        "effective_hooks": ["personal_story", "exclusive_insight", "curated_list"],
        "frequency": "Weekly or bi-weekly",
    },
    "comment": {
        "name": "LinkedIn Comment",
        "max_length": 1250,
        "optimal_length": {"min": 30, "max": 150, "ideal": 75},
        "best_practices": [
            "Add value, don't just agree",
            "Share your perspective or experience",
            "Ask a thoughtful follow-up question",
            "Be one of the first commenters",
            "Engage with other commenters",
        ],
        "effective_hooks": ["personal_experience", "question", "contrarian_view"],
    },
}


def get_content_type_best_practices(content_type: str) -> Dict[str, Any]:
    """Get best practices for a LinkedIn content type."""
    return LINKEDIN_CONTENT_TYPES.get(content_type, {})


def get_all_content_types() -> Dict[str, Any]:
    """Get all LinkedIn content types and their best practices."""
    return LINKEDIN_CONTENT_TYPES
