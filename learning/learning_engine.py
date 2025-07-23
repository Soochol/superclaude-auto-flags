#!/usr/bin/env python3
"""
SuperClaude Adaptive Learning Engine
적응형 학습 엔진 - 사용자 행동 기반 플래그 추천 학습
"""

import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter

from learning_storage import LearningStorage, get_learning_storage
from data_collector import LearningDataCollector, get_data_collector

@dataclass
class LearningPattern:
    """학습된 패턴"""
    pattern_id: str
    base_flags: str
    success_rate: float
    usage_count: int
    confidence_score: float
    context_weights: Dict[str, float]
    last_updated: str
    user_preference_score: float

@dataclass
class RecommendationScore:
    """추천 점수"""
    pattern_id: str
    flags: str
    score: float
    confidence: int
    reasoning: List[str]
    learning_factors: Dict[str, float]

class AdaptiveLearningEngine:
    """적응형 학습 엔진"""
    
    def __init__(self, storage: Optional[LearningStorage] = None):
        self.storage = storage or get_learning_storage()
        self.learning_rate = 0.1
        self.decay_factor = 0.95
        self.min_samples_for_learning = 3
        self.confidence_threshold = 0.7
        
        # 학습된 패턴 캐시
        self._pattern_cache: Dict[str, LearningPattern] = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5분
    
    def learn_from_interactions(self, days: int = 30) -> Dict[str, Any]:
        """사용자 상호작용에서 학습"""
        interactions = self.storage.get_user_interactions(days=days)
        
        learning_stats = {
            'total_interactions': len(interactions),
            'successful_interactions': 0,
            'patterns_updated': 0,
            'new_patterns_discovered': 0
        }
        
        # 패턴별 상호작용 그룹화
        pattern_interactions = defaultdict(list)
        
        for interaction in interactions:
            pattern_name = self._identify_interaction_pattern(interaction)
            pattern_interactions[pattern_name].append(interaction)
            
            if interaction['success']:
                learning_stats['successful_interactions'] += 1
        
        # 각 패턴에 대해 학습 수행
        for pattern_name, pattern_data in pattern_interactions.items():
            if len(pattern_data) >= self.min_samples_for_learning:
                self._update_pattern_learning(pattern_name, pattern_data)
                learning_stats['patterns_updated'] += 1
        
        # 새로운 패턴 발견
        new_patterns = self._discover_new_patterns(interactions)
        learning_stats['new_patterns_discovered'] = len(new_patterns)
        
        return learning_stats
    
    def get_adaptive_recommendation(self, command: str, description: str, 
                                  project_context: Dict[str, Any]) -> RecommendationScore:
        """적응형 추천 생성"""
        
        # 캐시된 패턴 로드
        self._load_patterns_cache()
        
        # 컨텍스트 기반 후보 패턴들 찾기
        candidate_patterns = self._find_candidate_patterns(command, description, project_context)
        
        # 각 패턴에 대해 점수 계산
        scored_recommendations = []
        
        for pattern in candidate_patterns:
            score = self._calculate_adaptive_score(pattern, command, description, project_context)
            scored_recommendations.append(score)
        
        # 최고 점수 패턴 선택
        if scored_recommendations:
            best_recommendation = max(scored_recommendations, key=lambda x: x.score)
            
            # 컨텍스트 기반 플래그 조정
            adjusted_flags = self._adjust_flags_for_context(
                best_recommendation.flags, 
                project_context
            )
            
            best_recommendation.flags = adjusted_flags
            return best_recommendation
        else:
            # 폴백: 기본 추천
            return self._get_fallback_recommendation(command, description)
    
    def update_learning_from_feedback(self, interaction_id: str, success: bool, 
                                    execution_time: float, user_rating: Optional[int] = None):
        """피드백 기반 학습 업데이트"""
        
        # 해당 상호작용 조회
        interactions = self.storage.get_user_interactions(days=7)
        target_interaction = None
        
        for interaction in interactions:
            if str(interaction['id']) == interaction_id:
                target_interaction = interaction
                break
        
        if not target_interaction:
            return
        
        # 패턴 식별
        pattern_name = self._identify_interaction_pattern(target_interaction)
        
        # 학습 가중치 계산
        learning_weight = self._calculate_learning_weight(
            success, execution_time, user_rating
        )
        
        # 패턴 업데이트
        self._update_pattern_weights(pattern_name, learning_weight, target_interaction)
        
        # 사용자 선호도 업데이트
        project_hash = target_interaction['project_hash']
        current_preference = self.storage.get_user_preferences(project_hash).get(pattern_name, 1.0)
        
        # 성공/실패에 따른 선호도 조정
        preference_adjustment = learning_weight * self.learning_rate
        new_preference = max(0.1, min(2.0, current_preference + preference_adjustment))
        
        self.storage.update_user_preference(pattern_name, new_preference, project_hash)
    
    def analyze_learning_progress(self) -> Dict[str, Any]:
        """학습 진행 상황 분석"""
        
        # 패턴 성공률 조회
        pattern_success_rates = self.storage.get_pattern_success_rates()
        
        # 사용자 선호도 조회
        user_preferences = self.storage.get_user_preferences()
        
        # 최근 상호작용 분석
        recent_interactions = self.storage.get_user_interactions(days=7)
        
        analysis = {
            'total_patterns_learned': len(pattern_success_rates),
            'avg_success_rate': np.mean([p.success_rate for p in pattern_success_rates.values()]) if pattern_success_rates else 0,
            'most_successful_patterns': self._get_top_patterns(pattern_success_rates, 'success_rate'),
            'most_used_patterns': self._get_top_patterns(pattern_success_rates, 'total_uses'),
            'user_preference_diversity': len(user_preferences),
            'learning_trend': self._calculate_learning_trend(recent_interactions),
            'recommendation_accuracy': self._calculate_recommendation_accuracy(recent_interactions)
        }
        
        return analysis
    
    def _identify_interaction_pattern(self, interaction: Dict[str, Any]) -> str:
        """상호작용에서 패턴 식별"""
        command = interaction['command']
        description = interaction.get('description', '')
        
        # 기본 패턴 매칭 로직
        text = f"{command} {description}".lower()
        
        # 우선순위 패턴 확인
        priority_patterns = {
            'analyze_security': ['security', '보안', 'vulnerability', '취약점', 'audit'],
            'analyze_performance': ['performance', '성능', 'optimize', '최적화', 'bottleneck'],
            'analyze_architecture': ['architecture', '아키텍처', 'system design', 'structure'],
            'implement_ui': ['component', '컴포넌트', 'ui', 'interface', 'frontend'],
            'implement_api': ['api', 'endpoint', 'backend', '백엔드', 'server'],
            'implement_auth': ['auth', '인증', 'login', 'user', 'permission'],
            'improve_quality': ['improve', '개선', 'refactor', '리팩토링', 'cleanup'],
            'improve_performance': ['improve', '개선', 'performance', '성능', 'optimize'],
        }
        
        for pattern_name, keywords in priority_patterns.items():
            if any(keyword in text for keyword in keywords):
                return pattern_name
        
        # 기본 패턴
        return f"{command}_general"
    
    def _update_pattern_learning(self, pattern_name: str, interactions: List[Dict[str, Any]]):
        """패턴 학습 업데이트"""
        
        # 성공/실패 분석
        successful_interactions = [i for i in interactions if i['success']]
        success_rate = len(successful_interactions) / len(interactions)
        
        # 플래그 사용 빈도 분석
        flag_usage = Counter()
        for interaction in successful_interactions:
            flags = interaction['recommended_flags'].split()
            for flag in flags:
                flag_usage[flag] += 1
        
        # 컨텍스트 가중치 계산
        context_weights = self._calculate_context_weights(interactions)
        
        # 학습된 패턴 생성/업데이트
        if pattern_name in self._pattern_cache:
            existing_pattern = self._pattern_cache[pattern_name]
            
            # 지수 이동 평균으로 업데이트
            new_success_rate = (existing_pattern.success_rate * self.decay_factor + 
                              success_rate * (1 - self.decay_factor))
            
            updated_pattern = LearningPattern(
                pattern_id=pattern_name,
                base_flags=self._determine_optimal_flags(flag_usage),
                success_rate=new_success_rate,
                usage_count=existing_pattern.usage_count + len(interactions),
                confidence_score=self._calculate_confidence_score(len(interactions), new_success_rate),
                context_weights=context_weights,
                last_updated=datetime.now().isoformat(),
                user_preference_score=existing_pattern.user_preference_score
            )
        else:
            updated_pattern = LearningPattern(
                pattern_id=pattern_name,
                base_flags=self._determine_optimal_flags(flag_usage),
                success_rate=success_rate,
                usage_count=len(interactions),
                confidence_score=self._calculate_confidence_score(len(interactions), success_rate),
                context_weights=context_weights,
                last_updated=datetime.now().isoformat(),
                user_preference_score=1.0
            )
        
        self._pattern_cache[pattern_name] = updated_pattern
    
    def _discover_new_patterns(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """새로운 패턴 발견"""
        new_patterns = []
        
        # 명령어-설명 조합 분석
        command_desc_pairs = []
        for interaction in interactions:
            command = interaction['command']
            description = interaction.get('description', '')
            command_desc_pairs.append((command, description))
        
        # 빈번한 조합 찾기
        pair_counts = Counter(command_desc_pairs)
        
        for (command, description), count in pair_counts.items():
            if count >= self.min_samples_for_learning:
                # 새로운 패턴 후보
                pattern_candidate = f"{command}_{self._extract_key_terms(description)}"
                
                if pattern_candidate not in self._pattern_cache:
                    new_patterns.append(pattern_candidate)
        
        return new_patterns
    
    def _load_patterns_cache(self):
        """패턴 캐시 로드"""
        current_time = datetime.now().timestamp()
        
        if current_time - self._cache_timestamp > self._cache_ttl:
            # 캐시 갱신
            self._pattern_cache.clear()
            
            # 데이터베이스에서 패턴 로드
            pattern_success_rates = self.storage.get_pattern_success_rates()
            user_preferences = self.storage.get_user_preferences()
            
            for pattern_name, pattern_data in pattern_success_rates.items():
                user_pref = user_preferences.get(pattern_name, 1.0)
                
                learned_pattern = LearningPattern(
                    pattern_id=pattern_name,
                    base_flags=self._get_pattern_base_flags(pattern_name),
                    success_rate=pattern_data.success_rate,
                    usage_count=pattern_data.total_uses,
                    confidence_score=self._calculate_confidence_score(
                        pattern_data.total_uses, pattern_data.success_rate
                    ),
                    context_weights=pattern_data.context_conditions,
                    last_updated=pattern_data.last_updated,
                    user_preference_score=user_pref
                )
                
                self._pattern_cache[pattern_name] = learned_pattern
            
            self._cache_timestamp = current_time
    
    def _find_candidate_patterns(self, command: str, description: str, 
                               project_context: Dict[str, Any]) -> List[LearningPattern]:
        """후보 패턴들 찾기"""
        candidates = []
        
        # 명령어 기반 필터링
        for pattern_name, pattern in self._pattern_cache.items():
            if command in pattern_name or pattern_name.endswith('_general'):
                candidates.append(pattern)
        
        # 컨텍스트 유사성 기반 추가 후보
        for pattern_name, pattern in self._pattern_cache.items():
            context_similarity = self._calculate_context_similarity(
                pattern.context_weights, project_context
            )
            
            if context_similarity > 0.5:  # 임계값 이상의 유사성
                candidates.append(pattern)
        
        # 중복 제거
        unique_candidates = {p.pattern_id: p for p in candidates}
        return list(unique_candidates.values())
    
    def _calculate_adaptive_score(self, pattern: LearningPattern, command: str, 
                                description: str, project_context: Dict[str, Any]) -> RecommendationScore:
        """적응형 점수 계산"""
        
        reasoning = []
        learning_factors = {}
        
        # 1. 기본 성공률 점수 (0-40점)
        success_score = pattern.success_rate * 40
        learning_factors['success_rate'] = pattern.success_rate
        reasoning.append(f"성공률: {pattern.success_rate:.2f}")
        
        # 2. 사용자 선호도 점수 (0-20점)
        preference_score = min(pattern.user_preference_score, 2.0) * 10
        learning_factors['user_preference'] = pattern.user_preference_score
        reasoning.append(f"사용자 선호도: {pattern.user_preference_score:.2f}")
        
        # 3. 컨텍스트 유사성 점수 (0-20점)
        context_similarity = self._calculate_context_similarity(
            pattern.context_weights, project_context
        )
        context_score = context_similarity * 20
        learning_factors['context_similarity'] = context_similarity
        reasoning.append(f"컨텍스트 유사성: {context_similarity:.2f}")
        
        # 4. 신뢰도 점수 (0-10점)
        confidence_score = pattern.confidence_score * 10
        learning_factors['confidence'] = pattern.confidence_score
        reasoning.append(f"신뢰도: {pattern.confidence_score:.2f}")
        
        # 5. 최신성 점수 (0-10점)
        recency_score = self._calculate_recency_score(pattern.last_updated) * 10
        learning_factors['recency'] = recency_score / 10
        reasoning.append(f"최신성: {recency_score/10:.2f}")
        
        # 총점 계산
        total_score = success_score + preference_score + context_score + confidence_score + recency_score
        
        # 신뢰도 백분율 계산
        confidence_percentage = min(95, int(total_score))
        
        return RecommendationScore(
            pattern_id=pattern.pattern_id,
            flags=pattern.base_flags,
            score=total_score,
            confidence=confidence_percentage,
            reasoning=reasoning,
            learning_factors=learning_factors
        )
    
    def _adjust_flags_for_context(self, base_flags: str, project_context: Dict[str, Any]) -> str:
        """컨텍스트 기반 플래그 조정"""
        flags = base_flags
        
        # 프로젝트 크기에 따른 조정
        project_size = project_context.get('project_size', 'small')
        file_count = project_context.get('file_count', 0)
        
        if project_size in ['large', 'very_large'] or file_count > 50:
            if '--delegate' not in flags:
                flags += ' --delegate'
        
        if project_size == 'very_large' or file_count > 100:
            if '--uc' not in flags:
                flags += ' --uc'
        
        # 언어별 조정
        languages = project_context.get('languages', [])
        if 'python' in languages and '--validate' not in flags:
            flags += ' --validate'
        
        # 프레임워크별 조정
        frameworks = project_context.get('frameworks', [])
        if any(fw in frameworks for fw in ['react', 'vue', 'angular']) and '--magic' not in flags:
            flags += ' --magic'
        
        return flags.strip()
    
    def _get_fallback_recommendation(self, command: str, description: str) -> RecommendationScore:
        """폴백 추천"""
        base_flags = '--think --uc'
        confidence = 60
        
        if command == 'analyze':
            base_flags = '--persona-analyzer --think --uc'
            confidence = 70
        elif command == 'implement':
            base_flags = '--persona-backend --c7 --uc'
            confidence = 65
        elif command == 'improve':
            base_flags = '--persona-refactorer --think --uc'
            confidence = 68
        
        return RecommendationScore(
            pattern_id=f"{command}_fallback",
            flags=base_flags,
            score=confidence,
            confidence=confidence,
            reasoning=['폴백 추천 (학습 데이터 부족)'],
            learning_factors={'fallback': True}
        )
    
    def _calculate_context_weights(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """컨텍스트 가중치 계산"""
        weights = defaultdict(float)
        
        for interaction in interactions:
            try:
                context = interaction.get('project_context', '{}')
                if isinstance(context, str):
                    import json
                    context = json.loads(context)
                
                # 프로젝트 특성별 가중치
                project_size = context.get('project_size', 'unknown')
                languages = context.get('languages', [])
                frameworks = context.get('frameworks', [])
                
                weights[f'size_{project_size}'] += 1
                for lang in languages:
                    weights[f'lang_{lang}'] += 1
                for fw in frameworks:
                    weights[f'framework_{fw}'] += 1
                    
            except:
                continue
        
        # 정규화
        total = sum(weights.values())
        if total > 0:
            for key in weights:
                weights[key] /= total
        
        return dict(weights)
    
    def _determine_optimal_flags(self, flag_usage: Counter) -> str:
        """최적 플래그 조합 결정"""
        if not flag_usage:
            return '--think --uc'
        
        # 사용 빈도 기반 플래그 선택
        total_usage = sum(flag_usage.values())
        selected_flags = []
        
        for flag, count in flag_usage.most_common():
            usage_rate = count / total_usage
            if usage_rate > 0.3:  # 30% 이상 사용된 플래그
                selected_flags.append(flag)
        
        return ' '.join(selected_flags) if selected_flags else '--think --uc'
    
    def _calculate_confidence_score(self, usage_count: int, success_rate: float) -> float:
        """신뢰도 점수 계산"""
        # 사용 횟수가 많을수록, 성공률이 높을수록 신뢰도 증가
        usage_factor = min(usage_count / 20, 1.0)  # 20회 사용시 최대
        confidence = success_rate * usage_factor
        return min(confidence, 1.0)
    
    def _extract_key_terms(self, description: str) -> str:
        """설명에서 핵심 용어 추출"""
        key_terms = ['security', 'performance', 'ui', 'api', 'database', 'auth', 'test']
        description_lower = description.lower()
        
        found_terms = [term for term in key_terms if term in description_lower]
        return '_'.join(found_terms[:2]) if found_terms else 'general'
    
    def _calculate_context_similarity(self, pattern_context: Dict[str, float], 
                                    current_context: Dict[str, Any]) -> float:
        """컨텍스트 유사성 계산"""
        if not pattern_context:
            return 0.5  # 중립적
        
        similarity_score = 0.0
        total_weight = 0.0
        
        # 프로젝트 크기 비교
        current_size = current_context.get('project_size', 'unknown')
        size_key = f'size_{current_size}'
        if size_key in pattern_context:
            similarity_score += pattern_context[size_key] * 0.3
            total_weight += 0.3
        
        # 언어 비교
        current_languages = current_context.get('languages', [])
        for lang in current_languages:
            lang_key = f'lang_{lang}'
            if lang_key in pattern_context:
                similarity_score += pattern_context[lang_key] * 0.4
                total_weight += 0.4
        
        # 프레임워크 비교
        current_frameworks = current_context.get('frameworks', [])
        for fw in current_frameworks:
            fw_key = f'framework_{fw}'
            if fw_key in pattern_context:
                similarity_score += pattern_context[fw_key] * 0.3
                total_weight += 0.3
        
        return similarity_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_recency_score(self, last_updated: str) -> float:
        """최신성 점수 계산"""
        try:
            updated_time = datetime.fromisoformat(last_updated)
            now = datetime.now()
            days_diff = (now - updated_time).days
            
            # 30일 이내는 1.0, 그 이후는 지수적 감소
            if days_diff <= 30:
                return 1.0
            else:
                return math.exp(-days_diff / 60)  # 60일 반감기
        except:
            return 0.5
    
    def _get_pattern_base_flags(self, pattern_name: str) -> str:
        """패턴 기본 플래그 반환"""
        default_flags = {
            'analyze_security': '--persona-security --focus security --think --validate',
            'analyze_performance': '--persona-performance --think-hard --focus performance',
            'analyze_architecture': '--persona-architect --ultrathink --seq',
            'implement_ui': '--persona-frontend --magic --c7',
            'implement_api': '--persona-backend --seq --c7',
            'implement_auth': '--persona-security --persona-backend --validate',
            'improve_quality': '--persona-refactorer --loop --validate',
            'improve_performance': '--persona-performance --think-hard --play'
        }
        
        return default_flags.get(pattern_name, '--think --uc')
    
    def _calculate_learning_weight(self, success: bool, execution_time: float, 
                                 user_rating: Optional[int]) -> float:
        """학습 가중치 계산"""
        weight = 0.0
        
        # 성공/실패 기본 가중치
        if success:
            weight += 0.5
        else:
            weight -= 0.3
        
        # 실행 시간 기반 조정
        if execution_time < 30:
            weight += 0.2  # 빠른 실행
        elif execution_time > 120:
            weight -= 0.1  # 느린 실행
        
        # 사용자 평점 기반 조정
        if user_rating is not None:
            if user_rating >= 4:
                weight += 0.3
            elif user_rating <= 2:
                weight -= 0.2
        
        return max(-1.0, min(1.0, weight))  # -1.0 ~ 1.0 범위로 제한
    
    def _update_pattern_weights(self, pattern_name: str, learning_weight: float, 
                              interaction: Dict[str, Any]):
        """패턴 가중치 업데이트"""
        if pattern_name in self._pattern_cache:
            pattern = self._pattern_cache[pattern_name]
            
            # 성공률 업데이트
            adjustment = learning_weight * self.learning_rate
            new_success_rate = max(0.0, min(1.0, pattern.success_rate + adjustment))
            
            pattern.success_rate = new_success_rate
            pattern.last_updated = datetime.now().isoformat()
            
            # 데이터베이스에도 반영
            try:
                context = interaction.get('project_context', '{}')
                if isinstance(context, str):
                    import json
                    context = json.loads(context)
                
                self.storage.update_pattern_success(
                    pattern_name, 
                    learning_weight > 0, 
                    context
                )
            except:
                pass
    
    def _get_top_patterns(self, pattern_data: Dict, metric: str, top_n: int = 5) -> List[Dict]:
        """상위 패턴 조회"""
        sorted_patterns = sorted(
            pattern_data.items(),
            key=lambda x: getattr(x[1], metric),
            reverse=True
        )
        
        return [
            {
                'pattern_name': pattern_name,
                'metric_value': getattr(pattern_data, metric),
                'total_uses': pattern_data.total_uses
            }
            for pattern_name, pattern_data in sorted_patterns[:top_n]
        ]
    
    def _calculate_learning_trend(self, interactions: List[Dict[str, Any]]) -> str:
        """학습 트렌드 계산"""
        if len(interactions) < 5:
            return 'insufficient_data'
        
        # 최근 5개와 이전 5개 비교
        recent_success_rate = sum(1 for i in interactions[:5] if i['success']) / 5
        older_success_rate = sum(1 for i in interactions[5:10] if i['success']) / min(5, len(interactions[5:10]))
        
        if recent_success_rate > older_success_rate + 0.1:
            return 'improving'
        elif recent_success_rate < older_success_rate - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_recommendation_accuracy(self, interactions: List[Dict[str, Any]]) -> float:
        """추천 정확도 계산"""
        if not interactions:
            return 0.0
        
        accurate_recommendations = 0
        
        for interaction in interactions:
            # 추천된 플래그와 실제 성공 여부 비교
            confidence = interaction.get('confidence', 0)
            success = interaction.get('success', False)
            
            # 높은 신뢰도(80% 이상) 추천이 성공했거나
            # 낮은 신뢰도(60% 이하) 추천이 실패한 경우 정확한 것으로 간주
            if (confidence >= 80 and success) or (confidence <= 60 and not success):
                accurate_recommendations += 1
        
        return accurate_recommendations / len(interactions)

# 전역 학습 엔진 인스턴스
_learning_engine_instance = None

def get_learning_engine() -> AdaptiveLearningEngine:
    """전역 학습 엔진 인스턴스 가져오기"""
    global _learning_engine_instance
    if _learning_engine_instance is None:
        _learning_engine_instance = AdaptiveLearningEngine()
    return _learning_engine_instance