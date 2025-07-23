#!/usr/bin/env python3
"""Execute the test"""

import sys
import os

# Change to the directory
os.chdir('/home/blessp/my_code/superclaude-auto-flags')

# Add to path
sys.path.insert(0, os.getcwd())

# Set test mode
os.environ['SUPERCLAUDE_TEST_MODE'] = '1'

# Now execute the simple test
try:
    exec(open('simple_test_runner.py').read())
except Exception as e:
    print(f"Error executing test: {e}")
    import traceback
    traceback.print_exc()