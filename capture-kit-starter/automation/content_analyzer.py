"""
Content Analyzer - Deep analysis of social media content

Analyzes hooks, frameworks, triggers, specificity, and authority signals.
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import asdict

from .schemas import (
    ContentAnalysis, HookType, Framework, Trigger,
    PLATFORM_CONFIGS
)


class ContentAnalyzer:
    """
    Deep content analysis for social media posts.
    """

    # Hook patterns
    HOOK_PATTERNS = {
        HookType.QUESTION: [
            r'^\s*[A-Z].*\?',  # Starts with question
            r'^(What|Why|How|When|Where|Who|Which|Do you|Have you|Did you)',
        ],
        HookType.CONTRARIAN: [
            r'(unpopular opinion|hot take|controversial|against the grain)',
            r'(everyone.*(wrong|missing)|nobody.*(talking|realizes))',
            r'(stop|quit|don\'t).*(doing|believing|thinking)',
        ],
        HookType.DATA: [
            r'\d+%',
            r'\$[\d,]+',
            r'(\d+x|\d+X)',
            r'(data|research|study|survey|analysis).*(shows|reveals|finds)',
        ],
        HookType.STORY: [
            r'^(I |My |We |Our |Last |Yesterday |Today |When I)',
            r'(years ago|months ago|story|learned|realized|discovered)',
        ],
        HookType.CALLOUT: [
            r'(@\w+|Hey |Attention |To all|For everyone)',
            r'(If you\'re a|For those who|Anyone who)',
        ],
        HookType.BOLD_CLAIM: [
            r'^(This is|The |Here\'s|There\'s)',
            r'(will change|game.?changer|revolutionary|secret)',
            r'(most people|99%|majority).*(don\'t|won\'t|can\'t)',
        ],
        HookType.HOW_TO: [
            r'^(How to|How I|Here\'s how|Step)',
            r'(\d+ (ways|steps|tips|tricks|secrets))',
        ],
        HookType.LIST: [
            r'^\d+[\.\)]',
            r'(\d+ things|thread|breakdown)',
        ],
    }

    # Trigger patterns
    TRIGGER_PATTERNS = {
        Trigger.FEAR: [
            r'(warning|danger|risk|mistake|avoid|never|fail|lose|crash)',
            r'(don\'t|won\'t|can\'t).*(survive|make it|succeed)',
        ],
        Trigger.GREED: [
            r'(profit|gain|money|wealth|rich|income|revenue)',
            r'(\$[\d,]+|[0-9]+x|\d+%.*return)',
        ],
        Trigger.CURIOSITY: [
            r'(secret|hidden|revealed|discover|surprising|unexpected)',
            r'(what.*actually|real reason|truth about)',
        ],
        Trigger.FOMO: [
            r'(limited|exclusive|only \d+|last chance|ending soon)',
            r'(don\'t miss|before it\'s|while you can)',
        ],
        Trigger.VALIDATION: [
            r'(you\'re right|I agree|exactly|this is why)',
            r'(smart people|successful|winners|top \d+%)',
        ],
        Trigger.URGENCY: [
            r'(now|today|immediately|right now|asap)',
            r'(deadline|expires|ends|last)',
        ],
        Trigger.EXCLUSIVITY: [
            r'(insider|exclusive|only for|members only)',
            r'(few (know|understand|realize)|not many)',
        ],
    }

    # Authority signals
    AUTHORITY_PATTERNS = [
        r'(years of experience|\d+ years)',
        r'(worked (at|with|for))',
        r'(research|study|data|analysis)',
        r'(expert|specialist|professional)',
        r'(built|created|founded|launched)',
        r'(clients|customers|companies)',
        r'(\$[\d,]+[MBK]|\d+[MBK] (users|followers|revenue))',
    ]

    def __init__(self):
        """Initialize analyzer."""
        pass

    def analyze(self, content: str, platform: str = "twitter") -> ContentAnalysis:
        """
        Perform deep analysis of content.

        Args:
            content: The content to analyze
            platform: Target platform

        Returns:
            ContentAnalysis with all metrics
        """
        analysis = ContentAnalysis(
            content=content,
            platform=platform,
        )

        # Basic metrics
        analysis.word_count = len(content.split())
        analysis.char_count = len(content)
        analysis.sentence_count = len(re.split(r'[.!?]+', content))
        analysis.line_count = len(content.split('\n'))

        # Hook analysis
        hook_type, hook_text, hook_strength = self._analyze_hook(content)
        analysis.hook_type = hook_type.value if hook_type else ""
        analysis.hook_text = hook_text
        analysis.hook_strength = hook_strength

        # Framework detection
        analysis.framework = self._detect_framework(content).value

        # Trigger analysis
        triggers, trigger_strength = self._analyze_triggers(content)
        analysis.triggers = [t.value for t in triggers]
        analysis.trigger_strength = trigger_strength

        # Specificity analysis
        specificity, has_numbers, has_data, has_examples = self._analyze_specificity(content)
        analysis.specificity = specificity
        analysis.has_numbers = has_numbers
        analysis.has_data = has_data
        analysis.has_examples = has_examples

        # Authority signals
        analysis.authority_signals = self._detect_authority_signals(content)

        # Platform fit
        platform_score, platform_issues = self._check_platform_fit(content, platform)
        analysis.platform_score = platform_score
        analysis.platform_issues = platform_issues

        # Compile techniques
        analysis.techniques = self._compile_techniques(analysis)

        # Identify strengths and weaknesses
        analysis.strengths, analysis.weaknesses = self._evaluate_content(analysis)

        return analysis

    def _analyze_hook(self, content: str) -> Tuple[HookType, str, float]:
        """Analyze the hook (first line/sentence)."""
        # Get first line
        first_line = content.split('\n')[0].strip()
        if not first_line:
            return None, "", 0.0

        # Get first sentence
        first_sentence = re.split(r'[.!?]', content)[0].strip()

        hook_text = first_line if len(first_line) <= 100 else first_sentence

        # Check against patterns
        best_match = None
        best_strength = 0.0

        for hook_type, patterns in self.HOOK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, hook_text, re.IGNORECASE):
                    # Calculate strength based on position and clarity
                    strength = 0.7
                    if hook_text == first_line[:len(hook_text)]:
                        strength += 0.2  # Bonus for being at very start
                    if len(hook_text) <= 50:
                        strength += 0.1  # Bonus for conciseness

                    if strength > best_strength:
                        best_match = hook_type
                        best_strength = strength
                    break

        return best_match, hook_text[:100], best_strength

    def _detect_framework(self, content: str) -> Framework:
        """Detect the content framework."""
        # Check for thread indicators
        if re.search(r'(thread|🧵|\d+/\d+|^\d+[\.\)])', content, re.IGNORECASE):
            return Framework.THREAD

        # Check for quote tweet style
        if content.strip().startswith('"') or re.search(r'^["\'].*["\']', content):
            return Framework.QUOTE_TWEET

        # Check for reply indicators
        if content.strip().startswith('@'):
            return Framework.REPLY

        # Check for carousel (Instagram)
        if re.search(r'(swipe|slide \d+|carousel)', content, re.IGNORECASE):
            return Framework.CAROUSEL

        return Framework.SINGLE

    def _analyze_triggers(self, content: str) -> Tuple[List[Trigger], float]:
        """Analyze emotional triggers."""
        triggers_found = []
        content_lower = content.lower()

        for trigger, patterns in self.TRIGGER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    if trigger not in triggers_found:
                        triggers_found.append(trigger)
                    break

        # Calculate strength based on number and type of triggers
        strength = min(len(triggers_found) * 0.25, 1.0)

        # Bonus for high-impact triggers
        high_impact = [Trigger.CURIOSITY, Trigger.FOMO, Trigger.FEAR]
        if any(t in triggers_found for t in high_impact):
            strength = min(strength + 0.15, 1.0)

        return triggers_found, strength

    def _analyze_specificity(self, content: str) -> Tuple[str, bool, bool, bool]:
        """Analyze content specificity."""
        has_numbers = bool(re.search(r'\d+', content))
        has_data = bool(re.search(r'(\d+%|\$[\d,]+|data|research|study)', content, re.IGNORECASE))
        has_examples = bool(re.search(r'(for example|e\.g\.|such as|like when)', content, re.IGNORECASE))

        # Count specific elements
        specificity_score = 0
        if has_numbers:
            specificity_score += 1
        if has_data:
            specificity_score += 1
        if has_examples:
            specificity_score += 1
        if re.search(r'(@\w+|\$[A-Z]{1,5})', content):  # Mentions or tickers
            specificity_score += 1

        if specificity_score >= 3:
            specificity = "concrete"
        elif specificity_score >= 1:
            specificity = "moderate"
        else:
            specificity = "vague"

        return specificity, has_numbers, has_data, has_examples

    def _detect_authority_signals(self, content: str) -> List[str]:
        """Detect authority signals in content."""
        signals = []

        for pattern in self.AUTHORITY_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match and match not in signals:
                    signals.append(match)

        return signals[:5]  # Limit to top 5

    def _check_platform_fit(self, content: str, platform: str) -> Tuple[float, List[str]]:
        """Check how well content fits platform requirements."""
        issues = []
        score = 100.0

        config = PLATFORM_CONFIGS.get(platform, {})

        if platform == "twitter":
            # Length checks
            if len(content) > 280:
                issues.append(f"Too long for tweet ({len(content)} chars, max 280)")
                score -= 30

            # Reply length
            reply_range = config.get("reply_length_chars", (70, 100))
            if len(content) < reply_range[0]:
                issues.append(f"Reply too short for engagement")
                score -= 10

        elif platform == "linkedin":
            # Length checks
            length_range = config.get("post_length_chars", (1200, 1500))
            if len(content) < length_range[0] * 0.5:
                issues.append("Consider expanding for LinkedIn depth")
                score -= 15

            # Line breaks
            if config.get("use_line_breaks") and '\n' not in content:
                issues.append("Add line breaks for readability")
                score -= 10

            # External links
            if config.get("avoid_external_links") and re.search(r'https?://', content):
                issues.append("External links reduce LinkedIn reach")
                score -= 20

        elif platform == "instagram":
            # Hashtags
            hashtag_count = len(re.findall(r'#\w+', content))
            hashtag_range = config.get("hashtag_count", (5, 15))
            if hashtag_count < hashtag_range[0]:
                issues.append(f"Add more hashtags ({hashtag_count}, aim for {hashtag_range[0]}-{hashtag_range[1]})")
                score -= 10
            elif hashtag_count > hashtag_range[1]:
                issues.append(f"Too many hashtags ({hashtag_count}, max {hashtag_range[1]})")
                score -= 10

        return max(score, 0), issues

    def _compile_techniques(self, analysis: ContentAnalysis) -> List[str]:
        """Compile list of techniques used."""
        techniques = []

        if analysis.hook_type:
            techniques.append(f"hook:{analysis.hook_type}")

        techniques.append(f"framework:{analysis.framework}")

        for trigger in analysis.triggers:
            techniques.append(f"trigger:{trigger}")

        techniques.append(f"specificity:{analysis.specificity}")

        if analysis.authority_signals:
            techniques.append("authority_signals")

        return techniques

    def _evaluate_content(self, analysis: ContentAnalysis) -> Tuple[List[str], List[str]]:
        """Evaluate content strengths and weaknesses."""
        strengths = []
        weaknesses = []

        # Hook evaluation
        if analysis.hook_strength >= 0.7:
            strengths.append(f"Strong {analysis.hook_type} hook")
        elif not analysis.hook_type:
            weaknesses.append("Missing clear hook")

        # Trigger evaluation
        if len(analysis.triggers) >= 2:
            strengths.append("Multiple emotional triggers")
        elif len(analysis.triggers) == 0:
            weaknesses.append("No emotional triggers detected")

        # Specificity evaluation
        if analysis.specificity == "concrete":
            strengths.append("Concrete and specific")
        elif analysis.specificity == "vague":
            weaknesses.append("Too vague - add specifics")

        # Data evaluation
        if analysis.has_data:
            strengths.append("Data-backed claims")

        # Authority evaluation
        if len(analysis.authority_signals) >= 2:
            strengths.append("Strong authority signals")

        # Platform fit
        if analysis.platform_score >= 80:
            strengths.append(f"Good {analysis.platform} fit")
        elif analysis.platform_issues:
            for issue in analysis.platform_issues[:2]:
                weaknesses.append(issue)

        return strengths, weaknesses

    def get_technique_label(self, analysis: ContentAnalysis) -> str:
        """Get a human-readable technique label."""
        parts = []

        if analysis.hook_type:
            hook_labels = {
                "question": "Question Hook",
                "contrarian": "Contrarian Take",
                "data": "Data Lead",
                "story": "Story Hook",
                "callout": "Direct Callout",
                "bold_claim": "Bold Claim",
                "how_to": "How-To",
                "list": "List Format",
            }
            parts.append(hook_labels.get(analysis.hook_type, analysis.hook_type))

        if analysis.framework != "single":
            framework_labels = {
                "thread": "Thread",
                "quote_tweet": "Quote Tweet",
                "reply": "Reply",
                "carousel": "Carousel",
            }
            parts.append(framework_labels.get(analysis.framework, analysis.framework))

        if analysis.triggers:
            trigger_labels = {
                "fear": "Fear",
                "greed": "Greed",
                "curiosity": "Curiosity",
                "fomo": "FOMO",
                "validation": "Validation",
            }
            top_trigger = analysis.triggers[0]
            parts.append(trigger_labels.get(top_trigger, top_trigger))

        return " + ".join(parts) if parts else "Standard"


# Convenience function
def analyze_content(content: str, platform: str = "twitter") -> Dict[str, Any]:
    """Analyze content and return dict."""
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze(content, platform)
    return asdict(analysis)
