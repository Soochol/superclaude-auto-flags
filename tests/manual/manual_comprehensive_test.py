#!/usr/bin/env python3
"""
Manual Comprehensive Test - SuperClaude Learning System
This test manually validates all integration points and generates a complete report
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Set working directory
current_dir = Path('/home/blessp/my_code/superclaude-auto-flags')
os.chdir(current_dir)
sys.path.insert(0, str(current_dir))

class TestExecutor:
    """Execute comprehensive integration tests manually"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Execute all test phases"""
        
        print("🚀 SuperClaude Learning System - Manual Comprehensive Test")
        print("=" * 70)
        print(f"📁 Test Directory: {current_dir}")
        print(f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Phase 1: System Availability
        print("📋 PHASE 1: System Availability Check")
        self.results['system_availability'] = self.test_system_availability()
        print()
        
        # Phase 2: Component Tests
        print("📋 PHASE 2: Component Integration Tests")
        self.results['component_tests'] = self.test_components()
        print()
        
        # Phase 3: End-to-End Workflow Tests  
        print("📋 PHASE 3: End-to-End Workflow Tests")
        self.results['e2e_tests'] = self.test_end_to_end_workflows()
        print()
        
        # Phase 4: Learning System Tests
        print("📋 PHASE 4: Learning System Tests")
        self.results['learning_tests'] = self.test_learning_system()
        print()
        
        # Phase 5: Hook Integration Tests
        print("📋 PHASE 5: Hook Integration Tests")
        self.results['hook_tests'] = self.test_hook_integration()
        print()
        
        # Phase 6: Performance Analysis
        print("📋 PHASE 6: Performance Analysis")
        self.results['performance'] = self.analyze_performance()
        print()
        
        # Generate Final Report
        self.generate_final_report()
    
    def test_system_availability(self) -> Dict[str, Any]:
        """Test system component availability"""
        
        availability = {
            'components_found': 0,
            'components_importable': 0, 
            'total_components': 0,
            'missing_components': [],
            'import_errors': [],
            'overall_health': True
        }
        
        # Core components to check
        components = [
            'claude_sc_preprocessor',
            'adaptive_recommender', 
            'learning_engine',
            'learning_storage',
            'data_collector',
            'feedback_processor'
        ]
        
        availability['total_components'] = len(components)
        
        for component in components:
            component_file = current_dir / f"{component}.py"
            
            # Check file exists
            if component_file.exists():
                availability['components_found'] += 1
                print(f"  ✅ Found: {component}.py")
                
                # Try importing
                try:
                    __import__(component)
                    availability['components_importable'] += 1
                    print(f"    ✅ Import successful")
                except Exception as e:
                    availability['import_errors'].append({
                        'component': component,
                        'error': str(e)
                    })
                    availability['overall_health'] = False
                    print(f"    ❌ Import failed: {str(e)}")
            else:
                availability['missing_components'].append(component)
                availability['overall_health'] = False
                print(f"  ❌ Missing: {component}.py")
        
        # Summary
        found_rate = availability['components_found'] / availability['total_components'] * 100
        import_rate = availability['components_importable'] / availability['total_components'] * 100
        
        print(f"  📊 Files Found: {availability['components_found']}/{availability['total_components']} ({found_rate:.0f}%)")
        print(f"  📊 Import Success: {availability['components_importable']}/{availability['total_components']} ({import_rate:.0f}%)")
        
        return availability
    
    def test_components(self) -> Dict[str, Any]:
        """Test individual component functionality"""
        
        component_results = {}
        
        # Test SCCommandProcessor
        print("  🧪 Testing SCCommandProcessor...")
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            
            processor = SCCommandProcessor()
            
            # Test basic processing
            test_commands = [
                "/sc:analyze find security vulnerabilities",
                "/sc:implement React component",
                "/sc:improve performance optimization",
                "regular command without /sc:"
            ]
            
            results = []
            for cmd in test_commands:
                start_time = time.time()
                result = processor.process(cmd)
                end_time = time.time()
                
                # Analyze result
                is_processed = len(result) > len(cmd) if cmd.startswith('/sc:') else result == cmd
                
                results.append({
                    'command': cmd,
                    'processed': is_processed,
                    'response_time': end_time - start_time,
                    'output_length': len(result)
                })
                
                status = "✅" if is_processed else "❌"
                print(f"    {status} {cmd[:30]}... ({end_time - start_time:.3f}s)")
            
            # Calculate success rate
            processed_count = sum(1 for r in results if r['processed'])
            success_rate = processed_count / len(results) * 100
            
            component_results['SCCommandProcessor'] = {
                'success_rate': success_rate,
                'test_results': results,
                'status': 'PASS' if success_rate >= 75 else 'FAIL'
            }
            
            print(f"    📊 Success Rate: {success_rate:.1f}%")
            
        except Exception as e:
            component_results['SCCommandProcessor'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"    ❌ Failed: {str(e)}")
        
        # Test Learning Storage
        print("  🧪 Testing LearningStorage...")
        try:
            from learning_storage import LearningStorage, UserInteraction
            
            with tempfile.TemporaryDirectory() as temp_dir:
                storage = LearningStorage(temp_dir)
                
                # Test basic operations
                interaction = UserInteraction(
                    timestamp=time.strftime('%Y-%m-%dT%H:%M:%S'),
                    user_input="/sc:analyze test",
                    command="analyze",
                    description="test",
                    recommended_flags="--persona-analyzer",
                    actual_flags="--persona-analyzer",
                    project_context={"type": "test"},
                    success=True,
                    execution_time=10.0,
                    confidence=85,
                    reasoning="test reasoning",
                    user_id=storage.user_id,
                    project_hash="test_hash"
                )
                
                # Record and retrieve
                interaction_id = storage.record_interaction(interaction)
                retrieved = storage.get_user_interactions(days=1)
                
                success = interaction_id is not None and len(retrieved) > 0
                
                component_results['LearningStorage'] = {
                    'status': 'PASS' if success else 'FAIL',
                    'interaction_recorded': interaction_id is not None,
                    'retrieval_working': len(retrieved) > 0
                }
                
                print(f"    ✅ Storage operations: {'PASS' if success else 'FAIL'}")
        
        except Exception as e:
            component_results['LearningStorage'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"    ❌ Failed: {str(e)}")
        
        # Test Learning Engine
        print("  🧪 Testing AdaptiveLearningEngine...")
        try:
            from learning_engine import AdaptiveLearningEngine, get_learning_engine
            
            with tempfile.TemporaryDirectory() as temp_dir:
                from learning_storage import LearningStorage
                storage = LearningStorage(temp_dir)
                engine = AdaptiveLearningEngine(storage)
                
                # Test recommendation generation
                recommendation = engine.get_adaptive_recommendation(
                    command="analyze",
                    description="security test",
                    project_context={"project_type": "python_backend"}
                )
                
                success = (recommendation and 
                          hasattr(recommendation, 'flags') and 
                          len(recommendation.flags) > 0)
                
                component_results['AdaptiveLearningEngine'] = {
                    'status': 'PASS' if success else 'FAIL',
                    'recommendation_generated': success,
                    'flags': recommendation.flags if success else '',
                    'confidence': recommendation.confidence if success else 0
                }
                
                print(f"    ✅ Recommendation: {'PASS' if success else 'FAIL'}")
                if success:
                    print(f"       Flags: {recommendation.flags}")
                    print(f"       Confidence: {recommendation.confidence}")
        
        except Exception as e:
            component_results['AdaptiveLearningEngine'] = {
                'status': 'ERROR', 
                'error': str(e)
            }
            print(f"    ❌ Failed: {str(e)}")
        
        return component_results
    
    def test_end_to_end_workflows(self) -> Dict[str, Any]:
        """Test end-to-end workflow scenarios"""
        
        test_scenarios = [
            {
                'name': 'Security Analysis',
                'command': '/sc:analyze find security vulnerabilities',
                'expected_keywords': ['security', 'persona-security', 'validate'],
                'min_confidence': 80
            },
            {
                'name': 'React Implementation', 
                'command': '/sc:implement React user interface component',
                'expected_keywords': ['frontend', 'magic', 'persona-frontend'],
                'min_confidence': 75
            },
            {
                'name': 'Performance Optimization',
                'command': '/sc:improve performance optimization', 
                'expected_keywords': ['performance', 'persona-performance', 'think'],
                'min_confidence': 70
            },
            {
                'name': 'Architecture Analysis',
                'command': '/sc:analyze architecture patterns',
                'expected_keywords': ['architect', 'persona-architect', 'ultrathink'],
                'min_confidence': 80
            }
        ]
        
        workflow_results = {}
        
        for scenario in test_scenarios:
            print(f"  🧪 Testing: {scenario['name']}")
            
            try:
                from claude_sc_preprocessor import SCCommandProcessor
                
                processor = SCCommandProcessor()
                start_time = time.time()
                result = processor.process(scenario['command'])
                end_time = time.time()
                
                # Extract information from result
                flags_found = self.extract_flags_from_result(result)
                confidence = self.extract_confidence_from_result(result)
                
                # Check expectations
                keyword_matches = sum(1 for keyword in scenario['expected_keywords'] 
                                    if keyword.lower() in result.lower())
                keyword_score = keyword_matches / len(scenario['expected_keywords']) * 100
                
                confidence_ok = confidence >= scenario['min_confidence']
                
                success = keyword_score >= 50 and confidence_ok
                
                workflow_results[scenario['name']] = {
                    'command': scenario['command'],
                    'success': success,
                    'response_time': end_time - start_time,
                    'flags_generated': flags_found,
                    'confidence': confidence,
                    'keyword_score': keyword_score,
                    'expected_keywords': scenario['expected_keywords'],
                    'keywords_found': keyword_matches
                }
                
                status = "✅" if success else "❌"
                print(f"    {status} {scenario['name']}: {'PASS' if success else 'FAIL'}")
                print(f"       Response Time: {end_time - start_time:.3f}s")
                print(f"       Keywords: {keyword_matches}/{len(scenario['expected_keywords'])}")
                print(f"       Confidence: {confidence}%")
                print(f"       Flags: {flags_found}")
                
            except Exception as e:
                workflow_results[scenario['name']] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"    ❌ {scenario['name']}: ERROR - {str(e)}")
        
        return workflow_results
    
    def test_learning_system(self) -> Dict[str, Any]:
        """Test learning system integration and effectiveness"""
        
        learning_results = {
            'personalization_working': False,
            'data_collection_working': False,
            'feedback_processing_working': False,
            'recommendation_quality': 0,
            'learning_enabled': False
        }
        
        print("  🧪 Testing Learning System Integration...")
        
        try:
            # Test Personalized Recommender
            from adaptive_recommender import get_personalized_recommender
            
            recommender = get_personalized_recommender()
            
            # Test multiple contexts
            test_contexts = [
                {'project_type': 'python_backend', 'complexity': 'complex'},
                {'project_type': 'frontend', 'complexity': 'simple'}, 
                {'project_type': 'python_general', 'complexity': 'moderate'}
            ]
            
            successful_recommendations = 0
            total_confidence = 0
            
            for context in test_contexts:
                try:
                    recommendation = recommender.get_personalized_recommendation(
                        "/sc:analyze test code", context
                    )
                    
                    if recommendation and hasattr(recommendation, 'flags'):
                        successful_recommendations += 1
                        total_confidence += recommendation.confidence
                        
                except Exception as e:
                    print(f"    ⚠️ Personalization test failed for context {context}: {e}")
            
            if successful_recommendations > 0:
                learning_results['personalization_working'] = True
                learning_results['recommendation_quality'] = total_confidence / successful_recommendations
                learning_results['learning_enabled'] = True
                
                print(f"    ✅ Personalization: {successful_recommendations}/{len(test_contexts)} contexts")
                print(f"    📊 Average Quality: {learning_results['recommendation_quality']:.1f}%")
            else:
                print(f"    ❌ Personalization: No successful recommendations")
            
            # Test Data Collection
            try:
                from data_collector import get_data_collector
                
                collector = get_data_collector()
                context = collector.collect_project_context(str(current_dir))
                
                if context and 'project_hash' in context:
                    learning_results['data_collection_working'] = True
                    print(f"    ✅ Data Collection: Project context collected")
                else:
                    print(f"    ❌ Data Collection: Failed to collect context")
                    
            except Exception as e:
                print(f"    ❌ Data Collection: {str(e)}")
            
            # Test Feedback Processing
            try:
                from feedback_processor import get_feedback_processor
                
                processor = get_feedback_processor()
                
                # Test immediate feedback
                feedback = processor.process_immediate_feedback(
                    interaction_id="test_interaction",
                    success=True,
                    execution_time=15.0,
                    error_details=None
                )
                
                if feedback and hasattr(feedback, 'feedback_id'):
                    learning_results['feedback_processing_working'] = True
                    print(f"    ✅ Feedback Processing: Working")
                else:
                    print(f"    ❌ Feedback Processing: Failed")
                    
            except Exception as e:
                print(f"    ❌ Feedback Processing: {str(e)}")
                
        except Exception as e:
            print(f"    ❌ Learning System: Major error - {str(e)}")
        
        return learning_results
    
    def test_hook_integration(self) -> Dict[str, Any]:
        """Test hook system integration"""
        
        hook_results = {
            'hook_file_exists': False,
            'hook_functions_available': False,
            'hook_config_exists': False,
            'integration_status': 'FAIL'
        }
        
        # Check hook file
        hook_file = current_dir / 'superclaude_prompt_hook.py'
        if hook_file.exists():
            hook_results['hook_file_exists'] = True
            print(f"    ✅ Hook file exists: {hook_file.name}")
            
            try:
                # Import hook module
                import superclaude_prompt_hook as hook
                
                # Check required functions
                required_functions = ['handle_user_prompt_submit', 'handle_pre_tool_use']
                available_functions = []
                
                for func_name in required_functions:
                    if hasattr(hook, func_name):
                        available_functions.append(func_name)
                        print(f"    ✅ Function available: {func_name}")
                    else:
                        print(f"    ❌ Function missing: {func_name}")
                
                if len(available_functions) == len(required_functions):
                    hook_results['hook_functions_available'] = True
                    hook_results['integration_status'] = 'PASS'
                
            except Exception as e:
                print(f"    ❌ Hook import failed: {str(e)}")
        else:
            print(f"    ❌ Hook file not found: {hook_file}")
        
        # Check hook configuration
        config_file = current_dir / 'superclaude_hooks_config.json'
        if config_file.exists():
            hook_results['hook_config_exists'] = True
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                print(f"    ✅ Hook config loaded: {len(config)} entries")
            except Exception as e:
                print(f"    ⚠️ Hook config exists but invalid: {str(e)}")
        else:
            print(f"    ⚠️ Hook config not found: {config_file}")
        
        return hook_results
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance characteristics"""
        
        performance = {
            'total_test_time': time.time() - self.start_time,
            'component_response_times': {},
            'memory_efficiency': 'Unknown',
            'throughput_estimate': 0.0,
            'performance_grade': 'C'
        }
        
        # Calculate performance metrics from test results
        if 'e2e_tests' in self.results:
            response_times = []
            for test_name, test_result in self.results['e2e_tests'].items():
                if 'response_time' in test_result:
                    response_times.append(test_result['response_time'])
                    performance['component_response_times'][test_name] = test_result['response_time']
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                performance['throughput_estimate'] = 1.0 / avg_response_time if avg_response_time > 0 else 0
                
                # Grade performance
                if avg_response_time < 0.1:
                    performance['performance_grade'] = 'A+'
                elif avg_response_time < 0.5:
                    performance['performance_grade'] = 'A'
                elif avg_response_time < 1.0:
                    performance['performance_grade'] = 'B'
                elif avg_response_time < 2.0:
                    performance['performance_grade'] = 'C'
                else:
                    performance['performance_grade'] = 'D'
        
        print(f"    📊 Total Test Time: {performance['total_test_time']:.2f}s")
        print(f"    📊 Estimated Throughput: {performance['throughput_estimate']:.1f} req/sec")
        print(f"    📊 Performance Grade: {performance['performance_grade']}")
        
        return performance
    
    def extract_flags_from_result(self, result: str) -> str:
        """Extract flags from command processor result"""
        import re
        
        # Look for Korean flag pattern
        korean_pattern = r'적용된 플래그:\s*([^\n]+)'
        match = re.search(korean_pattern, result)
        if match:
            return match.group(1).strip()
        
        # Look for English flag pattern
        english_pattern = r'flags?:\s*([^\n]+)'
        match = re.search(english_pattern, result, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Look for flags at end
        lines = result.split('\n')
        for line in reversed(lines):
            if '--' in line and line.strip().startswith('--'):
                return line.strip()
        
        return ""
    
    def extract_confidence_from_result(self, result: str) -> int:
        """Extract confidence from command processor result"""
        import re
        
        # Look for Korean confidence pattern
        korean_pattern = r'신뢰도:\s*(\d+)%'
        match = re.search(korean_pattern, result)
        if match:
            return int(match.group(1))
        
        # Look for English confidence pattern
        english_pattern = r'confidence:\s*(\d+)%'
        match = re.search(english_pattern, result, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 0
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        
        print("=" * 70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Overall Statistics
        total_time = time.time() - self.start_time
        print(f"⏰ Total Test Duration: {total_time:.2f} seconds")
        print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System Health Overview
        print("🏥 SYSTEM HEALTH OVERVIEW")
        print("-" * 40)
        
        if 'system_availability' in self.results:
            avail = self.results['system_availability']
            health_status = "🟢 HEALTHY" if avail['overall_health'] else "🔴 UNHEALTHY"
            print(f"Overall Health: {health_status}")
            print(f"Components Found: {avail['components_found']}/{avail['total_components']}")
            print(f"Import Success: {avail['components_importable']}/{avail['total_components']}")
        
        print()
        
        # Component Test Results
        print("🔧 COMPONENT TEST RESULTS")
        print("-" * 40)
        
        if 'component_tests' in self.results:
            for component, result in self.results['component_tests'].items():
                status = result.get('status', 'UNKNOWN')
                icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
                print(f"{icon} {component}: {status}")
                
                if 'success_rate' in result:
                    print(f"   Success Rate: {result['success_rate']:.1f}%")
        
        print()
        
        # End-to-End Test Results
        print("🔄 END-TO-END TEST RESULTS")
        print("-" * 40)
        
        if 'e2e_tests' in self.results:
            total_e2e = len(self.results['e2e_tests'])
            passed_e2e = sum(1 for r in self.results['e2e_tests'].values() if r.get('success', False))
            
            print(f"Tests Passed: {passed_e2e}/{total_e2e} ({passed_e2e/total_e2e*100:.1f}%)")
            
            for test_name, result in self.results['e2e_tests'].items():
                status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
                response_time = result.get('response_time', 0)
                confidence = result.get('confidence', 0)
                
                print(f"  {status} {test_name}")
                print(f"     Time: {response_time:.3f}s, Confidence: {confidence}%")
        
        print()
        
        # Learning System Results
        print("🧠 LEARNING SYSTEM RESULTS")
        print("-" * 40)
        
        if 'learning_tests' in self.results:
            learning = self.results['learning_tests']
            
            learning_enabled = "✅" if learning.get('learning_enabled', False) else "❌"
            personalization = "✅" if learning.get('personalization_working', False) else "❌"
            data_collection = "✅" if learning.get('data_collection_working', False) else "❌"
            feedback = "✅" if learning.get('feedback_processing_working', False) else "❌"
            
            print(f"Learning Enabled: {learning_enabled}")
            print(f"Personalization: {personalization}")
            print(f"Data Collection: {data_collection}")
            print(f"Feedback Processing: {feedback}")
            print(f"Recommendation Quality: {learning.get('recommendation_quality', 0):.1f}%")
        
        print()
        
        # Performance Analysis
        print("⚡ PERFORMANCE ANALYSIS")
        print("-" * 40)
        
        if 'performance' in self.results:
            perf = self.results['performance']
            print(f"Performance Grade: {perf.get('performance_grade', 'Unknown')}")
            print(f"Throughput: {perf.get('throughput_estimate', 0):.1f} requests/sec")
            
            if 'component_response_times' in perf:
                print("Response Times:")
                for component, time_val in perf['component_response_times'].items():
                    print(f"  {component}: {time_val:.3f}s")
        
        print()
        
        # Integration Issues
        issues_found = []
        
        if 'system_availability' in self.results:
            issues_found.extend(self.results['system_availability'].get('import_errors', []))
        
        if issues_found:
            print("⚠️ INTEGRATION ISSUES")
            print("-" * 40)
            for issue in issues_found:
                if isinstance(issue, dict):
                    print(f"  • {issue.get('component', 'Unknown')}: {issue.get('error', 'Unknown error')}")
                else:
                    print(f"  • {issue}")
        else:
            print("✅ NO MAJOR INTEGRATION ISSUES FOUND")
        
        print()
        
        # Final Assessment
        print("🎯 FINAL ASSESSMENT")
        print("-" * 40)
        
        # Calculate overall success rate
        success_metrics = []
        
        if 'system_availability' in self.results:
            success_metrics.append(self.results['system_availability']['overall_health'])
        
        if 'component_tests' in self.results:
            component_success = sum(1 for r in self.results['component_tests'].values() 
                                  if r.get('status') == 'PASS')
            total_components = len(self.results['component_tests'])
            success_metrics.append(component_success / total_components if total_components > 0 else 0)
        
        if 'e2e_tests' in self.results:
            e2e_success = sum(1 for r in self.results['e2e_tests'].values() if r.get('success', False))
            total_e2e = len(self.results['e2e_tests'])
            success_metrics.append(e2e_success / total_e2e if total_e2e > 0 else 0)
        
        if success_metrics:
            overall_success = sum(success_metrics) / len(success_metrics) * 100
            
            if overall_success >= 90:
                assessment = "🟢 EXCELLENT - System ready for production"
            elif overall_success >= 75:
                assessment = "🟡 GOOD - System functional with minor issues"
            elif overall_success >= 60:
                assessment = "🟠 FAIR - System needs attention"
            else:
                assessment = "🔴 POOR - System has critical issues"
            
            print(f"Overall Success Rate: {overall_success:.1f}%")
            print(f"Assessment: {assessment}")
        else:
            print("Assessment: Unable to calculate due to insufficient data")
        
        print()
        print("=" * 70)
        
        # Save detailed report
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_test_time': total_time,
            'results': self.results,
            'overall_success_rate': sum(success_metrics) / len(success_metrics) * 100 if success_metrics else 0
        }
        
        report_file = current_dir / 'manual_comprehensive_test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    executor = TestExecutor()
    executor.run_all_tests()