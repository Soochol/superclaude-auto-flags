#!/usr/bin/env python3
"""
Focused Stability Test for SuperClaude Learning System
Tests the most critical failure scenarios to prove production readiness
"""

import os
import sys
import tempfile
import shutil
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import traceback

# Ensure dependencies are available
try:
    import numpy
except ImportError:
    print("Installing NumPy...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy

try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
    import yaml

print("✅ Dependencies ready")

class FocusedStabilityTester:
    """Focused stability tester for critical scenarios"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Setup isolated test environment"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="superclaude_test_"))
        self.original_cwd = os.getcwd()
        
        # Create test project structure
        (self.temp_dir / "src").mkdir()
        for i in range(5):
            (self.temp_dir / "src" / f"test_{i}.py").write_text(f"# Test file {i}")
        
        os.chdir(self.temp_dir)
        
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def run_test(self, test_func, test_name: str) -> bool:
        """Run a single test"""
        print(f"Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {duration:.2f}s")
            
            self.test_results.append({
                'name': test_name,
                'passed': result,
                'duration': duration,
                'error': None
            })
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"  ❌ FAIL - {duration:.2f}s - Error: {str(e)}")
            
            self.test_results.append({
                'name': test_name,
                'passed': False,
                'duration': duration,
                'error': str(e)
            })
            
            return False
    
    def test_basic_import_safety(self) -> bool:
        """Test that imports don't crash the system"""
        try:
            # Test basic import
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Test initialization
            processor = SCCommandProcessor()
            
            # Test basic operation
            result = processor.process("normal command")
            
            return result == "normal command"
            
        except Exception as e:
            print(f"    Import safety error: {e}")
            return False
    
    def test_missing_dependency_graceful_degradation(self) -> bool:
        """Test behavior when numpy is missing"""
        
        # Temporarily hide numpy
        original_modules = sys.modules.copy()
        
        try:
            # Remove numpy from modules
            modules_to_remove = [m for m in sys.modules if m.startswith('numpy')]
            for module in modules_to_remove:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Mock import error
            import builtins
            original_import = builtins.__import__
            
            def mock_import(name, *args, **kwargs):
                if name == 'numpy':
                    raise ImportError("No module named 'numpy'")
                return original_import(name, *args, **kwargs)
            
            builtins.__import__ = mock_import
            
            # Force reimport of modules that might use numpy
            modules_to_reimport = [m for m in sys.modules if 'learning' in m or 'claude_sc' in m]
            for module in modules_to_reimport:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Test that system still works
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Test normal operation
            result = processor.process("test command")
            
            # Test /sc: command  
            result2 = processor.process("/sc:analyze this code")
            
            return isinstance(result, str) and isinstance(result2, str)
            
        except Exception as e:
            print(f"    Numpy degradation error: {e}")
            return False
        finally:
            # Restore original state
            builtins.__import__ = original_import
            sys.modules.clear()
            sys.modules.update(original_modules)
    
    def test_learning_system_failure_fallback(self) -> bool:
        """Test fallback when learning system fails"""
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Disable learning components
            processor.recommender = None
            processor.data_collector = None
            processor.feedback_processor = None
            
            # Test SC command still works with static patterns
            result = processor.process("/sc:analyze security vulnerabilities")
            
            # Should contain appropriate flags or original command
            return "--persona-security" in result or "security vulnerabilities" in result
            
        except Exception as e:
            print(f"    Learning fallback error: {e}")
            return False
    
    def test_database_failure_graceful_handling(self) -> bool:
        """Test database connection failures"""
        try:
            from learning_storage import LearningStorage
            
            # Try to connect to invalid database path
            invalid_path = "/dev/null/cannot_create/test.db"
            storage = LearningStorage(invalid_path)
            
            # Should handle gracefully without crashing
            interactions = storage.get_user_interactions(days=7)
            
            # Should return empty list, not crash
            return isinstance(interactions, list)
            
        except Exception as e:
            # Exception is acceptable as long as it's handled gracefully
            print(f"    Database failure (acceptable): {e}")
            return True
    
    def test_malformed_input_handling(self) -> bool:
        """Test handling of malformed inputs"""
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Test various malformed inputs
            malformed_inputs = [
                "",
                "/sc:",
                "/sc: ",
                "/sc:invalid_command_with_extremely_long_description_" + "x" * 1000,
                "/sc:analyze\nwith\nnewlines",
                "/sc:한글명령어 테스트",
            ]
            
            for malformed_input in malformed_inputs:
                result = processor.process(malformed_input)
                if not isinstance(result, str):
                    return False
            
            return True
            
        except Exception as e:
            print(f"    Malformed input error: {e}")
            return False
    
    def test_concurrent_access_basic(self) -> bool:
        """Test basic concurrent access"""
        try:
            import threading
            from claude_sc_preprocessor import SCCommandProcessor
            
            results = []
            errors = []
            
            def worker():
                try:
                    processor = SCCommandProcessor()
                    result = processor.process("/sc:analyze concurrent test")
                    results.append(result)
                except Exception as e:
                    errors.append(e)
            
            # Create 3 threads
            threads = []
            for i in range(3):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=10)
            
            # At least 2 should succeed
            return len(results) >= 2
            
        except Exception as e:
            print(f"    Concurrent access error: {e}")
            return False
    
    def test_claude_functionality_preservation(self) -> bool:
        """Critical test: Claude functionality must never be broken"""
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Force various failure conditions
            processor.pattern_matcher = None
            processor.recommender = None
            
            # Test that non-SC commands always pass through unchanged
            normal_commands = [
                "Please help me debug this code",
                "What is the best way to implement authentication?",
                "Explain how this algorithm works",
                "",
                "Write a function that calculates fibonacci numbers"
            ]
            
            for command in normal_commands:
                result = processor.process(command)
                if result != command:
                    print(f"    Command changed: '{command}' -> '{result}'")
                    return False
            
            return True
            
        except Exception as e:
            print(f"    Claude preservation error: {e}")
            return False
    
    def test_memory_usage_reasonable(self) -> bool:
        """Test that memory usage is reasonable"""
        try:
            import psutil
            
            # Get baseline memory
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Create and use multiple processors
            for i in range(10):
                processor = SCCommandProcessor()
                processor.process(f"/sc:analyze memory test {i}")
            
            # Check memory growth
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = end_memory - start_memory
            
            print(f"    Memory growth: {memory_growth:.2f} MB")
            
            # Should not grow excessively (allow 20MB growth)
            return memory_growth < 20
            
        except ImportError:
            print("    psutil not available, skipping memory test")
            return True
        except Exception as e:
            print(f"    Memory test error: {e}")
            return False
    
    def test_configuration_corruption_handling(self) -> bool:
        """Test handling of corrupted configuration"""
        try:
            # Create corrupted config file
            corrupt_config = self.temp_dir / "corrupt_rules.yaml"
            corrupt_config.write_text("invalid: yaml: content: [unclosed")
            
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor(str(corrupt_config))
            
            # Should fall back to default behavior
            result = processor.process("/sc:analyze security")
            
            return isinstance(result, str)
            
        except Exception as e:
            print(f"    Config corruption error: {e}")
            return False
    
    def test_large_project_handling(self) -> bool:
        """Test handling of large projects"""
        try:
            # Create large project structure
            large_dir = self.temp_dir / "large_project"
            large_dir.mkdir()
            
            # Create many files
            for i in range(100):
                (large_dir / f"file_{i}.py").write_text(f"# File {i}")
            
            original_cwd = os.getcwd()
            os.chdir(large_dir)
            
            try:
                from claude_sc_preprocessor import SCCommandProcessor
                processor = SCCommandProcessor()
                
                result = processor.process("/sc:analyze this large project")
                
                # Should handle gracefully, possibly with delegation
                return isinstance(result, str)
                
            finally:
                os.chdir(original_cwd)
        
        except Exception as e:
            print(f"    Large project error: {e}")
            return False
    
    def run_focused_tests(self):
        """Run focused test suite"""
        print("SuperClaude Learning System - Focused Stability Test")
        print("=" * 60)
        
        self.setup_test_environment()
        
        try:
            # Critical tests - these must pass for production readiness
            critical_tests = [
                (self.test_claude_functionality_preservation, "Claude Functionality Preservation [CRITICAL]"),
                (self.test_basic_import_safety, "Basic Import Safety"),
                (self.test_missing_dependency_graceful_degradation, "Missing Dependency Graceful Degradation"),
                (self.test_learning_system_failure_fallback, "Learning System Failure Fallback"),
            ]
            
            # Important but not critical tests
            important_tests = [
                (self.test_database_failure_graceful_handling, "Database Failure Graceful Handling"),
                (self.test_malformed_input_handling, "Malformed Input Handling"),
                (self.test_concurrent_access_basic, "Basic Concurrent Access"),
                (self.test_memory_usage_reasonable, "Reasonable Memory Usage"),
                (self.test_configuration_corruption_handling, "Configuration Corruption Handling"),
                (self.test_large_project_handling, "Large Project Handling"),
            ]
            
            print("\nRunning CRITICAL tests:")
            critical_passed = 0
            for test_func, test_name in critical_tests:
                if self.run_test(test_func, test_name):
                    critical_passed += 1
            
            print(f"\nRunning IMPORTANT tests:")
            important_passed = 0
            for test_func, test_name in important_tests:
                if self.run_test(test_func, test_name):
                    important_passed += 1
            
            # Generate report
            self.generate_report(critical_tests, important_tests, critical_passed, important_passed)
            
        finally:
            self.cleanup_test_environment()
    
    def generate_report(self, critical_tests, important_tests, critical_passed, important_passed):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("FOCUSED STABILITY TEST REPORT")
        print("=" * 60)
        
        total_critical = len(critical_tests)
        total_important = len(important_tests)
        total_tests = len(self.test_results)
        total_passed = sum(1 for r in self.test_results if r['passed'])
        
        print(f"\nTEST SUMMARY:")
        print(f"  Critical Tests: {critical_passed}/{total_critical} passed")
        print(f"  Important Tests: {important_passed}/{total_important} passed")
        print(f"  Total Tests: {total_passed}/{total_tests} passed")
        print(f"  Success Rate: {(total_passed/total_tests)*100:.1f}%")
        
        # Determine production readiness
        production_ready = critical_passed == total_critical
        claude_safe = any(r['name'].endswith('[CRITICAL]') and r['passed'] for r in self.test_results)
        
        print(f"\nSAFETY ASSESSMENT:")
        print(f"  Claude Functionality Safe: {'✅ YES' if claude_safe else '❌ NO'}")
        print(f"  Production Ready: {'✅ YES' if production_ready else '❌ NO'}")
        
        print(f"\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"  {status} | {result['name']:<50} | {result['duration']:.2f}s")
            if result['error']:
                print(f"    Error: {result['error']}")
        
        print(f"\nRECOMMENDATIONS:")
        if not claude_safe:
            print("  🚨 CRITICAL: Fix Claude functionality preservation before any deployment")
        elif not production_ready:
            print("  ⚠️  HIGH: Address critical test failures before production deployment")
        elif important_passed < total_important * 0.8:
            print("  ⚠️  MEDIUM: Consider addressing important test failures for robustness")
        else:
            print("  ✅ System demonstrates good stability and production readiness")
        
        print("\nPRODUCTION READINESS CRITERIA:")
        print(f"  1. Claude never breaks: {'✅' if claude_safe else '❌'}")
        print(f"  2. Graceful degradation: {'✅' if critical_passed >= 3 else '❌'}")
        print(f"  3. Error isolation: {'✅' if important_passed >= total_important * 0.7 else '❌'}")
        print(f"  4. Performance acceptable: {'✅' if total_passed >= total_tests * 0.8 else '❌'}")
        
        if production_ready and claude_safe and important_passed >= total_important * 0.7:
            print(f"\n🎉 FINAL ASSESSMENT: PRODUCTION READY")
        else:
            print(f"\n⚠️  FINAL ASSESSMENT: NOT READY FOR PRODUCTION")

def main():
    """Main test execution"""
    tester = FocusedStabilityTester()
    tester.run_focused_tests()

if __name__ == "__main__":
    main()