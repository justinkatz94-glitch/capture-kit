"""
FinTwit Scanner - Find trending posts in finance/trading Twitter

Scans known finance accounts and surfaces high-engagement posts.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import Counter

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from social.twitter_public_scraper import fetch_twitter_profile


class FinTwitScanner:
    """
    Scanner for finding trending posts in finance Twitter.
    """

    # Finance/trading accounts to monitor
    DEFAULT_ACCOUNTS = [
        "unusual_whales",
        "bluedeerc",
        "OptionsHawk",
        "SqueezeMetrics",
        "spotgamma",
        "TradingTalent",
        "jam_croissant",
        "peraborsa",
        "Ksidiii",
        "GVol_Alert",
    ]

    # Keywords for filtering relevant posts
    FILTER_KEYWORDS = {
        "options": [
            "options", "calls", "puts", "premium", "IV", "implied volatility",
            "gamma", "delta", "theta", "vega", "strike", "expiry", "expiration",
            "OTM", "ITM", "ATM", "spread", "straddle", "strangle", "iron condor",
            "0DTE", "weeklies", "monthlies", "LEAPs", "contract"
        ],
        "dealer_positioning": [
            "dealer", "positioning", "GEX", "gamma exposure", "DIX", "GIX",
            "dark pool", "flow", "hedging", "market maker", "MM", "pin",
            "max pain", "OI", "open interest", "volume", "sweep", "block",
            "unusual", "activity", "whale", "smart money"
        ],
        "market_structure": [
            "market structure", "support", "resistance", "breakout", "breakdown",
            "liquidity", "bid", "ask", "spread", "depth", "order book",
            "supply", "demand", "trend", "reversal", "consolidation",
            "level", "zone", "area", "price action"
        ],
        "general_trading": [
            "SPX", "SPY", "QQQ", "ES", "NQ", "VIX", "UVXY", "SVXY",
            "bull", "bear", "long", "short", "entry", "exit", "target",
            "stop", "risk", "reward", "trade", "position", "exposure",
            "market", "stock", "price", "move", "rally", "sell", "buy",
            "$", "profit", "loss", "gain", "drop", "rip", "dump",
            "earnings", "Fed", "FOMC", "CPI", "jobs", "data"
        ]
    }

    def __init__(self, accounts: List[str] = None, hours_back: int = 48, include_all_time: bool = True):
        """
        Initialize scanner.

        Args:
            accounts: List of Twitter accounts to monitor
            hours_back: How many hours back to look for posts (ignored if include_all_time=True)
            include_all_time: If True, include high-engagement posts regardless of time
        """
        self.accounts = accounts or self.DEFAULT_ACCOUNTS
        self.hours_back = hours_back
        self.include_all_time = include_all_time  # Include popular posts regardless of time
        self.posts_cache: Dict[str, List[Dict]] = {}
        self.scan_results: List[Dict] = []

    def scan(self, max_posts_per_account: int = 50) -> List[Dict[str, Any]]:
        """
        Scan accounts for trending posts.

        Args:
            max_posts_per_account: Max posts to fetch per account

        Returns:
            List of trending posts sorted by engagement
        """
        all_posts = []
        cutoff_time = datetime.now() - timedelta(hours=self.hours_back)

        print(f"Scanning {len(self.accounts)} accounts for posts from last {self.hours_back} hours...")
        print()

        for account in self.accounts:
            print(f"  Fetching @{account}...", end=" ")

            try:
                profile_data = fetch_twitter_profile(account, max_posts_per_account)

                if "error" in profile_data:
                    print(f"[SKIP] {profile_data['error']}")
                    continue

                posts = profile_data.get("posts", [])
                profile = profile_data.get("profile", {})
                followers = self._parse_followers(profile.get("followers", 0))

                # Filter and process posts
                relevant_posts = []
                for post in posts:
                    # Parse timestamp
                    timestamp = self._parse_timestamp(post.get("timestamp"))

                    # Skip old posts unless include_all_time is set
                    if not self.include_all_time and timestamp and timestamp < cutoff_time:
                        continue

                    # Calculate engagement
                    likes = self._parse_metric(post.get("likes", 0))
                    retweets = self._parse_metric(post.get("retweets", 0))
                    replies = self._parse_metric(post.get("replies", 0))
                    total_engagement = likes + retweets + replies

                    # Check relevance
                    content = post.get("content", "")
                    categories = self._categorize_post(content)

                    if not categories:
                        continue  # Skip non-relevant posts

                    # Calculate engagement rate
                    engagement_rate = (total_engagement / followers * 100) if followers > 0 else 0

                    relevant_posts.append({
                        "author": account,
                        "author_followers": followers,
                        "content": content,
                        "timestamp": timestamp.isoformat() if timestamp else None,
                        "timestamp_display": self._format_time_ago(timestamp) if timestamp else "unknown",
                        "likes": likes,
                        "retweets": retweets,
                        "replies": replies,
                        "total_engagement": total_engagement,
                        "engagement_rate": round(engagement_rate, 4),
                        "categories": categories,
                        "url": f"https://x.com/{account}/status/{post.get('id', '')}" if post.get('id') else None,
                        "id": post.get("id"),
                    })

                all_posts.extend(relevant_posts)
                print(f"[OK] {len(relevant_posts)} relevant posts")

            except Exception as e:
                print(f"[ERROR] {str(e)[:50]}")

        # Sort by engagement score (weighted)
        all_posts.sort(key=lambda p: self._calculate_trending_score(p), reverse=True)

        self.scan_results = all_posts
        return all_posts

    def _parse_followers(self, value) -> int:
        """Parse follower count."""
        return self._parse_metric(value)

    def _parse_metric(self, value) -> int:
        """Parse engagement metric."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            value = value.strip().upper().replace(",", "")
            if not value or value == "0":
                return 0
            multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            for suffix, mult in multipliers.items():
                if value.endswith(suffix):
                    try:
                        return int(float(value[:-1]) * mult)
                    except:
                        return 0
            try:
                return int(float(value))
            except:
                return 0
        return 0

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime."""
        if not timestamp_str:
            return None

        # Try various formats
        formats = [
            "%a %b %d %H:%M:%S %z %Y",  # Twitter format: "Thu Jan 15 11:00:00 +0000 2026"
            "%Y-%m-%dT%H:%M:%S.%fZ",     # ISO format
            "%Y-%m-%dT%H:%M:%SZ",         # ISO format without microseconds
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                # Convert to naive datetime for comparison
                if dt.tzinfo:
                    dt = dt.replace(tzinfo=None)
                return dt
            except:
                continue

        return None

    def _format_time_ago(self, dt: datetime) -> str:
        """Format datetime as relative time."""
        if not dt:
            return "unknown"

        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"

    def _categorize_post(self, content: str) -> List[str]:
        """Categorize post by topic keywords."""
        content_lower = content.lower()
        categories = []

        for category, keywords in self.FILTER_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    if category not in categories:
                        categories.append(category)
                    break

        return categories

    def _calculate_trending_score(self, post: Dict) -> float:
        """
        Calculate trending score for ranking.

        Factors:
        - Engagement rate (weighted heavily)
        - Total engagement
        - Recency
        """
        engagement_rate = post.get("engagement_rate", 0)
        total_engagement = post.get("total_engagement", 0)

        # Recency bonus
        timestamp = self._parse_timestamp(post.get("timestamp")) if isinstance(post.get("timestamp"), str) else None
        if timestamp:
            hours_ago = (datetime.now() - timestamp).total_seconds() / 3600
            recency_multiplier = max(0.5, 1 - (hours_ago / 48))  # Decay over 48 hours
        else:
            recency_multiplier = 0.5

        # Score formula
        score = (
            (engagement_rate * 1000) +  # Engagement rate is most important
            (total_engagement * 0.1) +   # Raw engagement
            (recency_multiplier * 100)   # Recency boost
        )

        return score

    def get_top_posts(self, n: int = 10, category: str = None) -> List[Dict]:
        """Get top N trending posts, optionally filtered by category."""
        posts = self.scan_results

        if category:
            posts = [p for p in posts if category in p.get("categories", [])]

        return posts[:n]

    def get_reply_opportunities(self, min_engagement: int = 100, max_replies: int = 50) -> List[Dict]:
        """
        Find posts that are good reply opportunities.

        Good opportunities:
        - High engagement (post is getting attention)
        - Moderate reply count (not overcrowded)
        - Recent (still in active discussion)
        """
        opportunities = []

        for post in self.scan_results:
            if post.get("total_engagement", 0) < min_engagement:
                continue
            if post.get("replies", 0) > max_replies:
                continue

            # Score opportunity
            opportunity_score = (
                post.get("engagement_rate", 0) * 10 +
                min(post.get("total_engagement", 0) / 100, 50) -
                post.get("replies", 0) * 0.5  # Fewer replies = better opportunity
            )

            post_copy = post.copy()
            post_copy["opportunity_score"] = round(opportunity_score, 2)
            opportunities.append(post_copy)

        opportunities.sort(key=lambda p: p.get("opportunity_score", 0), reverse=True)
        return opportunities

    def format_results(self, posts: List[Dict] = None, limit: int = 10) -> str:
        """Format posts for display."""
        posts = posts or self.scan_results[:limit]

        lines = []
        lines.append("=" * 70)
        lines.append("FINTWIT TRENDING POSTS")
        lines.append("=" * 70)

        for i, post in enumerate(posts[:limit], 1):
            lines.append(f"\n#{i} @{post.get('author')} • {post.get('timestamp_display', 'unknown')}")
            lines.append(f"   {post.get('likes', 0):,} likes • {post.get('retweets', 0):,} RTs • {post.get('replies', 0):,} replies")
            lines.append(f"   Categories: {', '.join(post.get('categories', []))}")
            lines.append(f"   Engagement rate: {post.get('engagement_rate', 0):.2f}%")
            lines.append("")

            # Truncate content
            content = post.get("content", "")
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"   \"{content}\"")

            if post.get("url"):
                lines.append(f"   {post.get('url')}")

        return "\n".join(lines)


def scan_fintwit(
    accounts: List[str] = None,
    hours_back: int = 48,
    category: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Quick function to scan FinTwit.

    Args:
        accounts: Accounts to scan (uses defaults if None)
        hours_back: Hours to look back
        category: Filter by category (options, dealer_positioning, market_structure)
        limit: Max posts to return

    Returns:
        Scan results with trending posts
    """
    scanner = FinTwitScanner(accounts=accounts, hours_back=hours_back)
    scanner.scan()

    posts = scanner.get_top_posts(n=limit, category=category)
    opportunities = scanner.get_reply_opportunities()[:5]

    return {
        "scan_time": datetime.now().isoformat(),
        "accounts_scanned": len(scanner.accounts),
        "total_posts_found": len(scanner.scan_results),
        "trending_posts": posts,
        "reply_opportunities": opportunities,
        "categories_found": _aggregate_categories(scanner.scan_results),
    }


def get_daily_brief(accounts: List[str] = None) -> str:
    """
    Get a formatted daily brief of FinTwit activity.

    Returns:
        Formatted string with daily brief
    """
    scanner = FinTwitScanner(accounts=accounts, hours_back=24)
    scanner.scan()

    lines = []
    lines.append("=" * 70)
    lines.append(f"FINTWIT DAILY BRIEF - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    # Summary stats
    total_posts = len(scanner.scan_results)
    categories = _aggregate_categories(scanner.scan_results)

    lines.append(f"\nTotal relevant posts: {total_posts}")
    lines.append(f"Categories: {categories}")

    # Top trending
    lines.append("\n" + "-" * 40)
    lines.append("TOP TRENDING POSTS")
    lines.append("-" * 40)

    for i, post in enumerate(scanner.get_top_posts(5), 1):
        lines.append(f"\n{i}. @{post.get('author')} ({post.get('timestamp_display')})")
        content = post.get("content", "")[:150]
        lines.append(f"   \"{content}...\"" if len(post.get("content", "")) > 150 else f"   \"{content}\"")
        lines.append(f"   Engagement: {post.get('total_engagement', 0):,} ({post.get('engagement_rate', 0):.2f}%)")

    # Reply opportunities
    opportunities = scanner.get_reply_opportunities()[:5]
    if opportunities:
        lines.append("\n" + "-" * 40)
        lines.append("REPLY OPPORTUNITIES")
        lines.append("-" * 40)

        for i, post in enumerate(opportunities, 1):
            lines.append(f"\n{i}. @{post.get('author')} - {post.get('replies', 0)} replies (opportunity score: {post.get('opportunity_score', 0)})")
            content = post.get("content", "")[:100]
            lines.append(f"   \"{content}...\"")
            if post.get("url"):
                lines.append(f"   {post.get('url')}")

    # Category breakdown
    lines.append("\n" + "-" * 40)
    lines.append("BY CATEGORY")
    lines.append("-" * 40)

    for category in ["options", "dealer_positioning", "market_structure"]:
        cat_posts = scanner.get_top_posts(3, category=category)
        if cat_posts:
            lines.append(f"\n{category.upper().replace('_', ' ')}: {len([p for p in scanner.scan_results if category in p.get('categories', [])])} posts")
            for post in cat_posts[:2]:
                lines.append(f"  • @{post.get('author')}: \"{post.get('content', '')[:80]}...\"")

    return "\n".join(lines)


def _aggregate_categories(posts: List[Dict]) -> Dict[str, int]:
    """Count posts per category."""
    counter = Counter()
    for post in posts:
        for cat in post.get("categories", []):
            counter[cat] += 1
    return dict(counter)


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FinTwit Scanner")
    parser.add_argument("--hours", type=int, default=48, help="Hours to look back")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--limit", type=int, default=10, help="Max posts to show")
    parser.add_argument("--brief", action="store_true", help="Show daily brief")
    parser.add_argument("--opportunities", action="store_true", help="Show reply opportunities")

    args = parser.parse_args()

    if args.brief:
        print(get_daily_brief())
    else:
        scanner = FinTwitScanner(hours_back=args.hours)
        scanner.scan()

        if args.opportunities:
            opps = scanner.get_reply_opportunities()
            print("\nREPLY OPPORTUNITIES:")
            for i, opp in enumerate(opps[:10], 1):
                print(f"\n{i}. @{opp.get('author')} (score: {opp.get('opportunity_score')})")
                print(f"   {opp.get('content', '')[:100]}...")
                print(f"   {opp.get('url')}")
        else:
            posts = scanner.get_top_posts(args.limit, args.category)
            print(scanner.format_results(posts, args.limit))
