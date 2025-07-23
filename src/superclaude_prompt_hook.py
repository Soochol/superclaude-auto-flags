#!/usr/bin/env python3
"""
SuperClaude UserPromptSubmit Hook (학습 기능 통합)
Claude Code Hook 시스템과 통합된 지능형 프롬프트 전처리기

사용자가 claude "/sc:analyze ..." 명령어를 직접 사용할 수 있게 해주는 Hook
학습 기능을 통해 사용자별 맞춤 추천을 제공합니다.
"""

import sys
import json
import os
import time
from pathlib import Path

# claude_sc_preprocessor 임포트를 위한 경로 추가
sys.path.insert(0, str(Path.home() / '.claude'))

# 전역 변수로 프로세서 인스턴스 관리
_processor_instance = None
_last_interaction_start_time = None

def safe_hook_execution():
    """안전한 Hook 실행 - 학습 기능 포함"""
    global _processor_instance, _last_interaction_start_time
    
    try:
        # stdin에서 사용자 프롬프트 읽기
        if not sys.stdin.isatty():
            user_prompt = sys.stdin.read().strip()
        else:
            # 테스트용: 명령행 인자에서 읽기
            user_prompt = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ""
        
        # /sc: 명령어인지 확인
        if not user_prompt.startswith('/sc:'):
            # 일반 명령어는 그대로 진행
            return {"continue": True}
        
        # SuperClaude 처리기 임포트 (지연 임포트로 오류 방지)
        try:
            from claude_sc_preprocessor import SCCommandProcessor
        except ImportError:
            # 처리기를 찾을 수 없으면 원본 그대로 진행
            return {"continue": True}
        
        # 프로세서 인스턴스 재사용 (학습 상태 유지)
        if _processor_instance is None:
            _processor_instance = SCCommandProcessor()
        
        # 상호작용 시작 시간 기록
        _last_interaction_start_time = time.time()
        
        # SuperClaude 전처리 실행 (학습 기능 포함)
        enhanced_prompt = _processor_instance.process(user_prompt)
        
        # Hook 응답: 새로운 프롬프트로 교체
        return {
            "continue": True,
            "new_prompt": enhanced_prompt
        }
        
    except Exception as e:
        # 모든 오류 상황에서 기본 동작으로 fallback
        error_log_path = Path.home() / '.claude' / 'logs' / 'hook_errors.log'
        try:
            error_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(error_log_path, 'a') as f:
                f.write(f"SuperClaude Hook Error: {e}\n")
        except:
            pass  # 로그 실패도 무시하고 계속 진행
        
        return {"continue": True}

def main():
    """메인 실행 함수"""
    result = safe_hook_execution()
    print(json.dumps(result))

if __name__ == "__main__":
    main()