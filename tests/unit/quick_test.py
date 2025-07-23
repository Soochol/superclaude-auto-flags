#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir('/home/blessp/my_code/superclaude-auto-flags')
print(f"Working in: {os.getcwd()}")

# Quick pip install
subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy', 'PyYAML'], check=False)

# Test imports
for module in ['numpy', 'yaml', 'learning_storage', 'data_collector', 'learning_engine', 'adaptive_recommender', 'feedback_processor', 'claude_sc_preprocessor']:
    try:
        __import__(module)
        print(f'✅ {module}')
    except Exception as e:
        print(f'❌ {module}: {e}')