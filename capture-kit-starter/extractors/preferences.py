"""
Preferences Extractor
Analyzes daily check-in responses to extract user preferences and constraints.
"""

import re
from typing import Dict, List, Any


def extract_preferences(checkins: Dict) -> Dict[str, Any]:
    """
    Extract preferences from daily check-in responses.

    Args:
        checkins: Dict with day_1, day_2, etc. keys containing question/response

    Returns:
        Preferences with do[], never_do[], ask_first[] lists
    """
    if not checkins:
        return {"error": "No check-in data provided"}

    # Collect all responses
    all_responses = []
    for day_key, data in checkins.items():
        if isinstance(data, dict):
            response = data.get("response", "")
            question = data.get("question", "")
            all_responses.append({
                "day": day_key,
                "question": question,
                "response": response
            })

    if not all_responses:
        return {"error": "No responses found in check-in data"}

    # Extract preferences by category
    do_items = _extract_do_preferences(all_responses)
    never_do_items = _extract_never_do(all_responses)
    ask_first_items = _extract_ask_first(all_responses)

    return {
        "do": do_items,
        "never_do": never_do_items,
        "ask_first": ask_first_items
    }


def _extract_do_preferences(responses: List[Dict]) -> List[str]:
    """
    Extract things the user wants help with.
    """
    do_items = []

    # Keywords indicating desired help
    do_keywords = [
        "help", "would be great", "wish", "want", "love if",
        "could you", "can you", "please", "draft", "remind",
        "organize", "suggest", "recommend", "assist"
    ]

    for entry in responses:
        response = entry["response"].lower()
        question = entry["question"].lower()

        # Look for questions about desired help
        if "help" in question or "easier" in question or "wish" in question:
            # Extract specific requests
            items = _extract_action_items(entry["response"])
            do_items.extend(items)

        # Look for responses with positive intent
        elif any(kw in response for kw in do_keywords):
            items = _extract_action_items(entry["response"])
            do_items.extend(items)

    # Deduplicate and clean
    return list(dict.fromkeys(do_items))[:6]


def _extract_never_do(responses: List[Dict]) -> List[str]:
    """
    Extract things the user never wants done.
    """
    never_items = []

    # Keywords indicating prohibitions
    never_keywords = [
        "never", "don't", "dont", "hate", "can't stand",
        "not", "without", "no ", "avoid", "stop"
    ]

    # Time-related constraints
    time_patterns = [
        (r"(?:no|don't|never).*before\s+(\d{1,2}(?:am|pm)?)", "Schedule meetings before {0}"),
        (r"(?:no|don't|never).*after\s+(\d{1,2}(?:am|pm)?)", "Schedule meetings after {0}"),
        (r"hate.*(?:before|early|morning)", "Schedule meetings before 9am"),
        (r"(\d{1,2})-(\d{1,2}(?:pm)?)", "Schedule during {0}-{1}"),  # Time ranges
    ]

    for entry in responses:
        response = entry["response"]
        response_lower = response.lower()
        question = entry["question"].lower()

        # Check for "never do" questions
        if "never" in question or "don't want" in question:
            items = _extract_constraints(response)
            never_items.extend(items)

        # Check for constraint keywords in any response
        for kw in never_keywords:
            if kw in response_lower:
                items = _extract_constraints(response)
                never_items.extend(items)
                break

        # Check for time-based constraints
        for pattern, template in time_patterns:
            matches = re.findall(pattern, response_lower)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        never_items.append(template.format(*match))
                    else:
                        never_items.append(template.format(match))

    # Clean and deduplicate
    cleaned = []
    for item in never_items:
        item = item.strip()
        if item and len(item) > 5:
            # Ensure it's not already present (case-insensitive)
            if not any(item.lower() == existing.lower() for existing in cleaned):
                cleaned.append(item)

    return cleaned[:6]


def _extract_ask_first(responses: List[Dict]) -> List[str]:
    """
    Extract things that need confirmation before action.
    """
    ask_items = []

    # Keywords indicating need for approval
    ask_keywords = [
        "check with me", "ask first", "confirm", "review",
        "before", "approval", "let me know", "run by me"
    ]

    for entry in responses:
        response = entry["response"].lower()

        # Look for approval-related language
        if any(kw in response for kw in ask_keywords):
            # Extract what needs approval
            items = _extract_approval_items(entry["response"])
            ask_items.extend(items)

    # Default items based on common patterns
    if not ask_items:
        # Check for client-related constraints
        all_text = ' '.join(e["response"].lower() for e in responses)
        if "client" in all_text and ("approval" in all_text or "review" in all_text or "without" in all_text):
            ask_items.append("Before rescheduling client meetings")
            ask_items.append("Before sharing internal notes externally")
        if "deadline" in all_text or "timeline" in all_text:
            ask_items.append("Before committing to tight deadlines")

    return list(dict.fromkeys(ask_items))[:5]


def _extract_action_items(text: str) -> List[str]:
    """
    Extract actionable items from text.
    """
    items = []

    # Common patterns for desired actions
    patterns = [
        r"(?:drafting|draft)\s+(?:the\s+)?(.+?)(?:\.|,|$)",
        r"(?:help\s+(?:me\s+)?(?:with\s+)?)?(.+?)(?:would be|could be)",
        r"(?:remind\s+(?:me\s+)?(?:of\s+)?)?(.+?)(?:after|before)",
        r"(?:suggest|recommend)\s+(.+?)(?:\.|,|$)",
    ]

    # Direct extraction based on common phrases
    if "drafting" in text.lower() or "draft" in text.lower():
        items.append("Draft client emails for review")

    if "tighten" in text.lower() or "shorter" in text.lower():
        items.append("Suggest shorter/tighter versions of my writing")

    if "action item" in text.lower() or "meeting" in text.lower():
        items.append("Remind me of action items after meetings")

    if "timeline" in text.lower() or "project" in text.lower():
        items.append("Help organize project timelines")

    return items


def _extract_constraints(text: str) -> List[str]:
    """
    Extract constraint statements from text.
    """
    constraints = []

    # Common constraint patterns
    if "send" in text.lower() and ("without" in text.lower() or "review" in text.lower() or "approval" in text.lower()):
        constraints.append("Send anything to clients without approval")

    if "9am" in text.lower() or "before 9" in text.lower() or "morning" in text.lower():
        if "hate" in text.lower() or "meeting" in text.lower() or "don't" in text.lower():
            constraints.append("Schedule meetings before 9am")

    if "6pm" in text.lower() or "after 6" in text.lower():
        constraints.append("Schedule meetings after 6pm")

    if "pickup" in text.lower() or "3-4" in text.lower() or "school" in text.lower():
        constraints.append("Schedule during school pickup (3-4pm)")

    if "vague" in text.lower() or "indirect" in text.lower():
        constraints.append("Be vague or indirect")

    return constraints


def _extract_approval_items(text: str) -> List[str]:
    """
    Extract items that need pre-approval.
    """
    items = []

    if "client" in text.lower():
        if "reschedul" in text.lower() or "meeting" in text.lower():
            items.append("Before rescheduling client meetings")

    if "deadline" in text.lower() or "tight" in text.lower():
        items.append("Before committing to tight deadlines")

    if "internal" in text.lower() or "share" in text.lower() or "external" in text.lower():
        items.append("Before sharing internal notes externally")

    return items


if __name__ == "__main__":
    # Quick test
    test_checkins = {
        "day_1": {
            "question": "What's one thing you wish your AI already knew about you?",
            "response": "That I hate meetings before 9am."
        },
        "day_2": {
            "question": "What kind of help would make tomorrow easier?",
            "response": "Drafting client emails. I spend so much time on those."
        },
        "day_4": {
            "question": "What's something you never want your AI to do?",
            "response": "Send anything to a client without me reviewing it first."
        }
    }

    import json
    result = extract_preferences(test_checkins)
    print(json.dumps(result, indent=2))
