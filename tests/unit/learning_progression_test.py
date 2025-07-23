#!/usr/bin/env python3
"""
SuperClaude Learning Progression Simulation and Test Suite
학습 시스템의 실제 학습 능력과 시간 경과에 따른 개선 효과 검증

This comprehensive test simulates 20-30 user interactions over time to verify:
1. Pattern Recognition Learning
2. User Preference Adaptation
3. Context Awareness Improvement
4. Confidence Calibration Enhancement
5. Feedback Processing Effectiveness
"""

import os
import sys
import json
import random
import sqlite3
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from learning_engine import AdaptiveLearningEngine, RecommendationScore
from learning_storage import LearningStorage, UserInteraction, FeedbackRecord

@dataclass
class SimulationScenario:
    """시뮬레이션 시나리오"""
    name: str
    command: str
    description: str
    project_context: Dict[str, Any]
    expected_pattern: str
    success_probability: float
    execution_time_range: Tuple[float, float]
    user_rating_bias: float  # -1.0 to 1.0

@dataclass
class LearningMetrics:
    """학습 측정 지표"""
    timestamp: str
    interaction_count: int
    avg_confidence: float
    recommendation_accuracy: float
    pattern_diversity: int
    user_preference_strength: float
    context_adaptation_score: float

class LearningProgressionSimulator:
    """학습 진행 시뮬레이터"""
    
    def __init__(self, temp_dir: str = None):
        # 임시 디렉토리에서 테스트
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="superclaude_learning_test_")
        print(f"🔧 테스트 환경 설정: {self.temp_dir}")
        
        # 테스트용 학습 시스템 생성
        self.storage = LearningStorage(self.temp_dir)
        self.engine = AdaptiveLearningEngine(self.storage)
        
        # 시뮬레이션 시나리오 정의
        self.scenarios = self._create_simulation_scenarios()
        
        # 사용자 프로필 시뮬레이션
        self.user_profile = {
            'security_focus': 0.8,  # 보안에 관심 많음
            'performance_conscious': 0.6,  # 성능에 관심 보통
            'frontend_preference': 0.3,  # 프론트엔드 작업 적음
            'backend_preference': 0.9,  # 백엔드 작업 많음
            'quality_focused': 0.7,  # 품질에 관심 많음
        }
        
        # 프로젝트 컨텍스트 시뮬레이션
        self.project_contexts = self._create_project_contexts()
        
        # 학습 진행 메트릭
        self.learning_metrics: List[LearningMetrics] = []
        
        # 초기 상태 기록
        self._record_initial_metrics()
    
    def _create_simulation_scenarios(self) -> List[SimulationScenario]:
        """시뮬레이션 시나리오 생성"""
        return [
            # 보안 분석 시나리오
            SimulationScenario(
                name="security_vulnerability_analysis",
                command="analyze",
                description="Find security vulnerabilities in authentication system",
                project_context={"languages": ["python"], "frameworks": ["django"], "project_size": "large"},
                expected_pattern="analyze_security",
                success_probability=0.85,
                execution_time_range=(45, 90),
                user_rating_bias=0.3
            ),
            SimulationScenario(
                name="api_security_audit",
                command="analyze",
                description="Security audit for REST API endpoints",
                project_context={"languages": ["javascript"], "frameworks": ["express"], "project_size": "medium"},
                expected_pattern="analyze_security",
                success_probability=0.80,
                execution_time_range=(30, 60),
                user_rating_bias=0.2
            ),
            
            # 성능 최적화 시나리오
            SimulationScenario(
                name="database_performance_optimization",
                command="improve",
                description="Optimize database query performance",
                project_context={"languages": ["python"], "frameworks": ["sqlalchemy"], "project_size": "large"},
                expected_pattern="improve_performance",
                success_probability=0.75,
                execution_time_range=(60, 120),
                user_rating_bias=0.1
            ),
            SimulationScenario(
                name="frontend_performance_tuning",
                command="improve",
                description="Improve React component rendering performance",
                project_context={"languages": ["javascript"], "frameworks": ["react"], "project_size": "medium"},
                expected_pattern="improve_performance",
                success_probability=0.70,
                execution_time_range=(40, 80),
                user_rating_bias=-0.1
            ),
            
            # UI 구현 시나리오
            SimulationScenario(
                name="react_component_implementation",
                command="implement",
                description="Create responsive dashboard component",
                project_context={"languages": ["javascript"], "frameworks": ["react"], "project_size": "medium"},
                expected_pattern="implement_ui",
                success_probability=0.90,
                execution_time_range=(25, 50),
                user_rating_bias=0.0
            ),
            SimulationScenario(
                name="vue_form_component",
                command="implement",
                description="Build complex form component with validation",
                project_context={"languages": ["javascript"], "frameworks": ["vue"], "project_size": "small"},
                expected_pattern="implement_ui",
                success_probability=0.85,
                execution_time_range=(30, 60),
                user_rating_bias=0.1
            ),
            
            # API 구현 시나리오
            SimulationScenario(
                name="rest_api_implementation",
                command="implement",
                description="Implement user authentication API endpoints",
                project_context={"languages": ["python"], "frameworks": ["fastapi"], "project_size": "medium"},
                expected_pattern="implement_api",
                success_probability=0.85,
                execution_time_range=(50, 100),
                user_rating_bias=0.2
            ),
            SimulationScenario(
                name="graphql_api_implementation",
                command="implement",
                description="Create GraphQL resolvers for user management",
                project_context={"languages": ["javascript"], "frameworks": ["apollo"], "project_size": "large"},
                expected_pattern="implement_api",
                success_probability=0.80,
                execution_time_range=(60, 120),
                user_rating_bias=0.1
            ),
            
            # 아키텍처 분석 시나리오
            SimulationScenario(
                name="microservices_architecture_review",
                command="analyze",
                description="Review microservices architecture design",
                project_context={"languages": ["python", "javascript"], "frameworks": ["docker", "kubernetes"], "project_size": "very_large"},
                expected_pattern="analyze_architecture",
                success_probability=0.75,
                execution_time_range=(90, 180),
                user_rating_bias=0.3
            ),
            
            # 코드 품질 개선 시나리오
            SimulationScenario(
                name="code_quality_improvement",
                command="improve",
                description="Refactor legacy code for better maintainability",
                project_context={"languages": ["python"], "frameworks": [], "project_size": "large"},
                expected_pattern="improve_quality",
                success_probability=0.80,
                execution_time_range=(70, 140),
                user_rating_bias=0.2
            ),
        ]
    
    def _create_project_contexts(self) -> List[Dict[str, Any]]:
        """프로젝트 컨텍스트 생성"""
        return [
            {
                "name": "enterprise_auth_system",
                "languages": ["python"],
                "frameworks": ["django", "celery"],
                "project_size": "very_large",
                "file_count": 150,
                "security_sensitive": True
            },
            {
                "name": "ecommerce_frontend",
                "languages": ["javascript", "typescript"],
                "frameworks": ["react", "nextjs"],
                "project_size": "large",
                "file_count": 80,
                "performance_critical": True
            },
            {
                "name": "api_gateway",
                "languages": ["python"],
                "frameworks": ["fastapi", "redis"],
                "project_size": "medium",
                "file_count": 45,
                "high_availability": True
            },
            {
                "name": "mobile_app_backend",
                "languages": ["javascript"],
                "frameworks": ["express", "mongodb"],
                "project_size": "medium",
                "file_count": 35,
                "mobile_optimized": True
            },
            {
                "name": "data_pipeline",
                "languages": ["python"],
                "frameworks": ["airflow", "pandas"],
                "project_size": "large",
                "file_count": 65,
                "data_intensive": True
            }
        ]
    
    def _record_initial_metrics(self):
        """초기 메트릭 기록"""
        metrics = LearningMetrics(
            timestamp=datetime.now().isoformat(),
            interaction_count=0,
            avg_confidence=0.0,
            recommendation_accuracy=0.0,
            pattern_diversity=0,
            user_preference_strength=0.0,
            context_adaptation_score=0.0
        )
        self.learning_metrics.append(metrics)
    
    def simulate_user_interactions(self, num_interactions: int = 25) -> List[Dict[str, Any]]:
        """사용자 상호작용 시뮬레이션"""
        print(f"\n🎯 {num_interactions}개 사용자 상호작용 시뮬레이션 시작")
        
        interactions = []
        
        for i in range(num_interactions):
            # 시나리오 선택 (사용자 프로필 기반 가중 선택)
            scenario = self._select_scenario_by_user_preference()
            project_context = random.choice(self.project_contexts)
            
            # 시간 경과 시뮬레이션 (1-7일 간격)
            if i > 0:
                time_gap = random.uniform(1, 7)  # 1-7일
                time.sleep(0.1)  # 실제 시간 간격 시뮬레이션
            
            print(f"  📋 상호작용 {i+1}/{num_interactions}: {scenario.name}")
            
            # 추천 생성
            recommendation = self.engine.get_adaptive_recommendation(
                scenario.command,
                scenario.description,
                project_context
            )
            
            # 성공/실패 시뮬레이션
            success = random.random() < scenario.success_probability
            execution_time = random.uniform(*scenario.execution_time_range)
            
            # 사용자 평점 시뮬레이션
            base_rating = 4 if success else 2
            rating_adjustment = scenario.user_rating_bias * random.uniform(-1, 1)
            user_rating = max(1, min(5, int(base_rating + rating_adjustment)))
            
            # 상호작용 기록
            interaction = UserInteraction(
                timestamp=datetime.now().isoformat(),
                user_input=f"/sc:{scenario.command} {scenario.description}",
                command=scenario.command,
                description=scenario.description,
                recommended_flags=recommendation.flags,
                actual_flags=recommendation.flags,  # 시뮬레이션에서는 동일
                project_context=project_context,
                success=success,
                execution_time=execution_time,
                confidence=recommendation.confidence,
                reasoning=json.dumps(recommendation.reasoning),
                user_id=self.storage.user_id,
                project_hash=self.storage.get_project_hash(project_context['name'])
            )
            
            # 데이터베이스에 기록
            interaction_id = self.storage.record_interaction(interaction)
            
            # 피드백 기록
            feedback = FeedbackRecord(
                timestamp=datetime.now().isoformat(),
                interaction_id=interaction_id,
                feedback_type="implicit",
                rating=user_rating,
                success_indicator=success,
                user_correction=None,
                user_id=self.storage.user_id,
                project_hash=self.storage.get_project_hash(project_context['name'])
            )
            
            self.storage.record_feedback(feedback)
            
            # 학습 엔진에 피드백 적용
            self.engine.update_learning_from_feedback(
                interaction_id, success, execution_time, user_rating
            )
            
            # 주기적으로 학습 수행 및 메트릭 기록
            if (i + 1) % 5 == 0:
                print(f"    🧠 학습 진행 중... ({i+1}개 상호작용 완료)")
                self.engine.learn_from_interactions(days=30)
                self._record_learning_metrics(i + 1)
            
            interactions.append({
                'scenario': scenario.name,
                'recommendation': asdict(recommendation),
                'success': success,
                'execution_time': execution_time,
                'user_rating': user_rating,
                'interaction_id': interaction_id
            })
        
        # 최종 학습 수행
        print("  🎓 최종 학습 수행 중...")
        final_learning_stats = self.engine.learn_from_interactions(days=30)
        self._record_learning_metrics(num_interactions)
        
        print(f"✅ 시뮬레이션 완료: {num_interactions}개 상호작용, 학습 통계: {final_learning_stats}")
        return interactions
    
    def _select_scenario_by_user_preference(self) -> SimulationScenario:
        """사용자 선호도 기반 시나리오 선택"""
        weights = []
        
        for scenario in self.scenarios:
            weight = 1.0  # 기본 가중치
            
            # 사용자 프로필 기반 가중치 조정
            if 'security' in scenario.name:
                weight *= (1 + self.user_profile['security_focus'])
            elif 'performance' in scenario.name:
                weight *= (1 + self.user_profile['performance_conscious'])
            elif 'ui' in scenario.name or 'component' in scenario.name:
                weight *= (1 + self.user_profile['frontend_preference'])
            elif 'api' in scenario.name:
                weight *= (1 + self.user_profile['backend_preference'])
            elif 'quality' in scenario.name:
                weight *= (1 + self.user_profile['quality_focused'])
            
            weights.append(weight)
        
        # 가중 랜덤 선택
        total_weight = sum(weights)
        normalized_weights = [w/total_weight for w in weights]
        
        return np.random.choice(self.scenarios, p=normalized_weights)
    
    def _record_learning_metrics(self, interaction_count: int):
        """학습 메트릭 기록"""
        # 최근 상호작용 분석
        recent_interactions = self.storage.get_user_interactions(days=30)
        
        if not recent_interactions:
            return
        
        # 평균 신뢰도 계산
        avg_confidence = np.mean([i['confidence'] for i in recent_interactions])
        
        # 추천 정확도 계산 (높은 신뢰도 추천이 성공했는지)
        high_confidence_interactions = [i for i in recent_interactions if i['confidence'] >= 80]
        if high_confidence_interactions:
            accurate_predictions = sum(1 for i in high_confidence_interactions if i['success'])
            recommendation_accuracy = accurate_predictions / len(high_confidence_interactions)
        else:
            recommendation_accuracy = 0.0
        
        # 패턴 다양성 (학습된 패턴 수)
        pattern_success_rates = self.storage.get_pattern_success_rates()
        pattern_diversity = len(pattern_success_rates)
        
        # 사용자 선호도 강도 (선호도 편차 평균)
        user_preferences = self.storage.get_user_preferences()
        if user_preferences:
            preference_values = list(user_preferences.values())
            user_preference_strength = np.std(preference_values)  # 편차가 클수록 선호도가 뚜렷함
        else:
            user_preference_strength = 0.0
        
        # 컨텍스트 적응 점수 (컨텍스트별 성공률 차이)
        context_adaptation_score = self._calculate_context_adaptation_score(recent_interactions)
        
        metrics = LearningMetrics(
            timestamp=datetime.now().isoformat(),
            interaction_count=interaction_count,
            avg_confidence=avg_confidence,
            recommendation_accuracy=recommendation_accuracy,
            pattern_diversity=pattern_diversity,
            user_preference_strength=user_preference_strength,
            context_adaptation_score=context_adaptation_score
        )
        
        self.learning_metrics.append(metrics)
    
    def _calculate_context_adaptation_score(self, interactions: List[Dict]) -> float:
        """컨텍스트 적응 점수 계산"""
        if len(interactions) < 10:
            return 0.0
        
        # 프로젝트별 성공률 계산
        project_success_rates = {}
        for interaction in interactions:
            project_hash = interaction['project_hash']
            if project_hash not in project_success_rates:
                project_success_rates[project_hash] = []
            project_success_rates[project_hash].append(interaction['success'])
        
        # 각 프로젝트의 성공률 계산
        success_rates = []
        for project_hash, successes in project_success_rates.items():
            if len(successes) >= 3:  # 최소 3개 샘플
                success_rate = sum(successes) / len(successes)
                success_rates.append(success_rate)
        
        if len(success_rates) < 2:
            return 0.0
        
        # 성공률 분산 계산 (낮을수록 일관성 있음 = 좋은 적응)
        variance = np.var(success_rates)
        adaptation_score = max(0.0, 1.0 - variance * 2)  # 0-1 범위로 정규화
        
        return adaptation_score
    
    def test_learning_mechanisms(self) -> Dict[str, Any]:
        """학습 메커니즘 테스트"""
        print("\n🔬 학습 메커니즘 테스트 시작")
        
        results = {}
        
        # 1. 패턴 인식 테스트
        print("  📊 패턴 인식 능력 테스트")
        pattern_recognition_score = self._test_pattern_recognition()
        results['pattern_recognition'] = pattern_recognition_score
        
        # 2. 사용자 선호도 적응 테스트
        print("  👤 사용자 선호도 적응 테스트")
        user_adaptation_score = self._test_user_preference_adaptation()
        results['user_preference_adaptation'] = user_adaptation_score
        
        # 3. 컨텍스트 인식 테스트
        print("  🎯 컨텍스트 인식 능력 테스트")
        context_awareness_score = self._test_context_awareness()
        results['context_awareness'] = context_awareness_score
        
        # 4. 신뢰도 보정 테스트
        print("  📈 신뢰도 보정 능력 테스트")
        confidence_calibration_score = self._test_confidence_calibration()
        results['confidence_calibration'] = confidence_calibration_score
        
        # 5. 피드백 처리 테스트
        print("  🔄 피드백 처리 효과 테스트")
        feedback_effectiveness_score = self._test_feedback_processing()
        results['feedback_processing'] = feedback_effectiveness_score
        
        return results
    
    def _test_pattern_recognition(self) -> float:
        """패턴 인식 능력 테스트"""
        # 알려진 패턴에 대한 추천 정확도 측정
        test_cases = [
            ("analyze", "security vulnerability scan", "analyze_security"),
            ("implement", "React dashboard component", "implement_ui"),
            ("improve", "database query performance", "improve_performance"),
            ("analyze", "system architecture review", "analyze_architecture"),
        ]
        
        correct_predictions = 0
        
        for command, description, expected_pattern in test_cases:
            project_context = random.choice(self.project_contexts)
            recommendation = self.engine.get_adaptive_recommendation(command, description, project_context)
            
            # 추천된 플래그가 예상 패턴과 일치하는지 확인
            expected_flags = self.engine._get_pattern_base_flags(expected_pattern)
            
            # 주요 플래그가 포함되어 있는지 확인
            expected_flag_list = expected_flags.split()
            recommended_flag_list = recommendation.flags.split()
            
            # 핵심 플래그 매칭 확인
            core_match = any(flag in recommended_flag_list for flag in expected_flag_list[:2])
            
            if core_match:
                correct_predictions += 1
        
        return correct_predictions / len(test_cases)
    
    def _test_user_preference_adaptation(self) -> float:
        """사용자 선호도 적응 테스트"""
        # 사용자 선호도 조회
        user_preferences = self.storage.get_user_preferences()
        
        if not user_preferences:
            return 0.0
        
        # 선호도 분산 측정 (높을수록 개인화가 잘 됨)
        preference_values = list(user_preferences.values())
        preference_variance = np.var(preference_values)
        
        # 0-1 범위로 정규화
        adaptation_score = min(1.0, preference_variance)
        
        return adaptation_score
    
    def _test_context_awareness(self) -> float:
        """컨텍스트 인식 능력 테스트"""
        # 동일한 명령어, 다른 컨텍스트에 대한 추천 차이 측정
        test_command = "implement"
        test_description = "user authentication system"
        
        contexts = [
            {"languages": ["python"], "frameworks": ["django"], "project_size": "large"},
            {"languages": ["javascript"], "frameworks": ["react"], "project_size": "small"},
            {"languages": ["python"], "frameworks": ["fastapi"], "project_size": "medium"}
        ]
        
        recommendations = []
        for context in contexts:
            rec = self.engine.get_adaptive_recommendation(test_command, test_description, context)
            recommendations.append(rec.flags)
        
        # 추천의 다양성 측정 (다른 컨텍스트에 다른 추천)
        unique_recommendations = len(set(recommendations))
        context_awareness_score = unique_recommendations / len(contexts)
        
        return context_awareness_score
    
    def _test_confidence_calibration(self) -> float:
        """신뢰도 보정 능력 테스트"""
        # 최근 상호작용에서 신뢰도와 실제 성공률의 상관관계 측정
        recent_interactions = self.storage.get_user_interactions(days=30)
        
        if len(recent_interactions) < 10:
            return 0.0
        
        # 신뢰도 구간별 실제 성공률 계산
        high_confidence = [i for i in recent_interactions if i['confidence'] >= 80]
        medium_confidence = [i for i in recent_interactions if 60 <= i['confidence'] < 80]
        low_confidence = [i for i in recent_interactions if i['confidence'] < 60]
        
        confidence_accuracy = 0.0
        weight_sum = 0.0
        
        # 고신뢰도 구간 (80% 이상 성공해야 함)
        if high_confidence:
            high_success_rate = sum(i['success'] for i in high_confidence) / len(high_confidence)
            if high_success_rate >= 0.75:  # 기대값보다 높으면 점수
                confidence_accuracy += high_success_rate * 0.5
            weight_sum += 0.5
        
        # 중간신뢰도 구간 (60-70% 성공)
        if medium_confidence:
            medium_success_rate = sum(i['success'] for i in medium_confidence) / len(medium_confidence)
            if 0.55 <= medium_success_rate <= 0.75:  # 적절한 범위
                confidence_accuracy += 0.65 * 0.3
            weight_sum += 0.3
        
        # 저신뢰도 구간 (50% 이하 성공)
        if low_confidence:
            low_success_rate = sum(i['success'] for i in low_confidence) / len(low_confidence)
            if low_success_rate <= 0.6:  # 예상대로 낮은 성공률
                confidence_accuracy += (1 - low_success_rate) * 0.2
            weight_sum += 0.2
        
        return confidence_accuracy / weight_sum if weight_sum > 0 else 0.0
    
    def _test_feedback_processing(self) -> float:
        """피드백 처리 효과 테스트"""
        # 시간 경과에 따른 성공률 개선 측정
        all_interactions = self.storage.get_user_interactions(days=30)
        
        if len(all_interactions) < 20:
            return 0.0
        
        # 시간순 정렬
        sorted_interactions = sorted(all_interactions, key=lambda x: x['timestamp'])
        
        # 초기 절반과 후반 절반의 성공률 비교
        half_point = len(sorted_interactions) // 2
        
        early_interactions = sorted_interactions[:half_point]
        late_interactions = sorted_interactions[half_point:]
        
        early_success_rate = sum(i['success'] for i in early_interactions) / len(early_interactions)
        late_success_rate = sum(i['success'] for i in late_interactions) / len(late_interactions)
        
        # 개선 정도 측정 (0-1 범위로 정규화)
        improvement = late_success_rate - early_success_rate
        improvement_score = max(0.0, min(1.0, improvement + 0.5))  # -0.5 ~ 0.5 -> 0 ~ 1
        
        return improvement_score
    
    def measure_learning_effectiveness(self) -> Dict[str, Any]:
        """학습 효과 측정"""
        print("\n📊 학습 효과 측정 중...")
        
        if len(self.learning_metrics) < 2:
            return {"error": "충분한 메트릭 데이터 없음"}
        
        initial_metrics = self.learning_metrics[0]
        final_metrics = self.learning_metrics[-1]
        
        # 개선 지표 계산
        improvements = {
            'confidence_improvement': final_metrics.avg_confidence - initial_metrics.avg_confidence,
            'accuracy_improvement': final_metrics.recommendation_accuracy - initial_metrics.recommendation_accuracy,
            'pattern_diversity_growth': final_metrics.pattern_diversity - initial_metrics.pattern_diversity,
            'preference_strength_growth': final_metrics.user_preference_strength - initial_metrics.user_preference_strength,
            'context_adaptation_improvement': final_metrics.context_adaptation_score - initial_metrics.context_adaptation_score
        }
        
        # 전체 학습 효과 점수
        learning_effectiveness_score = np.mean([
            max(0, improvements['confidence_improvement'] / 20),  # 20점 개선 = 1.0점
            max(0, improvements['accuracy_improvement']),  # 직접 비율
            max(0, improvements['pattern_diversity_growth'] / 10),  # 10개 패턴 = 1.0점
            max(0, improvements['preference_strength_growth']),  # 직접 점수
            max(0, improvements['context_adaptation_improvement'])  # 직접 점수
        ])
        
        return {
            'initial_state': asdict(initial_metrics),
            'final_state': asdict(final_metrics),
            'improvements': improvements,
            'learning_effectiveness_score': learning_effectiveness_score,
            'metrics_timeline': [asdict(m) for m in self.learning_metrics]
        }
    
    def test_data_persistence(self) -> Dict[str, Any]:
        """데이터 지속성 테스트"""
        print("\n💾 데이터 지속성 테스트")
        
        # 현재 데이터 상태 기록
        before_state = {
            'interactions_count': len(self.storage.get_user_interactions(days=30)),
            'patterns_count': len(self.storage.get_pattern_success_rates()),
            'preferences_count': len(self.storage.get_user_preferences())
        }
        
        # 새로운 스토리지 인스턴스 생성 (재시작 시뮬레이션)
        new_storage = LearningStorage(self.temp_dir)
        new_engine = AdaptiveLearningEngine(new_storage)
        
        # 데이터 복구 확인
        after_state = {
            'interactions_count': len(new_storage.get_user_interactions(days=30)),
            'patterns_count': len(new_storage.get_pattern_success_rates()),
            'preferences_count': len(new_storage.get_user_preferences())
        }
        
        # 데이터 일관성 확인
        data_consistency = {
            'interactions_preserved': before_state['interactions_count'] == after_state['interactions_count'],
            'patterns_preserved': before_state['patterns_count'] == after_state['patterns_count'],
            'preferences_preserved': before_state['preferences_count'] == after_state['preferences_count']
        }
        
        # 학습 상태 복구 테스트
        test_recommendation = new_engine.get_adaptive_recommendation(
            "analyze", "security vulnerability assessment", 
            {"languages": ["python"], "project_size": "large"}
        )
        
        learning_state_recovered = test_recommendation.confidence > 60  # 기본값보다 높아야 함
        
        return {
            'before_restart': before_state,
            'after_restart': after_state,
            'data_consistency': data_consistency,
            'learning_state_recovered': learning_state_recovered,
            'persistence_score': sum(data_consistency.values()) / len(data_consistency)
        }
    
    def compare_cold_vs_warm_performance(self) -> Dict[str, Any]:
        """콜드 스타트 vs 웜 시스템 성능 비교"""
        print("\n🌡️ 콜드 스타트 vs 웜 시스템 성능 비교")
        
        # 웜 시스템 성능 (현재 학습된 상태)
        warm_test_cases = [
            ("analyze", "security audit for web application"),
            ("implement", "REST API for user management"),
            ("improve", "database query optimization"),
        ]
        
        warm_performance = []
        for command, description in warm_test_cases:
            context = random.choice(self.project_contexts)
            recommendation = self.engine.get_adaptive_recommendation(command, description, context)
            warm_performance.append({
                'confidence': recommendation.confidence,
                'flags_count': len(recommendation.flags.split()),
                'reasoning_depth': len(recommendation.reasoning)
            })
        
        # 콜드 시스템 성능 (새로운 임시 시스템)
        cold_temp_dir = tempfile.mkdtemp(prefix="superclaude_cold_test_")
        cold_storage = LearningStorage(cold_temp_dir)
        cold_engine = AdaptiveLearningEngine(cold_storage)
        
        cold_performance = []
        for command, description in warm_test_cases:
            context = random.choice(self.project_contexts)
            recommendation = cold_engine.get_adaptive_recommendation(command, description, context)
            cold_performance.append({
                'confidence': recommendation.confidence,
                'flags_count': len(recommendation.flags.split()),
                'reasoning_depth': len(recommendation.reasoning)
            })
        
        # 성능 차이 계산
        warm_avg_confidence = np.mean([p['confidence'] for p in warm_performance])
        cold_avg_confidence = np.mean([p['confidence'] for p in cold_performance])
        
        warm_avg_flags = np.mean([p['flags_count'] for p in warm_performance])
        cold_avg_flags = np.mean([p['flags_count'] for p in cold_performance])
        
        warm_avg_reasoning = np.mean([p['reasoning_depth'] for p in warm_performance])
        cold_avg_reasoning = np.mean([p['reasoning_depth'] for p in cold_performance])
        
        # 정리
        import shutil
        shutil.rmtree(cold_temp_dir, ignore_errors=True)
        
        return {
            'warm_system': {
                'avg_confidence': warm_avg_confidence,
                'avg_flags_count': warm_avg_flags,
                'avg_reasoning_depth': warm_avg_reasoning,
                'performance_samples': warm_performance
            },
            'cold_system': {
                'avg_confidence': cold_avg_confidence,
                'avg_flags_count': cold_avg_flags,
                'avg_reasoning_depth': cold_avg_reasoning,
                'performance_samples': cold_performance
            },
            'improvements': {
                'confidence_gain': warm_avg_confidence - cold_avg_confidence,
                'flags_sophistication_gain': warm_avg_flags - cold_avg_flags,
                'reasoning_depth_gain': warm_avg_reasoning - cold_avg_reasoning
            },
            'overall_improvement_score': (
                (warm_avg_confidence - cold_avg_confidence) / 100 +  # 신뢰도 개선
                max(0, (warm_avg_flags - cold_avg_flags) / 5) +  # 플래그 정교함
                max(0, (warm_avg_reasoning - cold_avg_reasoning) / 10)  # 추론 깊이
            ) / 3
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 테스트 보고서 생성"""
        print("\n📋 종합 테스트 보고서 생성 중...")
        
        # 모든 테스트 결과 수집
        learning_mechanisms = self.test_learning_mechanisms()
        learning_effectiveness = self.measure_learning_effectiveness()
        data_persistence = self.test_data_persistence()
        cold_vs_warm = self.compare_cold_vs_warm_performance()
        
        # 최종 학습 분석
        learning_analysis = self.engine.analyze_learning_progress()
        
        # 전체 점수 계산
        overall_scores = {
            'pattern_recognition': learning_mechanisms.get('pattern_recognition', 0),
            'user_adaptation': learning_mechanisms.get('user_preference_adaptation', 0),
            'context_awareness': learning_mechanisms.get('context_awareness', 0),
            'confidence_calibration': learning_mechanisms.get('confidence_calibration', 0),
            'feedback_processing': learning_mechanisms.get('feedback_processing', 0),
            'learning_effectiveness': learning_effectiveness.get('learning_effectiveness_score', 0),
            'data_persistence': data_persistence.get('persistence_score', 0),
            'warm_vs_cold_improvement': cold_vs_warm.get('overall_improvement_score', 0)
        }
        
        total_score = np.mean(list(overall_scores.values()))
        
        # 결론 도출
        conclusions = []
        if total_score >= 0.8:
            conclusions.append("✅ 학습 시스템이 매우 효과적으로 작동하고 있습니다.")
        elif total_score >= 0.6:
            conclusions.append("⚠️ 학습 시스템이 적절히 작동하나 개선 여지가 있습니다.")
        else:
            conclusions.append("❌ 학습 시스템에 심각한 문제가 있습니다.")
        
        if overall_scores['learning_effectiveness'] > 0.5:
            conclusions.append("📈 시간에 따른 성능 개선이 확인되었습니다.")
        
        if overall_scores['warm_vs_cold_improvement'] > 0.3:
            conclusions.append("🔥 웜 시스템이 콜드 시스템보다 현저히 우수한 성능을 보입니다.")
        
        if overall_scores['data_persistence'] >= 0.9:
            conclusions.append("💾 데이터 지속성이 확실히 보장됩니다.")
        
        return {
            'test_summary': {
                'total_interactions_simulated': self.learning_metrics[-1].interaction_count if self.learning_metrics else 0,
                'total_score': total_score,
                'test_passed': total_score >= 0.6,
                'conclusions': conclusions
            },
            'detailed_scores': overall_scores,
            'learning_mechanisms': learning_mechanisms,
            'learning_effectiveness': learning_effectiveness,
            'data_persistence': data_persistence,
            'cold_vs_warm_comparison': cold_vs_warm,
            'learning_analysis': learning_analysis,
            'test_environment': {
                'temp_directory': self.temp_dir,
                'user_profile': self.user_profile,
                'test_scenarios_count': len(self.scenarios)
            }
        }
    
    def cleanup(self):
        """테스트 환경 정리"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"🧹 테스트 환경 정리 완료: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ 정리 중 오류: {e}")

def run_comprehensive_learning_test():
    """종합 학습 테스트 실행"""
    print("🚀 SuperClaude 학습 시스템 종합 테스트 시작")
    print("=" * 80)
    
    simulator = None
    try:
        # 시뮬레이터 초기화
        simulator = LearningProgressionSimulator()
        
        # 사용자 상호작용 시뮬레이션 (25회)
        interactions = simulator.simulate_user_interactions(25)
        
        # 종합 보고서 생성
        report = simulator.generate_comprehensive_report()
        
        # 보고서 출력
        print("\n" + "=" * 80)
        print("📊 SuperClaude 학습 시스템 테스트 결과")
        print("=" * 80)
        
        summary = report['test_summary']
        print(f"\n🎯 테스트 요약:")
        print(f"   • 시뮬레이션된 상호작용: {summary['total_interactions_simulated']}회")
        print(f"   • 전체 점수: {summary['total_score']:.3f}/1.000")
        print(f"   • 테스트 통과: {'✅ PASS' if summary['test_passed'] else '❌ FAIL'}")
        
        print(f"\n📋 결론:")
        for conclusion in summary['conclusions']:
            print(f"   {conclusion}")
        
        print(f"\n📊 세부 점수:")
        scores = report['detailed_scores']
        for metric, score in scores.items():
            status = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
            print(f"   {status} {metric}: {score:.3f}")
        
        # 학습 효과 상세 분석
        if 'learning_effectiveness' in report:
            effectiveness = report['learning_effectiveness']
            print(f"\n📈 학습 효과 분석:")
            if 'improvements' in effectiveness:
                improvements = effectiveness['improvements']
                print(f"   • 신뢰도 개선: {improvements.get('confidence_improvement', 0):.2f}점")
                print(f"   • 정확도 개선: {improvements.get('accuracy_improvement', 0):.3f}")
                print(f"   • 패턴 다양성 증가: {improvements.get('pattern_diversity_growth', 0)}개")
                print(f"   • 사용자 선호도 강화: {improvements.get('preference_strength_growth', 0):.3f}")
        
        # 콜드 vs 웜 비교
        if 'cold_vs_warm_comparison' in report:
            comparison = report['cold_vs_warm_comparison']
            print(f"\n🌡️ 콜드 vs 웜 시스템 비교:")
            improvements = comparison.get('improvements', {})
            print(f"   • 신뢰도 향상: {improvements.get('confidence_gain', 0):.1f}점")
            print(f"   • 플래그 정교함 향상: {improvements.get('flags_sophistication_gain', 0):.1f}개")
            print(f"   • 추론 깊이 향상: {improvements.get('reasoning_depth_gain', 0):.1f}항목")
        
        # 데이터 지속성
        if 'data_persistence' in report:
            persistence = report['data_persistence']
            print(f"\n💾 데이터 지속성:")
            consistency = persistence.get('data_consistency', {})
            for key, value in consistency.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {'보존됨' if value else '손실됨'}")
        
        print("\n" + "=" * 80)
        
        # JSON 보고서 저장
        report_file = f"/tmp/superclaude_learning_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 상세 보고서 저장됨: {report_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if simulator:
            simulator.cleanup()

if __name__ == "__main__":
    run_comprehensive_learning_test()