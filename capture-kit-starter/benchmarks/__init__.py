"""
Capture Kit - Benchmarking System

Analyze top performers and viral posts to improve your social media presence.
"""

from .benchmark_manager import (
    BenchmarkManager,
    analyze_viral_post,
    compare_to_benchmark,
    get_benchmark_recommendations,
)

__all__ = [
    'BenchmarkManager',
    'analyze_viral_post',
    'compare_to_benchmark',
    'get_benchmark_recommendations',
]
