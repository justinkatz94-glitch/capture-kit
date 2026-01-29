#!/usr/bin/env python3
"""
LinkedIn Content Agent

A dedicated agent for generating LinkedIn content that combines:
1. User's voice profile (from prior posts across social media)
2. User's niche topics and expertise areas
3. Top LinkedIn performers' patterns in the user's niche

Usage:
    python linkedin_agent.py post --topic "gamma exposure"
    python linkedin_agent.py comment --url "linkedin.com/post/..." --content "original post"
    python linkedin_agent.py repurpose --content "twitter post to adapt"
    python linkedin_agent.py analyze --content "analyze this post"
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation.user_manager import get_active_profile, UserManager
from automation.linkedin_benchmark import LinkedInBenchmarkManager, get_generation_context
from automation.content_analyzer import ContentAnalyzer
from automation.platforms import get_adapter

# Check for Anthropic SDK
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LinkedInAgent:
    """
    LinkedIn content generation agent.

    Combines user voice, niche expertise, and top performer patterns
    to generate authentic, optimized LinkedIn content.
    """

    def __init__(self):
        """Initialize the LinkedIn agent."""
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

        # Load user profile
        self.profile = get_active_profile()
        if not self.profile:
            raise ValueError("No active user profile. Run: python automation_cli.py user create")

        self.user_name = self.profile.get("name", "Unknown")

        # Load LinkedIn benchmark
        self.benchmark_manager = LinkedInBenchmarkManager(self.user_name)
        self.benchmark_context = self.benchmark_manager.get_generation_context()

        # Get LinkedIn adapter for platform rules
        self.linkedin_adapter = get_adapter("linkedin")

        # Content analyzer
        self.analyzer = ContentAnalyzer()

    @property
    def is_available(self) -> bool:
        """Check if agent is ready."""
        return self.client is not None

    def _build_system_prompt(self) -> str:
        """Build the system prompt with user voice and benchmark data."""
        voice = self.profile.get("voice", {})
        niche = self.profile.get("niche", "")
        niche_topics = self.profile.get("niche_topics", [])

        # Get benchmark patterns
        has_benchmark = self.benchmark_context.get("has_data", False)

        prompt = f"""You are a LinkedIn content specialist writing as {self.user_name}.

## YOUR VOICE PROFILE

You write exactly like this person across all their social media:
- Tone: {voice.get('tone', 'professional')}
- Formality: {voice.get('formality', 'balanced')}
- Vocabulary: {voice.get('vocabulary', 'professional')}
- Emoji usage: {voice.get('emoji_style', 'minimal')}

Signature phrases to use naturally:
{json.dumps(voice.get('signature_phrases', []), indent=2)}

Phrases to AVOID:
{json.dumps(voice.get('avoided_phrases', []), indent=2)}

## NICHE & EXPERTISE

Primary niche: {niche}
Topics you're known for: {', '.join(niche_topics)}

You are an expert in these areas. Your content should demonstrate deep knowledge
while remaining accessible to your LinkedIn audience.

## LINKEDIN PLATFORM RULES

{self.linkedin_adapter.get_system_prompt_rules()}

Key LinkedIn best practices:
- First line is CRITICAL - it appears in the feed preview
- Use line breaks liberally for readability
- Optimal post length: 150-300 words (1200-1500 characters)
- Personal stories and lessons outperform generic advice
- Ask questions to drive engagement
- Avoid external links in the main post (algorithm penalty)
"""

        # Add benchmark data if available
        if has_benchmark:
            prompt += f"""
## BENCHMARK DATA FROM TOP PERFORMERS IN YOUR NICHE

Based on analysis of top LinkedIn creators in {niche}:

Optimal post length: {self.benchmark_context.get('optimal_length', {}).get('avg', 200)} words
Effective hooks: {', '.join(self.benchmark_context.get('effective_hooks', ['personal_story', 'question', 'contrarian']))}
Top topics: {', '.join(self.benchmark_context.get('top_topics', niche_topics))}

Style notes from top performers:
- Use line breaks: {'Yes' if self.benchmark_context.get('style_notes', {}).get('use_line_breaks') else 'Sparingly'}
- Use emoji: {'Yes' if self.benchmark_context.get('style_notes', {}).get('use_emoji') else 'No'}
- Use hashtags: {'Yes' if self.benchmark_context.get('style_notes', {}).get('use_hashtags') else 'No'}

Example high-performing posts in your niche:
"""
            for i, ex in enumerate(self.benchmark_context.get('examples', [])[:2], 1):
                prompt += f"""
{i}. @{ex.get('author', 'unknown')} ({ex.get('engagement', 0)} likes):
"{ex.get('content', '')[:300]}..."
"""
        else:
            prompt += """
## LINKEDIN BEST PRACTICES (No benchmark data yet)

Since you haven't added benchmark posts yet, follow these general best practices:
- Start with a hook that creates curiosity
- Use short paragraphs (1-2 sentences)
- Include a personal angle or story
- End with a question or call to discussion
- Keep it under 300 words for optimal engagement
"""

        prompt += """
## RULES

1. SOUND EXACTLY LIKE THE USER - match their tone, vocabulary, and style
2. NEVER use corporate jargon or LinkedIn cliches ("excited to announce", "thrilled", etc.)
3. Be specific - use concrete examples, numbers, and real experiences
4. Structure for mobile reading - short lines, clear breaks
5. The first line must hook the reader (it shows in the feed preview)
6. End with engagement - a question or invitation to discuss
7. Show expertise through insight, not credentials
8. Be authentic - LinkedIn rewards genuine voice over polished corporate speak
"""

        return prompt

    def generate_post(self, topic: str, hook_type: str = None) -> dict:
        """
        Generate an original LinkedIn post.

        Args:
            topic: Topic or theme for the post
            hook_type: Specific hook type (question, personal_story, contrarian, data, list)

        Returns:
            Dict with post content and metadata
        """
        if not self.is_available:
            return {"error": "API key not set. Run: setx ANTHROPIC_API_KEY 'your-key'"}

        system_prompt = self._build_system_prompt()

        hook_instruction = ""
        if hook_type:
            hook_instruction = f"\nUse a {hook_type.upper()} hook specifically."

        user_prompt = f"""Write an original LinkedIn post about: {topic}
{hook_instruction}

The post should:
1. Start with a compelling first line (this shows in the feed)
2. Share genuine insight or experience related to {topic}
3. Connect it to your expertise in {', '.join(self.profile.get('niche_topics', []))}
4. End with something that invites discussion

Provide your response as JSON:
{{
    "post": "your full post here with line breaks",
    "hook_type": "the hook type used",
    "first_line": "just the first line",
    "word_count": number,
    "engagement_prediction": "low/medium/high",
    "why": "why this post should resonate"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            response_text = response.content[0].text

            # Extract JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())

                # Analyze the post
                analysis = self.analyzer.analyze(result.get("post", ""), "linkedin")
                result["platform_score"] = analysis.platform_score
                result["char_count"] = len(result.get("post", ""))

                return result

            return {"error": "Could not parse response", "raw": response_text}

        except Exception as e:
            return {"error": str(e)}

    def generate_comment(self, original_content: str, author: str = "unknown") -> dict:
        """
        Generate a comment/reply to a LinkedIn post.

        Args:
            original_content: The post to reply to
            author: Author of the original post

        Returns:
            Dict with comment options
        """
        if not self.is_available:
            return {"error": "API key not set"}

        system_prompt = self._build_system_prompt()

        user_prompt = f"""Generate 3 comment options for this LinkedIn post.

ORIGINAL POST by {author}:
"{original_content}"

For LinkedIn comments:
- Be substantive, not just "Great post!"
- Add your perspective or experience
- Keep it focused (2-4 sentences ideal)
- Consider asking a follow-up question

Provide your response as JSON:
{{
    "comments": [
        {{
            "text": "comment text",
            "type": "amplify/question/perspective/personal",
            "why": "why this works"
        }}
    ]
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            response_text = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())

            return {"error": "Could not parse response"}

        except Exception as e:
            return {"error": str(e)}

    def repurpose_content(self, content: str, source_platform: str = "twitter") -> dict:
        """
        Repurpose content from another platform for LinkedIn.

        Args:
            content: Original content (e.g., a tweet or thread)
            source_platform: Where the content came from

        Returns:
            Dict with LinkedIn-optimized version
        """
        if not self.is_available:
            return {"error": "API key not set"}

        system_prompt = self._build_system_prompt()

        user_prompt = f"""Repurpose this {source_platform} content for LinkedIn.

ORIGINAL ({source_platform}):
"{content}"

Transform this into a LinkedIn post that:
1. Expands on the core idea (LinkedIn rewards depth)
2. Adds context and examples
3. Uses LinkedIn-appropriate formatting (line breaks, structure)
4. Maintains my voice and expertise positioning
5. Ends with engagement

Provide your response as JSON:
{{
    "linkedin_post": "the full LinkedIn version",
    "changes_made": ["list of key changes"],
    "word_count": number,
    "why": "why these changes improve it for LinkedIn"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            response_text = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())

            return {"error": "Could not parse response"}

        except Exception as e:
            return {"error": str(e)}

    def generate_article(self, topic: str, style: str = "educational") -> dict:
        """
        Generate a LinkedIn article with best practices.

        Args:
            topic: Article topic
            style: Article style (educational, case_study, opinion, how_to)

        Returns:
            Dict with article content and metadata
        """
        if not self.is_available:
            return {"error": "API key not set"}

        system_prompt = self._build_system_prompt()

        # Add article-specific best practices
        article_practices = """
## LINKEDIN ARTICLE BEST PRACTICES

LinkedIn articles are long-form content that:
- Rank in Google search (SEO opportunity)
- Stay on your profile permanently
- Demonstrate deep expertise
- Build authority in your niche

Structure for maximum impact:
1. HEADLINE: Clear, specific, benefit-driven (50-70 chars ideal)
2. HOOK: First 2-3 sentences must grab attention
3. BODY: Use headers (H2) to break sections, short paragraphs
4. EVIDENCE: Include data, examples, case studies
5. TAKEAWAYS: Actionable insights readers can use
6. CTA: End with engagement driver

Optimal length: 1500-2500 words (shows as 5-8 min read)
Use bullet points and numbered lists for scannability.
Include 1-2 relevant images if possible.
"""

        style_instructions = {
            "educational": "Teach the reader something valuable. Use clear explanations, examples, and step-by-step breakdowns.",
            "case_study": "Tell a story of a real situation with lessons learned. Include specific numbers and outcomes.",
            "opinion": "Take a clear stance on a topic. Support with evidence but own your perspective.",
            "how_to": "Provide a practical guide. Number the steps, explain the why behind each step.",
        }

        user_prompt = f"""Write a LinkedIn article about: {topic}

Style: {style.upper()} - {style_instructions.get(style, '')}

The article should demonstrate your expertise in {', '.join(self.profile.get('niche_topics', []))}.

{article_practices}

Provide your response as JSON:
{{
    "headline": "article headline (50-70 chars)",
    "hook": "first 2-3 sentences",
    "body": "full article body with ## headers for sections",
    "key_takeaways": ["list", "of", "takeaways"],
    "word_count": number,
    "read_time_minutes": number,
    "why": "why this article should perform well"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            response_text = response.content[0].text

            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())

                # Build full article
                full_article = f"# {result.get('headline', '')}\n\n"
                full_article += f"{result.get('hook', '')}\n\n"
                full_article += result.get('body', '')

                result['full_article'] = full_article
                return result

            return {"error": "Could not parse response"}

        except Exception as e:
            return {"error": str(e)}

    def analyze_post(self, content: str) -> dict:
        """
        Analyze a LinkedIn post for optimization opportunities.

        Args:
            content: Post content to analyze

        Returns:
            Analysis with scores and suggestions
        """
        analysis = self.analyzer.analyze(content, "linkedin")

        # Get platform-specific scoring
        platform_result = self.linkedin_adapter.score_platform_fit(content, "post")

        # Compare to benchmark
        benchmark_comparison = {}
        if self.benchmark_context.get("has_data"):
            optimal_length = self.benchmark_context.get("optimal_length", {}).get("avg", 200)
            benchmark_comparison = {
                "vs_optimal_length": f"{analysis.word_count} words (optimal: {optimal_length})",
                "uses_effective_hooks": analysis.hook_type in self.benchmark_context.get("effective_hooks", []),
                "matches_style": True,  # Could be more sophisticated
            }

        return {
            "word_count": analysis.word_count,
            "char_count": analysis.char_count,
            "hook_type": analysis.hook_type,
            "hook_strength": analysis.hook_strength,
            "platform_score": platform_result["score"],
            "issues": platform_result.get("issues", []),
            "strengths": analysis.strengths,
            "weaknesses": analysis.weaknesses,
            "benchmark_comparison": benchmark_comparison,
            "suggestions": analysis.weaknesses + platform_result.get("issues", []),
        }

    def get_status(self) -> dict:
        """Get agent status and configuration."""
        return {
            "user": self.user_name,
            "niche": self.profile.get("niche", ""),
            "niche_topics": self.profile.get("niche_topics", []),
            "api_available": self.is_available,
            "benchmark_data": self.benchmark_context.get("has_data", False),
            "benchmark_posts": self.benchmark_context.get("total_posts_analyzed", 0),
            "benchmark_accounts": self.benchmark_context.get("accounts_tracked", 0),
            "voice_configured": bool(self.profile.get("voice", {}).get("signature_phrases")),
        }


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Content Agent - Generate authentic LinkedIn content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s post --topic "gamma exposure and market structure"
  %(prog)s post --topic "options trading lessons" --hook personal_story
  %(prog)s comment --content "Original post text here" --author "John Doe"
  %(prog)s repurpose --content "Tweet to adapt" --source twitter
  %(prog)s analyze --content "Post to analyze"
  %(prog)s status
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Post command
    post_parser = subparsers.add_parser("post", help="Generate original LinkedIn post")
    post_parser.add_argument("--topic", "-t", required=True, help="Topic for the post")
    post_parser.add_argument("--hook", choices=["question", "personal_story", "contrarian", "data", "list", "bold_claim"],
                            help="Specific hook type to use")

    # Article command
    article_parser = subparsers.add_parser("article", help="Generate LinkedIn article")
    article_parser.add_argument("--topic", "-t", required=True, help="Article topic")
    article_parser.add_argument("--style", "-s", choices=["educational", "case_study", "opinion", "how_to"],
                                default="educational", help="Article style")

    # Comment command
    comment_parser = subparsers.add_parser("comment", help="Generate comment on a post")
    comment_parser.add_argument("--content", "-c", required=True, help="Original post content")
    comment_parser.add_argument("--author", "-a", default="unknown", help="Original post author")

    # Repurpose command
    repurpose_parser = subparsers.add_parser("repurpose", help="Repurpose content for LinkedIn")
    repurpose_parser.add_argument("--content", "-c", required=True, help="Content to repurpose")
    repurpose_parser.add_argument("--source", "-s", default="twitter", help="Source platform")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a LinkedIn post")
    analyze_parser.add_argument("--content", "-c", required=True, help="Post to analyze")

    # Status command
    subparsers.add_parser("status", help="Show agent status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize agent
    try:
        agent = LinkedInAgent()
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # Route commands
    if args.command == "status":
        status = agent.get_status()
        print("LinkedIn Agent Status")
        print("=" * 50)
        print(f"User: {status['user']}")
        print(f"Niche: {status['niche']}")
        print(f"Topics: {', '.join(status['niche_topics'])}")
        print()
        print(f"API Available: {'Yes' if status['api_available'] else 'No'}")
        print(f"Voice Configured: {'Yes' if status['voice_configured'] else 'No'}")
        print(f"Benchmark Data: {'Yes' if status['benchmark_data'] else 'No'}")
        if status['benchmark_data']:
            print(f"  - Posts analyzed: {status['benchmark_posts']}")
            print(f"  - Accounts tracked: {status['benchmark_accounts']}")

    elif args.command == "post":
        if not agent.is_available:
            print("[ERROR] ANTHROPIC_API_KEY not set")
            return

        print(f"Generating LinkedIn post about: {args.topic}")
        print("-" * 50)

        result = agent.generate_post(args.topic, args.hook)

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        print()
        print(result.get("post", ""))
        print()
        print("-" * 50)
        print(f"Hook: {result.get('hook_type', 'unknown')}")
        print(f"Words: {result.get('word_count', 0)} | Chars: {result.get('char_count', 0)}")
        print(f"Platform Score: {result.get('platform_score', 0):.0f}%")
        print(f"Engagement Prediction: {result.get('engagement_prediction', 'unknown')}")
        print()
        print(f"Why: {result.get('why', '')}")

    elif args.command == "article":
        if not agent.is_available:
            print("[ERROR] ANTHROPIC_API_KEY not set")
            return

        print(f"Generating LinkedIn article about: {args.topic}")
        print(f"Style: {args.style}")
        print("-" * 50)

        result = agent.generate_article(args.topic, args.style)

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        print()
        print(f"# {result.get('headline', '')}")
        print()
        print(result.get('hook', ''))
        print()
        # Print body with ASCII-safe encoding
        body = result.get('body', '').encode('ascii', 'replace').decode('ascii')
        print(body[:2000])
        if len(result.get('body', '')) > 2000:
            print("\n... [truncated for display]")
        print()
        print("-" * 50)
        print(f"Words: {result.get('word_count', 0)} | Read time: {result.get('read_time_minutes', 0)} min")
        print()
        print("Key takeaways:")
        for takeaway in result.get('key_takeaways', [])[:5]:
            print(f"  - {takeaway}")
        print()
        print(f"Why: {result.get('why', '')}")

    elif args.command == "comment":
        if not agent.is_available:
            print("[ERROR] ANTHROPIC_API_KEY not set")
            return

        print(f"Generating comments for post by @{args.author}")
        print("-" * 50)

        result = agent.generate_comment(args.content, args.author)

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        for i, comment in enumerate(result.get("comments", []), 1):
            print(f"\nOption {i} [{comment.get('type', 'comment').upper()}]:")
            print(f"  {comment.get('text', '')}")
            print(f"  Why: {comment.get('why', '')}")

    elif args.command == "repurpose":
        if not agent.is_available:
            print("[ERROR] ANTHROPIC_API_KEY not set")
            return

        print(f"Repurposing {args.source} content for LinkedIn...")
        print("-" * 50)

        result = agent.repurpose_content(args.content, args.source)

        if "error" in result:
            print(f"[ERROR] {result['error']}")
            return

        print()
        post_text = result.get("linkedin_post", "").encode('ascii', 'replace').decode('ascii')
        print(post_text)
        print()
        print("-" * 50)
        print(f"Words: {result.get('word_count', 0)}")
        changes = [c.encode('ascii', 'replace').decode('ascii') for c in result.get('changes_made', [])]
        print(f"Changes: {', '.join(changes)}")
        print(f"Why: {result.get('why', '')}")

    elif args.command == "analyze":
        print("Analyzing LinkedIn post...")
        print("-" * 50)

        result = agent.analyze_post(args.content)

        print(f"\nWords: {result['word_count']} | Chars: {result['char_count']}")
        print(f"Hook: {result['hook_type'] or 'none'} (strength: {result['hook_strength']:.0%})")
        print(f"Platform Score: {result['platform_score']}%")

        if result.get('strengths'):
            print("\nStrengths:")
            for s in result['strengths']:
                print(f"  + {s}")

        if result.get('issues'):
            print("\nIssues:")
            for issue in result['issues']:
                print(f"  - {issue}")

        if result.get('benchmark_comparison'):
            print("\nVs Benchmark:")
            bc = result['benchmark_comparison']
            print(f"  Length: {bc.get('vs_optimal_length', 'N/A')}")
            print(f"  Uses effective hook: {'Yes' if bc.get('uses_effective_hooks') else 'No'}")


if __name__ == "__main__":
    main()
