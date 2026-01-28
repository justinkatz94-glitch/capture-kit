#!/usr/bin/env python3
"""
Capture Kit - Main Automation CLI

Unified command-line interface for all automation features.
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from automation import (
    UserManager, ContentAnalyzer, LLMGenerator,
    get_active_user, switch_user
)
from automation.queue_manager import QueueManager
from automation.post_tracker import PostTracker
from automation.trending_scanner import TrendingScanner
from automation.feedback_loop import FeedbackLoop
from automation.voice_evolver import VoiceEvolver


def cmd_user_create(args):
    """Create a new user profile."""
    manager = UserManager()
    result = manager.create_user(
        name=args.name,
        twitter_handle=args.twitter or "",
        linkedin_handle=args.linkedin or "",
        instagram_handle=args.instagram or "",
        niche=args.niche or "",
        goal=args.goal or "grow_followers",
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Created user: {result['name']}")
    print(f"  Niche: {result['niche']}")
    print(f"  Goal: {result['goal']}")
    print(f"  Profile: {result['profile_path']}")


def cmd_user_switch(args):
    """Switch active user."""
    result = switch_user(args.name)
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Switched to: {result['active_user']}")
    print(f"  Niche: {result['niche']}")
    print(f"  Goal: {result['goal']}")


def cmd_user_list(args):
    """List all users."""
    manager = UserManager()
    users = manager.list_users()

    if not users:
        print("No users found. Create one with: user create <name>")
        return

    print("Users:")
    for user in users:
        active = " (active)" if user['is_active'] else ""
        print(f"  - {user['name']}{active}")
        print(f"      Niche: {user['niche']}, Goal: {user['goal']}")


def cmd_user_profile(args):
    """Show active user profile."""
    manager = UserManager()
    profile = manager.get_active_profile()

    if not profile:
        print("No active user. Switch to a user first.")
        return

    print(f"Profile: {profile['name']}")
    print(f"  Username: {profile['username']}")
    print(f"  Niche: {profile['niche']}")
    print(f"  Goal: {profile['goal']}")
    print(f"  Watchlist: {len(profile.get('watchlist', []))} accounts")
    print(f"  Keywords: {len(profile.get('keywords', []))} keywords")
    print(f"\nVoice:")
    voice = profile.get('voice', {})
    print(f"  Tone: {voice.get('tone', 'not set')}")
    print(f"  Formality: {voice.get('formality', 'not set')}")
    print(f"  Emoji style: {voice.get('emoji_style', 'not set')}")


def cmd_scan(args):
    """Scan for trending posts."""
    user = get_active_user()
    if not user:
        print("No active user. Create or switch to a user first.")
        return

    scanner = TrendingScanner()
    stats = scanner.get_scan_stats()

    print(f"Scan Stats for {user}:")
    print(f"  Watchlist: {stats['watchlist_size']} accounts")
    print(f"  Keywords: {stats['keywords_count']}")
    print(f"  Cached posts: {stats['total_posts']}")
    print(f"  High opportunity: {stats['high_opportunity']}")
    print(f"  Last scan: {stats['last_scan'] or 'never'}")
    print()

    # Show watchlist
    watchlist = scanner.get_watchlist()
    print("Watchlist accounts:")
    for account in watchlist[:10]:
        print(f"  - {account}")
    if len(watchlist) > 10:
        print(f"  ... and {len(watchlist) - 10} more")


def cmd_opportunities(args):
    """Show reply opportunities."""
    scanner = TrendingScanner()
    opportunities = scanner.get_opportunities(
        min_score=args.min_score,
        limit=args.limit
    )

    if not opportunities:
        print("No high-scoring opportunities found.")
        print("Add posts with: add-post --author @handle --content '...'")
        return

    print(f"Top {len(opportunities)} Reply Opportunities:\n")
    for i, post in enumerate(opportunities, 1):
        print(f"{i}. @{post.author} (Score: {post.reply_opportunity_score:.0f})")
        print(f"   {post.content[:100]}...")
        print(f"   Engagement: {post.total_engagement} | URL: {post.url}")
        print()


def cmd_add_post(args):
    """Add a post to the trending cache."""
    scanner = TrendingScanner()
    from automation.trending_scanner import TrendingPost

    post = TrendingPost(
        id=str(hash(args.url or args.content))[:8],
        author=args.author.lstrip('@'),
        content=args.content,
        url=args.url or "",
        platform=args.platform,
        posted_at=args.posted_at or "",
        likes=args.likes or 0,
        retweets=args.retweets or 0,
        replies=args.replies or 0,
    )

    result = scanner.add_post(post)
    print(f"Status: {result['status']}")
    if 'score' in result:
        print(f"Opportunity score: {result['score']:.0f}")


def cmd_draft(args):
    """Draft replies to a post."""
    user = get_active_user()
    if not user:
        print("No active user. Create or switch to a user first.")
        return

    # Try to use LLM generator
    generator = LLMGenerator()
    analyzer = ContentAnalyzer()

    # Generate replies
    print(f"Generating replies to @{args.author}...")
    print(f"Content: {args.content[:100]}...")
    print()

    replies = generator.generate_replies(
        post_content=args.content,
        post_author=args.author,
        count=args.count
    )

    for i, reply in enumerate(replies, 1):
        analysis = analyzer.analyze(reply, "twitter")
        word_count = len(reply.split())

        print(f"Reply {i}:")
        print(f"  {reply}")
        print(f"  [{word_count} words | Hook: {analysis.hook_type or 'none'} | Triggers: {', '.join(analysis.triggers[:2]) or 'none'}]")
        print()


def cmd_queue_add(args):
    """Add content to queue."""
    queue = QueueManager()
    analyzer = ContentAnalyzer()

    analysis = analyzer.analyze(args.content, args.platform)

    item = queue.add_to_queue(
        content=args.content,
        platform=args.platform,
        reply_to_url=args.reply_to,
        reply_to_author=args.author,
        analysis=analysis.to_dict() if hasattr(analysis, 'to_dict') else {},
    )

    print(f"Added to queue: {item.id}")
    print(f"  Platform: {item.platform}")
    print(f"  Status: {item.status}")


def cmd_queue_list(args):
    """List queue items."""
    queue = QueueManager()
    stats = queue.get_queue_stats()

    print("Queue Status:")
    print(f"  Pending: {stats['pending_count']}")
    print(f"  Approved: {stats['approved_count']}")
    print(f"  Posted: {stats['posted_count']}")
    print()

    if args.status == "pending" or not args.status:
        pending = queue.list_pending()
        if pending:
            print("Pending items:")
            for item in pending[:10]:
                print(f"  [{item.id}] {item.content[:60]}...")
                print(f"       Score: {item.combined_score:.2f} | Platform: {item.platform}")

    if args.status == "approved":
        approved = queue.list_approved()
        if approved:
            print("Approved items:")
            for item in approved[:10]:
                print(f"  [{item.id}] {item.content[:60]}...")


def cmd_queue_approve(args):
    """Approve a queue item."""
    queue = QueueManager()
    result = queue.approve(args.item_id)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Approved: {result['item_id']}")


def cmd_queue_post(args):
    """Mark item as posted."""
    queue = QueueManager()
    result = queue.mark_posted(args.item_id, args.url or "")

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Marked as posted: {result['item_id']}")


def cmd_log(args):
    """Log a posted piece of content."""
    tracker = PostTracker()

    record = tracker.log_post(
        content=args.content,
        url=args.url,
        platform=args.platform,
        initial_engagement={
            "likes": args.likes or 0,
            "retweets": args.retweets or 0,
            "replies": args.replies or 0,
        }
    )

    print(f"Logged post: {record.id}")
    print(f"  Hook: {record.hook_type or 'none'}")
    print(f"  Framework: {record.framework}")
    print(f"  Techniques: {', '.join(record.techniques[:3])}")


def cmd_history(args):
    """Show post history."""
    tracker = PostTracker()
    posts = tracker.get_recent_posts(limit=args.limit)

    if not posts:
        print("No posts in history yet.")
        return

    print(f"Recent {len(posts)} posts:\n")
    for post in posts:
        velocity = f"Velocity: {post.engagement_velocity:.1f}/hr" if post.engagement_velocity else ""
        print(f"[{post.id}] {post.posted_at[:10]} | {post.platform}")
        print(f"  {post.content[:70]}...")
        print(f"  Hook: {post.hook_type or 'none'} | {velocity}")
        print()


def cmd_report(args):
    """Generate weekly report."""
    loop = FeedbackLoop()

    try:
        summary = loop.generate_weekly_report(week_offset=args.week or 0)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"Weekly Report: {summary.week_start[:10]} to {summary.week_end[:10]}")
    print(f"{'='*50}")
    print(f"Posts: {summary.posts_count}")
    print(f"Total engagement: {summary.total_engagement}")
    print(f"Avg engagement rate: {summary.avg_engagement_rate:.2f}")
    print()

    if summary.best_hook_types:
        print(f"Best hooks: {', '.join(summary.best_hook_types)}")

    if summary.successful_techniques:
        print(f"Top techniques:")
        for tech in summary.successful_techniques[:3]:
            print(f"  - {tech['technique']}: {tech['avg_velocity']:.1f} velocity")

    if summary.recommendations:
        print(f"\nRecommendations:")
        for rec in summary.recommendations:
            print(f"  - {rec}")

    if summary.next_week_focus:
        print(f"\nFocus next week: {summary.next_week_focus}")


def cmd_trends(args):
    """Show trend analysis."""
    loop = FeedbackLoop()
    trends = loop.get_trend_analysis(weeks=args.weeks or 4)

    if "error" in trends:
        print(f"Error: {trends['error']}")
        return

    print(f"Trend Analysis ({trends['weeks_analyzed']} weeks)")
    print(f"{'='*40}")
    print(f"Velocity trend: {trends['velocity_trend']}")
    print(f"Volume trend: {trends['volume_trend']}")
    print(f"Avg velocity: {trends['avg_velocity']:.2f}")
    print(f"Avg posts/week: {trends['avg_posts_per_week']:.1f}")

    if trends['consistent_techniques']:
        print(f"\nConsistent winners: {', '.join(trends['consistent_techniques'])}")

    print(f"\nRecommendation: {trends['recommendation']}")


def cmd_evolve(args):
    """Suggest or apply voice evolution."""
    evolver = VoiceEvolver()

    if args.apply:
        # Apply evolution
        result = evolver.apply_evolution()
        if "error" in result:
            print(f"Error: {result['error']}")
            return

        print("Voice evolved!")
        print(f"Version: {result['version']}")
        for change in result['changes_made']:
            print(f"  - {change}")
    else:
        # Just suggest
        suggestions = evolver.suggest_voice_updates()
        if "error" in suggestions:
            print(f"Error: {suggestions['error']}")
            return

        print("Voice Evolution Suggestions")
        print(f"{'='*40}")

        for i, sug in enumerate(suggestions.get('suggestions', [])):
            print(f"\n{i+1}. {sug.get('field', '')}")
            if 'current' in sug and 'suggested' in sug:
                print(f"   Current: {sug['current']} -> Suggested: {sug['suggested']}")
            if 'values' in sug:
                print(f"   Add: {sug['values']}")
            print(f"   Reason: {sug['reason']}")

        print("\nRun with --apply to apply these changes")


def cmd_analyze(args):
    """Analyze content."""
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze(args.content, args.platform)

    print("Content Analysis")
    print(f"{'='*40}")
    print(f"Words: {analysis.word_count} | Chars: {analysis.char_count}")
    print()
    print(f"Hook: {analysis.hook_type or 'none'} (strength: {analysis.hook_strength:.0%})")
    print(f"  \"{analysis.hook_text[:60]}...\"")
    print()
    print(f"Framework: {analysis.framework}")
    print(f"Triggers: {', '.join(analysis.triggers) or 'none'}")
    print(f"Specificity: {analysis.specificity}")
    print()
    print(f"Platform fit: {analysis.platform_score:.0f}%")
    for issue in analysis.platform_issues:
        print(f"  ! {issue}")
    print()

    if analysis.strengths:
        print("Strengths:")
        for s in analysis.strengths:
            print(f"  + {s}")

    if analysis.weaknesses:
        print("Weaknesses:")
        for w in analysis.weaknesses:
            print(f"  - {w}")


def main():
    parser = argparse.ArgumentParser(
        description="Capture Kit - Social Media Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s user create "John Doe" --twitter @johndoe --niche fintwit
  %(prog)s user switch "John Doe"
  %(prog)s scan
  %(prog)s opportunities
  %(prog)s draft --author spotgamma --content "Market update..."
  %(prog)s analyze --content "Your post content here"
  %(prog)s report
  %(prog)s evolve --apply
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # User commands
    user_parser = subparsers.add_parser("user", help="User management")
    user_sub = user_parser.add_subparsers(dest="user_command")

    create_parser = user_sub.add_parser("create", help="Create user")
    create_parser.add_argument("name", help="User name")
    create_parser.add_argument("--twitter", help="Twitter handle")
    create_parser.add_argument("--linkedin", help="LinkedIn handle")
    create_parser.add_argument("--instagram", help="Instagram handle")
    create_parser.add_argument("--niche", help="Niche (fintwit, crypto, tech)")
    create_parser.add_argument("--goal", help="Goal (grow_followers, drive_traffic, build_authority)")

    switch_parser = user_sub.add_parser("switch", help="Switch user")
    switch_parser.add_argument("name", help="User name")

    user_sub.add_parser("list", help="List users")
    user_sub.add_parser("profile", help="Show active profile")

    # Scan
    subparsers.add_parser("scan", help="Scan for trending posts")

    # Opportunities
    opp_parser = subparsers.add_parser("opportunities", help="Show reply opportunities")
    opp_parser.add_argument("--min-score", type=float, default=50, help="Minimum score")
    opp_parser.add_argument("--limit", type=int, default=10, help="Max results")

    # Add post
    add_parser = subparsers.add_parser("add-post", help="Add post to trending cache")
    add_parser.add_argument("--author", required=True, help="Post author")
    add_parser.add_argument("--content", required=True, help="Post content")
    add_parser.add_argument("--url", help="Post URL")
    add_parser.add_argument("--platform", default="twitter", help="Platform")
    add_parser.add_argument("--posted-at", help="Posted timestamp")
    add_parser.add_argument("--likes", type=int, help="Like count")
    add_parser.add_argument("--retweets", type=int, help="Retweet count")
    add_parser.add_argument("--replies", type=int, help="Reply count")

    # Draft
    draft_parser = subparsers.add_parser("draft", help="Draft replies")
    draft_parser.add_argument("--author", required=True, help="Original author")
    draft_parser.add_argument("--content", required=True, help="Original content")
    draft_parser.add_argument("--count", type=int, default=3, help="Number of drafts")

    # Queue commands
    queue_parser = subparsers.add_parser("queue", help="Queue management")
    queue_sub = queue_parser.add_subparsers(dest="queue_command")

    qadd = queue_sub.add_parser("add", help="Add to queue")
    qadd.add_argument("--content", required=True, help="Content")
    qadd.add_argument("--platform", default="twitter", help="Platform")
    qadd.add_argument("--reply-to", help="Reply to URL")
    qadd.add_argument("--author", help="Original author")

    qlist = queue_sub.add_parser("list", help="List queue")
    qlist.add_argument("--status", choices=["pending", "approved", "posted"], help="Filter by status")

    qapprove = queue_sub.add_parser("approve", help="Approve item")
    qapprove.add_argument("item_id", help="Item ID")

    qpost = queue_sub.add_parser("post", help="Mark as posted")
    qpost.add_argument("item_id", help="Item ID")
    qpost.add_argument("--url", help="Post URL")

    # Log
    log_parser = subparsers.add_parser("log", help="Log a post")
    log_parser.add_argument("--content", required=True, help="Post content")
    log_parser.add_argument("--url", required=True, help="Post URL")
    log_parser.add_argument("--platform", default="twitter", help="Platform")
    log_parser.add_argument("--likes", type=int, help="Initial likes")
    log_parser.add_argument("--retweets", type=int, help="Initial retweets")
    log_parser.add_argument("--replies", type=int, help="Initial replies")

    # History
    hist_parser = subparsers.add_parser("history", help="Show post history")
    hist_parser.add_argument("--limit", type=int, default=10, help="Max posts")

    # Report
    report_parser = subparsers.add_parser("report", help="Generate weekly report")
    report_parser.add_argument("--week", type=int, default=0, help="Week offset (0=current, -1=last)")

    # Trends
    trends_parser = subparsers.add_parser("trends", help="Show trend analysis")
    trends_parser.add_argument("--weeks", type=int, default=4, help="Weeks to analyze")

    # Evolve
    evolve_parser = subparsers.add_parser("evolve", help="Voice evolution")
    evolve_parser.add_argument("--apply", action="store_true", help="Apply suggestions")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze content")
    analyze_parser.add_argument("--content", required=True, help="Content to analyze")
    analyze_parser.add_argument("--platform", default="twitter", help="Platform")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route commands
    if args.command == "user":
        if args.user_command == "create":
            cmd_user_create(args)
        elif args.user_command == "switch":
            cmd_user_switch(args)
        elif args.user_command == "list":
            cmd_user_list(args)
        elif args.user_command == "profile":
            cmd_user_profile(args)
        else:
            user_parser.print_help()

    elif args.command == "scan":
        cmd_scan(args)

    elif args.command == "opportunities":
        cmd_opportunities(args)

    elif args.command == "add-post":
        cmd_add_post(args)

    elif args.command == "draft":
        cmd_draft(args)

    elif args.command == "queue":
        if args.queue_command == "add":
            cmd_queue_add(args)
        elif args.queue_command == "list":
            cmd_queue_list(args)
        elif args.queue_command == "approve":
            cmd_queue_approve(args)
        elif args.queue_command == "post":
            cmd_queue_post(args)
        else:
            queue_parser.print_help()

    elif args.command == "log":
        cmd_log(args)

    elif args.command == "history":
        cmd_history(args)

    elif args.command == "report":
        cmd_report(args)

    elif args.command == "trends":
        cmd_trends(args)

    elif args.command == "evolve":
        cmd_evolve(args)

    elif args.command == "analyze":
        cmd_analyze(args)


if __name__ == "__main__":
    main()
