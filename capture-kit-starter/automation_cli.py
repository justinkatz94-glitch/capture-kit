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
from automation.follow_targeting import FollowTargetingManager
from automation.platforms import get_adapter, list_platforms
from automation.linkedin_benchmark import LinkedInBenchmarkManager, BenchmarkPost


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
    limit = getattr(args, 'limit', 10)
    print("Watchlist accounts:")
    for account in watchlist[:limit]:
        print(f"  - {account}")
    if len(watchlist) > limit:
        print(f"  ... and {len(watchlist) - limit} more")


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

    platform = getattr(args, 'platform', 'twitter')

    # Try to use LLM generator
    generator = LLMGenerator()
    analyzer = ContentAnalyzer()

    # Get platform adapter
    try:
        adapter = get_adapter(platform)
    except ValueError:
        adapter = None

    # Generate replies
    print(f"Generating {platform.upper()} replies to @{args.author}...")
    print(f"Content: {args.content[:100]}...")
    print()

    original_post = {
        "content": args.content,
        "author": args.author,
    }

    replies = generator.generate_replies(
        original_post=original_post,
        platform=platform,
        num_replies=args.count
    )

    for i, reply in enumerate(replies, 1):
        # Reply is a GeneratedReply object
        reply_content = reply.content if hasattr(reply, 'content') else str(reply)

        # Format for platform if adapter available
        if adapter:
            reply_content = adapter.format_for_platform(reply_content, "reply")

        analysis = analyzer.analyze(reply_content, platform)
        word_count = len(reply_content.split())
        char_count = len(reply_content)

        # Get platform-specific score
        if adapter:
            platform_result = adapter.score_platform_fit(reply_content, "reply")
            score = platform_result["score"]
        else:
            score = analysis.platform_score

        print(f"Reply {i}:")
        print(f"  {reply_content}")
        print(f"  [{word_count} words, {char_count} chars | Hook: {analysis.hook_type or 'none'} | Platform fit: {score}%]")
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

    # Get platform adapter for additional analysis
    try:
        adapter = get_adapter(args.platform)
        platform_result = adapter.score_platform_fit(args.content, args.content_type)
    except ValueError:
        adapter = None
        platform_result = None

    print(f"Content Analysis ({args.platform.upper()})")
    print(f"{'='*40}")
    print(f"Words: {analysis.word_count} | Chars: {analysis.char_count}")
    print()
    print(f"Hook: {analysis.hook_type or 'none'} (strength: {analysis.hook_strength:.0%})")
    if analysis.hook_text:
        print(f"  \"{analysis.hook_text[:60]}...\"")
    print()
    print(f"Framework: {analysis.framework}")
    print(f"Triggers: {', '.join(analysis.triggers) or 'none'}")
    print(f"Specificity: {analysis.specificity}")
    print()

    # Platform-specific scoring
    if platform_result:
        print(f"Platform fit ({args.platform}): {platform_result['score']}%")
        for issue in platform_result.get('issues', []):
            print(f"  ! {issue}")
    else:
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


# =============================================================================
# PLATFORM COMMANDS
# =============================================================================

def cmd_platforms_list(args):
    """List all available platforms."""
    platforms = list_platforms()
    print("Available Platforms:")
    print(f"{'='*40}")
    for platform in platforms:
        adapter = get_adapter(platform)
        print(f"\n{platform.upper()}")
        if adapter.post_length:
            print(f"  Post length: {adapter.post_length.optimal_min}-{adapter.post_length.optimal_max} chars")
        if adapter.reply_length:
            print(f"  Reply length: {adapter.reply_length.optimal_min}-{adapter.reply_length.optimal_max} chars")
        print(f"  Best hooks: {', '.join(adapter.effective_hooks[:4])}")


def cmd_platforms_show(args):
    """Show detailed rules for a platform."""
    try:
        adapter = get_adapter(args.platform)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"{adapter.platform_name.upper()} Platform Rules")
    print(f"{'='*50}")

    # Length configs
    print("\nContent Length Requirements:")
    if adapter.post_length:
        print(f"  Post: {adapter.post_length.min}-{adapter.post_length.max} chars (optimal: {adapter.post_length.optimal_min}-{adapter.post_length.optimal_max})")
    if adapter.reply_length:
        print(f"  Reply: {adapter.reply_length.min}-{adapter.reply_length.max} chars (optimal: {adapter.reply_length.optimal_min}-{adapter.reply_length.optimal_max})")
    if adapter.comment_length and adapter.comment_length != adapter.reply_length:
        print(f"  Comment: {adapter.comment_length.min}-{adapter.comment_length.max} chars (optimal: {adapter.comment_length.optimal_min}-{adapter.comment_length.optimal_max})")

    # Best times
    if adapter.best_times:
        print("\nBest Posting Times:")
        for window in adapter.best_times:
            print(f"  - {window.to_string()}")

    if adapter.best_days:
        print(f"\nBest Days: {', '.join(adapter.best_days)}")
    if adapter.worst_days:
        print(f"Worst Days: {', '.join(adapter.worst_days)}")

    # Effective hooks
    if adapter.effective_hooks:
        print(f"\nEffective Hooks: {', '.join(adapter.effective_hooks)}")

    # Rules
    if adapter.rules.get("do"):
        print("\nDO:")
        for rule in adapter.rules["do"]:
            print(f"  + {rule}")

    if adapter.rules.get("dont"):
        print("\nDON'T:")
        for rule in adapter.rules["dont"]:
            print(f"  - {rule}")

    if adapter.rules.get("tips"):
        print("\nTIPS:")
        for tip in adapter.rules["tips"]:
            print(f"  * {tip}")


# =============================================================================
# TARGETS COMMANDS
# =============================================================================

def cmd_targets_add(args):
    """Add a follow target."""
    manager = FollowTargetingManager()
    result = manager.add_target(
        handle=args.handle,
        reason=args.reason or "",
        source=args.source or "",
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Added target: @{result['handle']}")
    if result.get('reason'):
        print(f"  Reason: {result['reason']}")


def cmd_targets_remove(args):
    """Remove a follow target."""
    manager = FollowTargetingManager()
    result = manager.remove_target(args.handle)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Removed: @{result['handle']}")


def cmd_targets_list(args):
    """List follow targets."""
    manager = FollowTargetingManager()
    targets = manager.list_targets(status=args.status)

    if not targets:
        print("No targets found.")
        print("Add targets with: targets add @handle --reason 'why'")
        return

    status_label = f" ({args.status})" if args.status else ""
    print(f"Follow Targets{status_label}: {len(targets)}\n")

    for target in targets[:20]:
        status = ""
        if target.unfollowed_at:
            status = " [unfollowed]"
        elif target.followed_back is True:
            status = " [followed back]"
        elif target.followed_back is False:
            status = " [no followback]"
        elif target.followed_at:
            days = target.days_since_follow
            status = f" [followed {days}d ago]" if days else " [followed]"
        else:
            status = " [pending]"

        print(f"  @{target.handle}{status}")
        if target.reason:
            print(f"      Reason: {target.reason}")
        if target.source:
            print(f"      Source: @{target.source}")

    if len(targets) > 20:
        print(f"\n  ... and {len(targets) - 20} more")


def cmd_targets_track(args):
    """Track a follow action."""
    manager = FollowTargetingManager()
    result = manager.track_follow(
        handle=args.handle,
        source=args.source or "",
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Tracked follow: @{result['handle']}")
    print(f"  Status: {result['status']}")


def cmd_targets_followback(args):
    """Record followback status."""
    manager = FollowTargetingManager()

    if args.yes:
        followed_back = True
    elif args.no:
        followed_back = False
    else:
        print("Error: Specify --yes or --no")
        return

    result = manager.record_followback(args.handle, followed_back)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    status = "followed back" if followed_back else "did NOT follow back"
    print(f"@{result['handle']} {status}")


def cmd_targets_check(args):
    """Check for unfollow candidates."""
    manager = FollowTargetingManager()
    candidates = manager.get_unfollow_candidates(days=args.days)

    if not candidates:
        settings = manager.get_settings()
        days = args.days or settings.get("followback_check_days", 7)
        print(f"No unfollow candidates (checked after {days} days)")
        return

    print(f"Unfollow Candidates ({len(candidates)}):\n")
    for target in candidates:
        days = target.days_since_follow
        status = "unknown" if target.followed_back is None else "no followback"
        print(f"  @{target.handle} - followed {days} days ago ({status})")
        if target.source:
            print(f"      Source: @{target.source}")

    print(f"\nUnfollow with: targets unfollow @handle --reason 'why'")


def cmd_targets_unfollow(args):
    """Record an unfollow action."""
    manager = FollowTargetingManager()
    result = manager.record_unfollow(
        handle=args.handle,
        reason=args.reason or "",
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Recorded unfollow: @{result['handle']}")
    if result.get('reason'):
        print(f"  Reason: {result['reason']}")


def cmd_targets_suggest(args):
    """Suggest new follow targets."""
    manager = FollowTargetingManager()
    suggestions = manager.suggest_targets(limit=args.limit or 10)

    if not suggestions:
        print("No suggestions available.")
        print("Add accounts to your watchlist first.")
        return

    print(f"Suggested Follow Targets:\n")
    for i, sug in enumerate(suggestions, 1):
        print(f"{i}. {sug['handle']}")
        print(f"   Reason: {sug['reason']}")
        print(f"   Action: {sug['action']}")
        print()


def cmd_targets_analyze(args):
    """Analyze a potential follow target."""
    manager = FollowTargetingManager()
    analysis = manager.analyze_target(args.handle)

    print(f"Analysis for @{analysis['handle']}")
    print(f"{'='*40}")
    print(f"\nRecommendation: {analysis['analysis']['recommendation']}")

    print(f"\nFactors to check:")
    for factor in analysis['analysis']['factors_to_check']:
        print(f"  - {factor}")

    print(f"\nGood signs:")
    for sign in analysis['scoring_guide']['good_signs']:
        print(f"  + {sign}")

    print(f"\nRed flags:")
    for flag in analysis['scoring_guide']['red_flags']:
        print(f"  - {flag}")


def cmd_targets_stats(args):
    """Show follow targeting statistics."""
    manager = FollowTargetingManager()
    stats = manager.get_stats()

    print("Follow Targeting Stats")
    print(f"{'='*40}")
    print(f"Total targets: {stats['total_targets']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Currently followed: {stats['currently_followed']}")
    print(f"  Unfollowed: {stats['unfollowed']}")
    print()
    print(f"Followback tracking:")
    print(f"  Followed back: {stats['followbacks']}")
    print(f"  No followback: {stats['no_followbacks']}")
    print(f"  Unknown: {stats['unknown_status']}")
    print(f"  Followback rate: {stats['followback_rate']}")
    print()
    print(f"Unfollow candidates: {stats['unfollow_candidates']}")


def cmd_targets_followed(args):
    """Show followed accounts needing status check."""
    manager = FollowTargetingManager()

    if args.pending:
        targets = manager.get_followed_pending_check()
        if not targets:
            print("No accounts pending followback check.")
            return

        print(f"Accounts needing followback check ({len(targets)}):\n")
        for target in targets:
            days = target.days_since_follow
            print(f"  @{target.handle} - followed {days} days ago")

        print(f"\nRecord with: targets followback @handle --yes/--no")
    else:
        targets = manager.list_targets(status="followed")
        if not targets:
            print("No followed accounts.")
            return

        print(f"Currently followed ({len(targets)}):\n")
        for target in targets[:20]:
            days = target.days_since_follow
            fb = ""
            if target.followed_back is True:
                fb = " [FB]"
            elif target.followed_back is False:
                fb = " [no FB]"
            print(f"  @{target.handle} - {days} days{fb}")


def cmd_targets_settings(args):
    """View or update targeting settings."""
    manager = FollowTargetingManager()

    if args.days is not None:
        result = manager.update_settings(followback_check_days=args.days)
        print(f"Updated followback check to {args.days} days")
    else:
        settings = manager.get_settings()
        print("Follow Targeting Settings")
        print(f"{'='*40}")
        for key, value in settings.items():
            print(f"  {key}: {value}")


# =============================================================================
# BENCHMARK COMMANDS
# =============================================================================

def cmd_benchmark_add(args):
    """Add a benchmark account."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user. Create or switch to a user first.")
        return

    result = manager.add_account(args.handle, args.name or "")

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Added benchmark: @{result['added']}")
    print(f"  Total accounts: {result['total_accounts']}")


def cmd_benchmark_remove(args):
    """Remove a benchmark account."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user.")
        return

    result = manager.remove_account(args.handle)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Removed: @{result['removed']}")


def cmd_benchmark_list(args):
    """List benchmark accounts."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user.")
        return

    accounts = manager.list_accounts()

    if not accounts:
        print("No benchmark accounts.")
        print("Add accounts with: benchmark add @handle")
        return

    print(f"LinkedIn Benchmark Accounts ({len(accounts)}):\n")
    for acct in accounts:
        posts = acct.get('posts_analyzed', 0)
        print(f"  @{acct['handle']}")
        if acct.get('name') and acct['name'] != acct['handle']:
            print(f"      Name: {acct['name']}")
        print(f"      Posts analyzed: {posts}")
        if acct.get('last_scanned'):
            print(f"      Last scanned: {acct['last_scanned'][:10]}")


def cmd_benchmark_add_post(args):
    """Add a post to benchmark data."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user.")
        return

    post = BenchmarkPost(
        id="",
        author=args.author.lstrip('@'),
        platform="linkedin",
        content=args.content,
        url=args.url or "",
        likes=args.likes or 0,
        comments=args.comments or 0,
        shares=args.shares or 0,
    )

    result = manager.add_post(post)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"Added post from @{result['author']}")
    print(f"  Hook type: {result['hook_type']}")
    print(f"  Post ID: {result['post_id']}")


def cmd_benchmark_patterns(args):
    """Show extracted patterns."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user.")
        return

    patterns = manager.get_patterns()

    if not patterns:
        print("No patterns extracted yet.")
        print("Add posts with: benchmark add-post --author @handle --content '...'")
        return

    print("LinkedIn Benchmark Patterns")
    print(f"{'='*50}")
    print(f"Total posts analyzed: {patterns.get('total_posts', 0)}")
    print()

    # Optimal length
    length = patterns.get('optimal_length', {})
    print(f"Optimal post length: {length.get('avg', 0)} words")
    print(f"  Range: {length.get('min', 0)} - {length.get('max', 0)} words")
    print()

    # Hook types
    hooks = patterns.get('hook_types', {})
    if hooks:
        print("Effective hooks:")
        for hook, count in list(hooks.items())[:5]:
            print(f"  - {hook}: {count} posts")
    print()

    # Style
    print("Style patterns:")
    print(f"  Line breaks: {patterns.get('line_break_usage', 0)}% of posts")
    print(f"  Emoji usage: {patterns.get('emoji_usage', 0)}% of posts")
    print(f"  Hashtags: {patterns.get('hashtag_usage', 0)}% of posts")
    print()

    # Top topics
    topics = patterns.get('top_topics', {})
    if topics:
        print("Top topics:")
        for topic, count in list(topics.items())[:5]:
            print(f"  - {topic}: {count} mentions")


def cmd_benchmark_stats(args):
    """Show benchmark statistics."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user.")
        return

    stats = manager.get_stats()

    if "error" in stats:
        print(f"Error: {stats['error']}")
        return

    print("LinkedIn Benchmark Stats")
    print(f"{'='*50}")
    print(f"User: {stats['user']}")
    print(f"Niche: {stats['niche']}")
    print(f"Topics: {', '.join(stats.get('niche_topics', []))}")
    print()
    print(f"Accounts tracked: {stats['accounts_tracked']}")
    print(f"Posts analyzed: {stats['total_posts_analyzed']}")
    print(f"Last updated: {stats['updated_at'][:10] if stats.get('updated_at') else 'never'}")


def cmd_benchmark_context(args):
    """Show generation context (what LLM sees)."""
    manager = LinkedInBenchmarkManager()
    if not manager.user_name:
        print("No active user.")
        return

    context = manager.get_generation_context()

    if not context.get('has_data'):
        print(context.get('message', 'No benchmark data'))
        return

    print("LLM Generation Context")
    print(f"{'='*50}")
    print(f"Niche: {context['niche']}")
    print(f"Topics: {', '.join(context['niche_topics'])}")
    print()
    print(f"Optimal length: {context['optimal_length'].get('avg', 0)} words")
    print(f"Effective hooks: {', '.join(context['effective_hooks'])}")
    print(f"Top topics: {', '.join(context['top_topics'])}")
    print()
    print("Style recommendations:")
    style = context['style_notes']
    print(f"  Use line breaks: {'Yes' if style['use_line_breaks'] else 'No'}")
    print(f"  Use emoji: {'Yes' if style['use_emoji'] else 'No'}")
    print(f"  Use hashtags: {'Yes' if style['use_hashtags'] else 'No'}")
    print()
    print(f"Based on {context['total_posts_analyzed']} posts from {context['accounts_tracked']} accounts")

    if context.get('examples'):
        print()
        print("Example posts:")
        for i, ex in enumerate(context['examples'][:2], 1):
            print(f"\n  {i}. @{ex['author']} ({ex['engagement']} likes)")
            print(f"     {ex['content'][:150]}...")


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
    scan_parser = subparsers.add_parser("scan", help="Scan for trending posts")
    scan_parser.add_argument("--limit", type=int, default=10, help="Max accounts to show")

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
    draft_parser.add_argument("--author", default="unknown", help="Original author")
    draft_parser.add_argument("--content", required=True, help="Original content")
    draft_parser.add_argument("--count", type=int, default=3, help="Number of drafts")
    draft_parser.add_argument("--platform", default="twitter", help="Platform (twitter, linkedin, instagram)")

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
    analyze_parser.add_argument("--platform", default="twitter", help="Platform (twitter, linkedin, instagram)")
    analyze_parser.add_argument("--content-type", dest="content_type", default="post",
                                choices=["post", "reply", "comment"], help="Content type")

    # Platforms commands
    platforms_parser = subparsers.add_parser("platforms", help="Platform information")
    platforms_sub = platforms_parser.add_subparsers(dest="platforms_command")

    platforms_sub.add_parser("list", help="List available platforms")

    pshow = platforms_sub.add_parser("show", help="Show platform rules")
    pshow.add_argument("platform", help="Platform name (twitter, linkedin, instagram)")

    # Targets commands
    targets_parser = subparsers.add_parser("targets", help="Follow targeting management")
    targets_sub = targets_parser.add_subparsers(dest="targets_command")

    # targets add
    tadd = targets_sub.add_parser("add", help="Add follow target")
    tadd.add_argument("handle", help="Twitter handle")
    tadd.add_argument("--reason", help="Why you want to follow them")
    tadd.add_argument("--source", help="Account you found them from")

    # targets remove
    tremove = targets_sub.add_parser("remove", help="Remove target")
    tremove.add_argument("handle", help="Twitter handle")

    # targets list
    tlist = targets_sub.add_parser("list", help="List targets")
    tlist.add_argument("--status", choices=["pending", "followed", "unfollowed", "followback", "no_followback"],
                       help="Filter by status")

    # targets track
    ttrack = targets_sub.add_parser("track", help="Track a follow action")
    ttrack.add_argument("handle", help="Handle that was followed")
    ttrack.add_argument("--source", help="Where you found them")

    # targets followback
    tfb = targets_sub.add_parser("followback", help="Record followback status")
    tfb.add_argument("handle", help="Twitter handle")
    tfb.add_argument("--yes", action="store_true", help="They followed back")
    tfb.add_argument("--no", action="store_true", help="They did not follow back")

    # targets check
    tcheck = targets_sub.add_parser("check", help="Show unfollow candidates")
    tcheck.add_argument("--days", type=int, help="Days to wait before suggesting unfollow")

    # targets unfollow
    tunfollow = targets_sub.add_parser("unfollow", help="Record an unfollow")
    tunfollow.add_argument("handle", help="Handle that was unfollowed")
    tunfollow.add_argument("--reason", help="Reason for unfollowing")

    # targets suggest
    tsuggest = targets_sub.add_parser("suggest", help="Suggest new targets")
    tsuggest.add_argument("--limit", type=int, default=10, help="Max suggestions")

    # targets analyze
    tanalyze = targets_sub.add_parser("analyze", help="Analyze a potential target")
    tanalyze.add_argument("handle", help="Handle to analyze")

    # targets stats
    targets_sub.add_parser("stats", help="Show targeting statistics")

    # targets followed
    tfollowed = targets_sub.add_parser("followed", help="Show followed accounts")
    tfollowed.add_argument("--pending", action="store_true", help="Show accounts needing followback check")

    # targets settings
    tsettings = targets_sub.add_parser("settings", help="View/update settings")
    tsettings.add_argument("--days", type=int, help="Set followback check days")

    # Benchmark commands (LinkedIn)
    benchmark_parser = subparsers.add_parser("benchmark", help="LinkedIn benchmark management")
    benchmark_sub = benchmark_parser.add_subparsers(dest="benchmark_command")

    # benchmark add
    badd = benchmark_sub.add_parser("add", help="Add benchmark account")
    badd.add_argument("handle", help="LinkedIn handle")
    badd.add_argument("--name", help="Display name")

    # benchmark remove
    bremove = benchmark_sub.add_parser("remove", help="Remove benchmark account")
    bremove.add_argument("handle", help="LinkedIn handle")

    # benchmark list
    benchmark_sub.add_parser("list", help="List benchmark accounts")

    # benchmark add-post
    baddpost = benchmark_sub.add_parser("add-post", help="Add post to benchmark")
    baddpost.add_argument("--author", required=True, help="Post author")
    baddpost.add_argument("--content", required=True, help="Post content")
    baddpost.add_argument("--url", help="Post URL")
    baddpost.add_argument("--likes", type=int, default=0, help="Like count")
    baddpost.add_argument("--comments", type=int, default=0, help="Comment count")
    baddpost.add_argument("--shares", type=int, default=0, help="Share count")

    # benchmark patterns
    benchmark_sub.add_parser("patterns", help="Show extracted patterns")

    # benchmark stats
    benchmark_sub.add_parser("stats", help="Show benchmark statistics")

    # benchmark context
    benchmark_sub.add_parser("context", help="Show LLM generation context")

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

    elif args.command == "platforms":
        if args.platforms_command == "list":
            cmd_platforms_list(args)
        elif args.platforms_command == "show":
            cmd_platforms_show(args)
        else:
            platforms_parser.print_help()

    elif args.command == "targets":
        if args.targets_command == "add":
            cmd_targets_add(args)
        elif args.targets_command == "remove":
            cmd_targets_remove(args)
        elif args.targets_command == "list":
            cmd_targets_list(args)
        elif args.targets_command == "track":
            cmd_targets_track(args)
        elif args.targets_command == "followback":
            cmd_targets_followback(args)
        elif args.targets_command == "check":
            cmd_targets_check(args)
        elif args.targets_command == "unfollow":
            cmd_targets_unfollow(args)
        elif args.targets_command == "suggest":
            cmd_targets_suggest(args)
        elif args.targets_command == "analyze":
            cmd_targets_analyze(args)
        elif args.targets_command == "stats":
            cmd_targets_stats(args)
        elif args.targets_command == "followed":
            cmd_targets_followed(args)
        elif args.targets_command == "settings":
            cmd_targets_settings(args)
        else:
            targets_parser.print_help()

    elif args.command == "benchmark":
        if args.benchmark_command == "add":
            cmd_benchmark_add(args)
        elif args.benchmark_command == "remove":
            cmd_benchmark_remove(args)
        elif args.benchmark_command == "list":
            cmd_benchmark_list(args)
        elif args.benchmark_command == "add-post":
            cmd_benchmark_add_post(args)
        elif args.benchmark_command == "patterns":
            cmd_benchmark_patterns(args)
        elif args.benchmark_command == "stats":
            cmd_benchmark_stats(args)
        elif args.benchmark_command == "context":
            cmd_benchmark_context(args)
        else:
            benchmark_parser.print_help()


if __name__ == "__main__":
    main()
