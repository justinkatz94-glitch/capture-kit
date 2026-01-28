"""Core profile extractors for Capture Kit."""
from .writing_style import extract_writing_style
from .speaking_style import extract_speaking_style
from .work_patterns import extract_work_patterns
from .preferences import extract_preferences

__all__ = [
    'extract_writing_style',
    'extract_speaking_style',
    'extract_work_patterns',
    'extract_preferences'
]
