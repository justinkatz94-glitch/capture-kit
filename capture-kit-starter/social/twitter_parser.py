"""
Twitter Data Export Parser
Parses Twitter's official data export ZIP file.
"""

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
    ├── data/
    │   ├── tweets.js
    │   ├── like.js
    │   ├── profile.js
    │   └── ...
    """

    path = Path(zip_path)
    if not path.exists():
        return {"error": f"File not found: {zip_path}"}

    tweets = []
    profile = {}

    try:
        # Handle both ZIP files and extracted folders
        if path.is_file() and path.suffix == '.zip':
            tweets, profile = _parse_zip(path)
        elif path.is_dir():
            tweets, profile = _parse_folder(path)
        else:
            return {"error": f"Unsupported file type: {path}"}

    except Exception as e:
        return {"error": f"Failed to parse Twitter export: {str(e)}"}

    # Filter to only original posts (not RTs, not replies)
    original_tweets = [t for t in tweets if not t['is_retweet'] and not t['is_reply']]

    return {
        "platform": "twitter",
        "profile": {
            "username": profile.get('username', 'unknown'),
            "display_name": profile.get('displayName', ''),
            "bio": profile.get('description', {}).get('bio', '') if isinstance(profile.get('description'), dict) else profile.get('description', '')
        },
        "posts": original_tweets,
        "total_posts": len(original_tweets),
        "date_range": _get_date_range(original_tweets)
    }


def _parse_zip(zip_path: Path) -> tuple:
    """Parse a ZIP file."""
    tweets = []
    profile = {}

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            if 'tweets.js' in name:
                content = zf.read(name).decode('utf-8')
                tweets = _parse_tweets_js(content)

            if 'profile.js' in name:
                content = zf.read(name).decode('utf-8')
                profile = _parse_profile_js(content)

    return tweets, profile


def _parse_folder(folder_path: Path) -> tuple:
    """Parse an extracted folder."""
    tweets = []
    profile = {}

    # Look for tweets.js
    for tweets_file in folder_path.rglob('tweets.js'):
        content = tweets_file.read_text(encoding='utf-8')
        tweets = _parse_tweets_js(content)
        break

    # Look for profile.js
    for profile_file in folder_path.rglob('profile.js'):
        content = profile_file.read_text(encoding='utf-8')
        profile = _parse_profile_js(content)
        break

    return tweets, profile


def _parse_tweets_js(content: str) -> List[Dict]:
    """Parse tweets.js content."""
    # Twitter wraps JSON in "window.YTD.tweets.part0 = "
    json_str = content.split(' = ', 1)[1] if ' = ' in content else content

    try:
        raw_tweets = json.loads(json_str)
    except json.JSONDecodeError:
        return []

    tweets = []
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

    return tweets


def _parse_profile_js(content: str) -> Dict:
    """Parse profile.js content."""
    json_str = content.split(' = ', 1)[1] if ' = ' in content else content

    try:
        profile_data = json.loads(json_str)
    except json.JSONDecodeError:
        return {}

    if isinstance(profile_data, list) and profile_data:
        return profile_data[0].get('profile', profile_data[0])

    return profile_data if isinstance(profile_data, dict) else {}


def _parse_twitter_date(date_str: str) -> str:
    """Convert Twitter's date format to ISO."""
    if not date_str:
        return ""

    try:
        # Twitter format: "Sat Oct 10 20:19:24 +0000 2020"
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.isoformat()
    except ValueError:
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_twitter_export(sys.argv[1])
        print(f"Parsed {result['total_posts']} tweets from @{result['profile']['username']}")
        print(f"Date range: {result['date_range']}")
