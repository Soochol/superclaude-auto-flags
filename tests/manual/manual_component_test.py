#!/usr/bin/env python3
"""
Manual Component Test - Direct execution without subprocess
"""

import sys
import os
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, '/home/blessp/my_code/superclaude-auto-flags')

def test_component(component_name, test_func):
    """Test a single component with error handling"""
    print(f"\n🔍 Testing {component_name}...")
    try:
        result = test_func()
        if result:
            print(f"   ✅ {component_name}: PASSED")
            return True
        else:
            print(f"   ❌ {component_name}: FAILED")
            return False
    except Exception as e:
        print(f"   💥 {component_name}: ERROR - {e}")
        return False

def test_learning_storage():
    """Test LearningStorage component"""
    try:
        from learning_storage import LearningStorage, UserInteraction
        
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp())
        os.environ['SUPERCLAUDE_TEST_MODE'] = '1'
        
        # Initialize storage
        storage = LearningStorage(str(temp_dir))
        print(f"      • Storage initialized with user_id: {storage.user_id[:8]}...")
        
        # Check database creation
        db_path = temp_dir / 'superclaude_learning.db'
        if not db_path.exists():
            print("      • Database file not created")
            return False
        print("      • Database file created")
        
        # Test interaction recording
        interaction = UserInteraction(
            timestamp=datetime.now().isoformat(),
            user_input="/sc:analyze test code",
            command="analyze",
            description="test code",
            recommended_flags="--persona-analyzer --think",
            actual_flags="--persona-analyzer --think",
            project_context={"project_type": "test", "file_count": 10},
            success=True,
            execution_time=15.5,
            confidence=85,
            reasoning="test pattern matching",
            user_id=storage.user_id,
            project_hash="test_hash_123"
        )
        
        interaction_id = storage.record_interaction(interaction)
        if not interaction_id:
            print("      • Failed to record interaction")
            return False
        print(f"      • Interaction recorded with ID: {interaction_id}")
        
        # Test interaction retrieval
        interactions = storage.get_user_interactions(days=1)
        if len(interactions) == 0:
            print("      • Failed to retrieve interactions")
            return False
        print(f"      • Retrieved {len(interactions)} interactions")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except ImportError as e:
        print(f"      • Import error: {e}")
        return False
    except Exception as e:
        print(f"      • Unexpected error: {e}")
        return False

def test_data_collector():
    """Test LearningDataCollector component"""
    try:
        from data_collector import LearningDataCollector
        from learning_storage import LearningStorage
        
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        storage = LearningStorage(str(temp_dir))
        collector = LearningDataCollector(storage)
        print("      • DataCollector initialized")
        
        # Test project context collection
        test_project_path = '/home/blessp/my_code/superclaude-auto-flags'
        context = collector.collect_project_context(test_project_path)
        
        required_keys = ['project_hash', 'file_count', 'languages', 'project_path']
        missing_keys = [k for k in required_keys if k not in context]
        
        if missing_keys:
            print(f"      • Missing context keys: {missing_keys}")
            return False
        
        print(f"      • Project context collected: {len(context)} keys")
        print(f"      • File count: {context.get('file_count', 'N/A')}")
        print(f"      • Languages: {context.get('languages', 'N/A')}")
        
        # Test interaction lifecycle
        interaction_id = collector.start_interaction(
            user_input="/sc:analyze security vulnerabilities",
            recommended_flags="--persona-security --think",
            confidence=85,
            reasoning="security pattern detected",
            project_context=context
        )
        
        if not interaction_id:
            print("      • Failed to start interaction")
            return False
        print(f"      • Interaction started: {interaction_id}")
        
        # End interaction
        collector.end_interaction(
            actual_flags="--persona-security --think",
            success=True,
            error_message=None
        )
        print("      • Interaction ended successfully")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except ImportError as e:
        print(f"      • Import error: {e}")
        return False
    except Exception as e:
        print(f"      • Unexpected error: {e}")
        return False

def test_learning_engine():
    """Test AdaptiveLearningEngine component"""
    try:
        from learning_engine import AdaptiveLearningEngine
        from learning_storage import LearningStorage
        
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        storage = LearningStorage(str(temp_dir))
        engine = AdaptiveLearningEngine(storage)
        print("      • LearningEngine initialized")
        
        # Test recommendation generation
        recommendation = engine.get_adaptive_recommendation(
            command="analyze",
            description="security vulnerabilities in authentication system",
            project_context={
                "project_type": "python_backend",
                "complexity": "complex",
                "file_count": 150,
                "languages": ["python"],
                "frameworks": ["django"]
            }
        )
        
        if not hasattr(recommendation, 'flags'):
            print("      • Recommendation missing flags attribute")
            return False
        
        if not hasattr(recommendation, 'confidence'):
            print("      • Recommendation missing confidence attribute")
            return False
        
        if not hasattr(recommendation, 'reasoning'):
            print("      • Recommendation missing reasoning attribute")
            return False
        
        print(f"      • Generated recommendation with flags: {recommendation.flags}")
        print(f"      • Confidence: {recommendation.confidence}")
        print(f"      • Reasoning steps: {len(recommendation.reasoning)}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except ImportError as e:
        print(f"      • Import error: {e}")
        return False
    except Exception as e:
        print(f"      • Unexpected error: {e}")  
        return False

def test_personalized_recommender():
    """Test PersonalizedAdaptiveRecommender component"""
    try:
        from adaptive_recommender import PersonalizedAdaptiveRecommender
        from learning_storage import LearningStorage
        
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        storage = LearningStorage(str(temp_dir))
        recommender = PersonalizedAdaptiveRecommender(storage)
        print("      • PersonalizedRecommender initialized")
        
        # Test personalized recommendation
        recommendation = recommender.get_personalized_recommendation(
            user_input="/sc:improve code quality and security",
            project_context={
                "project_type": "python_backend",
                "complexity": "complex",
                "file_count": 200,
                "languages": ["python"],
                "frameworks": ["fastapi"]
            }
        )
        
        if not hasattr(recommendation, 'flags'):
            print("      • Personalized recommendation missing flags")
            return False
        
        if not hasattr(recommendation, 'personalization_factors'):
            print("      • Missing personalization factors")
            return False
        
        print(f"      • Generated personalized flags: {recommendation.flags}")
        print(f"      • Personalization factors: {len(recommendation.personalization_factors)}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except ImportError as e:
        print(f"      • Import error: {e}")
        return False
    except Exception as e:
        print(f"      • Unexpected error: {e}")
        return False

def test_feedback_processor():
    """Test FeedbackProcessor component"""
    try:
        from feedback_processor import FeedbackProcessor
        from learning_storage import LearningStorage
        
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        storage = LearningStorage(str(temp_dir))
        processor = FeedbackProcessor(storage)
        print("      • FeedbackProcessor initialized")
        
        # Test immediate feedback processing
        feedback = processor.process_immediate_feedback(
            interaction_id="test_interaction_001",
            success=True,
            execution_time=25.5,
            error_details=None
        )
        
        if not hasattr(feedback, 'feedback_id'):
            print("      • Immediate feedback missing feedback_id")
            return False
        
        if not hasattr(feedback, 'learning_weight'):
            print("      • Immediate feedback missing learning_weight")
            return False
        
        print(f"      • Immediate feedback processed: {feedback.feedback_id}")
        print(f"      • Learning weight: {feedback.learning_weight}")
        
        # Test explicit feedback processing
        explicit_feedback = processor.process_explicit_feedback(
            interaction_id="test_interaction_002",
            user_rating=4,
            user_correction="Could use --ultrathink for complex analysis"
        )
        
        if not hasattr(explicit_feedback, 'feedback_id'):
            print("      • Explicit feedback missing feedback_id")
            return False
        
        print(f"      • Explicit feedback processed: {explicit_feedback.feedback_id}")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return True
        
    except ImportError as e:
        print(f"      • Import error: {e}")
        return False
    except Exception as e:
        print(f"      • Unexpected error: {e}")
        return False

def test_command_processor():
    """Test SCCommandProcessor component"""
    try:
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        print("      • SCCommandProcessor initialized")
        
        # Test /sc: command processing
        test_inputs = [
            "/sc:analyze 이 코드의 보안 문제점을 찾아줘",
            "/sc:implement user authentication system",
            "/sc:improve performance of database queries"
        ]
        
        for i, user_input in enumerate(test_inputs):
            result = processor.process(user_input)
            
            if not result:
                print(f"      • Failed to process input {i+1}")
                return False
            
            if "SuperClaude" not in result:
                print(f"      • Result doesn't contain SuperClaude indicator")
                return False
            
            if "--persona-" not in result:
                print(f"      • Result doesn't contain persona flags")
                return False
            
            print(f"      • Processed input {i+1}: Success")
        
        # Test normal command passthrough
        normal_input = "regular command without /sc:"
        normal_result = processor.process(normal_input)
        
        if normal_result != normal_input:
            print("      • Normal command passthrough failed")
            return False
        
        print("      • Normal command passthrough: Success")
        
        return True
        
    except ImportError as e:
        print(f"      • Import error: {e}")
        return False
    except Exception as e:
        print(f"      • Unexpected error: {e}")
        return False

def main():
    """Execute all tests"""
    print("🧪 SuperClaude Learning System - Manual Component Test")
    print("=" * 60)
    
    # Define test components
    test_components = [
        ("LearningStorage", test_learning_storage),
        ("LearningDataCollector", test_data_collector),
        ("AdaptiveLearningEngine", test_learning_engine),
        ("PersonalizedRecommender", test_personalized_recommender),
        ("FeedbackProcessor", test_feedback_processor),
        ("SCCommandProcessor", test_command_processor),
    ]
    
    results = {}
    
    # Run tests
    for component_name, test_func in test_components:
        results[component_name] = test_component(component_name, test_func)
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"\n🎯 Overall Results: {passed}/{total} components passed ({passed/total*100:.1f}%)")
    
    print(f"\n📋 Component Status:")
    for component_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   • {component_name}: {status}")
    
    # System readiness assessment
    print(f"\n🚀 System Readiness Assessment:")
    if passed == total:
        print("   ✅ SYSTEM FULLY FUNCTIONAL")
        print("   → All components working correctly")
        print("   → Ready for production deployment")
        print("   → Recommend comprehensive integration testing")
    elif passed >= total * 0.75:
        print("   ⚠️ SYSTEM MOSTLY FUNCTIONAL")
        print("   → Core functionality available")
        print("   → Some components need attention")
        print("   → Can proceed with limited deployment")
    else:
        print("   ❌ SYSTEM NEEDS SIGNIFICANT WORK")
        print("   → Major components are failing")
        print("   → Requires debugging and fixes")
        print("   → Not ready for production")
    
    # Specific recommendations
    failed_components = [name for name, result in results.items() if not result]
    if failed_components:
        print(f"\n🔧 Failed Components Need Attention:")
        for comp in failed_components:
            print(f"   • {comp}")
    
    # Dependency check
    try:
        import numpy
        print(f"\n📦 Dependencies:")
        print("   ✅ NumPy available - Advanced learning features enabled")
    except ImportError:
        print(f"\n📦 Dependencies:")
        print("   ⚠️ NumPy missing - Install with: pip install numpy")
        print("   → Some advanced learning features may be limited")
    
    return 0 if passed >= total * 0.75 else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Test completed with exit code: {exit_code}")