"""
Capture Kit - Unified Social Media Collector
Orchestrates data collection from multiple platforms and methods.

Usage:
    # From data exports (recommended)
    collector = SocialCollector()
    collector.add_export("twitter", "/path/to/twitter-archive.zip")
    collector.add_export("linkedin", "/path/to/linkedin-export.zip")
    result = collector.analyze()
    
    # From direct scraping (requires Playwright)
    collector = SocialCollector()
    await collector.scrape("twitter", username="@yourhandle")
    await collector.scrape("linkedin")
    result = collector.analyze()
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import parsers
from .twitter_parser import parse_twitter_export
from .linkedin_parser import parse_linkedin_export
from .meta_parser import parse_instagram_export, parse_facebook_export
from .style_extractor import extract_social_style

# Try to import direct scraper (optional - requires playwright)
try:
    from .direct_scraper import SocialScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False


class SocialCollector:
    """
    Unified social media data collector.
    Supports both data exports and direct scraping.
    """
    
    SUPPORTED_PLATFORMS = ["twitter", "linkedin", "instagram", "facebook"]
    
    def __init__(self):
        self.platform_data: Dict[str, Dict] = {}
        self.scraper: Optional['SocialScraper'] = None
    
    # =========================================================================
    # DATA EXPORT METHODS (Recommended)
    # =========================================================================
    
    def add_export(self, platform: str, path: str) -> Dict[str, Any]:
        """
        Add data from an official platform export.
        
        Args:
            platform: One of "twitter", "linkedin", "instagram", "facebook"
            path: Path to the export ZIP file or extracted folder
        
        Returns:
            Parsed data summary
        """
        platform = platform.lower()
        
        if platform not in self.SUPPORTED_PLATFORMS:
            return {"error": f"Unsupported platform: {platform}. Supported: {self.SUPPORTED_PLATFORMS}"}
        
        # Verify path exists
        if not Path(path).exists():
            return {"error": f"Path not found: {path}"}
        
        # Parse based on platform
        if platform == "twitter":
            data = parse_twitter_export(path)
        elif platform == "linkedin":
            data = parse_linkedin_export(path)
        elif platform == "instagram":
            data = parse_instagram_export(path)
        elif platform == "facebook":
            data = parse_facebook_export(path)
        else:
            return {"error": f"Parser not implemented for: {platform}"}
        
        # Check for errors
        if "error" in data:
            return data
        
        # Store
        self.platform_data[platform] = data
        
        return {
            "status": "success",
            "platform": platform,
            "posts": data.get("total_posts", len(data.get("posts", []))),
            "profile": bool(data.get("profile"))
        }
    
    def add_exports_from_folder(self, folder: str) -> List[Dict[str, Any]]:
        """
        Auto-detect and add all exports from a folder.
        
        Args:
            folder: Folder containing export ZIP files
        
        Returns:
            List of results for each detected export
        """
        results = []
        folder_path = Path(folder)
        
        if not folder_path.is_dir():
            return [{"error": f"Not a folder: {folder}"}]
        
        # Look for ZIP files and folders that match platform names
        for item in folder_path.iterdir():
            name_lower = item.name.lower()
            
            # Detect platform from filename
            platform = None
            if 'twitter' in name_lower or 'x.com' in name_lower:
                platform = 'twitter'
            elif 'linkedin' in name_lower:
                platform = 'linkedin'
            elif 'instagram' in name_lower:
                platform = 'instagram'
            elif 'facebook' in name_lower:
                platform = 'facebook'
            
            if platform and (item.suffix == '.zip' or item.is_dir()):
                result = self.add_export(platform, str(item))
                result["source"] = item.name
                results.append(result)
        
        return results
    
    # =========================================================================
    # DIRECT SCRAPING METHODS (Requires Playwright)
    # =========================================================================
    
    async def scrape(
        self,
        platform: str,
        username: str = None,
        max_posts: int = 50,
        headless: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape data directly from a platform using logged-in browser.
        
        Args:
            platform: One of "twitter", "linkedin", "instagram"
            username: Username to scrape (your own)
            max_posts: Maximum posts to collect
            headless: If False, shows browser window for transparency
        
        Returns:
            Scraped data summary
        """
        if not SCRAPER_AVAILABLE:
            return {
                "error": "Playwright not installed. Run: pip install playwright && playwright install chromium"
            }
        
        platform = platform.lower()
        
        if platform not in ["twitter", "linkedin", "instagram"]:
            return {"error": f"Direct scraping not supported for: {platform}"}
        
        # Initialize scraper if needed
        if not self.scraper:
            self.scraper = SocialScraper(headless=headless)
            await self.scraper.start()
        
        # Scrape
        try:
            if platform == "twitter":
                if not username:
                    return {"error": "Username required for Twitter scraping"}
                data = await self.scraper.scrape_twitter(username, max_posts)
            
            elif platform == "linkedin":
                data = await self.scraper.scrape_linkedin(max_posts=max_posts)
            
            elif platform == "instagram":
                if not username:
                    return {"error": "Username required for Instagram scraping"}
                data = await self.scraper.scrape_instagram(username, max_posts)
            
            else:
                return {"error": f"Scraper not implemented for: {platform}"}
            
            # Check for errors
            if "error" in data:
                return data
            
            # Store
            self.platform_data[platform] = data
            
            return {
                "status": "success",
                "platform": platform,
                "posts": len(data.get("posts", [])),
                "profile": bool(data.get("profile"))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def close_scraper(self):
        """Close the browser scraper if open."""
        if self.scraper:
            await self.scraper.stop()
            self.scraper = None
    
    # =========================================================================
    # ANALYSIS METHODS
    # =========================================================================
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze all collected social media data.
        
        Returns:
            Comprehensive social media style analysis
        """
        if not self.platform_data:
            return {"error": "No data collected. Use add_export() or scrape() first."}
        
        # Prepare data for style extractor
        platform_list = []
        for platform, data in self.platform_data.items():
            platform_list.append({
                "platform": platform,
                "posts": data.get("posts", []),
                "profile": data.get("profile", {})
            })
        
        # Run analysis
        analysis = extract_social_style(platform_list)
        
        # Add profile summaries
        analysis["profiles"] = {}
        for platform, data in self.platform_data.items():
            analysis["profiles"][platform] = data.get("profile", {})
        
        # Add metadata
        analysis["collection_metadata"] = {
            "platforms_collected": list(self.platform_data.keys()),
            "analyzed_at": datetime.now().isoformat()
        }
        
        return analysis
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Get all posts from all platforms."""
        all_posts = []
        for platform, data in self.platform_data.items():
            for post in data.get("posts", []):
                post_copy = post.copy()
                post_copy["_platform"] = platform
                all_posts.append(post_copy)
        return all_posts
    
    def get_platform_data(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get raw data for a specific platform."""
        return self.platform_data.get(platform.lower())
    
    def export_to_file(self, path: str, include_raw: bool = False) -> str:
        """
        Export analysis to JSON file.
        
        Args:
            path: Output file path
            include_raw: If True, includes all raw post data (can be large)
        
        Returns:
            Path to created file
        """
        output = self.analyze()
        
        if include_raw:
            output["raw_data"] = self.platform_data
        
        path = Path(path)
        path.write_text(json.dumps(output, indent=2, default=str))
        
        return str(path)
    
    def summary(self) -> str:
        """Get a human-readable summary of collected data."""
        if not self.platform_data:
            return "No data collected yet."
        
        lines = ["Social Media Data Summary", "=" * 40]
        
        for platform, data in self.platform_data.items():
            posts = len(data.get("posts", []))
            profile = data.get("profile", {})
            name = profile.get("name") or profile.get("username") or "Unknown"
            
            lines.append(f"\n{platform.upper()}")
            lines.append(f"  Profile: {name}")
            lines.append(f"  Posts: {posts}")
            
            if platform == "twitter":
                lines.append(f"  Replies: {len(data.get('replies', []))}")
            elif platform == "linkedin":
                lines.append(f"  Skills: {len(data.get('skills', []))}")
                lines.append(f"  Positions: {len(data.get('positions', []))}")
        
        return "\n".join(lines)


# =========================================================================
# CONVENIENCE FUNCTIONS
# =========================================================================

def quick_analyze_export(platform: str, path: str) -> Dict[str, Any]:
    """
    Quickly analyze a single export file.
    
    Args:
        platform: Platform name
        path: Path to export
    
    Returns:
        Analysis results
    """
    collector = SocialCollector()
    result = collector.add_export(platform, path)
    
    if "error" in result:
        return result
    
    return collector.analyze()


def quick_analyze_folder(folder: str) -> Dict[str, Any]:
    """
    Analyze all exports in a folder.
    
    Args:
        folder: Folder containing exports
    
    Returns:
        Analysis results
    """
    collector = SocialCollector()
    results = collector.add_exports_from_folder(folder)
    
    # Check if any succeeded
    successes = [r for r in results if r.get("status") == "success"]
    if not successes:
        return {"error": "No valid exports found", "details": results}
    
    return collector.analyze()


# =========================================================================
# CLI INTERFACE
# =========================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect and analyze social media data")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Analyze data exports")
    export_parser.add_argument("--twitter", "-t", help="Twitter export ZIP")
    export_parser.add_argument("--linkedin", "-l", help="LinkedIn export ZIP")
    export_parser.add_argument("--instagram", "-i", help="Instagram export ZIP")
    export_parser.add_argument("--facebook", "-f", help="Facebook export ZIP")
    export_parser.add_argument("--folder", help="Folder with multiple exports")
    export_parser.add_argument("--output", "-o", help="Output JSON file")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape profiles directly")
    scrape_parser.add_argument("platform", choices=["twitter", "linkedin", "instagram"])
    scrape_parser.add_argument("--username", "-u", help="Username to scrape")
    scrape_parser.add_argument("--max-posts", "-n", type=int, default=50)
    scrape_parser.add_argument("--output", "-o", help="Output JSON file")
    scrape_parser.add_argument("--headless", action="store_true")
    
    args = parser.parse_args()
    
    if args.command == "export":
        collector = SocialCollector()
        
        # Add individual exports
        if args.twitter:
            print(f"Loading Twitter export: {args.twitter}")
            print(collector.add_export("twitter", args.twitter))
        if args.linkedin:
            print(f"Loading LinkedIn export: {args.linkedin}")
            print(collector.add_export("linkedin", args.linkedin))
        if args.instagram:
            print(f"Loading Instagram export: {args.instagram}")
            print(collector.add_export("instagram", args.instagram))
        if args.facebook:
            print(f"Loading Facebook export: {args.facebook}")
            print(collector.add_export("facebook", args.facebook))
        if args.folder:
            print(f"Loading exports from folder: {args.folder}")
            for result in collector.add_exports_from_folder(args.folder):
                print(f"  {result}")
        
        # Analyze
        print("\n" + collector.summary())
        
        analysis = collector.analyze()
        
        if args.output:
            collector.export_to_file(args.output)
            print(f"\nAnalysis saved to: {args.output}")
        else:
            print("\n" + json.dumps(analysis, indent=2, default=str))
    
    elif args.command == "scrape":
        async def run_scrape():
            collector = SocialCollector()
            
            result = await collector.scrape(
                args.platform,
                username=args.username,
                max_posts=args.max_posts,
                headless=args.headless
            )
            
            print(result)
            
            if result.get("status") == "success":
                analysis = collector.analyze()
                
                if args.output:
                    collector.export_to_file(args.output)
                    print(f"\nAnalysis saved to: {args.output}")
                else:
                    print("\n" + json.dumps(analysis, indent=2, default=str))
            
            await collector.close_scraper()
        
        asyncio.run(run_scrape())
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
