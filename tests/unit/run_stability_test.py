#!/usr/bin/env python3
"""
Simple test runner for SuperClaude stability testing
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Change to project directory
os.chdir(current_dir)

# Import and run the focused test
try:
    from focused_stability_test import FocusedStabilityTester
    
    print("Starting SuperClaude Stability Test...")
    print("Working directory:", os.getcwd())
    print("Python path includes:", current_dir)
    
    tester = FocusedStabilityTester()
    tester.run_focused_tests()
    
except Exception as e:
    print(f"Test execution failed: {e}")
    import traceback
    traceback.print_exc()
    
print("\nTest execution completed.")