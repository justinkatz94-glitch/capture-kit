# Sample Test Data for Capture Kit Profile Extraction
# Simulates: Sarah Chen, owner of a 6-person marketing agency

"""
PERSONA: Sarah Chen
- Runs "Spark Creative" - boutique marketing agency
- 6 employees, mostly remote
- Clients: B2B SaaS companies
- Communication style: Professional but warm, direct, uses exclamations
- Work pattern: Early mornings, avoids late meetings
- Verbal habits: "at the end of the day", "let's circle back", "love it"
"""

# =============================================================================
# WRITING SAMPLES (Emails, Slack, Docs)
# =============================================================================

SAMPLE_EMAILS = [
    # Email 1: Client communication (formal-ish)
    """
    Hi Marcus,

    Thanks for sending over the Q3 campaign brief! I've reviewed it with the team and we're excited to get started.

    A few quick questions before we dive in:
    - What's the target launch date for the landing pages?
    - Do you have brand guidelines we should follow, or are we starting fresh?
    - Who should we loop in for approvals on the creative side?

    Let me know when you have a moment to chat. Happy to jump on a quick call this week.

    Best,
    Sarah
    """,
    
    # Email 2: Team communication (casual)
    """
    Hey team!

    Quick update on the Acme project - client loved the initial concepts! They want to move forward with Option B (the bold color palette).

    Next steps:
    - Jamie: Can you start on the hero illustrations by Thursday?
    - Dev: Let's finalize the copy deck by EOD tomorrow
    - Everyone: Team sync moved to 2pm Wednesday

    Let me know if anyone's blocked on anything. Great work so far!

    Sarah
    """,
    
    # Email 3: Vendor/partner (professional)
    """
    Hi Rachel,

    Following up on our conversation last week about the photography shoot for the Nexus rebrand.

    We'd like to book the studio for March 15-16. Can you confirm availability and send over a quote? We're looking at approximately 40 product shots plus some lifestyle imagery.

    Also, do you have recommendations for a stylist who specializes in tech products? Our last shoot felt a bit generic and we want something more editorial this time.

    Thanks so much for your help with this!

    Best,
    Sarah Chen
    Spark Creative
    """,
    
    # Email 4: Quick reply (very casual)
    """
    Perfect, thanks! That works for me.

    See you at 3pm.

    Sarah
    """,
    
    # Email 5: Difficult conversation (measured)
    """
    Hi Tom,

    I wanted to follow up on our call yesterday about the timeline concerns.

    I understand the pressure to launch by end of month, but I want to be transparent - rushing the creative process usually leads to work we're not proud of. At the end of the day, a delayed launch with strong assets will outperform a rushed one.

    Here's what I can commit to:
    - Final concepts by the 18th (vs. 15th originally)
    - One round of revisions included
    - Launch-ready assets by the 25th

    Would this adjusted timeline work for your team? Happy to discuss alternatives if needed.

    Best,
    Sarah
    """,
    
    # Email 6: Internal feedback
    """
    Hey Jamie,

    Just reviewed the latest round of designs - love the direction you're taking with the iconography! The simplified style really fits the brand.

    A few small tweaks:
    - Can we try a slightly warmer shade of blue? Current feels a bit cold
    - The spacing on the feature grid feels tight on mobile
    - Love the hover animations, but let's make sure they work on slower connections

    Overall though, this is really strong work. Let's circle back tomorrow and finalize.

    Sarah
    """,
    
    # Email 7: Meeting follow-up
    """
    Hi all,

    Great meeting today! Here's a quick recap of what we discussed:

    Decisions made:
    - Going with the "Stories" concept for the campaign
    - Budget approved for influencer partnerships
    - Launch date: April 12th

    Action items:
    - Sarah: Send SOW to client by Friday
    - Dev: First draft of campaign copy by Monday
    - Jamie: Mood board for visual direction by Tuesday

    Let me know if I missed anything. Excited to kick this off!

    Best,
    Sarah
    """,
    
    # Email 8: Apologetic/rescheduling
    """
    Hi Marcus,

    I'm so sorry but I need to reschedule our 4pm call today - something urgent came up with another client that I need to handle.

    Would tomorrow at the same time work? Or I'm also free Thursday morning before 10am.

    Again, apologies for the last-minute change. I really appreciate your flexibility.

    Best,
    Sarah
    """,
    
    # Email 9: Celebration/praise
    """
    TEAM!!

    We just got word - Nexus campaign won Best B2B Campaign at the Marketing Excellence Awards!!!

    I am SO proud of everyone. This was a true team effort and you all absolutely crushed it. The late nights, the endless revisions, the "just one more tweak" requests - it all paid off.

    Drinks on me Friday. You've earned it!

    Sarah ðŸŽ‰
    """,
    
    # Email 10: Scope/boundary setting
    """
    Hi Lisa,

    Thanks for thinking of us for this project! The scope sounds interesting.

    I do want to flag that the timeline you mentioned (2 weeks for full rebrand) is quite aggressive for what you're describing. Typically a project like this takes 6-8 weeks to do well.

    I'd hate to commit to something and then deliver work that doesn't meet our standards - or yours. Would you be open to discussing a phased approach? We could prioritize the most critical assets for your launch and tackle the rest in a second phase.

    Let me know your thoughts. Happy to jump on a call to discuss options.

    Best,
    Sarah
    """
]

SAMPLE_SLACK_MESSAGES = [
    "sounds good! let's sync after lunch",
    "can someone remind me what the client's feedback was on the hero image?",
    "love it ðŸ‘",
    "running 5 min late to standup, start without me",
    "just sent over the updated deck - let me know if the links work",
    "who has bandwidth to help with the Acme social posts this week?",
    "great catch @jamie - fixed!",
    "reminder: no meeting tomorrow, I'm at a conference",
    "this is really coming together nicely ðŸ”¥",
    "can we push the deadline to Friday? client just added scope",
    "perfect, thanks!",
    "let's circle back on this tomorrow - I need to think on it",
    "quick q: are we using their brand fonts or ours?",
    "heading out for the day, ping me if anything urgent",
    "at the end of the day, the client gets final say on color palette"
]

SAMPLE_DOCUMENT_SNIPPETS = [
    # From a proposal
    """
    Spark Creative brings 8 years of B2B marketing expertise to every engagement. 
    Our approach combines strategic thinking with creative execution, ensuring your 
    brand stands out in a crowded market. We don't just make things look good - 
    we make them work.
    """,
    
    # From internal notes
    """
    Client meeting notes - Nexus rebrand
    - They want to feel more "enterprise" but not boring
    - Competitor analysis: they hate how generic everyone looks
    - Budget: $45k for full rebrand, flexible on timeline
    - Key stakeholder: VP Marketing (Lisa) - final decision maker
    - Watch out for: CEO sometimes overrides at last minute
    """,
    
    # From a creative brief
    """
    Campaign Objective: Position Nexus as the leader in AI-powered analytics
    
    Target Audience: CTOs and VP Engineering at mid-market SaaS companies
    
    Key Message: "Finally, analytics that think ahead"
    
    Tone: Confident but not arrogant. Smart but accessible. 
    Think: trusted advisor, not used car salesman.
    
    Mandatory Elements:
    - New logo usage per brand guidelines
    - Customer proof points (at least 2 case studies)
    - Clear CTA to demo request
    """
]


# =============================================================================
# SPEAKING SAMPLES (Transcripts from meetings/calls)
# =============================================================================

SAMPLE_TRANSCRIPTS = [
    # Transcript 1: Client kickoff call
    """
    [00:00:15] Sarah: Alright, I think everyone's here. Thanks for joining, everyone. So, um, let's dive right in. Marcus, why don't you start by giving us the overview of what you're hoping to achieve with this campaign?

    [00:00:32] Marcus: Sure, so basically we're looking to...

    [00:02:45] Sarah: Got it, that makes sense. So at the end of the day, you're trying to differentiate from the competitors who all look the same, right? I think there's a real opportunity here to do something bold. Let me share some initial thoughts...

    [00:05:12] Sarah: ...and that's why I think the "Stories" angle could work really well. It's authentic, it's different, and honestly, it's the kind of work we love doing. What do you think?

    [00:05:30] Marcus: I like it. What would the timeline look like?

    [00:05:35] Sarah: Good question. So typically for a campaign of this scope, we're looking at about 6 weeks from kickoff to launch-ready assets. That gives us time to do it right, you know? We could probably compress it to 4 weeks if we really needed to, but I'd rather not rush the creative process if we don't have to.
    """,
    
    # Transcript 2: Internal team meeting
    """
    [00:00:00] Sarah: Okay team, let's do a quick roundtable. Jamie, where are we on the Acme designs?

    [00:00:08] Jamie: So I've got the homepage done and I'm about halfway through the product pages. Should be done by end of day tomorrow.

    [00:00:18] Sarah: Perfect. Love what I've seen so far, by the way. The, um, the illustration style is really working. Dev, how about copy?

    [00:00:28] Dev: Yeah, so I'm a bit stuck on the value prop section actually. The client's messaging is kind of all over the place and I'm trying to, like, distill it down.

    [00:00:40] Sarah: Okay, let's circle back on that after this call. I have some notes from my last conversation with them that might help. At the end of the day, we need to make their message clearer than they can themselves, right? That's kind of our job.

    [00:00:55] Dev: Yeah, that would be super helpful.

    [00:01:00] Sarah: Great. Anyone else blocked on anything? No? Okay, let's reconvene Thursday same time. Good work everyone.
    """,
    
    # Transcript 3: Sales/pitch call
    """
    [00:00:20] Sarah: So tell me a bit about what's not working with your current marketing. What made you reach out?

    [00:00:30] Prospect: Honestly, we've been working with a larger agency and it just feels like we're a small fish to them. The work is fine but it's not... special, you know?

    [00:00:45] Sarah: I totally get that. That's actually why a lot of our clients come to us. We're intentionally small - six people - because we want every client to feel like a priority. You're not going to get handed off to a junior team here. I'm involved in every project.

    [00:01:05] Prospect: That's refreshing to hear.

    [00:01:08] Sarah: Yeah, and look, I'll be honest with you - we're not the cheapest option out there. But the clients who work with us tend to stick around for years because we actually move the needle. At the end of the day, that's what matters, right? Not just pretty pictures but actual results.

    [00:01:30] Prospect: Absolutely. Can you walk me through your process?

    [00:01:35] Sarah: Of course. So we start with what we call a Brand Deep Dive...
    """,
    
    # Transcript 4: Casual team chat
    """
    Sarah: Hey, did you see the email from Marcus? He loved the concepts!

    Jamie: Oh awesome! Which one did they pick?

    Sarah: Option B, the bold one. I'm actually kind of surprised, they usually play it safe. But I'm excited, it's gonna be fun to execute.

    Jamie: Nice. Do we have budget for the custom illustrations or are we using stock?

    Sarah: Custom. I made sure that was in the SOW. Stock would totally kill the vibe we're going for.

    Jamie: Love it. Okay, I'll start sketching tomorrow.

    Sarah: Perfect. Oh, and heads up - I'm out Friday afternoon for my kid's thing. Just ping me if anything's urgent.
    """,
    
    # Transcript 5: Difficult feedback conversation
    """
    [00:00:10] Sarah: So I wanted to chat about the last round of revisions on the Nexus project. I noticed we're on round four now and the changes are getting pretty significant.

    [00:00:22] Client: Yeah, I know, I'm sorry about that. The CEO keeps weighing in at the last minute.

    [00:00:30] Sarah: No, I get it, that happens. But here's my concern - we're kind of spinning our wheels at this point, and honestly, it's not great for the work or the timeline. Can we maybe set up a review process where all stakeholders see it at once? That way we're not playing telephone.

    [00:00:50] Client: That makes sense. I'll talk to the team.

    [00:00:55] Sarah: I appreciate that. And look, I want to be clear - we want to get this right. That's the whole point. But the back and forth is, um, it's making it hard to do our best work. Does that make sense?

    [00:01:10] Client: Totally. I'll get everyone aligned on our end.

    [00:01:15] Sarah: Perfect. Thank you. Okay, so moving forward...
    """
]


# =============================================================================
# DAILY CHECK-IN RESPONSES
# =============================================================================

DAILY_CHECKINS = {
    "day_1": {
        "question": "What's one thing you wish your AI already knew about you?",
        "response": "That I hate meetings before 9am. And I really don't like when people are vague - just tell me what you need directly."
    },
    "day_2": {
        "question": "What kind of help would make tomorrow easier?",
        "response": "Honestly, drafting the first version of client emails. I spend so much time on those and they all follow the same pattern anyway."
    },
    "day_3": {
        "question": "Is there anything from today you'd want to remember forever?",
        "response": "The feedback framework I used with the Nexus client actually worked really well. Something about acknowledging their constraints first before pushing back."
    },
    "day_4": {
        "question": "What's something you never want your AI to do?",
        "response": "Send anything to a client without me reviewing it first. Ever. Also don't schedule things during school pickup (3-4pm) or after 6pm."
    },
    "day_5": {
        "question": "Anything else before I build your profile?",
        "response": "I tend to be too wordy in first drafts. If you can help me tighten things up that would be amazing. Also I overuse exclamation points apparently lol"
    }
}


# =============================================================================
# SCREEN CAPTURE METADATA (Simulated OCR + timestamps)
# =============================================================================

SCREEN_CAPTURE_LOG = [
    # Day 1
    {"timestamp": "2025-01-20 07:12:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-20 07:35:00", "app": "Gmail", "window_title": "Composing: Re: Q3 Campaign Brief"},
    {"timestamp": "2025-01-20 08:00:00", "app": "Slack", "window_title": "Spark Creative - #general"},
    {"timestamp": "2025-01-20 08:15:00", "app": "Figma", "window_title": "Nexus Rebrand - Landing Page"},
    {"timestamp": "2025-01-20 09:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-20 10:05:00", "app": "Google Docs", "window_title": "Nexus Campaign Brief - Draft"},
    {"timestamp": "2025-01-20 11:30:00", "app": "Slack", "window_title": "Spark Creative - #nexus-project"},
    {"timestamp": "2025-01-20 12:00:00", "app": "Chrome", "window_title": "Lunch break - YouTube"},
    {"timestamp": "2025-01-20 13:00:00", "app": "Notion", "window_title": "Weekly Planning"},
    {"timestamp": "2025-01-20 14:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-20 15:30:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-20 16:45:00", "app": "Figma", "window_title": "Acme - Homepage Designs"},
    {"timestamp": "2025-01-20 17:30:00", "app": "Gmail", "window_title": "Composing: Team Update"},
    
    # Day 2
    {"timestamp": "2025-01-21 07:05:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-21 07:45:00", "app": "Slack", "window_title": "Spark Creative - #general"},
    {"timestamp": "2025-01-21 08:30:00", "app": "Google Sheets", "window_title": "Q1 Budget Tracker"},
    {"timestamp": "2025-01-21 09:15:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-21 10:30:00", "app": "Figma", "window_title": "Nexus Rebrand - Brand Guidelines"},
    {"timestamp": "2025-01-21 12:00:00", "app": "Chrome", "window_title": "LinkedIn"},
    {"timestamp": "2025-01-21 13:00:00", "app": "Notion", "window_title": "Client Tracker"},
    {"timestamp": "2025-01-21 14:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-21 15:00:00", "app": "Slack", "window_title": "Spark Creative - DM with Jamie"},
    {"timestamp": "2025-01-21 16:00:00", "app": "Gmail", "window_title": "Composing: Re: Photography Shoot"},
    {"timestamp": "2025-01-21 17:00:00", "app": "Google Docs", "window_title": "SOW - Nexus Campaign"},
    
    # Day 3
    {"timestamp": "2025-01-22 06:55:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-22 07:30:00", "app": "Notion", "window_title": "Daily Tasks"},
    {"timestamp": "2025-01-22 08:00:00", "app": "Slack", "window_title": "Spark Creative - #general"},
    {"timestamp": "2025-01-22 09:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-22 10:30:00", "app": "Google Docs", "window_title": "Proposal - New Client"},
    {"timestamp": "2025-01-22 11:45:00", "app": "Figma", "window_title": "Acme - Product Pages"},
    {"timestamp": "2025-01-22 12:15:00", "app": "Chrome", "window_title": "Spotify"},
    {"timestamp": "2025-01-22 13:00:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-22 14:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-22 15:30:00", "app": "Slack", "window_title": "Spark Creative - #acme-project"},
    {"timestamp": "2025-01-22 16:30:00", "app": "Gmail", "window_title": "Composing: Re: Timeline Concerns"},
    {"timestamp": "2025-01-22 17:15:00", "app": "Notion", "window_title": "Meeting Notes"},
    
    # Day 4
    {"timestamp": "2025-01-23 07:10:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-23 08:00:00", "app": "Slack", "window_title": "Spark Creative - #general"},
    {"timestamp": "2025-01-23 08:45:00", "app": "Google Docs", "window_title": "Creative Brief - Nexus"},
    {"timestamp": "2025-01-23 10:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-23 11:00:00", "app": "Figma", "window_title": "Nexus - Campaign Assets"},
    {"timestamp": "2025-01-23 12:00:00", "app": "Chrome", "window_title": "Dribbble - Inspiration"},
    {"timestamp": "2025-01-23 13:00:00", "app": "Slack", "window_title": "Spark Creative - DM with Dev"},
    {"timestamp": "2025-01-23 14:00:00", "app": "Gmail", "window_title": "Composing: Re: Budget Questions"},
    {"timestamp": "2025-01-23 15:45:00", "app": "Notion", "window_title": "Process Documentation"},
    {"timestamp": "2025-01-23 16:30:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    
    # Day 5
    {"timestamp": "2025-01-24 07:00:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-24 07:30:00", "app": "Slack", "window_title": "Spark Creative - #general"},
    {"timestamp": "2025-01-24 08:15:00", "app": "Google Docs", "window_title": "Weekly Report"},
    {"timestamp": "2025-01-24 09:00:00", "app": "Zoom", "window_title": "Zoom Meeting"},
    {"timestamp": "2025-01-24 10:00:00", "app": "Figma", "window_title": "Acme - Final Review"},
    {"timestamp": "2025-01-24 11:30:00", "app": "Gmail", "window_title": "Composing: TEAM - We Won!"},
    {"timestamp": "2025-01-24 12:00:00", "app": "Chrome", "window_title": "Restaurant reservations"},
    {"timestamp": "2025-01-24 13:00:00", "app": "Slack", "window_title": "Spark Creative - #celebrations"},
    {"timestamp": "2025-01-24 14:00:00", "app": "Notion", "window_title": "Q1 Planning"},
    {"timestamp": "2025-01-24 15:00:00", "app": "Gmail", "window_title": "Inbox - sarah@sparkcreative.co"},
    {"timestamp": "2025-01-24 16:00:00", "app": "Figma", "window_title": "New Project - Wireframes"},
]


# =============================================================================
# EXPECTED PROFILE OUTPUT (Ground Truth for Validation)
# =============================================================================

EXPECTED_PROFILE = {
    "communication": {
        "writing_style": {
            "tone": "Professional but warm",
            "formality": 3,  # Neutral-to-formal, adapts to context
            "formality_label": "Balanced Professional",
            "avg_sentence_length": "medium",
            "punctuation_patterns": ["uses_exclamations", "occasional_emoji"],
            "common_phrases": ["let me know", "at the end of the day", "let's circle back", "happy to"],
            "sign_off": {
                "most_common": "Best,",
                "frequency": 0.7,
                "alternatives": ["Sarah", "Thanks,"]
            }
        },
        "speaking_style": {
            "pace": "medium",
            "filler_words": [
                {"word": "um", "per_100_words": 1.2},
                {"word": "like", "per_100_words": 0.8},
                {"word": "you know", "per_100_words": 0.6}
            ],
            "vocabulary_level": "moderate",
            "directness": 4,  # Fairly direct, but diplomatic
            "directness_label": "Direct but Diplomatic",
            "verbal_habits": ["at the end of the day", "let's circle back", "I want to be clear"]
        }
    },
    "work_patterns": {
        "peak_hours": ["07:00-08:00", "09:00-11:00", "14:00-16:00"],
        "primary_tools": ["Gmail", "Slack", "Figma", "Zoom", "Google Docs", "Notion"],
        "meeting_load": "medium",  # ~2-3 meetings per day
        "email_habits": {
            "batch_times": ["morning", "late_afternoon"],
            "avg_response_length": "medium"
        },
        "task_switching_frequency": "moderate"
    },
    "preferences": {
        "do": [
            "Draft client emails for review",
            "Suggest shorter/tighter versions of my writing",
            "Remind me of action items after meetings",
            "Help organize project timelines"
        ],
        "never_do": [
            "Send anything to clients without approval",
            "Schedule meetings before 9am",
            "Schedule meetings after 6pm",
            "Schedule during school pickup (3-4pm)",
            "Be vague or indirect"
        ],
        "ask_first": [
            "Before rescheduling client meetings",
            "Before committing to tight deadlines",
            "Before sharing internal notes externally"
        ]
    },
    "context": {
        "role": "Agency Owner / Creative Director",
        "company": "Spark Creative",
        "team_size": "6",
        "industry": "B2B Marketing / Creative Services",
        "key_relationships": ["Marcus (client)", "Jamie (designer)", "Dev (copywriter)"]
    }
}


# =============================================================================
# TEST HARNESS
# =============================================================================

def get_all_writing_samples() -> list:
    """Returns all text samples for writing style extraction."""
    return SAMPLE_EMAILS + SAMPLE_SLACK_MESSAGES + SAMPLE_DOCUMENT_SNIPPETS


def get_all_transcripts() -> list:
    """Returns all transcript samples for speaking style extraction."""
    return SAMPLE_TRANSCRIPTS


def get_screen_captures() -> list:
    """Returns simulated screen capture log."""
    return SCREEN_CAPTURE_LOG


def get_daily_checkins() -> dict:
    """Returns daily check-in responses."""
    return DAILY_CHECKINS


def get_expected_profile() -> dict:
    """Returns the ground truth profile for validation."""
    return EXPECTED_PROFILE


def validate_profile(generated: dict, expected: dict) -> dict:
    """
    Compares generated profile against expected and returns accuracy metrics.
    """
    results = {
        "matches": [],
        "mismatches": [],
        "missing": [],
        "extra": []
    }
    
    # Simple validation - check key fields
    checks = [
        ("tone", generated.get("communication", {}).get("writing_style", {}).get("tone")),
        ("formality", generated.get("communication", {}).get("writing_style", {}).get("formality")),
        ("directness", generated.get("communication", {}).get("speaking_style", {}).get("directness")),
        ("sign_off", generated.get("communication", {}).get("writing_style", {}).get("sign_off", {}).get("most_common")),
    ]
    
    expected_values = {
        "tone": "Professional but warm",
        "formality": 3,
        "directness": 4,
        "sign_off": "Best,"
    }
    
    for key, actual in checks:
        expected_val = expected_values.get(key)
        if actual == expected_val:
            results["matches"].append(f"{key}: {actual}")
        elif actual is None:
            results["missing"].append(key)
        else:
            results["mismatches"].append(f"{key}: expected '{expected_val}', got '{actual}'")
    
    return results


# =============================================================================
# MAIN - Run this to see sample data
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CAPTURE KIT - SAMPLE TEST DATA")
    print("=" * 60)
    print(f"\nPersona: Sarah Chen, owner of Spark Creative (marketing agency)")
    print(f"\nData available:")
    print(f"  - {len(SAMPLE_EMAILS)} email samples")
    print(f"  - {len(SAMPLE_SLACK_MESSAGES)} Slack messages")
    print(f"  - {len(SAMPLE_DOCUMENT_SNIPPETS)} document snippets")
    print(f"  - {len(SAMPLE_TRANSCRIPTS)} meeting transcripts")
    print(f"  - {len(SCREEN_CAPTURE_LOG)} screen capture events")
    print(f"  - {len(DAILY_CHECKINS)} daily check-in responses")
    print(f"\nExpected profile summary:")
    print(f"  - Tone: Professional but warm")
    print(f"  - Formality: 3/5 (Balanced)")
    print(f"  - Directness: 4/5 (Direct but diplomatic)")
    print(f"  - Sign-off: 'Best,' (70% frequency)")
    print(f"  - Verbal habits: 'at the end of the day', 'let's circle back'")
    print(f"\nRun extractors against this data to validate profile quality.")
