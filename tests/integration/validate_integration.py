#!/usr/bin/env python3
"""
Quick Integration Validation Script
Tests the core SuperClaude learning system functionality
"""

import os
import sys
import tempfile
import time
import json
from pathlib import Path

# Set working directory and paths
os.chdir('/home/blessp/my_code/superclaude-auto-flags')
sys.path.insert(0, '/home/blessp/my_code/superclaude-auto-flags')

def validate_core_components():
    """Validate core component functionality"""
    
    print("🔍 SuperClaude Integration Validation")
    print("=" * 50)
    
    results = {
        'tests_run': 0,
        'tests_passed': 0,
        'component_status': {},
        'integration_working': False,
        'recommendations_generated': [],
        'performance_metrics': {}
    }
    
    # Test 1: SCCommandProcessor
    print("\n📝 Test 1: SCCommandProcessor")
    results['tests_run'] += 1
    
    try:
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        
        # Test various commands
        test_commands = [
            "/sc:analyze find security vulnerabilities",
            "/sc:implement React component",
            "/sc:improve performance",
            "normal command"
        ]
        
        processor_results = []
        for cmd in test_commands:
            start_time = time.time()
            result = processor.process(cmd)
            end_time = time.time()
            
            is_enhanced = len(result) > len(cmd) if cmd.startswith('/sc:') else result == cmd
            
            processor_results.append({
                'command': cmd,
                'enhanced': is_enhanced,
                'response_time': end_time - start_time,
                'result_length': len(result)
            })
            
            print(f"  {'✅' if is_enhanced else '❌'} {cmd[:30]}... ({end_time - start_time:.3f}s)")
        
        # Success if at least 75% of /sc: commands were enhanced
        sc_commands = [r for r in processor_results if r['command'].startswith('/sc:')]
        enhanced_count = sum(1 for r in sc_commands if r['enhanced'])
        success_rate = enhanced_count / len(sc_commands) * 100 if sc_commands else 0
        
        if success_rate >= 75:
            results['tests_passed'] += 1
            results['component_status']['SCCommandProcessor'] = 'PASS'
            print(f"  📊 Success Rate: {success_rate:.1f}% - PASS")
        else:
            results['component_status']['SCCommandProcessor'] = 'FAIL'
            print(f"  📊 Success Rate: {success_rate:.1f}% - FAIL")
        
        results['performance_metrics']['avg_response_time'] = sum(r['response_time'] for r in processor_results) / len(processor_results)
        
    except Exception as e:
        results['component_status']['SCCommandProcessor'] = f'ERROR: {str(e)}'
        print(f"  ❌ Error: {str(e)}")
    
    # Test 2: Learning Storage
    print("\n💾 Test 2: Learning Storage")
    results['tests_run'] += 1
    
    try:
        from learning_storage import LearningStorage, UserInteraction
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            
            # Create test interaction
            interaction = UserInteraction(
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%S'),
                user_input="/sc:test command",
                command="test",
                description="test description",
                recommended_flags="--test-flag",
                actual_flags="--test-flag",
                project_context={"test": "context"},
                success=True,
                execution_time=5.0,
                confidence=90,
                reasoning="test reasoning",
                user_id=storage.user_id,
                project_hash="test_hash"
            )
            
            # Test CRUD operations
            interaction_id = storage.record_interaction(interaction)
            retrieved_interactions = storage.get_user_interactions(days=1)
            
            if interaction_id and len(retrieved_interactions) > 0:
                results['tests_passed'] += 1
                results['component_status']['LearningStorage'] = 'PASS'
                print(f"  ✅ Storage operations: PASS")
                print(f"  📊 Interaction ID: {interaction_id}")
                print(f"  📊 Retrieved: {len(retrieved_interactions)} interactions")
            else:
                results['component_status']['LearningStorage'] = 'FAIL'
                print(f"  ❌ Storage operations: FAIL")
                
    except Exception as e:
        results['component_status']['LearningStorage'] = f'ERROR: {str(e)}'
        print(f"  ❌ Error: {str(e)}")
    
    # Test 3: Learning Engine
    print("\n🧠 Test 3: Learning Engine")
    results['tests_run'] += 1
    
    try:
        from learning_engine import AdaptiveLearningEngine
        from learning_storage import LearningStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LearningStorage(temp_dir)
            engine = AdaptiveLearningEngine(storage)
            
            # Test recommendation generation
            recommendation = engine.get_adaptive_recommendation(
                command="analyze",
                description="security test",
                project_context={"project_type": "python_backend", "complexity": "moderate"}
            )
            
            if recommendation and hasattr(recommendation, 'flags') and len(recommendation.flags) > 0:
                results['tests_passed'] += 1
                results['component_status']['LearningEngine'] = 'PASS'
                results['recommendations_generated'].append({
                    'flags': recommendation.flags,
                    'confidence': recommendation.confidence,
                    'reasoning': recommendation.reasoning
                })
                print(f"  ✅ Recommendation generation: PASS")
                print(f"  📊 Flags: {recommendation.flags}")
                print(f"  📊 Confidence: {recommendation.confidence}")
            else:
                results['component_status']['LearningEngine'] = 'FAIL'
                print(f"  ❌ Recommendation generation: FAIL")
                
    except Exception as e:
        results['component_status']['LearningEngine'] = f'ERROR: {str(e)}'
        print(f"  ❌ Error: {str(e)}")
    
    # Test 4: End-to-End Integration
    print("\n🔄 Test 4: End-to-End Integration")
    results['tests_run'] += 1
    
    try:
        # Test the complete workflow
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        
        # Test realistic scenarios
        scenarios = [
            {
                'input': '/sc:analyze find security vulnerabilities in this Python project',
                'expected_keywords': ['security', 'persona-security', 'validate']
            },
            {
                'input': '/sc:implement user authentication system',
                'expected_keywords': ['auth', 'security', 'backend']
            }
        ]
        
        successful_integrations = 0
        
        for scenario in scenarios:
            start_time = time.time()
            result = processor.process(scenario['input'])
            end_time = time.time()
            
            # Check if expected keywords are present
            result_lower = result.lower()
            keyword_matches = sum(1 for keyword in scenario['expected_keywords'] 
                                if keyword.lower() in result_lower)
            
            if keyword_matches >= len(scenario['expected_keywords']) * 0.5:  # At least 50% match
                successful_integrations += 1
                print(f"  ✅ {scenario['input'][:40]}... ({end_time - start_time:.3f}s)")
            else:
                print(f"  ❌ {scenario['input'][:40]}... ({end_time - start_time:.3f}s)")
        
        if successful_integrations >= len(scenarios) * 0.75:  # At least 75% success
            results['tests_passed'] += 1
            results['component_status']['EndToEndIntegration'] = 'PASS'
            results['integration_working'] = True
            print(f"  📊 Integration Success: {successful_integrations}/{len(scenarios)} - PASS")
        else:
            results['component_status']['EndToEndIntegration'] = 'FAIL'
            print(f"  📊 Integration Success: {successful_integrations}/{len(scenarios)} - FAIL")
            
    except Exception as e:
        results['component_status']['EndToEndIntegration'] = f'ERROR: {str(e)}'
        print(f"  ❌ Error: {str(e)}")
    
    # Test 5: Hook Integration Check
    print("\n🔗 Test 5: Hook Integration Check")
    results['tests_run'] += 1
    
    try:
        # Check if hook files exist and are properly configured
        hook_file = Path('/home/blessp/my_code/superclaude-auto-flags/superclaude_prompt_hook.py')
        config_file = Path('/home/blessp/my_code/superclaude-auto-flags/superclaude_hooks_config.json')
        
        hook_exists = hook_file.exists()
        config_exists = config_file.exists()
        
        if hook_exists and config_exists:
            # Try to import hook
            import superclaude_prompt_hook
            
            # Check if required functions exist
            has_functions = (hasattr(superclaude_prompt_hook, 'safe_hook_execution') or
                           hasattr(superclaude_prompt_hook, 'main'))
            
            if has_functions:
                results['tests_passed'] += 1
                results['component_status']['HookIntegration'] = 'PASS'
                print(f"  ✅ Hook files and functions: PASS")
                print(f"  📊 Hook file: {hook_file.name}")
                print(f"  📊 Config file: {config_file.name}")
            else:
                results['component_status']['HookIntegration'] = 'FAIL - Missing functions'
                print(f"  ❌ Hook functions missing")
        else:
            results['component_status']['HookIntegration'] = 'FAIL - Missing files'
            print(f"  ❌ Hook files missing: hook={hook_exists}, config={config_exists}")
            
    except Exception as e:
        results['component_status']['HookIntegration'] = f'ERROR: {str(e)}'
        print(f"  ❌ Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    success_rate = results['tests_passed'] / results['tests_run'] * 100 if results['tests_run'] > 0 else 0
    
    print(f"Tests Passed: {results['tests_passed']}/{results['tests_run']} ({success_rate:.1f}%)")
    print(f"Integration Working: {'✅ YES' if results['integration_working'] else '❌ NO'}")
    
    if 'avg_response_time' in results['performance_metrics']:
        avg_time = results['performance_metrics']['avg_response_time']
        throughput = 1.0 / avg_time if avg_time > 0 else 0
        print(f"Average Response Time: {avg_time:.3f}s")
        print(f"Estimated Throughput: {throughput:.1f} requests/sec")
    
    print(f"Recommendations Generated: {len(results['recommendations_generated'])}")
    
    print("\nComponent Status:")
    for component, status in results['component_status'].items():
        icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
        print(f"  {icon} {component}: {status}")
    
    # Overall Assessment
    if success_rate >= 90:
        assessment = "🟢 EXCELLENT - System fully functional"
    elif success_rate >= 75:
        assessment = "🟡 GOOD - System mostly functional"
    elif success_rate >= 50:
        assessment = "🟠 FAIR - System partially functional"
    else:
        assessment = "🔴 POOR - System has major issues"
    
    print(f"\nOverall Assessment: {assessment}")
    
    # Save results
    report_path = Path('/home/blessp/my_code/superclaude-auto-flags/validation_report.json')
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = validate_core_components()
    print(f"\n🎯 Final Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    sys.exit(0 if success else 1)