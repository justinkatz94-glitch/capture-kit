"""
Platform Adapters - Multi-platform support with platform-specific rules.

Registry and factory for platform adapters.
"""

from typing import Dict, List, Optional, Type
from .base import PlatformAdapter

# Registry of available adapters
_ADAPTERS: Dict[str, Type[PlatformAdapter]] = {}


def register_adapter(adapter_class: Type[PlatformAdapter]):
    """Register a platform adapter."""
    _ADAPTERS[adapter_class.platform_name.lower()] = adapter_class
    return adapter_class


def get_adapter(platform_name: str) -> PlatformAdapter:
    """
    Get an adapter instance for a platform.

    Args:
        platform_name: Name of the platform (twitter, linkedin, instagram)

    Returns:
        PlatformAdapter instance

    Raises:
        ValueError: If platform is not supported
    """
    platform_name = platform_name.lower()
    if platform_name not in _ADAPTERS:
        available = ", ".join(_ADAPTERS.keys())
        raise ValueError(f"Unknown platform '{platform_name}'. Available: {available}")

    return _ADAPTERS[platform_name]()


def list_platforms() -> List[str]:
    """List all available platform names."""
    return list(_ADAPTERS.keys())


def get_all_adapters() -> Dict[str, PlatformAdapter]:
    """Get instances of all registered adapters."""
    return {name: cls() for name, cls in _ADAPTERS.items()}


# Import adapters to trigger registration
from .twitter import TwitterAdapter
from .linkedin import LinkedInAdapter
from .instagram import InstagramAdapter

__all__ = [
    'PlatformAdapter',
    'get_adapter',
    'list_platforms',
    'get_all_adapters',
    'register_adapter',
    'TwitterAdapter',
    'LinkedInAdapter',
    'InstagramAdapter',
]
