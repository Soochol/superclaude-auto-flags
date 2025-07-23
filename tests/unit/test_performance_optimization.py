#!/usr/bin/env python3
"""
SuperClaude 성능 최적화 테스트
빠른 응답 시스템 검증
"""

import time
import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path.cwd()))

def test_quick_response_performance():
    """빠른 응답 성능 테스트"""
    print("🚀 SuperClaude 빠른 응답 성능 테스트")
    print("=" * 60)
    
    try:
        from claude_sc_preprocessor import SCCommandProcessor
        from performance_optimizer import get_performance_optimizer
        
        processor = SCCommandProcessor()
        optimizer = get_performance_optimizer()
        
        # 테스트 케이스들
        test_cases = [
            "/sc:analyze find security vulnerabilities",
            "/sc:implement React user interface component", 
            "/sc:improve database query performance",
            "/sc:analyze src/hardware/mcu architecture",
            "/sc:implement new authentication service"
        ]
        
        print("\n📋 빠른 모드 성능 테스트:")
        print("-" * 40)
        
        total_time = 0
        for i, test_input in enumerate(test_cases, 1):
            start_time = time.time()
            
            # 빠른 모드로 처리
            result = processor.process(test_input, quick_mode=True)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            total_time += response_time
            
            print(f"\n{i}. 명령어: {test_input}")
            print(f"   ⏱️ 응답 시간: {response_time:.1f}ms")
            print(f"   ✅ 처리 성공: {'빠른 응답' in result}")
            
            # 100ms 이하 목표 확인
            if response_time <= 100:
                print(f"   🎯 목표 달성: ✅ (<100ms)")
            else:
                print(f"   ⚠️ 목표 미달성: {response_time:.1f}ms")
        
        avg_time = total_time / len(test_cases)
        print(f"\n📊 평균 응답 시간: {avg_time:.1f}ms")
        
        # 성능 메트릭 확인
        metrics = optimizer.get_performance_metrics()
        print(f"\n📈 성능 메트릭:")
        print(f"   • 총 요청 수: {metrics['total_requests']}")
        print(f"   • 캐시 히트: {metrics['cache_hits']}")
        print(f"   • 빠른 응답: {metrics['quick_responses']}")
        print(f"   • 캐시 히트율: {metrics.get('cache_hit_rate', 0):.1%}")
        
        return avg_time <= 100
        
    except ImportError as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def test_cache_effectiveness():
    """캐시 효과성 테스트"""
    print("\n🗄️ 캐시 효과성 테스트")
    print("-" * 40)
    
    try:
        from performance_optimizer import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        test_context = {
            'project_type': 'python_backend',
            'complexity': 'moderate', 
            'file_count': 25
        }
        
        test_command = "analyze security vulnerabilities"
        
        # 첫 번째 요청 (캐시 미스)
        start_time = time.time()
        result1 = optimizer.get_quick_recommendation(
            "/sc:" + test_command, "analyze", "security vulnerabilities", test_context
        )
        first_time = (time.time() - start_time) * 1000
        
        # 두 번째 요청 (캐시 히트)
        start_time = time.time()
        result2 = optimizer.get_quick_recommendation(
            "/sc:" + test_command, "analyze", "security vulnerabilities", test_context
        )
        second_time = (time.time() - start_time) * 1000
        
        print(f"첫 번째 요청 (캐시 미스): {first_time:.1f}ms")
        print(f"두 번째 요청 (캐시 히트): {second_time:.1f}ms")
        print(f"성능 개선: {((first_time - second_time) / first_time * 100):.1f}%")
        
        # 결과 일관성 확인
        flags_match = result1.flags == result2.flags
        confidence_match = result1.confidence == result2.confidence
        
        print(f"플래그 일관성: {'✅' if flags_match else '❌'}")
        print(f"신뢰도 일관성: {'✅' if confidence_match else '❌'}")
        
        return second_time < first_time and flags_match and confidence_match
        
    except Exception as e:
        print(f"❌ 캐시 테스트 실패: {e}")
        return False

def test_background_processing():
    """백그라운드 처리 테스트"""
    print("\n🔄 백그라운드 처리 테스트")
    print("-" * 40)
    
    try:
        from performance_optimizer import get_performance_optimizer
        
        optimizer = get_performance_optimizer()
        
        # 백그라운드 큐에 작업 추가
        test_task = {
            'user_input': '/sc:analyze test background processing',
            'context': {'project_type': 'test'},
            'cache_key': 'test_background'
        }
        
        initial_queue_size = len(optimizer.background_queue)
        optimizer._queue_background_enhancement(
            test_task['user_input'], 
            test_task['context'], 
            test_task['cache_key']
        )
        
        # 큐에 추가되었는지 확인
        queue_added = len(optimizer.background_queue) > initial_queue_size
        
        print(f"백그라운드 큐 추가: {'✅' if queue_added else '❌'}")
        print(f"백그라운드 처리 실행: {'✅' if optimizer.is_processing or optimizer.background_thread else '❌'}")
        
        # 잠시 대기하여 처리 확인
        time.sleep(0.5)
        processing_started = optimizer.is_processing
        
        print(f"처리 시작됨: {'✅' if processing_started else '❌'}")
        
        return queue_added
        
    except Exception as e:
        print(f"❌ 백그라운드 처리 테스트 실패: {e}")
        return False

def test_real_world_scenario():
    """실제 사용 시나리오 테스트"""
    print("\n🌍 실제 사용 시나리오 테스트")
    print("-" * 40)
    
    try:
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        
        # WF_EOL_TESTER 프로젝트 시뮬레이션
        test_scenarios = [
            {
                'command': '/sc:analyze src/hardware/mcu security issues',
                'expected_persona': 'security',
                'expected_time_limit': 150  # ms
            },
            {
                'command': '/sc:implement new temperature sensor service',
                'expected_persona': 'backend',
                'expected_time_limit': 120
            },
            {
                'command': '/sc:improve serial communication performance',
                'expected_persona': 'performance', 
                'expected_time_limit': 130
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n시나리오 {i}: {scenario['command']}")
            
            start_time = time.time()
            result = processor.process(scenario['command'], quick_mode=True)
            response_time = (time.time() - start_time) * 1000
            
            # 응답 시간 확인
            time_ok = response_time <= scenario['expected_time_limit']
            
            # Persona 확인
            persona_found = f"--persona-{scenario['expected_persona']}" in result
            
            print(f"   ⏱️ 응답 시간: {response_time:.1f}ms ({'✅' if time_ok else '❌'})")
            print(f"   🎭 예상 Persona: {'✅' if persona_found else '❌'}")
            print(f"   📋 빠른 응답: {'✅' if '빠른 응답' in result else '❌'}")
            
            if not (time_ok and persona_found):
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 실제 시나리오 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 SuperClaude 성능 최적화 종합 테스트")
    print("=" * 80)
    
    tests = [
        ("빠른 응답 성능", test_quick_response_performance),
        ("캐시 효과성", test_cache_effectiveness), 
        ("백그라운드 처리", test_background_processing),
        ("실제 사용 시나리오", test_real_world_scenario)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 테스트 시작...")
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} 테스트 통과")
                passed += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"💥 {test_name} 테스트 오류: {e}")
    
    print(f"\n🎯 최종 결과: {passed}/{total} 테스트 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 성능 최적화 테스트 통과! SuperClaude가 빨라졌습니다!")
    else:
        print("⚠️ 일부 테스트 실패. 추가 최적화가 필요합니다.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)