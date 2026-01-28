"""
Work Patterns Extractor
Analyzes screen capture data to extract work behavior patterns.
"""

import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Any


def extract_work_patterns(screen_data: List[Dict]) -> Dict[str, Any]:
    """
    Extract work patterns from screen capture metadata.

    Args:
        screen_data: List of dicts with timestamp, app, window_title

    Returns:
        Work patterns analysis with peak hours, tools, meeting load
    """
    if not screen_data:
        return {"error": "No screen data provided"}

    # Parse timestamps
    parsed_data = []
    for entry in screen_data:
        ts = _parse_timestamp(entry.get("timestamp"))
        if ts:
            parsed_data.append({
                "datetime": ts,
                "app": entry.get("app", "Unknown"),
                "window_title": entry.get("window_title", "")
            })

    if not parsed_data:
        return {"error": "Could not parse any timestamps"}

    # Analyze components
    peak_hours = _analyze_peak_hours(parsed_data)
    primary_tools = _extract_primary_tools(parsed_data)
    meeting_load = _analyze_meeting_load(parsed_data)
    email_habits = _analyze_email_habits(parsed_data)
    task_switching = _analyze_task_switching(parsed_data)

    return {
        "peak_hours": peak_hours,
        "primary_tools": primary_tools,
        "meeting_load": meeting_load,
        "email_habits": email_habits,
        "task_switching_frequency": task_switching
    }


def _parse_timestamp(ts: Any) -> datetime:
    """Parse various timestamp formats."""
    if not ts:
        return None

    if isinstance(ts, datetime):
        return ts

    if isinstance(ts, str):
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue

    return None


def _analyze_peak_hours(data: List[Dict]) -> List[str]:
    """
    Identify peak working hours.
    Returns hour ranges like "09:00-11:00"
    """
    hour_counts = Counter()

    for entry in data:
        hour = entry["datetime"].hour
        hour_counts[hour] += 1

    # Find peak hours (top hours by activity)
    sorted_hours = sorted(hour_counts.items(), key=lambda x: -x[1])

    # Group consecutive hours into ranges
    top_hours = [h for h, _ in sorted_hours[:6]]
    top_hours.sort()

    ranges = []
    if top_hours:
        range_start = top_hours[0]
        prev_hour = top_hours[0]

        for hour in top_hours[1:] + [None]:
            if hour is None or hour != prev_hour + 1:
                # End current range
                range_end = prev_hour + 1
                ranges.append(f"{range_start:02d}:00-{range_end:02d}:00")
                if hour is not None:
                    range_start = hour
            prev_hour = hour if hour else prev_hour

    return ranges[:3]  # Return top 3 ranges


def _extract_primary_tools(data: List[Dict]) -> List[str]:
    """
    Extract most-used applications.
    """
    app_counts = Counter()

    for entry in data:
        app = entry["app"]
        if app and app.lower() not in ["unknown", ""]:
            app_counts[app] += 1

    # Return top apps by usage
    return [app for app, _ in app_counts.most_common(8)]


def _analyze_meeting_load(data: List[Dict]) -> str:
    """
    Categorize meeting load based on video call app usage.
    """
    meeting_apps = ["zoom", "meet", "teams", "webex", "skype", "google meet"]

    total_entries = len(data)
    meeting_entries = 0

    for entry in data:
        app_lower = entry["app"].lower()
        window_lower = entry.get("window_title", "").lower()

        if any(m in app_lower or m in window_lower for m in meeting_apps):
            meeting_entries += 1

    # Calculate meeting percentage
    meeting_pct = meeting_entries / total_entries if total_entries else 0

    # Group by days to count meetings per day
    days = set(entry["datetime"].date() for entry in data)
    num_days = len(days) if days else 1

    meetings_per_day = meeting_entries / num_days

    if meetings_per_day > 4:
        return "high"
    elif meetings_per_day > 2:
        return "medium"
    else:
        return "low"


def _analyze_email_habits(data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze email usage patterns.
    """
    email_apps = ["gmail", "outlook", "mail", "thunderbird", "spark"]

    email_hours = []
    email_count = 0

    for entry in data:
        app_lower = entry["app"].lower()
        window_lower = entry.get("window_title", "").lower()

        if any(e in app_lower for e in email_apps) or "inbox" in window_lower:
            email_hours.append(entry["datetime"].hour)
            email_count += 1

    if not email_hours:
        return {
            "batch_times": [],
            "avg_response_length": "unknown"
        }

    # Find batch times (peak email hours)
    hour_counts = Counter(email_hours)
    sorted_hours = sorted(hour_counts.items(), key=lambda x: -x[1])

    batch_times = []
    for hour, _ in sorted_hours[:2]:
        if 5 <= hour < 12:
            batch_times.append("morning")
        elif 12 <= hour < 17:
            batch_times.append("afternoon")
        elif 17 <= hour < 21:
            batch_times.append("late_afternoon")
        else:
            batch_times.append("evening")

    # Deduplicate while preserving order
    seen = set()
    batch_times = [x for x in batch_times if not (x in seen or seen.add(x))]

    return {
        "batch_times": batch_times,
        "avg_response_length": "medium"  # Would need email content to determine
    }


def _analyze_task_switching(data: List[Dict]) -> str:
    """
    Analyze task switching frequency.
    """
    if len(data) < 2:
        return "unknown"

    # Sort by timestamp
    sorted_data = sorted(data, key=lambda x: x["datetime"])

    # Count app switches
    switches = 0
    prev_app = sorted_data[0]["app"]

    for entry in sorted_data[1:]:
        if entry["app"] != prev_app:
            switches += 1
        prev_app = entry["app"]

    # Calculate switch rate
    total_entries = len(sorted_data)
    switch_rate = switches / total_entries if total_entries else 0

    if switch_rate > 0.7:
        return "high"
    elif switch_rate > 0.4:
        return "moderate"
    else:
        return "low"


if __name__ == "__main__":
    # Quick test
    test_data = [
        {"timestamp": "2025-01-20 07:12:00", "app": "Gmail", "window_title": "Inbox"},
        {"timestamp": "2025-01-20 08:00:00", "app": "Slack", "window_title": "general"},
        {"timestamp": "2025-01-20 09:00:00", "app": "Zoom", "window_title": "Meeting"},
        {"timestamp": "2025-01-20 10:00:00", "app": "Figma", "window_title": "Design"},
        {"timestamp": "2025-01-20 14:00:00", "app": "Zoom", "window_title": "Meeting"},
    ]

    import json
    result = extract_work_patterns(test_data)
    print(json.dumps(result, indent=2))
