#!/usr/bin/env python3
"""
FinTwit Engagement CLI

Commands:
    scan fintwit         - Find trending posts in finance Twitter
    draft replies        - Generate reply options in your voice
    daily brief          - Get daily engagement brief

Examples:
    python fintwit_cli.py scan
    python fintwit_cli.py scan --category options --hours 24
    python fintwit_cli.py draft --content "Gamma flip incoming..."
    python fintwit_cli.py brief
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Ensure imports work
sys.path.insert(0, str(Path(__file__).parent))

from engagement.scanner import FinTwitScanner, scan_fintwit, get_daily_brief
from engagement.reply_generator import ReplyGenerator, draft_replies
from engagement.scoring import score_reply, analyze_reply_quality


def cmd_scan(args):
    """Scan FinTwit for trending posts."""
    print("\n" + "=" * 70)
    print("FINTWIT SCANNER")
    print("=" * 70)

    # Custom accounts if provided
    accounts = None
    if args.accounts:
        accounts = [a.strip().lstrip('@') for a in args.accounts.split(',')]

    scanner = FinTwitScanner(accounts=accounts, hours_back=args.hours)
    scanner.scan()

    # Filter by category if specified
    posts = scanner.get_top_posts(args.limit, category=args.category)

    if not posts:
        print("\nNo relevant posts found. Try expanding the time range or accounts.")
        return

    print(f"\nFound {len(scanner.scan_results)} relevant posts from {len(scanner.accounts)} accounts")
    print(f"Showing top {len(posts)} by engagement")

    if args.category:
        print(f"Filtered by: {args.category}")

    print("\n" + "-" * 70)

    for i, post in enumerate(posts, 1):
        print(f"\n#{i} @{post.get('author')} • {post.get('timestamp_display', 'unknown')}")
        print(f"   Engagement: {post.get('likes', 0):,} likes • {post.get('retweets', 0):,} RTs • {post.get('replies', 0):,} replies")
        print(f"   Rate: {post.get('engagement_rate', 0):.2f}% • Categories: {', '.join(post.get('categories', []))}")

        content = post.get("content", "")
        if len(content) > 200:
            content = content[:200] + "..."
        print(f"\n   \"{content}\"")

        if post.get("url"):
            print(f"\n   URL: {post.get('url')}")

        print("-" * 70)

    # Show reply opportunities if requested
    if args.opportunities:
        print("\n" + "=" * 70)
        print("REPLY OPPORTUNITIES")
        print("=" * 70)

        opps = scanner.get_reply_opportunities()[:5]
        for i, opp in enumerate(opps, 1):
            print(f"\n{i}. @{opp.get('author')} (Opportunity Score: {opp.get('opportunity_score', 0):.1f})")
            print(f"   {opp.get('content', '')[:100]}...")
            print(f"   {opp.get('url')}")


def cmd_draft(args):
    """Draft replies to a post."""
    print("\n" + "=" * 70)
    print("REPLY GENERATOR")
    print("=" * 70)

    # Get post content
    content = args.content
    author = args.author or "unknown"

    if not content:
        print("\nPaste the post content (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        content = " ".join(lines)

    if not content:
        print("Error: No content provided")
        return

    print(f"\nOriginal post by @{author}:")
    print(f"\"{content[:200]}{'...' if len(content) > 200 else ''}\"")

    # Load profile
    profile_path = args.profile
    if not profile_path:
        default_profile = Path(__file__).parent / "profiles" / "justin_katz.json"
        if default_profile.exists():
            profile_path = str(default_profile)
            print(f"\nUsing profile: justin_katz.json")

    # Generate replies
    generator = ReplyGenerator(
        profile_path=profile_path,
        benchmark_name=args.benchmark
    )

    original_post = {
        "content": content,
        "author": author,
        "url": args.url,
    }

    print("\nGenerating replies...")
    replies = generator.generate_replies(original_post, args.num)

    print("\n" + "=" * 70)
    print("GENERATED REPLIES")
    print("=" * 70)

    for i, reply in enumerate(replies, 1):
        print(f"\n#{i} [{reply['type'].upper()}]")
        print(f"   Combined Score: {reply.get('combined_score', 0):.1f}/100")
        print(f"   Voice Match: {reply.get('voice_match', 0):.0f}% | Engagement: {reply.get('engagement_potential', 0):.0f}% | Length: {reply.get('length_score', 0):.0f}%")
        print(f"   Words: {reply['word_count']} (target: 26)")

        print(f"\n   \"{reply['text']}\"")
        print("-" * 50)

    # Offer to copy best reply
    print(f"\nBest reply (#{1}):")
    print(f"\n{replies[0]['text']}")


def cmd_brief(args):
    """Show daily engagement brief."""
    # Custom accounts if provided
    accounts = None
    if args.accounts:
        accounts = [a.strip().lstrip('@') for a in args.accounts.split(',')]

    brief = get_daily_brief(accounts)
    print(brief)


def cmd_opportunities(args):
    """Show reply opportunities."""
    print("\n" + "=" * 70)
    print("REPLY OPPORTUNITIES")
    print("=" * 70)

    scanner = FinTwitScanner(hours_back=args.hours)
    scanner.scan()

    opps = scanner.get_reply_opportunities()

    if not opps:
        print("\nNo good reply opportunities found right now.")
        return

    print(f"\nFound {len(opps)} opportunities (showing top {min(len(opps), args.limit)})")
    print("\nCriteria: High engagement, moderate replies, recent posts")

    for i, opp in enumerate(opps[:args.limit], 1):
        print(f"\n{'-' * 60}")
        print(f"#{i} Opportunity Score: {opp.get('opportunity_score', 0):.1f}")
        print(f"   @{opp.get('author')} • {opp.get('timestamp_display')}")
        print(f"   {opp.get('likes', 0):,} likes • {opp.get('retweets', 0):,} RTs • {opp.get('replies', 0):,} replies")

        content = opp.get("content", "")
        if len(content) > 150:
            content = content[:150] + "..."
        print(f"\n   \"{content}\"")

        if opp.get("url"):
            print(f"\n   {opp.get('url')}")

        # Quick draft option
        print(f"\n   → Run: python fintwit_cli.py draft -c \"{opp.get('content', '')[:50]}...\" -a {opp.get('author')}")


def cmd_analyze(args):
    """Analyze a reply for quality."""
    print("\n" + "=" * 70)
    print("REPLY ANALYZER")
    print("=" * 70)

    reply_text = args.text
    if not reply_text:
        print("\nPaste your reply text:")
        reply_text = input().strip()

    if not reply_text:
        print("Error: No reply text provided")
        return

    # Load profile and benchmark
    profile_path = args.profile
    if not profile_path:
        default_profile = Path(__file__).parent / "profiles" / "justin_katz.json"
        if default_profile.exists():
            profile_path = str(default_profile)

    voice = {}
    if profile_path and Path(profile_path).exists():
        with open(profile_path, 'r') as f:
            profile = json.load(f)
            voice = profile.get("voice", {})

    benchmark_path = Path(__file__).parent / "benchmarks" / f"{args.benchmark}.json"
    patterns = {}
    if benchmark_path.exists():
        with open(benchmark_path, 'r') as f:
            benchmark = json.load(f)
            patterns = benchmark.get("patterns", {})

    # Analyze
    analysis = analyze_reply_quality(reply_text, voice, patterns)

    print(f"\nReply: \"{reply_text}\"")
    print(f"\nWord count: {analysis['metrics']['word_count']} (target: 26)")

    scores = analysis['scores']
    print(f"\n--- SCORES ---")
    print(f"Combined Score:      {scores['combined_score']:.1f}/100")
    print(f"Voice Match:         {scores['voice_match']:.1f}/100")
    print(f"Engagement Potential:{scores['engagement_potential']:.1f}/100")
    print(f"Length Score:        {scores['length_score']:.1f}/100")

    if analysis.get('suggestions'):
        print(f"\n--- SUGGESTIONS ---")
        for suggestion in analysis['suggestions']:
            print(f"  • {suggestion}")


def main():
    parser = argparse.ArgumentParser(
        description="FinTwit Engagement CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fintwit_cli.py scan                          # Scan for trending posts
  python fintwit_cli.py scan --category options       # Filter by category
  python fintwit_cli.py scan --opportunities          # Show reply opportunities
  python fintwit_cli.py draft -c "Post content here"  # Draft replies
  python fintwit_cli.py brief                         # Daily engagement brief
  python fintwit_cli.py analyze -t "Your reply"       # Analyze a reply
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan FinTwit for trending posts")
    scan_parser.add_argument("--hours", type=int, default=48, help="Hours to look back (default: 48)")
    scan_parser.add_argument("--category", "-c", choices=["options", "dealer_positioning", "market_structure", "general_trading"],
                            help="Filter by category")
    scan_parser.add_argument("--limit", "-n", type=int, default=10, help="Max posts to show (default: 10)")
    scan_parser.add_argument("--accounts", "-a", help="Comma-separated accounts to scan")
    scan_parser.add_argument("--opportunities", "-o", action="store_true", help="Also show reply opportunities")

    # Draft command
    draft_parser = subparsers.add_parser("draft", help="Draft replies to a post")
    draft_parser.add_argument("--content", "-c", help="Post content to reply to")
    draft_parser.add_argument("--author", "-a", help="Post author")
    draft_parser.add_argument("--url", "-u", help="Post URL")
    draft_parser.add_argument("--profile", "-p", help="Path to voice profile JSON")
    draft_parser.add_argument("--benchmark", "-b", default="finance_twitter", help="Benchmark to use")
    draft_parser.add_argument("--num", "-n", type=int, default=5, help="Number of replies to generate")

    # Brief command
    brief_parser = subparsers.add_parser("brief", help="Show daily engagement brief")
    brief_parser.add_argument("--accounts", "-a", help="Comma-separated accounts to scan")

    # Opportunities command
    opp_parser = subparsers.add_parser("opportunities", help="Find reply opportunities")
    opp_parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    opp_parser.add_argument("--limit", "-n", type=int, default=10, help="Max opportunities to show")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a reply for quality")
    analyze_parser.add_argument("--text", "-t", help="Reply text to analyze")
    analyze_parser.add_argument("--profile", "-p", help="Path to voice profile")
    analyze_parser.add_argument("--benchmark", "-b", default="finance_twitter", help="Benchmark to use")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "draft":
        cmd_draft(args)
    elif args.command == "brief":
        cmd_brief(args)
    elif args.command == "opportunities":
        cmd_opportunities(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
