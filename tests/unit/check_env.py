#!/usr/bin/env python3
import sys
import os

print("Python Environment Check:")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Try basic imports
try:
    import numpy
    print(f"✅ numpy: {numpy.__version__}")
except ImportError:
    print("❌ numpy: not installed")

try:
    import yaml  
    print(f"✅ yaml: {yaml.__version__}")
except ImportError:
    print("❌ yaml: not installed")

try:
    import sqlite3
    print(f"✅ sqlite3: {sqlite3.version}")
except ImportError:
    print("❌ sqlite3: not available")