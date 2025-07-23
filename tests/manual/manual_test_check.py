#!/usr/bin/env python3
"""Manual test execution and validation"""

import sys
import os
import tempfile
import traceback
from pathlib import Path

# Setup
os.chdir('/home/blessp/my_code/superclaude-auto-flags')
sys.path.insert(0, os.getcwd())
os.environ['SUPERCLAUDE_TEST_MODE'] = '1'

def check_module_import(module_name):
    """Check if a module can be imported"""
    try:
        module = __import__(module_name)
        return True, f"✅ {module_name} imported successfully"
    except ImportError as e:
        return False, f"❌ {module_name} import failed: {e}"
    except Exception as e:
        return False, f"⚠️  {module_name} import error: {e}"

def test_learning_storage():
    """Test learning storage functionality"""
    try:
        from learning_storage import LearningStorage, UserInteraction
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize storage
            storage = LearningStorage(temp_dir)
            
            # Test interaction creation
            interaction = UserInteraction(
                timestamp="2025-01-01T12:00:00",
                user_input="/sc:analyze test code",
                command="analyze", 
                description="test code analysis",
                recommended_flags="--persona-analyzer --think",
                actual_flags="--persona-analyzer --think",
                project_context={"project_type": "python_backend", "complexity": "moderate"},
                success=True,
                execution_time=15.5,
                confidence=85,
                reasoning="pattern matching for analysis command",
                user_id=storage.user_id,
                project_hash="test_hash_123"
            )
            
            # Record interaction
            interaction_id = storage.record_interaction(interaction)
            
            if interaction_id:
                # Try to retrieve interaction
                interactions = storage.get_user_interactions(days=1)
                if interactions and len(interactions) > 0:
                    return True, "✅ LearningStorage working correctly"
                else:
                    return False, "❌ LearningStorage: interaction retrieval failed"
            else:
                return False, "❌ LearningStorage: interaction recording failed"
                
    except Exception as e:
        return False, f"❌ LearningStorage test failed: {str(e)}"

def test_data_collector():
    """Test data collector functionality"""
    try:
        from data_collector import LearningDataCollector
        from learning_storage import LearningStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            collector = LearningDataCollector(storage)
            
            # Test project context collection
            context = collector.collect_project_context(os.getcwd())
            
            required_keys = ['project_hash', 'file_count', 'languages']
            missing_keys = [key for key in required_keys if key not in context]
            
            if not missing_keys:
                return True, "✅ DataCollector working correctly"
            else:
                return False, f"❌ DataCollector: missing keys {missing_keys}"
                
    except Exception as e:
        return False, f"❌ DataCollector test failed: {str(e)}"

def test_learning_engine():
    """Test learning engine functionality"""
    try:
        from learning_engine import AdaptiveLearningEngine
        from learning_storage import LearningStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            engine = AdaptiveLearningEngine(storage)
            
            # Test recommendation generation
            recommendation = engine.get_adaptive_recommendation(
                command="analyze",
                description="security vulnerabilities",
                project_context={
                    "project_type": "python_backend",
                    "complexity": "complex",
                    "file_count": 50
                }
            )
            
            if (hasattr(recommendation, 'flags') and 
                hasattr(recommendation, 'confidence') and
                hasattr(recommendation, 'reasoning')):
                return True, "✅ LearningEngine working correctly"
            else:
                return False, "❌ LearningEngine: invalid recommendation format"
                
    except Exception as e:
        return False, f"❌ LearningEngine test failed: {str(e)}"

def test_adaptive_recommender():
    """Test adaptive recommender functionality"""
    try:
        from adaptive_recommender import PersonalizedAdaptiveRecommender
        from learning_storage import LearningStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            recommender = PersonalizedAdaptiveRecommender(storage)
            
            # Test personalized recommendation
            recommendation = recommender.get_personalized_recommendation(
                user_input="/sc:analyze security issues in this codebase",
                project_context={
                    "project_type": "python_backend",
                    "complexity": "complex",
                    "file_count": 100
                }
            )
            
            if (hasattr(recommendation, 'flags') and 
                hasattr(recommendation, 'confidence') and
                hasattr(recommendation, 'personalization_factors')):
                return True, "✅ AdaptiveRecommender working correctly"
            else:
                return False, "❌ AdaptiveRecommender: invalid recommendation format"
                
    except Exception as e:
        return False, f"❌ AdaptiveRecommender test failed: {str(e)}"

def test_feedback_processor():
    """Test feedback processor functionality"""
    try:
        from feedback_processor import FeedbackProcessor
        from learning_storage import LearningStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            processor = FeedbackProcessor(storage)
            
            # Test immediate feedback processing
            feedback = processor.process_immediate_feedback(
                interaction_id="test_interaction_123",
                success=True,
                execution_time=20.5,
                error_details=None
            )
            
            if (hasattr(feedback, 'feedback_id') and 
                hasattr(feedback, 'learning_weight')):
                return True, "✅ FeedbackProcessor working correctly"
            else:
                return False, "❌ FeedbackProcessor: invalid feedback format"
                
    except Exception as e:
        return False, f"❌ FeedbackProcessor test failed: {str(e)}"

def test_command_processor():
    """Test command processor functionality"""
    try:
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        
        # Test command processing
        result = processor.process("/sc:analyze security vulnerabilities")
        
        if result and "SuperClaude" in result and "--persona-" in result:
            return True, "✅ SCCommandProcessor working correctly"
        else:
            return False, f"❌ SCCommandProcessor: unexpected result format: {result}"
            
    except Exception as e:
        return False, f"❌ SCCommandProcessor test failed: {str(e)}"

def run_manual_tests():
    """Run all manual tests"""
    print("🧪 SuperClaude Learning System Manual Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Import Check", lambda: check_module_import("learning_storage")),
        ("LearningStorage", test_learning_storage),
        ("DataCollector", test_data_collector),
        ("LearningEngine", test_learning_engine),
        ("AdaptiveRecommender", test_adaptive_recommender),
        ("FeedbackProcessor", test_feedback_processor),
        ("CommandProcessor", test_command_processor),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            success, message = test_func()
            results.append((test_name, success, message))
            print(f"   {message}")
        except Exception as e:
            results.append((test_name, False, f"❌ {test_name} failed with exception: {str(e)}"))
            print(f"   ❌ {test_name} failed with exception: {str(e)}")
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Learning system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_manual_tests()
    print(f"\nTest execution completed. Success: {success}")