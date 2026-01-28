"""
Reply Generator - Generate replies in YOUR voice, optimized for engagement

Uses your profile for voice matching and benchmarks for optimization.
"""

import json
import re
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Paths
PROFILES_DIR = Path(__file__).parent.parent / "profiles"
BENCHMARKS_DIR = Path(__file__).parent.parent / "benchmarks"


class ReplyGenerator:
    """
    Generate replies that sound like YOU but are optimized for engagement.
    """

    def __init__(
        self,
        profile_path: str = None,
        benchmark_name: str = "finance_twitter"
    ):
        """
        Initialize generator.

        Args:
            profile_path: Path to your voice profile JSON
            benchmark_name: Benchmark to use for optimization
        """
        self.profile = self._load_profile(profile_path)
        self.benchmark = self._load_benchmark(benchmark_name)

        # Load target length from benchmark patterns
        patterns = self.benchmark.get("patterns", {})
        optimal_length = patterns.get("optimal_length", {})
        self.target_length = int(optimal_length.get("avg", 26))
        self.min_length = int(optimal_length.get("min", 20))
        self.max_length = int(optimal_length.get("max", 35))

    def _load_profile(self, path: str = None) -> Dict[str, Any]:
        """Load user voice profile."""
        if path:
            profile_path = Path(path)
        else:
            # Try default paths
            for default in ["justin_katz.json", "my_profile.json", "profile.json"]:
                profile_path = PROFILES_DIR / default
                if profile_path.exists():
                    break

        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Return default profile structure
        return {
            "voice": {
                "tone": "professional",
                "formality": "balanced",
                "vocabulary": "professional",
                "signature_phrases": [],
                "emoji_style": "minimal",
            },
            "style": {
                "sentence_length": "concise",
                "punctuation": "standard",
                "capitalization": "standard",
            }
        }

    def _load_benchmark(self, name: str) -> Dict[str, Any]:
        """Load benchmark data."""
        benchmark_path = BENCHMARKS_DIR / f"{name}.json"

        if benchmark_path.exists():
            with open(benchmark_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {"patterns": {}}

    def generate_replies(
        self,
        original_post: Dict[str, Any],
        num_replies: int = 5,
        reply_type: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Generate reply options for a post.

        Args:
            original_post: The post to reply to (content, author, etc.)
            num_replies: Number of reply options to generate
            reply_type: Type of reply (auto, agree, question, insight, counter)

        Returns:
            List of reply options with scores
        """
        content = original_post.get("content", "")
        author = original_post.get("author", "unknown")

        # Analyze the original post
        post_analysis = self._analyze_post(content)

        # Get voice parameters
        voice = self.profile.get("voice", {})
        patterns = self.benchmark.get("patterns", {})

        # Generate different reply types
        replies = []

        # Determine reply types to generate
        if reply_type == "auto":
            types_to_generate = self._suggest_reply_types(post_analysis)
        else:
            types_to_generate = [reply_type] * num_replies

        for i, rtype in enumerate(types_to_generate[:num_replies]):
            reply = self._generate_single_reply(
                content=content,
                author=author,
                post_analysis=post_analysis,
                reply_type=rtype,
                voice=voice,
                patterns=patterns,
                variation=i
            )

            # Score the reply
            scores = self._score_reply(reply["text"], voice, patterns)
            reply.update(scores)

            replies.append(reply)

        # Sort by combined score
        replies.sort(key=lambda r: r.get("combined_score", 0), reverse=True)

        return replies

    def _analyze_post(self, content: str) -> Dict[str, Any]:
        """Analyze the original post to inform reply generation."""
        words = content.split()

        analysis = {
            "word_count": len(words),
            "has_question": "?" in content,
            "has_numbers": bool(re.search(r'\d', content)),
            "has_ticker": bool(re.search(r'\$[A-Z]{1,5}', content)),
            "sentiment": self._detect_sentiment(content),
            "topics": self._extract_topics(content),
            "key_points": self._extract_key_points(content),
        }

        return analysis

    def _detect_sentiment(self, content: str) -> str:
        """Detect post sentiment."""
        bullish = ["bull", "long", "buy", "calls", "breakout", "support", "higher", "rally", "green"]
        bearish = ["bear", "short", "sell", "puts", "breakdown", "resistance", "lower", "crash", "red"]

        content_lower = content.lower()
        bull_count = sum(1 for w in bullish if w in content_lower)
        bear_count = sum(1 for w in bearish if w in content_lower)

        if bull_count > bear_count:
            return "bullish"
        elif bear_count > bull_count:
            return "bearish"
        return "neutral"

    def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from post."""
        topics = []
        content_lower = content.lower()

        topic_keywords = {
            "options": ["options", "calls", "puts", "premium", "strike", "expiry"],
            "gamma": ["gamma", "gex", "delta", "hedging"],
            "flow": ["flow", "dark pool", "unusual", "sweep", "block"],
            "technicals": ["support", "resistance", "breakout", "trend", "chart"],
            "volatility": ["vix", "iv", "volatility", "vol"],
            "market": ["spx", "spy", "qqq", "market", "index"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                topics.append(topic)

        return topics

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points/claims from post."""
        points = []

        # Split into sentences
        sentences = re.split(r'[.!?]', content)
        for s in sentences:
            s = s.strip()
            if len(s) > 10:
                points.append(s)

        return points[:3]  # Top 3 points

    def _suggest_reply_types(self, analysis: Dict) -> List[str]:
        """Suggest appropriate reply types based on post analysis."""
        types = []

        if analysis.get("has_question"):
            types.append("answer")
            types.append("insight")

        if analysis.get("sentiment") in ["bullish", "bearish"]:
            types.append("agree")
            types.append("nuance")  # Add nuance/perspective

        if analysis.get("has_numbers") or "gamma" in analysis.get("topics", []):
            types.append("insight")
            types.append("question")

        # Always include some variety
        if "insight" not in types:
            types.append("insight")
        if "question" not in types:
            types.append("question")
        if "agree" not in types:
            types.append("agree")

        return types[:5]

    def _generate_single_reply(
        self,
        content: str,
        author: str,
        post_analysis: Dict,
        reply_type: str,
        voice: Dict,
        patterns: Dict,
        variation: int = 0
    ) -> Dict[str, Any]:
        """Generate a single reply."""

        # Get voice characteristics
        tone = voice.get("tone", "professional")
        formality = voice.get("formality", "balanced")
        signature_phrases = voice.get("signature_phrases", [])
        emoji_style = voice.get("emoji_style", "minimal")

        # Build reply based on type
        reply_templates = self._get_reply_templates(reply_type, tone)
        template = reply_templates[variation % len(reply_templates)]

        # Fill in template
        reply_text = self._fill_template(
            template=template,
            post_analysis=post_analysis,
            author=author,
            signature_phrases=signature_phrases
        )

        # Apply voice adjustments
        reply_text = self._apply_voice_style(
            text=reply_text,
            tone=tone,
            formality=formality,
            emoji_style=emoji_style
        )

        # Ensure target length - expand or contract to hit benchmark optimal
        reply_text = self._adjust_length(reply_text, self.target_length, voice, post_analysis)

        return {
            "text": reply_text,
            "type": reply_type,
            "word_count": len(reply_text.split()),
            "target_length": self.target_length,
            "responding_to": post_analysis.get("topics", []),
        }

    def _get_reply_templates(self, reply_type: str, tone: str) -> List[str]:
        """Get reply templates for a given type."""

        templates = {
            "agree": [
                "This is exactly what I've been tracking. {insight} - and when you combine that with {nuance}, the setup becomes even clearer.",
                "Spot on. {insight}. This is why {reason} - most people miss this connection.",
                "This aligns with what the flow is showing. {insight}. The key variable to watch here is {nuance}.",
                "Been seeing the same setup. {insight}. What makes this particularly interesting is {reason}.",
                "Nailed it. {insight}. From a positioning standpoint, {nuance} is what I'm watching most closely.",
            ],
            "insight": [
                "Worth noting - {insight}. This matters because {reason}. The follow-through here could be significant.",
                "Adding context: {insight}. What most people miss is {reason}. {follow_up}",
                "The key here is {insight}. When you factor in {nuance}, it paints a clearer picture. {follow_up}",
                "From a {topic} perspective: {insight}. This is particularly relevant because {reason}.",
                "{insight}. Combined with {nuance}, this is what the data suggests. Worth watching closely.",
            ],
            "question": [
                "Curious about the {topic} side of this - how does that factor into your thesis? Especially given {nuance}.",
                "What's your read on {topic} given this setup? I'm seeing {insight} which could change the dynamics.",
                "How are you positioning around {topic}? The {nuance} aspect seems like it could accelerate moves either way.",
                "Interesting breakdown. What levels are you watching where {topic} flips? That's usually where the real acceleration happens.",
                "Does this change your view on {topic}? I've been tracking {insight} which seems to confirm this thesis.",
            ],
            "nuance": [
                "Generally agree, but {nuance} is the wildcard here. If that shifts, {insight} could play out differently.",
                "True, though worth considering {nuance}. That's often the variable that catches people off guard when {reason}.",
                "Solid analysis. The one thing I'd add: {nuance} is the key variable. When that aligns with {insight}, moves accelerate.",
                "This is right, and {nuance} could amplify this significantly. I'm watching for {insight} as confirmation.",
                "Yes, and {nuance} tends to be underappreciated here. Combined with {insight}, the setup is clean.",
            ],
            "answer": [
                "From what I'm seeing: {insight}. The data supports this because {reason}. Key level to watch.",
                "The data suggests {insight}. What confirms this is {nuance}. That's the signal I'm tracking.",
                "Based on positioning: {insight}. This matters because {reason}. The setup looks clean from here.",
                "My read: {insight}. When you combine that with {nuance}, the picture becomes clearer. {follow_up}",
                "{insight}. The reason this matters: {reason}. I'm positioned accordingly.",
            ],
        }

        return templates.get(reply_type, templates["insight"])

    def _fill_template(
        self,
        template: str,
        post_analysis: Dict,
        author: str,
        signature_phrases: List[str]
    ) -> str:
        """Fill in template placeholders."""

        topics = post_analysis.get("topics", ["market"])
        sentiment = post_analysis.get("sentiment", "neutral")
        key_points = post_analysis.get("key_points", [])

        # Generate contextual insights based on topics
        insights = self._generate_insights(topics, sentiment)
        nuances = self._generate_nuances(topics, sentiment)
        reasons = self._generate_reasons(topics)
        follow_ups = self._generate_follow_ups(topics)

        # Fill placeholders
        text = template
        text = text.replace("{insight}", random.choice(insights) if insights else "this setup looks solid")
        text = text.replace("{nuance}", random.choice(nuances) if nuances else "timing matters")
        text = text.replace("{reason}", random.choice(reasons) if reasons else "it signals a shift")
        text = text.replace("{follow_up}", random.choice(follow_ups) if follow_ups else "")
        text = text.replace("{topic}", random.choice(topics) if topics else "market")

        # Add signature phrase occasionally
        if signature_phrases and random.random() < 0.3:
            phrase = random.choice(signature_phrases)
            if not text.endswith("."):
                text += "."
            text += f" {phrase}"

        return text

    def _generate_insights(self, topics: List[str], sentiment: str) -> List[str]:
        """Generate topic-relevant insights."""
        insights = []

        if "gamma" in topics:
            insights.extend([
                "dealer gamma is heavily negative here",
                "gamma flip level is the key",
                "expect volatility expansion near this level",
                "hedging flows will accelerate moves",
            ])

        if "options" in topics:
            insights.extend([
                "IV is pricing in a bigger move than usual",
                "open interest is clustered at key strikes",
                "premium sellers are getting squeezed",
                "the options market is signaling direction",
            ])

        if "flow" in topics:
            insights.extend([
                "unusual activity on the tape",
                "dark pool prints suggest accumulation",
                "sweep activity picked up significantly",
                "smart money positioning is clear",
            ])

        if "technicals" in topics:
            insights.extend([
                "price structure favors continuation",
                "liquidity pockets above/below current levels",
                "the trend is your friend until it bends",
                "watching for a clean break of structure",
            ])

        if "market" in topics or not insights:
            insights.extend([
                "market internals confirm the move",
                "breadth is supporting this",
                "correlation regime is shifting",
                "risk-on/off signals are aligning",
            ])

        return insights

    def _generate_nuances(self, topics: List[str], sentiment: str) -> List[str]:
        """Generate nuanced perspectives."""
        return [
            "time decay becomes a factor",
            "positioning can shift quickly",
            "context matters more than levels",
            "the reflexive nature of flows",
            "don't ignore the macro backdrop",
            "earnings could change this setup",
            "liquidity conditions are key",
        ]

    def _generate_reasons(self, topics: List[str]) -> List[str]:
        """Generate reasons/explanations."""
        return [
            "it changes the hedging dynamics",
            "flows tend to accelerate at these levels",
            "smart money has been positioning for this",
            "volatility regimes don't change often",
            "market structure amplifies moves here",
        ]

    def _generate_follow_ups(self, topics: List[str]) -> List[str]:
        """Generate follow-up statements."""
        return [
            "Will be watching this closely.",
            "Key level to monitor.",
            "The setup is clean.",
            "",  # Sometimes no follow-up
        ]

    def _apply_voice_style(
        self,
        text: str,
        tone: str,
        formality: str,
        emoji_style: str
    ) -> str:
        """Apply voice styling to text."""

        # Formality adjustments
        if formality == "casual":
            text = text.replace("This is", "This's")
            text = text.replace("I am", "I'm")
        elif formality == "formal":
            text = text.replace("don't", "do not")
            text = text.replace("can't", "cannot")

        # Emoji styling
        if emoji_style == "minimal":
            # Remove any emojis that might have been added
            text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]', '', text)
        elif emoji_style == "light":
            # Maybe add one relevant emoji
            if random.random() < 0.2:
                text += " 📊"

        return text.strip()

    def _adjust_length(self, text: str, target_words: int, voice: Dict, post_analysis: Dict) -> str:
        """Adjust reply length to hit target using voice profile data."""
        words = text.split()
        current_length = len(words)

        # If too long, truncate intelligently
        if current_length > target_words + 5:
            text = " ".join(words[:target_words])
            if not text.endswith((".", "!", "?")):
                text += "."
            return text

        # If too short, expand using signature phrases and contextual additions
        if current_length < target_words - 3:
            text = self._expand_reply(text, target_words, voice, post_analysis)

        return text

    def _expand_reply(self, text: str, target_words: int, voice: Dict, post_analysis: Dict) -> str:
        """Expand a short reply to hit the target word count."""
        words = text.split()
        current_length = len(words)
        topics = post_analysis.get("topics", [])

        # Expansion phrases based on context
        expansions = {
            "transitions": [
                "This is particularly relevant because",
                "What makes this interesting is",
                "The key factor here is",
                "Worth noting that",
                "From a positioning standpoint,",
            ],
            "amplifiers": [
                "- and when that happens, moves tend to accelerate.",
                "- this is where most people get caught off guard.",
                "- the data has been consistent on this.",
                "- I've been tracking this closely.",
                "- the setup looks clean from here.",
            ],
            "closers": [
                "Key level to watch.",
                "Will be monitoring this closely.",
                "The setup is there.",
                "Watching for confirmation.",
                "This is the signal.",
            ],
            "topic_specific": {
                "options": [
                    "Options flow confirms this thesis.",
                    "IV is pricing this in already.",
                    "The premium sellers are feeling this.",
                ],
                "gamma": [
                    "Gamma positioning supports this view.",
                    "Dealer hedging will amplify the move.",
                    "GEX levels confirm this setup.",
                ],
                "volatility": [
                    "Vol regime is shifting here.",
                    "Realized vs implied tells the story.",
                    "VIX term structure aligns with this.",
                ],
                "market": [
                    "Market internals confirm this.",
                    "Breadth supports the move.",
                    "Price action is clean here.",
                ],
            }
        }

        # Add signature phrases from voice profile
        signature_phrases = voice.get("signature_phrases", [])

        # Strategy: Add contextual expansions until we hit target
        attempts = 0
        max_attempts = 5

        while len(text.split()) < target_words - 2 and attempts < max_attempts:
            attempts += 1
            current_words = len(text.split())
            words_needed = target_words - current_words

            # Choose expansion based on what's needed
            if words_needed > 8 and not any(t in text.lower() for t in ["because", "when", "what makes"]):
                # Add a transition phrase
                expansion = random.choice(expansions["transitions"])
                if not text.endswith((".", "!", "?")):
                    text += "."
                text += f" {expansion}"

                # Add topic-specific content
                for topic in topics:
                    if topic in expansions["topic_specific"]:
                        topic_addition = random.choice(expansions["topic_specific"][topic])
                        text += f" {topic_addition}"
                        break

            elif words_needed > 5:
                # Add an amplifier
                amplifier = random.choice(expansions["amplifiers"])
                # Remove trailing punctuation before adding amplifier
                text = text.rstrip(".")
                text += amplifier

            elif words_needed > 2 and signature_phrases:
                # Add a signature phrase
                phrase = random.choice(signature_phrases)
                if phrase not in text:
                    if not text.endswith((".", "!", "?")):
                        text += "."
                    text += f" {phrase}"

            else:
                # Add a closer
                closer = random.choice(expansions["closers"])
                if closer not in text:
                    if not text.endswith((".", "!", "?")):
                        text += "."
                    text += f" {closer}"
                break

        # Clean up any double periods or spaces
        text = text.replace("..", ".").replace("  ", " ").strip()

        return text

    def _score_reply(
        self,
        text: str,
        voice: Dict,
        patterns: Dict
    ) -> Dict[str, float]:
        """Score a reply for voice match and engagement potential."""

        from .scoring import score_reply
        return score_reply(text, voice, patterns)


def draft_replies(
    post_url: str = None,
    post_content: str = None,
    post_author: str = None,
    profile_path: str = None,
    benchmark_name: str = "finance_twitter",
    num_replies: int = 5
) -> Dict[str, Any]:
    """
    Draft replies to a post.

    Args:
        post_url: URL of the post (optional)
        post_content: Content of the post
        post_author: Author of the post
        profile_path: Path to voice profile
        benchmark_name: Benchmark to use
        num_replies: Number of reply options

    Returns:
        Dict with original post and reply options
    """
    generator = ReplyGenerator(
        profile_path=profile_path,
        benchmark_name=benchmark_name
    )

    original_post = {
        "content": post_content or "",
        "author": post_author or "unknown",
        "url": post_url,
    }

    replies = generator.generate_replies(original_post, num_replies)

    return {
        "original_post": original_post,
        "replies": replies,
        "generated_at": datetime.now().isoformat(),
        "profile_used": profile_path or "default",
        "benchmark_used": benchmark_name,
    }


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reply Generator")
    parser.add_argument("--content", "-c", required=True, help="Post content to reply to")
    parser.add_argument("--author", "-a", default="unknown", help="Post author")
    parser.add_argument("--profile", "-p", help="Path to voice profile")
    parser.add_argument("--benchmark", "-b", default="finance_twitter", help="Benchmark name")
    parser.add_argument("--num", "-n", type=int, default=5, help="Number of replies")

    args = parser.parse_args()

    result = draft_replies(
        post_content=args.content,
        post_author=args.author,
        profile_path=args.profile,
        benchmark_name=args.benchmark,
        num_replies=args.num
    )

    print(f"\nOriginal post by @{result['original_post']['author']}:")
    print(f"\"{result['original_post']['content']}\"")
    print("\n" + "=" * 60)
    print("GENERATED REPLIES")
    print("=" * 60)

    for i, reply in enumerate(result['replies'], 1):
        print(f"\n#{i} [{reply['type'].upper()}] (Score: {reply.get('combined_score', 0):.1f})")
        print(f"   Voice Match: {reply.get('voice_match', 0):.0f}% | Engagement: {reply.get('engagement_potential', 0):.0f}%")
        print(f"   Words: {reply['word_count']}")
        print(f"\n   \"{reply['text']}\"")
