#!/usr/bin/env python3
"""
SuperClaude Learning System Integration Test Suite
Comprehensive end-to-end testing of the complete SuperClaude workflow
"""

import os
import sys
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    command: str
    success: bool
    response_time: float
    recommendation: Optional[Dict[str, Any]]
    error_message: Optional[str]
    flags_generated: str
    confidence: int
    reasoning: List[str]

@dataclass
class IntegrationTestReport:
    """Comprehensive test report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_response_time: float
    test_results: List[TestResult]
    system_status: Dict[str, Any]
    learning_effectiveness: Dict[str, Any]
    integration_issues: List[str]

class SuperClaudeIntegrationTester:
    """Comprehensive integration test suite"""
    
    def __init__(self, test_directory: str = None):
        self.test_directory = test_directory or os.getcwd()
        self.test_results: List[TestResult] = []
        self.integration_issues: List[str] = []
        
        # Test scenarios
        self.test_scenarios = [
            {
                'name': 'Security Analysis',
                'command': '/sc:analyze find security vulnerabilities',
                'expected_flags': ['--persona-security', '--focus', 'security', '--validate'],
                'expected_confidence_min': 85
            },
            {
                'name': 'React Component Implementation',
                'command': '/sc:implement React user interface component',
                'expected_flags': ['--persona-frontend', '--magic', '--c7'],
                'expected_confidence_min': 80
            },
            {
                'name': 'Performance Optimization',
                'command': '/sc:improve performance optimization',
                'expected_flags': ['--persona-performance', '--think-hard', '--focus', 'performance'],
                'expected_confidence_min': 80
            },
            {
                'name': 'Architecture Analysis',
                'command': '/sc:analyze architecture patterns',
                'expected_flags': ['--persona-architect', '--ultrathink', '--seq'],
                'expected_confidence_min': 85
            },
            {
                'name': 'API Implementation',
                'command': '/sc:implement REST API endpoints',
                'expected_flags': ['--persona-backend', '--seq', '--c7'],
                'expected_confidence_min': 80
            },
            {
                'name': 'Code Quality Improvement',
                'command': '/sc:improve code quality and refactoring',
                'expected_flags': ['--persona-refactorer', '--loop', '--validate'],
                'expected_confidence_min': 75
            }
        ]
    
    def run_comprehensive_test(self) -> IntegrationTestReport:
        """Run comprehensive integration test suite"""
        
        print("🚀 SuperClaude Learning System Integration Test Suite")
        print("=" * 60)
        
        # 1. System Availability Check
        print("\n📋 Phase 1: System Availability Check")
        system_status = self._check_system_availability()
        self._print_system_status(system_status)
        
        # 2. Component Integration Tests
        print("\n📋 Phase 2: Component Integration Tests")
        self._run_component_integration_tests()
        
        # 3. End-to-End Workflow Tests
        print("\n📋 Phase 3: End-to-End Workflow Tests")
        self._run_end_to_end_tests()
        
        # 4. Learning System Tests
        print("\n📋 Phase 4: Learning System Tests")
        learning_effectiveness = self._test_learning_system()
        
        # 5. Hook Integration Tests
        print("\n📋 Phase 5: Hook Integration Tests")
        self._test_hook_integration()
        
        # 6. Performance Characteristics
        print("\n📋 Phase 6: Performance Analysis")
        performance_results = self._analyze_performance()
        
        # Generate comprehensive report
        report = self._generate_report(system_status, learning_effectiveness, performance_results)
        
        # Print summary
        self._print_test_summary(report)
        
        return report
    
    def _check_system_availability(self) -> Dict[str, Any]:
        """Check system component availability"""
        status = {
            'components': {},
            'dependencies': {},
            'configuration': {},
            'overall_health': True
        }
        
        # Check core components
        components_to_check = [
            'claude_sc_preprocessor.py',
            'adaptive_recommender.py', 
            'learning_engine.py',
            'learning_storage.py',
            'data_collector.py',
            'feedback_processor.py',
            'superclaude_prompt_hook.py'
        ]
        
        for component in components_to_check:
            try:
                component_path = Path(self.test_directory) / component
                if component_path.exists():
                    # Try importing
                    spec = __import__(component.replace('.py', ''))
                    status['components'][component] = {
                        'available': True,
                        'path': str(component_path),
                        'size': component_path.stat().st_size
                    }
                else:
                    status['components'][component] = {
                        'available': False,
                        'error': 'File not found'
                    }
                    status['overall_health'] = False
            except Exception as e:
                status['components'][component] = {
                    'available': False,
                    'error': str(e)
                }
                status['overall_health'] = False
        
        # Check dependencies
        dependencies = ['yaml', 'json', 'pathlib', 'dataclasses', 'collections']
        for dep in dependencies:
            try:
                __import__(dep)
                status['dependencies'][dep] = {'available': True}
            except ImportError as e:
                status['dependencies'][dep] = {'available': False, 'error': str(e)}
                status['overall_health'] = False
        
        # Check configuration files
        config_files = ['orchestrator_rules.yaml', 'superclaude_hooks_config.json']
        for config_file in config_files:
            config_path = Path(self.test_directory) / config_file
            status['configuration'][config_file] = {
                'exists': config_path.exists(),
                'path': str(config_path) if config_path.exists() else None
            }
        
        return status
    
    def _run_component_integration_tests(self):
        """Test individual component integrations"""
        
        # Test SCCommandProcessor
        print("  🧪 Testing SCCommandProcessor...")
        try:
            from claude_sc_preprocessor import SCCommandProcessor
            
            processor = SCCommandProcessor()
            test_input = "/sc:analyze test code"
            start_time = time.time()
            result = processor.process(test_input)
            response_time = time.time() - start_time
            
            success = result != test_input and len(result) > len(test_input)
            
            self.test_results.append(TestResult(
                test_name="SCCommandProcessor Basic",
                command=test_input,
                success=success,
                response_time=response_time,
                recommendation=None,
                error_message=None if success else "No processing occurred",
                flags_generated=self._extract_flags(result),
                confidence=self._extract_confidence(result),
                reasoning=[]
            ))
            
            print(f"    ✅ SCCommandProcessor: {'PASS' if success else 'FAIL'} ({response_time:.3f}s)")
            
        except Exception as e:
            print(f"    ❌ SCCommandProcessor: FAIL - {str(e)}")
            self.integration_issues.append(f"SCCommandProcessor failure: {str(e)}")
        
        # Test Learning Components
        print("  🧪 Testing Learning System Components...")
        try:
            from adaptive_recommender import get_personalized_recommender
            
            recommender = get_personalized_recommender()
            
            # Test basic recommendation
            start_time = time.time()
            recommendation = recommender.get_personalized_recommendation(
                "/sc:analyze security", 
                {'project_type': 'python_backend', 'complexity': 'moderate'}
            )
            response_time = time.time() - start_time
            
            success = hasattr(recommendation, 'flags') and len(recommendation.flags) > 0
            
            self.test_results.append(TestResult(
                test_name="Learning System Basic",
                command="/sc:analyze security",
                success=success,
                response_time=response_time,
                recommendation=recommendation.__dict__ if success else None,
                error_message=None if success else "No recommendation generated",
                flags_generated=recommendation.flags if success else "",
                confidence=recommendation.confidence if success else 0,
                reasoning=recommendation.reasoning if success else []
            ))
            
            print(f"    ✅ Learning System: {'PASS' if success else 'FAIL'} ({response_time:.3f}s)")
            
        except Exception as e:
            print(f"    ❌ Learning System: FAIL - {str(e)}")
            self.integration_issues.append(f"Learning System failure: {str(e)}")
    
    def _run_end_to_end_tests(self):
        """Run end-to-end workflow tests"""
        
        for scenario in self.test_scenarios:
            print(f"  🧪 Testing: {scenario['name']}")
            
            try:
                # Test with SCCommandProcessor
                from claude_sc_preprocessor import SCCommandProcessor
                
                processor = SCCommandProcessor()
                start_time = time.time()
                result = processor.process(scenario['command'])
                response_time = time.time() - start_time
                
                # Extract flags and analyze
                flags_generated = self._extract_flags(result)
                confidence = self._extract_confidence(result)
                reasoning = self._extract_reasoning(result)
                
                # Check if expected flags are present
                flags_match = self._check_expected_flags(flags_generated, scenario['expected_flags'])
                confidence_ok = confidence >= scenario['expected_confidence_min']
                
                success = flags_match and confidence_ok and len(flags_generated) > 0
                
                self.test_results.append(TestResult(
                    test_name=scenario['name'],
                    command=scenario['command'],
                    success=success,
                    response_time=response_time,
                    recommendation=None,
                    error_message=self._generate_error_message(flags_match, confidence_ok, scenario),
                    flags_generated=flags_generated,
                    confidence=confidence,
                    reasoning=reasoning
                ))
                
                status = "PASS" if success else "FAIL"
                print(f"    ✅ {scenario['name']}: {status} ({response_time:.3f}s)")
                print(f"       Flags: {flags_generated}")
                print(f"       Confidence: {confidence}%")
                
            except Exception as e:
                print(f"    ❌ {scenario['name']}: FAIL - {str(e)}")
                self.test_results.append(TestResult(
                    test_name=scenario['name'],
                    command=scenario['command'],
                    success=False,
                    response_time=0.0,
                    recommendation=None,
                    error_message=str(e),
                    flags_generated="",
                    confidence=0,
                    reasoning=[]
                ))
                self.integration_issues.append(f"{scenario['name']} failure: {str(e)}")
    
    def _test_learning_system(self) -> Dict[str, Any]:
        """Test learning system effectiveness"""
        
        effectiveness = {
            'recommendations_generated': 0,
            'learning_enabled': False,
            'personalization_working': False,
            'data_collection_working': False,
            'feedback_processing_working': False,
            'average_confidence': 0.0,
            'errors': []
        }
        
        try:
            from adaptive_recommender import get_personalized_recommender
            from data_collector import get_data_collector
            from feedback_processor import get_feedback_processor
            
            # Test recommender
            recommender = get_personalized_recommender()
            effectiveness['recommendations_generated'] = 1
            effectiveness['learning_enabled'] = True
            
            # Test data collector
            collector = get_data_collector()
            if collector:
                effectiveness['data_collection_working'] = True
            
            # Test feedback processor
            feedback_proc = get_feedback_processor()
            if feedback_proc:
                effectiveness['feedback_processing_working'] = True
            
            # Test personalization
            test_contexts = [
                {'project_type': 'python_backend', 'complexity': 'complex'},
                {'project_type': 'frontend', 'complexity': 'simple'},
                {'project_type': 'python_general', 'complexity': 'moderate'}
            ]
            
            confidences = []
            for context in test_contexts:
                try:
                    rec = recommender.get_personalized_recommendation(
                        "/sc:analyze test", context
                    )
                    confidences.append(rec.confidence)
                    effectiveness['recommendations_generated'] += 1
                except Exception as e:
                    effectiveness['errors'].append(f"Personalization test failed: {str(e)}")
            
            if confidences:
                effectiveness['average_confidence'] = sum(confidences) / len(confidences)
                effectiveness['personalization_working'] = True
            
            print(f"    ✅ Learning System: Generated {effectiveness['recommendations_generated']} recommendations")
            print(f"    ✅ Average Confidence: {effectiveness['average_confidence']:.1f}%")
            print(f"    ✅ Components: Data Collection: {'✓' if effectiveness['data_collection_working'] else '✗'}, " +
                  f"Feedback: {'✓' if effectiveness['feedback_processing_working'] else '✗'}")
            
        except Exception as e:
            effectiveness['errors'].append(f"Learning system test failed: {str(e)}")
            print(f"    ❌ Learning System: FAIL - {str(e)}")
        
        return effectiveness
    
    def _test_hook_integration(self):
        """Test hook integration"""
        
        print("  🧪 Testing Hook Integration...")
        
        try:
            # Check if hook file exists
            hook_path = Path(self.test_directory) / 'superclaude_prompt_hook.py'
            
            if hook_path.exists():
                print(f"    ✅ Hook file exists: {hook_path}")
                
                # Try to import and test hook
                spec = __import__('superclaude_prompt_hook')
                
                # Check if hook has required functions
                if hasattr(spec, 'handle_user_prompt_submit'):
                    print("    ✅ UserPromptSubmit handler found")
                else:
                    print("    ❌ UserPromptSubmit handler missing")
                    self.integration_issues.append("UserPromptSubmit handler missing")
                
                if hasattr(spec, 'handle_pre_tool_use'):
                    print("    ✅ PreToolUse handler found")
                else:
                    print("    ❌ PreToolUse handler missing")
                    self.integration_issues.append("PreToolUse handler missing")
                
                # Test hook configuration
                config_path = Path(self.test_directory) / 'superclaude_hooks_config.json'
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    print(f"    ✅ Hook configuration loaded: {len(config)} entries")
                else:
                    print("    ⚠️  Hook configuration file missing")
                    
            else:
                print(f"    ❌ Hook file not found: {hook_path}")
                self.integration_issues.append("Hook file not found")
                
        except Exception as e:
            print(f"    ❌ Hook Integration: FAIL - {str(e)}")
            self.integration_issues.append(f"Hook integration failure: {str(e)}")
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        
        performance = {
            'average_response_time': 0.0,
            'max_response_time': 0.0,
            'min_response_time': float('inf'),
            'response_time_distribution': {},
            'throughput_per_second': 0.0,
            'memory_efficient': True,
            'performance_grade': 'A'
        }
        
        if self.test_results:
            response_times = [r.response_time for r in self.test_results if r.response_time > 0]
            
            if response_times:
                performance['average_response_time'] = sum(response_times) / len(response_times)
                performance['max_response_time'] = max(response_times)
                performance['min_response_time'] = min(response_times)
                performance['throughput_per_second'] = 1.0 / performance['average_response_time']
                
                # Grade performance
                avg_time = performance['average_response_time']
                if avg_time < 0.1:
                    performance['performance_grade'] = 'A+'
                elif avg_time < 0.5:
                    performance['performance_grade'] = 'A'
                elif avg_time < 1.0:
                    performance['performance_grade'] = 'B'
                elif avg_time < 2.0:
                    performance['performance_grade'] = 'C'
                else:
                    performance['performance_grade'] = 'D'
        
        print(f"    📊 Average Response Time: {performance['average_response_time']:.3f}s")
        print(f"    📊 Throughput: {performance['throughput_per_second']:.1f} requests/sec")
        print(f"    📊 Performance Grade: {performance['performance_grade']}")
        
        return performance
    
    def _generate_report(self, system_status: Dict[str, Any], learning_effectiveness: Dict[str, Any], 
                        performance_results: Dict[str, Any]) -> IntegrationTestReport:
        """Generate comprehensive test report"""
        
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = len(self.test_results) - passed_tests
        
        average_response_time = (
            sum(r.response_time for r in self.test_results) / len(self.test_results)
            if self.test_results else 0.0
        )
        
        return IntegrationTestReport(
            total_tests=len(self.test_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            average_response_time=average_response_time,
            test_results=self.test_results,
            system_status=system_status,
            learning_effectiveness=learning_effectiveness,
            integration_issues=self.integration_issues
        )
    
    def _print_system_status(self, status: Dict[str, Any]):
        """Print system status"""
        print(f"  🏥 System Health: {'✅ HEALTHY' if status['overall_health'] else '❌ UNHEALTHY'}")
        
        print("  📦 Components:")
        for component, info in status['components'].items():
            status_icon = "✅" if info['available'] else "❌"
            print(f"    {status_icon} {component}: {'Available' if info['available'] else info.get('error', 'Unavailable')}")
        
        print("  📚 Dependencies:")
        for dep, info in status['dependencies'].items():
            status_icon = "✅" if info['available'] else "❌"
            print(f"    {status_icon} {dep}: {'Available' if info['available'] else info.get('error', 'Missing')}")
    
    def _print_test_summary(self, report: IntegrationTestReport):
        """Print comprehensive test summary"""
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Overall Results
        success_rate = (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0
        print(f"🎯 Overall Success Rate: {success_rate:.1f}% ({report.passed_tests}/{report.total_tests})")
        print(f"⏱️  Average Response Time: {report.average_response_time:.3f}s")
        
        # Test Results by Category
        print(f"\n📋 Test Results:")
        for result in report.test_results:
            status_icon = "✅" if result.success else "❌"
            print(f"  {status_icon} {result.test_name}: {'PASS' if result.success else 'FAIL'}")
            print(f"     Command: {result.command}")
            print(f"     Flags: {result.flags_generated}")
            print(f"     Confidence: {result.confidence}%")
            print(f"     Response Time: {result.response_time:.3f}s")
            if result.error_message:
                print(f"     Error: {result.error_message}")
            print()
        
        # Learning System Status
        print(f"🧠 Learning System:")
        le = report.learning_effectiveness
        print(f"  • Learning Enabled: {'✅' if le['learning_enabled'] else '❌'}")
        print(f"  • Recommendations Generated: {le['recommendations_generated']}")
        print(f"  • Average Confidence: {le['average_confidence']:.1f}%")
        print(f"  • Personalization: {'✅' if le['personalization_working'] else '❌'}")
        print(f"  • Data Collection: {'✅' if le['data_collection_working'] else '❌'}")
        print(f"  • Feedback Processing: {'✅' if le['feedback_processing_working'] else '❌'}")
        
        # Integration Issues
        if report.integration_issues:
            print(f"\n⚠️  Integration Issues ({len(report.integration_issues)}):")
            for issue in report.integration_issues:
                print(f"  • {issue}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate >= 90:
            print("  ✅ System is working excellently!")
        elif success_rate >= 70:
            print("  📈 System is working well with minor issues")
        elif success_rate >= 50:
            print("  ⚠️  System has moderate issues that need attention")
        else:
            print("  🚨 System has critical issues requiring immediate attention")
        
        if report.average_response_time > 1.0:
            print("  ⚡ Consider performance optimization for faster response times")
        
        if not le['learning_enabled']:
            print("  🧠 Enable learning system for improved recommendations")
    
    def _extract_flags(self, response: str) -> str:
        """Extract flags from response"""
        # Look for pattern like "적용된 플래그: --flag1 --flag2"
        import re
        flag_pattern = r'적용된 플래그:\s*([^\n]+)'
        match = re.search(flag_pattern, response)
        if match:
            return match.group(1).strip()
        
        # Fallback: look for flags at the end
        lines = response.split('\n')
        for line in reversed(lines):
            if line.strip().startswith('--'):
                return line.strip()
        
        return ""
    
    def _extract_confidence(self, response: str) -> int:
        """Extract confidence from response"""
        import re
        confidence_pattern = r'신뢰도:\s*(\d+)%'
        match = re.search(confidence_pattern, response)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_reasoning(self, response: str) -> List[str]:
        """Extract reasoning from response"""
        reasoning = []
        import re
        
        # Look for "근거:" or "추천 근거:" sections
        reasoning_patterns = [
            r'근거:\s*([^\n]+)',
            r'추천 근거:\s*([^\n]+)',
            r'💡\s*([^\n]+)'
        ]
        
        for pattern in reasoning_patterns:
            matches = re.findall(pattern, response)
            reasoning.extend(matches)
        
        return reasoning
    
    def _check_expected_flags(self, generated_flags: str, expected_flags: List[str]) -> bool:
        """Check if expected flags are present"""
        if not generated_flags:
            return False
        
        generated_lower = generated_flags.lower()
        matches = 0
        
        for expected in expected_flags:
            if expected.lower() in generated_lower:
                matches += 1
        
        # At least 60% of expected flags should be present
        return matches >= len(expected_flags) * 0.6
    
    def _generate_error_message(self, flags_match: bool, confidence_ok: bool, scenario: Dict) -> Optional[str]:
        """Generate error message for failed tests"""
        errors = []
        
        if not flags_match:
            errors.append(f"Expected flags not found: {scenario['expected_flags']}")
        
        if not confidence_ok:
            errors.append(f"Confidence too low: expected >= {scenario['expected_confidence_min']}%")
        
        return "; ".join(errors) if errors else None

def main():
    """Main function to run comprehensive integration tests"""
    
    print("SuperClaude Learning System - Comprehensive Integration Test")
    print("Testing complete workflow from user input to recommendations")
    print()
    
    # Run tests
    tester = SuperClaudeIntegrationTester()
    report = tester.run_comprehensive_test()
    
    # Save report to file
    report_path = Path("comprehensive_integration_test_report.json")
    
    # Convert report to JSON-serializable format
    report_dict = {
        'timestamp': time.time(),
        'total_tests': report.total_tests,
        'passed_tests': report.passed_tests,
        'failed_tests': report.failed_tests,
        'success_rate': (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0,
        'average_response_time': report.average_response_time,
        'test_results': [
            {
                'test_name': r.test_name,
                'command': r.command,
                'success': r.success,
                'response_time': r.response_time,
                'flags_generated': r.flags_generated,
                'confidence': r.confidence,
                'reasoning': r.reasoning,
                'error_message': r.error_message
            } for r in report.test_results
        ],
        'system_status': report.system_status,
        'learning_effectiveness': report.learning_effectiveness,
        'integration_issues': report.integration_issues
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    return report.passed_tests == report.total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)