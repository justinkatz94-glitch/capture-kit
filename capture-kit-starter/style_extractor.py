"""
Social Media Style Extractor
Analyzes posts from any platform to extract communication patterns.

This module takes parsed social media data and extracts:
- Emoji usage patterns
- Hashtag style
- Vocabulary complexity
- Tone markers
- Posting time patterns
- Topics and interests
- Cross-platform formality comparison
"""

import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


# Emoji detection (covers most common emoji ranges)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Symbols & pictographs
    "\U0001F680-\U0001F6FF"  # Transport & map
    "\U0001F1E0-\U0001F1FF"  # Flags
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed characters
    "\U0001F900-\U0001F9FF"  # Supplemental symbols
    "\U0001FA00-\U0001FA6F"  # Chess symbols
    "\U0001FA70-\U0001FAFF"  # Symbols extended
    "\U00002600-\U000026FF"  # Misc symbols
    "]+",
    flags=re.UNICODE
)

# Common English stop words
STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
    'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
    'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just',
    'don', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'you', 'your',
    'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'and',
    'but', 'if', 'or', 'because', 'as', 'until', 'while', 'although'
}


def extract_social_style(platform_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze social media data to extract communication style.
    
    Args:
        platform_data: List of parsed platform exports, each containing:
            - platform: str ("twitter", "linkedin", "instagram", "facebook")
            - posts: List[Dict] with at least "content" and optionally "timestamp"
            - profile: Dict (optional)
    
    Returns:
        Comprehensive social media style analysis
    """
    if not platform_data:
        return {"error": "No data provided"}
    
    # Collect all posts and organize by platform
    all_posts = []
    platform_breakdown = {}
    
    for data in platform_data:
        platform = data.get("platform", "unknown")
        posts = data.get("posts", [])
        
        # Analyze this platform's posts
        platform_breakdown[platform] = _analyze_platform(posts)
        
        # Add to combined pool
        for post in posts:
            post_copy = post.copy()
            post_copy["_platform"] = platform
            all_posts.append(post_copy)
    
    # Extract all content for combined analysis
    all_content = [p.get("content", "") for p in all_posts if p.get("content")]
    
    if not all_content:
        return {
            "error": "No content found in posts",
            "platforms": list(platform_breakdown.keys())
        }
    
    # Build comprehensive analysis
    return {
        "total_posts_analyzed": len(all_posts),
        "platforms": list(platform_breakdown.keys()),
        
        # Overall style metrics
        "emoji_usage": _analyze_emoji_usage(all_content),
        "hashtag_style": _analyze_hashtag_style(all_content),
        "vocabulary": _analyze_vocabulary(all_content),
        "tone": _analyze_tone(all_content),
        "posting_patterns": _analyze_posting_patterns(all_posts),
        
        # Content analysis
        "topics": _extract_topics(all_content),
        "writing_metrics": _analyze_writing_metrics(all_content),
        
        # Per-platform breakdown
        "by_platform": platform_breakdown,
        
        # Cross-platform comparison
        "formality_comparison": _compare_formality(platform_breakdown),
        "style_consistency": _analyze_consistency(platform_breakdown)
    }


def _analyze_platform(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze posts from a single platform."""
    if not posts:
        return {"post_count": 0}
    
    content_list = [p.get("content", "") for p in posts if p.get("content")]
    if not content_list:
        return {"post_count": len(posts), "content_posts": 0}
    
    # Basic metrics
    lengths = [len(c.split()) for c in content_list]
    char_lengths = [len(c) for c in content_list]
    
    # Emoji analysis
    emoji_count = sum(len(EMOJI_PATTERN.findall(c)) for c in content_list)
    posts_with_emoji = sum(1 for c in content_list if EMOJI_PATTERN.search(c))
    
    # Hashtag analysis
    hashtag_count = sum(c.count('#') for c in content_list)
    
    # Question analysis (engagement indicator)
    question_count = sum(c.count('?') for c in content_list)
    
    # Link sharing
    link_count = sum(1 for c in content_list if 'http' in c.lower() or 'www.' in c.lower())
    
    return {
        "post_count": len(posts),
        "content_posts": len(content_list),
        "avg_words": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "avg_characters": round(sum(char_lengths) / len(char_lengths), 1) if char_lengths else 0,
        "emoji_per_post": round(emoji_count / len(content_list), 2),
        "posts_with_emoji_pct": round(posts_with_emoji / len(content_list) * 100, 1),
        "hashtags_per_post": round(hashtag_count / len(content_list), 2),
        "questions_asked": question_count,
        "posts_with_links_pct": round(link_count / len(content_list) * 100, 1)
    }


def _analyze_emoji_usage(content_list: List[str]) -> Dict[str, Any]:
    """Analyze emoji patterns across all posts."""
    all_emoji = []
    posts_with_emoji = 0
    
    for content in content_list:
        emojis = EMOJI_PATTERN.findall(content)
        if emojis:
            posts_with_emoji += 1
            # Flatten (some emoji are multi-char)
            for e in emojis:
                all_emoji.extend(list(e))
    
    if not content_list:
        return {"style": "none", "frequency": 0}
    
    freq = posts_with_emoji / len(content_list)
    
    # Categorize style
    if freq > 0.6:
        style = "heavy"
    elif freq > 0.3:
        style = "moderate"
    elif freq > 0.1:
        style = "light"
    else:
        style = "minimal"
    
    # Top emoji
    emoji_counter = Counter(all_emoji)
    top_emoji = [e for e, _ in emoji_counter.most_common(10)]
    
    return {
        "style": style,
        "frequency": round(freq, 2),
        "per_post": round(len(all_emoji) / len(content_list), 2) if content_list else 0,
        "top_emoji": top_emoji,
        "total_emoji_used": len(all_emoji)
    }


def _analyze_hashtag_style(content_list: List[str]) -> Dict[str, Any]:
    """Analyze hashtag usage patterns."""
    all_hashtags = []
    
    for content in content_list:
        hashtags = re.findall(r'#(\w+)', content)
        all_hashtags.extend([h.lower() for h in hashtags])
    
    if not all_hashtags:
        return {
            "style": "none",
            "per_post": 0,
            "top_hashtags": []
        }
    
    avg_per_post = len(all_hashtags) / len(content_list)
    
    # Categorize style
    if avg_per_post > 5:
        style = "heavy"  # Looks like marketing
    elif avg_per_post > 2:
        style = "active"
    elif avg_per_post > 0.5:
        style = "moderate"
    else:
        style = "minimal"
    
    # Top hashtags
    hashtag_counter = Counter(all_hashtags)
    
    return {
        "style": style,
        "per_post": round(avg_per_post, 2),
        "top_hashtags": [h for h, _ in hashtag_counter.most_common(15)],
        "unique_hashtags": len(set(all_hashtags)),
        "total_hashtags": len(all_hashtags)
    }


def _analyze_vocabulary(content_list: List[str]) -> Dict[str, Any]:
    """Analyze vocabulary patterns."""
    all_words = []
    
    for content in content_list:
        # Clean and tokenize
        clean = re.sub(r'[^\w\s]', ' ', content.lower())
        clean = re.sub(r'\s+', ' ', clean)
        words = [w for w in clean.split() if len(w) > 1 and w not in STOP_WORDS]
        all_words.extend(words)
    
    if not all_words:
        return {"level": "unknown", "breadth": "unknown"}
    
    # Average word length (complexity proxy)
    avg_length = sum(len(w) for w in all_words) / len(all_words)
    
    # Vocabulary breadth (unique ratio)
    unique_ratio = len(set(all_words)) / len(all_words)
    
    # Categorize complexity
    if avg_length > 6:
        level = "advanced"
    elif avg_length > 5:
        level = "professional"
    elif avg_length > 4:
        level = "moderate"
    else:
        level = "casual"
    
    # Breadth categorization
    if unique_ratio > 0.5:
        breadth = "highly_varied"
    elif unique_ratio > 0.35:
        breadth = "varied"
    elif unique_ratio > 0.2:
        breadth = "focused"
    else:
        breadth = "repetitive"
    
    # Signature words (frequent non-common words)
    word_counter = Counter(all_words)
    signature_words = [w for w, c in word_counter.most_common(30) if c > 1][:15]
    
    return {
        "level": level,
        "breadth": breadth,
        "avg_word_length": round(avg_length, 2),
        "unique_ratio": round(unique_ratio, 2),
        "total_words": len(all_words),
        "unique_words": len(set(all_words)),
        "signature_words": signature_words
    }


def _analyze_tone(content_list: List[str]) -> Dict[str, Any]:
    """Analyze tone markers in content."""
    combined = ' '.join(content_list).lower()
    total = len(content_list)
    
    if total == 0:
        return {"overall": "unknown"}
    
    # Excitement indicators
    exclamation_posts = sum(1 for c in content_list if '!' in c)
    caps_posts = sum(1 for c in content_list if any(
        word.isupper() and len(word) > 2 for word in c.split()
    ))
    
    # Hedging/uncertainty
    hedge_phrases = ['maybe', 'perhaps', 'might', 'could be', 'i think', 'i guess', 
                     'not sure', 'possibly', 'kind of', 'sort of']
    hedge_count = sum(combined.count(h) for h in hedge_phrases)
    
    # Confidence markers
    confidence_phrases = ['definitely', 'absolutely', 'clearly', 'obviously', 
                         'certainly', 'without doubt', 'for sure', 'no question']
    confidence_count = sum(combined.count(c) for c in confidence_phrases)
    
    # Positivity vs negativity (simple lexicon)
    positive_words = ['love', 'great', 'amazing', 'awesome', 'excited', 'happy',
                     'wonderful', 'fantastic', 'excellent', 'best', 'thanks', 'grateful']
    negative_words = ['hate', 'terrible', 'awful', 'worst', 'disappointed', 'frustrated',
                     'annoyed', 'angry', 'sad', 'bad', 'horrible', 'disgusting']
    
    positive_count = sum(combined.count(w) for w in positive_words)
    negative_count = sum(combined.count(w) for w in negative_words)
    
    # Determine overall tone
    excitement_ratio = exclamation_posts / total
    
    if excitement_ratio > 0.5:
        energy = "high_energy"
    elif excitement_ratio > 0.2:
        energy = "energetic"
    elif excitement_ratio > 0.05:
        energy = "balanced"
    else:
        energy = "measured"
    
    # Sentiment leaning
    if positive_count > negative_count * 2:
        sentiment = "positive"
    elif negative_count > positive_count * 2:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "energy": energy,
        "sentiment": sentiment,
        "exclamation_frequency": round(excitement_ratio, 2),
        "uses_caps_emphasis": caps_posts > total * 0.1,
        "hedging_tendency": "high" if hedge_count > total else "moderate" if hedge_count > total * 0.3 else "low",
        "confidence_markers": confidence_count,
        "positive_signals": positive_count,
        "negative_signals": negative_count
    }


def _analyze_posting_patterns(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze when posts are made."""
    hours = []
    days = []
    
    for post in posts:
        ts = post.get("timestamp")
        if not ts:
            continue
        
        dt = _parse_timestamp(ts)
        if dt:
            hours.append(dt.hour)
            days.append(dt.strftime('%A'))
    
    if not hours:
        return {"analysis": "insufficient_timestamp_data"}
    
    # Hour analysis
    hour_counter = Counter(hours)
    peak_hours = [h for h, _ in hour_counter.most_common(3)]
    
    # Day analysis
    day_counter = Counter(days)
    peak_days = [d for d, _ in day_counter.most_common(2)]
    
    # Time preference
    morning = sum(1 for h in hours if 5 <= h < 12)
    afternoon = sum(1 for h in hours if 12 <= h < 17)
    evening = sum(1 for h in hours if 17 <= h < 22)
    night = sum(1 for h in hours if h >= 22 or h < 5)
    
    max_period = max(morning, afternoon, evening, night)
    if max_period == morning:
        time_preference = "morning_person"
    elif max_period == evening:
        time_preference = "evening_poster"
    elif max_period == night:
        time_preference = "night_owl"
    else:
        time_preference = "daytime_active"
    
    return {
        "peak_hours": peak_hours,
        "peak_days": peak_days,
        "time_preference": time_preference,
        "morning_posts": morning,
        "afternoon_posts": afternoon,
        "evening_posts": evening,
        "night_posts": night,
        "analyzed_posts": len(hours)
    }


def _extract_topics(content_list: List[str]) -> List[str]:
    """Extract likely topics/interests from content."""
    combined = ' '.join(content_list).lower()
    
    # Topic keyword mapping
    topic_keywords = {
        "technology": ["ai", "tech", "software", "app", "startup", "coding", "data", "machine learning", "api", "developer"],
        "business": ["business", "marketing", "sales", "growth", "revenue", "startup", "entrepreneur", "client", "customer"],
        "career": ["job", "career", "hiring", "interview", "resume", "linkedin", "networking", "promotion", "salary"],
        "personal": ["family", "kids", "weekend", "vacation", "birthday", "friends", "home", "life"],
        "professional": ["team", "project", "launch", "milestone", "meeting", "deadline", "collaboration"],
        "creative": ["design", "art", "creative", "brand", "visual", "photography", "video", "content"],
        "health": ["fitness", "health", "workout", "running", "meditation", "wellness", "gym", "diet"],
        "finance": ["investing", "stocks", "crypto", "money", "finance", "market", "trading", "portfolio"],
        "education": ["learning", "course", "book", "reading", "study", "university", "degree", "skill"],
        "news": ["news", "politics", "election", "government", "policy", "world", "economy"]
    }
    
    detected = []
    for topic, keywords in topic_keywords.items():
        matches = sum(1 for kw in keywords if kw in combined)
        if matches >= 2:  # At least 2 keyword matches
            detected.append(topic)
    
    return detected


def _analyze_writing_metrics(content_list: List[str]) -> Dict[str, Any]:
    """Analyze basic writing metrics."""
    if not content_list:
        return {}
    
    # Sentence-like segments
    all_sentences = []
    for content in content_list:
        sentences = re.split(r'[.!?]+', content)
        all_sentences.extend([s.strip() for s in sentences if len(s.strip()) > 3])
    
    if not all_sentences:
        return {}
    
    # Average sentence length
    sent_lengths = [len(s.split()) for s in all_sentences]
    avg_sent_length = sum(sent_lengths) / len(sent_lengths)
    
    # Categorize
    if avg_sent_length > 20:
        sentence_style = "long_form"
    elif avg_sent_length > 12:
        sentence_style = "standard"
    elif avg_sent_length > 6:
        sentence_style = "concise"
    else:
        sentence_style = "punchy"
    
    return {
        "avg_sentence_length": round(avg_sent_length, 1),
        "sentence_style": sentence_style,
        "total_sentences": len(all_sentences)
    }


def _compare_formality(platform_breakdown: Dict[str, Dict]) -> Dict[str, str]:
    """Compare formality levels across platforms."""
    formality = {}
    
    for platform, metrics in platform_breakdown.items():
        if metrics.get("post_count", 0) == 0:
            formality[platform] = "unknown"
            continue
        
        avg_words = metrics.get("avg_words", 0)
        emoji_rate = metrics.get("emoji_per_post", 0)
        
        # LinkedIn is inherently more formal
        if platform == "linkedin":
            formality[platform] = "formal"
        # Instagram tends casual
        elif platform == "instagram":
            formality[platform] = "casual"
        # Twitter/Facebook depends on content
        else:
            if avg_words > 30 and emoji_rate < 0.3:
                formality[platform] = "formal"
            elif avg_words < 15 or emoji_rate > 1:
                formality[platform] = "casual"
            else:
                formality[platform] = "balanced"
    
    return formality


def _analyze_consistency(platform_breakdown: Dict[str, Dict]) -> Dict[str, Any]:
    """Analyze consistency across platforms."""
    if len(platform_breakdown) < 2:
        return {"analysis": "need_multiple_platforms"}
    
    # Compare emoji usage
    emoji_rates = [m.get("emoji_per_post", 0) for m in platform_breakdown.values()]
    emoji_variance = max(emoji_rates) - min(emoji_rates) if emoji_rates else 0
    
    # Compare post lengths
    avg_words = [m.get("avg_words", 0) for m in platform_breakdown.values() if m.get("avg_words")]
    length_variance = max(avg_words) - min(avg_words) if avg_words else 0
    
    # Consistency score (0-1, higher = more consistent)
    emoji_consistency = 1 - min(emoji_variance / 2, 1)  # Normalize
    length_consistency = 1 - min(length_variance / 50, 1)  # Normalize
    
    overall = (emoji_consistency + length_consistency) / 2
    
    if overall > 0.7:
        verdict = "highly_consistent"
    elif overall > 0.4:
        verdict = "moderately_consistent"
    else:
        verdict = "varies_by_platform"
    
    return {
        "verdict": verdict,
        "consistency_score": round(overall, 2),
        "emoji_variance": round(emoji_variance, 2),
        "length_variance": round(length_variance, 1)
    }


def _parse_timestamp(ts: Any) -> Optional[datetime]:
    """Parse various timestamp formats."""
    if not ts:
        return None
    
    # Unix timestamp
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(ts)
        except (ValueError, OSError):
            return None
    
    # ISO string
    if isinstance(ts, str):
        for fmt in [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%a %b %d %H:%M:%S %z %Y",  # Twitter format
        ]:
            try:
                return datetime.strptime(ts.replace('Z', '+0000'), fmt)
            except ValueError:
                continue
        
        # Try ISO parse as fallback
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    return None


# CLI usage
if __name__ == "__main__":
    import json
    
    # Example usage with sample data
    sample_data = [{
        "platform": "twitter",
        "posts": [
            {"content": "Just shipped the new feature! Team crushed it ðŸš€", "timestamp": "2025-01-15T14:32:00Z"},
            {"content": "Great meeting with the team today. Excited about Q2 plans!", "timestamp": "2025-01-14T10:00:00Z"},
            {"content": "Anyone else think AI is moving faster than we expected? ðŸ¤– #AI #tech", "timestamp": "2025-01-13T09:15:00Z"},
            {"content": "Monday motivation: ship something today ðŸ’ª", "timestamp": "2025-01-13T08:00:00Z"},
        ]
    }]
    
    result = extract_social_style(sample_data)
    print(json.dumps(result, indent=2))
