"""
Benchmark Manager - Analyze top performers and viral posts

This module provides tools for:
- Storing and managing benchmark data (top accounts, viral posts)
- Analyzing what makes posts successful
- Comparing your profile to benchmarks
- Generating actionable recommendations
"""

import json
import re
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# Get the benchmarks directory
BENCHMARKS_DIR = Path(__file__).parent


def get_benchmark_path(name: str) -> Path:
    """Get path to a benchmark file."""
    return BENCHMARKS_DIR / f"{name}.json"


class BenchmarkManager:
    """
    Manages benchmark data for a specific niche/category.
    """

    def __init__(self, name: str):
        """
        Initialize a benchmark manager.

        Args:
            name: Benchmark name (e.g., 'finance_twitter', 'tech_linkedin')
        """
        self.name = name
        self.path = get_benchmark_path(name)
        self.data = self._load_or_create()

    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing benchmark or create new one."""
        if self.path.exists():
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "name": self.name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "top_accounts": [],
            "viral_posts": [],
            "patterns": {
                "hooks": [],
                "structures": [],
                "optimal_length": {},
                "best_timing": {},
                "top_topics": [],
                "engagement_drivers": []
            },
            "aggregated_metrics": {}
        }

    def save(self):
        """Save benchmark data to file."""
        self.data["updated_at"] = datetime.now().isoformat()
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, default=str)

    def add_top_account(self, profile_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a top performer account to the benchmark.

        Args:
            profile_data: Raw profile data from scraper
            analysis: Style analysis from style_extractor

        Returns:
            Summary of what was added
        """
        username = profile_data.get("username", "unknown")

        # Check if already exists
        existing = [a for a in self.data["top_accounts"] if a.get("username") == username]
        if existing:
            # Update existing
            idx = self.data["top_accounts"].index(existing[0])
            self.data["top_accounts"][idx] = self._create_account_entry(profile_data, analysis)
            action = "updated"
        else:
            self.data["top_accounts"].append(self._create_account_entry(profile_data, analysis))
            action = "added"

        # Recalculate aggregate patterns
        self._recalculate_patterns()
        self.save()

        return {
            "status": "success",
            "action": action,
            "username": username,
            "posts_analyzed": len(profile_data.get("posts", [])),
            "followers": profile_data.get("profile", {}).get("followers", "unknown")
        }

    def _create_account_entry(self, profile_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """Create a standardized account entry."""
        profile = profile_data.get("profile", {})
        posts = profile_data.get("posts", [])

        # Calculate engagement metrics
        total_likes = sum(self._parse_metric(p.get("likes", 0)) for p in posts)
        total_retweets = sum(self._parse_metric(p.get("retweets", 0)) for p in posts)
        total_replies = sum(self._parse_metric(p.get("replies", 0)) for p in posts)

        avg_engagement = (total_likes + total_retweets + total_replies) / max(len(posts), 1)

        # Find top performing posts
        posts_with_engagement = []
        for p in posts:
            eng = (self._parse_metric(p.get("likes", 0)) +
                   self._parse_metric(p.get("retweets", 0)) +
                   self._parse_metric(p.get("replies", 0)))
            posts_with_engagement.append((eng, p))

        posts_with_engagement.sort(reverse=True, key=lambda x: x[0])
        top_posts = [p for _, p in posts_with_engagement[:10]]

        return {
            "username": profile_data.get("username", profile.get("username", "unknown")),
            "name": profile.get("name", ""),
            "bio": profile.get("bio", ""),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "total_posts": profile.get("tweets_count", len(posts)),
            "analyzed_posts": len(posts),
            "added_at": datetime.now().isoformat(),
            "metrics": {
                "avg_likes": total_likes / max(len(posts), 1),
                "avg_retweets": total_retweets / max(len(posts), 1),
                "avg_replies": total_replies / max(len(posts), 1),
                "avg_engagement": avg_engagement,
                "engagement_rate": self._calculate_engagement_rate(avg_engagement, profile.get("followers", 1))
            },
            "style": {
                "vocabulary_level": analysis.get("vocabulary", {}).get("level", "unknown"),
                "tone_energy": analysis.get("tone", {}).get("energy", "unknown"),
                "emoji_style": analysis.get("emoji_usage", {}).get("style", "unknown"),
                "emoji_per_post": analysis.get("emoji_usage", {}).get("per_post", 0),
                "hashtag_style": analysis.get("hashtag_style", {}).get("style", "unknown"),
                "avg_post_length": analysis.get("by_platform", {}).get("twitter", {}).get("avg_words", 0),
                "sentence_style": analysis.get("writing_metrics", {}).get("sentence_style", "unknown"),
                "posting_time": analysis.get("posting_patterns", {}).get("time_preference", "unknown"),
                "peak_hours": analysis.get("posting_patterns", {}).get("peak_hours", []),
                "peak_days": analysis.get("posting_patterns", {}).get("peak_days", []),
            },
            "signature_words": analysis.get("vocabulary", {}).get("signature_words", [])[:20],
            "topics": analysis.get("topics", []),
            "top_posts": top_posts,
            "raw_analysis": analysis
        }

    def _parse_metric(self, value) -> int:
        """Parse engagement metric that might be string or int."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            # Handle "1.2K", "5M", etc.
            value = value.strip().upper()
            if not value or value == "0":
                return 0
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            for suffix, mult in multipliers.items():
                if value.endswith(suffix):
                    try:
                        return int(float(value[:-1]) * mult)
                    except:
                        return 0
            try:
                return int(value.replace(',', ''))
            except:
                return 0
        return 0

    def _calculate_engagement_rate(self, avg_engagement: float, followers: int) -> float:
        """Calculate engagement rate as percentage."""
        followers = self._parse_metric(followers)
        if followers == 0:
            return 0
        return round((avg_engagement / followers) * 100, 4)

    def add_viral_post(self, post_data: Dict[str, Any], manual_analysis: str = None) -> Dict[str, Any]:
        """
        Add a viral post to the benchmark with analysis.

        Args:
            post_data: Post data (content, engagement metrics, etc.)
            manual_analysis: Optional manual notes on why it worked

        Returns:
            Analysis of the viral post
        """
        content = post_data.get("content", "")
        analysis = analyze_viral_post(post_data)

        entry = {
            "added_at": datetime.now().isoformat(),
            "content": content,
            "url": post_data.get("url", ""),
            "author": post_data.get("author", post_data.get("username", "unknown")),
            "metrics": {
                "likes": self._parse_metric(post_data.get("likes", 0)),
                "retweets": self._parse_metric(post_data.get("retweets", 0)),
                "replies": self._parse_metric(post_data.get("replies", 0)),
                "quotes": self._parse_metric(post_data.get("quotes", 0)),
            },
            "analysis": analysis,
            "manual_notes": manual_analysis or ""
        }

        self.data["viral_posts"].append(entry)
        self._recalculate_patterns()
        self.save()

        return {
            "status": "success",
            "post_preview": content[:100] + "..." if len(content) > 100 else content,
            "total_engagement": sum(entry["metrics"].values()),
            "analysis": analysis
        }

    def _recalculate_patterns(self):
        """Recalculate aggregate patterns from all data."""
        patterns = self.data["patterns"]

        # Aggregate from top accounts
        all_hooks = []
        all_lengths = []
        all_topics = []
        all_hours = []
        all_days = []
        all_styles = []

        for account in self.data["top_accounts"]:
            style = account.get("style", {})
            all_lengths.append(style.get("avg_post_length", 0))
            all_topics.extend(account.get("topics", []))
            all_hours.extend(style.get("peak_hours", []))
            all_days.extend(style.get("peak_days", []))
            all_styles.append({
                "vocabulary": style.get("vocabulary_level"),
                "tone": style.get("tone_energy"),
                "emoji": style.get("emoji_style"),
                "sentence": style.get("sentence_style"),
            })

            # Extract hooks from top posts
            for post in account.get("top_posts", [])[:5]:
                content = post.get("content", "")
                if content:
                    hook = self._extract_hook(content)
                    if hook:
                        all_hooks.append(hook)

        # Aggregate from viral posts
        for post in self.data["viral_posts"]:
            analysis = post.get("analysis", {})
            if analysis.get("hook"):
                all_hooks.append(analysis["hook"])
            all_lengths.append(analysis.get("word_count", 0))

        # Calculate patterns
        if all_lengths:
            patterns["optimal_length"] = {
                "min": min(l for l in all_lengths if l > 0) if any(l > 0 for l in all_lengths) else 0,
                "max": max(all_lengths),
                "avg": round(statistics.mean(l for l in all_lengths if l > 0), 1) if any(l > 0 for l in all_lengths) else 0,
                "median": round(statistics.median(l for l in all_lengths if l > 0), 1) if any(l > 0 for l in all_lengths) else 0,
            }

        if all_hours:
            hour_counts = Counter(all_hours)
            patterns["best_timing"]["peak_hours"] = [h for h, _ in hour_counts.most_common(3)]

        if all_days:
            day_counts = Counter(all_days)
            patterns["best_timing"]["peak_days"] = [d for d, _ in day_counts.most_common(3)]

        if all_topics:
            topic_counts = Counter(all_topics)
            patterns["top_topics"] = [t for t, _ in topic_counts.most_common(10)]

        # Analyze common hooks
        if all_hooks:
            patterns["hooks"] = self._categorize_hooks(all_hooks)

        # Aggregate style patterns
        if all_styles:
            patterns["common_styles"] = {
                "vocabulary": Counter(s["vocabulary"] for s in all_styles if s["vocabulary"]).most_common(1)[0][0] if all_styles else None,
                "tone": Counter(s["tone"] for s in all_styles if s["tone"]).most_common(1)[0][0] if all_styles else None,
                "emoji": Counter(s["emoji"] for s in all_styles if s["emoji"]).most_common(1)[0][0] if all_styles else None,
            }

        # Calculate aggregated metrics
        if self.data["top_accounts"]:
            all_eng_rates = [a.get("metrics", {}).get("engagement_rate", 0) for a in self.data["top_accounts"]]
            all_followers = [self._parse_metric(a.get("followers", 0)) for a in self.data["top_accounts"]]

            self.data["aggregated_metrics"] = {
                "avg_engagement_rate": round(statistics.mean(all_eng_rates), 4) if all_eng_rates else 0,
                "avg_followers": round(statistics.mean(all_followers), 0) if all_followers else 0,
                "total_accounts": len(self.data["top_accounts"]),
                "total_viral_posts": len(self.data["viral_posts"]),
            }

    def _extract_hook(self, content: str) -> Optional[str]:
        """Extract the hook (first line/sentence) from content."""
        content = content.strip()
        # First line
        first_line = content.split('\n')[0].strip()
        if len(first_line) > 10:
            return first_line[:150]
        # First sentence
        sentences = re.split(r'[.!?]', content)
        if sentences and len(sentences[0]) > 10:
            return sentences[0].strip()[:150]
        return None

    def _categorize_hooks(self, hooks: List[str]) -> List[Dict[str, Any]]:
        """Categorize hooks by type."""
        categorized = []
        hook_types = {
            "question": r'\?',
            "number": r'^\d+|^\$[\d,]+',
            "bold_claim": r'^(The|This|I|We|Everyone|Nobody|Never|Always)',
            "controversy": r'(wrong|mistake|lie|truth|secret|hidden)',
            "personal": r'^(I |My |We |Our )',
            "how_to": r'(How to|Here\'s how|Step)',
            "list": r'^\d+\.',
        }

        type_counts = Counter()
        type_examples = {k: [] for k in hook_types}

        for hook in hooks:
            for hook_type, pattern in hook_types.items():
                if re.search(pattern, hook, re.IGNORECASE):
                    type_counts[hook_type] += 1
                    if len(type_examples[hook_type]) < 3:
                        type_examples[hook_type].append(hook)
                    break

        for hook_type, count in type_counts.most_common():
            categorized.append({
                "type": hook_type,
                "count": count,
                "examples": type_examples[hook_type]
            })

        return categorized

    def compare_profile(self, user_profile: Dict[str, Any], user_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare a user's profile to this benchmark.

        Args:
            user_profile: User's profile data
            user_analysis: User's style analysis

        Returns:
            Detailed comparison with recommendations
        """
        return compare_to_benchmark(user_profile, user_analysis, self.data)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the benchmark."""
        return {
            "name": self.name,
            "total_accounts": len(self.data["top_accounts"]),
            "total_viral_posts": len(self.data["viral_posts"]),
            "accounts": [
                {
                    "username": a.get("username"),
                    "followers": a.get("followers"),
                    "engagement_rate": a.get("metrics", {}).get("engagement_rate")
                }
                for a in self.data["top_accounts"]
            ],
            "patterns": self.data["patterns"],
            "aggregated_metrics": self.data["aggregated_metrics"],
            "updated_at": self.data.get("updated_at")
        }


def analyze_viral_post(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze what makes a post viral/successful.

    Args:
        post_data: Post data with content and metrics

    Returns:
        Analysis of success factors
    """
    content = post_data.get("content", "")
    words = content.split()
    sentences = re.split(r'[.!?]+', content)

    analysis = {
        "word_count": len(words),
        "character_count": len(content),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "hook": None,
        "structure": None,
        "elements": [],
        "emotional_triggers": [],
        "success_factors": []
    }

    # Extract hook
    first_line = content.split('\n')[0].strip()
    analysis["hook"] = first_line[:150] if first_line else None

    # Analyze structure
    if '\n\n' in content or '\n' in content:
        lines = [l for l in content.split('\n') if l.strip()]
        if len(lines) > 3:
            analysis["structure"] = "multi_paragraph"
        else:
            analysis["structure"] = "short_form"
    else:
        analysis["structure"] = "single_block"

    # Detect elements
    elements = []
    if re.search(r'\d+', content):
        elements.append("numbers")
    if re.search(r'\$[\d,]+', content):
        elements.append("money_figures")
    if re.search(r'\?', content):
        elements.append("question")
    if re.search(r'!', content):
        elements.append("exclamation")
    if re.search(r'http[s]?://', content):
        elements.append("link")
    if re.search(r'@\w+', content):
        elements.append("mention")
    if re.search(r'#\w+', content):
        elements.append("hashtag")
    if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content):
        elements.append("emoji")

    analysis["elements"] = elements

    # Detect emotional triggers
    triggers = []
    trigger_patterns = {
        "urgency": r'(now|today|immediately|hurry|limited|last chance)',
        "curiosity": r'(secret|hidden|revealed|discover|truth)',
        "fear": r'(warning|danger|risk|mistake|avoid|never)',
        "greed": r'(profit|gain|money|wealth|rich|\$\d)',
        "social_proof": r'(everyone|people|they|most|many)',
        "authority": r'(expert|research|study|data|proven|years)',
        "exclusivity": r'(only|exclusive|rare|few|insider)',
    }

    for trigger_type, pattern in trigger_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            triggers.append(trigger_type)

    analysis["emotional_triggers"] = triggers

    # Determine success factors
    factors = []

    # Length optimization
    if 50 <= len(words) <= 150:
        factors.append("optimal_length")

    # Strong hook
    if first_line and (
        first_line.endswith('?') or
        re.search(r'^\d', first_line) or
        re.search(r'(How|What|Why|The)', first_line)
    ):
        factors.append("strong_hook")

    # Emotional appeal
    if len(triggers) >= 2:
        factors.append("emotional_appeal")

    # Easy to read
    if analysis["sentence_count"] > 0:
        avg_sentence_len = len(words) / analysis["sentence_count"]
        if avg_sentence_len <= 15:
            factors.append("easy_to_read")

    # Has concrete details
    if "numbers" in elements or "money_figures" in elements:
        factors.append("concrete_details")

    analysis["success_factors"] = factors

    return analysis


def compare_to_benchmark(
    user_profile: Dict[str, Any],
    user_analysis: Dict[str, Any],
    benchmark_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare a user's profile to a benchmark.

    Returns detailed comparison and recommendations.
    """
    comparison = {
        "summary": {},
        "gaps": [],
        "strengths": [],
        "recommendations": [],
        "detailed_comparison": {}
    }

    patterns = benchmark_data.get("patterns", {})
    agg_metrics = benchmark_data.get("aggregated_metrics", {})
    top_accounts = benchmark_data.get("top_accounts", [])

    if not top_accounts:
        return {"error": "Benchmark has no top accounts to compare against"}

    # Get user metrics
    user_style = user_analysis
    user_vocab = user_style.get("vocabulary", {})
    user_tone = user_style.get("tone", {})
    user_posting = user_style.get("posting_patterns", {})
    user_emoji = user_style.get("emoji_usage", {})
    user_platform = user_style.get("by_platform", {}).get("twitter", {})

    # Calculate benchmark averages
    bench_avg_length = patterns.get("optimal_length", {}).get("avg", 0)
    bench_vocab = patterns.get("common_styles", {}).get("vocabulary", "unknown")
    bench_tone = patterns.get("common_styles", {}).get("tone", "unknown")
    bench_emoji = patterns.get("common_styles", {}).get("emoji", "unknown")
    bench_hours = patterns.get("best_timing", {}).get("peak_hours", [])
    bench_days = patterns.get("best_timing", {}).get("peak_days", [])

    # Detailed comparison
    comparison["detailed_comparison"] = {
        "post_length": {
            "yours": user_platform.get("avg_words", 0),
            "benchmark_avg": bench_avg_length,
            "benchmark_range": patterns.get("optimal_length", {}),
            "verdict": _compare_values(user_platform.get("avg_words", 0), bench_avg_length, tolerance=0.3)
        },
        "vocabulary": {
            "yours": user_vocab.get("level", "unknown"),
            "benchmark": bench_vocab,
            "verdict": "match" if user_vocab.get("level") == bench_vocab else "different"
        },
        "tone": {
            "yours": user_tone.get("energy", "unknown"),
            "benchmark": bench_tone,
            "verdict": "match" if user_tone.get("energy") == bench_tone else "different"
        },
        "emoji_usage": {
            "yours": user_emoji.get("style", "unknown"),
            "your_per_post": user_emoji.get("per_post", 0),
            "benchmark": bench_emoji,
            "verdict": "match" if user_emoji.get("style") == bench_emoji else "different"
        },
        "posting_time": {
            "your_preference": user_posting.get("time_preference", "unknown"),
            "your_peak_hours": user_posting.get("peak_hours", []),
            "benchmark_peak_hours": bench_hours,
            "benchmark_peak_days": bench_days,
        }
    }

    # Identify gaps
    gaps = []

    # Post length gap
    user_length = user_platform.get("avg_words", 0)
    if bench_avg_length > 0:
        if user_length < bench_avg_length * 0.7:
            gaps.append({
                "area": "post_length",
                "issue": "Your posts are shorter than top performers",
                "yours": f"{user_length:.0f} words",
                "benchmark": f"{bench_avg_length:.0f} words",
                "priority": "high"
            })
        elif user_length > bench_avg_length * 1.5:
            gaps.append({
                "area": "post_length",
                "issue": "Your posts are longer than top performers",
                "yours": f"{user_length:.0f} words",
                "benchmark": f"{bench_avg_length:.0f} words",
                "priority": "medium"
            })

    # Vocabulary gap
    vocab_order = ["simple", "moderate", "professional", "advanced"]
    user_vocab_level = user_vocab.get("level", "unknown")
    if user_vocab_level in vocab_order and bench_vocab in vocab_order:
        user_idx = vocab_order.index(user_vocab_level)
        bench_idx = vocab_order.index(bench_vocab)
        if abs(user_idx - bench_idx) >= 2:
            gaps.append({
                "area": "vocabulary",
                "issue": f"Your vocabulary level differs significantly",
                "yours": user_vocab_level,
                "benchmark": bench_vocab,
                "priority": "medium"
            })

    # Posting time gap
    user_hours = set(user_posting.get("peak_hours", []))
    bench_hours_set = set(bench_hours)
    if user_hours and bench_hours_set and not user_hours.intersection(bench_hours_set):
        gaps.append({
            "area": "posting_time",
            "issue": "You're posting at different times than top performers",
            "yours": list(user_hours)[:3],
            "benchmark": list(bench_hours_set)[:3],
            "priority": "medium"
        })

    # Emoji usage gap
    if user_emoji.get("style") != bench_emoji and bench_emoji:
        gaps.append({
            "area": "emoji_usage",
            "issue": f"Your emoji usage ({user_emoji.get('style')}) differs from benchmark ({bench_emoji})",
            "yours": user_emoji.get("style"),
            "benchmark": bench_emoji,
            "priority": "low"
        })

    comparison["gaps"] = gaps

    # Identify strengths
    strengths = []

    if comparison["detailed_comparison"]["post_length"]["verdict"] == "match":
        strengths.append("Post length is optimized for the niche")

    if comparison["detailed_comparison"]["vocabulary"]["verdict"] == "match":
        strengths.append("Vocabulary level matches top performers")

    if comparison["detailed_comparison"]["tone"]["verdict"] == "match":
        strengths.append("Tone aligns with successful accounts")

    comparison["strengths"] = strengths

    # Generate recommendations
    comparison["recommendations"] = get_benchmark_recommendations(
        gaps, benchmark_data, user_analysis
    )

    # Summary score
    total_areas = 5
    matching = len(strengths)
    comparison["summary"] = {
        "alignment_score": f"{(matching / total_areas) * 100:.0f}%",
        "gaps_found": len(gaps),
        "high_priority_gaps": len([g for g in gaps if g.get("priority") == "high"]),
        "strengths": len(strengths)
    }

    return comparison


def _compare_values(user_val: float, bench_val: float, tolerance: float = 0.2) -> str:
    """Compare two values with tolerance."""
    if bench_val == 0:
        return "no_data"
    ratio = user_val / bench_val
    if 1 - tolerance <= ratio <= 1 + tolerance:
        return "match"
    elif ratio < 1 - tolerance:
        return "below"
    else:
        return "above"


def get_benchmark_recommendations(
    gaps: List[Dict],
    benchmark_data: Dict[str, Any],
    user_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate specific, actionable recommendations.
    """
    recommendations = []
    patterns = benchmark_data.get("patterns", {})
    viral_posts = benchmark_data.get("viral_posts", [])
    top_accounts = benchmark_data.get("top_accounts", [])

    for gap in gaps:
        area = gap.get("area")

        if area == "post_length":
            optimal = patterns.get("optimal_length", {})
            rec = {
                "area": "Post Length",
                "action": f"Aim for {optimal.get('avg', 50):.0f} words per post (range: {optimal.get('min', 30):.0f}-{optimal.get('max', 150):.0f})",
                "why": "Top performers in this niche use this length for maximum engagement",
                "priority": gap.get("priority", "medium")
            }
            recommendations.append(rec)

        elif area == "posting_time":
            bench_hours = patterns.get("best_timing", {}).get("peak_hours", [])
            bench_days = patterns.get("best_timing", {}).get("peak_days", [])
            rec = {
                "area": "Posting Schedule",
                "action": f"Post during peak hours: {bench_hours} on {bench_days}",
                "why": "This is when top performers get the most engagement",
                "priority": gap.get("priority", "medium")
            }
            recommendations.append(rec)

        elif area == "vocabulary":
            rec = {
                "area": "Writing Style",
                "action": f"Adjust vocabulary to '{gap.get('benchmark')}' level",
                "why": "Matching audience expectations improves engagement",
                "priority": gap.get("priority", "medium")
            }
            recommendations.append(rec)

        elif area == "emoji_usage":
            rec = {
                "area": "Emoji Usage",
                "action": f"Try a '{gap.get('benchmark')}' emoji style",
                "why": "Visual elements affect engagement in this niche",
                "priority": gap.get("priority", "low")
            }
            recommendations.append(rec)

    # Add hook recommendations based on viral posts
    if patterns.get("hooks"):
        top_hook_type = patterns["hooks"][0] if patterns["hooks"] else None
        if top_hook_type:
            rec = {
                "area": "Post Hooks",
                "action": f"Use more '{top_hook_type.get('type')}' hooks in your opening line",
                "why": "This hook type performs best in viral posts",
                "examples": top_hook_type.get("examples", [])[:2],
                "priority": "high"
            }
            recommendations.append(rec)

    # Add topic recommendations
    user_topics = set(user_analysis.get("topics", []))
    bench_topics = set(patterns.get("top_topics", []))
    missing_topics = bench_topics - user_topics
    if missing_topics:
        rec = {
            "area": "Content Topics",
            "action": f"Consider covering these popular topics: {list(missing_topics)[:5]}",
            "why": "Top performers frequently discuss these subjects",
            "priority": "medium"
        }
        recommendations.append(rec)

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

    return recommendations


# CLI Interface
def main():
    import argparse
    import sys

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from social.twitter_public_scraper import fetch_twitter_profile
    from social.style_extractor import extract_social_style

    parser = argparse.ArgumentParser(description="Benchmark Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a top account")
    analyze_parser.add_argument("username", help="Twitter username to analyze")
    analyze_parser.add_argument("--benchmark", "-b", required=True, help="Benchmark name")
    analyze_parser.add_argument("--max-posts", "-n", type=int, default=100)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare profile to benchmark")
    compare_parser.add_argument("username", help="Your Twitter username")
    compare_parser.add_argument("--benchmark", "-b", required=True, help="Benchmark name")
    compare_parser.add_argument("--max-posts", "-n", type=int, default=100)

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show benchmark summary")
    summary_parser.add_argument("benchmark", help="Benchmark name")

    args = parser.parse_args()

    if args.command == "analyze":
        print(f"Analyzing @{args.username} for benchmark '{args.benchmark}'...")

        # Fetch profile
        profile_data = fetch_twitter_profile(args.username, args.max_posts)
        if "error" in profile_data:
            print(f"Error: {profile_data['error']}")
            return

        print(f"Fetched {len(profile_data.get('posts', []))} posts")

        # Analyze style
        platform_data = [{
            "platform": "twitter",
            "posts": profile_data.get("posts", []),
            "profile": profile_data.get("profile", {})
        }]
        analysis = extract_social_style(platform_data)

        # Add to benchmark
        manager = BenchmarkManager(args.benchmark)
        result = manager.add_top_account(profile_data, analysis)

        print(f"\nResult: {json.dumps(result, indent=2)}")
        print(f"\nBenchmark saved to: {manager.path}")

    elif args.command == "compare":
        print(f"Comparing @{args.username} to benchmark '{args.benchmark}'...")

        # Fetch profile
        profile_data = fetch_twitter_profile(args.username, args.max_posts)
        if "error" in profile_data:
            print(f"Error: {profile_data['error']}")
            return

        # Analyze style
        platform_data = [{
            "platform": "twitter",
            "posts": profile_data.get("posts", []),
            "profile": profile_data.get("profile", {})
        }]
        analysis = extract_social_style(platform_data)

        # Load benchmark and compare
        manager = BenchmarkManager(args.benchmark)
        comparison = manager.compare_profile(profile_data, analysis)

        print(f"\n{json.dumps(comparison, indent=2)}")

    elif args.command == "summary":
        manager = BenchmarkManager(args.benchmark)
        summary = manager.get_summary()
        print(json.dumps(summary, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
