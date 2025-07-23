#!/usr/bin/env python3
"""
Claude Code Smart Wrapper

Claude Code를 감싸서 SuperClaude 지능형 플래그 추천 시스템을 투명하게 적용하는 wrapper
사용자는 단순히 /sc: 명령어만 입력하면 자동으로 최적의 플래그가 적용됩니다.
"""

import sys
import subprocess
import os
import json
from pathlib import Path

# claude_sc_preprocessor를 import하기 위해 경로 추가
sys.path.insert(0, str(Path.home() / '.claude'))

try:
    from claude_sc_preprocessor import SCCommandProcessor
except ImportError:
    # 모듈을 찾을 수 없는 경우 기본 동작
    SCCommandProcessor = None


def is_sc_command(prompt: str) -> bool:
    """SuperClaude 명령어인지 확인"""
    return prompt.strip().startswith('/sc:')


def process_prompt(prompt: str) -> str:
    """프롬프트 전처리"""
    if not SCCommandProcessor or not is_sc_command(prompt):
        return prompt
    
    try:
        processor = SCCommandProcessor()
        return processor.process(prompt)
    except Exception:
        # 오류 발생 시 원본 반환
        return prompt


def get_claude_command() -> str:
    """실제 Claude Code 명령어 경로 찾기"""
    # PATH에서 claude 명령어 찾기
    claude_paths = [
        '/usr/local/bin/claude',
        '/usr/bin/claude',
        '/opt/homebrew/bin/claude',
        '~/.local/bin/claude'
    ]
    
    for path in claude_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path) and os.access(expanded_path, os.X_OK):
            return expanded_path
    
    # PATH에서 검색
    try:
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # 기본값
    return 'claude'


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("Usage: claude-smart '<prompt>'")
        print("       claude-smart --help")
        sys.exit(1)
    
    # 도움말 표시
    if sys.argv[1] in ['--help', '-h']:
        print("""
Claude Code Smart Wrapper with SuperClaude Integration

사용법:
  claude-smart '<prompt>'                    # 일반 Claude Code 사용
  claude-smart '/sc:analyze 코드 분석해줘'     # SuperClaude 자동 플래그 적용
  claude-smart '/sc:implement 새 기능'        # UI/백엔드 자동 감지
  claude-smart '/sc:improve 성능 최적화'      # 성능 최적화 플래그 자동 적용

SuperClaude 명령어:
  /sc:analyze   - 코드/시스템 분석 (자동 persona 선택)
  /sc:implement - 기능 구현 (프로젝트 타입별 최적화)
  /sc:improve   - 코드 개선 (품질/성능 자동 감지)
  /sc:build     - 프로젝트 빌드 최적화
  /sc:test      - 테스트 실행 및 검증
  /sc:document  - 문서 작성

자동 적용되는 기능:
  ✅ 프로젝트 타입 자동 감지 (Python/JavaScript/etc)
  ✅ 복잡도 기반 thinking 레벨 조정
  ✅ 도메인별 최적 persona 선택
  ✅ MCP 서버 자동 활성화
  ✅ 대용량 프로젝트 delegation 적용
        """)
        sys.exit(0)
    
    # 사용자 입력 가져오기
    user_prompt = sys.argv[1]
    
    # SuperClaude 전처리 적용
    processed_prompt = process_prompt(user_prompt)
    
    # Claude Code 실행
    claude_cmd = get_claude_command()
    
    try:
        # Claude Code에 전처리된 프롬프트 전달
        result = subprocess.run(
            [claude_cmd, processed_prompt],
            check=False  # Claude Code의 exit code를 그대로 전달
        )
        sys.exit(result.returncode)
        
    except FileNotFoundError:
        print(f"Error: Claude Code not found at '{claude_cmd}'")
        print("Please install Claude Code or check your PATH")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error executing Claude Code: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()