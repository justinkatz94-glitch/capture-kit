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
    
    async def scrape_twitter(self, username: str, max_posts: int = 100) -> Dict[str, Any]:
        """
        Scrape Twitter/X profile.
        
        Args:
            username: Twitter username (with or without @)
            max_posts: Maximum number of posts to collect
        """
        username = username.lstrip('@')
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
    
    args = parser.parse_args()
    
    scraper = SocialScraper(headless=args.headless)
    
    try:
        await scraper.start()
        
        if args.platform == "twitter":
            if not args.username:
                print("Error: --username required for Twitter")
                return
            result = await scraper.scrape_twitter(args.username, args.max_posts)
        
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
