#!/usr/bin/env python3
"""
SuperClaude Hook-Only Testing Script
Hook 전용 시스템이 정상적으로 작동하는지 테스트
"""

import sys
import json
import subprocess
from pathlib import Path

def test_prompt_hook():
    """UserPromptSubmit Hook 테스트"""
    print("🎣 Testing UserPromptSubmit Hook...")
    
    hook_script = Path.home() / '.claude' / 'superclaude_prompt_hook.py'
    
    if not hook_script.exists():
        print("❌ Hook script not found. Run installation first.")
        return False
    
    # 직접 임포트해서 테스트
    sys.path.insert(0, str(Path.home() / '.claude'))
    
    try:
        # 시뮬레이션: /sc: 명령어 테스트
        sys.argv = ['superclaude_prompt_hook.py', '/sc:analyze', '보안', '취약점', '찾아줘']
        
        # Hook 스크립트 임포트 및 실행
        from superclaude_prompt_hook import safe_hook_execution
        result = safe_hook_execution()
        
        print(f"Hook 결과: {result}")
        
        if result.get("continue") and "new_prompt" in result:
            enhanced_prompt = result['new_prompt']
            print("✅ /sc: 명령어 성공적으로 처리됨")
            print(f"변환된 프롬프트: {enhanced_prompt}")
            
            # 변환 품질 검증
            if "--persona-" in enhanced_prompt and "/analyze" in enhanced_prompt:
                print("✅ 플래그 변환 품질 검증 통과")
                return True
            else:
                print("❌ 플래그 변환 품질 문제")
                return False
        else:
            print("❌ Hook 처리 실패")
            return False
            
    except Exception as e:
        print(f"❌ Hook 테스트 중 오류: {e}")
        return False

def test_tool_optimizer():
    """Tool Optimizer 테스트"""
    print("\n🔧 Testing Tool Optimizer...")
    
    optimizer_script = Path.home() / '.claude' / 'tool_optimizer.py'
    
    if not optimizer_script.exists():
        print("❌ Tool optimizer not found")
        return False
    
    try:
        # 직접 임포트해서 테스트
        sys.path.insert(0, str(Path.home() / '.claude'))
        from tool_optimizer import ToolOptimizer
        
        optimizer = ToolOptimizer()
        
        # Read 도구 테스트 (대용량 파일)
        read_result = optimizer.optimize_read_tool({
            "file_path": "/home/blessp/my_code/superclaude-auto-flags/README.md"
        })
        print(f"Read 최적화 결과: {read_result.get('continue', False)}")
        
        # Bash 도구 안전성 테스트
        bash_safe = optimizer.optimize_bash_tool({"command": "ls -la"})
        bash_dangerous = optimizer.optimize_bash_tool({"command": "rm -rf /"})
        
        print(f"Bash 안전 명령어: {bash_safe.get('continue', False)}")
        print(f"Bash 위험 명령어 차단: {not bash_dangerous.get('continue', True)}")
        
        if (bash_safe.get("continue") and 
            not bash_dangerous.get("continue") and
            read_result.get("continue")):
            print("✅ Tool Optimizer 모든 테스트 통과")
            return True
        else:
            print("❌ Tool Optimizer 일부 테스트 실패")
            return False
            
    except Exception as e:
        print(f"❌ Tool Optimizer 테스트 중 오류: {e}")
        return False

def test_hook_integration():
    """Hook 통합 테스트"""
    print("\n🎯 Testing Hook Integration...")
    
    # Claude 설정 파일 확인
    settings_path = Path.home() / '.claude' / 'settings.local.json'
    
    if not settings_path.exists():
        print("❌ Claude settings file not found")
        return False
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        hooks = settings.get('hooks', {})
        
        # UserPromptSubmit Hook 확인
        user_prompt_hooks = hooks.get('UserPromptSubmit', [])
        pre_tool_hooks = hooks.get('PreToolUse', [])
        
        if not user_prompt_hooks:
            print("❌ UserPromptSubmit Hook not configured")
            return False
        
        if not pre_tool_hooks:
            print("❌ PreToolUse Hook not configured")
            return False
        
        print("✅ Hook 설정 파일 정상 확인")
        print(f"   UserPromptSubmit: {len(user_prompt_hooks)} hook(s)")
        print(f"   PreToolUse: {len(pre_tool_hooks)} hook(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Hook 통합 테스트 중 오류: {e}")
        return False

def test_core_files():
    """핵심 파일 존재 확인"""
    print("\n📁 Testing Core Files...")
    
    required_files = [
        'claude_sc_preprocessor.py',
        'orchestrator_rules.yaml',
        'superclaude_prompt_hook.py',
        'tool_optimizer.py'
    ]
    
    claude_dir = Path.home() / '.claude'
    missing_files = []
    
    for file_name in required_files:
        file_path = claude_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
        else:
            print(f"✅ {file_name}")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ 모든 핵심 파일 존재 확인")
    return True

def main():
    """메인 테스트 실행"""
    print("🚀 SuperClaude Hook-Only System Test Suite")
    print("=" * 60)
    
    # 각 테스트 실행
    tests = [
        ("Core Files Check", test_core_files),
        ("UserPromptSubmit Hook", test_prompt_hook),
        ("Tool Optimizer", test_tool_optimizer), 
        ("Hook Integration", test_hook_integration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    # 최종 결과
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! SuperClaude Hook system is working correctly.")
        print("\n💡 Ready to use:")
        print("   claude '/sc:analyze find security issues'")
        print("   claude '/sc:implement React component'")
        print("   claude '/sc:improve performance optimization'")
        print("\n🎣 Hook features active:")
        print("   ✅ Intelligent /sc: command processing")
        print("   ✅ Automatic tool optimization")
        print("   ✅ Enhanced safety checks")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        print("💡 Try running: python3 install.py")
        sys.exit(1)

if __name__ == "__main__":
    main()