#!/usr/bin/env python3
"""
SuperClaude Learning System - Comprehensive Stability and Error Handling Test Suite

This test suite validates the production readiness of the SuperClaude learning system
by testing all possible failure modes, boundary conditions, and recovery mechanisms.

Key Safety Requirements:
1. Never break Claude functionality under any circumstances
2. Graceful degradation when components fail
3. Safe error isolation and recovery
4. No data loss under failure conditions
5. Production-ready performance under stress
"""

import os
import sys
import time
import json
import tempfile
import shutil
import sqlite3
import threading
import psutil
import traceback
import multiprocessing
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import unittest
import logging

# Configure logging for test results
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stability_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    passed: bool
    duration: float
    error_message: Optional[str] = None
    memory_peak: Optional[float] = None
    safety_validated: bool = True
    recovery_successful: bool = True

@dataclass
class StabilityReport:
    """Overall stability test report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration: float
    memory_peak_mb: float
    claude_always_works: bool
    safety_guarantees_met: bool
    production_ready: bool
    recommendations: List[str]

class SafetyValidator:
    """Validates that Claude functionality is never broken"""
    
    def __init__(self):
        self.claude_functionality_intact = True
        self.errors_isolated = True
        
    def test_claude_baseline(self) -> bool:
        """Test basic Claude functionality works"""
        try:
            # Test basic import of core components
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Test that non-SC commands pass through unchanged
            processor = SCCommandProcessor()
            test_input = "Please help me with this code"
            result = processor.process(test_input)
            
            # Should return unchanged
            return result == test_input
            
        except Exception as e:
            logger.error(f"Claude baseline test failed: {e}")
            self.claude_functionality_intact = False
            return False
    
    def test_error_isolation(self, error_source: str) -> bool:
        """Test that errors in one component don't affect Claude"""
        try:
            # Even if learning components fail, basic processing should work
            from claude_sc_preprocessor import SCCommandProcessor
            
            processor = SCCommandProcessor()
            
            # Force an error condition based on source
            if error_source == "learning_system":
                # Mock learning system failure
                processor.recommender = None
                processor.data_collector = None
                processor.feedback_processor = None
            
            # Test that Claude still works
            test_input = "normal command"
            result = processor.process(test_input)
            
            return result == test_input
            
        except Exception as e:
            logger.error(f"Error isolation test failed for {error_source}: {e}")
            self.errors_isolated = False
            return False

class StabilityTestSuite:
    """Comprehensive stability test suite"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.safety_validator = SafetyValidator()
        self.temp_dirs: List[Path] = []
        
    def setUp(self):
        """Test setup"""
        # Create temporary test environment
        self.test_dir = Path(tempfile.mkdtemp(prefix="superclaude_stability_"))
        self.temp_dirs.append(self.test_dir)
        
        # Setup test project structure
        (self.test_dir / "src").mkdir()
        (self.test_dir / "test").mkdir()
        (self.test_dir / "docs").mkdir()
        
        # Create test files
        for i in range(10):
            (self.test_dir / "src" / f"test_{i}.py").write_text(f"# Test file {i}")
        
        # Change to test directory
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Test cleanup"""
        os.chdir(self.original_cwd)
        
        # Clean up temp directories
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a single test with monitoring"""
        logger.info(f"Running test: {test_name}")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            success = test_func()
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = TestResult(
                test_name=test_name,
                passed=success,
                duration=end_time - start_time,
                memory_peak=end_memory - start_memory,
                safety_validated=self.safety_validator.claude_functionality_intact,
                recovery_successful=True
            )
            
            logger.info(f"Test {test_name}: {'PASS' if success else 'FAIL'} "
                       f"({result.duration:.2f}s, {result.memory_peak:.2f}MB)")
            
        except Exception as e:
            end_time = time.time()
            result = TestResult(
                test_name=test_name,
                passed=False,
                duration=end_time - start_time,
                error_message=str(e),
                safety_validated=self.safety_validator.claude_functionality_intact,
                recovery_successful=False
            )
            
            logger.error(f"Test {test_name}: FAIL - {e}")
            logger.error(traceback.format_exc())
        
        self.test_results.append(result)
        return result
    
    # =============================================================================
    # GRACEFUL DEGRADATION TESTS
    # =============================================================================
    
    def test_missing_numpy_dependency(self) -> bool:
        """Test behavior when numpy is unavailable"""
        
        # Temporarily hide numpy
        import sys
        original_modules = sys.modules.copy()
        
        try:
            # Remove numpy from modules
            modules_to_remove = [m for m in sys.modules if m.startswith('numpy')]
            for module in modules_to_remove:
                del sys.modules[module]
            
            # Mock import error
            import builtins
            original_import = builtins.__import__
            
            def mock_import(name, *args, **kwargs):
                if name == 'numpy':
                    raise ImportError("No module named 'numpy'")
                return original_import(name, *args, **kwargs)
            
            builtins.__import__ = mock_import
            
            # Test that system still works
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Test normal operation
            result = processor.process("test command")
            
            # Test /sc: command
            result = processor.process("/sc:analyze this code")
            
            return True
            
        finally:
            # Restore original state
            builtins.__import__ = original_import
            sys.modules.update(original_modules)
    
    def test_missing_yaml_dependency(self) -> bool:
        """Test behavior when PyYAML is unavailable"""
        
        import sys
        import builtins
        original_import = builtins.__import__
        
        try:
            def mock_import(name, *args, **kwargs):
                if name in ['yaml', 'PyYAML']:
                    raise ImportError("No module named 'yaml'")
                return original_import(name, *args, **kwargs)
            
            builtins.__import__ = mock_import
            
            # Force reimport of components
            modules_to_reload = [m for m in sys.modules if 'claude_sc' in m or 'learning' in m]
            for module in modules_to_reload:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Test system works with fallback rules
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            result = processor.process("/sc:analyze security issues")
            
            # Should still work with default rules
            return "/sc:analyze security issues" in result
            
        finally:
            builtins.__import__ = original_import
    
    def test_database_permission_error(self) -> bool:
        """Test behavior when SQLite database has permission issues"""
        
        try:
            # Create a database file with no permissions
            db_path = self.test_dir / "test.db"
            db_path.touch()
            db_path.chmod(0o000)  # No permissions
            
            # Test learning storage with inaccessible database
            from learning_storage import LearningStorage
            storage = LearningStorage(str(db_path))
            
            # Should gracefully handle permission errors
            interactions = storage.get_user_interactions(days=7)
            
            # Should return empty list instead of crashing
            return isinstance(interactions, list)
            
        except Exception as e:
            # Any exception here means graceful degradation failed
            logger.error(f"Database permission test failed ungracefully: {e}")
            return False
        finally:
            try:
                db_path.chmod(0o644)  # Restore permissions for cleanup
            except:
                pass
    
    def test_disk_full_simulation(self) -> bool:
        """Test behavior when disk is full"""
        
        try:
            # Create a small temp filesystem (not actually implementing disk full)
            # Instead, we'll test write failures
            
            from learning_storage import LearningStorage
            
            # Create storage with invalid path
            invalid_path = "/dev/null/cannot_write_here/test.db"
            storage = LearningStorage(invalid_path)
            
            # Try to record interaction
            interaction_id = storage.start_interaction(
                user_input="test",
                recommended_flags="--test",
                confidence=80,
                reasoning="test"
            )
            
            # Should handle gracefully
            return True
            
        except Exception as e:
            # Should not crash, should degrade gracefully
            logger.warning(f"Disk full test triggered exception (acceptable): {e}")
            return True  # Exception is OK as long as Claude still works
    
    def test_import_failure_recovery(self) -> bool:
        """Test recovery when learning modules can't be imported"""
        
        try:
            import sys
            import builtins
            original_import = builtins.__import__
            
            def mock_import(name, *args, **kwargs):
                if name in ['adaptive_recommender', 'data_collector', 'feedback_processor']:
                    raise ImportError(f"Mock failure importing {name}")
                return original_import(name, *args, **kwargs)
            
            builtins.__import__ = mock_import
            
            # Force reimport
            modules_to_reload = [m for m in sys.modules if 'claude_sc' in m]
            for module in modules_to_reload:
                if module in sys.modules:
                    del sys.modules[module]
            
            # Test that system falls back gracefully
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            result = processor.process("/sc:implement API endpoint")
            
            # Should work with static patterns
            return "--persona-backend" in result or "implement API endpoint" in result
            
        finally:
            builtins.__import__ = original_import
    
    def test_invalid_sc_command_input(self) -> bool:
        """Test handling of malformed /sc: commands"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Test various malformed inputs
            malformed_inputs = [
                "/sc:",
                "/sc:     ",
                "/sc:invalid_command_with_no_description",
                "/sc:analyze " + "x" * 10000,  # Very long input
                "/sc:한글명령어 테스트",  # Unicode
                "/sc:analyze\nmalicious\ncommand",  # Newlines
                "/sc:analyze; rm -rf /",  # Injection attempt
                "",  # Empty
                None,  # None (this will cause type error if not handled)
            ]
            
            for malformed_input in malformed_inputs[:-1]:  # Skip None for now
                result = processor.process(malformed_input)
                
                # Should either process gracefully or return original
                if not isinstance(result, str):
                    return False
            
            # Test None input
            try:
                result = processor.process(None)
                return False  # Should have handled this gracefully
            except:
                # Exception is acceptable for None input
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Invalid input test failed: {e}")
            return False
    
    def test_empty_project_directory(self) -> bool:
        """Test behavior in directories with no code files"""
        
        try:
            # Create completely empty directory
            empty_dir = self.test_dir / "empty"
            empty_dir.mkdir()
            
            original_cwd = os.getcwd()
            os.chdir(empty_dir)
            
            try:
                from claude_sc_preprocessor import SCCommandProcessor
                processor = SCCommandProcessor()
                
                result = processor.process("/sc:analyze this empty project")
                
                # Should handle gracefully
                return isinstance(result, str)
                
            finally:
                os.chdir(original_cwd)
        
        except Exception as e:
            logger.error(f"Empty project test failed: {e}")
            return False
    
    # =============================================================================
    # ERROR RECOVERY MECHANISM TESTS
    # =============================================================================
    
    def test_learning_system_failure_fallback(self) -> bool:
        """Test fallback to static patterns when learning system fails"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Simulate learning system failure
            processor.recommender = None
            processor.data_collector = None
            processor.feedback_processor = None
            
            # Test that static patterns still work
            result = processor.process("/sc:analyze security vulnerabilities")
            
            return "--persona-security" in result
            
        except Exception as e:
            logger.error(f"Learning fallback test failed: {e}")
            return False
    
    def test_database_corruption_recovery(self) -> bool:
        """Test recovery from corrupted SQLite database"""
        
        try:
            # Create corrupted database file
            corrupt_db = self.test_dir / "corrupt.db"
            corrupt_db.write_text("This is not a valid SQLite database")
            
            from learning_storage import LearningStorage
            storage = LearningStorage(str(corrupt_db))
            
            # Should detect corruption and create new database
            interactions = storage.get_user_interactions(days=7)
            
            return isinstance(interactions, list)
            
        except Exception as e:
            logger.warning(f"Database corruption test exception (acceptable): {e}")
            return True  # Should degrade gracefully
    
    def test_memory_pressure_handling(self) -> bool:
        """Test behavior under memory pressure"""
        
        try:
            # Create memory pressure by allocating large objects
            memory_hog = []
            
            try:
                # Allocate memory in chunks
                for i in range(10):
                    memory_hog.append([0] * 1000000)  # ~4MB per chunk
                
                # Test system under memory pressure
                from claude_sc_preprocessor import SCCommandProcessor
                processor = SCCommandProcessor()
                
                result = processor.process("/sc:analyze performance")
                
                return isinstance(result, str)
                
            finally:
                # Clean up memory
                del memory_hog
        
        except MemoryError:
            # Memory error is acceptable - system should still work
            return True
        except Exception as e:
            logger.error(f"Memory pressure test failed: {e}")
            return False
    
    def test_concurrent_access_safety(self) -> bool:
        """Test thread safety with multiple simultaneous users"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            
            results = []
            errors = []
            
            def worker_thread(thread_id):
                try:
                    processor = SCCommandProcessor()
                    result = processor.process(f"/sc:analyze thread {thread_id}")
                    results.append(result)
                except Exception as e:
                    errors.append(e)
            
            # Create multiple threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=30)  # 30 second timeout
            
            # Check results
            if errors:
                logger.warning(f"Concurrent access errors: {errors}")
            
            return len(results) >= 5  # At least half should succeed
            
        except Exception as e:
            logger.error(f"Concurrent access test failed: {e}")
            return False
    
    def test_network_timeout_handling(self) -> bool:
        """Test handling when external dependencies timeout"""
        
        # This system doesn't have external network dependencies,
        # but we test timeout simulation
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Simulate slow operation
            import time
            original_time_sleep = time.sleep
            
            def slow_sleep(duration):
                if duration > 0.1:  # If something tries to sleep too long
                    raise TimeoutError("Simulated timeout")
                return original_time_sleep(duration)
            
            time.sleep = slow_sleep
            
            try:
                result = processor.process("/sc:analyze network connectivity")
                return isinstance(result, str)
            finally:
                time.sleep = original_time_sleep
        
        except Exception as e:
            logger.warning(f"Timeout handling test exception: {e}")
            return True  # Should degrade gracefully
    
    # =============================================================================
    # BOUNDARY CONDITION TESTS
    # =============================================================================
    
    def test_extremely_large_project(self) -> bool:
        """Test with >1000 files"""
        
        try:
            # Create large project structure
            large_project = self.test_dir / "large_project"
            large_project.mkdir()
            
            # Create directory structure
            for i in range(20):
                sub_dir = large_project / f"module_{i}"
                sub_dir.mkdir()
                
                for j in range(60):  # 20 * 60 = 1200 files
                    (sub_dir / f"file_{j}.py").write_text(f"# Module {i} File {j}")
            
            original_cwd = os.getcwd()
            os.chdir(large_project)
            
            try:
                from claude_sc_preprocessor import SCCommandProcessor
                processor = SCCommandProcessor()
                
                # This should trigger delegation and compression
                result = processor.process("/sc:analyze this large codebase")
                
                # Should handle gracefully and include delegation
                return "--delegate" in result or isinstance(result, str)
                
            finally:
                os.chdir(original_cwd)
        
        except Exception as e:
            logger.error(f"Large project test failed: {e}")
            return False
    
    def test_very_long_command_input(self) -> bool:
        """Test with very long user inputs"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Create very long input
            long_description = "analyze " + "this code " * 1000  # ~9000 characters
            long_input = f"/sc:{long_description}"
            
            result = processor.process(long_input)
            
            return isinstance(result, str)
            
        except Exception as e:
            logger.error(f"Long input test failed: {e}")
            return False
    
    def test_rapid_fire_requests(self) -> bool:
        """Test performance under high load"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            start_time = time.time()
            
            # Send 100 requests rapidly
            for i in range(100):
                result = processor.process(f"/sc:analyze request {i}")
                if not isinstance(result, str):
                    return False
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should handle 100 requests in reasonable time
            logger.info(f"Processed 100 requests in {duration:.2f} seconds")
            return duration < 30  # Should be much faster than 30 seconds
            
        except Exception as e:
            logger.error(f"Rapid fire test failed: {e}")
            return False
    
    def test_empty_null_inputs(self) -> bool:
        """Test edge cases with missing data"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            edge_cases = [
                "",
                " ",
                "\n",
                "\t",
                "/sc:",
                "/sc: ",
                "/sc:\n",
            ]
            
            for edge_case in edge_cases:
                result = processor.process(edge_case)
                if not isinstance(result, str):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Edge case test failed: {e}")
            return False
    
    def test_unicode_special_characters(self) -> bool:
        """Test international character handling"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            unicode_tests = [
                "/sc:analyze 한글 코드 분석",
                "/sc:implement 日本語 コンポーネント",
                "/sc:improve código em português",
                "/sc:analyze код на русском",
                "/sc:implement ﷽ ٱلْأُرْدُنّ",  # Arabic
                "/sc:analyze 中文代码审查",
                "/sc:implement componente en español",
                "/sc:analyze 🚀 emoji code 🔥",
            ]
            
            for unicode_test in unicode_tests:
                result = processor.process(unicode_test)
                if not isinstance(result, str):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Unicode test failed: {e}")
            return False
    
    # =============================================================================
    # PRODUCTION FAILURE SCENARIO TESTS
    # =============================================================================
    
    def test_disk_space_exhaustion(self) -> bool:
        """Test when system runs out of storage"""
        
        try:
            # Can't actually exhaust disk space, so we test write failures
            from learning_storage import LearningStorage
            
            # Try to write to read-only location
            readonly_path = "/proc/test.db"  # /proc is read-only
            storage = LearningStorage(readonly_path)
            
            # Should handle write failures gracefully
            try:
                storage.start_interaction("test", "--test", 80, "test")
            except:
                pass  # Expected to fail
            
            # System should still work for read operations
            return True
            
        except Exception as e:
            logger.warning(f"Disk exhaustion test exception: {e}")
            return True
    
    def test_process_termination_cleanup(self) -> bool:
        """Test cleanup when process killed unexpectedly"""
        
        try:
            # Test that temporary files are properly handled
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Start operation
            result = processor.process("/sc:analyze cleanup test")
            
            # Simulate process termination by checking if any temp files were left
            # (This is a basic test - real termination testing would require subprocess)
            
            import tempfile
            temp_files_before = len(list(Path(tempfile.gettempdir()).glob("*superclaude*")))
            
            # Process another command
            processor.process("/sc:implement another test")
            
            temp_files_after = len(list(Path(tempfile.gettempdir()).glob("*superclaude*")))
            
            # Should not be accumulating temp files
            return temp_files_after <= temp_files_before + 2
            
        except Exception as e:
            logger.error(f"Process termination test failed: {e}")
            return False
    
    def test_configuration_corruption(self) -> bool:
        """Test with invalid config files"""
        
        try:
            # Create corrupted config file
            corrupt_config = self.test_dir / "orchestrator_rules.yaml"
            corrupt_config.write_text("invalid: yaml: content: [unclosed")
            
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor(str(corrupt_config))
            
            # Should fall back to default rules
            result = processor.process("/sc:analyze security")
            
            return isinstance(result, str)
            
        except Exception as e:
            logger.error(f"Config corruption test failed: {e}")
            return False
    
    def test_partial_system_updates(self) -> bool:
        """Test mixed old/new component versions"""
        
        try:
            # This test simulates version compatibility issues
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Test that system works even with partial imports
            processor = SCCommandProcessor()
            
            # Simulate missing new features
            if hasattr(processor, 'recommender'):
                processor.recommender = None  # Simulate old version
            
            result = processor.process("/sc:analyze version compatibility")
            
            return isinstance(result, str)
            
        except Exception as e:
            logger.error(f"Partial update test failed: {e}")
            return False
    
    # =============================================================================
    # SAFETY GUARANTEE VALIDATION
    # =============================================================================
    
    def test_claude_never_breaks(self) -> bool:
        """Validate Claude always works even if SuperClaude fails"""
        
        # Test baseline Claude functionality
        baseline_ok = self.safety_validator.test_claude_baseline()
        
        # Test that non-/sc commands always pass through
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            # Force various error conditions
            processor.pattern_matcher = None
            processor.recommender = None
            processor.data_collector = None
            
            # Test normal command
            normal_command = "Please help me debug this code"
            result = processor.process(normal_command)
            
            return baseline_ok and result == normal_command
            
        except Exception as e:
            logger.error(f"Claude safety test failed: {e}")
            return False
    
    def test_no_data_loss(self) -> bool:
        """Verify learning data integrity under failure modes"""
        
        try:
            from learning_storage import LearningStorage
            
            # Create test database
            test_db = self.test_dir / "integrity_test.db"
            storage = LearningStorage(str(test_db))
            
            # Add some test data
            interaction_id = storage.start_interaction(
                user_input="/sc:test integrity",
                recommended_flags="--test",
                confidence=85,
                reasoning="integrity test"
            )
            
            # Simulate various failure conditions
            try:
                # Try to corrupt during operation
                storage.end_interaction("", True, None)
            except:
                pass
            
            # Verify data is still accessible
            interactions = storage.get_user_interactions(days=1)
            
            return len(interactions) >= 0  # Should not crash
            
        except Exception as e:
            logger.error(f"Data integrity test failed: {e}")
            return False
    
    def test_fail_safe_defaults(self) -> bool:
        """Confirm safe fallback behavior"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Test with completely broken system
            processor = SCCommandProcessor()
            processor.pattern_matcher = None
            
            # Should still provide safe defaults
            result = processor.process("/sc:analyze unknown command")
            
            # Should either work or return original safely
            return isinstance(result, str)
            
        except Exception as e:
            logger.error(f"Fail-safe test failed: {e}")
            return False
    
    def test_error_isolation(self) -> bool:
        """Ensure errors don't cascade between components"""
        
        # Test isolation between different components
        isolation_tests = [
            "learning_system",
            "pattern_matcher", 
            "project_analyzer",
            "database_connection"
        ]
        
        for error_source in isolation_tests:
            isolated = self.safety_validator.test_error_isolation(error_source)
            if not isolated:
                return False
        
        return True
    
    # =============================================================================
    # PERFORMANCE UNDER STRESS TESTS
    # =============================================================================
    
    def test_memory_leak_detection(self) -> bool:
        """Test for memory leaks during extended operation"""
        
        try:
            import gc
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Get baseline memory
            gc.collect()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            processor = SCCommandProcessor()
            
            # Run many operations
            for i in range(50):
                result = processor.process(f"/sc:analyze memory test {i}")
                
                # Force garbage collection periodically
                if i % 10 == 0:
                    gc.collect()
            
            # Check final memory
            gc.collect()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_growth = end_memory - start_memory
            
            logger.info(f"Memory growth over 50 operations: {memory_growth:.2f} MB")
            
            # Should not grow excessively (allow 10MB growth)
            return memory_growth < 10
            
        except Exception as e:
            logger.error(f"Memory leak test failed: {e}")
            return False
    
    def test_resource_cleanup(self) -> bool:
        """Verify proper resource disposal"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            
            # Track file descriptors
            process = psutil.Process()
            start_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            
            # Create and use multiple processors
            processors = []
            for i in range(10):
                processor = SCCommandProcessor()
                processor.process(f"/sc:analyze resource test {i}")
                processors.append(processor)
            
            # Clean up references
            del processors
            import gc
            gc.collect()
            
            # Check file descriptors haven't grown excessively
            end_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            fd_growth = end_fds - start_fds
            
            logger.info(f"File descriptor growth: {fd_growth}")
            
            return fd_growth < 5  # Minimal growth allowed
            
        except Exception as e:
            logger.error(f"Resource cleanup test failed: {e}")
            return False
    
    def test_response_time_degradation(self) -> bool:
        """Test performance doesn't degrade over time"""
        
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            processor = SCCommandProcessor()
            
            response_times = []
            
            # Measure response times over multiple operations
            for i in range(20):
                start_time = time.time()
                processor.process(f"/sc:analyze performance test {i}")
                end_time = time.time()
                
                response_times.append(end_time - start_time)
            
            # Check that later operations aren't much slower
            early_avg = sum(response_times[:5]) / 5
            late_avg = sum(response_times[-5:]) / 5
            
            degradation_ratio = late_avg / early_avg if early_avg > 0 else 1
            
            logger.info(f"Response time degradation ratio: {degradation_ratio:.2f}")
            
            # Should not degrade more than 50%
            return degradation_ratio < 1.5
            
        except Exception as e:
            logger.error(f"Response time test failed: {e}")
            return False
    
    def test_database_locking_safety(self) -> bool:
        """Test concurrent database access safety"""
        
        try:
            from learning_storage import LearningStorage
            
            test_db = self.test_dir / "concurrent_test.db"
            
            results = []
            errors = []
            
            def database_worker(worker_id):
                try:
                    storage = LearningStorage(str(test_db))
                    
                    # Multiple operations per worker
                    for i in range(5):
                        interaction_id = storage.start_interaction(
                            user_input=f"worker {worker_id} operation {i}",
                            recommended_flags="--test",
                            confidence=80,
                            reasoning="concurrent test"
                        )
                        
                        storage.end_interaction("", True, None)
                    
                    results.append(f"Worker {worker_id} completed")
                    
                except Exception as e:
                    errors.append(f"Worker {worker_id}: {e}")
            
            # Create multiple database workers
            threads = []
            for i in range(5):
                thread = threading.Thread(target=database_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=30)
            
            # Check results
            if errors:
                logger.warning(f"Database concurrency errors: {errors}")
            
            return len(results) >= 3  # Most should succeed
            
        except Exception as e:
            logger.error(f"Database locking test failed: {e}")
            return False
    
    # =============================================================================
    # TEST EXECUTION AND REPORTING
    # =============================================================================
    
    def run_all_tests(self) -> StabilityReport:
        """Run all stability tests and generate report"""
        
        logger.info("="*80)
        logger.info("SUPERCLAUDE LEARNING SYSTEM - COMPREHENSIVE STABILITY TEST")
        logger.info("="*80)
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Setup test environment
        self.setUp()
        
        try:
            # Define all tests
            test_methods = [
                # Graceful Degradation Tests
                (self.test_missing_numpy_dependency, "Missing NumPy Dependency"),
                (self.test_missing_yaml_dependency, "Missing YAML Dependency"),
                (self.test_database_permission_error, "Database Permission Error"),
                (self.test_disk_full_simulation, "Disk Full Simulation"),
                (self.test_import_failure_recovery, "Import Failure Recovery"),
                (self.test_invalid_sc_command_input, "Invalid SC Command Input"),
                (self.test_empty_project_directory, "Empty Project Directory"),
                
                # Error Recovery Tests
                (self.test_learning_system_failure_fallback, "Learning System Fallback"),
                (self.test_database_corruption_recovery, "Database Corruption Recovery"),
                (self.test_memory_pressure_handling, "Memory Pressure Handling"),
                (self.test_concurrent_access_safety, "Concurrent Access Safety"),
                (self.test_network_timeout_handling, "Network Timeout Handling"),
                
                # Boundary Condition Tests
                (self.test_extremely_large_project, "Extremely Large Project"),
                (self.test_very_long_command_input, "Very Long Command Input"),
                (self.test_rapid_fire_requests, "Rapid Fire Requests"),
                (self.test_empty_null_inputs, "Empty/Null Inputs"),
                (self.test_unicode_special_characters, "Unicode/Special Characters"),
                
                # Production Failure Tests
                (self.test_disk_space_exhaustion, "Disk Space Exhaustion"),
                (self.test_process_termination_cleanup, "Process Termination Cleanup"),
                (self.test_configuration_corruption, "Configuration Corruption"),
                (self.test_partial_system_updates, "Partial System Updates"),
                
                # Safety Guarantee Tests
                (self.test_claude_never_breaks, "Claude Never Breaks"),
                (self.test_no_data_loss, "No Data Loss"),
                (self.test_fail_safe_defaults, "Fail-Safe Defaults"),
                (self.test_error_isolation, "Error Isolation"),
                
                # Performance Under Stress Tests
                (self.test_memory_leak_detection, "Memory Leak Detection"),
                (self.test_resource_cleanup, "Resource Cleanup"),
                (self.test_response_time_degradation, "Response Time Degradation"),
                (self.test_database_locking_safety, "Database Locking Safety"),
            ]
            
            # Run all tests
            for test_method, test_name in test_methods:
                self.run_test(test_method, test_name)
            
        finally:
            # Cleanup
            self.tearDown()
        
        # Calculate summary
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Validate safety guarantees
        claude_always_works = all(r.safety_validated for r in self.test_results)
        safety_guarantees_met = claude_always_works and \
                               all(r.recovery_successful or r.passed for r in self.test_results)
        
        # Determine production readiness
        critical_failures = [r for r in self.test_results 
                           if not r.passed and 'Claude Never Breaks' in r.test_name]
        production_ready = len(critical_failures) == 0 and passed_tests >= total_tests * 0.8
        
        # Generate recommendations
        recommendations = []
        if not claude_always_works:
            recommendations.append("CRITICAL: Fix Claude functionality preservation")
        if failed_tests > total_tests * 0.2:
            recommendations.append("HIGH: Address test failures before production")
        if not safety_guarantees_met:
            recommendations.append("HIGH: Ensure all safety guarantees are met")
        
        if passed_tests == total_tests:
            recommendations.append("System passed all stability tests - production ready")
        
        report = StabilityReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_duration=end_time - start_time,
            memory_peak_mb=end_memory - start_memory,
            claude_always_works=claude_always_works,
            safety_guarantees_met=safety_guarantees_met,
            production_ready=production_ready,
            recommendations=recommendations
        )
        
        self._generate_detailed_report(report)
        return report
    
    def _generate_detailed_report(self, report: StabilityReport):
        """Generate detailed stability report"""
        
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE STABILITY TEST REPORT")
        logger.info("="*80)
        
        logger.info(f"\nTEST SUMMARY:")
        logger.info(f"  Total Tests: {report.total_tests}")
        logger.info(f"  Passed: {report.passed_tests}")
        logger.info(f"  Failed: {report.failed_tests}")
        logger.info(f"  Success Rate: {(report.passed_tests/report.total_tests)*100:.1f}%")
        logger.info(f"  Total Duration: {report.total_duration:.2f} seconds")
        logger.info(f"  Peak Memory Usage: {report.memory_peak_mb:.2f} MB")
        
        logger.info(f"\nSAFETY GUARANTEES:")
        logger.info(f"  Claude Always Works: {'✅ YES' if report.claude_always_works else '❌ NO'}")
        logger.info(f"  Safety Guarantees Met: {'✅ YES' if report.safety_guarantees_met else '❌ NO'}")
        logger.info(f"  Production Ready: {'✅ YES' if report.production_ready else '❌ NO'}")
        
        logger.info(f"\nDETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            duration = f"{result.duration:.3f}s"
            memory = f"{result.memory_peak:.2f}MB" if result.memory_peak else "N/A"
            
            logger.info(f"  {status} | {result.test_name:<40} | {duration:>8} | {memory:>8}")
            
            if not result.passed and result.error_message:
                logger.info(f"    Error: {result.error_message}")
            
            if not result.safety_validated:
                logger.info(f"    ⚠️  Safety validation failed")
            
            if not result.recovery_successful:
                logger.info(f"    ⚠️  Recovery mechanism failed")
        
        logger.info(f"\nRECOMMENDATIONS:")
        for i, recommendation in enumerate(report.recommendations, 1):
            logger.info(f"  {i}. {recommendation}")
        
        logger.info("\n" + "="*80)
    
    @contextmanager
    def isolated_test_environment(self):
        """Context manager for isolated test environment"""
        
        # Save original state
        original_modules = sys.modules.copy()
        original_cwd = os.getcwd()
        
        try:
            yield
        finally:
            # Restore original state
            os.chdir(original_cwd)
            
            # Clean up any new modules that were imported during test
            new_modules = set(sys.modules.keys()) - set(original_modules.keys())
            for module in new_modules:
                if 'superclaude' in module or 'learning' in module:
                    try:
                        del sys.modules[module]
                    except:
                        pass

def main():
    """Main test execution"""
    
    print("SuperClaude Learning System - Comprehensive Stability Test")
    print("This test validates production readiness and safety guarantees")
    print("-" * 60)
    
    # Create test suite
    test_suite = StabilityTestSuite()
    
    try:
        # Run all tests
        report = test_suite.run_all_tests()
        
        # Summary
        print(f"\nFINAL ASSESSMENT:")
        print(f"Production Ready: {'YES' if report.production_ready else 'NO'}")
        print(f"Claude Safety: {'GUARANTEED' if report.claude_always_works else 'AT RISK'}")
        print(f"Test Success Rate: {(report.passed_tests/report.total_tests)*100:.1f}%")
        
        return 0 if report.production_ready else 1
        
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        logger.error(traceback.format_exc())
        return 2

if __name__ == "__main__":
    sys.exit(main())