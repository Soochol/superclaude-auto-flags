#!/usr/bin/env python3
"""
Test environment and install dependencies
"""

import sys
import subprocess
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current working directory:", os.getcwd())

# Try to install numpy
try:
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pip", "install", "numpy"], 
                          capture_output=True, text=True)
    print("Numpy installation result:")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except Exception as e:
    print("Error installing numpy:", e)

# Try to install PyYAML  
try:
    result = subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML"], 
                          capture_output=True, text=True)
    print("PyYAML installation result:")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except Exception as e:
    print("Error installing PyYAML:", e)

# Test imports
print("\n" + "="*50)
print("TESTING IMPORTS")
print("="*50)

modules_to_test = [
    "numpy", "yaml", "learning_storage", "data_collector", 
    "learning_engine", "adaptive_recommender", "feedback_processor", 
    "claude_sc_preprocessor"
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module}: SUCCESS")
    except ImportError as e:
        print(f"❌ {module}: FAILED - {e}")
    except Exception as e:
        print(f"⚠️  {module}: ERROR - {e}")