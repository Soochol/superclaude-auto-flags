#!/usr/bin/env python3
"""
SuperClaude Tool Optimizer - PreToolUse Hook
ORCHESTRATOR.md 로직 기반 도구별 자동 최적화
"""

import sys
import json
import os
from pathlib import Path

class ToolOptimizer:
    """도구별 최적화 로직"""
    
    def __init__(self):
        self.project_path = Path.cwd()
        self.file_count = self._count_source_files()
    
    def _count_source_files(self) -> int:
        """소스 파일 수 계산"""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.go', '.rs', '.java', '.cpp', '.c']
        count = 0
        
        try:
            for ext in extensions:
                count += len(list(self.project_path.rglob(f'*{ext}')))
        except:
            count = 50  # 기본값
        
        return count
    
    def _is_large_file(self, file_path: str) -> bool:
        """대용량 파일인지 확인"""
        try:
            if not file_path:
                return False
            path = Path(file_path)
            if path.exists():
                return path.stat().st_size > 100000  # 100KB 이상
        except:
            pass
        return False
    
    def optimize_read_tool(self, params: dict) -> dict:
        """Read 도구 최적화"""
        file_path = params.get('file_path', '')
        
        # 대용량 파일 자동 청킹
        if self._is_large_file(file_path):
            return {
                "continue": True,
                "new_params": {
                    **params,
                    "limit": 200,  # 처음 200줄만 읽기
                    "offset": 0
                }
            }
        
        return {"continue": True}
    
    def optimize_grep_tool(self, params: dict) -> dict:
        """Grep 도구 최적화"""
        # 대규모 프로젝트에서 scope 제한
        if self.file_count > 1000:
            new_params = {**params}
            
            # glob 패턴이 없으면 소스 파일만 검색
            if not params.get('glob'):
                new_params['glob'] = '*.{py,js,ts,jsx,tsx,vue}'
            
            # 결과 수 제한
            if not params.get('head_limit'):
                new_params['head_limit'] = 100
            
            return {
                "continue": True,
                "new_params": new_params
            }
        
        return {"continue": True}
    
    def optimize_edit_tool(self, params: dict) -> dict:
        """Edit 도구 최적화"""
        # 중요한 파일 백업 권장 (실제 백업은 사용자 결정)
        file_path = params.get('file_path', '')
        
        if any(important in file_path.lower() for important in 
               ['config', 'settings', 'package.json', 'requirements.txt']):
            # 중요한 파일 편집 시 주의 메시지 (실제로는 로그만)
            try:
                log_path = Path.home() / '.claude' / 'logs' / 'tool_optimizer.log'
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, 'a') as f:
                    f.write(f"Editing important file: {file_path}\n")
            except:
                pass
        
        return {"continue": True}
    
    def optimize_bash_tool(self, params: dict) -> dict:
        """Bash 도구 안전성 검증"""
        command = params.get('command', '')
        
        # 위험한 명령어 패턴 감지
        dangerous_patterns = ['rm -rf /', 'dd if=', 'mkfs', 'fdisk', 'format']
        
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return {
                    "continue": False,
                    "error": f"Potentially dangerous command detected: {pattern}"
                }
        
        return {"continue": True}

def safe_tool_optimization():
    """안전한 도구 최적화 실행"""
    try:
        if len(sys.argv) < 2:
            return {"continue": True}
        
        tool_name = sys.argv[1]
        
        # stdin에서 도구 파라미터 읽기
        if not sys.stdin.isatty():
            tool_params_json = sys.stdin.read().strip()
            if tool_params_json:
                tool_params = json.loads(tool_params_json)
            else:
                tool_params = {}
        else:
            tool_params = {}
        
        optimizer = ToolOptimizer()
        
        # 도구별 최적화 실행
        if tool_name.lower() == 'read':
            return optimizer.optimize_read_tool(tool_params)
        elif tool_name.lower() == 'grep':
            return optimizer.optimize_grep_tool(tool_params)
        elif tool_name.lower() in ['edit', 'multiedit']:
            return optimizer.optimize_edit_tool(tool_params)
        elif tool_name.lower() == 'bash':
            return optimizer.optimize_bash_tool(tool_params)
        else:
            return {"continue": True}
            
    except Exception as e:
        # 오류 시 기본 동작으로 fallback
        try:
            error_log_path = Path.home() / '.claude' / 'logs' / 'tool_optimizer_errors.log'
            error_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(error_log_path, 'a') as f:
                f.write(f"Tool Optimizer Error: {e}\n")
        except:
            pass
        
        return {"continue": True}

def main():
    """메인 실행 함수"""
    result = safe_tool_optimization()
    print(json.dumps(result))

if __name__ == "__main__":
    main()