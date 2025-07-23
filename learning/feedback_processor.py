#!/usr/bin/env python3
"""
SuperClaude Feedback Processing System
피드백 수집 및 처리 시스템
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from learning_storage import LearningStorage, FeedbackRecord, get_learning_storage
from adaptive_recommender import PersonalizedAdaptiveRecommender, get_personalized_recommender

class FeedbackType(Enum):
    IMPLICIT_SUCCESS = "implicit_success"
    IMPLICIT_FAILURE = "implicit_failure"
    EXPLICIT_RATING = "explicit_rating"
    USER_CORRECTION = "user_correction"
    PERFORMANCE_FEEDBACK = "performance_feedback"

@dataclass
class ProcessedFeedback:
    """처리된 피드백"""
    feedback_id: str
    feedback_type: FeedbackType
    learning_weight: float
    confidence_impact: float
    pattern_adjustments: Dict[str, float]
    personalization_updates: Dict[str, Any]
    processing_timestamp: str

@dataclass
class FeedbackAnalysis:
    """피드백 분석 결과"""
    total_feedback_count: int
    positive_feedback_ratio: float
    negative_feedback_ratio: float
    average_response_time: float
    improvement_trends: Dict[str, float]
    user_satisfaction_score: float
    recommendation_accuracy: float

class FeedbackProcessor:
    """피드백 처리 및 분석 시스템"""
    
    def __init__(self, storage: Optional[LearningStorage] = None,
                 recommender: Optional[PersonalizedAdaptiveRecommender] = None):
        self.storage = storage or get_learning_storage()
        self.recommender = recommender or get_personalized_recommender()
        
        # 피드백 처리 파라미터
        self.implicit_feedback_threshold = 2.0  # 초
        self.learning_rate = 0.1
        self.confidence_adjustment_factor = 0.05
        self.batch_processing_size = 50
        
        # 피드백 가중치
        self.feedback_weights = {
            FeedbackType.IMPLICIT_SUCCESS: 0.3,
            FeedbackType.IMPLICIT_FAILURE: 0.4,
            FeedbackType.EXPLICIT_RATING: 1.0,
            FeedbackType.USER_CORRECTION: 1.2,
            FeedbackType.PERFORMANCE_FEEDBACK: 0.6
        }
    
    def process_immediate_feedback(self, interaction_id: str, success: bool, 
                                 execution_time: float, error_details: Optional[str] = None) -> ProcessedFeedback:
        """즉시 피드백 처리"""
        
        # 피드백 타입 분류
        feedback_type = self._classify_implicit_feedback(success, execution_time, error_details)
        
        # 학습 가중치 계산
        learning_weight = self._calculate_learning_weight(feedback_type, success, execution_time)
        
        # 신뢰도 영향 계산
        confidence_impact = self._calculate_confidence_impact(feedback_type, success, execution_time)
        
        # 패턴 조정사항 결정
        pattern_adjustments = self._determine_pattern_adjustments(
            interaction_id, feedback_type, success, execution_time
        )
        
        # 개인화 업데이트 준비
        personalization_updates = self._prepare_personalization_updates(
            interaction_id, feedback_type, success
        )
        
        # 피드백 기록
        feedback_record = FeedbackRecord(
            timestamp=datetime.now().isoformat(),
            interaction_id=interaction_id,
            feedback_type=feedback_type.value,
            rating=self._success_to_rating(success, execution_time),
            success_indicator=success,
            user_correction=error_details,
            user_id=self.storage.user_id,
            project_hash=self.storage.get_project_hash(os.getcwd())
        )
        
        self.storage.record_feedback(feedback_record)
        
        # 실시간 업데이트 적용
        self._apply_immediate_updates(pattern_adjustments, personalization_updates)
        
        processed_feedback = ProcessedFeedback(
            feedback_id=f"{interaction_id}_{int(time.time())}",
            feedback_type=feedback_type,
            learning_weight=learning_weight,
            confidence_impact=confidence_impact,
            pattern_adjustments=pattern_adjustments,
            personalization_updates=personalization_updates,
            processing_timestamp=datetime.now().isoformat()
        )
        
        return processed_feedback
    
    def process_explicit_feedback(self, interaction_id: str, user_rating: int,
                                user_correction: Optional[str] = None) -> ProcessedFeedback:
        """명시적 피드백 처리"""
        
        feedback_type = FeedbackType.USER_CORRECTION if user_correction else FeedbackType.EXPLICIT_RATING
        
        # 명시적 피드백의 높은 학습 가중치
        learning_weight = self.feedback_weights[feedback_type] * (user_rating / 5.0)
        
        # 신뢰도 조정
        confidence_impact = self._calculate_explicit_confidence_impact(user_rating, user_correction)
        
        # 패턴 및 개인화 조정
        pattern_adjustments = self._process_explicit_pattern_adjustments(
            interaction_id, user_rating, user_correction
        )
        
        personalization_updates = self._process_explicit_personalization_updates(
            interaction_id, user_rating, user_correction
        )
        
        # 피드백 기록
        feedback_record = FeedbackRecord(
            timestamp=datetime.now().isoformat(),
            interaction_id=interaction_id,
            feedback_type=feedback_type.value,
            rating=user_rating,
            success_indicator=user_rating >= 3,
            user_correction=user_correction,
            user_id=self.storage.user_id,
            project_hash=self.storage.get_project_hash(os.getcwd())
        )
        
        self.storage.record_feedback(feedback_record)
        
        # 업데이트 적용
        self._apply_immediate_updates(pattern_adjustments, personalization_updates)
        
        return ProcessedFeedback(
            feedback_id=f"{interaction_id}_explicit_{int(time.time())}",
            feedback_type=feedback_type,
            learning_weight=learning_weight,
            confidence_impact=confidence_impact,
            pattern_adjustments=pattern_adjustments,
            personalization_updates=personalization_updates,
            processing_timestamp=datetime.now().isoformat()
        )
    
    def process_batch_feedback(self, days: int = 7) -> List[ProcessedFeedback]:
        """배치 피드백 처리"""
        
        # 최근 피드백 데이터 수집
        recent_interactions = self.storage.get_user_interactions(days=days)
        
        processed_feedbacks = []
        batch_updates = defaultdict(list)
        
        for interaction in recent_interactions:
            # 아직 처리되지 않은 피드백만 처리
            if not self._is_feedback_processed(str(interaction['id'])):
                
                # 배치 피드백 분석
                feedback_analysis = self._analyze_interaction_for_batch_processing(interaction)
                
                if feedback_analysis:
                    processed_feedback = self._create_batch_processed_feedback(
                        interaction, feedback_analysis
                    )
                    processed_feedbacks.append(processed_feedback)
                    
                    # 배치 업데이트 수집
                    for key, value in processed_feedback.pattern_adjustments.items():
                        batch_updates[key].append(value)
        
        # 배치 업데이트 적용
        self._apply_batch_updates(batch_updates)
        
        return processed_feedbacks
    
    def analyze_feedback_trends(self, days: int = 30) -> FeedbackAnalysis:
        """피드백 트렌드 분석"""
        
        interactions = self.storage.get_user_interactions(days=days)
        
        if not interactions:
            return self._create_empty_analysis()
        
        # 기본 통계
        total_count = len(interactions)
        successful_count = sum(1 for i in interactions if i.get('success', False))
        positive_ratio = successful_count / total_count
        
        # 응답 시간 분석
        execution_times = [i.get('execution_time', 0) for i in interactions if i.get('execution_time')]
        avg_response_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # 개선 트렌드 분석
        improvement_trends = self._calculate_improvement_trends(interactions)
        
        # 사용자 만족도 점수
        satisfaction_score = self._calculate_user_satisfaction(interactions)
        
        # 추천 정확도
        recommendation_accuracy = self._calculate_recommendation_accuracy(interactions)
        
        return FeedbackAnalysis(
            total_feedback_count=total_count,
            positive_feedback_ratio=positive_ratio,
            negative_feedback_ratio=1.0 - positive_ratio,
            average_response_time=avg_response_time,
            improvement_trends=improvement_trends,
            user_satisfaction_score=satisfaction_score,
            recommendation_accuracy=recommendation_accuracy
        )
    
    def generate_feedback_report(self, days: int = 30) -> Dict[str, Any]:
        """피드백 리포트 생성"""
        
        analysis = self.analyze_feedback_trends(days)
        interactions = self.storage.get_user_interactions(days=days)
        
        # 패턴별 성능 분석
        pattern_performance = self._analyze_pattern_performance(interactions)
        
        # 시간대별 성능 분석
        hourly_performance = self._analyze_hourly_performance(interactions)
        
        # 복잡도별 성능 분석  
        complexity_performance = self._analyze_complexity_performance(interactions)
        
        # 개선 권장사항
        recommendations = self._generate_improvement_recommendations(analysis, interactions)
        
        report = {
            'report_period': f"{days} days",
            'generated_at': datetime.now().isoformat(),
            'overall_analysis': asdict(analysis),
            'pattern_performance': pattern_performance,
            'hourly_performance': hourly_performance,
            'complexity_performance': complexity_performance,
            'improvement_recommendations': recommendations,
            'data_quality': self._assess_data_quality(interactions)
        }
        
        return report
    
    def _classify_implicit_feedback(self, success: bool, execution_time: float, 
                                  error_details: Optional[str]) -> FeedbackType:
        """암시적 피드백 분류"""
        
        if success:
            if execution_time < self.implicit_feedback_threshold:
                return FeedbackType.IMPLICIT_SUCCESS
            else:
                return FeedbackType.PERFORMANCE_FEEDBACK
        else:
            return FeedbackType.IMPLICIT_FAILURE
    
    def _calculate_learning_weight(self, feedback_type: FeedbackType, success: bool, 
                                 execution_time: float) -> float:
        """학습 가중치 계산"""
        
        base_weight = self.feedback_weights[feedback_type]
        
        # 성공/실패에 따른 조정
        success_multiplier = 1.0 if success else 0.7
        
        # 실행 시간에 따른 조정
        time_multiplier = 1.0
        if execution_time < 5:
            time_multiplier = 1.2  # 빠른 실행 보너스
        elif execution_time > 60:
            time_multiplier = 0.8  # 느린 실행 페널티
        
        return base_weight * success_multiplier * time_multiplier
    
    def _calculate_confidence_impact(self, feedback_type: FeedbackType, success: bool, 
                                   execution_time: float) -> float:
        """신뢰도 영향 계산"""
        
        base_impact = self.confidence_adjustment_factor
        
        if feedback_type == FeedbackType.IMPLICIT_SUCCESS:
            return base_impact * 0.5
        elif feedback_type == FeedbackType.IMPLICIT_FAILURE:
            return -base_impact * 0.8
        elif feedback_type == FeedbackType.PERFORMANCE_FEEDBACK:
            # 실행 시간 기반 조정
            if execution_time > 30:
                return -base_impact * 0.3
            else:
                return base_impact * 0.2
        
        return 0.0
    
    def _determine_pattern_adjustments(self, interaction_id: str, feedback_type: FeedbackType,
                                     success: bool, execution_time: float) -> Dict[str, float]:
        """패턴 조정사항 결정"""
        
        adjustments = {}
        
        # 상호작용 정보 조회
        interactions = self.storage.get_user_interactions(days=1)
        target_interaction = None
        
        for interaction in interactions:
            if str(interaction['id']) == interaction_id:
                target_interaction = interaction
                break
        
        if not target_interaction:
            return adjustments
        
        # 사용된 플래그 분석
        flags = target_interaction.get('recommended_flags', '').split()
        
        # 플래그별 조정
        for flag in flags:
            if flag.startswith('--persona-'):
                persona = flag.replace('--persona-', '')
                if success:
                    adjustments[f'persona_{persona}_boost'] = 0.1
                else:
                    adjustments[f'persona_{persona}_penalty'] = -0.05
            
            elif flag.startswith('--think'):
                thinking_level = flag.replace('--', '')
                if execution_time > 60:  # 너무 오래 걸림
                    adjustments[f'{thinking_level}_performance_penalty'] = -0.1
                elif success and execution_time < 30:
                    adjustments[f'{thinking_level}_performance_boost'] = 0.05
        
        return adjustments
    
    def _prepare_personalization_updates(self, interaction_id: str, feedback_type: FeedbackType,
                                       success: bool) -> Dict[str, Any]:
        """개인화 업데이트 준비"""
        
        updates = {
            'preference_adjustments': {},
            'confidence_updates': {},
            'pattern_reinforcements': {}
        }
        
        # 성공한 경우 선호도 강화
        if success:
            updates['preference_adjustments']['success_reinforcement'] = 0.1
        else:
            updates['preference_adjustments']['failure_adjustment'] = -0.05
        
        # 피드백 타입별 특별 처리
        if feedback_type == FeedbackType.IMPLICIT_SUCCESS:
            updates['confidence_updates']['implicit_success_boost'] = 0.02
        elif feedback_type == FeedbackType.IMPLICIT_FAILURE:
            updates['confidence_updates']['implicit_failure_penalty'] = -0.03
        
        return updates
    
    def _apply_immediate_updates(self, pattern_adjustments: Dict[str, float],
                               personalization_updates: Dict[str, Any]):
        """즉시 업데이트 적용"""
        
        # 패턴 조정 적용
        for adjustment_key, adjustment_value in pattern_adjustments.items():
            # 여기서는 로깅만 수행 (실제 적용은 learning_engine에서)
            print(f"Pattern adjustment: {adjustment_key} = {adjustment_value}")
        
        # 개인화 업데이트 적용
        for update_category, updates in personalization_updates.items():
            for update_key, update_value in updates.items():
                print(f"Personalization update: {update_category}.{update_key} = {update_value}")
    
    def _success_to_rating(self, success: bool, execution_time: float) -> int:
        """성공 여부를 평점으로 변환"""
        if not success:
            return 1
        
        # 실행 시간 기반 평점
        if execution_time < 10:
            return 5
        elif execution_time < 30:
            return 4
        elif execution_time < 60:
            return 3
        else:
            return 2
    
    def _calculate_explicit_confidence_impact(self, user_rating: int, 
                                            user_correction: Optional[str]) -> float:
        """명시적 피드백의 신뢰도 영향 계산"""
        
        # 평점 기반 조정
        rating_impact = (user_rating - 3) * 0.1  # 3점 기준으로 ±0.1
        
        # 사용자 수정사항이 있으면 추가 페널티
        correction_penalty = -0.15 if user_correction else 0.0
        
        return rating_impact + correction_penalty
    
    def _process_explicit_pattern_adjustments(self, interaction_id: str, user_rating: int,
                                            user_correction: Optional[str]) -> Dict[str, float]:
        """명시적 피드백의 패턴 조정 처리"""
        
        adjustments = {}
        
        # 평점 기반 조정
        if user_rating >= 4:
            adjustments['explicit_positive_reinforcement'] = 0.2
        elif user_rating <= 2:
            adjustments['explicit_negative_adjustment'] = -0.3
        
        # 사용자 수정사항 분석
        if user_correction:
            adjustments['user_correction_learning'] = 0.5
            
            # 수정사항에서 플래그 추출 시도
            if '--' in user_correction:
                adjustments['user_suggested_flags'] = 0.3
        
        return adjustments
    
    def _process_explicit_personalization_updates(self, interaction_id: str, user_rating: int,
                                                user_correction: Optional[str]) -> Dict[str, Any]:
        """명시적 피드백의 개인화 업데이트 처리"""
        
        updates = {
            'preference_adjustments': {},
            'confidence_updates': {},
            'learning_signals': {}
        }
        
        # 강한 선호도 신호
        if user_rating >= 4:
            updates['preference_adjustments']['strong_positive'] = 0.3
        elif user_rating <= 2:
            updates['preference_adjustments']['strong_negative'] = -0.2
        
        # 학습 신호
        updates['learning_signals']['explicit_feedback_weight'] = user_rating / 5.0
        
        return updates
    
    def _is_feedback_processed(self, interaction_id: str) -> bool:
        """피드백이 이미 처리되었는지 확인"""
        # 여기서는 간단히 False 반환 (실제로는 처리 이력 확인 필요)
        return False
    
    def _analyze_interaction_for_batch_processing(self, interaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """배치 처리를 위한 상호작용 분석"""
        
        success = interaction.get('success', False)
        execution_time = interaction.get('execution_time', 0)
        confidence = interaction.get('confidence', 0)
        
        # 분석할 가치가 있는지 판단
        if execution_time == 0:  # 데이터 없음
            return None
        
        analysis = {
            'performance_score': self._calculate_performance_score(success, execution_time),
            'confidence_accuracy': self._calculate_confidence_accuracy(success, confidence),
            'learning_value': self._calculate_learning_value(interaction)
        }
        
        return analysis
    
    def _create_batch_processed_feedback(self, interaction: Dict[str, Any], 
                                       analysis: Dict[str, Any]) -> ProcessedFeedback:
        """배치 처리된 피드백 생성"""
        
        feedback_type = FeedbackType.PERFORMANCE_FEEDBACK
        learning_weight = analysis['learning_value']
        confidence_impact = analysis['confidence_accuracy'] * 0.05
        
        pattern_adjustments = {
            'batch_performance_adjustment': analysis['performance_score'] * 0.1,
            'batch_confidence_adjustment': confidence_impact
        }
        
        personalization_updates = {
            'batch_learning': {'weight': learning_weight}
        }
        
        return ProcessedFeedback(
            feedback_id=f"batch_{interaction['id']}_{int(time.time())}",
            feedback_type=feedback_type,
            learning_weight=learning_weight,
            confidence_impact=confidence_impact,
            pattern_adjustments=pattern_adjustments,
            personalization_updates=personalization_updates,
            processing_timestamp=datetime.now().isoformat()
        )
    
    def _apply_batch_updates(self, batch_updates: Dict[str, List[float]]):
        """배치 업데이트 적용"""
        
        for update_key, values in batch_updates.items():
            if values:
                avg_adjustment = sum(values) / len(values)
                print(f"Batch update: {update_key} = {avg_adjustment:.3f} (from {len(values)} samples)")
    
    def _create_empty_analysis(self) -> FeedbackAnalysis:
        """빈 분석 결과 생성"""
        return FeedbackAnalysis(
            total_feedback_count=0,
            positive_feedback_ratio=0.0,
            negative_feedback_ratio=0.0,
            average_response_time=0.0,
            improvement_trends={},
            user_satisfaction_score=0.0,
            recommendation_accuracy=0.0
        )
    
    def _calculate_improvement_trends(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """개선 트렌드 계산"""
        
        if len(interactions) < 10:
            return {'insufficient_data': True}
        
        # 시간순 정렬
        sorted_interactions = sorted(interactions, key=lambda x: x['timestamp'])
        
        # 전반부와 후반부 비교
        mid_point = len(sorted_interactions) // 2
        first_half = sorted_interactions[:mid_point]
        second_half = sorted_interactions[mid_point:]
        
        first_success_rate = sum(1 for i in first_half if i.get('success', False)) / len(first_half)
        second_success_rate = sum(1 for i in second_half if i.get('success', False)) / len(second_half)
        
        success_improvement = second_success_rate - first_success_rate
        
        # 평균 신뢰도 트렌드
        first_confidence = sum(i.get('confidence', 0) for i in first_half) / len(first_half)
        second_confidence = sum(i.get('confidence', 0) for i in second_half) / len(second_half)
        
        confidence_improvement = second_confidence - first_confidence
        
        return {
            'success_rate_improvement': success_improvement,
            'confidence_improvement': confidence_improvement,
            'overall_trend': 'improving' if success_improvement > 0.05 else 'stable' if success_improvement > -0.05 else 'declining'
        }
    
    def _calculate_user_satisfaction(self, interactions: List[Dict[str, Any]]) -> float:
        """사용자 만족도 계산"""
        
        if not interactions:
            return 0.0
        
        # 성공률 기반 만족도
        success_rate = sum(1 for i in interactions if i.get('success', False)) / len(interactions)
        
        # 실행 시간 기반 만족도
        execution_times = [i.get('execution_time', 60) for i in interactions]
        avg_execution_time = sum(execution_times) / len(execution_times)
        time_satisfaction = max(0, min(1, (60 - avg_execution_time) / 60))
        
        # 신뢰도 정확성 기반 만족도
        accuracy_scores = []
        for interaction in interactions:
            confidence = interaction.get('confidence', 0)
            success = interaction.get('success', False)
            
            # 높은 신뢰도로 성공하거나 낮은 신뢰도로 실패한 경우 정확
            if (confidence >= 80 and success) or (confidence <= 60 and not success):
                accuracy_scores.append(1.0)
            else:
                accuracy_scores.append(0.0)
        
        accuracy_satisfaction = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.5
        
        # 종합 만족도 (가중 평균)
        overall_satisfaction = (
            success_rate * 0.5 +
            time_satisfaction * 0.3 +
            accuracy_satisfaction * 0.2
        )
        
        return min(1.0, max(0.0, overall_satisfaction))
    
    def _calculate_recommendation_accuracy(self, interactions: List[Dict[str, Any]]) -> float:
        """추천 정확도 계산"""
        
        if not interactions:
            return 0.0
        
        accurate_count = 0
        
        for interaction in interactions:
            confidence = interaction.get('confidence', 0)
            success = interaction.get('success', False)
            
            # 정확도 판정 기준
            if confidence >= 80:
                # 높은 신뢰도 → 성공해야 정확
                if success:
                    accurate_count += 1
            elif confidence <= 60:
                # 낮은 신뢰도 → 실패해도 정확 (신중한 추천)
                accurate_count += 1
            else:
                # 중간 신뢰도 → 성공하면 정확
                if success:
                    accurate_count += 1
        
        return accurate_count / len(interactions)
    
    def _calculate_performance_score(self, success: bool, execution_time: float) -> float:
        """성능 점수 계산"""
        success_score = 1.0 if success else 0.0
        
        # 실행 시간 점수 (30초 기준)
        time_score = max(0, min(1, (30 - execution_time) / 30)) if execution_time > 0 else 0.5
        
        return (success_score * 0.7) + (time_score * 0.3)
    
    def _calculate_confidence_accuracy(self, success: bool, confidence: int) -> float:
        """신뢰도 정확성 계산"""
        expected_success_prob = confidence / 100.0
        actual_success = 1.0 if success else 0.0
        
        # 예측과 실제 결과의 차이 (작을수록 정확)
        accuracy = 1.0 - abs(expected_success_prob - actual_success)
        return accuracy
    
    def _calculate_learning_value(self, interaction: Dict[str, Any]) -> float:
        """학습 가치 계산"""
        
        # 기본 학습 가치
        base_value = 0.5
        
        # 성공/실패에 따른 가치
        success = interaction.get('success', False)
        success_value = 0.3 if success else 0.4  # 실패가 더 많은 학습 가치
        
        # 실행 시간에 따른 가치
        execution_time = interaction.get('execution_time', 0)
        time_value = 0.2 if execution_time > 0 else 0.0
        
        # 신뢰도와 결과의 일치도에 따른 가치
        confidence = interaction.get('confidence', 0)
        confidence_accuracy = self._calculate_confidence_accuracy(success, confidence)
        accuracy_value = 0.3 * (1.0 - confidence_accuracy)  # 불일치할 때 더 많은 학습 가치
        
        return base_value + success_value + time_value + accuracy_value
    
    def _analyze_pattern_performance(self, interactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """패턴별 성능 분석"""
        
        pattern_stats = defaultdict(lambda: {'success_count': 0, 'total_count': 0, 'avg_time': 0, 'times': []})
        
        for interaction in interactions:
            # 패턴 추정 (명령어 기반)
            command = interaction.get('command', 'unknown')
            pattern_stats[command]['total_count'] += 1
            
            if interaction.get('success', False):
                pattern_stats[command]['success_count'] += 1
            
            execution_time = interaction.get('execution_time', 0)
            if execution_time > 0:
                pattern_stats[command]['times'].append(execution_time)
        
        # 통계 계산
        results = {}
        for pattern, stats in pattern_stats.items():
            if stats['total_count'] > 0:
                success_rate = stats['success_count'] / stats['total_count']
                avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
                
                results[pattern] = {
                    'success_rate': success_rate,
                    'average_execution_time': avg_time,
                    'total_uses': stats['total_count'],
                    'performance_score': self._calculate_pattern_performance_score(success_rate, avg_time)
                }
        
        return results
    
    def _analyze_hourly_performance(self, interactions: List[Dict[str, Any]]) -> Dict[int, Dict[str, float]]:
        """시간대별 성능 분석"""
        
        hourly_stats = defaultdict(lambda: {'success_count': 0, 'total_count': 0})
        
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                hour = timestamp.hour
                
                hourly_stats[hour]['total_count'] += 1
                if interaction.get('success', False):
                    hourly_stats[hour]['success_count'] += 1
            except:
                continue
        
        results = {}
        for hour, stats in hourly_stats.items():
            if stats['total_count'] > 0:
                success_rate = stats['success_count'] / stats['total_count']
                results[hour] = {
                    'success_rate': success_rate,
                    'total_interactions': stats['total_count']
                }
        
        return results
    
    def _analyze_complexity_performance(self, interactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """복잡도별 성능 분석"""
        
        complexity_stats = defaultdict(lambda: {'success_count': 0, 'total_count': 0})
        
        for interaction in interactions:
            try:
                context = interaction.get('project_context', '{}')
                if isinstance(context, str):
                    context = json.loads(context)
                
                complexity = context.get('complexity', 'unknown')
                
                complexity_stats[complexity]['total_count'] += 1
                if interaction.get('success', False):
                    complexity_stats[complexity]['success_count'] += 1
            except:
                continue
        
        results = {}
        for complexity, stats in complexity_stats.items():
            if stats['total_count'] > 0:
                success_rate = stats['success_count'] / stats['total_count']
                results[complexity] = {
                    'success_rate': success_rate,
                    'total_interactions': stats['total_count']
                }
        
        return results
    
    def _generate_improvement_recommendations(self, analysis: FeedbackAnalysis, 
                                            interactions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """개선 권장사항 생성"""
        
        recommendations = []
        
        # 성공률 기반 권장사항
        if analysis.positive_feedback_ratio < 0.7:
            recommendations.append({
                'type': 'success_rate_improvement',
                'priority': 'high',
                'recommendation': '성공률이 낮습니다. 더 보수적인 추천이나 추가 검증이 필요합니다.',
                'target_metric': 'success_rate',
                'current_value': f"{analysis.positive_feedback_ratio:.2f}",
                'target_value': '0.80+'
            })
        
        # 응답 시간 기반 권장사항
        if analysis.average_response_time > 60:
            recommendations.append({
                'type': 'performance_improvement',
                'priority': 'medium',
                'recommendation': '평균 응답 시간이 깁니다. 더 효율적인 플래그 조합을 고려하세요.',
                'target_metric': 'response_time',
                'current_value': f"{analysis.average_response_time:.1f}s",
                'target_value': '<30s'
            })
        
        # 추천 정확도 기반 권장사항
        if analysis.recommendation_accuracy < 0.8:
            recommendations.append({
                'type': 'accuracy_improvement',
                'priority': 'high',
                'recommendation': '추천 정확도를 높이기 위해 더 많은 학습 데이터가 필요합니다.',
                'target_metric': 'recommendation_accuracy',
                'current_value': f"{analysis.recommendation_accuracy:.2f}",
                'target_value': '0.85+'
            })
        
        # 데이터 품질 기반 권장사항
        if len(interactions) < 50:
            recommendations.append({
                'type': 'data_collection',
                'priority': 'medium',
                'recommendation': '더 나은 개인화를 위해 더 많은 상호작용 데이터가 필요합니다.',
                'target_metric': 'interaction_count',
                'current_value': str(len(interactions)),
                'target_value': '100+'
            })
        
        return recommendations
    
    def _assess_data_quality(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """데이터 품질 평가"""
        
        if not interactions:
            return {'quality_score': 0.0, 'issues': ['no_data']}
        
        issues = []
        quality_factors = []
        
        # 데이터 완성도 확인
        complete_interactions = 0
        for interaction in interactions:
            if all(key in interaction for key in ['success', 'execution_time', 'confidence', 'recommended_flags']):
                complete_interactions += 1
        
        completeness_ratio = complete_interactions / len(interactions)
        quality_factors.append(completeness_ratio)
        
        if completeness_ratio < 0.8:
            issues.append('incomplete_data')
        
        # 시간 분포 확인
        timestamps = []
        for interaction in interactions:
            try:
                timestamp = datetime.fromisoformat(interaction['timestamp'])
                timestamps.append(timestamp)
            except:
                continue
        
        if timestamps:
            time_span = (max(timestamps) - min(timestamps)).days
            time_diversity = min(1.0, time_span / 30)  # 30일 기준
            quality_factors.append(time_diversity)
            
            if time_span < 7:
                issues.append('limited_time_span')
        
        # 다양성 확인
        commands = set(interaction.get('command', 'unknown') for interaction in interactions)
        command_diversity = min(1.0, len(commands) / 5)  # 5가지 명령어 기준
        quality_factors.append(command_diversity)
        
        if len(commands) < 3:
            issues.append('limited_command_diversity')
        
        # 종합 품질 점수
        quality_score = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
        
        return {
            'quality_score': quality_score,
            'completeness_ratio': completeness_ratio,
            'time_diversity': time_diversity if 'time_diversity' in locals() else 0.0,
            'command_diversity': command_diversity,
            'issues': issues,
            'total_interactions': len(interactions)
        }
    
    def _calculate_pattern_performance_score(self, success_rate: float, avg_time: float) -> float:
        """패턴 성능 점수 계산"""
        
        # 성공률 점수 (0-0.7)
        success_score = success_rate * 0.7
        
        # 시간 점수 (0-0.3)
        time_score = max(0, min(0.3, (60 - avg_time) / 60 * 0.3)) if avg_time > 0 else 0.15
        
        return success_score + time_score

# 전역 피드백 프로세서 인스턴스
_feedback_processor_instance = None

def get_feedback_processor() -> FeedbackProcessor:
    """전역 피드백 프로세서 인스턴스 가져오기"""
    global _feedback_processor_instance
    if _feedback_processor_instance is None:
        _feedback_processor_instance = FeedbackProcessor()
    return _feedback_processor_instance