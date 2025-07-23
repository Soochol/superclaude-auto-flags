"""
SuperClaude Auto Flags - Core Components

This package contains the core functionality for SuperClaude's intelligent
flag recommendation system.
"""

__version__ = "1.0.0"
__author__ = "SuperClaude Team"

from .claude_sc_preprocessor import SCCommandProcessor
from .claude_smart_wrapper import *

__all__ = ['SCCommandProcessor']