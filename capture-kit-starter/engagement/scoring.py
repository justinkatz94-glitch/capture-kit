"""
Reply Scoring - Score replies for voice match and engagement potential

Scoring criteria:
1. Voice Match - How much does it sound like YOU
2. Engagement Potential - Based on benchmark patterns
3. Length Optimization - Target ~26 words
"""

import re
from typing import Dict, List, Any


def score_reply(
    text: str,
    voice: Dict[str, Any],
    patterns: Dict[str, Any],
    target_length: int = 26
) -> Dict[str, float]:
    """
    Score a reply for quality.

    Args:
        text: The reply text
        voice: User's voice profile
        patterns: Benchmark patterns
        target_length: Target word count

    Returns:
        Dict with scores
    """
    voice_score = calculate_voice_match(text, voice)
    engagement_score = calculate_engagement_potential(text, patterns)
    length_score = calculate_length_score(text, target_length)

    # Combined score (weighted average)
    combined = (
        voice_score * 0.35 +
        engagement_score * 0.45 +
        length_score * 0.20
    )

    return {
        "voice_match": round(voice_score, 1),
        "engagement_potential": round(engagement_score, 1),
        "length_score": round(length_score, 1),
        "combined_score": round(combined, 1),
    }


def calculate_voice_match(text: str, voice: Dict[str, Any]) -> float:
    """
    Calculate how well text matches user's voice.

    Factors:
    - Tone alignment
    - Vocabulary level match
    - Signature phrases used
    - Formality match
    - Emoji usage match

    Returns:
        Score 0-100
    """
    score = 50  # Start at neutral

    text_lower = text.lower()
    words = text.split()

    # Tone matching
    tone = voice.get("tone", "professional")
    if tone == "professional":
        # Professional markers
        professional_markers = [
            "data", "suggest", "indicate", "perspective", "context",
            "positioning", "setup", "level", "watch", "monitor"
        ]
        matches = sum(1 for m in professional_markers if m in text_lower)
        score += min(matches * 3, 15)

        # Penalize casual markers
        casual_markers = ["lol", "lmao", "tbh", "ngl", "bruh", "bro"]
        casual_count = sum(1 for m in casual_markers if m in text_lower)
        score -= casual_count * 5

    elif tone == "casual":
        casual_markers = ["pretty", "kinda", "yeah", "cool", "nice"]
        matches = sum(1 for m in casual_markers if m in text_lower)
        score += min(matches * 3, 15)

    # Vocabulary level matching
    vocab_level = voice.get("vocabulary", "professional")
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)

    if vocab_level == "professional":
        if 5 <= avg_word_length <= 7:
            score += 10
        elif avg_word_length > 7:
            score += 5
    elif vocab_level == "simple":
        if avg_word_length <= 5:
            score += 10

    # Signature phrases
    signature_phrases = voice.get("signature_phrases", [])
    for phrase in signature_phrases:
        if phrase.lower() in text_lower:
            score += 8  # Bonus for using signature phrase

    # Formality matching
    formality = voice.get("formality", "balanced")
    contractions = ["don't", "can't", "won't", "isn't", "aren't", "it's", "that's"]
    contraction_count = sum(1 for c in contractions if c in text_lower)

    if formality == "formal":
        score -= contraction_count * 2  # Penalize contractions
    elif formality == "casual":
        score += contraction_count * 2  # Reward contractions

    # Emoji usage
    emoji_style = voice.get("emoji_style", "minimal")
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]', text))

    if emoji_style == "minimal":
        if emoji_count == 0:
            score += 5
        else:
            score -= emoji_count * 3
    elif emoji_style == "light":
        if emoji_count == 1:
            score += 5
        elif emoji_count > 2:
            score -= (emoji_count - 2) * 3

    # Sentence structure
    sentence_style = voice.get("sentence_length", "concise")
    sentences = re.split(r'[.!?]', text)
    avg_sentence_words = len(words) / max(len([s for s in sentences if s.strip()]), 1)

    if sentence_style == "concise":
        if avg_sentence_words <= 12:
            score += 10
        elif avg_sentence_words > 20:
            score -= 5

    # Clamp to 0-100
    return max(0, min(100, score))


def calculate_engagement_potential(text: str, patterns: Dict[str, Any]) -> float:
    """
    Calculate engagement potential based on benchmark patterns.

    Factors:
    - Hook type match
    - Optimal length
    - Topic relevance
    - Engagement triggers

    Returns:
        Score 0-100
    """
    score = 50  # Start at neutral

    text_lower = text.lower()
    words = text.split()

    # Hook analysis - first sentence/phrase
    first_sentence = re.split(r'[.!?]', text)[0].strip()

    # Check for effective hook types
    hooks = patterns.get("hooks", [])
    hook_types_found = []

    # Question hook
    if "?" in first_sentence:
        hook_types_found.append("question")
        score += 10

    # Number hook
    if re.search(r'^\d', first_sentence) or re.search(r'\d+%', first_sentence):
        hook_types_found.append("number")
        score += 8

    # Personal hook
    if first_sentence.lower().startswith(("i ", "my ", "i've ", "i'm ")):
        hook_types_found.append("personal")
        score += 5

    # Bold claim hook
    if first_sentence.lower().startswith(("this is", "the key", "exactly", "spot on")):
        hook_types_found.append("bold_claim")
        score += 7

    # Length optimization
    optimal_length = patterns.get("optimal_length", {})
    target = optimal_length.get("avg", 26)
    word_count = len(words)

    length_diff = abs(word_count - target)
    if length_diff <= 5:
        score += 15
    elif length_diff <= 10:
        score += 8
    elif length_diff > 15:
        score -= 10

    # Engagement trigger words
    engagement_triggers = [
        "key", "important", "watch", "signal", "data", "shows",
        "this is", "here's", "notice", "look at", "the real",
        "actually", "truth", "most people", "few understand"
    ]
    trigger_count = sum(1 for t in engagement_triggers if t in text_lower)
    score += min(trigger_count * 4, 15)

    # Concrete details (numbers, specifics)
    has_numbers = bool(re.search(r'\d', text))
    has_ticker = bool(re.search(r'\$[A-Z]{1,5}', text))

    if has_numbers:
        score += 5
    if has_ticker:
        score += 5

    # Readability - short sentences are better for engagement
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    if sentences:
        avg_sentence_length = word_count / len(sentences)
        if avg_sentence_length <= 12:
            score += 10
        elif avg_sentence_length > 20:
            score -= 5

    # Call to action or conversation starter
    cta_patterns = ["what do you", "thoughts?", "agree?", "how about", "curious"]
    has_cta = any(p in text_lower for p in cta_patterns)
    if has_cta:
        score += 8

    # Clamp to 0-100
    return max(0, min(100, score))


def calculate_length_score(text: str, target: int = 26) -> float:
    """
    Score based on length optimization.

    Returns:
        Score 0-100
    """
    words = text.split()
    word_count = len(words)

    # Perfect length
    if word_count == target:
        return 100

    # Calculate penalty for deviation
    diff = abs(word_count - target)

    if diff <= 3:
        return 95
    elif diff <= 5:
        return 85
    elif diff <= 10:
        return 70
    elif diff <= 15:
        return 50
    else:
        return max(20, 100 - (diff * 3))


def analyze_reply_quality(
    text: str,
    voice: Dict[str, Any],
    patterns: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Detailed analysis of reply quality.

    Returns:
        Detailed breakdown of scores and suggestions
    """
    scores = score_reply(text, voice, patterns)

    # Analyze specifics
    words = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]

    analysis = {
        "scores": scores,
        "metrics": {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
            "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
        },
        "voice_breakdown": {
            "tone_match": "good" if scores["voice_match"] >= 60 else "needs work",
            "vocabulary_match": "good" if scores["voice_match"] >= 60 else "adjust",
        },
        "engagement_breakdown": {
            "has_hook": "?" in text[:50] or text.lower().startswith(("this", "the", "key")),
            "has_specifics": bool(re.search(r'\d', text)),
            "length_optimized": 20 <= len(words) <= 32,
        },
        "suggestions": []
    }

    # Generate suggestions
    if len(words) > 32:
        analysis["suggestions"].append("Consider shortening - optimal length is ~26 words")
    elif len(words) < 15:
        analysis["suggestions"].append("Could add more substance - aim for ~26 words")

    if scores["voice_match"] < 60:
        analysis["suggestions"].append("Review your voice profile - reply may not sound like you")

    if scores["engagement_potential"] < 60:
        analysis["suggestions"].append("Add a stronger hook or specific details for better engagement")

    if not analysis["engagement_breakdown"]["has_hook"]:
        analysis["suggestions"].append("Start with a question or bold statement for a stronger hook")

    return analysis
