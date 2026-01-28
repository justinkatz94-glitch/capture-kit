"""
Capture Kit - FinTwit Engagement System

Tools for finding trending posts and generating optimized replies in your voice.
"""

from .scanner import FinTwitScanner, scan_fintwit, get_daily_brief
from .reply_generator import ReplyGenerator, draft_replies
from .scoring import score_reply, calculate_voice_match

__all__ = [
    'FinTwitScanner',
    'scan_fintwit',
    'get_daily_brief',
    'ReplyGenerator',
    'draft_replies',
    'score_reply',
    'calculate_voice_match',
]
