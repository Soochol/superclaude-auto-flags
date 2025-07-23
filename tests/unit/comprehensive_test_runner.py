#!/usr/bin/env python3
"""
Comprehensive Test Runner for SuperClaude Learning System
Systematically tests each component with detailed error reporting
"""

import sys
import os
import tempfile
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

class ComponentTestResult:
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.passed_tests = []
        self.failed_tests = []
        self.errors = []
        
    def add_success(self, test_name: str):
        self.passed_tests.append(test_name)
        
    def add_failure(self, test_name: str, error: str):
        self.failed_tests.append((test_name, error))
        
    def add_error(self, error: str):
        self.errors.append(error)
    
    @property
    def success_rate(self) -> float:
        total = len(self.passed_tests) + len(self.failed_tests)
        return len(self.passed_tests) / total if total > 0 else 0.0
    
    @property
    def is_functional(self) -> bool:
        return len(self.passed_tests) > 0 and len(self.errors) == 0

class ComprehensiveTestRunner:
    def __init__(self):
        self.results: Dict[str, ComponentTestResult] = {}
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Setup isolated test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ['SUPERCLAUDE_TEST_MODE'] = '1'
        os.environ['SUPERCLAUDE_STORAGE_DIR'] = str(self.temp_dir)
        print(f"🔧 Test environment setup at: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        if 'SUPERCLAUDE_TEST_MODE' in os.environ:
            del os.environ['SUPERCLAUDE_TEST_MODE']
        if 'SUPERCLAUDE_STORAGE_DIR' in os.environ:
            del os.environ['SUPERCLAUDE_STORAGE_DIR']
        print("🧹 Test environment cleaned up")
    
    def test_learning_storage(self) -> ComponentTestResult:
        """Test LearningStorage component"""
        result = ComponentTestResult("LearningStorage")
        
        try:
            from learning_storage import LearningStorage, UserInteraction
            result.add_success("Import successful")
            
            # Test database creation
            try:
                storage = LearningStorage(str(self.temp_dir))
                result.add_success("Database initialization")
                
                # Test database file creation
                db_path = self.temp_dir / 'superclaude_learning.db'
                if db_path.exists():
                    result.add_success("Database file created")
                else:
                    result.add_failure("Database file creation", "Database file not found")
                
                # Test table creation
                try:
                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [row[0] for row in cursor.fetchall()]
                        
                        expected_tables = ['interactions', 'feedback', 'pattern_success', 'user_preferences']
                        missing_tables = [t for t in expected_tables if t not in tables]
                        
                        if not missing_tables:
                            result.add_success("All required tables created")
                        else:
                            result.add_failure("Table creation", f"Missing tables: {missing_tables}")
                except Exception as e:
                    result.add_failure("Table verification", str(e))
                
                # Test basic interaction recording
                try:
                    interaction = UserInteraction(
                        timestamp=datetime.now().isoformat(),
                        user_input="/sc:analyze test",
                        command="analyze",
                        description="test",
                        recommended_flags="--persona-analyzer",
                        actual_flags="--persona-analyzer",
                        project_context={"test": True},
                        success=True,
                        execution_time=15.0,
                        confidence=80,
                        reasoning="test",
                        user_id=storage.user_id,
                        project_hash="test_hash"
                    )
                    
                    interaction_id = storage.record_interaction(interaction)
                    if interaction_id:
                        result.add_success("Interaction recording")
                    else:
                        result.add_failure("Interaction recording", "No interaction ID returned")
                        
                    # Test interaction retrieval
                    interactions = storage.get_user_interactions(days=1)
                    if len(interactions) > 0:
                        result.add_success("Interaction retrieval")
                    else:
                        result.add_failure("Interaction retrieval", "No interactions found")
                        
                except Exception as e:
                    result.add_failure("Interaction operations", str(e))
                    
            except Exception as e:
                result.add_failure("Storage initialization", str(e))
                
        except ImportError as e:
            result.add_error(f"Import error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error: {e}")
            
        return result
    
    def test_data_collector(self) -> ComponentTestResult:
        """Test LearningDataCollector component"""
        result = ComponentTestResult("LearningDataCollector")
        
        try:
            from data_collector import LearningDataCollector
            from learning_storage import LearningStorage
            result.add_success("Import successful")
            
            try:
                storage = LearningStorage(str(self.temp_dir))
                collector = LearningDataCollector(storage)
                result.add_success("Component initialization")
                
                # Test project context collection
                try:
                    context = collector.collect_project_context(str(Path.cwd()))
                    required_keys = ['project_hash', 'file_count', 'languages']
                    missing_keys = [k for k in required_keys if k not in context]
                    
                    if not missing_keys:
                        result.add_success("Project context collection")
                    else:
                        result.add_failure("Project context collection", f"Missing keys: {missing_keys}")
                except Exception as e:
                    result.add_failure("Project context collection", str(e))
                
                # Test interaction lifecycle
                try:
                    interaction_id = collector.start_interaction(
                        user_input="/sc:analyze test code",
                        recommended_flags="--persona-analyzer",
                        confidence=85,
                        reasoning="test",
                        project_context={"test": True}
                    )
                    
                    if interaction_id:
                        result.add_success("Interaction start")
                        
                        # Test interaction end
                        collector.end_interaction(
                            actual_flags="--persona-analyzer",
                            success=True,
                            error_message=None
                        )
                        result.add_success("Interaction end")
                    else:
                        result.add_failure("Interaction start", "No interaction ID returned")
                        
                except Exception as e:
                    result.add_failure("Interaction lifecycle", str(e))
                    
            except Exception as e:
                result.add_failure("Collector initialization", str(e))
                
        except ImportError as e:
            result.add_error(f"Import error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error: {e}")
            
        return result
    
    def test_learning_engine(self) -> ComponentTestResult:
        """Test AdaptiveLearningEngine component"""
        result = ComponentTestResult("AdaptiveLearningEngine")
        
        try:
            from learning_engine import AdaptiveLearningEngine
            from learning_storage import LearningStorage
            result.add_success("Import successful")
            
            try:
                storage = LearningStorage(str(self.temp_dir))
                engine = AdaptiveLearningEngine(storage)
                result.add_success("Component initialization")
                
                # Test basic recommendation
                try:
                    recommendation = engine.get_adaptive_recommendation(
                        command="analyze",
                        description="security issues",
                        project_context={
                            "project_type": "python_backend",
                            "complexity": "moderate",
                            "file_count": 25
                        }
                    )
                    
                    if hasattr(recommendation, 'flags') and recommendation.flags:
                        result.add_success("Basic recommendation generation")
                    else:
                        result.add_failure("Basic recommendation generation", "No flags in recommendation")
                        
                    if hasattr(recommendation, 'confidence') and recommendation.confidence > 0:
                        result.add_success("Confidence scoring")
                    else:
                        result.add_failure("Confidence scoring", "Invalid confidence score")
                        
                    if hasattr(recommendation, 'reasoning') and isinstance(recommendation.reasoning, list):
                        result.add_success("Reasoning generation")
                    else:
                        result.add_failure("Reasoning generation", "Invalid reasoning format")
                        
                except Exception as e:
                    result.add_failure("Recommendation generation", str(e))
                    
            except Exception as e:
                result.add_failure("Engine initialization", str(e))
                
        except ImportError as e:
            result.add_error(f"Import error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error: {e}")
            
        return result
    
    def test_personalized_recommender(self) -> ComponentTestResult:
        """Test PersonalizedAdaptiveRecommender component"""
        result = ComponentTestResult("PersonalizedRecommender")
        
        try:
            from adaptive_recommender import PersonalizedAdaptiveRecommender
            from learning_storage import LearningStorage
            result.add_success("Import successful")
            
            try:
                storage = LearningStorage(str(self.temp_dir))
                recommender = PersonalizedAdaptiveRecommender(storage)
                result.add_success("Component initialization")
                
                # Test personalized recommendation
                try:
                    recommendation = recommender.get_personalized_recommendation(
                        user_input="/sc:analyze security vulnerabilities",
                        project_context={
                            "project_type": "python_backend",
                            "complexity": "complex",
                            "file_count": 150
                        }
                    )
                    
                    if hasattr(recommendation, 'flags') and recommendation.flags:
                        result.add_success("Personalized recommendation generation")
                    else:
                        result.add_failure("Personalized recommendation generation", "No flags in recommendation")
                        
                    if hasattr(recommendation, 'personalization_factors'):
                        result.add_success("Personalization factors")
                    else:
                        result.add_failure("Personalization factors", "No personalization factors found")
                        
                except Exception as e:
                    result.add_failure("Personalized recommendation", str(e))
                    
            except Exception as e:
                result.add_failure("Recommender initialization", str(e))
                
        except ImportError as e:
            result.add_error(f"Import error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error: {e}")
            
        return result
    
    def test_feedback_processor(self) -> ComponentTestResult:
        """Test FeedbackProcessor component"""
        result = ComponentTestResult("FeedbackProcessor")
        
        try:
            from feedback_processor import FeedbackProcessor
            from learning_storage import LearningStorage
            result.add_success("Import successful")
            
            try:
                storage = LearningStorage(str(self.temp_dir))
                processor = FeedbackProcessor(storage)
                result.add_success("Component initialization")
                
                # Test immediate feedback processing
                try:
                    feedback = processor.process_immediate_feedback(
                        interaction_id="test_interaction_1",
                        success=True,
                        execution_time=20.5,
                        error_details=None
                    )
                    
                    if hasattr(feedback, 'feedback_id') and feedback.feedback_id:
                        result.add_success("Immediate feedback processing")
                    else:
                        result.add_failure("Immediate feedback processing", "No feedback ID generated")
                        
                    if hasattr(feedback, 'learning_weight') and feedback.learning_weight > 0:
                        result.add_success("Learning weight calculation")
                    else:
                        result.add_failure("Learning weight calculation", "Invalid learning weight")
                        
                except Exception as e:
                    result.add_failure("Immediate feedback processing", str(e))
                
                # Test explicit feedback processing
                try:
                    explicit_feedback = processor.process_explicit_feedback(
                        interaction_id="test_interaction_2",
                        user_rating=4,
                        user_correction=None
                    )
                    
                    if hasattr(explicit_feedback, 'feedback_id') and explicit_feedback.feedback_id:
                        result.add_success("Explicit feedback processing")
                    else:
                        result.add_failure("Explicit feedback processing", "No feedback ID generated")
                        
                except Exception as e:
                    result.add_failure("Explicit feedback processing", str(e))
                    
            except Exception as e:
                result.add_failure("Processor initialization", str(e))
                
        except ImportError as e:
            result.add_error(f"Import error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error: {e}")
            
        return result
    
    def test_command_processor(self) -> ComponentTestResult:
        """Test SCCommandProcessor component"""
        result = ComponentTestResult("SCCommandProcessor")
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            result.add_success("Import successful")
            
            try:
                processor = SCCommandProcessor()
                result.add_success("Component initialization")
                
                # Test /sc: command processing
                try:
                    user_input = "/sc:analyze 이 코드의 보안 문제점을 찾아줘"
                    processed_result = processor.process(user_input)
                    
                    if processed_result and "SuperClaude" in processed_result:
                        result.add_success("/sc: command processing")
                    else:
                        result.add_failure("/sc: command processing", "Invalid processing result")
                        
                    if "--persona-" in processed_result:
                        result.add_success("Persona recommendation")
                    else:
                        result.add_failure("Persona recommendation", "No persona flags found")
                        
                except Exception as e:
                    result.add_failure("Command processing", str(e))
                
                # Test normal command passthrough
                try:
                    normal_input = "normal command"
                    normal_result = processor.process(normal_input)
                    
                    if normal_result == normal_input:
                        result.add_success("Normal command passthrough")
                    else:
                        result.add_failure("Normal command passthrough", "Command was modified incorrectly")
                        
                except Exception as e:
                    result.add_failure("Normal command handling", str(e))
                    
            except Exception as e:
                result.add_failure("Processor initialization", str(e))
                
        except ImportError as e:
            result.add_error(f"Import error: {e}")
        except Exception as e:
            result.add_error(f"Unexpected error: {e}")
            
        return result
    
    def run_all_tests(self) -> Dict[str, ComponentTestResult]:
        """Run all component tests"""
        print("🧪 SuperClaude Learning System - Comprehensive Component Test")
        print("=" * 70)
        
        self.setup_test_environment()
        
        try:
            # Test each component
            test_methods = [
                ("LearningStorage", self.test_learning_storage),
                ("LearningDataCollector", self.test_data_collector),
                ("AdaptiveLearningEngine", self.test_learning_engine),
                ("PersonalizedRecommender", self.test_personalized_recommender),
                ("FeedbackProcessor", self.test_feedback_processor),
                ("SCCommandProcessor", self.test_command_processor),
            ]
            
            for component_name, test_method in test_methods:
                print(f"\n🔍 Testing {component_name}...")
                self.results[component_name] = test_method()
                
                result = self.results[component_name]
                status = "✅ FUNCTIONAL" if result.is_functional else "❌ ISSUES"
                print(f"   {status} - {len(result.passed_tests)} passed, {len(result.failed_tests)} failed, {len(result.errors)} errors")
                
        finally:
            self.cleanup_test_environment()
            
        return self.results
    
    def generate_report(self) -> str:
        """Generate detailed test report"""
        report = []
        report.append("=" * 70)
        report.append("📊 SUPERCLAUDE LEARNING SYSTEM TEST REPORT")
        report.append("=" * 70)
        
        total_components = len(self.results)
        functional_components = sum(1 for r in self.results.values() if r.is_functional)
        
        report.append(f"\n🎯 OVERALL SYSTEM STATUS:")
        report.append(f"   • Total Components: {total_components}")
        report.append(f"   • Functional Components: {functional_components}")
        report.append(f"   • System Readiness: {functional_components/total_components*100:.1f}%")
        
        if functional_components == total_components:
            report.append("   • ✅ SYSTEM READY FOR DEPLOYMENT")
        elif functional_components >= total_components * 0.75:
            report.append("   • ⚠️ SYSTEM MOSTLY FUNCTIONAL - Minor issues to resolve")
        else:
            report.append("   • ❌ SYSTEM NOT READY - Major issues require attention")
        
        report.append("\n📋 COMPONENT DETAILS:")
        
        for component_name, result in self.results.items():
            report.append(f"\n🔧 {component_name}:")
            report.append(f"   Status: {'✅ Functional' if result.is_functional else '❌ Issues Found'}")
            report.append(f"   Success Rate: {result.success_rate*100:.1f}%")
            
            if result.passed_tests:
                report.append(f"   ✅ Passed Tests ({len(result.passed_tests)}):")
                for test in result.passed_tests:
                    report.append(f"      • {test}")
            
            if result.failed_tests:
                report.append(f"   ❌ Failed Tests ({len(result.failed_tests)}):")
                for test, error in result.failed_tests:
                    report.append(f"      • {test}: {error}")
            
            if result.errors:
                report.append(f"   💥 Critical Errors ({len(result.errors)}):")
                for error in result.errors:
                    report.append(f"      • {error}")
        
        report.append("\n🔍 ARCHITECTURE ASSESSMENT:")
        
        core_components = ["LearningStorage", "LearningDataCollector", "AdaptiveLearningEngine"]
        core_functional = all(self.results.get(comp, ComponentTestResult(comp)).is_functional for comp in core_components)
        
        if core_functional:
            report.append("   ✅ Core learning architecture is sound")
        else:
            report.append("   ❌ Core learning architecture has issues")
        
        integration_components = ["PersonalizedRecommender", "FeedbackProcessor", "SCCommandProcessor"]
        integration_functional = all(self.results.get(comp, ComponentTestResult(comp)).is_functional for comp in integration_components)
        
        if integration_functional:
            report.append("   ✅ Integration layer is functional")
        else:
            report.append("   ⚠️ Integration layer has some issues")
        
        report.append("\n🚀 RECOMMENDATIONS:")
        
        for component_name, result in self.results.items():
            if not result.is_functional:
                if result.errors:
                    report.append(f"   • {component_name}: Fix critical import/initialization errors first")
                elif result.failed_tests:
                    report.append(f"   • {component_name}: Address failing tests to improve reliability")
        
        if functional_components == total_components:
            report.append("   • System is ready for production use")
            report.append("   • Consider adding performance optimization tests")
            report.append("   • Implement continuous integration testing")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)

def main():
    """Main test execution"""
    runner = ComprehensiveTestRunner()
    results = runner.run_all_tests()
    report = runner.generate_report()
    
    print(report)
    
    # Save report to file
    report_file = Path("comprehensive_test_report.md")
    report_file.write_text(report)
    print(f"\n📄 Full report saved to: {report_file.absolute()}")
    
    # Return success/failure code
    functional_count = sum(1 for r in results.values() if r.is_functional)
    total_count = len(results)
    
    return 0 if functional_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())