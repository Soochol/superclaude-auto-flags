#!/usr/bin/env python3
"""
SuperClaude Learning Data Collector
사용자 행동 데이터 수집 시스템
"""

import time
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from learning_storage import LearningStorage, UserInteraction, FeedbackRecord, get_learning_storage

@dataclass
class CommandAnalysis:
    """명령어 분석 결과"""
    command_type: str
    complexity_score: float
    expected_duration: float
    risk_level: str
    success_indicators: List[str]

class LearningDataCollector:
    """사용자 행동 및 시스템 성능 데이터 수집"""
    
    def __init__(self, storage: Optional[LearningStorage] = None):
        self.storage = storage or get_learning_storage()
        self.current_interaction_id: Optional[str] = None
        self.interaction_start_time: Optional[float] = None
        self.project_context_cache: Dict[str, Any] = {}
    
    def start_interaction(self, user_input: str, recommended_flags: str, 
                         confidence: int, reasoning: str, 
                         project_context: Dict[str, Any]) -> str:
        """상호작용 시작 기록"""
        self.interaction_start_time = time.time()
        
        # 명령어 파싱
        command, description = self._parse_user_input(user_input)
        
        # 프로젝트 해시 생성
        project_hash = self.storage.get_project_hash(os.getcwd())
        
        # 상호작용 기록 생성
        interaction = UserInteraction(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            command=command,
            description=description,
            recommended_flags=recommended_flags,
            actual_flags="",  # 실제 사용된 플래그는 나중에 업데이트
            project_context=project_context,
            success=False,  # 초기값, 나중에 업데이트
            execution_time=0.0,  # 나중에 계산
            confidence=confidence,
            reasoning=reasoning,
            user_id=self.storage.user_id,
            project_hash=project_hash
        )
        
        self.current_interaction_id = self.storage.record_interaction(interaction)
        return self.current_interaction_id
    
    def end_interaction(self, actual_flags: str, success: bool, 
                       error_message: Optional[str] = None):
        """상호작용 종료 기록"""
        if not self.current_interaction_id or not self.interaction_start_time:
            return
        
        execution_time = time.time() - self.interaction_start_time
        
        # 데이터베이스에서 기존 상호작용 조회 후 업데이트
        interactions = self.storage.get_user_interactions(days=1)
        for interaction in interactions:
            if str(interaction['id']) == self.current_interaction_id:
                # 성공 여부 분석
                analyzed_success = self._analyze_success(
                    interaction['command'], 
                    success, 
                    error_message,
                    execution_time
                )
                
                # 상호작용 업데이트 (실제로는 새로운 기록을 만들어야 함)
                updated_interaction = UserInteraction(
                    timestamp=interaction['timestamp'],
                    user_input=interaction['user_input'],
                    command=interaction['command'],
                    description=interaction['description'],
                    recommended_flags=interaction['recommended_flags'],
                    actual_flags=actual_flags,
                    project_context=json.loads(interaction['project_context']),
                    success=analyzed_success,
                    execution_time=execution_time,
                    confidence=interaction['confidence'],
                    reasoning=interaction['reasoning'],
                    user_id=interaction['user_id'],
                    project_hash=interaction['project_hash']
                )
                
                # 패턴 성공률 업데이트
                pattern_name = self._identify_pattern(
                    interaction['command'], 
                    interaction['description']
                )
                
                if pattern_name:
                    self.storage.update_pattern_success(
                        pattern_name, 
                        analyzed_success,
                        json.loads(interaction['project_context'])
                    )
                
                # 암시적 피드백 기록
                self.record_implicit_feedback(analyzed_success, execution_time)
                break
        
        self.current_interaction_id = None
        self.interaction_start_time = None
    
    def record_implicit_feedback(self, success: bool, execution_time: float):
        """암시적 피드백 기록 (사용자 행동 기반)"""
        if not self.current_interaction_id:
            return
        
        feedback = FeedbackRecord(
            timestamp=datetime.now().isoformat(),
            interaction_id=self.current_interaction_id,
            feedback_type='implicit',
            rating=self._calculate_implicit_rating(success, execution_time),
            success_indicator=success,
            user_correction=None,
            user_id=self.storage.user_id,
            project_hash=self.storage.get_project_hash(os.getcwd())
        )
        
        self.storage.record_feedback(feedback)
    
    def record_explicit_feedback(self, rating: int, correction: Optional[str] = None):
        """명시적 피드백 기록 (사용자 직접 입력)"""
        if not self.current_interaction_id:
            return
        
        feedback = FeedbackRecord(
            timestamp=datetime.now().isoformat(),
            interaction_id=self.current_interaction_id,
            feedback_type='explicit',
            rating=rating,
            success_indicator=rating >= 3,
            user_correction=correction,
            user_id=self.storage.user_id,
            project_hash=self.storage.get_project_hash(os.getcwd())
        )
        
        self.storage.record_feedback(feedback)
    
    def analyze_command_complexity(self, user_input: str, 
                                 project_context: Dict[str, Any]) -> CommandAnalysis:
        """명령어 복잡도 분석"""
        command, description = self._parse_user_input(user_input)
        
        # 복잡도 스코어 계산
        complexity_score = self._calculate_complexity_score(command, description, project_context)
        
        # 예상 실행 시간 계산
        expected_duration = self._estimate_duration(command, complexity_score, project_context)
        
        # 위험도 평가
        risk_level = self._assess_risk_level(command, description)
        
        # 성공 지표 정의
        success_indicators = self._define_success_indicators(command)
        
        return CommandAnalysis(
            command_type=command,
            complexity_score=complexity_score,
            expected_duration=expected_duration,
            risk_level=risk_level,
            success_indicators=success_indicators
        )
    
    def collect_project_context(self, project_path: str) -> Dict[str, Any]:
        """프로젝트 컨텍스트 수집"""
        project_path = Path(project_path)
        project_hash = self.storage.get_project_hash(str(project_path))
        
        # 캐시된 컨텍스트 확인
        if project_hash in self.project_context_cache:
            cache_time = self.project_context_cache[project_hash].get('_cache_time', 0)
            if time.time() - cache_time < 3600:  # 1시간 캐시
                return self.project_context_cache[project_hash]
        
        context = {
            'project_path': str(project_path),
            'project_hash': project_hash,
            'file_count': self._count_files(project_path),
            'languages': self._detect_languages(project_path),
            'frameworks': self._detect_frameworks(project_path),
            'project_size': self._calculate_project_size(project_path),
            'complexity_indicators': self._analyze_complexity_indicators(project_path),
            'last_modified': self._get_last_modified(project_path),
            'git_info': self._get_git_info(project_path),
            '_cache_time': time.time()
        }
        
        self.project_context_cache[project_hash] = context
        return context
    
    def _parse_user_input(self, user_input: str) -> Tuple[str, str]:
        """사용자 입력 파싱"""
        if user_input.startswith('/sc:'):
            match = re.match(r'/sc:(\w+)\s*(.*)', user_input.strip())
            if match:
                return match.group(1), match.group(2)
        return 'unknown', user_input
    
    def _analyze_success(self, command: str, reported_success: bool, 
                        error_message: Optional[str], execution_time: float) -> bool:
        """성공 여부 분석"""
        # 보고된 성공 여부를 기본으로 하되, 추가 지표로 검증
        if not reported_success:
            return False
        
        # 실행 시간이 너무 짧으면 실패일 가능성
        if execution_time < 1.0 and command in ['implement', 'analyze', 'improve']:
            return False
        
        # 에러 메시지가 있으면 실패
        if error_message and any(keyword in error_message.lower() for keyword in ['error', 'failed', 'exception']):
            return False
        
        return True
    
    def _identify_pattern(self, command: str, description: str) -> Optional[str]:
        """사용된 패턴 식별"""
        text = f"{command} {description}".lower()
        
        # 패턴 매칭 로직 (orchestrator_rules.yaml과 동일)
        pattern_keywords = {
            'analyze_security': ['security', '보안', 'vulnerability', '취약점'],
            'analyze_performance': ['performance', '성능', 'optimize', '최적화'],
            'implement_ui': ['component', '컴포넌트', 'ui', 'interface'],
            'implement_api': ['api', 'endpoint', 'backend', '백엔드'],
            'improve_quality': ['improve', '개선', 'refactor', '리팩토링']
        }
        
        for pattern_name, keywords in pattern_keywords.items():
            if any(keyword in text for keyword in keywords):
                return pattern_name
        
        return f"{command}_general"
    
    def _calculate_complexity_score(self, command: str, description: str, 
                                  project_context: Dict[str, Any]) -> float:
        """복잡도 스코어 계산 (0.0 - 1.0)"""
        score = 0.0
        
        # 명령어 기본 복잡도
        command_complexity = {
            'analyze': 0.4,
            'implement': 0.6,
            'improve': 0.5,
            'debug': 0.7,
            'document': 0.2
        }
        score += command_complexity.get(command, 0.3)
        
        # 설명 길이에 따른 복잡도
        word_count = len(description.split())
        score += min(word_count / 100, 0.3)
        
        # 프로젝트 크기에 따른 복잡도
        file_count = project_context.get('file_count', 0)
        if file_count > 100:
            score += 0.2
        elif file_count > 50:
            score += 0.1
        
        # 키워드 기반 복잡도 증가
        complex_keywords = ['architecture', 'system', 'comprehensive', 'entire', 'security', 'performance']
        for keyword in complex_keywords:
            if keyword in description.lower():
                score += 0.1
        
        return min(score, 1.0)
    
    def _estimate_duration(self, command: str, complexity_score: float, 
                          project_context: Dict[str, Any]) -> float:
        """예상 실행 시간 추정 (초)"""
        base_durations = {
            'analyze': 30,
            'implement': 60,
            'improve': 45,
            'debug': 40,
            'document': 20
        }
        
        base_duration = base_durations.get(command, 30)
        complexity_multiplier = 1 + (complexity_score * 2)
        
        return base_duration * complexity_multiplier
    
    def _assess_risk_level(self, command: str, description: str) -> str:
        """위험도 평가"""
        high_risk_keywords = ['delete', 'remove', 'drop', 'truncate', 'rm -rf']
        medium_risk_keywords = ['modify', 'update', 'change', 'refactor']
        
        text = f"{command} {description}".lower()
        
        if any(keyword in text for keyword in high_risk_keywords):
            return 'high'
        elif any(keyword in text for keyword in medium_risk_keywords):
            return 'medium'
        else:
            return 'low'
    
    def _define_success_indicators(self, command: str) -> List[str]:
        """성공 지표 정의"""
        indicators = {
            'analyze': ['completed_analysis', 'no_errors', 'generated_report'],
            'implement': ['code_created', 'tests_pass', 'no_syntax_errors'],
            'improve': ['code_modified', 'improvements_applied', 'quality_increased'],
            'debug': ['issue_identified', 'fix_applied', 'tests_pass'],
            'document': ['documentation_created', 'content_complete']
        }
        
        return indicators.get(command, ['completed_successfully'])
    
    def _calculate_implicit_rating(self, success: bool, execution_time: float) -> int:
        """암시적 평점 계산 (1-5)"""
        if not success:
            return 1
        
        # 실행 시간 기반 평점
        if execution_time < 10:
            return 5  # 매우 빠름
        elif execution_time < 30:
            return 4  # 빠름
        elif execution_time < 60:
            return 3  # 보통
        elif execution_time < 120:
            return 2  # 느림
        else:
            return 1  # 매우 느림
    
    def _count_files(self, project_path: Path) -> int:
        """파일 수 계산"""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.go', '.rs', '.java', '.cpp', '.c']
        count = 0
        try:
            for ext in extensions:
                count += len(list(project_path.rglob(f'*{ext}')))
        except:
            count = 0
        return count
    
    def _detect_languages(self, project_path: Path) -> List[str]:
        """언어 감지"""
        languages = []
        
        if list(project_path.glob('*.py')) or (project_path / 'pyproject.toml').exists():
            languages.append('python')
        if list(project_path.glob('*.js')) or (project_path / 'package.json').exists():
            languages.append('javascript')
        if list(project_path.glob('*.ts')):
            languages.append('typescript')
        if list(project_path.glob('*.go')):
            languages.append('go')
        if list(project_path.glob('*.rs')):
            languages.append('rust')
        
        return languages
    
    def _detect_frameworks(self, project_path: Path) -> List[str]:
        """프레임워크 감지"""
        frameworks = []
        
        # package.json 확인
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        frameworks.append('react')
                    if 'vue' in deps:
                        frameworks.append('vue')
                    if 'angular' in deps:
                        frameworks.append('angular')
                    if 'express' in deps:
                        frameworks.append('express')
            except:
                pass
        
        # Python 프레임워크 감지
        if (project_path / 'requirements.txt').exists():
            try:
                with open(project_path / 'requirements.txt') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        frameworks.append('django')
                    if 'flask' in content:
                        frameworks.append('flask')
                    if 'fastapi' in content:
                        frameworks.append('fastapi')
            except:
                pass
        
        return frameworks
    
    def _calculate_project_size(self, project_path: Path) -> str:
        """프로젝트 크기 계산"""
        file_count = self._count_files(project_path)
        
        if file_count > 1000:
            return 'very_large'
        elif file_count > 100:
            return 'large'
        elif file_count > 20:
            return 'medium'
        else:
            return 'small'
    
    def _analyze_complexity_indicators(self, project_path: Path) -> Dict[str, Any]:
        """복잡도 지표 분석"""
        indicators = {
            'has_tests': bool(list(project_path.glob('**/test*'))),
            'has_docs': bool(list(project_path.glob('**/doc*')) or list(project_path.glob('README*'))),
            'has_config': bool(list(project_path.glob('**/config*'))),
            'directory_depth': self._calculate_directory_depth(project_path),
            'has_ci': bool(list(project_path.glob('.github/**')) or list(project_path.glob('.gitlab-ci*')))
        }
        
        return indicators
    
    def _calculate_directory_depth(self, project_path: Path) -> int:
        """디렉토리 깊이 계산"""
        max_depth = 0
        try:
            for item in project_path.rglob('*'):
                if item.is_dir():
                    depth = len(item.relative_to(project_path).parts)
                    max_depth = max(max_depth, depth)
        except:
            max_depth = 1
        return max_depth
    
    def _get_last_modified(self, project_path: Path) -> str:
        """최근 수정 시간"""
        try:
            latest_time = 0
            for item in project_path.rglob('*'):
                if item.is_file():
                    latest_time = max(latest_time, item.stat().st_mtime)
            return datetime.fromtimestamp(latest_time).isoformat()
        except:
            return datetime.now().isoformat()
    
    def _get_git_info(self, project_path: Path) -> Dict[str, Any]:
        """Git 정보 수집"""
        git_dir = project_path / '.git'
        if not git_dir.exists():
            return {'is_git_repo': False}
        
        try:
            # HEAD 파일에서 현재 브랜치 정보
            head_file = git_dir / 'HEAD'
            current_branch = 'unknown'
            if head_file.exists():
                head_content = head_file.read_text().strip()
                if head_content.startswith('ref: refs/heads/'):
                    current_branch = head_content.split('/')[-1]
            
            return {
                'is_git_repo': True,
                'current_branch': current_branch,
                'has_uncommitted_changes': self._has_uncommitted_changes(project_path)
            }
        except:
            return {'is_git_repo': True, 'error': 'failed_to_read_git_info'}
    
    def _has_uncommitted_changes(self, project_path: Path) -> bool:
        """커밋되지 않은 변경사항 확인"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return bool(result.stdout.strip())
        except:
            return False

# 전역 데이터 수집기 인스턴스
_collector_instance = None

def get_data_collector() -> LearningDataCollector:
    """전역 데이터 수집기 인스턴스 가져오기"""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = LearningDataCollector()
    return _collector_instance