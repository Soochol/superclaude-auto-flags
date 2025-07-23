#!/usr/bin/env python3
"""Manual import test without external execution"""

import sys
import os
import sqlite3
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("=" * 60)  
print("SuperClaude Learning System - Manual Import Test")
print("=" * 60)

# Test 1: Check basic dependencies
print("\n📦 Checking basic dependencies:")

try:
    import json
    import datetime
    import pathlib
    import typing
    import dataclasses
    import threading
    import collections
    import enum
    import re
    import time
    import hashlib
    print("✅ All standard library modules available")
except ImportError as e:
    print(f"❌ Standard library issue: {e}")

# Test 2: Check numpy
print("\n🔢 Checking NumPy:")
try:
    import numpy as np
    print(f"✅ NumPy available - version {np.__version__}")
    numpy_available = True
except ImportError:
    print("❌ NumPy not available - run: pip install numpy")
    numpy_available = False

# Test 3: Check PyYAML  
print("\n📄 Checking PyYAML:")
try:
    import yaml
    print(f"✅ PyYAML available - version {yaml.__version__}")
    yaml_available = True
except ImportError:
    print("❌ PyYAML not available - run: pip install PyYAML")
    yaml_available = False

# Test 4: Test learning system modules
print("\n🧠 Testing learning system modules:")

modules_to_test = [
    'learning_storage',
    'data_collector', 
    'learning_engine',
    'adaptive_recommender',
    'feedback_processor',
    'claude_sc_preprocessor'
]

module_results = {}
for module_name in modules_to_test:
    try:
        module = __import__(module_name)
        print(f"✅ {module_name}: Import successful")
        module_results[module_name] = True
    except ImportError as e:
        print(f"❌ {module_name}: Import failed - {e}")
        module_results[module_name] = False
    except Exception as e:
        print(f"⚠️  {module_name}: Import error - {e}")
        module_results[module_name] = False

# Test 5: SQLite database test
print("\n💾 Testing SQLite database:")
try:
    test_db_path = current_dir / "test_permissions.db"
    
    # Create database and table
    conn = sqlite3.connect(str(test_db_path))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_permissions (
            id INTEGER PRIMARY KEY,
            test_name TEXT,
            timestamp REAL
        )
    """)
    
    # Insert test record
    cursor.execute("INSERT INTO test_permissions (test_name, timestamp) VALUES (?, ?)", 
                   ("permissions_test", time.time()))
    conn.commit()
    
    # Read test record
    cursor.execute("SELECT COUNT(*) FROM test_permissions")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    # Clean up
    if test_db_path.exists():
        test_db_path.unlink()
    
    print(f"✅ SQLite test successful - created/inserted/queried {count} records")
    sqlite_available = True

except Exception as e:
    print(f"❌ SQLite test failed: {e}")
    sqlite_available = False

# Summary
print("\n" + "=" * 60)
print("PHASE 1 TEST RESULTS:")
print("=" * 60)

print(f"📦 Dependencies:")
print(f"   NumPy: {'✅ Available' if numpy_available else '❌ Missing'}")
print(f"   PyYAML: {'✅ Available' if yaml_available else '❌ Missing'}")

print(f"\n🧠 Learning System Modules:")
for module, success in module_results.items():
    print(f"   {module}: {'✅ OK' if success else '❌ Failed'}")

print(f"\n💾 Database:")
print(f"   SQLite: {'✅ OK' if sqlite_available else '❌ Failed'}")

# Overall status
deps_ok = numpy_available and yaml_available  
modules_ok = all(module_results.values())
all_ok = deps_ok and modules_ok and sqlite_available

print(f"\n🎯 Overall Status: {'✅ ALL SYSTEMS READY' if all_ok else '❌ ISSUES DETECTED'}")

if not all_ok:
    print("\n🔧 Required Actions:")
    if not numpy_available:
        print("   - Install NumPy: pip install numpy")
    if not yaml_available:  
        print("   - Install PyYAML: pip install PyYAML")
    if not modules_ok:
        print("   - Fix module import issues (see details above)")
    if not sqlite_available:
        print("   - Check file system permissions for SQLite")

print("=" * 60)