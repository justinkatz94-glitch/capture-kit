"""
Speaking Style Extractor
Analyzes transcripts to extract verbal communication patterns.
"""

import re
from collections import Counter
from typing import Dict, List, Any


def extract_speaking_style(transcripts: List[str]) -> Dict[str, Any]:
    """
    Extract speaking style from meeting/call transcripts.

    Args:
        transcripts: List of transcript text samples

    Returns:
        Speaking style analysis with pace, filler words, directness, verbal habits
    """
    if not transcripts:
        return {"error": "No transcripts provided"}

    # Filter empty transcripts
    transcripts = [t.strip() for t in transcripts if t and t.strip()]
    if not transcripts:
        return {"error": "All transcripts were empty"}

    # Combine all text for analysis
    combined = ' '.join(transcripts).lower()
    word_count = len(combined.split())

    # Analyze components
    pace = _analyze_pace(transcripts)
    filler_words = _analyze_filler_words(combined, word_count)
    vocabulary_level = _analyze_vocabulary_level(combined)
    directness, directness_label = _analyze_directness(combined, word_count)
    verbal_habits = _extract_verbal_habits(combined)

    return {
        "pace": pace,
        "filler_words": filler_words,
        "vocabulary_level": vocabulary_level,
        "directness": directness,
        "directness_label": directness_label,
        "verbal_habits": verbal_habits
    }


def _analyze_pace(transcripts: List[str]) -> str:
    """
    Estimate speaking pace from transcript structure.
    Based on sentence length and complexity.
    """
    all_text = ' '.join(transcripts)

    # Split into sentence-like segments
    sentences = re.split(r'[.!?]+', all_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    if not sentences:
        return "medium"

    # Calculate average words per segment
    avg_words = sum(len(s.split()) for s in sentences) / len(sentences)

    # Check for pauses indicated in transcripts
    pause_indicators = all_text.lower().count('...') + all_text.lower().count('um') + all_text.lower().count('uh')
    pause_ratio = pause_indicators / len(sentences) if sentences else 0

    if avg_words > 15 and pause_ratio < 0.3:
        return "fast"
    elif avg_words < 8 or pause_ratio > 0.8:
        return "slow"
    else:
        return "medium"


def _analyze_filler_words(text: str, total_words: int) -> List[Dict[str, Any]]:
    """
    Count filler word usage.
    """
    filler_patterns = {
        "um": r'\bum\b',
        "uh": r'\buh\b',
        "like": r'\blike\b',
        "you know": r'\byou know\b',
        "so": r'\bso,',  # "so" at start of clause
        "basically": r'\bbasically\b',
        "actually": r'\bactually\b',
        "right": r'\bright\?',  # "right?" as filler
        "I mean": r'\bi mean\b',
    }

    results = []

    for word, pattern in filler_patterns.items():
        count = len(re.findall(pattern, text, re.IGNORECASE))
        if count > 0:
            per_100 = round((count / total_words) * 100, 1) if total_words else 0
            results.append({
                "word": word,
                "per_100_words": per_100
            })

    # Sort by frequency
    results.sort(key=lambda x: -x["per_100_words"])

    return results[:5]  # Return top 5


def _analyze_vocabulary_level(text: str) -> str:
    """
    Assess vocabulary complexity.
    """
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    if not words:
        return "moderate"

    # Calculate average word length
    avg_length = sum(len(w) for w in words) / len(words)

    # Check for advanced vocabulary
    advanced_words = [
        'specifically', 'essentially', 'fundamentally', 'comprehensive',
        'strategic', 'implementation', 'differentiate', 'perspective',
        'infrastructure', 'optimization', 'leverage', 'methodology'
    ]
    advanced_count = sum(text.count(w) for w in advanced_words)

    # Simple/casual words
    simple_words = [
        'good', 'bad', 'nice', 'cool', 'stuff', 'thing', 'things',
        'get', 'got', 'big', 'small', 'lot', 'lots'
    ]
    simple_count = sum(text.count(w) for w in simple_words)

    # Determine level
    if avg_length > 5 and advanced_count > 5:
        return "advanced"
    elif avg_length < 4 or simple_count > advanced_count * 3:
        return "simple"
    else:
        return "moderate"


def _analyze_directness(text: str, total_words: int) -> tuple:
    """
    Analyze directness level on 1-5 scale.

    Returns:
        (directness_score, directness_label)
    """
    # Hedging/softening language
    hedging_phrases = [
        'maybe', 'perhaps', 'might', 'could', 'possibly',
        'i think', 'i guess', 'sort of', 'kind of', 'a bit',
        'not sure', 'i wonder', 'it seems', 'probably'
    ]

    # Direct/assertive language
    direct_phrases = [
        'we need', 'we should', 'i want', "let's", 'definitely',
        'absolutely', 'clearly', 'obviously', 'i believe',
        'the point is', 'here\'s the thing', 'bottom line'
    ]

    hedge_count = sum(text.count(phrase) for phrase in hedging_phrases)
    direct_count = sum(text.count(phrase) for phrase in direct_phrases)

    # Calculate ratio
    hedge_ratio = hedge_count / (total_words / 100) if total_words else 0
    direct_ratio = direct_count / (total_words / 100) if total_words else 0

    # Score calculation
    if direct_ratio > hedge_ratio * 2:
        score = 5
    elif direct_ratio > hedge_ratio:
        score = 4
    elif hedge_ratio > direct_ratio * 2:
        score = 2
    elif hedge_ratio > direct_ratio:
        score = 3
    else:
        score = 3

    labels = {
        1: "Very Indirect",
        2: "Indirect",
        3: "Balanced",
        4: "Direct but Diplomatic",
        5: "Very Direct"
    }

    return score, labels[score]


def _extract_verbal_habits(text: str) -> List[str]:
    """
    Extract recurring verbal phrases/habits.
    """
    # Common verbal habits to look for
    habits = [
        "at the end of the day",
        "let's circle back",
        "let me be clear",
        "i want to be clear",
        "to be honest",
        "honestly",
        "the thing is",
        "here's the thing",
        "what i'm saying is",
        "my point is",
        "bottom line",
        "long story short",
        "that said",
        "having said that",
        "in terms of",
        "when it comes to",
        "as i mentioned",
        "like i said",
        "you know what i mean",
        "does that make sense",
        "if that makes sense",
        "moving forward",
        "going forward",
        "at this point",
        "for what it's worth"
    ]

    found_habits = []
    for habit in habits:
        count = text.count(habit)
        if count >= 1:  # Found at least once
            found_habits.append((habit, count))

    # Sort by frequency and return just the phrases
    found_habits.sort(key=lambda x: -x[1])
    return [habit for habit, _ in found_habits[:6]]


if __name__ == "__main__":
    # Quick test
    test_transcripts = [
        """So, um, I think at the end of the day we need to focus on the client.
        Let's circle back on this after we review the data.""",
        """You know, I want to be clear about our approach here.
        We should definitely prioritize quality over speed."""
    ]

    import json
    result = extract_speaking_style(test_transcripts)
    print(json.dumps(result, indent=2))
