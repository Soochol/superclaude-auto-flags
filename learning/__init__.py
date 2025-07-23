"""
SuperClaude Learning System

This package contains the adaptive learning components that improve
SuperClaude's recommendations over time.
"""

from .adaptive_recommender import get_personalized_recommender
from .data_collector import get_data_collector
from .feedback_processor import get_feedback_processor

__all__ = [
    'get_personalized_recommender',
    'get_data_collector', 
    'get_feedback_processor'
]