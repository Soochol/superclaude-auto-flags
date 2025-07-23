#!/usr/bin/env python3
"""Simple test runner"""

import sys
import os
import subprocess

# Change to correct directory
os.chdir('/home/blessp/my_code/superclaude-auto-flags')

# Try to run the test
try:
    # First check if required modules exist
    print("Checking dependencies...")
    missing = []
    
    try:
        from learning_storage import LearningStorage
        print("✓ learning_storage")
    except ImportError as e:
        print(f"✗ learning_storage: {e}")
        missing.append("learning_storage")
    
    try:
        from data_collector import LearningDataCollector
        print("✓ data_collector")
    except ImportError as e:
        print(f"✗ data_collector: {e}")
        missing.append("data_collector")
    
    try:
        from learning_engine import AdaptiveLearningEngine
        print("✓ learning_engine")
    except ImportError as e:
        print(f"✗ learning_engine: {e}")
        missing.append("learning_engine")
    
    try:
        from adaptive_recommender import PersonalizedAdaptiveRecommender
        print("✓ adaptive_recommender")
    except ImportError as e:
        print(f"✗ adaptive_recommender: {e}")
        missing.append("adaptive_recommender")
    
    try:
        from feedback_processor import FeedbackProcessor
        print("✓ feedback_processor")
    except ImportError as e:
        print(f"✗ feedback_processor: {e}")
        missing.append("feedback_processor")
    
    try:
        from claude_sc_preprocessor import SCCommandProcessor
        print("✓ claude_sc_preprocessor")
    except ImportError as e:
        print(f"✗ claude_sc_preprocessor: {e}")
        missing.append("claude_sc_preprocessor")
    
    if missing:
        print(f"\nMissing modules: {missing}")
        print("Cannot run tests without all modules.")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("All dependencies found! Running tests...")
    print("="*50)
    
    # Import and run the test
    from test_learning_system import run_all_tests
    success = run_all_tests()
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
except Exception as e:
    print(f"Error running tests: {e}")
    import traceback
    traceback.print_exc()