#!/usr/bin/env python3
"""
SuperClaude Personalized Adaptive Recommender
개인화된 적응형 추천 시스템
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from learning_storage import LearningStorage, get_learning_storage
from learning_engine import AdaptiveLearningEngine, get_learning_engine, RecommendationScore
from data_collector import LearningDataCollector, get_data_collector

@dataclass
class PersonalizedRecommendation:
    """개인화된 추천 결과"""
    flags: str
    confidence: int 
    reasoning: List[str]
    personalization_factors: Dict[str, float]
    learning_confidence: float
    fallback_used: bool
    recommendation_id: str

@dataclass
class UserProfile:
    """사용자 프로필"""
    user_id: str
    preferred_personas: Dict[str, float]
    preferred_thinking_levels: Dict[str, float]
    preferred_mcp_servers: Dict[str, float]
    project_type_preferences: Dict[str, float]
    complexity_preferences: Dict[str, float]
    success_patterns: Dict[str, float]
    last_updated: str
    total_interactions: int

class PersonalizedAdaptiveRecommender:
    """개인화된 적응형 추천기"""
    
    def __init__(self, storage: Optional[LearningStorage] = None,
                 learning_engine: Optional[AdaptiveLearningEngine] = None):
        self.storage = storage or get_learning_storage()
        self.learning_engine = learning_engine or get_learning_engine()
        self.data_collector = get_data_collector()
        
        # 개인화 파라미터
        self.personalization_weight = 0.4  # 개인화 vs 일반화 균형
        self.min_interactions_for_personalization = 10
        self.profile_cache_ttl = 1800  # 30분
        
        # 사용자 프로필 캐시
        self._user_profile_cache: Optional[UserProfile] = None
        self._profile_cache_time = 0
    
    def get_personalized_recommendation(self, user_input: str, project_context: Dict[str, Any]) -> PersonalizedRecommendation:
        """개인화된 추천 생성"""
        
        # 사용자 프로필 로드
        user_profile = self._get_user_profile()
        
        # 명령어 파싱
        command, description = self._parse_user_input(user_input)
        
        # 기본 학습 기반 추천 가져오기
        base_recommendation = self.learning_engine.get_adaptive_recommendation(
            command, description, project_context
        )
        
        # 개인화 적용
        personalized_rec = self._apply_personalization(
            base_recommendation, user_profile, project_context
        )
        
        # 추천 ID 생성
        recommendation_id = self._generate_recommendation_id(user_input, project_context)
        
        return PersonalizedRecommendation(
            flags=personalized_rec['flags'],
            confidence=personalized_rec['confidence'],
            reasoning=personalized_rec['reasoning'],
            personalization_factors=personalized_rec['personalization_factors'],
            learning_confidence=base_recommendation.score / 100,
            fallback_used=personalized_rec['fallback_used'],
            recommendation_id=recommendation_id
        )
    
    def update_personalization(self, recommendation_id: str, success: bool, 
                             execution_time: float, user_rating: Optional[int] = None):
        """개인화 모델 업데이트"""
        
        # 기본 학습 엔진 업데이트
        self.learning_engine.update_learning_from_feedback(
            recommendation_id, success, execution_time, user_rating
        )
        
        # 개인화 선호도 업데이트
        self._update_personal_preferences(recommendation_id, success, execution_time, user_rating)
        
        # 프로필 캐시 무효화
        self._invalidate_profile_cache()
    
    def analyze_personalization_effectiveness(self) -> Dict[str, Any]:
        """개인화 효과성 분석"""
        
        user_profile = self._get_user_profile()
        recent_interactions = self.storage.get_user_interactions(days=30)
        
        # 개인화 전후 성능 비교
        personalized_success_rate = self._calculate_personalized_success_rate(recent_interactions)
        baseline_success_rate = self._calculate_baseline_success_rate(recent_interactions)
        
        # 선호도 분석
        preference_diversity = self._calculate_preference_diversity(user_profile)
        preference_stability = self._calculate_preference_stability()
        
        analysis = {
            'personalization_improvement': personalized_success_rate - baseline_success_rate,
            'current_success_rate': personalized_success_rate,
            'baseline_success_rate': baseline_success_rate,
            'total_interactions': user_profile.total_interactions,
            'preference_diversity': preference_diversity,
            'preference_stability': preference_stability,
            'top_preferred_personas': self._get_top_preferences(user_profile.preferred_personas),
            'top_preferred_thinking_levels': self._get_top_preferences(user_profile.preferred_thinking_levels),
            'personalization_confidence': self._calculate_personalization_confidence(user_profile),
            'recommendations_today': len([i for i in recent_interactions if 
                                        datetime.fromisoformat(i['timestamp']).date() == datetime.now().date()])
        }
        
        return analysis
    
    def export_user_profile(self) -> Dict[str, Any]:
        """사용자 프로필 내보내기 (개인정보 제거)"""
        user_profile = self._get_user_profile()
        
        # 개인정보 제거한 익명화된 프로필
        anonymized_profile = {
            'profile_version': '1.0',
            'export_timestamp': datetime.now().isoformat(),
            'total_interactions': user_profile.total_interactions,
            'preferred_personas': user_profile.preferred_personas,
            'preferred_thinking_levels': user_profile.preferred_thinking_levels,
            'preferred_mcp_servers': user_profile.preferred_mcp_servers,
            'project_type_preferences': user_profile.project_type_preferences,
            'complexity_preferences': user_profile.complexity_preferences,
            'profile_maturity': 'mature' if user_profile.total_interactions > 50 else 'developing',
            'personalization_enabled': user_profile.total_interactions >= self.min_interactions_for_personalization
        }
        
        return anonymized_profile
    
    def _get_user_profile(self) -> UserProfile:
        """사용자 프로필 가져오기"""
        current_time = datetime.now().timestamp()
        
        # 캐시 확인
        if (self._user_profile_cache and 
            current_time - self._profile_cache_time < self.profile_cache_ttl):
            return self._user_profile_cache
        
        # 프로필 생성/업데이트
        user_profile = self._build_user_profile()
        
        # 캐시 업데이트
        self._user_profile_cache = user_profile
        self._profile_cache_time = current_time
        
        return user_profile
    
    def _build_user_profile(self) -> UserProfile:
        """사용자 프로필 구축"""
        
        # 최근 상호작용 데이터 수집
        interactions = self.storage.get_user_interactions(days=90)  # 3개월 데이터
        
        if len(interactions) < 3:
            # 기본 프로필 반환
            return self._create_default_profile()
        
        # 선호도 분석
        preferred_personas = self._analyze_persona_preferences(interactions)
        preferred_thinking_levels = self._analyze_thinking_level_preferences(interactions)
        preferred_mcp_servers = self._analyze_mcp_server_preferences(interactions)
        project_type_preferences = self._analyze_project_type_preferences(interactions)
        complexity_preferences = self._analyze_complexity_preferences(interactions)
        success_patterns = self._analyze_success_patterns(interactions)
        
        return UserProfile(
            user_id=self.storage.user_id,
            preferred_personas=preferred_personas,
            preferred_thinking_levels=preferred_thinking_levels,
            preferred_mcp_servers=preferred_mcp_servers,
            project_type_preferences=project_type_preferences,
            complexity_preferences=complexity_preferences,
            success_patterns=success_patterns,
            last_updated=datetime.now().isoformat(),
            total_interactions=len(interactions)
        )
    
    def _create_default_profile(self) -> UserProfile:
        """기본 사용자 프로필 생성"""
        return UserProfile(
            user_id=self.storage.user_id,
            preferred_personas={'analyzer': 1.0, 'backend': 0.8, 'frontend': 0.6},
            preferred_thinking_levels={'think': 1.0, 'think_hard': 0.7},
            preferred_mcp_servers={'Sequential': 1.0, 'Context7': 0.8},
            project_type_preferences={'python_backend': 1.0},
            complexity_preferences={'moderate': 1.0, 'complex': 0.8},
            success_patterns={},
            last_updated=datetime.now().isoformat(),
            total_interactions=0
        )
    
    def _apply_personalization(self, base_recommendation: RecommendationScore, 
                             user_profile: UserProfile, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """개인화 적용"""
        
        # 개인화가 가능한 최소 상호작용 수 확인
        if user_profile.total_interactions < self.min_interactions_for_personalization:
            return {
                'flags': base_recommendation.flags,
                'confidence': base_recommendation.confidence,
                'reasoning': base_recommendation.reasoning + ['개인화 데이터 부족 (기본 추천 사용)'],
                'personalization_factors': {'insufficient_data': True},
                'fallback_used': True
            }
        
        # 개인화 요소들 계산
        personalization_factors = {}
        reasoning = list(base_recommendation.reasoning)
        
        # 1. Persona 개인화
        personalized_flags = self._personalize_personas(
            base_recommendation.flags, user_profile.preferred_personas
        )
        if personalized_flags != base_recommendation.flags:
            reasoning.append("사용자 선호 persona로 조정")
            personalization_factors['persona_adjustment'] = True
        
        # 2. Thinking level 개인화
        personalized_flags = self._personalize_thinking_levels(
            personalized_flags, user_profile.preferred_thinking_levels, project_context
        )
        
        # 3. MCP 서버 개인화
        personalized_flags = self._personalize_mcp_servers(
            personalized_flags, user_profile.preferred_mcp_servers
        )
        
        # 4. 프로젝트 타입별 개인화
        personalized_flags = self._personalize_for_project_type(
            personalized_flags, user_profile.project_type_preferences, project_context
        )
        
        # 5. 개인화된 신뢰도 계산
        personalized_confidence = self._calculate_personalized_confidence(
            base_recommendation.confidence, user_profile, project_context
        )
        
        # 개인화 요소 요약
        personalization_factors.update({
            'persona_preferences_applied': len(user_profile.preferred_personas) > 0,
            'thinking_level_adjusted': 'thinking_level_adjustment' in reasoning,
            'mcp_server_optimized': len(user_profile.preferred_mcp_servers) > 0,
            'project_type_optimized': len(user_profile.project_type_preferences) > 0,
            'personalization_strength': self.personalization_weight,
            'confidence_boost': personalized_confidence - base_recommendation.confidence
        })
        
        return {
            'flags': personalized_flags,
            'confidence': personalized_confidence,
            'reasoning': reasoning,
            'personalization_factors': personalization_factors,
            'fallback_used': False
        }
    
    def _personalize_personas(self, flags: str, preferred_personas: Dict[str, float]) -> str:
        """Persona 개인화"""
        if not preferred_personas:
            return flags
        
        # 현재 플래그에서 persona 추출
        current_personas = []
        for flag in flags.split():
            if flag.startswith('--persona-'):
                current_personas.append(flag.replace('--persona-', ''))
        
        # 선호도가 높은 persona로 대체 고려
        flag_parts = flags.split()
        
        # 낮은 선호도의 persona 제거
        for i, flag in enumerate(flag_parts):
            if flag.startswith('--persona-'):
                persona_name = flag.replace('--persona-', '')
                preference = preferred_personas.get(persona_name, 0.5)
                
                # 선호도가 0.3 미만이면 제거 고려
                if preference < 0.3 and len(current_personas) > 1:
                    flag_parts[i] = ''
        
        # 높은 선호도의 persona 추가
        for persona, preference in sorted(preferred_personas.items(), key=lambda x: x[1], reverse=True):
            if preference > 0.8 and f'--persona-{persona}' not in flags:
                # 호환 가능한 persona인지 확인
                if self._is_compatible_persona(persona, current_personas):
                    flag_parts.append(f'--persona-{persona}')
                    break
        
        return ' '.join(filter(None, flag_parts))
    
    def _personalize_thinking_levels(self, flags: str, preferred_levels: Dict[str, float], 
                                   project_context: Dict[str, Any]) -> str:
        """Thinking level 개인화"""
        if not preferred_levels:
            return flags
        
        flag_parts = flags.split()
        current_thinking = None
        
        # 현재 thinking level 찾기
        thinking_flags = ['--think', '--think-hard', '--ultrathink']
        for flag in thinking_flags:
            if flag in flag_parts:
                current_thinking = flag.replace('--', '')
                break
        
        # 선호도 높은 thinking level 선택
        best_level = max(preferred_levels.items(), key=lambda x: x[1])
        preferred_level, preference_score = best_level
        
        # 프로젝트 복잡도와 선호도 조합
        project_complexity = project_context.get('complexity', 'moderate')
        complexity_multiplier = {'simple': 0.7, 'moderate': 1.0, 'complex': 1.3}.get(project_complexity, 1.0)
        
        adjusted_preference = preference_score * complexity_multiplier
        
        # thinking level 교체
        if current_thinking and adjusted_preference > 0.7:
            for i, flag in enumerate(flag_parts):
                if flag in thinking_flags:
                    flag_parts[i] = f'--{preferred_level}'
                    break
        
        return ' '.join(flag_parts)
    
    def _personalize_mcp_servers(self, flags: str, preferred_servers: Dict[str, float]) -> str:
        """MCP 서버 개인화"""
        if not preferred_servers:
            return flags
        
        flag_parts = flags.split()
        
        # MCP 서버 플래그 매핑
        server_flags = {
            'Sequential': ['--seq', '--sequential'],
            'Context7': ['--c7', '--context7'], 
            'Magic': ['--magic'],
            'Playwright': ['--play', '--playwright']
        }
        
        # 선호도 낮은 서버 제거
        for server, preference in preferred_servers.items():
            if preference < 0.4:
                server_flag_options = server_flags.get(server, [])
                for flag_option in server_flag_options:
                    if flag_option in flag_parts:
                        flag_parts.remove(flag_option)
        
        # 선호도 높은 서버 추가
        for server, preference in sorted(preferred_servers.items(), key=lambda x: x[1], reverse=True):
            if preference > 0.8:
                server_flag_options = server_flags.get(server, [])
                if server_flag_options and not any(opt in flag_parts for opt in server_flag_options):
                    flag_parts.append(server_flag_options[0])  # 첫 번째 옵션 사용
        
        return ' '.join(flag_parts)
    
    def _personalize_for_project_type(self, flags: str, project_preferences: Dict[str, float],
                                    project_context: Dict[str, Any]) -> str:
        """프로젝트 타입별 개인화"""
        current_project_type = project_context.get('project_type', 'unknown')
        preference = project_preferences.get(current_project_type, 0.5)
        
        flag_parts = flags.split()
        
        # 선호도가 높은 프로젝트 타입의 경우 추가 최적화
        if preference > 0.8:
            if current_project_type == 'python_backend' and '--validate' not in flag_parts:
                flag_parts.append('--validate')
            elif current_project_type == 'frontend' and '--magic' not in flag_parts:
                flag_parts.append('--magic')
            elif 'large' in current_project_type and '--delegate' not in flag_parts:
                flag_parts.append('--delegate')
        
        return ' '.join(flag_parts)
    
    def _calculate_personalized_confidence(self, base_confidence: int, user_profile: UserProfile,
                                         project_context: Dict[str, Any]) -> int:
        """개인화된 신뢰도 계산"""
        
        # 기본 신뢰도에서 시작
        confidence = base_confidence
        
        # 상호작용 수에 따른 개인화 신뢰도 보정
        interaction_factor = min(user_profile.total_interactions / 50, 1.0)  # 50회 이상에서 최대
        
        # 프로젝트 타입 일치도
        current_project_type = project_context.get('project_type', 'unknown')
        project_preference = user_profile.project_type_preferences.get(current_project_type, 0.5)
        
        # 복잡도 선호도 일치
        current_complexity = project_context.get('complexity', 'moderate')
        complexity_preference = user_profile.complexity_preferences.get(current_complexity, 0.5)
        
        # 개인화 보정 계산
        personalization_boost = (
            interaction_factor * 0.3 +
            (project_preference - 0.5) * 0.4 +
            (complexity_preference - 0.5) * 0.3
        ) * 20  # 최대 ±20점 보정
        
        # 최종 신뢰도 계산
        personalized_confidence = confidence + personalization_boost
        
        return max(50, min(98, int(personalized_confidence)))  # 50-98% 범위
    
    def _analyze_persona_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Persona 선호도 분석"""
        persona_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for interaction in interactions:
            flags = interaction.get('recommended_flags', '')
            success = interaction.get('success', False)
            
            # 플래그에서 persona 추출
            for flag in flags.split():
                if flag.startswith('--persona-'):
                    persona = flag.replace('--persona-', '')
                    persona_success[persona]['total'] += 1
                    if success:
                        persona_success[persona]['success'] += 1
        
        # 성공률 기반 선호도 계산
        preferences = {}
        for persona, stats in persona_success.items():
            if stats['total'] >= 3:  # 최소 3회 사용
                success_rate = stats['success'] / stats['total']
                preferences[persona] = success_rate
        
        return preferences
    
    def _analyze_thinking_level_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Thinking level 선호도 분석"""
        thinking_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for interaction in interactions:
            flags = interaction.get('recommended_flags', '')
            success = interaction.get('success', False)
            
            # thinking level 추출
            thinking_level = 'think'  # 기본값
            if '--ultrathink' in flags:
                thinking_level = 'ultrathink'
            elif '--think-hard' in flags:
                thinking_level = 'think_hard'
            elif '--think' in flags:
                thinking_level = 'think'
            
            thinking_success[thinking_level]['total'] += 1
            if success:
                thinking_success[thinking_level]['success'] += 1
        
        preferences = {}
        for level, stats in thinking_success.items():
            if stats['total'] >= 2:
                success_rate = stats['success'] / stats['total']
                preferences[level] = success_rate
        
        return preferences
    
    def _analyze_mcp_server_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """MCP 서버 선호도 분석"""
        server_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        server_indicators = {
            'Sequential': ['--seq', '--sequential'],
            'Context7': ['--c7', '--context7'],
            'Magic': ['--magic'],
            'Playwright': ['--play', '--playwright']
        }
        
        for interaction in interactions:
            flags = interaction.get('recommended_flags', '')
            success = interaction.get('success', False)
            
            for server, indicators in server_indicators.items():
                if any(indicator in flags for indicator in indicators):
                    server_success[server]['total'] += 1
                    if success:
                        server_success[server]['success'] += 1
        
        preferences = {}
        for server, stats in server_success.items():
            if stats['total'] >= 2:
                success_rate = stats['success'] / stats['total']
                preferences[server] = success_rate
        
        return preferences
    
    def _analyze_project_type_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """프로젝트 타입 선호도 분석"""
        type_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for interaction in interactions:
            try:
                context = interaction.get('project_context', '{}')
                if isinstance(context, str):
                    context = json.loads(context)
                
                project_type = context.get('project_type', 'unknown')
                success = interaction.get('success', False)
                
                type_success[project_type]['total'] += 1
                if success:
                    type_success[project_type]['success'] += 1
            except:
                continue
        
        preferences = {}
        for ptype, stats in type_success.items():
            if stats['total'] >= 2:
                success_rate = stats['success'] / stats['total']
                preferences[ptype] = success_rate
        
        return preferences
    
    def _analyze_complexity_preferences(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """복잡도 선호도 분석"""
        complexity_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for interaction in interactions:
            try:
                context = interaction.get('project_context', '{}')
                if isinstance(context, str):
                    context = json.loads(context)
                
                complexity = context.get('complexity', 'moderate')
                success = interaction.get('success', False)
                
                complexity_success[complexity]['total'] += 1
                if success:
                    complexity_success[complexity]['success'] += 1
            except:
                continue
        
        preferences = {}
        for complexity, stats in complexity_success.items():
            if stats['total'] >= 2:
                success_rate = stats['success'] / stats['total']
                preferences[complexity] = success_rate
        
        return preferences
    
    def _analyze_success_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """성공 패턴 분석"""
        patterns = {}
        
        # 시간대별 성공률
        hourly_success = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                hour = timestamp.hour
                success = interaction.get('success', False)
                
                hourly_success[hour]['total'] += 1
                if success:
                    hourly_success[hour]['success'] += 1
            except:
                continue
        
        # 성공률이 높은 시간대 저장
        for hour, stats in hourly_success.items():
            if stats['total'] >= 2:
                success_rate = stats['success'] / stats['total']
                if success_rate > 0.7:  # 70% 이상 성공한 시간대
                    patterns[f'peak_hour_{hour}'] = success_rate
        
        return patterns
    
    def _parse_user_input(self, user_input: str) -> Tuple[str, str]:
        """사용자 입력 파싱"""
        if user_input.startswith('/sc:'):
            import re
            match = re.match(r'/sc:(\w+)\s*(.*)', user_input.strip())
            if match:
                return match.group(1), match.group(2)
        return 'unknown', user_input
    
    def _generate_recommendation_id(self, user_input: str, project_context: Dict[str, Any]) -> str:
        """추천 ID 생성"""
        import hashlib
        content = f"{user_input}_{project_context.get('project_hash', '')}_{datetime.now().timestamp()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _is_compatible_persona(self, persona: str, current_personas: List[str]) -> bool:
        """Persona 호환성 확인"""
        # 호환되지 않는 persona 조합
        incompatible_pairs = [
            ('frontend', 'backend'),
            ('security', 'performance')  # 일부 경우에만
        ]
        
        for existing in current_personas:
            for pair in incompatible_pairs:
                if (persona in pair and existing in pair and 
                    persona != existing):
                    return False
        
        return True
    
    def _update_personal_preferences(self, recommendation_id: str, success: bool,
                                   execution_time: float, user_rating: Optional[int]):
        """개인 선호도 업데이트"""
        # 현재는 learning_engine에서 처리하지만
        # 추후 더 정교한 개인화 업데이트 로직 추가 가능
        pass
    
    def _invalidate_profile_cache(self):
        """프로필 캐시 무효화"""
        self._user_profile_cache = None
        self._profile_cache_time = 0
    
    def _calculate_personalized_success_rate(self, interactions: List[Dict[str, Any]]) -> float:
        """개인화된 성공률 계산"""
        if not interactions:
            return 0.0
        
        # 신뢰도가 높은 추천들의 성공률
        high_confidence_interactions = [
            i for i in interactions if i.get('confidence', 0) >= 80
        ]
        
        if not high_confidence_interactions:
            return sum(1 for i in interactions if i.get('success', False)) / len(interactions)
        
        return sum(1 for i in high_confidence_interactions if i.get('success', False)) / len(high_confidence_interactions)
    
    def _calculate_baseline_success_rate(self, interactions: List[Dict[str, Any]]) -> float:
        """기준선 성공률 계산"""
        if not interactions:
            return 0.0
        
        # 전체 상호작용의 단순 성공률
        return sum(1 for i in interactions if i.get('success', False)) / len(interactions)
    
    def _calculate_preference_diversity(self, user_profile: UserProfile) -> float:
        """선호도 다양성 계산"""
        all_preferences = []
        all_preferences.extend(user_profile.preferred_personas.values())
        all_preferences.extend(user_profile.preferred_thinking_levels.values())
        all_preferences.extend(user_profile.preferred_mcp_servers.values())
        
        if not all_preferences:
            return 0.0
        
        # 표준편차로 다양성 측정
        import statistics
        return statistics.stdev(all_preferences) if len(all_preferences) > 1 else 0.0
    
    def _calculate_preference_stability(self) -> float:
        """선호도 안정성 계산"""
        # 최근 30일과 이전 30일의 선호도 비교
        recent_interactions = self.storage.get_user_interactions(days=30)
        older_interactions = self.storage.get_user_interactions(days=60)
        older_interactions = older_interactions[len(recent_interactions):]
        
        if len(recent_interactions) < 5 or len(older_interactions) < 5:
            return 0.5  # 데이터 부족
        
        recent_personas = self._analyze_persona_preferences(recent_interactions)
        older_personas = self._analyze_persona_preferences(older_interactions)
        
        # 공통 persona들의 선호도 변화 측정
        common_personas = set(recent_personas.keys()) & set(older_personas.keys())
        
        if not common_personas:
            return 0.3  # 불안정
        
        changes = []
        for persona in common_personas:
            change = abs(recent_personas[persona] - older_personas[persona])
            changes.append(change)
        
        avg_change = sum(changes) / len(changes)
        stability = max(0, 1 - avg_change)  # 변화가 적을수록 안정성 높음
        
        return stability
    
    def _get_top_preferences(self, preferences: Dict[str, float], top_n: int = 3) -> List[Dict[str, Any]]:
        """상위 선호도 항목 반환"""
        sorted_prefs = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'item': item, 'preference_score': score}
            for item, score in sorted_prefs[:top_n]
        ]
    
    def _calculate_personalization_confidence(self, user_profile: UserProfile) -> float:
        """개인화 신뢰도 계산"""
        factors = []
        
        # 상호작용 수
        interaction_factor = min(user_profile.total_interactions / 50, 1.0)
        factors.append(interaction_factor * 0.4)
        
        # 선호도 데이터의 풍부함
        preference_richness = (
            len(user_profile.preferred_personas) * 0.1 +
            len(user_profile.preferred_thinking_levels) * 0.1 +
            len(user_profile.preferred_mcp_servers) * 0.1 +
            len(user_profile.project_type_preferences) * 0.1
        )
        factors.append(min(preference_richness, 0.3))
        
        # 선호도 강도 (확실한 선호도가 있는지)
        strong_preferences = 0
        for prefs in [user_profile.preferred_personas, user_profile.preferred_thinking_levels]:
            strong_preferences += sum(1 for score in prefs.values() if score > 0.8 or score < 0.2)
        
        strength_factor = min(strong_preferences / 10, 0.3)
        factors.append(strength_factor)
        
        return sum(factors)

# 전역 개인화 추천기 인스턴스
_personalized_recommender_instance = None

def get_personalized_recommender() -> PersonalizedAdaptiveRecommender:
    """전역 개인화 추천기 인스턴스 가져오기"""
    global _personalized_recommender_instance
    if _personalized_recommender_instance is None:
        _personalized_recommender_instance = PersonalizedAdaptiveRecommender()
    return _personalized_recommender_instance