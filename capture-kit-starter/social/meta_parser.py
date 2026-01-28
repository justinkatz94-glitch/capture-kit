"""
Meta Platform Parsers (Instagram & Facebook)
Parses official data exports from Meta platforms.
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any


# =============================================================================
# INSTAGRAM PARSER
# =============================================================================

def parse_instagram_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse Instagram's data export ZIP file.

    Expected structure (JSON format):
    instagram-data/
    ├── personal_information/
    │   └── personal_information.json
    ├── content/
    │   └── posts_1.json
    ├── comments/
    │   └── post_comments.json
    └── ...
    """

    path = Path(zip_path)
    if not path.exists():
        return {"error": f"File not found: {zip_path}"}

    profile = {}
    posts = []
    comments = []

    try:
        if path.is_file() and path.suffix == '.zip':
            profile, posts, comments = _parse_instagram_zip(path)
        elif path.is_dir():
            profile, posts, comments = _parse_instagram_folder(path)
        else:
            return {"error": f"Unsupported file type: {path}"}

    except Exception as e:
        return {"error": f"Failed to parse Instagram export: {str(e)}"}

    return {
        "platform": "instagram",
        "profile": profile,
        "posts": posts,
        "comments": comments,
        "total_posts": len(posts),
        "total_comments": len(comments)
    }


def _parse_instagram_zip(zip_path: Path) -> tuple:
    """Parse Instagram ZIP file."""
    profile = {}
    posts = []
    comments = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            if not name.endswith('.json'):
                continue

            try:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue

            if 'personal_information.json' in name:
                profile = _parse_instagram_profile(data)

            elif 'posts_1.json' in name or 'content/posts' in name:
                posts.extend(_parse_instagram_posts(data))

            elif 'post_comments.json' in name:
                comments.extend(_parse_instagram_comments(data))

    return profile, posts, comments


def _parse_instagram_folder(folder_path: Path) -> tuple:
    """Parse extracted Instagram folder."""
    profile = {}
    posts = []
    comments = []

    for json_file in folder_path.rglob('*.json'):
        try:
            content = json_file.read_text(encoding='utf-8')
            data = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

        name = json_file.name

        if name == 'personal_information.json':
            profile = _parse_instagram_profile(data)

        elif 'posts' in name:
            posts.extend(_parse_instagram_posts(data))

        elif 'comments' in name:
            comments.extend(_parse_instagram_comments(data))

    return profile, posts, comments


def _parse_instagram_profile(data: Dict) -> Dict:
    """Parse Instagram profile data."""
    profile_user = data.get('profile_user', [{}])
    if isinstance(profile_user, list) and profile_user:
        pi = profile_user[0]
    else:
        pi = profile_user if isinstance(profile_user, dict) else {}

    return {
        "username": pi.get('username', ''),
        "name": pi.get('name', ''),
        "bio": pi.get('biography', '')
    }


def _parse_instagram_posts(data: Any) -> List[Dict]:
    """Parse Instagram posts data."""
    posts = []

    items = data if isinstance(data, list) else data.get('ig_posts', [])

    for post in items:
        # Instagram structure can vary
        media = post.get('media', [{}])[0] if post.get('media') else post

        content = media.get('title', media.get('caption', ''))
        timestamp = media.get('creation_timestamp', media.get('taken_at', ''))

        if content or timestamp:
            posts.append({
                "content": content,
                "timestamp": timestamp,
                "media_type": "image"
            })

    return posts


def _parse_instagram_comments(data: Any) -> List[Dict]:
    """Parse Instagram comments data."""
    comments = []

    items = data if isinstance(data, list) else data.get('comments_media_comments', [])

    for comment in items:
        string_data = comment.get('string_list_data', [{}])
        if string_data:
            first = string_data[0] if string_data else {}
            content = first.get('value', '')
            timestamp = first.get('timestamp', '')

            if content:
                comments.append({
                    "content": content,
                    "timestamp": timestamp
                })

    return comments


# =============================================================================
# FACEBOOK PARSER
# =============================================================================

def parse_facebook_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse Facebook's data export ZIP file.

    Expected structure:
    facebook-data/
    ├── profile_information/
    │   └── profile_information.json
    ├── posts/
    │   └── your_posts_1.json
    ├── comments_and_reactions/
    │   └── comments.json
    └── ...
    """

    path = Path(zip_path)
    if not path.exists():
        return {"error": f"File not found: {zip_path}"}

    profile = {}
    posts = []
    comments = []

    try:
        if path.is_file() and path.suffix == '.zip':
            profile, posts, comments = _parse_facebook_zip(path)
        elif path.is_dir():
            profile, posts, comments = _parse_facebook_folder(path)
        else:
            return {"error": f"Unsupported file type: {path}"}

    except Exception as e:
        return {"error": f"Failed to parse Facebook export: {str(e)}"}

    return {
        "platform": "facebook",
        "profile": profile,
        "posts": posts,
        "comments": comments,
        "total_posts": len(posts),
        "total_comments": len(comments)
    }


def _parse_facebook_zip(zip_path: Path) -> tuple:
    """Parse Facebook ZIP file."""
    profile = {}
    posts = []
    comments = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            if not name.endswith('.json'):
                continue

            try:
                content = zf.read(name).decode('utf-8')
                data = json.loads(content)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue

            if 'profile_information.json' in name:
                profile = _parse_facebook_profile(data)

            elif 'your_posts' in name:
                posts.extend(_parse_facebook_posts(data))

            elif 'comments.json' in name:
                comments.extend(_parse_facebook_comments(data))

    return profile, posts, comments


def _parse_facebook_folder(folder_path: Path) -> tuple:
    """Parse extracted Facebook folder."""
    profile = {}
    posts = []
    comments = []

    for json_file in folder_path.rglob('*.json'):
        try:
            content = json_file.read_text(encoding='utf-8')
            data = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

        name = json_file.name

        if name == 'profile_information.json':
            profile = _parse_facebook_profile(data)

        elif 'your_posts' in name:
            posts.extend(_parse_facebook_posts(data))

        elif name == 'comments.json':
            comments.extend(_parse_facebook_comments(data))

    return profile, posts, comments


def _parse_facebook_profile(data: Dict) -> Dict:
    """Parse Facebook profile data."""
    pi = data.get('profile_v2', data)

    name_data = pi.get('name', {})
    full_name = name_data.get('full_name', '') if isinstance(name_data, dict) else str(name_data)

    return {
        "name": full_name,
        "bio": pi.get('intro_bio', {}).get('text', '') if isinstance(pi.get('intro_bio'), dict) else '',
        "current_city": pi.get('current_city', {}).get('name', '') if isinstance(pi.get('current_city'), dict) else ''
    }


def _parse_facebook_posts(data: Any) -> List[Dict]:
    """Parse Facebook posts data."""
    posts = []

    items = data if isinstance(data, list) else []

    for post in items:
        # Extract text from various possible locations
        text = ''
        if 'data' in post:
            for item in post['data']:
                if 'post' in item:
                    text = item['post']
                    break

        content = text or post.get('title', '')
        timestamp = post.get('timestamp', '')

        if content or timestamp:
            posts.append({
                "content": content,
                "timestamp": timestamp,
                "attachments": len(post.get('attachments', []))
            })

    return posts


def _parse_facebook_comments(data: Any) -> List[Dict]:
    """Parse Facebook comments data."""
    comments = []

    items = data.get('comments_v2', data if isinstance(data, list) else [])

    for comment in items:
        comment_data = comment.get('comment', {})
        content = comment_data.get('comment', '') if isinstance(comment_data, dict) else ''
        timestamp = comment.get('timestamp', '')

        if content:
            comments.append({
                "content": content,
                "timestamp": timestamp
            })

    return comments


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        platform = sys.argv[1]
        path = sys.argv[2]

        if platform == 'instagram':
            result = parse_instagram_export(path)
        elif platform == 'facebook':
            result = parse_facebook_export(path)
        else:
            print(f"Unknown platform: {platform}")
            sys.exit(1)

        print(f"Parsed {platform} export:")
        print(f"  Profile: {result.get('profile', {})}")
        print(f"  Posts: {result.get('total_posts', 0)}")
        print(f"  Comments: {result.get('total_comments', 0)}")
