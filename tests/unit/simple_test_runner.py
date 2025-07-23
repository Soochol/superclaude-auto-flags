#!/usr/bin/env python3
"""
Simple test runner for the SuperClaude learning system
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Set working directory
os.chdir('/home/blessp/my_code/superclaude-auto-flags')

# Set up test environment
os.environ['SUPERCLAUDE_TEST_MODE'] = '1'

def test_basic_imports():
    """Test that all modules can be imported"""
    print("Testing basic imports...")
    
    modules_to_test = [
        'learning_storage',
        'data_collector', 
        'learning_engine',
        'adaptive_recommender',
        'feedback_processor',
        'claude_sc_preprocessor'
    ]
    
    results = {}
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            results[module_name] = "✅ SUCCESS"
            print(f"  ✅ {module_name}")
        except ImportError as e:
            results[module_name] = f"❌ FAILED: {e}"
            print(f"  ❌ {module_name}: {e}")
        except Exception as e:
            results[module_name] = f"⚠️  ERROR: {e}"
            print(f"  ⚠️  {module_name}: {e}")
    
    return results

def test_core_functionality():
    """Test core functionality of each component"""
    print("\nTesting core functionality...")
    
    try:
        # Test LearningStorage
        print("  Testing LearningStorage...")
        from learning_storage import LearningStorage, UserInteraction
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            print("    ✅ Storage initialization")
            
            # Test basic interaction recording
            interaction = UserInteraction(
                timestamp="2025-01-01T12:00:00",
                user_input="/sc:analyze test",
                command="analyze",
                description="test",
                recommended_flags="--persona-analyzer",
                actual_flags="--persona-analyzer",
                project_context={"type": "test"},
                success=True,
                execution_time=10.0,
                confidence=85,
                reasoning="test",
                user_id=storage.user_id,
                project_hash="test_hash"
            )
            
            interaction_id = storage.record_interaction(interaction)
            if interaction_id:
                print("    ✅ Interaction recording")
            else:
                print("    ❌ Interaction recording failed")
        
        # Test DataCollector
        print("  Testing DataCollector...")
        from data_collector import LearningDataCollector
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            collector = LearningDataCollector(storage)
            
            context = collector.collect_project_context(os.getcwd())
            if context and 'project_hash' in context:
                print("    ✅ Project context collection")
            else:
                print("    ❌ Project context collection failed")
        
        # Test LearningEngine
        print("  Testing LearningEngine...")
        from learning_engine import AdaptiveLearningEngine
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            engine = AdaptiveLearningEngine(storage)
            
            recommendation = engine.get_adaptive_recommendation(
                command="analyze",
                description="test",
                project_context={"project_type": "python"}
            )
            
            if recommendation and hasattr(recommendation, 'flags'):
                print("    ✅ Adaptive recommendation")
            else:
                print("    ❌ Adaptive recommendation failed")
        
        # Test PersonalizedAdaptiveRecommender
        print("  Testing PersonalizedAdaptiveRecommender...")
        from adaptive_recommender import PersonalizedAdaptiveRecommender
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            recommender = PersonalizedAdaptiveRecommender(storage)
            
            recommendation = recommender.get_personalized_recommendation(
                user_input="/sc:analyze test",
                project_context={"project_type": "python"}
            )
            
            if recommendation and hasattr(recommendation, 'flags'):
                print("    ✅ Personalized recommendation")
            else:
                print("    ❌ Personalized recommendation failed")
        
        # Test FeedbackProcessor
        print("  Testing FeedbackProcessor...")
        from feedback_processor import FeedbackProcessor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            processor = FeedbackProcessor(storage)
            
            feedback = processor.process_immediate_feedback(
                interaction_id="test_1",
                success=True,
                execution_time=15.0,
                error_details=None
            )
            
            if feedback and hasattr(feedback, 'feedback_id'):
                print("    ✅ Feedback processing")
            else:
                print("    ❌ Feedback processing failed")
        
        # Test SCCommandProcessor (integration)
        print("  Testing SCCommandProcessor...")
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        result = processor.process("/sc:analyze test code")
        
        if result and "SuperClaude" in result:
            print("    ✅ Command processing")
        else:
            print("    ❌ Command processing failed")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Core functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """Test database operations"""
    print("\nTesting database operations...")
    
    try:
        from learning_storage import LearningStorage
        import sqlite3
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            
            # Check if database file was created
            db_path = Path(temp_dir) / 'superclaude_learning.db'
            if db_path.exists():
                print("    ✅ Database file creation")
            else:
                print("    ❌ Database file creation failed")
                return False
            
            # Check table structure
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['interactions', 'feedback', 'pattern_success', 'user_preferences']
                missing_tables = []
                
                for table in expected_tables:
                    if table in tables:
                        print(f"    ✅ Table '{table}' exists")
                    else:
                        print(f"    ❌ Table '{table}' missing")
                        missing_tables.append(table)
                
                if not missing_tables:
                    print("    ✅ All expected tables exist")
                    return True
                else:
                    print(f"    ❌ Missing tables: {missing_tables}")
                    return False
    
    except Exception as e:
        print(f"    ❌ Database operations test failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🧪 SuperClaude Learning System Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Basic imports
    results['imports'] = test_basic_imports()
    
    # Test 2: Core functionality  
    results['core_functionality'] = test_core_functionality()
    
    # Test 3: Database operations
    results['database'] = test_database_operations()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    total_passed = 0
    total_tests = 0
    
    # Import results
    for module, result in results['imports'].items():
        total_tests += 1
        if "SUCCESS" in result:
            total_passed += 1
    
    # Core functionality results
    if results['core_functionality']:
        total_passed += 1
    total_tests += 1
    
    # Database results  
    if results['database']:
        total_passed += 1
    total_tests += 1
    
    print(f"  Tests passed: {total_passed}/{total_tests}")
    
    if total_passed == total_tests:
        print("  🎉 All tests passed!")
        return True
    else:
        print("  ⚠️  Some tests failed - check implementation")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)