#!/usr/bin/env python3
"""
Capture Kit Benchmark CLI

Commands:
    analyze top account @username for benchmark <name>
    add viral post <url> to benchmark <name>
    compare profile @username to benchmark <name>
    show benchmark <name>
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

from benchmarks.benchmark_manager import BenchmarkManager, analyze_viral_post
from social.twitter_public_scraper import fetch_twitter_profile
from social.style_extractor import extract_social_style


def analyze_account(username: str, benchmark_name: str, max_posts: int = 100):
    """Analyze a top account and add to benchmark."""
    username = username.lstrip('@')
    print(f"\n{'='*60}")
    print(f"ANALYZING @{username} FOR BENCHMARK: {benchmark_name}")
    print(f"{'='*60}\n")

    # Fetch profile
    print(f"Fetching profile for @{username}...")
    profile_data = fetch_twitter_profile(username, max_posts)

    if "error" in profile_data:
        print(f"Error: {profile_data['error']}")
        return None

    posts = profile_data.get("posts", [])
    profile = profile_data.get("profile", {})

    print(f"  Name: {profile.get('name', 'N/A')}")
    print(f"  Followers: {profile.get('followers', 'N/A'):,}")
    print(f"  Posts fetched: {len(posts)}")

    # Analyze style
    print("\nAnalyzing communication style...")
    platform_data = [{
        "platform": "twitter",
        "posts": posts,
        "profile": profile
    }]
    analysis = extract_social_style(platform_data)

    print(f"  Vocabulary: {analysis.get('vocabulary', {}).get('level', 'N/A')}")
    print(f"  Tone: {analysis.get('tone', {}).get('energy', 'N/A')}")
    print(f"  Emoji style: {analysis.get('emoji_usage', {}).get('style', 'N/A')}")
    print(f"  Posting preference: {analysis.get('posting_patterns', {}).get('time_preference', 'N/A')}")

    # Add to benchmark
    print(f"\nAdding to benchmark '{benchmark_name}'...")
    manager = BenchmarkManager(benchmark_name)
    result = manager.add_top_account(profile_data, analysis)

    print(f"\n  Status: {result.get('status')}")
    print(f"  Action: {result.get('action')}")
    print(f"  Posts analyzed: {result.get('posts_analyzed')}")

    # Show updated benchmark stats
    summary = manager.get_summary()
    print(f"\nBenchmark now has {summary['total_accounts']} accounts")

    return result


def add_viral_post(post_url: str, benchmark_name: str, notes: str = None):
    """Add a viral post to the benchmark."""
    print(f"\n{'='*60}")
    print(f"ADDING VIRAL POST TO BENCHMARK: {benchmark_name}")
    print(f"{'='*60}\n")

    # Extract tweet ID from URL
    match = re.search(r'/status/(\d+)', post_url)
    if not match:
        print("Error: Could not extract tweet ID from URL")
        return None

    tweet_id = match.group(1)
    print(f"Tweet ID: {tweet_id}")

    # For now, we'll need to manually provide post data
    # since fetching individual tweets requires auth
    print("\nNote: Individual tweet fetching requires authentication.")
    print("Please provide the post details manually.\n")

    # Create a basic post entry
    post_data = {
        "url": post_url,
        "id": tweet_id,
        "content": input("Paste the tweet content: ").strip(),
        "likes": int(input("Number of likes: ") or "0"),
        "retweets": int(input("Number of retweets: ") or "0"),
        "replies": int(input("Number of replies: ") or "0"),
        "author": input("Author username: ").strip() or "unknown"
    }

    if notes is None:
        notes = input("Why do you think this post went viral? ").strip()

    manager = BenchmarkManager(benchmark_name)
    result = manager.add_viral_post(post_data, notes)

    print(f"\nPost added successfully!")
    print(f"Total engagement: {result.get('total_engagement'):,}")
    print(f"\nAnalysis:")
    analysis = result.get('analysis', {})
    print(f"  Word count: {analysis.get('word_count')}")
    print(f"  Structure: {analysis.get('structure')}")
    print(f"  Success factors: {analysis.get('success_factors')}")
    print(f"  Emotional triggers: {analysis.get('emotional_triggers')}")

    return result


def compare_profile(username: str, benchmark_name: str, max_posts: int = 100):
    """Compare a profile to a benchmark."""
    username = username.lstrip('@')
    print(f"\n{'='*60}")
    print(f"COMPARING @{username} TO BENCHMARK: {benchmark_name}")
    print(f"{'='*60}\n")

    # Load benchmark
    manager = BenchmarkManager(benchmark_name)
    if not manager.data.get("top_accounts"):
        print(f"Error: Benchmark '{benchmark_name}' has no accounts to compare against.")
        return None

    # Fetch profile
    print(f"Fetching your profile @{username}...")
    profile_data = fetch_twitter_profile(username, max_posts)

    if "error" in profile_data:
        print(f"Error: {profile_data['error']}")
        return None

    posts = profile_data.get("posts", [])
    profile = profile_data.get("profile", {})

    print(f"  Name: {profile.get('name', 'N/A')}")
    print(f"  Followers: {profile.get('followers', 'N/A'):,}")
    print(f"  Posts analyzed: {len(posts)}")

    # Analyze style
    print("\nAnalyzing your communication style...")
    platform_data = [{
        "platform": "twitter",
        "posts": posts,
        "profile": profile
    }]
    analysis = extract_social_style(platform_data)

    # Compare
    print("\nComparing to benchmark...")
    comparison = manager.compare_profile(profile_data, analysis)

    # Display results
    print(f"\n{'='*60}")
    print("COMPARISON RESULTS")
    print(f"{'='*60}")

    summary = comparison.get("summary", {})
    print(f"\nAlignment Score: {summary.get('alignment_score', 'N/A')}")
    print(f"Gaps Found: {summary.get('gaps_found', 0)}")
    print(f"High Priority Issues: {summary.get('high_priority_gaps', 0)}")
    print(f"Strengths: {summary.get('strengths', 0)}")

    # Strengths
    if comparison.get("strengths"):
        print(f"\n--- YOUR STRENGTHS ---")
        for s in comparison["strengths"]:
            print(f"  + {s}")

    # Gaps
    if comparison.get("gaps"):
        print(f"\n--- GAPS TO ADDRESS ---")
        for gap in comparison["gaps"]:
            priority_icon = {"high": "!!!", "medium": "!!", "low": "!"}.get(gap.get("priority"), "")
            print(f"\n  [{priority_icon}] {gap.get('area').upper()}")
            print(f"      Issue: {gap.get('issue')}")
            print(f"      Yours: {gap.get('yours')}")
            print(f"      Benchmark: {gap.get('benchmark')}")

    # Recommendations
    if comparison.get("recommendations"):
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}")
        for i, rec in enumerate(comparison["recommendations"], 1):
            priority = rec.get("priority", "medium")
            print(f"\n{i}. [{priority.upper()}] {rec.get('area')}")
            print(f"   Action: {rec.get('action')}")
            print(f"   Why: {rec.get('why')}")
            if rec.get("examples"):
                print(f"   Examples:")
                for ex in rec["examples"][:2]:
                    print(f"     - \"{ex[:80]}...\"" if len(ex) > 80 else f"     - \"{ex}\"")

    # Detailed comparison
    print(f"\n{'='*60}")
    print("DETAILED COMPARISON")
    print(f"{'='*60}")
    detailed = comparison.get("detailed_comparison", {})

    for area, data in detailed.items():
        print(f"\n{area.replace('_', ' ').title()}:")
        if isinstance(data, dict):
            for k, v in data.items():
                if k != "verdict":
                    print(f"  {k}: {v}")

    return comparison


def show_benchmark(benchmark_name: str):
    """Show benchmark summary and stats."""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {benchmark_name}")
    print(f"{'='*60}\n")

    manager = BenchmarkManager(benchmark_name)
    summary = manager.get_summary()

    print(f"Total Accounts: {summary.get('total_accounts', 0)}")
    print(f"Total Viral Posts: {summary.get('total_viral_posts', 0)}")
    print(f"Last Updated: {summary.get('updated_at', 'N/A')}")

    if summary.get("accounts"):
        print(f"\n--- TOP ACCOUNTS ---")
        for acc in summary["accounts"]:
            followers = acc.get("followers", 0)
            if isinstance(followers, int):
                followers_str = f"{followers:,}"
            else:
                followers_str = str(followers)
            print(f"  @{acc.get('username')}: {followers_str} followers, {acc.get('engagement_rate', 0):.2f}% engagement")

    if summary.get("patterns"):
        patterns = summary["patterns"]
        print(f"\n--- DISCOVERED PATTERNS ---")

        if patterns.get("optimal_length"):
            length = patterns["optimal_length"]
            print(f"  Optimal post length: {length.get('avg', 0):.0f} words (range: {length.get('min', 0):.0f}-{length.get('max', 0):.0f})")

        if patterns.get("best_timing"):
            timing = patterns["best_timing"]
            print(f"  Best posting hours: {timing.get('peak_hours', [])}")
            print(f"  Best posting days: {timing.get('peak_days', [])}")

        if patterns.get("top_topics"):
            print(f"  Top topics: {patterns['top_topics'][:5]}")

        if patterns.get("common_styles"):
            styles = patterns["common_styles"]
            print(f"  Common vocabulary: {styles.get('vocabulary')}")
            print(f"  Common tone: {styles.get('tone')}")
            print(f"  Emoji usage: {styles.get('emoji')}")

        if patterns.get("hooks"):
            print(f"\n--- EFFECTIVE HOOKS ---")
            for hook in patterns["hooks"][:3]:
                print(f"  {hook.get('type')}: {hook.get('count')} occurrences")
                for ex in hook.get("examples", [])[:1]:
                    print(f"    Example: \"{ex[:70]}...\"" if len(ex) > 70 else f"    Example: \"{ex}\"")

    if summary.get("aggregated_metrics"):
        metrics = summary["aggregated_metrics"]
        print(f"\n--- AGGREGATE METRICS ---")
        print(f"  Avg engagement rate: {metrics.get('avg_engagement_rate', 0):.2f}%")
        print(f"  Avg followers: {metrics.get('avg_followers', 0):,.0f}")


def main():
    parser = argparse.ArgumentParser(
        description="Capture Kit Benchmark CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_cli.py analyze @unusual_whales -b finance_twitter
  python benchmark_cli.py compare @myusername -b finance_twitter
  python benchmark_cli.py show finance_twitter
  python benchmark_cli.py add-viral "https://twitter.com/x/status/123" -b finance_twitter
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a top account for benchmark")
    analyze_parser.add_argument("username", help="Twitter username (with or without @)")
    analyze_parser.add_argument("-b", "--benchmark", required=True, help="Benchmark name")
    analyze_parser.add_argument("-n", "--max-posts", type=int, default=100, help="Max posts to fetch")

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare your profile to benchmark")
    compare_parser.add_argument("username", help="Your Twitter username")
    compare_parser.add_argument("-b", "--benchmark", required=True, help="Benchmark name")
    compare_parser.add_argument("-n", "--max-posts", type=int, default=100, help="Max posts to fetch")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show benchmark summary")
    show_parser.add_argument("benchmark", help="Benchmark name")

    # Add viral post command
    viral_parser = subparsers.add_parser("add-viral", help="Add a viral post to benchmark")
    viral_parser.add_argument("url", help="Tweet URL")
    viral_parser.add_argument("-b", "--benchmark", required=True, help="Benchmark name")
    viral_parser.add_argument("--notes", help="Notes on why it went viral")

    args = parser.parse_args()

    if args.command == "analyze":
        analyze_account(args.username, args.benchmark, args.max_posts)

    elif args.command == "compare":
        compare_profile(args.username, args.benchmark, args.max_posts)

    elif args.command == "show":
        show_benchmark(args.benchmark)

    elif args.command == "add-viral":
        add_viral_post(args.url, args.benchmark, args.notes)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
