"""
Auto-Engage: Scan trending posts and generate replies in one command.

Usage:
    python auto_engage.py
    python auto_engage.py --limit 5
    python auto_engage.py --category options
"""

import os
import sys
import argparse

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation.llm_generator import LLMGenerator
from automation.user_manager import get_active_profile
from engagement.scanner import scan_fintwit
from engagement.scoring import score_opportunity


def auto_engage(limit: int = 3, category: str = None, platform: str = "twitter"):
    """
    Scan for trending posts and generate replies automatically.
    
    Args:
        limit: Number of posts to generate replies for
        category: Filter by category (options, dealer_positioning, market_structure)
        platform: Target platform
    """
    print("=" * 60)
    print("AUTO-ENGAGE: Scanning and Drafting")
    print("=" * 60)
    print()
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY not set")
        print("Run: setx ANTHROPIC_API_KEY \"your-key-here\"")
        return
    
    # Check for active profile
    profile = get_active_profile()
    if not profile:
        print("[ERROR] No active user profile")
        print("Run: python automation_cli.py user create")
        return
    
    print(f"[OK] User: {profile.get('name', 'Unknown')}")
    print(f"[OK] Platform: {platform}")
    print()
    
    # Step 1: Scan for trending posts
    print("[SCAN] Scanning for trending posts...")
    print("-" * 40)
    
    try:
        result = scan_fintwit(category=category, limit=limit * 3)  # Get extra to filter
        posts = result.get('trending_posts', []) or result.get('reply_opportunities', [])
    except Exception as e:
        print(f"[ERROR] Scan failed: {e}")
        print("\nNote: Twitter syndication API may be rate-limited.")
        print("Try again in a few minutes.")
        return
    
    if not posts:
        print("No posts found. Try again later.")
        return
    
    # Score and sort opportunities
    scored_posts = []
    for post in posts:
        try:
            score = score_opportunity(post)
            post['opportunity_score'] = score
            scored_posts.append(post)
        except:
            post['opportunity_score'] = 50
            scored_posts.append(post)
    
    scored_posts.sort(key=lambda p: p.get('opportunity_score', 0), reverse=True)
    top_posts = scored_posts[:limit]
    
    print(f"Found {len(posts)} posts, selected top {len(top_posts)}")
    print()
    
    # Step 2: Generate replies for each
    generator = LLMGenerator()
    
    if not generator.is_available:
        print("[ERROR] LLM not available - check API key")
        return
    
    for i, post in enumerate(top_posts, 1):
        author = post.get('author', post.get('username', 'unknown'))
        content = post.get('content', post.get('text', ''))
        score = post.get('opportunity_score', 0)
        
        if not content:
            continue
        
        print("=" * 60)
        print(f"POST {i}/{len(top_posts)} | @{author} | Opportunity: {score:.0f}/100")
        print("=" * 60)
        print()
        print(f'"{content[:280]}{"..." if len(content) > 280 else ""}"')
        print()
        print("-" * 40)
        print("GENERATED REPLIES:")
        print("-" * 40)
        
        try:
            replies = generator.generate_replies(
                original_post={"content": content, "author": author},
                platform=platform,
                num_replies=3
            )
            
            for j, reply in enumerate(replies, 1):
                if hasattr(reply, 'content'):
                    text = reply.content
                    hook = reply.hook_type or "none"
                    score = reply.combined_score
                    words = reply.word_count
                    chars = reply.char_count
                    strategy = reply.technique_label or "reply"
                else:
                    text = reply.get('content', '')
                    hook = reply.get('hook_type', 'none')
                    score = reply.get('combined_score', 0)
                    words = reply.get('word_count', 0)
                    chars = reply.get('char_count', 0)
                    strategy = reply.get('technique_label', 'reply')
                
                if "Error" in text:
                    print(f"\n  [ERROR] {text}")
                    continue
                
                print(f"\n  Reply {j} [{strategy.upper()}]:")
                print(f"    {text}")
                print(f"    [{words} words, {chars} chars | Hook: {hook} | Score: {score:.0f}%]")
            
        except Exception as e:
            print(f"  [ERROR] Generation failed: {e}")
        
        print()
    
    print("=" * 60)
    print("Done. Copy the replies you like and post them!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Auto-engage: scan and draft in one command")
    parser.add_argument("--limit", "-l", type=int, default=3, help="Number of posts to reply to")
    parser.add_argument("--category", "-c", type=str, default=None, 
                        help="Category filter (options, dealer_positioning, market_structure)")
    parser.add_argument("--platform", "-p", type=str, default="twitter", help="Target platform")
    
    args = parser.parse_args()
    
    auto_engage(limit=args.limit, category=args.category, platform=args.platform)


if __name__ == "__main__":
    main()
