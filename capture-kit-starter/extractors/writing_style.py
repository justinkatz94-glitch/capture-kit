"""
Writing Style Extractor
Analyzes text samples (emails, Slack, docs) to extract writing style patterns.
"""

import re
from collections import Counter
from typing import Dict, List, Any


def extract_writing_style(samples: List[str]) -> Dict[str, Any]:
    """
    Extract writing style from text samples.

    Args:
        samples: List of text samples (emails, messages, documents)

    Returns:
        Writing style analysis with tone, formality, common phrases, sign-offs
    """
    if not samples:
        return {"error": "No samples provided"}

    # Filter empty samples
    samples = [s.strip() for s in samples if s and s.strip()]
    if not samples:
        return {"error": "All samples were empty"}

    # Analyze components
    tone = _analyze_tone(samples)
    formality, formality_label = _analyze_formality(samples)
    sentence_length = _analyze_sentence_length(samples)
    punctuation = _analyze_punctuation(samples)
    common_phrases = _extract_common_phrases(samples)
    sign_off = _analyze_sign_offs(samples)

    return {
        "tone": tone,
        "formality": formality,
        "formality_label": formality_label,
        "avg_sentence_length": sentence_length,
        "punctuation_patterns": punctuation,
        "common_phrases": common_phrases,
        "sign_off": sign_off
    }


def _analyze_tone(samples: List[str]) -> str:
    """Determine overall tone from samples."""
    combined = ' '.join(samples).lower()

    # Tone indicators
    warm_words = ['thanks', 'appreciate', 'great', 'love', 'happy', 'excited',
                  'wonderful', 'pleased', 'glad', 'hope']
    formal_words = ['regarding', 'pursuant', 'hereby', 'acknowledge', 'kindly',
                    'request', 'inform', 'sincerely', 'respectfully']
    casual_words = ['hey', 'cool', 'awesome', 'nice', 'yeah', 'yep', 'gonna',
                    'wanna', 'kinda', 'lol', 'haha']

    warm_count = sum(combined.count(w) for w in warm_words)
    formal_count = sum(combined.count(w) for w in formal_words)
    casual_count = sum(combined.count(w) for w in casual_words)

    # Count exclamations (enthusiasm)
    exclamations = sum(s.count('!') for s in samples)
    avg_exclamations = exclamations / len(samples)

    # Determine tone
    if warm_count > casual_count and avg_exclamations > 0.3:
        return "Professional but warm"
    elif formal_count > casual_count and formal_count > warm_count:
        return "Formal"
    elif casual_count > formal_count and casual_count > warm_count:
        return "Casual"
    elif warm_count > 0 and formal_count > 0:
        return "Professional but warm"
    else:
        return "Neutral"


def _analyze_formality(samples: List[str]) -> tuple:
    """
    Analyze formality level on 1-5 scale.

    Returns:
        (formality_score, formality_label)
    """
    combined = ' '.join(samples).lower()

    # Formality indicators
    formal_markers = [
        'dear ', 'sincerely', 'regards', 'respectfully', 'kindly',
        'i am writing', 'please be advised', 'at your earliest',
        'pursuant to', 'as per', 'hereby'
    ]

    casual_markers = [
        'hey ', 'hi ', 'thanks!', 'cool', 'awesome', 'yeah', 'yep',
        'gonna', 'wanna', 'lol', 'haha', 'btw', 'fyi', '!'
    ]

    contractions = ["don't", "can't", "won't", "i'm", "you're", "we're",
                    "they're", "it's", "that's", "what's", "let's"]

    formal_count = sum(combined.count(m) for m in formal_markers)
    casual_count = sum(combined.count(m) for m in casual_markers)
    contraction_count = sum(combined.count(c) for c in contractions)

    # Calculate average word length (longer = more formal)
    words = re.findall(r'\b[a-z]+\b', combined)
    avg_word_length = sum(len(w) for w in words) / len(words) if words else 4

    # Score calculation
    score = 3  # Start neutral

    if formal_count > 5:
        score += 1
    if casual_count > 10:
        score -= 1
    if contraction_count > len(samples) * 2:
        score -= 0.5
    if avg_word_length > 5:
        score += 0.5
    if avg_word_length < 4:
        score -= 0.5

    # Clamp to 1-5
    score = max(1, min(5, round(score)))

    labels = {
        1: "Very Casual",
        2: "Casual",
        3: "Balanced Professional",
        4: "Formal",
        5: "Very Formal"
    }

    return score, labels[score]


def _analyze_sentence_length(samples: List[str]) -> str:
    """Categorize average sentence length."""
    all_sentences = []

    for sample in samples:
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', sample)
        all_sentences.extend([s.strip() for s in sentences if len(s.strip()) > 3])

    if not all_sentences:
        return "medium"

    # Calculate average word count per sentence
    word_counts = [len(s.split()) for s in all_sentences]
    avg = sum(word_counts) / len(word_counts)

    if avg > 20:
        return "long"
    elif avg < 10:
        return "short"
    else:
        return "medium"


def _analyze_punctuation(samples: List[str]) -> List[str]:
    """Identify punctuation patterns."""
    patterns = []
    combined = ''.join(samples)

    # Check for exclamation usage
    exclamation_count = combined.count('!')
    if exclamation_count > len(samples) * 0.3:
        patterns.append("uses_exclamations")

    # Check for emoji usage
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+"
    )
    emoji_matches = emoji_pattern.findall(combined)
    if emoji_matches:
        patterns.append("occasional_emoji")

    # Check for ellipsis usage
    if combined.count('...') > 2:
        patterns.append("uses_ellipsis")

    # Check for question marks
    if combined.count('?') > len(samples) * 0.2:
        patterns.append("asks_questions")

    # Check for dashes
    if combined.count(' - ') > 3 or combined.count('—') > 3:
        patterns.append("uses_dashes")

    return patterns if patterns else ["standard_punctuation"]


def _extract_common_phrases(samples: List[str]) -> List[str]:
    """Extract commonly used phrases."""
    combined = ' '.join(samples).lower()

    # Predefined phrases to look for
    candidate_phrases = [
        "let me know", "at the end of the day", "let's circle back",
        "happy to", "sounds good", "thanks for", "looking forward",
        "quick question", "just wanted to", "hope this helps",
        "feel free to", "please let me know", "as discussed",
        "moving forward", "per our conversation", "touch base",
        "circle back", "follow up", "reach out", "loop in",
        "on my radar", "take a look", "keep me posted",
        "heads up", "fyi", "just a heads up", "quick update"
    ]

    # Count occurrences
    phrase_counts = {}
    for phrase in candidate_phrases:
        count = combined.count(phrase)
        if count > 0:
            phrase_counts[phrase] = count

    # Sort by frequency and return top phrases
    sorted_phrases = sorted(phrase_counts.items(), key=lambda x: -x[1])
    return [phrase for phrase, _ in sorted_phrases[:8]]


def _analyze_sign_offs(samples: List[str]) -> Dict[str, Any]:
    """Analyze email/message sign-off patterns."""
    # Common sign-offs to detect
    sign_off_patterns = [
        (r'\bBest,?\s*$', 'Best,'),
        (r'\bThanks,?\s*$', 'Thanks,'),
        (r'\bThanks!?\s*$', 'Thanks,'),
        (r'\bCheers,?\s*$', 'Cheers,'),
        (r'\bRegards,?\s*$', 'Regards,'),
        (r'\bBest regards,?\s*$', 'Best regards,'),
        (r'\bSincerely,?\s*$', 'Sincerely,'),
        (r'\bTake care,?\s*$', 'Take care,'),
        (r'\bSarah\s*$', 'Sarah'),  # First name only
        (r'\bThank you,?\s*$', 'Thank you,'),
    ]

    sign_off_counts = Counter()

    for sample in samples:
        # Check last few lines of each sample
        lines = sample.strip().split('\n')
        last_lines = '\n'.join(lines[-4:]) if len(lines) >= 4 else sample

        for pattern, name in sign_off_patterns:
            if re.search(pattern, last_lines, re.IGNORECASE | re.MULTILINE):
                sign_off_counts[name] += 1
                break

    if not sign_off_counts:
        return {
            "most_common": "None detected",
            "frequency": 0,
            "alternatives": []
        }

    total = sum(sign_off_counts.values())
    most_common = sign_off_counts.most_common(1)[0]
    alternatives = [so for so, _ in sign_off_counts.most_common()[1:4]]

    return {
        "most_common": most_common[0],
        "frequency": round(most_common[1] / len(samples), 2),
        "alternatives": alternatives
    }


if __name__ == "__main__":
    # Quick test
    test_samples = [
        "Hi team!\n\nJust a quick update - project is on track.\n\nBest,\nSarah",
        "Thanks for the info! Let me know if you need anything else.\n\nSarah",
        "At the end of the day, we need to deliver quality work.\n\nBest,\nSarah"
    ]

    import json
    result = extract_writing_style(test_samples)
    print(json.dumps(result, indent=2))
