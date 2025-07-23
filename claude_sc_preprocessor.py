#!/usr/bin/env python3
"""
SuperClaude 지능형 플래그 자동완성 시스템

사용자가 /sc: 명령어를 입력하면 ORCHESTRATOR.md 로직에 따라
자동으로 최적의 플래그 조합을 추천하고 적용하는 시스템
"""

import re
import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ProjectContext:
    """프로젝트 컨텍스트 정보"""
    project_type: str
    domain: str
    complexity: str
    file_count: int
    framework: Optional[str] = None
    language: Optional[str] = None
    

@dataclass
class FlagRecommendation:
    """플래그 추천 결과"""
    flags: str
    confidence: int
    reasoning: str
    mcp_servers: List[str]
    personas: List[str]


class PatternMatcher:
    """ORCHESTRATOR.md 패턴 매칭 엔진"""
    
    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)
        self.orchestrator_patterns = self._load_orchestrator_patterns()
    
    def _load_rules(self, path: str) -> Dict:
        """규칙 파일 로드"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict:
        """기본 규칙 반환 (파일이 없을 때)"""
        return {
            'patterns': {
                'analyze_general': {
                    'keywords': ['analyze', '분석', 'review', '검토'],
                    'base_flags': '--persona-analyzer --think',
                    'confidence': 85,
                    'mcp_servers': ['Sequential']
                },
                'analyze_security': {
                    'keywords': ['security', '보안', 'vulnerability', '취약점', 'audit'],
                    'base_flags': '--persona-security --focus security --think --validate',
                    'confidence': 95,
                    'mcp_servers': ['Sequential']
                },
                'analyze_performance': {
                    'keywords': ['performance', '성능', 'optimize', '최적화', 'bottleneck'],
                    'base_flags': '--persona-performance --think-hard --focus performance',
                    'confidence': 90,
                    'mcp_servers': ['Sequential', 'Playwright']
                },
                'implement_ui': {
                    'keywords': ['component', '컴포넌트', 'ui', 'interface', 'frontend'],
                    'base_flags': '--persona-frontend --magic --c7',
                    'confidence': 94,
                    'mcp_servers': ['Magic', 'Context7']
                },
                'implement_api': {
                    'keywords': ['api', 'endpoint', 'backend', 'server', '서버'],
                    'base_flags': '--persona-backend --seq --c7',
                    'confidence': 92,
                    'mcp_servers': ['Sequential', 'Context7']
                },
                'improve_quality': {
                    'keywords': ['improve', '개선', 'refactor', '리팩토링', 'cleanup'],
                    'base_flags': '--persona-refactorer --loop --validate',
                    'confidence': 88,
                    'mcp_servers': ['Sequential']
                }
            }
        }
    
    def _load_orchestrator_patterns(self) -> Dict:
        """ORCHESTRATOR.md의 Master Routing Table 패턴"""
        return {
            'analyze_architecture': {
                'pattern': r'(analyze|분석).*(architecture|아키텍처)',
                'flags': '--persona-architect --ultrathink --seq',
                'confidence': 95,
                'complexity': 'complex'
            },
            'security_audit': {
                'pattern': r'(security|보안).*(audit|감사)',
                'flags': '--persona-security --ultrathink --seq --validate',
                'confidence': 95,
                'complexity': 'complex'
            },
            'implement_auth': {
                'pattern': r'(implement|구현).*(auth|인증)',
                'flags': '--persona-security --persona-backend --validate',
                'confidence': 90,
                'complexity': 'complex'
            },
            'optimize_performance': {
                'pattern': r'(optimize|최적화).*(performance|성능)',
                'flags': '--persona-performance --think-hard --play',
                'confidence': 90,
                'complexity': 'complex'
            }
        }
    
    def find_best_match(self, command: str, description: str, context: ProjectContext) -> FlagRecommendation:
        """최적의 플래그 조합 찾기"""
        
        # 1. ORCHESTRATOR 고급 패턴 우선 확인
        full_text = f"{command} {description}".lower()
        
        for pattern_name, pattern_info in self.orchestrator_patterns.items():
            if re.search(pattern_info['pattern'], full_text, re.IGNORECASE):
                return FlagRecommendation(
                    flags=pattern_info['flags'],
                    confidence=pattern_info['confidence'],
                    reasoning=f"ORCHESTRATOR 패턴 매칭: {pattern_name}",
                    mcp_servers=self._extract_mcp_servers(pattern_info['flags']),
                    personas=self._extract_personas(pattern_info['flags'])
                )
        
        # 2. 기본 규칙 패턴 매칭 - 전체 텍스트에서 매칭
        best_match = None
        best_pattern_name = None
        highest_score = 0
        
        # 우선순위 패턴 먼저 확인 (보안, 성능, 아키텍처 등)
        priority_patterns = ['analyze_security', 'analyze_performance', 'analyze_architecture', 'implement_authentication']
        
        for pattern_name in priority_patterns:
            if pattern_name in self.rules['patterns']:
                pattern_info = self.rules['patterns'][pattern_name]
                score = self._calculate_match_score(full_text, pattern_info['keywords'])
                if score > 0:  # 키워드가 하나라도 매칭되면 최우선
                    highest_score = score + 0.5  # 우선순위 보너스
                    best_match = pattern_info
                    best_pattern_name = pattern_name
                    break
        
        # 우선순위 패턴에서 매칭 안된 경우 일반 패턴 확인
        if not best_match:
            for pattern_name, pattern_info in self.rules['patterns'].items():
                score = self._calculate_match_score(full_text, pattern_info['keywords'])
                
                if score > highest_score:
                    highest_score = score
                    best_match = pattern_info
                    best_pattern_name = pattern_name
                
        if best_match and highest_score > 0.0:  # 키워드가 하나라도 매칭되면
            flags = self._apply_context_modifiers(best_match['base_flags'], context)
            return FlagRecommendation(
                flags=flags,
                confidence=min(95, int(best_match['confidence'] * (0.5 + highest_score * 0.5))),
                reasoning=f"패턴 매칭: {best_pattern_name} (점수: {highest_score:.2f})",
                mcp_servers=best_match.get('mcp_servers', []),
                personas=self._extract_personas(flags)
            )
        
        # 3. 기본 폴백
        return self._get_default_recommendation(command, context)
    
    def _calculate_match_score(self, text: str, keywords: List[str]) -> float:
        """키워드 매칭 점수 계산"""
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        return matches / len(keywords) if keywords else 0
    
    def _apply_context_modifiers(self, base_flags: str, context: ProjectContext) -> str:
        """프로젝트 컨텍스트에 따른 플래그 수정"""
        flags = base_flags
        
        # 복잡도에 따른 thinking 레벨 조정
        if context.complexity == 'complex' and '--think' in flags and '--think-hard' not in flags:
            flags = flags.replace('--think', '--think-hard')
        
        # 프로젝트 타입별 최적화
        if context.project_type == 'python_backend':
            if '--persona-backend' not in flags and 'analyze' in flags:
                flags += ' --validate'  # Python 백엔드는 추가 검증
        
        # 파일 수에 따른 delegation 추가
        if context.file_count > 50:
            flags += ' --delegate'
        
        # 토큰 효율성을 위한 압축
        flags += ' --uc'
        
        return flags
    
    def _extract_mcp_servers(self, flags: str) -> List[str]:
        """플래그에서 MCP 서버 추출"""
        servers = []
        if '--seq' in flags or '--sequential' in flags:
            servers.append('Sequential')
        if '--c7' in flags or '--context7' in flags:
            servers.append('Context7')
        if '--magic' in flags:
            servers.append('Magic')
        if '--play' in flags or '--playwright' in flags:
            servers.append('Playwright')
        return servers
    
    def _extract_personas(self, flags: str) -> List[str]:
        """플래그에서 persona 추출"""
        personas = []
        persona_map = {
            '--persona-analyzer': 'analyzer',
            '--persona-architect': 'architect', 
            '--persona-security': 'security',
            '--persona-performance': 'performance',
            '--persona-frontend': 'frontend',
            '--persona-backend': 'backend',
            '--persona-refactorer': 'refactorer'
        }
        
        for flag, persona in persona_map.items():
            if flag in flags:
                personas.append(persona)
        
        return personas
    
    def _get_default_recommendation(self, command: str, context: ProjectContext) -> FlagRecommendation:
        """기본 추천 (매칭 실패 시)"""
        if 'analyze' in command:
            flags = '--persona-analyzer --think --uc'
            confidence = 70
        elif 'implement' in command:
            if context.project_type == 'python_backend':
                flags = '--persona-backend --c7 --uc'
            else:
                flags = '--persona-frontend --magic --uc'
            confidence = 75
        elif 'improve' in command:
            flags = '--persona-refactorer --think --uc'
            confidence = 70
        else:
            flags = '--think --uc'
            confidence = 60
            
        return FlagRecommendation(
            flags=flags,
            confidence=confidence,
            reasoning="기본 명령어 패턴 기반 추천",
            mcp_servers=self._extract_mcp_servers(flags),
            personas=self._extract_personas(flags)
        )


class ProjectAnalyzer:
    """프로젝트 컨텍스트 분석기"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def analyze(self) -> ProjectContext:
        """프로젝트 분석"""
        
        # 언어 및 프레임워크 탐지
        language, framework = self._detect_language_and_framework()
        
        # 프로젝트 타입 결정
        project_type = self._determine_project_type(language, framework)
        
        # 도메인 추정
        domain = self._estimate_domain()
        
        # 복잡도 계산
        complexity = self._calculate_complexity()
        
        # 파일 수 계산
        file_count = self._count_source_files()
        
        return ProjectContext(
            project_type=project_type,
            domain=domain, 
            complexity=complexity,
            file_count=file_count,
            framework=framework,
            language=language
        )
    
    def _detect_language_and_framework(self) -> Tuple[str, Optional[str]]:
        """언어 및 프레임워크 탐지"""
        
        # Python 체크
        if (self.project_path / 'pyproject.toml').exists() or \
           (self.project_path / 'requirements.txt').exists():
            
            # Python 프레임워크 체크
            framework = None
            if (self.project_path / 'main.py').exists():
                try:
                    main_content = (self.project_path / 'main.py').read_text()
                    if 'asyncio' in main_content:
                        framework = 'asyncio'
                    elif 'flask' in main_content.lower():
                        framework = 'flask'
                    elif 'django' in main_content.lower():
                        framework = 'django'
                    elif 'fastapi' in main_content.lower():
                        framework = 'fastapi'
                except:
                    pass
            
            return 'python', framework
        
        # JavaScript/TypeScript 체크
        if (self.project_path / 'package.json').exists():
            try:
                package_json = json.loads((self.project_path / 'package.json').read_text())
                deps = {**package_json.get('dependencies', {}), 
                       **package_json.get('devDependencies', {})}
                
                if 'react' in deps:
                    return 'javascript', 'react'
                elif 'vue' in deps:
                    return 'javascript', 'vue'
                elif 'angular' in deps:
                    return 'javascript', 'angular'
                else:
                    return 'javascript', 'node'
            except:
                return 'javascript', None
        
        return 'unknown', None
    
    def _determine_project_type(self, language: str, framework: Optional[str]) -> str:
        """프로젝트 타입 결정"""
        if language == 'python':
            if framework in ['flask', 'django', 'fastapi']:
                return 'python_web'
            elif framework == 'asyncio':
                return 'python_backend'
            else:
                return 'python_general'
        elif language == 'javascript':
            if framework in ['react', 'vue', 'angular']:
                return 'frontend'
            else:
                return 'backend'
        else:
            return 'general'
    
    def _estimate_domain(self) -> str:
        """도메인 추정"""
        project_name = self.project_path.name.lower()
        
        if 'test' in project_name or 'eol' in project_name:
            return 'hardware_testing'
        elif 'web' in project_name or 'api' in project_name:
            return 'web_development'
        elif 'ui' in project_name or 'frontend' in project_name:
            return 'frontend'
        elif 'ml' in project_name or 'ai' in project_name:
            return 'machine_learning'
        else:
            return 'general'
    
    def _calculate_complexity(self) -> str:
        """복잡도 계산"""
        file_count = self._count_source_files()
        
        if file_count > 100:
            return 'complex'
        elif file_count > 20:
            return 'moderate'
        else:
            return 'simple'
    
    def _count_source_files(self) -> int:
        """소스 파일 수 계산"""
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.go', '.rs', '.java', '.cpp', '.c']
        count = 0
        
        try:
            for ext in extensions:
                count += len(list(self.project_path.rglob(f'*{ext}')))
        except:
            count = 10  # 기본값
            
        return count


class SCCommandProcessor:
    """SuperClaude 명령어 전처리기"""
    
    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = str(Path.home() / '.claude' / 'orchestrator_rules.yaml')
        
        self.pattern_matcher = PatternMatcher(rules_path)
        self.current_dir = os.getcwd()
        
    def process(self, user_input: str) -> str:
        """사용자 입력 전처리"""
        
        # /sc: 명령어가 아니면 그대로 반환
        if not user_input.strip().startswith('/sc:'):
            return user_input
        
        try:
            # 명령어와 설명 분리
            command, description = self._parse_sc_command(user_input)
            
            # 프로젝트 컨텍스트 분석
            context = self._get_project_context()
            
            # 최적 플래그 조합 찾기
            recommendation = self.pattern_matcher.find_best_match(command, description, context)
            
            # 결과 포맷팅
            enhanced_input = self._format_enhanced_command(
                user_input, recommendation, context
            )
            
            return enhanced_input
            
        except Exception as e:
            # 오류 발생 시 원본 입력 반환
            return user_input
    
    def _parse_sc_command(self, user_input: str) -> Tuple[str, str]:
        """SuperClaude 명령어 파싱"""
        # /sc:analyze 이 코드 분석해줘 -> ('analyze', '이 코드 분석해줘')
        match = re.match(r'/sc:(\w+)\s*(.*)', user_input.strip())
        if match:
            return match.group(1), match.group(2)
        else:
            return 'unknown', user_input
    
    def _get_project_context(self) -> ProjectContext:
        """현재 프로젝트 컨텍스트 가져오기"""
        analyzer = ProjectAnalyzer(self.current_dir)
        return analyzer.analyze()
    
    def _format_enhanced_command(self, original_input: str, recommendation: FlagRecommendation, context: ProjectContext) -> str:
        """향상된 명령어 포맷팅"""
        
        # SuperClaude 활성화 메시지 생성
        activation_msg = f"""🎯 SuperClaude 지능형 분석 활성화

📁 프로젝트: {context.project_type.replace('_', ' ').title()}
🏗️ 도메인: {context.domain.replace('_', ' ').title()}
📊 복잡도: {context.complexity} ({context.file_count}개 파일)

🚀 적용된 플래그: {recommendation.flags}
🎯 신뢰도: {recommendation.confidence}%
💡 근거: {recommendation.reasoning}

🔧 MCP 서버: {', '.join(recommendation.mcp_servers) if recommendation.mcp_servers else 'None'}
👥 전문가: {', '.join(recommendation.personas) if recommendation.personas else 'General'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{original_input} {recommendation.flags}"""
        
        return activation_msg


def main():
    """메인 함수 - CLI 실행용"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claude_sc_preprocessor.py '<user_input>'")
        sys.exit(1)
    
    user_input = sys.argv[1]
    processor = SCCommandProcessor()
    result = processor.process(user_input)
    
    print(result)


if __name__ == "__main__":
    main()