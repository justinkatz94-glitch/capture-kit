"""
LLM Generator - Claude API integration for content generation

Generates content using user's voice profile and benchmark patterns.
FIXED: Added anti-hallucination safeguards for market data.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from .schemas import (
    generate_id, now_iso, load_json,
    PLATFORM_CONFIGS, GOAL_CONFIGS, QueueItem
)
from .content_analyzer import ContentAnalyzer, analyze_content
from .user_manager import get_active_profile

# Import LinkedIn benchmark (lazy to avoid circular imports)
def _get_linkedin_benchmark_context(user_name: str = None) -> Dict[str, Any]:
    """Get LinkedIn benchmark context for a user."""
    try:
        from .linkedin_benchmark import get_generation_context
        return get_generation_context(user_name)
    except ImportError:
        return {}

# Import platform adapters (lazy to avoid circular imports)
def _get_platform_adapter(platform: str):
    """Get platform adapter."""
    try:
        from .platforms import get_adapter
        return get_adapter(platform)
    except (ImportError, ValueError):
        return None

# Check for Anthropic SDK
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Paths
BASE_DIR = Path(__file__).parent.parent
BENCHMARKS_DIR = BASE_DIR / "benchmarks"


@dataclass
class GeneratedReply:
    """A generated reply with metadata."""
    id: str
    content: str
    platform: str
    technique_label: str
    hook_type: str
    framework: str
    triggers: List[str]
    voice_match: float
    engagement_prediction: float
    combined_score: float
    why: str
    word_count: int
    char_count: int


class LLMGenerator:
    """
    Claude-powered content generator.

    Uses user's voice profile and benchmark patterns to generate
    authentic, optimized content.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize generator.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = None
        self.analyzer = ContentAnalyzer()

        if ANTHROPIC_AVAILABLE and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.client is not None

    def _load_benchmark(self, name: str, platform: str = "twitter", user_name: str = None) -> Dict[str, Any]:
        """
        Load benchmark data.

        For LinkedIn, uses user-specific benchmark data if available.
        For other platforms, uses general benchmark files.
        """
        # For LinkedIn, try to use user's LinkedIn benchmark
        if platform == "linkedin":
            linkedin_context = _get_linkedin_benchmark_context(user_name)
            if linkedin_context.get("has_data"):
                # Convert LinkedIn benchmark context to benchmark format
                return {
                    "patterns": {
                        "optimal_length": linkedin_context.get("optimal_length", {}),
                        "hooks": linkedin_context.get("effective_hooks", []),
                        "top_topics": linkedin_context.get("top_topics", []),
                    },
                    "top_accounts": [
                        {"username": ex.get("author"), "top_posts": [ex]}
                        for ex in linkedin_context.get("examples", [])
                    ],
                    "style_notes": linkedin_context.get("style_notes", {}),
                    "source": "user_linkedin_benchmark",
                }

        # Fall back to general benchmark file
        path = BENCHMARKS_DIR / f"{name}.json"
        if path.exists():
            return load_json(str(path))
        return {}

    def _get_platform_rules(self, platform: str) -> str:
        """Get platform-specific rules from adapter."""
        adapter = _get_platform_adapter(platform)
        if adapter:
            return adapter.get_system_prompt_rules()
        return ""

    def _build_system_prompt(
        self,
        profile: Dict[str, Any],
        benchmark: Dict[str, Any],
        platform: str,
        goal: str
    ) -> str:
        """Build system prompt with voice profile and benchmark data."""

        voice = profile.get("voice", {})
        proven_patterns = profile.get("proven_patterns", [])
        platform_prefs = profile.get("platform_preferences", {}).get(platform, {})
        platform_config = PLATFORM_CONFIGS.get(platform, {})
        goal_config = GOAL_CONFIGS.get(goal, {})
        benchmark_patterns = benchmark.get("patterns", {})

        # Get benchmark examples
        top_accounts = benchmark.get("top_accounts", [])
        example_posts = []
        for account in top_accounts[:3]:
            for post in account.get("top_posts", [])[:2]:
                if post.get("content"):
                    example_posts.append({
                        "author": account.get("username"),
                        "content": post.get("content")[:200],
                        "engagement": post.get("likes", 0),
                    })

        prompt = f"""You are a social media content writer who perfectly matches a specific person's voice and style.

## YOUR VOICE PROFILE

You write exactly like this person:
- Tone: {voice.get('tone', 'professional')}
- Formality: {voice.get('formality', 'balanced')}
- Vocabulary: {voice.get('vocabulary', 'professional')}
- Emoji usage: {voice.get('emoji_style', 'minimal')}

Signature phrases to use naturally:
{json.dumps(voice.get('signature_phrases', []), indent=2)}

Phrases to AVOID:
{json.dumps(voice.get('avoided_phrases', []), indent=2)}

## PROVEN PATTERNS FOR THIS USER

These patterns have worked well for this specific user:
{json.dumps(proven_patterns[-5:] if proven_patterns else ['No proven patterns yet - focus on benchmark patterns'], indent=2)}

## BENCHMARK DATA (Top Performers in Niche)

Optimal post length: {benchmark_patterns.get('optimal_length', {}).get('avg', 26)} words
Best posting hours: {benchmark_patterns.get('best_timing', {}).get('peak_hours', [])}
Best days: {benchmark_patterns.get('best_timing', {}).get('peak_days', [])}
Top topics: {benchmark_patterns.get('top_topics', [])}

Effective hook types:
{json.dumps(benchmark_patterns.get('hooks', [])[:3], indent=2)}

## EXAMPLES FROM TOP PERFORMERS

{json.dumps(example_posts[:5], indent=2)}

## PLATFORM: {platform.upper()}

Platform strategy: {platform_config.get('strategy', '')}
Target reply length: {platform_prefs.get('reply_length', 80)} chars
Target post length: {platform_prefs.get('post_length', 240)} chars

{self._get_platform_rules(platform)}

## GOAL: {goal.upper().replace('_', ' ')}

Optimize for: {goal_config.get('optimize_for', 'engagement')}
Content focus: {goal_config.get('content_focus', '')}

## CRITICAL RULES - DATA INTEGRITY

**NEVER FABRICATE DATA OR STATISTICS:**
- NEVER invent numbers, percentages, or statistics
- NEVER say "data suggests", "studies show", or "historically" with made-up information  
- NEVER claim to know current prices, levels, or market positioning
- NEVER fabricate patterns like "70% of the time" or "this typically happens"
- NEVER make up correlations or cause-effect relationships you don't have data for

**YOU HAVE NO MARKET DATA. You only know what's in the original post.**

## SAFE REPLY STRATEGIES

Use these approaches that add value WITHOUT fabricating:

1. **ASK A SMART QUESTION** - Shows expertise without claiming facts
   - "What's your read on how this affects [related area]?"
   - "Curious if you're seeing similar signals in [X]?"

2. **SHARE PERSPECTIVE AS OPINION** - Frame as your view, not universal truth
   - "My read on this..."
   - "I'd be watching [X] closely here"
   - "One way to think about this..."

3. **AMPLIFY THEIR POINT** - Validate and reframe without adding fake data
   - "This is the nuance most people miss"
   - "Underrated point about [specific element]"
   - "Worth emphasizing: [restate their insight differently]"

4. **CONNECT TO RELATED CONCEPTS** - Link ideas the audience knows
   - "This connects to [related concept]"
   - "The [specific term] angle here is underappreciated"

5. **OFFER ALTERNATIVE FRAMING** - Present as consideration, not fact
   - "One thing I'd add to this framework..."
   - "Playing devil's advocate - what if [scenario]?"

## VOICE RULES

1. SOUND EXACTLY LIKE THE USER - match their tone, vocabulary, and style
2. Keep within platform length requirements
3. Use the user's signature phrases naturally (don't force them)
4. Include emotional engagement (curiosity, validation) through QUESTIONS not claims
5. Start with something that hooks - a question, a reframe, a contrast
6. Never be generic or corporate-sounding
7. Match the energy of the niche

## WHAT NOT TO DO

❌ "Data suggests gamma flips at round numbers create momentum" (fabricated)
❌ "This typically leads to 30% moves" (fabricated)
❌ "70% of the time this setup resolves higher" (fabricated)
❌ "Historically, dealer positioning at these levels..." (fabricated)

## WHAT TO DO

✅ "What's your read on how this plays out into OPEX?"
✅ "The gamma flip angle here doesn't get enough attention"
✅ "My read: worth watching the 5900 level closely"
✅ "Curious if you're seeing this in other names too"
✅ "This is the setup most people miss - the positioning context matters"
"""

        return prompt

    def generate_replies(
        self,
        original_post: Dict[str, Any],
        profile: Dict[str, Any] = None,
        platform: str = "twitter",
        num_replies: int = 3,
        benchmark_name: str = "finance_twitter",
    ) -> List[GeneratedReply]:
        """
        Generate reply options for a post.

        Args:
            original_post: Post to reply to (content, author, url)
            profile: User profile (uses active profile if None)
            platform: Target platform
            num_replies: Number of replies to generate
            benchmark_name: Benchmark to use

        Returns:
            List of GeneratedReply objects
        """
        if not self.is_available:
            return self._generate_fallback_replies(original_post, profile, platform, num_replies)

        profile = profile or get_active_profile()
        if not profile:
            return [self._error_reply("No active user profile")]

        user_name = profile.get("name")
        benchmark = self._load_benchmark(benchmark_name, platform=platform, user_name=user_name)
        goal = profile.get("goal", "grow_followers")

        system_prompt = self._build_system_prompt(profile, benchmark, platform, goal)

        user_prompt = f"""Generate {num_replies} reply options for this post.

ORIGINAL POST by @{original_post.get('author', 'unknown')}:
"{original_post.get('content', '')}"

**IMPORTANT**: You have NO market data. Only reference information that appears in the original post above.

For each reply, use a DIFFERENT strategy:
- One should ASK A QUESTION
- One should AMPLIFY/VALIDATE their point  
- One should OFFER PERSPECTIVE (framed as opinion)

For each reply, provide:
1. The reply text (appropriate length for {platform})
2. Strategy used (question, amplify, perspective, connection, contrast)
3. Primary emotional trigger (curiosity, validation, FOMO)
4. Why this reply should work

Format your response as JSON array:
[
  {{
    "reply": "your reply text here",
    "strategy": "question",
    "hook_type": "question",
    "trigger": "curiosity",
    "why": "explanation of why this works"
  }}
]

Remember: Sound like ME. Add value through ENGAGEMENT, not fabricated analysis."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                replies_data = json.loads(json_match.group())
            else:
                return [self._error_reply("Could not parse LLM response")]

            # Convert to GeneratedReply objects
            generated_replies = []
            for i, reply_data in enumerate(replies_data[:num_replies]):
                reply_content = reply_data.get("reply", "")

                # Analyze the generated content
                analysis = self.analyzer.analyze(reply_content, platform)

                # Calculate scores
                voice_match = self._calculate_voice_match(reply_content, profile)
                engagement_pred = self._calculate_engagement_prediction(analysis, benchmark)

                generated_reply = GeneratedReply(
                    id=generate_id(),
                    content=reply_content,
                    platform=platform,
                    technique_label=reply_data.get("strategy", self.analyzer.get_technique_label(analysis)),
                    hook_type=reply_data.get("hook_type", analysis.hook_type),
                    framework=analysis.framework,
                    triggers=[reply_data.get("trigger", "")] + analysis.triggers[:2],
                    voice_match=voice_match,
                    engagement_prediction=engagement_pred,
                    combined_score=(voice_match * 0.35 + engagement_pred * 0.65),
                    why=reply_data.get("why", ""),
                    word_count=analysis.word_count,
                    char_count=analysis.char_count,
                )
                generated_replies.append(generated_reply)

            # Sort by combined score
            generated_replies.sort(key=lambda r: r.combined_score, reverse=True)

            return generated_replies

        except Exception as e:
            return [self._error_reply(f"LLM error: {str(e)}")]

    def _generate_fallback_replies(
        self,
        original_post: Dict[str, Any],
        profile: Dict[str, Any],
        platform: str,
        num_replies: int
    ) -> List[GeneratedReply]:
        """Generate replies without LLM (template-based fallback)."""
        # Import the existing reply generator as fallback
        from engagement.reply_generator import ReplyGenerator

        profile = profile or get_active_profile() or {}

        # Use the existing generator
        generator = ReplyGenerator(
            profile_path=None,
            benchmark_name="finance_twitter"
        )
        generator.profile = profile

        replies = generator.generate_replies(original_post, num_replies)

        # Convert to GeneratedReply format
        generated = []
        for reply in replies:
            analysis = self.analyzer.analyze(reply.get("text", ""), platform)

            generated.append(GeneratedReply(
                id=generate_id(),
                content=reply.get("text", ""),
                platform=platform,
                technique_label=self.analyzer.get_technique_label(analysis),
                hook_type=analysis.hook_type,
                framework=analysis.framework,
                triggers=analysis.triggers,
                voice_match=reply.get("voice_match", 70),
                engagement_prediction=reply.get("engagement_potential", 70),
                combined_score=reply.get("combined_score", 70),
                why=f"Template-based {reply.get('type', 'reply')} reply",
                word_count=analysis.word_count,
                char_count=analysis.char_count,
            ))

        return generated

    def _error_reply(self, message: str) -> GeneratedReply:
        """Create an error reply."""
        return GeneratedReply(
            id=generate_id(),
            content=f"Error: {message}",
            platform="",
            technique_label="error",
            hook_type="",
            framework="",
            triggers=[],
            voice_match=0,
            engagement_prediction=0,
            combined_score=0,
            why=message,
            word_count=0,
            char_count=0,
        )

    def _calculate_voice_match(self, content: str, profile: Dict[str, Any]) -> float:
        """Calculate how well content matches user's voice."""
        score = 70.0  # Base score
        voice = profile.get("voice", {})
        content_lower = content.lower()

        # Check signature phrases
        for phrase in voice.get("signature_phrases", []):
            if phrase.lower() in content_lower:
                score += 5

        # Check avoided phrases (penalty)
        for phrase in voice.get("avoided_phrases", []):
            if phrase.lower() in content_lower:
                score -= 10

        # Tone matching
        tone = voice.get("tone", "professional")
        if tone == "professional":
            professional_words = ["data", "analysis", "perspective", "context", "positioning"]
            score += sum(2 for w in professional_words if w in content_lower)
        elif tone == "casual":
            casual_words = ["pretty", "kinda", "gonna", "cool", "nice"]
            score += sum(2 for w in casual_words if w in content_lower)

        # Vocabulary level
        vocab = voice.get("vocabulary", "professional")
        words = content.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)

        if vocab == "professional" and 5 <= avg_word_len <= 7:
            score += 5
        elif vocab == "simple" and avg_word_len <= 5:
            score += 5

        return min(max(score, 0), 100)

    def _calculate_engagement_prediction(
        self,
        analysis,
        benchmark: Dict[str, Any]
    ) -> float:
        """Predict engagement based on analysis and benchmark."""
        score = 60.0  # Base score

        patterns = benchmark.get("patterns", {})

        # Hook bonus
        if analysis.hook_strength >= 0.7:
            score += 15
        elif analysis.hook_type:
            score += 8

        # Trigger bonus
        score += min(len(analysis.triggers) * 5, 15)

        # Specificity bonus
        if analysis.specificity == "concrete":
            score += 10
        elif analysis.specificity == "moderate":
            score += 5

        # Length optimization
        optimal = patterns.get("optimal_length", {}).get("avg", 26)
        if optimal > 0:
            length_diff = abs(analysis.word_count - optimal)
            if length_diff <= 5:
                score += 10
            elif length_diff <= 10:
                score += 5

        # Authority signals
        if analysis.authority_signals:
            score += 5

        return min(max(score, 0), 100)

    def generate_post(
        self,
        topic: str,
        profile: Dict[str, Any] = None,
        platform: str = "twitter",
        hook_type: str = None,
        benchmark_name: str = "finance_twitter",
    ) -> GeneratedReply:
        """
        Generate an original post on a topic.

        Args:
            topic: Topic or theme for the post
            profile: User profile
            platform: Target platform
            hook_type: Specific hook type to use (optional)
            benchmark_name: Benchmark to use

        Returns:
            GeneratedReply object
        """
        if not self.is_available:
            return self._error_reply("LLM not available - set ANTHROPIC_API_KEY")

        profile = profile or get_active_profile()
        if not profile:
            return self._error_reply("No active user profile")

        user_name = profile.get("name")
        benchmark = self._load_benchmark(benchmark_name, platform=platform, user_name=user_name)
        goal = profile.get("goal", "grow_followers")

        system_prompt = self._build_system_prompt(profile, benchmark, platform, goal)

        platform_config = PLATFORM_CONFIGS.get(platform, {})
        length_hint = ""
        if platform == "twitter":
            length_hint = "Keep under 280 characters."
        elif platform == "linkedin":
            length_hint = "Aim for 1200-1500 characters with line breaks."

        hook_instruction = ""
        if hook_type:
            hook_instruction = f"Use a {hook_type} hook specifically."

        user_prompt = f"""Write an original {platform} post about: {topic}

{hook_instruction}
{length_hint}

**IMPORTANT**: Do not fabricate statistics or data. Share perspective, ask questions, or make observations - but don't invent numbers.

Provide your response as JSON:
{{
  "post": "your post text here",
  "hook_type": "the hook type used",
  "trigger": "primary emotional trigger",
  "why": "why this post should perform well"
}}

Remember: Sound like ME, optimize like TOP PERFORMERS. No fabricated data."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            response_text = response.content[0].text

            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                post_data = json.loads(json_match.group())
            else:
                return self._error_reply("Could not parse response")

            post_content = post_data.get("post", "")
            analysis = self.analyzer.analyze(post_content, platform)

            return GeneratedReply(
                id=generate_id(),
                content=post_content,
                platform=platform,
                technique_label=self.analyzer.get_technique_label(analysis),
                hook_type=post_data.get("hook_type", analysis.hook_type),
                framework=analysis.framework,
                triggers=[post_data.get("trigger", "")] + analysis.triggers[:2],
                voice_match=self._calculate_voice_match(post_content, profile),
                engagement_prediction=self._calculate_engagement_prediction(analysis, benchmark),
                combined_score=0,  # Will be calculated
                why=post_data.get("why", ""),
                word_count=analysis.word_count,
                char_count=analysis.char_count,
            )

        except Exception as e:
            return self._error_reply(f"LLM error: {str(e)}")

    def adapt_content(
        self,
        content: str,
        from_platform: str,
        to_platform: str,
        profile: Dict[str, Any] = None,
    ) -> GeneratedReply:
        """
        Adapt content from one platform to another.

        Args:
            content: Original content
            from_platform: Source platform
            to_platform: Target platform
            profile: User profile

        Returns:
            Adapted content
        """
        if not self.is_available:
            return self._error_reply("LLM not available")

        profile = profile or get_active_profile()
        from_config = PLATFORM_CONFIGS.get(from_platform, {})
        to_config = PLATFORM_CONFIGS.get(to_platform, {})

        prompt = f"""Adapt this {from_platform} content for {to_platform}:

ORIGINAL ({from_platform}):
"{content}"

TARGET PLATFORM: {to_platform}
- Strategy: {to_config.get('strategy', '')}
- Length: {to_config.get('post_length_chars', (100, 500))} chars

Maintain the core message but optimize for {to_platform}.

Respond with JSON:
{{
  "adapted": "adapted content here",
  "changes": ["list of changes made"],
  "why": "why these changes improve platform fit"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', response_text)

            if json_match:
                data = json.loads(json_match.group())
                adapted_content = data.get("adapted", "")
                analysis = self.analyzer.analyze(adapted_content, to_platform)

                return GeneratedReply(
                    id=generate_id(),
                    content=adapted_content,
                    platform=to_platform,
                    technique_label=self.analyzer.get_technique_label(analysis),
                    hook_type=analysis.hook_type,
                    framework=analysis.framework,
                    triggers=analysis.triggers,
                    voice_match=self._calculate_voice_match(adapted_content, profile or {}),
                    engagement_prediction=0,
                    combined_score=0,
                    why=data.get("why", ""),
                    word_count=analysis.word_count,
                    char_count=analysis.char_count,
                )

        except Exception as e:
            return self._error_reply(f"Adaptation error: {str(e)}")

        return self._error_reply("Could not adapt content")


# Convenience functions
def generate_replies(original_post: Dict, **kwargs) -> List[Dict]:
    """Generate replies and return as dicts."""
    generator = LLMGenerator()
    replies = generator.generate_replies(original_post, **kwargs)
    return [asdict(r) for r in replies]


def generate_post(topic: str, **kwargs) -> Dict:
    """Generate a post and return as dict."""
    generator = LLMGenerator()
    reply = generator.generate_post(topic, **kwargs)
    return asdict(reply)
