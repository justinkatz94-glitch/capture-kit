# Capture Kit - Social Media Collection Module

## Overview

Capture the user's **own** social media activity to enrich their AI profile. This is NOT scraping others â€” it's helping users export and analyze their own public presence.

---

## Legal/Ethical Framework

### âœ… What We CAN Do
- Help users export their **own** data
- Use official platform data export features (GDPR "Download Your Data")
- Scrape with user's **own authenticated session**
- Analyze public posts the user themselves authored

### âŒ What We WON'T Do
- Scrape other people's profiles
- Bypass authentication
- Violate platform ToS for commercial data harvesting
- Store credentials (we use active browser sessions)

### The "Mirror Test"
> "Would the user be comfortable if we showed them exactly what we collected?"

If yes â†’ proceed. If no â†’ don't collect it.

---

## Data Collection Strategies (Ranked by Preference)

### Strategy 1: Official Data Exports (Best)
Most platforms let users download their data. This is:
- Fully legal
- Complete historical data
- Clean structured format

| Platform | Export Location | Format | Wait Time |
|----------|-----------------|--------|-----------|
| Twitter/X | Settings â†’ Your Account â†’ Download Archive | JSON/HTML | Minutes to hours |
| LinkedIn | Settings â†’ Data Privacy â†’ Get a copy | JSON | ~24 hours |
| Facebook | Settings â†’ Your Information â†’ Download | JSON/HTML | Minutes to hours |
| Instagram | Settings â†’ Your Activity â†’ Download | JSON | ~48 hours |
| TikTok | Settings â†’ Account â†’ Download Data | JSON | ~3 days |

**Flow:**
1. App shows user: "To capture your social presence, download your data from these platforms"
2. Provides direct links and simple instructions
3. User uploads the ZIP files to the app
4. We parse and extract relevant signals

### Strategy 2: Browser Extension (Good)
A lightweight extension that:
- Runs while user is logged into their accounts
- Captures their posts/comments as they scroll
- Works on any platform without API access

**Pros:** Real-time, works everywhere
**Cons:** Requires user to browse their own history

### Strategy 3: Authenticated Scraping (Acceptable)
User provides active session (logged-in browser):
- Playwright/Puppeteer automates their logged-in browser
- Navigates to their profile and collects posts
- User watches it happen (transparent)

**Pros:** Fast, comprehensive
**Cons:** Feels more invasive, platform changes break it

### Strategy 4: API Access (Limited)
Official APIs where available:
- Twitter API (paid, limited)
- LinkedIn API (restricted to approved apps)
- Meta API (mostly for business pages)

**Pros:** Stable, legal
**Cons:** Expensive, limited data, approval required

---

## Recommended Approach for Capture Kit

### Phase 1: Data Export Helper (Ship First)
Simple, legal, no technical risk:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚          CAPTURE YOUR SOCIAL PRESENCE                        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                              â”‚
â”‚  We'll analyze your public posts to understand your voice.  â”‚
â”‚  Download your data from any platforms you use:             â”‚
â”‚                                                              â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”        â”‚
â”‚  â”‚ Twitter â”‚  â”‚LinkedIn â”‚  â”‚Facebook â”‚  â”‚Instagramâ”‚        â”‚
â”‚  â”‚    â†“    â”‚  â”‚    â†“    â”‚  â”‚    â†“    â”‚  â”‚    â†“    â”‚        â”‚
â”‚  â”‚[Get Data]â”‚  â”‚[Get Data]â”‚  â”‚[Get Data]â”‚  â”‚[Get Data]â”‚     â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜        â”‚
â”‚                                                              â”‚
â”‚  Then drag your ZIP files here:                             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”‚
â”‚  â”‚                                                    â”‚      â”‚
â”‚  â”‚            ðŸ“ Drop files here                     â”‚      â”‚
â”‚  â”‚                                                    â”‚      â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â”‚
â”‚                                                              â”‚
â”‚  [Skip for now]                    [I've uploaded my data]  â”‚
â”‚                                                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Phase 2: Browser Extension (V2)
For users who want passive collection:
- Chrome/Firefox extension
- Captures posts as they browse their own profiles
- Optional, not required

### Phase 3: One-Click Scraper (V3)
For power users who want everything:
- Opens browser, logs them in, scrapes their history
- Full transparency (they watch it happen)
- Requires explicit consent

---

## Data We Extract From Social Media

### From Posts/Tweets
```python
{
    "platform": "twitter",
    "content": "Just shipped the new feature! Team crushed it ðŸš€",
    "timestamp": "2025-01-15T14:32:00Z",
    "engagement": {"likes": 45, "replies": 12, "reposts": 3},
    "media_type": "text",  # or "image", "video", "link"
    "is_reply": False,
    "is_repost": False
}
```

### Signals We Extract

| Signal | What It Tells Us | Example |
|--------|------------------|---------|
| **Vocabulary** | Formality level, industry jargon | "We're excited to announce" vs "omg this is huge" |
| **Emoji usage** | Expressiveness, tone | Heavy ðŸ”¥ðŸš€ = energetic |
| **Posting frequency** | Communication rhythm | Daily poster vs. occasional |
| **Time of day** | Work patterns | Posts at 7am = early riser |
| **Topics** | Interests, expertise | Talks about AI, marketing, family |
| **Hashtag style** | Marketing-savvy vs. organic | #B2BMarketing vs. no hashtags |
| **Engagement style** | How they interact | Lots of replies = conversational |
| **Tone consistency** | Professional vs. personal split | LinkedIn formal, Twitter casual |

---

## Platform-Specific Parsers

### Twitter/X Data Export Parser

```python
# profile/extractors/social/twitter_parser.py

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def parse_twitter_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse Twitter's data export ZIP file.
    
    Expected structure:
    twitter-archive/
    â”œâ”€â”€ data/
    â”‚   â”œâ”€â”€ tweets.js
    â”‚   â”œâ”€â”€ like.js
    â”‚   â”œâ”€â”€ profile.js
    â”‚   â””â”€â”€ ...
    """
    
    tweets = []
    profile = {}
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Find tweets.js
        for name in zf.namelist():
            if 'tweets.js' in name:
                content = zf.read(name).decode('utf-8')
                # Twitter wraps JSON in "window.YTD.tweets.part0 = "
                json_str = content.split(' = ', 1)[1] if ' = ' in content else content
                raw_tweets = json.loads(json_str)
                
                for item in raw_tweets:
                    tweet = item.get('tweet', item)
                    tweets.append({
                        "id": tweet.get('id_str', tweet.get('id')),
                        "content": tweet.get('full_text', tweet.get('text', '')),
                        "timestamp": _parse_twitter_date(tweet.get('created_at', '')),
                        "likes": int(tweet.get('favorite_count', 0)),
                        "retweets": int(tweet.get('retweet_count', 0)),
                        "is_reply": tweet.get('in_reply_to_user_id') is not None,
                        "is_retweet": tweet.get('full_text', '').startswith('RT @'),
                        "hashtags": [h['text'] for h in tweet.get('entities', {}).get('hashtags', [])],
                        "mentions": [m['screen_name'] for m in tweet.get('entities', {}).get('user_mentions', [])]
                    })
            
            if 'profile.js' in name:
                content = zf.read(name).decode('utf-8')
                json_str = content.split(' = ', 1)[1] if ' = ' in content else content
                profile_data = json.loads(json_str)
                if isinstance(profile_data, list) and profile_data:
                    profile = profile_data[0].get('profile', profile_data[0])
    
    # Filter to only original posts (not RTs, not replies)
    original_tweets = [t for t in tweets if not t['is_retweet'] and not t['is_reply']]
    
    return {
        "platform": "twitter",
        "profile": {
            "username": profile.get('username', 'unknown'),
            "display_name": profile.get('displayName', ''),
            "bio": profile.get('description', {}).get('bio', '')
        },
        "posts": original_tweets,
        "total_posts": len(original_tweets),
        "date_range": _get_date_range(original_tweets)
    }


def _parse_twitter_date(date_str: str) -> str:
    """Convert Twitter's date format to ISO."""
    if not date_str:
        return ""
    try:
        # Twitter format: "Sat Oct 10 20:19:24 +0000 2020"
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.isoformat()
    except:
        return date_str


def _get_date_range(posts: List[Dict]) -> Dict[str, str]:
    """Get earliest and latest post dates."""
    if not posts:
        return {"earliest": "", "latest": ""}
    
    timestamps = [p['timestamp'] for p in posts if p['timestamp']]
    if not timestamps:
        return {"earliest": "", "latest": ""}
    
    return {
        "earliest": min(timestamps),
        "latest": max(timestamps)
    }


# Test
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_twitter_export(sys.argv[1])
        print(f"Parsed {result['total_posts']} tweets from @{result['profile']['username']}")
        print(f"Date range: {result['date_range']}")
```

### LinkedIn Data Export Parser

```python
# profile/extractors/social/linkedin_parser.py

import json
import csv
import zipfile
from pathlib import Path
from typing import Dict, List, Any

def parse_linkedin_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse LinkedIn's data export ZIP file.
    
    Expected structure:
    Basic_LinkedInDataExport/
    â”œâ”€â”€ Profile.csv
    â”œâ”€â”€ Positions.csv
    â”œâ”€â”€ Skills.csv
    â”œâ”€â”€ Connections.csv
    â”œâ”€â”€ Messages.csv (if requested)
    â””â”€â”€ ...
    """
    
    profile = {}
    positions = []
    skills = []
    posts = []  # LinkedIn calls these "shares"
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            
            # Profile
            if 'Profile.csv' in name:
                content = zf.read(name).decode('utf-8')
                reader = csv.DictReader(content.splitlines())
                for row in reader:
                    profile = {
                        "first_name": row.get('First Name', ''),
                        "last_name": row.get('Last Name', ''),
                        "headline": row.get('Headline', ''),
                        "summary": row.get('Summary', ''),
                        "industry": row.get('Industry', '')
                    }
                    break  # Only one row
            
            # Work history
            if 'Positions.csv' in name:
                content = zf.read(name).decode('utf-8')
                reader = csv.DictReader(content.splitlines())
                for row in reader:
                    positions.append({
                        "company": row.get('Company Name', ''),
                        "title": row.get('Title', ''),
                        "start_date": row.get('Started On', ''),
                        "end_date": row.get('Finished On', ''),
                        "description": row.get('Description', '')
                    })
            
            # Skills
            if 'Skills.csv' in name:
                content = zf.read(name).decode('utf-8')
                reader = csv.DictReader(content.splitlines())
                for row in reader:
                    skill = row.get('Name', row.get('Skill', ''))
                    if skill:
                        skills.append(skill)
            
            # Posts/Shares (if available)
            if 'Shares.csv' in name or 'Posts.csv' in name:
                content = zf.read(name).decode('utf-8')
                reader = csv.DictReader(content.splitlines())
                for row in reader:
                    posts.append({
                        "content": row.get('ShareCommentary', row.get('Content', '')),
                        "timestamp": row.get('Date', ''),
                        "url": row.get('ShareLink', '')
                    })
    
    return {
        "platform": "linkedin",
        "profile": profile,
        "positions": positions,
        "skills": skills,
        "posts": posts,
        "total_posts": len(posts)
    }
```

### Instagram Data Export Parser

```python
# profile/extractors/social/instagram_parser.py

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any

def parse_instagram_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse Instagram's data export ZIP file.
    
    Expected structure (JSON format):
    instagram-data/
    â”œâ”€â”€ personal_information/
    â”‚   â””â”€â”€ personal_information.json
    â”œâ”€â”€ content/
    â”‚   â””â”€â”€ posts_1.json
    â”œâ”€â”€ comments/
    â”‚   â””â”€â”€ post_comments.json
    â””â”€â”€ ...
    """
    
    profile = {}
    posts = []
    comments = []
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            
            # Profile
            if 'personal_information.json' in name:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
                pi = data.get('profile_user', [{}])[0] if isinstance(data.get('profile_user'), list) else {}
                profile = {
                    "username": pi.get('username', ''),
                    "name": pi.get('name', ''),
                    "bio": pi.get('biography', '')
                }
            
            # Posts
            if 'posts_1.json' in name or 'content/posts' in name:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
                
                for post in data if isinstance(data, list) else data.get('ig_posts', []):
                    # Instagram structure can vary
                    media = post.get('media', [{}])[0] if post.get('media') else post
                    posts.append({
                        "content": media.get('title', media.get('caption', '')),
                        "timestamp": media.get('creation_timestamp', media.get('taken_at', '')),
                        "media_type": "image"  # Could parse for video
                    })
            
            # Comments they've made
            if 'post_comments.json' in name:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
                
                for comment in data if isinstance(data, list) else data.get('comments_media_comments', []):
                    comments.append({
                        "content": comment.get('string_list_data', [{}])[0].get('value', ''),
                        "timestamp": comment.get('string_list_data', [{}])[0].get('timestamp', '')
                    })
    
    return {
        "platform": "instagram",
        "profile": profile,
        "posts": posts,
        "comments": comments,
        "total_posts": len(posts),
        "total_comments": len(comments)
    }
```

### Facebook Data Export Parser

```python
# profile/extractors/social/facebook_parser.py

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any

def parse_facebook_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse Facebook's data export ZIP file.
    
    Expected structure:
    facebook-data/
    â”œâ”€â”€ profile_information/
    â”‚   â””â”€â”€ profile_information.json
    â”œâ”€â”€ posts/
    â”‚   â””â”€â”€ your_posts_1.json
    â”œâ”€â”€ comments_and_reactions/
    â”‚   â””â”€â”€ comments.json
    â””â”€â”€ ...
    """
    
    profile = {}
    posts = []
    comments = []
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            
            # Profile
            if 'profile_information.json' in name:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
                pi = data.get('profile_v2', data)
                profile = {
                    "name": pi.get('name', {}).get('full_name', ''),
                    "bio": pi.get('intro_bio', {}).get('text', ''),
                    "current_city": pi.get('current_city', {}).get('name', '')
                }
            
            # Posts
            if 'your_posts' in name and name.endswith('.json'):
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
                
                for post in data if isinstance(data, list) else []:
                    # Extract text from various possible locations
                    text = ''
                    if 'data' in post:
                        for item in post['data']:
                            if 'post' in item:
                                text = item['post']
                    
                    posts.append({
                        "content": text or post.get('title', ''),
                        "timestamp": post.get('timestamp', ''),
                        "attachments": len(post.get('attachments', []))
                    })
            
            # Comments
            if 'comments.json' in name:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
                
                for comment in data.get('comments_v2', data if isinstance(data, list) else []):
                    comments.append({
                        "content": comment.get('comment', {}).get('comment', ''),
                        "timestamp": comment.get('timestamp', '')
                    })
    
    return {
        "platform": "facebook",
        "profile": profile,
        "posts": posts,
        "comments": comments,
        "total_posts": len(posts),
        "total_comments": len(comments)
    }
```

---

## Social Media Style Extractor

```python
# profile/extractors/social_style.py

"""
Extracts communication style signals from social media data.
Works with parsed exports from any platform.
"""

import re
from collections import Counter
from typing import Dict, List, Any
from datetime import datetime

# Emoji detection pattern
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+", 
    flags=re.UNICODE
)

def extract_social_style(social_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze social media posts to extract communication style.
    
    Args:
        social_data: List of parsed platform exports, each with:
            - platform: str
            - posts: List[{content, timestamp, ...}]
    
    Returns:
        Social media communication profile
    """
    
    all_posts = []
    platform_breakdown = {}
    
    # Collect all posts across platforms
    for platform_data in social_data:
        platform = platform_data.get('platform', 'unknown')
        posts = platform_data.get('posts', [])
        
        platform_breakdown[platform] = {
            "post_count": len(posts),
            "style": _analyze_platform_posts(posts)
        }
        
        for post in posts:
            post['_platform'] = platform
            all_posts.append(post)
    
    # Cross-platform analysis
    all_content = [p.get('content', '') for p in all_posts if p.get('content')]
    
    return {
        "total_posts_analyzed": len(all_posts),
        "platforms": list(platform_breakdown.keys()),
        
        # Overall style
        "emoji_usage": _analyze_emoji_usage(all_content),
        "hashtag_style": _analyze_hashtag_style(all_content),
        "vocabulary": _analyze_vocabulary(all_content),
        "tone_markers": _analyze_tone_markers(all_content),
        "posting_patterns": _analyze_posting_patterns(all_posts),
        
        # Per-platform breakdown
        "platform_breakdown": platform_breakdown,
        
        # Topics and interests
        "topics": _extract_topics(all_content),
        
        # Formality comparison across platforms
        "formality_by_platform": _compare_formality(platform_breakdown)
    }


def _analyze_platform_posts(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze posts from a single platform."""
    if not posts:
        return {}
    
    content_list = [p.get('content', '') for p in posts if p.get('content')]
    
    # Average post length
    lengths = [len(c.split()) for c in content_list]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    
    # Emoji frequency
    emoji_count = sum(len(EMOJI_PATTERN.findall(c)) for c in content_list)
    emoji_per_post = emoji_count / len(content_list) if content_list else 0
    
    # Hashtag frequency
    hashtag_count = sum(c.count('#') for c in content_list)
    hashtags_per_post = hashtag_count / len(content_list) if content_list else 0
    
    # Question frequency (engagement style)
    question_count = sum(c.count('?') for c in content_list)
    
    return {
        "avg_post_length_words": round(avg_length, 1),
        "emoji_per_post": round(emoji_per_post, 2),
        "hashtags_per_post": round(hashtags_per_post, 2),
        "questions_asked": question_count,
        "post_count": len(content_list)
    }


def _analyze_emoji_usage(content_list: List[str]) -> Dict[str, Any]:
    """Analyze emoji patterns."""
    all_emoji = []
    posts_with_emoji = 0
    
    for content in content_list:
        emojis = EMOJI_PATTERN.findall(content)
        if emojis:
            posts_with_emoji += 1
            all_emoji.extend(emojis)
    
    emoji_freq = posts_with_emoji / len(content_list) if content_list else 0
    
    # Get most common emojis
    emoji_counter = Counter(all_emoji)
    top_emoji = [e for e, _ in emoji_counter.most_common(5)]
    
    return {
        "frequency": round(emoji_freq, 2),  # % of posts with emoji
        "style": "heavy" if emoji_freq > 0.5 else "moderate" if emoji_freq > 0.2 else "light",
        "top_emoji": top_emoji
    }


def _analyze_hashtag_style(content_list: List[str]) -> Dict[str, Any]:
    """Analyze hashtag usage patterns."""
    all_hashtags = []
    
    for content in content_list:
        hashtags = re.findall(r'#(\w+)', content)
        all_hashtags.extend([h.lower() for h in hashtags])
    
    if not all_hashtags:
        return {"usage": "none", "top_hashtags": []}
    
    hashtag_counter = Counter(all_hashtags)
    avg_per_post = len(all_hashtags) / len(content_list)
    
    return {
        "usage": "heavy" if avg_per_post > 3 else "moderate" if avg_per_post > 1 else "light",
        "avg_per_post": round(avg_per_post, 1),
        "top_hashtags": [h for h, _ in hashtag_counter.most_common(10)],
        "style": "marketing" if avg_per_post > 2 else "organic"
    }


def _analyze_vocabulary(content_list: List[str]) -> Dict[str, Any]:
    """Analyze vocabulary complexity and patterns."""
    all_words = []
    
    for content in content_list:
        # Clean and split
        clean = re.sub(r'[^\w\s]', '', content.lower())
        words = clean.split()
        all_words.extend(words)
    
    if not all_words:
        return {}
    
    # Average word length (proxy for complexity)
    avg_word_length = sum(len(w) for w in all_words) / len(all_words)
    
    # Unique words ratio (vocabulary breadth)
    unique_ratio = len(set(all_words)) / len(all_words)
    
    # Common words they use
    word_counter = Counter(all_words)
    # Filter out very common words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of', 'and', 'in', 'for', 'on', 'with', 'i', 'you', 'it', 'this', 'that'}
    signature_words = [w for w, c in word_counter.most_common(50) if w not in stop_words and len(w) > 2][:10]
    
    return {
        "complexity": "advanced" if avg_word_length > 5 else "moderate" if avg_word_length > 4 else "simple",
        "avg_word_length": round(avg_word_length, 1),
        "vocabulary_breadth": "varied" if unique_ratio > 0.4 else "focused",
        "signature_words": signature_words
    }


def _analyze_tone_markers(content_list: List[str]) -> Dict[str, Any]:
    """Detect tone indicators."""
    
    combined = ' '.join(content_list).lower()
    total_posts = len(content_list)
    
    # Excitement markers
    exclamation_posts = sum(1 for c in content_list if '!' in c)
    caps_posts = sum(1 for c in content_list if any(word.isupper() and len(word) > 2 for word in c.split()))
    
    # Hedging/uncertainty
    hedge_words = ['maybe', 'perhaps', 'might', 'could', 'possibly', 'i think', 'i guess']
    hedge_count = sum(combined.count(h) for h in hedge_words)
    
    # Confidence markers
    confidence_words = ['definitely', 'absolutely', 'clearly', 'obviously', 'certainly']
    confidence_count = sum(combined.count(c) for c in confidence_words)
    
    # Determine overall tone
    excitement_ratio = exclamation_posts / total_posts if total_posts else 0
    
    tone = "enthusiastic" if excitement_ratio > 0.4 else "measured" if excitement_ratio < 0.1 else "balanced"
    
    return {
        "overall": tone,
        "excitement_level": round(excitement_ratio, 2),
        "uses_caps_for_emphasis": caps_posts > total_posts * 0.1,
        "hedging_tendency": "high" if hedge_count > total_posts else "low",
        "confidence_markers": confidence_count
    }


def _analyze_posting_patterns(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze when and how often they post."""
    
    if not posts:
        return {}
    
    # Try to parse timestamps
    hours = []
    days = []
    
    for post in posts:
        ts = post.get('timestamp', '')
        if not ts:
            continue
        
        try:
            # Try ISO format
            if isinstance(ts, str):
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    continue
            elif isinstance(ts, (int, float)):
                dt = datetime.fromtimestamp(ts)
            else:
                continue
            
            hours.append(dt.hour)
            days.append(dt.strftime('%A'))
        except:
            continue
    
    if not hours:
        return {"time_analysis": "insufficient_data"}
    
    # Most active hours
    hour_counter = Counter(hours)
    peak_hours = [h for h, _ in hour_counter.most_common(3)]
    
    # Most active days
    day_counter = Counter(days)
    peak_days = [d for d, _ in day_counter.most_common(2)]
    
    # Determine if morning/afternoon/evening person
    morning = sum(1 for h in hours if 5 <= h < 12)
    afternoon = sum(1 for h in hours if 12 <= h < 17)
    evening = sum(1 for h in hours if 17 <= h < 22)
    
    if morning > afternoon and morning > evening:
        time_preference = "morning"
    elif evening > morning and evening > afternoon:
        time_preference = "evening"
    else:
        time_preference = "afternoon"
    
    return {
        "peak_hours": peak_hours,
        "peak_days": peak_days,
        "time_preference": time_preference,
        "posts_analyzed": len(hours)
    }


def _extract_topics(content_list: List[str]) -> List[str]:
    """Extract main topics/interests from posts."""
    
    # Simple keyword extraction (could be enhanced with NLP)
    topic_keywords = {
        "technology": ["ai", "tech", "software", "app", "startup", "coding", "data"],
        "business": ["business", "marketing", "sales", "growth", "revenue", "startup", "entrepreneur"],
        "personal": ["family", "kids", "weekend", "vacation", "birthday", "friends"],
        "professional": ["team", "project", "launch", "milestone", "hiring", "work"],
        "creative": ["design", "art", "creative", "brand", "visual", "photography"],
        "health": ["fitness", "health", "workout", "running", "meditation", "wellness"]
    }
    
    combined = ' '.join(content_list).lower()
    
    detected = []
    for topic, keywords in topic_keywords.items():
        if any(kw in combined for kw in keywords):
            detected.append(topic)
    
    return detected


def _compare_formality(platform_breakdown: Dict) -> Dict[str, str]:
    """Compare formality across platforms."""
    
    formality = {}
    
    for platform, data in platform_breakdown.items():
        style = data.get('style', {})
        avg_length = style.get('avg_post_length_words', 0)
        emoji = style.get('emoji_per_post', 0)
        
        # Rough formality heuristic
        if platform == 'linkedin':
            formality[platform] = "formal"  # LinkedIn is always more formal
        elif avg_length > 20 and emoji < 0.5:
            formality[platform] = "formal"
        elif avg_length < 10 or emoji > 1:
            formality[platform] = "casual"
        else:
            formality[platform] = "balanced"
    
    return formality


# Test
if __name__ == "__main__":
    # Test with sample data
    sample_data = [{
        "platform": "twitter",
        "posts": [
            {"content": "Just shipped the new feature! Team crushed it ðŸš€", "timestamp": "2025-01-15T14:32:00Z"},
            {"content": "Great meeting with the team today. Excited about Q2 plans!", "timestamp": "2025-01-14T10:00:00Z"},
            {"content": "Anyone else think AI is moving faster than we expected? ðŸ¤–", "timestamp": "2025-01-13T09:15:00Z"}
        ]
    }]
    
    result = extract_social_style(sample_data)
    import json
    print(json.dumps(result, indent=2))
```

---

## Integration with Profile Generator

```python
# In profile/generator.py

def generate_profile(
    writing_samples: List[str] = None,
    transcripts: List[str] = None,
    screen_captures: List[Dict] = None,
    daily_checkins: Dict = None,
    social_exports: List[str] = None  # NEW: paths to social media export ZIPs
) -> Dict[str, Any]:
    """Generate complete user profile."""
    
    profile = {}
    
    # ... existing extractors ...
    
    # Social media (if provided)
    if social_exports:
        social_data = []
        
        for export_path in social_exports:
            # Detect platform and parse
            if 'twitter' in export_path.lower():
                social_data.append(parse_twitter_export(export_path))
            elif 'linkedin' in export_path.lower():
                social_data.append(parse_linkedin_export(export_path))
            elif 'instagram' in export_path.lower():
                social_data.append(parse_instagram_export(export_path))
            elif 'facebook' in export_path.lower():
                social_data.append(parse_facebook_export(export_path))
        
        if social_data:
            profile["social_presence"] = extract_social_style(social_data)
    
    return profile
```

---

## GLM Prompt to Build This

```
Build the social media collection module for Capture Kit.

We need parsers for user data exports from:
1. Twitter/X (tweets.js format)
2. LinkedIn (CSV format)
3. Instagram (JSON format)
4. Facebook (JSON format)

Then a unified extractor that analyzes all posts to detect:
- Emoji usage patterns
- Hashtag style
- Vocabulary complexity
- Tone markers
- Posting time patterns
- Topics/interests
- Formality differences across platforms

Files to create:
1. profile/extractors/social/twitter_parser.py
2. profile/extractors/social/linkedin_parser.py
3. profile/extractors/social/instagram_parser.py
4. profile/extractors/social/facebook_parser.py
5. profile/extractors/social_style.py

Constraints:
- Handle messy/incomplete exports gracefully
- No external dependencies beyond standard library
- Each parser <150 lines
- Return consistent schema across platforms

Start with twitter_parser.py
```

---

## Privacy Notice for Users

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           ðŸ“± SOCIAL MEDIA CAPTURE                           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                              â”‚
â”‚  Adding your social media helps your AI understand          â”‚
â”‚  how you communicate publicly vs. privately.                â”‚
â”‚                                                              â”‚
â”‚  WHAT WE ANALYZE:                                           â”‚
â”‚  âœ“ Your writing style and tone                              â”‚
â”‚  âœ“ Topics you talk about                                    â”‚
â”‚  âœ“ When you're most active                                  â”‚
â”‚  âœ“ How formal vs. casual you are                           â”‚
â”‚                                                              â”‚
â”‚  WHAT WE DON'T DO:                                          â”‚
â”‚  âœ— Contact your followers                                   â”‚
â”‚  âœ— Post anything on your behalf                            â”‚
â”‚  âœ— Store your login credentials                            â”‚
â”‚  âœ— Access private/DM messages                               â”‚
â”‚                                                              â”‚
â”‚  Your data stays on your device.                            â”‚
â”‚                                                              â”‚
â”‚  [Skip This]                          [Add Social Data]     â”‚
â”‚                                                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```
