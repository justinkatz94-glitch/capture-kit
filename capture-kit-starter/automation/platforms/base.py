"""
Base Platform Adapter - Abstract base class for all platform adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LengthConfig:
    """Configuration for content length."""
    min: int
    optimal_min: int
    optimal_max: int
    max: int

    def is_optimal(self, length: int) -> bool:
        """Check if length is in optimal range."""
        return self.optimal_min <= length <= self.optimal_max

    def is_valid(self, length: int) -> bool:
        """Check if length is within valid range."""
        return self.min <= length <= self.max

    def score(self, length: int) -> int:
        """Score length from 0-100."""
        if length < self.min:
            return max(0, 50 - (self.min - length) * 5)
        elif length > self.max:
            return max(0, 50 - (length - self.max) * 2)
        elif self.is_optimal(length):
            return 100
        elif length < self.optimal_min:
            # Between min and optimal_min
            ratio = (length - self.min) / (self.optimal_min - self.min)
            return int(70 + ratio * 30)
        else:
            # Between optimal_max and max
            ratio = (self.max - length) / (self.max - self.optimal_max)
            return int(70 + ratio * 30)


@dataclass
class TimeWindow:
    """Time window for posting."""
    start_hour: int
    end_hour: int
    timezone: str = "EST"
    days: List[str] = None  # None = all days

    def __post_init__(self):
        if self.days is None:
            self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def to_string(self) -> str:
        """Human-readable format."""
        time_str = f"{self.start_hour}:00-{self.end_hour}:00 {self.timezone}"
        if len(self.days) < 7:
            return f"{', '.join(self.days)} {time_str}"
        return time_str


class PlatformAdapter(ABC):
    """
    Abstract base class for platform-specific adapters.

    Each platform has different rules, optimal lengths, and best practices.
    Adapters encode this knowledge to help generate platform-optimized content.
    """

    # Override in subclasses
    platform_name: str = "base"

    # Content length configs
    reply_length: LengthConfig = None
    post_length: LengthConfig = None
    comment_length: LengthConfig = None  # For platforms that distinguish

    # Timing
    best_times: List[TimeWindow] = []
    best_days: List[str] = []
    worst_days: List[str] = []

    # Content strategy
    effective_hooks: List[str] = []

    # Platform rules (dos and donts)
    rules: Dict[str, List[str]] = {
        "do": [],
        "dont": [],
        "tips": [],
    }

    def get_length_config(self, content_type: str = "post") -> Optional[LengthConfig]:
        """Get length config for content type."""
        configs = {
            "post": self.post_length,
            "reply": self.reply_length,
            "comment": self.comment_length or self.reply_length,
        }
        return configs.get(content_type)

    def format_for_platform(self, content: str, content_type: str = "post") -> str:
        """
        Format content for this platform.

        Override in subclasses for platform-specific formatting.

        Args:
            content: Raw content
            content_type: Type of content (post, reply, comment)

        Returns:
            Formatted content
        """
        return content

    def score_platform_fit(self, content: str, content_type: str = "post") -> Dict[str, Any]:
        """
        Score how well content fits this platform.

        Args:
            content: Content to score
            content_type: Type of content

        Returns:
            Dict with score (0-100) and issues list
        """
        issues = []
        score = 100

        # Length scoring
        length_config = self.get_length_config(content_type)
        if length_config:
            char_count = len(content)
            word_count = len(content.split())

            length_score = length_config.score(char_count)
            if length_score < 70:
                if char_count < length_config.min:
                    issues.append(f"Too short ({char_count} chars, min {length_config.min})")
                elif char_count > length_config.max:
                    issues.append(f"Too long ({char_count} chars, max {length_config.max})")
                elif char_count < length_config.optimal_min:
                    issues.append(f"Below optimal length ({char_count} chars, aim for {length_config.optimal_min}+)")
                elif char_count > length_config.optimal_max:
                    issues.append(f"Above optimal length ({char_count} chars, aim for {length_config.optimal_max} or less)")

            # Weight length as 40% of score
            score = int(score * 0.6 + length_score * 0.4)

        # Hook check (first line analysis)
        first_line = content.split('\n')[0].strip()
        if len(first_line) > 100:
            issues.append("First line too long - may get truncated")
            score -= 10

        return {
            "score": max(0, min(100, score)),
            "issues": issues,
            "length_config": {
                "chars": len(content),
                "words": len(content.split()),
                "optimal_range": f"{length_config.optimal_min}-{length_config.optimal_max}" if length_config else "N/A",
            }
        }

    def get_system_prompt_rules(self, content_type: str = "post") -> str:
        """
        Get platform rules formatted for LLM system prompt.

        Args:
            content_type: Type of content being generated

        Returns:
            Formatted rules string for LLM
        """
        length_config = self.get_length_config(content_type)

        lines = [
            f"## {self.platform_name.upper()} PLATFORM RULES",
            "",
        ]

        # Length requirements
        if length_config:
            lines.extend([
                f"### Length Requirements ({content_type})",
                f"- Minimum: {length_config.min} characters",
                f"- Optimal: {length_config.optimal_min}-{length_config.optimal_max} characters",
                f"- Maximum: {length_config.max} characters",
                "",
            ])

        # Best times
        if self.best_times:
            lines.append("### Best Posting Times")
            for window in self.best_times:
                lines.append(f"- {window.to_string()}")
            lines.append("")

        # Effective hooks
        if self.effective_hooks:
            lines.extend([
                "### Effective Hook Types",
                f"- {', '.join(self.effective_hooks)}",
                "",
            ])

        # Rules
        if self.rules.get("do"):
            lines.append("### DO:")
            for rule in self.rules["do"]:
                lines.append(f"- {rule}")
            lines.append("")

        if self.rules.get("dont"):
            lines.append("### DON'T:")
            for rule in self.rules["dont"]:
                lines.append(f"- {rule}")
            lines.append("")

        if self.rules.get("tips"):
            lines.append("### TIPS:")
            for tip in self.rules["tips"]:
                lines.append(f"- {tip}")
            lines.append("")

        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of this adapter's configuration."""
        return {
            "platform": self.platform_name,
            "post_length": {
                "min": self.post_length.min if self.post_length else None,
                "optimal": f"{self.post_length.optimal_min}-{self.post_length.optimal_max}" if self.post_length else None,
                "max": self.post_length.max if self.post_length else None,
            },
            "reply_length": {
                "min": self.reply_length.min if self.reply_length else None,
                "optimal": f"{self.reply_length.optimal_min}-{self.reply_length.optimal_max}" if self.reply_length else None,
                "max": self.reply_length.max if self.reply_length else None,
            },
            "best_times": [w.to_string() for w in self.best_times],
            "best_days": self.best_days,
            "worst_days": self.worst_days,
            "effective_hooks": self.effective_hooks,
            "rules": self.rules,
        }
