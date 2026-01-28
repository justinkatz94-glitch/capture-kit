"""
Twitter Public Profile Scraper

Uses Twitter's syndication API (designed for embeds) to fetch public profile data.
No authentication required.

Note: This has limitations - Twitter may rate limit or block requests.
For best results, use official Twitter data exports.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def fetch_twitter_profile(username: str, max_tweets: int = 50) -> Dict[str, Any]:
    """
    Fetch a Twitter profile using public APIs.

    Args:
        username: Twitter username (with or without @)
        max_tweets: Maximum tweets to fetch (limited by API)

    Returns:
        Dict with profile info and tweets, or error
    """
    username = username.lstrip('@')

    # Try syndication timeline API first
    result = _fetch_via_syndication(username)

    if "error" not in result:
        return result

    # If that fails, try timeline API
    return {"error": f"Could not fetch profile for @{username}. Twitter may be blocking requests."}


def _fetch_via_syndication(username: str) -> Dict[str, Any]:
    """Fetch using Twitter's syndication API (used for embeds)."""

    # Twitter syndication API endpoint
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        request = Request(url, headers=headers)
        response = urlopen(request, timeout=15)
        html = response.read().decode('utf-8')

        # Extract the embedded data from the HTML response
        return _parse_syndication_html(html, username)

    except HTTPError as e:
        if e.code == 404:
            return {"error": f"User @{username} not found"}
        return {"error": f"HTTP error {e.code}: {e.reason}"}
    except URLError as e:
        return {"error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"error": f"Failed to fetch: {str(e)}"}


def _parse_syndication_html(html: str, username: str) -> Dict[str, Any]:
    """Parse the syndication HTML response to extract tweets."""

    tweets = []
    profile = {"username": username}

    # Look for the __NEXT_DATA__ script which contains JSON
    data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)

    if data_match:
        try:
            data = json.loads(data_match.group(1))

            # Navigate to the timeline data
            props = data.get('props', {}).get('pageProps', {})
            timeline = props.get('timeline', {}).get('entries', [])

            for entry in timeline:
                content = entry.get('content', {})
                tweet = content.get('tweet', {})

                if tweet:
                    tweet_data = {
                        "id": tweet.get('id_str', ''),
                        "content": tweet.get('text', ''),
                        "timestamp": tweet.get('created_at', ''),
                        "likes": tweet.get('favorite_count', 0),
                        "retweets": tweet.get('retweet_count', 0),
                        "replies": tweet.get('reply_count', 0),
                    }

                    # Get user info from first tweet
                    if not profile.get('name') and tweet.get('user'):
                        user = tweet['user']
                        profile.update({
                            "name": user.get('name', ''),
                            "bio": user.get('description', ''),
                            "followers": user.get('followers_count', 0),
                            "following": user.get('friends_count', 0),
                            "tweets_count": user.get('statuses_count', 0),
                            "profile_image": user.get('profile_image_url_https', ''),
                        })

                    tweets.append(tweet_data)

        except json.JSONDecodeError:
            pass

    # Fallback: try to extract tweets from HTML directly
    if not tweets:
        tweets = _extract_tweets_from_html(html)

    if not tweets:
        return {"error": "No tweets found. Profile may be private or empty."}

    return {
        "platform": "twitter",
        "username": username,
        "profile": profile,
        "posts": tweets,
        "total_posts": len(tweets),
        "scraped_at": datetime.now().isoformat(),
        "source": "syndication_api"
    }


def _extract_tweets_from_html(html: str) -> List[Dict]:
    """Fallback: extract tweets from HTML using regex."""
    tweets = []

    # Look for tweet text in the HTML
    # This is fragile but can work as a fallback
    tweet_pattern = re.compile(
        r'data-tweet-id="(\d+)".*?'
        r'<p class="[^"]*tweet-text[^"]*"[^>]*>(.+?)</p>',
        re.DOTALL
    )

    for match in tweet_pattern.finditer(html):
        tweet_id, content = match.groups()
        # Clean HTML from content
        content = re.sub(r'<[^>]+>', '', content)
        content = content.strip()

        if content:
            tweets.append({
                "id": tweet_id,
                "content": content,
                "timestamp": None,
                "likes": 0,
                "retweets": 0,
                "replies": 0,
            })

    return tweets


def analyze_twitter_profile(username: str) -> Dict[str, Any]:
    """
    Fetch and analyze a Twitter profile.

    Args:
        username: Twitter username

    Returns:
        Analysis results including style extraction
    """
    from .style_extractor import extract_social_style

    data = fetch_twitter_profile(username)

    if "error" in data:
        return data

    # Run style analysis
    platform_data = [{
        "platform": "twitter",
        "posts": data.get("posts", []),
        "profile": data.get("profile", {})
    }]

    analysis = extract_social_style(platform_data)
    analysis["profile"] = data.get("profile", {})
    analysis["total_posts"] = data.get("total_posts", 0)

    return analysis


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python twitter_public_scraper.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    print(f"Fetching @{username}...")

    result = fetch_twitter_profile(username)
    print(json.dumps(result, indent=2, default=str))
