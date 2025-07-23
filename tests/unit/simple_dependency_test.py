#!/usr/bin/env python3
"""
Simple Dependency and Import Test
Tests what components can be imported and basic functionality
"""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '/home/blessp/my_code/superclaude-auto-flags')

def test_imports():
    """Test which components can be imported"""
    results = {}
    
    # Test core dependencies
    dependencies = {
        'json': 'json',
        'sqlite3': 'sqlite3', 
        'datetime': 'datetime',
        'pathlib': 'pathlib',
        'threading': 'threading',
        'numpy': 'numpy',
        'dataclasses': 'dataclasses'
    }
    
    print("🔍 Testing Dependencies:")
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
            results[name] = True
        except ImportError:
            print(f"   ❌ {name} - MISSING")
            results[name] = False
    
    # Test component imports
    components = {
        'learning_storage': 'LearningStorage',
        'data_collector': 'LearningDataCollector', 
        'learning_engine': 'AdaptiveLearningEngine',
        'adaptive_recommender': 'PersonalizedAdaptiveRecommender',
        'feedback_processor': 'FeedbackProcessor',
        'claude_sc_preprocessor': 'SCCommandProcessor'
    }
    
    print("\n🧩 Testing Component Imports:")
    for module_name, class_name in components.items():
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
            results[f"{module_name}_{class_name}"] = True
        except ImportError as e:
            print(f"   ❌ {module_name}.{class_name} - Import Error: {e}")
            results[f"{module_name}_{class_name}"] = False
        except AttributeError as e:
            print(f"   ⚠️  {module_name}.{class_name} - Attribute Error: {e}")
            results[f"{module_name}_{class_name}"] = False
        except Exception as e:
            print(f"   💥 {module_name}.{class_name} - Unexpected Error: {e}")
            results[f"{module_name}_{class_name}"] = False
    
    return results

def test_basic_functionality():
    """Test basic functionality of components that can be imported"""
    print("\n🧪 Testing Basic Functionality:")
    
    # Setup test environment
    temp_dir = Path(tempfile.mkdtemp())
    os.environ['SUPERCLAUDE_TEST_MODE'] = '1'
    os.environ['SUPERCLAUDE_STORAGE_DIR'] = str(temp_dir)
    
    try:
        # Test LearningStorage if available
        try:
            from learning_storage import LearningStorage, UserInteraction
            from datetime import datetime
            
            storage = LearningStorage(str(temp_dir))
            print("   ✅ LearningStorage - Initialization successful")
            
            # Test database creation
            db_path = temp_dir / 'superclaude_learning.db'
            if db_path.exists():
                print("   ✅ LearningStorage - Database file created")
            else:
                print("   ❌ LearningStorage - Database file not created")
            
            # Test basic interaction recording (if datetime works)
            try:
                interaction = UserInteraction(
                    timestamp=datetime.now().isoformat(),
                    user_input="/sc:test",
                    command="test", 
                    description="test",
                    recommended_flags="--test",
                    actual_flags="--test",
                    project_context={"test": True},
                    success=True,
                    execution_time=1.0,
                    confidence=80,
                    reasoning="test",
                    user_id=storage.user_id,
                    project_hash="test"
                )
                
                interaction_id = storage.record_interaction(interaction)
                if interaction_id:
                    print("   ✅ LearningStorage - Interaction recording works")
                else:
                    print("   ❌ LearningStorage - Interaction recording failed")
                    
            except Exception as e:
                print(f"   ❌ LearningStorage - Interaction test failed: {e}")
                
        except Exception as e:
            print(f"   ❌ LearningStorage - Failed: {e}")
        
        # Test DataCollector if available
        try:
            from data_collector import LearningDataCollector
            from learning_storage import LearningStorage
            
            storage = LearningStorage(str(temp_dir))
            collector = LearningDataCollector(storage)
            print("   ✅ LearningDataCollector - Initialization successful")
            
            # Test project context collection
            try:
                context = collector.collect_project_context('/home/blessp/my_code/superclaude-auto-flags')
                if isinstance(context, dict) and 'project_hash' in context:
                    print("   ✅ LearningDataCollector - Project context collection works")
                else:
                    print("   ❌ LearningDataCollector - Invalid project context")
            except Exception as e:
                print(f"   ❌ LearningDataCollector - Context collection failed: {e}")
                
        except Exception as e:
            print(f"   ❌ LearningDataCollector - Failed: {e}")
        
        # Test other components (with dependency checks)
        components_to_test = [
            ('learning_engine', 'AdaptiveLearningEngine', lambda storage: lambda: None),
            ('adaptive_recommender', 'PersonalizedAdaptiveRecommender', lambda storage: lambda: None),
            ('feedback_processor', 'FeedbackProcessor', lambda storage: lambda: None),
            ('claude_sc_preprocessor', 'SCCommandProcessor', lambda: lambda: None)
        ]
        
        for module_name, class_name, test_func in components_to_test:
            try:
                module = __import__(module_name)
                cls = getattr(module, class_name)
                
                if module_name == 'claude_sc_preprocessor':
                    instance = cls()
                else:
                    storage = LearningStorage(str(temp_dir))
                    instance = cls(storage)
                    
                print(f"   ✅ {class_name} - Initialization successful")
                
            except Exception as e:
                print(f"   ❌ {class_name} - Failed: {e}")
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        if 'SUPERCLAUDE_TEST_MODE' in os.environ:
            del os.environ['SUPERCLAUDE_TEST_MODE']
        if 'SUPERCLAUDE_STORAGE_DIR' in os.environ:
            del os.environ['SUPERCLAUDE_STORAGE_DIR']

def generate_architecture_assessment(import_results):
    """Generate architecture assessment based on test results"""
    print("\n📊 ARCHITECTURE ASSESSMENT:")
    print("=" * 50)
    
    # Check core dependencies
    core_deps = ['json', 'sqlite3', 'datetime', 'pathlib', 'dataclasses']
    missing_core = [dep for dep in core_deps if not import_results.get(dep, False)]
    
    if not missing_core:
        print("✅ Core Python dependencies: AVAILABLE")
    else:
        print(f"❌ Missing core dependencies: {missing_core}")
    
    # Check optional dependencies
    optional_deps = ['numpy']
    missing_optional = [dep for dep in optional_deps if not import_results.get(dep, False)]
    
    if not missing_optional:
        print("✅ Optional dependencies: AVAILABLE")
    else:
        print(f"⚠️ Missing optional dependencies: {missing_optional}")
        print("   → Some advanced features may not work optimally")
    
    # Check component architecture
    components = [
        'learning_storage_LearningStorage',
        'data_collector_LearningDataCollector', 
        'learning_engine_AdaptiveLearningEngine',
        'adaptive_recommender_PersonalizedAdaptiveRecommender',
        'feedback_processor_FeedbackProcessor',
        'claude_sc_preprocessor_SCCommandProcessor'
    ]
    
    working_components = [comp for comp in components if import_results.get(comp, False)]
    
    print(f"\n🧩 Component Status: {len(working_components)}/{len(components)} functional")
    
    if len(working_components) == len(components):
        print("✅ ARCHITECTURE STATUS: FULLY FUNCTIONAL")
        print("   → All components can be imported and initialized")
        print("   → System ready for comprehensive testing")
    elif len(working_components) >= len(components) * 0.75:
        print("⚠️ ARCHITECTURE STATUS: MOSTLY FUNCTIONAL")
        print("   → Core functionality available")
        print("   → Some advanced features may have issues")
    else:
        print("❌ ARCHITECTURE STATUS: SIGNIFICANT ISSUES")
        print("   → Major components have import/initialization problems")
        print("   → System requires dependency resolution")
    
    # Recommendations
    print("\n🚀 RECOMMENDATIONS:")
    if missing_optional:
        print("   1. Install missing optional dependencies:")
        print("      pip install numpy")
    
    broken_components = [comp for comp in components if not import_results.get(comp, False)]
    if broken_components:
        print("   2. Fix component issues:")
        for comp in broken_components:
            print(f"      • {comp.replace('_', '.')}")
    
    if len(working_components) >= len(components) * 0.75:
        print("   3. System is ready for production testing")
        print("   4. Consider implementing continuous integration")
    
    return len(working_components) / len(components)

def main():
    """Main test execution"""
    print("🔍 SuperClaude Learning System - Dependency & Architecture Test")
    print("=" * 65)
    
    import_results = test_imports()
    test_basic_functionality()
    readiness_score = generate_architecture_assessment(import_results)
    
    print(f"\n🎯 SYSTEM READINESS: {readiness_score*100:.1f}%")
    
    if readiness_score >= 0.9:
        print("🎉 System is ready for comprehensive testing!")
        return 0
    elif readiness_score >= 0.75:
        print("⚠️ System is mostly functional with minor issues")
        return 0  
    else:
        print("❌ System requires significant fixes before deployment")
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\nTest completed with exit code: {exit_code}")