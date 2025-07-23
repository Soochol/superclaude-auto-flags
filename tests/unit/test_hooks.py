#!/usr/bin/env python3
"""
SuperClaude Hook Testing Script
Hook 기능이 정상적으로 작동하는지 테스트
"""

import sys
import json
import subprocess
from pathlib import Path

def test_prompt_hook():
    """UserPromptSubmit Hook 테스트"""
    print("🧪 Testing UserPromptSubmit Hook...")
    
    hook_script = Path.home() / '.claude' / 'superclaude_prompt_hook.py'
    
    if not hook_script.exists():
        print("❌ Hook script not found. Run installation first.")
        return False
    
    # 테스트 프롬프트
    test_prompts = [
        "/sc:analyze 보안 취약점 찾아줘",
        "/sc:implement React 컴포넌트",
        "/sc:improve 성능 최적화",
        "일반 명령어 테스트"
    ]
    
    success_count = 0
    
    for prompt in test_prompts:
        try:
            result = subprocess.run(
                ['python3', str(hook_script), prompt],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("continue"):
                    success_count += 1
                    
                    if prompt.startswith("/sc:") and "new_prompt" in response:
                        print(f"✅ {prompt[:20]}... → Enhanced")
                    else:
                        print(f"✅ {prompt[:20]}... → Passed through")
                else:
                    print(f"❌ {prompt[:20]}... → Blocked")
            else:
                print(f"❌ {prompt[:20]}... → Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ {prompt[:20]}... → Exception: {e}")
    
    print(f"\nUserPromptSubmit Hook Test: {success_count}/{len(test_prompts)} passed")
    return success_count == len(test_prompts)

def test_tool_optimizer():
    """Tool Optimizer 테스트"""
    print("\n🔧 Testing Tool Optimizer...")
    
    optimizer_script = Path.home() / '.claude' / 'tool_optimizer.py'
    
    if not optimizer_script.exists():
        print("❌ Tool optimizer script not found. Run installation first.")
        return False
    
    # 테스트 케이스
    test_cases = [
        ("Read", '{"file_path": "/very/large/file.txt"}'),
        ("Grep", '{"pattern": "test", "path": "."}'),
        ("Edit", '{"file_path": "config.json", "old_string": "old", "new_string": "new"}'),
        ("Bash", '{"command": "ls -la"}'),
        ("Bash", '{"command": "rm -rf /"}')  # 위험한 명령어 테스트
    ]
    
    success_count = 0
    
    for tool_name, params_json in test_cases:
        try:
            process = subprocess.Popen(
                ['python3', str(optimizer_script), tool_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=params_json, timeout=10)
            
            if process.returncode == 0:
                response = json.loads(stdout)
                
                if tool_name == "Bash" and "rm -rf /" in params_json:
                    # 위험한 명령어는 차단되어야 함
                    if not response.get("continue"):
                        print(f"✅ {tool_name} (dangerous) → Blocked correctly")
                        success_count += 1
                    else:
                        print(f"❌ {tool_name} (dangerous) → Should be blocked")
                else:
                    if response.get("continue"):
                        print(f"✅ {tool_name} → Optimized")
                        success_count += 1
                    else:
                        print(f"❌ {tool_name} → Unexpected block")
            else:
                print(f"❌ {tool_name} → Error: {stderr}")
                
        except Exception as e:
            print(f"❌ {tool_name} → Exception: {e}")
    
    print(f"\nTool Optimizer Test: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

def test_wrapper_compatibility():
    """기존 Wrapper와의 호환성 테스트"""
    print("\n🔄 Testing Wrapper Compatibility...")
    
    wrapper_script = Path.home() / '.claude' / 'claude_smart_wrapper.py'
    
    if not wrapper_script.exists():
        print("❌ Wrapper script not found. Run installation first.")
        return False
    
    try:
        # 도움말 테스트
        result = subprocess.run(
            ['python3', str(wrapper_script), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "SuperClaude" in result.stdout:
            print("✅ Wrapper help system working")
            return True
        else:
            print(f"❌ Wrapper help failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Wrapper test exception: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 SuperClaude Hook System Test Suite")
    print("=" * 50)
    
    # 설치 확인
    claude_dir = Path.home() / '.claude'
    if not claude_dir.exists():
        print("❌ .claude directory not found. Please run installation first.")
        sys.exit(1)
    
    # 각 테스트 실행
    tests = [
        ("UserPromptSubmit Hook", test_prompt_hook),
        ("Tool Optimizer", test_tool_optimizer), 
        ("Wrapper Compatibility", test_wrapper_compatibility)
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
        print("\n💡 Next steps:")
        print("1. Run: python3 install_with_hooks.py --hooks")
        print("2. Restart your shell: source ~/.bashrc")
        print("3. Test: claude '/sc:analyze test command'")
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()