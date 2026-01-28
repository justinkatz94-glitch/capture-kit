"""
Capture Kit - Profile Generator
Generates a complete user profile from all data sources.
"""

from typing import Dict, List, Any, Optional

from extractors.writing_style import extract_writing_style
from extractors.speaking_style import extract_speaking_style
from extractors.work_patterns import extract_work_patterns
from extractors.preferences import extract_preferences


def generate_profile(
    writing_samples: List[str] = None,
    transcripts: List[str] = None,
    screen_captures: List[Dict] = None,
    daily_checkins: Dict = None,
    social_exports: List[str] = None
) -> Dict[str, Any]:
    """
    Generate complete user profile from all data sources.

    Args:
        writing_samples: List of text samples (emails, messages, docs)
        transcripts: List of meeting/call transcripts
        screen_captures: List of screen capture metadata dicts
        daily_checkins: Dict of daily check-in responses
        social_exports: List of paths to social media export ZIPs

    Returns:
        Complete user profile dictionary
    """

    profile = {}

    # Extract writing style
    if writing_samples:
        profile["communication"] = profile.get("communication", {})
        writing_result = extract_writing_style(writing_samples)
        if "error" not in writing_result:
            profile["communication"]["writing_style"] = writing_result

    # Extract speaking style
    if transcripts:
        profile["communication"] = profile.get("communication", {})
        speaking_result = extract_speaking_style(transcripts)
        if "error" not in speaking_result:
            profile["communication"]["speaking_style"] = speaking_result

    # Extract work patterns
    if screen_captures:
        work_result = extract_work_patterns(screen_captures)
        if "error" not in work_result:
            profile["work_patterns"] = work_result

    # Extract preferences
    if daily_checkins:
        pref_result = extract_preferences(daily_checkins)
        if "error" not in pref_result:
            profile["preferences"] = pref_result

    # Process social media exports if provided
    if social_exports:
        try:
            from social import SocialCollector

            collector = SocialCollector()

            for export_path in social_exports:
                # Auto-detect platform from filename
                export_lower = export_path.lower()
                if 'twitter' in export_lower:
                    collector.add_export('twitter', export_path)
                elif 'linkedin' in export_lower:
                    collector.add_export('linkedin', export_path)
                elif 'instagram' in export_lower:
                    collector.add_export('instagram', export_path)
                elif 'facebook' in export_lower:
                    collector.add_export('facebook', export_path)

            analysis = collector.analyze()
            if "error" not in analysis:
                profile["social_presence"] = analysis

        except ImportError:
            # Social module not available
            pass

    return profile


def generate_profile_summary(profile: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of the profile.

    Args:
        profile: Generated profile dictionary

    Returns:
        Formatted summary string
    """
    lines = ["=" * 60, "USER PROFILE SUMMARY", "=" * 60]

    # Communication style
    if "communication" in profile:
        comm = profile["communication"]

        if "writing_style" in comm:
            ws = comm["writing_style"]
            lines.append("\nWRITING STYLE")
            lines.append(f"  Tone: {ws.get('tone', 'Unknown')}")
            lines.append(f"  Formality: {ws.get('formality', '?')}/5 ({ws.get('formality_label', '')})")
            if ws.get("common_phrases"):
                lines.append(f"  Common phrases: {', '.join(ws['common_phrases'][:3])}")
            if ws.get("sign_off"):
                so = ws["sign_off"]
                lines.append(f"  Sign-off: {so.get('most_common', 'None')} ({int(so.get('frequency', 0) * 100)}%)")

        if "speaking_style" in comm:
            ss = comm["speaking_style"]
            lines.append("\nSPEAKING STYLE")
            lines.append(f"  Pace: {ss.get('pace', 'Unknown')}")
            lines.append(f"  Directness: {ss.get('directness', '?')}/5 ({ss.get('directness_label', '')})")
            lines.append(f"  Vocabulary: {ss.get('vocabulary_level', 'Unknown')}")
            if ss.get("verbal_habits"):
                lines.append(f"  Verbal habits: {', '.join(ss['verbal_habits'][:3])}")

    # Work patterns
    if "work_patterns" in profile:
        wp = profile["work_patterns"]
        lines.append("\nWORK PATTERNS")
        if wp.get("peak_hours"):
            lines.append(f"  Peak hours: {', '.join(wp['peak_hours'])}")
        if wp.get("primary_tools"):
            lines.append(f"  Primary tools: {', '.join(wp['primary_tools'][:5])}")
        lines.append(f"  Meeting load: {wp.get('meeting_load', 'Unknown')}")

    # Preferences
    if "preferences" in profile:
        pref = profile["preferences"]
        lines.append("\nPREFERENCES")
        if pref.get("do"):
            lines.append("  DO:")
            for item in pref["do"][:3]:
                lines.append(f"    - {item}")
        if pref.get("never_do"):
            lines.append("  NEVER DO:")
            for item in pref["never_do"][:3]:
                lines.append(f"    - {item}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    # Test with sample data
    from test_data.sample_data import (
        get_all_writing_samples,
        get_all_transcripts,
        get_screen_captures,
        get_daily_checkins
    )

    print("Generating profile from sample data...")

    profile = generate_profile(
        writing_samples=get_all_writing_samples(),
        transcripts=get_all_transcripts(),
        screen_captures=get_screen_captures(),
        daily_checkins=get_daily_checkins()
    )

    print(generate_profile_summary(profile))

    # Also output as JSON
    import json
    print("\nFull profile JSON:")
    print(json.dumps(profile, indent=2))
