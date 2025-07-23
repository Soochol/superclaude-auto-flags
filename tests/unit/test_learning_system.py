#!/usr/bin/env python3
"""
SuperClaude Learning System Test Suite
학습 시스템 전체 테스트
"""

import sys
import json
import os
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime
import unittest

# 테스트를 위한 경로 추가
sys.path.insert(0, str(Path.cwd()))

class TestLearningSystem(unittest.TestCase):
    """학습 시스템 통합 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.environ['SUPERCLAUDE_TEST_MODE'] = '1'
        os.environ['SUPERCLAUDE_STORAGE_DIR'] = str(self.temp_dir)
    
    def tearDown(self):
        """테스트 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if 'SUPERCLAUDE_TEST_MODE' in os.environ:
            del os.environ['SUPERCLAUDE_TEST_MODE']
        if 'SUPERCLAUDE_STORAGE_DIR' in os.environ:
            del os.environ['SUPERCLAUDE_STORAGE_DIR']
    
    def test_learning_storage_basic(self):
        """학습 저장소 기본 기능 테스트"""
        from learning_storage import LearningStorage, UserInteraction
        
        storage = LearningStorage(str(self.temp_dir))
        
        # 상호작용 기록 테스트
        interaction = UserInteraction(
            timestamp=datetime.now().isoformat(),
            user_input="/sc:analyze test",
            command="analyze",
            description="test",
            recommended_flags="--persona-analyzer --think",
            actual_flags="--persona-analyzer --think",
            project_context={"project_type": "python_backend"},
            success=True,
            execution_time=15.5,
            confidence=85,
            reasoning="test pattern matching",
            user_id=storage.user_id,
            project_hash="test_hash"
        )
        
        interaction_id = storage.record_interaction(interaction)
        self.assertIsNotNone(interaction_id)
        
        # 상호작용 조회 테스트
        interactions = storage.get_user_interactions(days=1)
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0]['command'], 'analyze')
    
    def test_data_collector(self):
        """데이터 수집기 테스트"""
        from data_collector import LearningDataCollector
        from learning_storage import LearningStorage
        
        storage = LearningStorage(str(self.temp_dir))
        collector = LearningDataCollector(storage)
        
        # 프로젝트 컨텍스트 수집 테스트
        context = collector.collect_project_context(str(Path.cwd()))
        
        self.assertIn('project_hash', context)
        self.assertIn('file_count', context)
        self.assertIn('languages', context)
        
        # 상호작용 시작/종료 테스트
        interaction_id = collector.start_interaction(
            user_input="/sc:analyze test code",
            recommended_flags="--persona-analyzer --think",
            confidence=85,
            reasoning="pattern matching",
            project_context=context
        )
        
        self.assertIsNotNone(interaction_id)
        
        collector.end_interaction(
            actual_flags="--persona-analyzer --think",
            success=True,
            error_message=None
        )
    
    def test_learning_engine(self):
        """학습 엔진 테스트"""
        from learning_engine import AdaptiveLearningEngine
        from learning_storage import LearningStorage
        
        storage = LearningStorage(str(self.temp_dir))
        engine = AdaptiveLearningEngine(storage)
        
        # 기본 추천 테스트
        recommendation = engine.get_adaptive_recommendation(
            command="analyze",
            description="security issues",
            project_context={
                "project_type": "python_backend",
                "complexity": "moderate",
                "file_count": 25
            }
        )
        
        self.assertIsNotNone(recommendation.flags)
        self.assertGreater(recommendation.confidence, 0)
        self.assertIsInstance(recommendation.reasoning, list)
    
    def test_personalized_recommender(self):
        """개인화 추천기 테스트"""
        from adaptive_recommender import PersonalizedAdaptiveRecommender
        from learning_storage import LearningStorage
        
        storage = LearningStorage(str(self.temp_dir))
        recommender = PersonalizedAdaptiveRecommender(storage)
        
        # 개인화 추천 테스트
        recommendation = recommender.get_personalized_recommendation(
            user_input="/sc:analyze security vulnerabilities",
            project_context={
                "project_type": "python_backend",
                "complexity": "complex",
                "file_count": 150
            }
        )
        
        self.assertIsNotNone(recommendation.flags)
        self.assertGreater(recommendation.confidence, 0)
        self.assertIsInstance(recommendation.reasoning, list)
        self.assertIn('personalization_factors', recommendation.__dict__)
    
    def test_feedback_processor(self):
        """피드백 처리기 테스트"""
        from feedback_processor import FeedbackProcessor
        from learning_storage import LearningStorage
        
        storage = LearningStorage(str(self.temp_dir))
        processor = FeedbackProcessor(storage)
        
        # 즉시 피드백 처리 테스트
        processed_feedback = processor.process_immediate_feedback(
            interaction_id="test_interaction_1",
            success=True,
            execution_time=20.5,
            error_details=None
        )
        
        self.assertIsNotNone(processed_feedback.feedback_id)
        self.assertGreater(processed_feedback.learning_weight, 0)
        
        # 명시적 피드백 처리 테스트
        explicit_feedback = processor.process_explicit_feedback(
            interaction_id="test_interaction_2",
            user_rating=4,
            user_correction=None
        )
        
        self.assertIsNotNone(explicit_feedback.feedback_id)
        self.assertGreater(explicit_feedback.learning_weight, 0)
    
    def test_integration_workflow(self):
        """통합 워크플로우 테스트"""
        from claude_sc_preprocessor import SCCommandProcessor
        
        # 테스트 프로젝트 디렉토리 설정
        test_project = self.temp_dir / "test_project"
        test_project.mkdir()
        (test_project / "main.py").write_text("print('hello world')")
        (test_project / "requirements.txt").write_text("requests==2.28.0")
        
        os.chdir(test_project)
        
        try:
            processor = SCCommandProcessor()
            
            # /sc: 명령어 처리 테스트
            user_input = "/sc:analyze 이 코드의 보안 문제점을 찾아줘"
            result = processor.process(user_input)
            
            self.assertIsNotNone(result)
            self.assertIn("SuperClaude", result)
            self.assertIn("--persona-", result)
            
            # 실행 결과 기록 테스트
            processor.record_execution_result(
                success=True,
                execution_time=25.0,
                error_details=None
            )
            
        finally:
            os.chdir(Path.cwd().parent)
    
    def test_learning_progression(self):
        """학습 진행 상황 테스트"""
        from learning_storage import LearningStorage, UserInteraction
        from learning_engine import AdaptiveLearningEngine
        from datetime import datetime, timedelta
        
        storage = LearningStorage(str(self.temp_dir))
        engine = AdaptiveLearningEngine(storage)
        
        # 여러 상호작용 시뮬레이션
        for i in range(10):
            interaction = UserInteraction(
                timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
                user_input=f"/sc:analyze test {i}",
                command="analyze",
                description=f"test {i}",
                recommended_flags="--persona-analyzer --think",
                actual_flags="--persona-analyzer --think",
                project_context={"project_type": "python_backend"},
                success=i % 3 != 0,  # 2/3 성공률
                execution_time=10.0 + i,
                confidence=80 + i,
                reasoning="automated test",
                user_id=storage.user_id,
                project_hash="test_progression"
            )
            
            storage.record_interaction(interaction)
        
        # 학습 진행 상황 분석
        analysis = engine.analyze_learning_progress()
        
        self.assertIn('total_patterns_learned', analysis)
        self.assertIn('avg_success_rate', analysis)
        self.assertGreaterEqual(analysis['avg_success_rate'], 0.0)
        self.assertLessEqual(analysis['avg_success_rate'], 1.0)
    
    def test_database_integrity(self):
        """데이터베이스 무결성 테스트"""
        from learning_storage import LearningStorage
        
        storage = LearningStorage(str(self.temp_dir))
        
        # 데이터베이스 파일 존재 확인
        db_path = self.temp_dir / 'superclaude_learning.db'
        self.assertTrue(db_path.exists())
        
        # 테이블 구조 확인
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['interactions', 'feedback', 'pattern_success', 'user_preferences']
            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} not found")
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        
        # 잘못된 입력에 대한 안전한 처리
        result = processor.process("")
        self.assertEqual(result, "")
        
        result = processor.process("normal command")
        self.assertEqual(result, "normal command")
        
        # /sc: 명령어가 아닌 경우
        result = processor.process("analyze this code")
        self.assertEqual(result, "analyze this code")

class TestSystemPerformance(unittest.TestCase):
    """시스템 성능 테스트"""
    
    def test_recommendation_speed(self):
        """추천 속도 테스트"""
        import time
        from claude_sc_preprocessor import SCCommandProcessor
        
        processor = SCCommandProcessor()
        
        # 추천 속도 측정
        start_time = time.time()
        for i in range(10):
            result = processor.process(f"/sc:analyze test code {i}")
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        self.assertLess(avg_time, 1.0, "Recommendation should be fast (< 1 second)")
    
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        import psutil
        import os
        from claude_sc_preprocessor import SCCommandProcessor
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 여러 추천 실행
        processor = SCCommandProcessor()
        for i in range(100):
            processor.process(f"/sc:analyze test {i}")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가가 100MB 이하인지 확인
        self.assertLess(memory_increase, 100 * 1024 * 1024, "Memory usage should be reasonable")

def run_all_tests():
    """모든 테스트 실행"""
    
    print("🧪 SuperClaude Learning System Test Suite")
    print("=" * 60)
    
    # 기본 의존성 확인
    missing_deps = []
    try:
        import numpy
    except ImportError:
        missing_deps.append('numpy')
    
    try:
        import sqlite3
    except ImportError:
        missing_deps.append('sqlite3')
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install: pip install numpy")
        return False
    
    # 테스트 실행
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 케이스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestLearningSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemPerformance))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print(f"🎯 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 All tests passed! Learning system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)