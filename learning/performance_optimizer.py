#!/usr/bin/env python3
"""
SuperClaude Performance Optimizer
성능 최적화 및 빠른 응답 시스템
"""

import time
import threading
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class QuickRecommendation:
    """빠른 추천 결과"""
    flags: str
    confidence: int
    reasoning: str
    response_time_ms: float
    is_enhanced: bool = False
    enhanced_flags: Optional[str] = None
    enhanced_confidence: Optional[int] = None

class PerformanceOptimizer:
    """성능 최적화 시스템"""
    
    def __init__(self):
        # 캐시 시스템
        self.project_cache = {}
        self.pattern_cache = {}
        self.cache_ttl = 1800  # 30분
        
        # 성능 메트릭
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'average_response_time': 0.0,
            'quick_responses': 0,
            'enhanced_responses': 0
        }
        
        # 백그라운드 처리 큐
        self.background_queue = []
        self.background_thread = None
        self.is_processing = False
    
    def get_quick_recommendation(self, user_input: str, command: str, 
                                description: str, context: Dict[str, Any]) -> QuickRecommendation:
        """즉시 기본 추천 제공 (목표: <100ms)"""
        start_time = time.time()
        
        try:
            # 캐시 확인
            cache_key = f"{command}:{hash(description)}:{context.get('project_type', 'unknown')}"
            cached_result = self._get_cached_recommendation(cache_key)
            
            if cached_result:
                self.metrics['cache_hits'] += 1
                response_time = (time.time() - start_time) * 1000
                
                return QuickRecommendation(
                    flags=cached_result['flags'],
                    confidence=cached_result['confidence'],
                    reasoning=f"⚡ 캐시된 추천 (응답시간: {response_time:.1f}ms)",
                    response_time_ms=response_time,
                    is_enhanced=False
                )
            
            # 빠른 패턴 매칭
            quick_flags, confidence, reasoning = self._quick_pattern_match(command, description, context)
            
            response_time = (time.time() - start_time) * 1000
            self.metrics['quick_responses'] += 1
            
            # 결과 캐싱
            self._cache_recommendation(cache_key, {
                'flags': quick_flags,
                'confidence': confidence,
                'timestamp': datetime.now()
            })
            
            # 백그라운드에서 학습 기반 개선 처리 시작
            self._queue_background_enhancement(user_input, context, cache_key)
            
            return QuickRecommendation(
                flags=quick_flags,
                confidence=confidence,
                reasoning=f"⚡ 즉시 추천 (응답시간: {response_time:.1f}ms) • 학습 개선 진행 중...",
                response_time_ms=response_time,
                is_enhanced=False
            )
            
        except Exception as e:
            # 실패시 기본 추천
            response_time = (time.time() - start_time) * 1000
            return QuickRecommendation(
                flags="--think --uc",
                confidence=60,
                reasoning=f"⚡ 기본 추천 (오류 복구: {str(e)[:50]}...)",
                response_time_ms=response_time,
                is_enhanced=False
            )
    
    def _quick_pattern_match(self, command: str, description: str, 
                           context: Dict[str, Any]) -> Tuple[str, int, str]:
        """빠른 패턴 매칭 (복잡한 학습 로직 제외)"""
        
        text = f"{command} {description}".lower()
        
        # 우선순위 패턴들 (빠른 매칭)
        priority_patterns = {
            'security': {
                'keywords': ['security', '보안', 'vulnerability', '취약점', 'audit'],
                'flags': '--persona-security --focus security --validate --uc',
                'confidence': 95
            },
            'performance': {
                'keywords': ['performance', '성능', 'optimize', '최적화', 'bottleneck'],
                'flags': '--persona-performance --think-hard --focus performance --uc',
                'confidence': 90
            },
            'frontend': {
                'keywords': ['react', 'vue', 'component', '컴포넌트', 'ui', 'interface'],
                'flags': '--persona-frontend --magic --c7 --uc',
                'confidence': 94
            },
            'backend': {
                'keywords': ['api', 'server', '서버', 'backend', 'database'],
                'flags': '--persona-backend --seq --c7 --uc',
                'confidence': 92
            },
            'architecture': {
                'keywords': ['architecture', '아키텍처', 'design', 'pattern'],
                'flags': '--persona-architect --ultrathink --seq --uc',
                'confidence': 95
            }
        }
        
        # 키워드 매칭
        for pattern_name, pattern_info in priority_patterns.items():
            for keyword in pattern_info['keywords']:
                if keyword in text:
                    # 프로젝트 컨텍스트 기반 조정
                    flags = self._adjust_flags_for_context(pattern_info['flags'], context)
                    
                    return (
                        flags,
                        pattern_info['confidence'],
                        f"빠른 패턴 매칭: {pattern_name}"
                    )
        
        # 기본 명령어별 매칭
        if command == 'analyze':
            flags = '--persona-analyzer --think --uc'
            confidence = 80
        elif command == 'implement':
            if context.get('project_type', '').startswith('python'):
                flags = '--persona-backend --c7 --uc'
            else:
                flags = '--persona-frontend --magic --uc'
            confidence = 75
        elif command == 'improve':
            flags = '--persona-refactorer --loop --uc'
            confidence = 85
        else:
            flags = '--think --uc'
            confidence = 60
        
        # 컨텍스트 조정
        flags = self._adjust_flags_for_context(flags, context)
        
        return flags, confidence, f"기본 명령어 패턴: {command}"
    
    def _adjust_flags_for_context(self, base_flags: str, context: Dict[str, Any]) -> str:
        """프로젝트 컨텍스트에 따른 플래그 조정"""
        flags = base_flags
        
        # 복잡도에 따른 조정
        complexity = context.get('complexity', 'moderate')
        if complexity == 'complex' and '--think' in flags and '--think-hard' not in flags:
            flags = flags.replace('--think', '--think-hard')
        
        # 파일 수에 따른 delegation 추가
        file_count = context.get('file_count', 0)
        if file_count > 50 and '--delegate' not in flags:
            flags += ' --delegate'
        
        return flags
    
    def _get_cached_recommendation(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """캐시된 추천 조회"""
        if cache_key in self.pattern_cache:
            cached = self.pattern_cache[cache_key]
            # TTL 확인
            if datetime.now() - cached['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached
            else:
                # 만료된 캐시 삭제
                del self.pattern_cache[cache_key]
        
        return None
    
    def _cache_recommendation(self, cache_key: str, recommendation: Dict[str, Any]):
        """추천 결과 캐싱"""
        self.pattern_cache[cache_key] = recommendation
        
        # 캐시 크기 제한 (최대 1000개)
        if len(self.pattern_cache) > 1000:
            # 가장 오래된 항목 제거
            oldest_key = min(self.pattern_cache.keys(), 
                           key=lambda k: self.pattern_cache[k]['timestamp'])
            del self.pattern_cache[oldest_key]
    
    def _queue_background_enhancement(self, user_input: str, context: Dict[str, Any], cache_key: str):
        """백그라운드 학습 기반 개선 처리 큐에 추가"""
        enhancement_task = {
            'user_input': user_input,
            'context': context,
            'cache_key': cache_key,
            'timestamp': datetime.now()
        }
        
        self.background_queue.append(enhancement_task)
        
        # 백그라운드 스레드 시작 (아직 실행 중이 아니라면)
        if not self.is_processing:
            self._start_background_processing()
    
    def _start_background_processing(self):
        """백그라운드 처리 스레드 시작"""
        if self.background_thread and self.background_thread.is_alive():
            return
        
        self.is_processing = True
        self.background_thread = threading.Thread(target=self._background_processor, daemon=True)
        self.background_thread.start()
    
    def _background_processor(self):
        """백그라운드에서 학습 기반 개선 처리"""
        while self.background_queue or self.is_processing:
            try:
                if not self.background_queue:
                    time.sleep(0.1)
                    continue
                
                task = self.background_queue.pop(0)
                
                # 학습 기반 개선 처리 (시간이 걸리는 작업)
                enhanced_result = self._process_learning_enhancement(task)
                
                if enhanced_result:
                    # 캐시 업데이트
                    self._update_enhanced_cache(task['cache_key'], enhanced_result)
                    self.metrics['enhanced_responses'] += 1
                
            except Exception as e:
                print(f"Background processing error: {e}")
                continue
        
        self.is_processing = False
    
    def _process_learning_enhancement(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """학습 기반 개선 처리 (실제 학습 시스템 호출)"""
        try:
            # 여기서 실제 학습 시스템 호출
            # 시간이 걸리는 작업이므로 백그라운드에서 처리
            
            # 임시로 개선된 추천 시뮬레이션
            time.sleep(1)  # 학습 처리 시뮬레이션
            
            return {
                'enhanced_flags': task.get('context', {}).get('enhanced_flags', ''),
                'enhanced_confidence': 95,
                'enhancement_reasoning': '학습 기반 개선 완료'
            }
            
        except Exception as e:
            print(f"Learning enhancement error: {e}")
            return None
    
    def _update_enhanced_cache(self, cache_key: str, enhanced_result: Dict[str, Any]):
        """개선된 결과로 캐시 업데이트"""
        if cache_key in self.pattern_cache:
            self.pattern_cache[cache_key].update(enhanced_result)
            self.pattern_cache[cache_key]['enhanced'] = True
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        self.metrics['cache_hit_rate'] = (
            self.metrics['cache_hits'] / self.metrics['total_requests'] 
            if self.metrics['total_requests'] > 0 else 0
        )
        
        return self.metrics.copy()
    
    def clear_cache(self):
        """캐시 초기화"""
        self.project_cache.clear()
        self.pattern_cache.clear()
        print("✅ SuperClaude 캐시 초기화 완료")

# 전역 성능 최적화 인스턴스
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """전역 성능 최적화 인스턴스 반환"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def quick_recommend(user_input: str, command: str, description: str, 
                   context: Dict[str, Any]) -> QuickRecommendation:
    """빠른 추천 인터페이스"""
    optimizer = get_performance_optimizer()
    optimizer.metrics['total_requests'] += 1
    
    return optimizer.get_quick_recommendation(user_input, command, description, context)

if __name__ == "__main__":
    # 성능 테스트
    optimizer = PerformanceOptimizer()
    
    test_context = {
        'project_type': 'python_backend',
        'complexity': 'moderate',
        'file_count': 25
    }
    
    print("🚀 SuperClaude 성능 최적화 테스트")
    print("=" * 50)
    
    # 테스트 케이스들
    test_cases = [
        ("analyze security vulnerabilities", "analyze", "security vulnerabilities"),
        ("implement React component", "implement", "React component"),
        ("improve performance bottlenecks", "improve", "performance bottlenecks")
    ]
    
    for user_input, command, description in test_cases:
        result = optimizer.get_quick_recommendation(user_input, command, description, test_context)
        
        print(f"\n📋 명령어: {user_input}")
        print(f"⚡ 추천 플래그: {result.flags}")
        print(f"🎯 신뢰도: {result.confidence}%")
        print(f"⏱️ 응답 시간: {result.response_time_ms:.1f}ms")
        print(f"💡 근거: {result.reasoning}")
    
    print(f"\n📊 성능 메트릭:")
    metrics = optimizer.get_performance_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")