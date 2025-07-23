#!/usr/bin/env python3
"""
Test script to check dependencies and module imports
"""

import sys
import os
import subprocess
import sqlite3
from pathlib import Path

def test_dependencies():
    """Test if required dependencies are installed"""
    results = {
        'dependencies': {},
        'modules': {},
        'sqlite_test': False
    }
    
    # Test numpy
    try:
        import numpy
        results['dependencies']['numpy'] = f"✅ Installed (version {numpy.__version__})"
    except ImportError:
        results['dependencies']['numpy'] = "❌ Not installed - need to install"
        print("Installing numpy...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
            import numpy
            results['dependencies']['numpy'] = f"✅ Installed after installation (version {numpy.__version__})"
        except Exception as e:
            results['dependencies']['numpy'] = f"❌ Failed to install: {e}"
    
    # Test PyYAML
    try:
        import yaml
        results['dependencies']['PyYAML'] = f"✅ Installed (version {yaml.__version__})"
    except ImportError:
        results['dependencies']['PyYAML'] = "❌ Not installed - need to install"
        print("Installing PyYAML...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
            import yaml
            results['dependencies']['PyYAML'] = f"✅ Installed after installation (version {yaml.__version__})"
        except Exception as e:
            results['dependencies']['PyYAML'] = f"❌ Failed to install: {e}"
    
    # Test learning system modules
    modules_to_test = [
        'learning_storage',
        'data_collector',
        'learning_engine', 
        'adaptive_recommender',
        'feedback_processor',
        'claude_sc_preprocessor'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            results['modules'][module] = "✅ Import successful"
        except ImportError as e:
            results['modules'][module] = f"❌ Import failed: {e}"
        except Exception as e:
            results['modules'][module] = f"⚠️ Import error: {e}"
    
    # Test SQLite database creation
    try:
        test_db_path = Path(__file__).parent / "test_database.db"
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Create a simple test table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test_record",))
        conn.commit()
        
        # Query test data
        cursor.execute("SELECT * FROM test_table")
        records = cursor.fetchall()
        
        conn.close()
        
        # Clean up test database
        test_db_path.unlink()
        
        results['sqlite_test'] = f"✅ SQLite test successful - created table, inserted data, queried {len(records)} records"
        
    except Exception as e:
        results['sqlite_test'] = f"❌ SQLite test failed: {e}"
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("SuperClaude Learning System - Dependency Test")
    print("=" * 60)
    
    results = test_dependencies()
    
    print("\n📦 Dependencies Check:")
    for dep, status in results['dependencies'].items():
        print(f"  {dep}: {status}")
    
    print("\n🔧 Module Import Test:")
    for module, status in results['modules'].items():
        print(f"  {module}: {status}")
    
    print(f"\n💾 SQLite Database Test:")
    print(f"  {results['sqlite_test']}")
    
    # Summary
    dep_success = all("✅" in status for status in results['dependencies'].values())
    module_success = all("✅" in status for status in results['modules'].values())
    sqlite_success = "✅" in str(results['sqlite_test'])
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Dependencies: {'✅ All OK' if dep_success else '❌ Issues found'}")
    print(f"  Module Imports: {'✅ All OK' if module_success else '❌ Issues found'}")
    print(f"  SQLite Test: {'✅ OK' if sqlite_success else '❌ Failed'}")
    print("=" * 60)
    
    if dep_success and module_success and sqlite_success:
        print("🎉 Phase 1 Testing: ALL SYSTEMS READY!")
    else:
        print("⚠️  Phase 1 Testing: Issues detected - see details above")