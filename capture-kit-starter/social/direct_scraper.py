"""
Direct Social Media Profile Scraper
Uses Playwright to scrape user's OWN profile from their logged-in browser session.

This scraper:
1. Opens a visible browser window (user sees everything)
2. User logs in manually (we never touch credentials)
3. Navigates to their profile and extracts posts
4. User watches the entire process (full transparency)

Supported platforms:
- Twitter/X
- LinkedIn
- Instagram (requires login)

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class SocialScraper:
    """
    Transparent social media scraper that uses user's logged-in session.
    """
    
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        """
        Args:
            headless: If False (default), shows browser window for transparency
            slow_mo: Milliseconds to wait between actions (so user can watch)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed. Run: pip install playwright && playwright install chromium")
        
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def start(self):
        """Start the browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.page = await self.browser.new_page()
        
        # Set reasonable viewport
        await self.page.set_viewport_size({"width": 1280, "height": 800})
    
    async def stop(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def wait_for_login(self, url: str, check_selector: str, timeout: int = 300):
        """
        Navigate to URL and wait for user to log in.
        
        Args:
            url: Login page URL
            check_selector: CSS selector that appears when logged in
            timeout: Max seconds to wait for login
        """
        await self.page.goto(url)
        print(f"Please log in to your account. Waiting up to {timeout} seconds...")
        
        try:
            await self.page.wait_for_selector(check_selector, timeout=timeout * 1000)
            print("Login detected! Proceeding with scrape...")
            return True
        except Exception:
            print("Login timeout. Please try again.")
            return False
    
    # =========================================================================
    # TWITTER/X SCRAPER
    # =========================================================================

    # List of Nitter instances to try (public Twitter frontends, no login required)
    NITTER_INSTANCES = [
        "https://nitter.net",
        "https://nitter.poast.org",
        "https://nitter.cz",
        "https://nitter.privacydev.net",
        "https://nitter.1d4.us",
    ]

    async def scrape_twitter(self, username: str, max_posts: int = 100, use_nitter: bool = True) -> Dict[str, Any]:
        """
        Scrape Twitter/X profile.

        Args:
            username: Twitter username (with or without @)
            max_posts: Maximum number of posts to collect
            use_nitter: If True, use Nitter (no login required). If False, use Twitter directly.
        """
        username = username.lstrip('@')

        if use_nitter:
            return await self._scrape_twitter_via_nitter(username, max_posts)

        profile_url = f"https://x.com/{username}"

        # Navigate to profile
        await self.page.goto(profile_url)
        await self.page.wait_for_timeout(2000)

        # Check if logged in by looking for compose button
        is_logged_in = await self.page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
        if not is_logged_in:
            print("Not logged in. Please log in first.")
            if not await self.wait_for_login(
                "https://x.com/login",
                '[data-testid="SideNav_NewTweet_Button"]'
            ):
                return {"error": "Login required"}
            await self.page.goto(profile_url)
            await self.page.wait_for_timeout(2000)

        # Extract profile info
        profile = await self._extract_twitter_profile()

        # Scroll and collect tweets
        tweets = await self._collect_twitter_tweets(max_posts)

        return {
            "platform": "twitter",
            "username": username,
            "profile": profile,
            "posts": tweets,
            "total_posts": len(tweets),
            "scraped_at": datetime.now().isoformat()
        }

    async def _scrape_twitter_via_nitter(self, username: str, max_posts: int) -> Dict[str, Any]:
        """
        Scrape Twitter profile via Nitter or public API (no login required).
        """
        # First, try the syndication API (most reliable, no browser needed)
        print("Trying Twitter syndication API...")
        try:
            from .twitter_public_scraper import fetch_twitter_profile
            result = fetch_twitter_profile(username, max_posts)
            if "error" not in result:
                print(f"Successfully fetched {result.get('total_posts', 0)} tweets via syndication API")
                return result
            print(f"Syndication API failed: {result.get('error')}")
        except Exception as e:
            print(f"Syndication API error: {e}")

        # Fallback to Nitter instances
        working_instance = None
        for instance in self.NITTER_INSTANCES:
            try:
                profile_url = f"{instance}/{username}"
                print(f"Trying Nitter instance: {instance}")
                response = await self.page.goto(profile_url, timeout=15000)
                await self.page.wait_for_timeout(2000)

                # Check if page loaded successfully
                if response and response.status == 200:
                    # Check for error messages
                    error_el = await self.page.query_selector('.error-panel, .error-page')
                    if not error_el:
                        working_instance = instance
                        print(f"Using Nitter instance: {instance}")
                        break
            except Exception as e:
                print(f"Instance {instance} failed: {e}")
                continue

        if not working_instance:
            return {"error": "All methods failed. Try again later or use official Twitter data export."}

        # Check for user not found
        not_found = await self.page.query_selector('.error-panel')
        if not_found:
            error_text = await not_found.inner_text()
            print(f"Error from Nitter: {error_text}")
            return {"error": f"User not found or Nitter error: {error_text}"}

        # Extract profile info from Nitter
        profile = await self._extract_nitter_profile()
        print(f"Profile extracted: {profile}")

        # Collect tweets from Nitter
        tweets = await self._collect_nitter_tweets(max_posts)
        print(f"Tweets collected: {len(tweets)}")

        return {
            "platform": "twitter",
            "username": username,
            "profile": profile,
            "posts": tweets,
            "total_posts": len(tweets),
            "scraped_at": datetime.now().isoformat(),
            "source": "nitter"
        }

    async def _extract_nitter_profile(self) -> Dict[str, str]:
        """Extract profile information from Nitter page."""
        profile = {}

        try:
            # Name
            name_el = await self.page.query_selector('.profile-card-fullname')
            if name_el:
                profile["name"] = await name_el.inner_text()

            # Username
            username_el = await self.page.query_selector('.profile-card-username')
            if username_el:
                profile["username"] = await username_el.inner_text()

            # Bio
            bio_el = await self.page.query_selector('.profile-bio')
            if bio_el:
                profile["bio"] = await bio_el.inner_text()

            # Location
            loc_el = await self.page.query_selector('.profile-location')
            if loc_el:
                profile["location"] = await loc_el.inner_text()

            # Stats
            stats = await self.page.query_selector_all('.profile-stat-num')
            stat_labels = await self.page.query_selector_all('.profile-stat-header')
            for i, (stat, label) in enumerate(zip(stats, stat_labels)):
                label_text = (await label.inner_text()).lower().strip()
                stat_text = await stat.inner_text()
                if 'tweet' in label_text:
                    profile["tweets"] = stat_text
                elif 'following' in label_text:
                    profile["following"] = stat_text
                elif 'follower' in label_text:
                    profile["followers"] = stat_text
                elif 'like' in label_text:
                    profile["likes"] = stat_text

        except Exception as e:
            profile["_error"] = str(e)

        return profile

    async def _collect_nitter_tweets(self, max_posts: int) -> List[Dict]:
        """Scroll and collect tweets from Nitter."""
        tweets = []
        seen_content = set()
        scroll_attempts = 0
        max_scroll_attempts = 20

        while len(tweets) < max_posts and scroll_attempts < max_scroll_attempts:
            # Get all timeline items
            tweet_elements = await self.page.query_selector_all('.timeline-item')

            for tweet_el in tweet_elements:
                try:
                    # Skip retweets if they have a retweet indicator
                    retweet_el = await tweet_el.query_selector('.retweet-header')
                    is_retweet = retweet_el is not None

                    # Extract tweet content
                    content_el = await tweet_el.query_selector('.tweet-content')
                    content = await content_el.inner_text() if content_el else ""

                    # Skip if already seen
                    if content in seen_content or not content.strip():
                        continue
                    seen_content.add(content)

                    # Extract timestamp
                    time_el = await tweet_el.query_selector('.tweet-date a')
                    timestamp_text = await time_el.get_attribute('title') if time_el else None
                    tweet_link = await time_el.get_attribute('href') if time_el else None

                    # Extract stats
                    stats = {}
                    stat_container = await tweet_el.query_selector('.tweet-stats')
                    if stat_container:
                        stat_spans = await stat_container.query_selector_all('.tweet-stat')
                        for stat_span in stat_spans:
                            icon = await stat_span.query_selector('.icon-container')
                            if icon:
                                icon_class = await icon.get_attribute('class') or ""
                                value_el = await stat_span.query_selector('.tweet-stat-num')
                                value = await value_el.inner_text() if value_el else "0"

                                if 'comment' in icon_class or 'reply' in icon_class:
                                    stats['replies'] = value
                                elif 'retweet' in icon_class:
                                    stats['retweets'] = value
                                elif 'heart' in icon_class or 'like' in icon_class:
                                    stats['likes'] = value
                                elif 'quote' in icon_class:
                                    stats['quotes'] = value

                    tweets.append({
                        "content": content,
                        "timestamp": timestamp_text,
                        "is_retweet": is_retweet,
                        "replies": stats.get("replies", "0"),
                        "retweets": stats.get("retweets", "0"),
                        "likes": stats.get("likes", "0"),
                        "quotes": stats.get("quotes", "0"),
                    })

                    if len(tweets) >= max_posts:
                        break

                except Exception:
                    continue

            # Try to load more by clicking "Load more" or scrolling
            load_more = await self.page.query_selector('.show-more a')
            if load_more and len(tweets) < max_posts:
                try:
                    await load_more.click()
                    await self.page.wait_for_timeout(2000)
                except:
                    # Fall back to scrolling
                    await self.page.evaluate("window.scrollBy(0, 1000)")
                    await self.page.wait_for_timeout(1500)
            else:
                await self.page.evaluate("window.scrollBy(0, 1000)")
                await self.page.wait_for_timeout(1500)

            scroll_attempts += 1

        return tweets
    
    async def _extract_twitter_profile(self) -> Dict[str, str]:
        """Extract Twitter profile information from current page."""
        profile = {}
        
        try:
            # Name
            name_el = await self.page.query_selector('[data-testid="UserName"] span')
            if name_el:
                profile["name"] = await name_el.inner_text()
            
            # Bio
            bio_el = await self.page.query_selector('[data-testid="UserDescription"]')
            if bio_el:
                profile["bio"] = await bio_el.inner_text()
            
            # Location
            loc_el = await self.page.query_selector('[data-testid="UserLocation"]')
            if loc_el:
                profile["location"] = await loc_el.inner_text()
            
            # Stats (followers, following)
            stats = await self.page.query_selector_all('[href*="/followers"], [href*="/following"]')
            for stat in stats:
                text = await stat.inner_text()
                if "Following" in text:
                    profile["following"] = text.replace("Following", "").strip()
                elif "Followers" in text:
                    profile["followers"] = text.replace("Followers", "").strip()
            
        except Exception as e:
            profile["_error"] = str(e)
        
        return profile
    
    async def _collect_twitter_tweets(self, max_posts: int) -> List[Dict]:
        """Scroll and collect tweets."""
        tweets = []
        seen_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 50
        
        while len(tweets) < max_posts and scroll_attempts < max_scroll_attempts:
            # Get all tweet articles on page
            tweet_elements = await self.page.query_selector_all('article[data-testid="tweet"]')
            
            for tweet_el in tweet_elements:
                try:
                    # Get tweet ID from link
                    link = await tweet_el.query_selector('a[href*="/status/"]')
                    if not link:
                        continue
                    
                    href = await link.get_attribute('href')
                    tweet_id = href.split('/status/')[-1].split('/')[0].split('?')[0]
                    
                    if tweet_id in seen_ids:
                        continue
                    seen_ids.add(tweet_id)
                    
                    # Extract tweet content
                    content_el = await tweet_el.query_selector('[data-testid="tweetText"]')
                    content = await content_el.inner_text() if content_el else ""
                    
                    # Extract timestamp
                    time_el = await tweet_el.query_selector('time')
                    timestamp = await time_el.get_attribute('datetime') if time_el else None
                    
                    # Extract engagement metrics
                    metrics = {}
                    for metric in ['reply', 'retweet', 'like']:
                        metric_el = await tweet_el.query_selector(f'[data-testid="{metric}"]')
                        if metric_el:
                            metric_text = await metric_el.inner_text()
                            metrics[metric] = metric_text if metric_text else "0"
                    
                    tweets.append({
                        "id": tweet_id,
                        "content": content,
                        "timestamp": timestamp,
                        "replies": metrics.get("reply", "0"),
                        "retweets": metrics.get("retweet", "0"),
                        "likes": metrics.get("like", "0"),
                        "url": f"https://x.com/i/status/{tweet_id}"
                    })
                    
                    if len(tweets) >= max_posts:
                        break
                        
                except Exception:
                    continue
            
            # Scroll down
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await self.page.wait_for_timeout(1500)
            scroll_attempts += 1
        
        return tweets
    
    # =========================================================================
    # LINKEDIN SCRAPER
    # =========================================================================
    
    async def scrape_linkedin(self, profile_url: str = None, max_posts: int = 50) -> Dict[str, Any]:
        """
        Scrape LinkedIn profile and activity.
        
        Args:
            profile_url: LinkedIn profile URL (or None to scrape logged-in user)
            max_posts: Maximum number of posts to collect
        """
        # Start at LinkedIn
        await self.page.goto("https://www.linkedin.com/feed/")
        await self.page.wait_for_timeout(2000)
        
        # Check if logged in
        is_logged_in = await self.page.query_selector('.global-nav__me-photo')
        if not is_logged_in:
            print("Not logged in. Please log in first.")
            if not await self.wait_for_login(
                "https://www.linkedin.com/login",
                '.global-nav__me-photo'
            ):
                return {"error": "Login required"}
        
        # Navigate to profile if URL provided, otherwise find own profile
        if profile_url:
            await self.page.goto(profile_url)
        else:
            # Click on "Me" and go to profile
            me_button = await self.page.query_selector('.global-nav__me-photo')
            if me_button:
                await me_button.click()
                await self.page.wait_for_timeout(1000)
                
                view_profile = await self.page.query_selector('a:has-text("View Profile")')
                if view_profile:
                    await view_profile.click()
        
        await self.page.wait_for_timeout(2000)
        
        # Extract profile
        profile = await self._extract_linkedin_profile()
        
        # Navigate to activity/posts
        activity_url = self.page.url.rstrip('/') + '/recent-activity/all/'
        await self.page.goto(activity_url)
        await self.page.wait_for_timeout(2000)
        
        # Collect posts
        posts = await self._collect_linkedin_posts(max_posts)
        
        return {
            "platform": "linkedin",
            "profile": profile,
            "posts": posts,
            "total_posts": len(posts),
            "scraped_at": datetime.now().isoformat()
        }
    
    async def _extract_linkedin_profile(self) -> Dict[str, str]:
        """Extract LinkedIn profile information."""
        profile = {}
        
        try:
            # Name
            name_el = await self.page.query_selector('h1.text-heading-xlarge')
            if name_el:
                profile["name"] = await name_el.inner_text()
            
            # Headline
            headline_el = await self.page.query_selector('.text-body-medium')
            if headline_el:
                profile["headline"] = await headline_el.inner_text()
            
            # Location
            loc_el = await self.page.query_selector('.text-body-small.inline')
            if loc_el:
                profile["location"] = await loc_el.inner_text()
            
            # About section
            about_section = await self.page.query_selector('#about ~ .display-flex span[aria-hidden="true"]')
            if about_section:
                profile["about"] = await about_section.inner_text()
                
        except Exception as e:
            profile["_error"] = str(e)
        
        return profile
    
    async def _collect_linkedin_posts(self, max_posts: int) -> List[Dict]:
        """Scroll and collect LinkedIn posts."""
        posts = []
        scroll_attempts = 0
        max_scroll_attempts = 30
        
        while len(posts) < max_posts and scroll_attempts < max_scroll_attempts:
            # Get all post containers
            post_elements = await self.page.query_selector_all('.feed-shared-update-v2')
            
            for post_el in post_elements:
                if len(posts) >= max_posts:
                    break
                    
                try:
                    # Extract text content
                    content_el = await post_el.query_selector('.feed-shared-update-v2__description')
                    content = ""
                    if content_el:
                        content = await content_el.inner_text()
                    
                    # Skip if no content or already seen
                    if not content.strip() or content in [p['content'] for p in posts]:
                        continue
                    
                    # Extract timestamp
                    time_el = await post_el.query_selector('.update-components-actor__sub-description span')
                    timestamp = await time_el.inner_text() if time_el else ""
                    
                    posts.append({
                        "content": content.strip(),
                        "timestamp_text": timestamp,
                        "timestamp": None  # LinkedIn shows relative time
                    })
                    
                except Exception:
                    continue
            
            # Scroll
            await self.page.evaluate("window.scrollBy(0, 800)")
            await self.page.wait_for_timeout(2000)
            scroll_attempts += 1
        
        return posts
    
    # =========================================================================
    # INSTAGRAM SCRAPER
    # =========================================================================
    
    async def scrape_instagram(self, username: str, max_posts: int = 50) -> Dict[str, Any]:
        """
        Scrape Instagram profile.
        
        Args:
            username: Instagram username
            max_posts: Maximum number of posts to collect
        """
        profile_url = f"https://www.instagram.com/{username}/"
        
        await self.page.goto(profile_url)
        await self.page.wait_for_timeout(2000)
        
        # Check if logged in (Instagram blocks most content without login)
        login_button = await self.page.query_selector('a[href="/accounts/login/"]')
        if login_button:
            print("Not logged in. Please log in first.")
            if not await self.wait_for_login(
                "https://www.instagram.com/accounts/login/",
                'svg[aria-label="Home"]'
            ):
                return {"error": "Login required"}
            await self.page.goto(profile_url)
            await self.page.wait_for_timeout(2000)
        
        # Extract profile
        profile = await self._extract_instagram_profile()
        
        # Collect posts by clicking into them
        posts = await self._collect_instagram_posts(max_posts)
        
        return {
            "platform": "instagram",
            "username": username,
            "profile": profile,
            "posts": posts,
            "total_posts": len(posts),
            "scraped_at": datetime.now().isoformat()
        }
    
    async def _extract_instagram_profile(self) -> Dict[str, str]:
        """Extract Instagram profile information."""
        profile = {}
        
        try:
            # Name
            name_el = await self.page.query_selector('header section span')
            if name_el:
                profile["name"] = await name_el.inner_text()
            
            # Bio
            bio_el = await self.page.query_selector('header section > div > span')
            if bio_el:
                profile["bio"] = await bio_el.inner_text()
            
            # Stats
            stats = await self.page.query_selector_all('header section ul li span')
            stat_names = ["posts", "followers", "following"]
            for i, stat in enumerate(stats[:3]):
                text = await stat.inner_text()
                if i < len(stat_names):
                    profile[stat_names[i]] = text
                    
        except Exception as e:
            profile["_error"] = str(e)
        
        return profile
    
    async def _collect_instagram_posts(self, max_posts: int) -> List[Dict]:
        """Collect Instagram posts by clicking into each one."""
        posts = []
        
        # Get all post links on the profile
        post_links = await self.page.query_selector_all('article a[href*="/p/"]')
        
        for link in post_links[:max_posts]:
            try:
                href = await link.get_attribute('href')
                post_url = f"https://www.instagram.com{href}"
                
                # Navigate to post
                await self.page.goto(post_url)
                await self.page.wait_for_timeout(1500)
                
                # Extract caption
                caption_el = await self.page.query_selector('article span._ap3a')
                caption = await caption_el.inner_text() if caption_el else ""
                
                # Extract timestamp
                time_el = await self.page.query_selector('time')
                timestamp = await time_el.get_attribute('datetime') if time_el else None
                
                # Extract likes
                likes_el = await self.page.query_selector('section span')
                likes = await likes_el.inner_text() if likes_el else "0"
                
                posts.append({
                    "url": post_url,
                    "content": caption,
                    "timestamp": timestamp,
                    "likes": likes
                })
                
            except Exception:
                continue
            
            # Go back to profile
            await self.page.go_back()
            await self.page.wait_for_timeout(1000)
        
        return posts


# =========================================================================
# CLI INTERFACE
# =========================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape your own social media profiles")
    parser.add_argument("platform", choices=["twitter", "linkedin", "instagram"])
    parser.add_argument("--username", "-u", help="Username to scrape (your own)")
    parser.add_argument("--max-posts", "-n", type=int, default=50, help="Max posts to collect")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--headless", action="store_true", help="Run without visible browser")
    parser.add_argument("--no-nitter", action="store_true", help="Use Twitter directly instead of Nitter (requires login)")

    args = parser.parse_args()

    scraper = SocialScraper(headless=args.headless)

    try:
        await scraper.start()

        if args.platform == "twitter":
            if not args.username:
                print("Error: --username required for Twitter")
                return
            use_nitter = not args.no_nitter
            result = await scraper.scrape_twitter(args.username, args.max_posts, use_nitter=use_nitter)
        
        elif args.platform == "linkedin":
            result = await scraper.scrape_linkedin(max_posts=args.max_posts)
        
        elif args.platform == "instagram":
            if not args.username:
                print("Error: --username required for Instagram")
                return
            result = await scraper.scrape_instagram(args.username, args.max_posts)
        
        # Output
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2))
            print(f"Saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
            
    finally:
        await scraper.stop()


if __name__ == "__main__":
    asyncio.run(main())
