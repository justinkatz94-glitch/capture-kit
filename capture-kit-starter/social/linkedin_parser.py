"""
LinkedIn Data Export Parser
Parses LinkedIn's official data export ZIP file.
"""

import json
import csv
import zipfile
from pathlib import Path
from typing import Dict, List, Any
from io import StringIO


def parse_linkedin_export(zip_path: str) -> Dict[str, Any]:
    """
    Parse LinkedIn's data export ZIP file.

    Expected structure:
    Basic_LinkedInDataExport/
    ├── Profile.csv
    ├── Positions.csv
    ├── Skills.csv
    ├── Connections.csv
    ├── Messages.csv (if requested)
    └── ...
    """

    path = Path(zip_path)
    if not path.exists():
        return {"error": f"File not found: {zip_path}"}

    profile = {}
    positions = []
    skills = []
    posts = []

    try:
        if path.is_file() and path.suffix == '.zip':
            profile, positions, skills, posts = _parse_zip(path)
        elif path.is_dir():
            profile, positions, skills, posts = _parse_folder(path)
        else:
            return {"error": f"Unsupported file type: {path}"}

    except Exception as e:
        return {"error": f"Failed to parse LinkedIn export: {str(e)}"}

    return {
        "platform": "linkedin",
        "profile": profile,
        "positions": positions,
        "skills": skills,
        "posts": posts,
        "total_posts": len(posts)
    }


def _parse_zip(zip_path: Path) -> tuple:
    """Parse a ZIP file."""
    profile = {}
    positions = []
    skills = []
    posts = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            try:
                content = zf.read(name).decode('utf-8')
            except UnicodeDecodeError:
                content = zf.read(name).decode('utf-8', errors='ignore')

            if 'Profile.csv' in name:
                profile = _parse_profile_csv(content)

            elif 'Positions.csv' in name:
                positions = _parse_positions_csv(content)

            elif 'Skills.csv' in name:
                skills = _parse_skills_csv(content)

            elif 'Shares.csv' in name or 'Posts.csv' in name:
                posts = _parse_posts_csv(content)

    return profile, positions, skills, posts


def _parse_folder(folder_path: Path) -> tuple:
    """Parse an extracted folder."""
    profile = {}
    positions = []
    skills = []
    posts = []

    for csv_file in folder_path.rglob('*.csv'):
        content = csv_file.read_text(encoding='utf-8', errors='ignore')
        name = csv_file.name

        if name == 'Profile.csv':
            profile = _parse_profile_csv(content)
        elif name == 'Positions.csv':
            positions = _parse_positions_csv(content)
        elif name == 'Skills.csv':
            skills = _parse_skills_csv(content)
        elif name in ['Shares.csv', 'Posts.csv']:
            posts = _parse_posts_csv(content)

    return profile, positions, skills, posts


def _parse_profile_csv(content: str) -> Dict:
    """Parse Profile.csv content."""
    reader = csv.DictReader(StringIO(content))

    for row in reader:
        return {
            "first_name": row.get('First Name', ''),
            "last_name": row.get('Last Name', ''),
            "headline": row.get('Headline', ''),
            "summary": row.get('Summary', ''),
            "industry": row.get('Industry', ''),
            "name": f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
        }

    return {}


def _parse_positions_csv(content: str) -> List[Dict]:
    """Parse Positions.csv content."""
    positions = []
    reader = csv.DictReader(StringIO(content))

    for row in reader:
        positions.append({
            "company": row.get('Company Name', ''),
            "title": row.get('Title', ''),
            "start_date": row.get('Started On', ''),
            "end_date": row.get('Finished On', ''),
            "description": row.get('Description', '')
        })

    return positions


def _parse_skills_csv(content: str) -> List[str]:
    """Parse Skills.csv content."""
    skills = []
    reader = csv.DictReader(StringIO(content))

    for row in reader:
        skill = row.get('Name', row.get('Skill', ''))
        if skill:
            skills.append(skill)

    return skills


def _parse_posts_csv(content: str) -> List[Dict]:
    """Parse Shares.csv or Posts.csv content."""
    posts = []
    reader = csv.DictReader(StringIO(content))

    for row in reader:
        post_content = row.get('ShareCommentary', row.get('Content', ''))
        if post_content:
            posts.append({
                "content": post_content,
                "timestamp": row.get('Date', ''),
                "url": row.get('ShareLink', '')
            })

    return posts


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_linkedin_export(sys.argv[1])
        print(f"Parsed LinkedIn export:")
        print(f"  Profile: {result['profile'].get('name', 'Unknown')}")
        print(f"  Positions: {len(result['positions'])}")
        print(f"  Skills: {len(result['skills'])}")
        print(f"  Posts: {result['total_posts']}")
