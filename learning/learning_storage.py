#!/usr/bin/env python3
"""
SuperClaude Learning Data Storage System
학습 데이터 저장 및 관리 시스템
"""

import json
import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import threading

@dataclass
class UserInteraction:
    """사용자 상호작용 기록"""
    timestamp: str
    user_input: str
    command: str
    description: str
    recommended_flags: str
    actual_flags: str
    project_context: Dict[str, Any]
    success: bool
    execution_time: float
    confidence: int
    reasoning: str
    user_id: str
    project_hash: str

@dataclass
class FeedbackRecord:
    """사용자 피드백 기록"""
    timestamp: str
    interaction_id: str
    feedback_type: str  # 'implicit', 'explicit'
    rating: Optional[int]  # 1-5 scale
    success_indicator: bool
    user_correction: Optional[str]
    user_id: str
    project_hash: str

@dataclass
class PatternSuccess:
    """패턴 성공률 기록"""
    pattern_name: str
    total_uses: int
    successful_uses: int
    success_rate: float
    last_updated: str
    context_conditions: Dict[str, Any]

class LearningStorage:
    """학습 데이터 저장 및 관리"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        # 학습 데이터는 별도 디렉토리에 저장 (SuperClaude 코드와 분리)
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / '.claude' / 'learning'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.storage_dir / 'superclaude_learning.db'
        self.user_id = self._get_or_create_user_id()
        self._lock = threading.Lock()
        
        self._init_database()
    
    def _get_or_create_user_id(self) -> str:
        """사용자 ID 생성 또는 로드"""
        user_id_file = self.storage_dir / 'user_id.txt'
        
        if user_id_file.exists():
            return user_id_file.read_text().strip()
        else:
            # 개인정보 보호를 위한 익명 ID 생성
            user_id = hashlib.sha256(f"{os.getlogin()}{Path.home()}".encode()).hexdigest()[:16]
            user_id_file.write_text(user_id)
            return user_id
    
    def _init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    command TEXT NOT NULL,
                    description TEXT,
                    recommended_flags TEXT,
                    actual_flags TEXT,
                    project_context TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    confidence INTEGER,
                    reasoning TEXT,
                    user_id TEXT NOT NULL,
                    project_hash TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    interaction_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER,
                    success_indicator BOOLEAN,
                    user_correction TEXT,
                    user_id TEXT NOT NULL,
                    project_hash TEXT NOT NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pattern_success (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT UNIQUE NOT NULL,
                    total_uses INTEGER DEFAULT 0,
                    successful_uses INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    last_updated TEXT NOT NULL,
                    context_conditions TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    project_hash TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    preference_weight REAL DEFAULT 1.0,
                    last_updated TEXT NOT NULL,
                    UNIQUE(user_id, project_hash, pattern_name)
                )
            ''')
            
            # 인덱스 생성
            conn.execute('CREATE INDEX IF NOT EXISTS idx_interactions_user_project ON interactions(user_id, project_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_interaction ON feedback(interaction_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_pattern_success_name ON pattern_success(pattern_name)')
    
    def record_interaction(self, interaction: UserInteraction) -> str:
        """사용자 상호작용 기록"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO interactions (
                        timestamp, user_input, command, description,
                        recommended_flags, actual_flags, project_context,
                        success, execution_time, confidence, reasoning,
                        user_id, project_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.timestamp,
                    interaction.user_input,
                    interaction.command,
                    interaction.description,
                    interaction.recommended_flags,
                    interaction.actual_flags,
                    json.dumps(interaction.project_context),
                    interaction.success,
                    interaction.execution_time,
                    interaction.confidence,
                    interaction.reasoning,
                    interaction.user_id,
                    interaction.project_hash
                ))
                
                return str(cursor.lastrowid)
    
    def record_feedback(self, feedback: FeedbackRecord):
        """피드백 기록"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO feedback (
                        timestamp, interaction_id, feedback_type,
                        rating, success_indicator, user_correction,
                        user_id, project_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    feedback.timestamp,
                    feedback.interaction_id,
                    feedback.feedback_type,
                    feedback.rating,
                    feedback.success_indicator,
                    feedback.user_correction,
                    feedback.user_id,
                    feedback.project_hash
                ))
    
    def update_pattern_success(self, pattern_name: str, success: bool, context: Dict[str, Any]):
        """패턴 성공률 업데이트"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # 기존 기록 조회
                cursor = conn.execute(
                    'SELECT total_uses, successful_uses FROM pattern_success WHERE pattern_name = ?',
                    (pattern_name,)
                )
                result = cursor.fetchone()
                
                if result:
                    total_uses, successful_uses = result
                    total_uses += 1
                    if success:
                        successful_uses += 1
                    success_rate = successful_uses / total_uses
                    
                    conn.execute('''
                        UPDATE pattern_success 
                        SET total_uses = ?, successful_uses = ?, success_rate = ?, 
                            last_updated = ?, context_conditions = ?
                        WHERE pattern_name = ?
                    ''', (
                        total_uses, successful_uses, success_rate,
                        datetime.now().isoformat(),
                        json.dumps(context),
                        pattern_name
                    ))
                else:
                    # 새 패턴 생성
                    total_uses = 1
                    successful_uses = 1 if success else 0
                    success_rate = successful_uses / total_uses
                    
                    conn.execute('''
                        INSERT INTO pattern_success 
                        (pattern_name, total_uses, successful_uses, success_rate, last_updated, context_conditions)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern_name, total_uses, successful_uses, success_rate,
                        datetime.now().isoformat(),
                        json.dumps(context)
                    ))
    
    def get_user_interactions(self, days: int = 30, project_hash: Optional[str] = None) -> List[Dict]:
        """사용자 상호작용 기록 조회"""
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = '''
                SELECT * FROM interactions 
                WHERE user_id = ? AND timestamp > ?
            '''
            params = [self.user_id, since_date]
            
            if project_hash:
                query += ' AND project_hash = ?'
                params.append(project_hash)
                
            query += ' ORDER BY timestamp DESC'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pattern_success_rates(self) -> Dict[str, PatternSuccess]:
        """패턴 성공률 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM pattern_success')
            
            results = {}
            for row in cursor.fetchall():
                pattern = PatternSuccess(
                    pattern_name=row['pattern_name'],
                    total_uses=row['total_uses'],
                    successful_uses=row['successful_uses'],
                    success_rate=row['success_rate'],
                    last_updated=row['last_updated'],
                    context_conditions=json.loads(row['context_conditions']) if row['context_conditions'] else {}
                )
                results[row['pattern_name']] = pattern
            
            return results
    
    def get_user_preferences(self, project_hash: Optional[str] = None) -> Dict[str, float]:
        """사용자 선호도 조회"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT pattern_name, preference_weight 
                FROM user_preferences 
                WHERE user_id = ?
            '''
            params = [self.user_id]
            
            if project_hash:
                query += ' AND project_hash = ?'
                params.append(project_hash)
            
            cursor = conn.execute(query, params)
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def update_user_preference(self, pattern_name: str, weight: float, project_hash: str):
        """사용자 선호도 업데이트"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, project_hash, pattern_name, preference_weight, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    self.user_id, project_hash, pattern_name, weight,
                    datetime.now().isoformat()
                ))
    
    def get_project_hash(self, project_path: str) -> str:
        """프로젝트 해시 생성"""
        project_path = Path(project_path).resolve()
        return hashlib.sha256(str(project_path).encode()).hexdigest()[:16]
    
    def cleanup_old_data(self, days: int = 90):
        """오래된 데이터 정리"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM interactions WHERE timestamp < ?', (cutoff_date,))
                conn.execute('DELETE FROM feedback WHERE timestamp < ?', (cutoff_date,))
    
    def export_learning_data(self) -> Dict[str, Any]:
        """학습 데이터 내보내기 (개인정보 제외)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 패턴 성공률 데이터
            pattern_cursor = conn.execute('SELECT * FROM pattern_success')
            patterns = [dict(row) for row in pattern_cursor.fetchall()]
            
            # 사용자별 프로젝트 컨텍스트 통계 (익명화)
            stats_cursor = conn.execute('''
                SELECT project_hash, command, 
                       COUNT(*) as usage_count,
                       AVG(confidence) as avg_confidence,
                       AVG(success) as success_rate
                FROM interactions 
                WHERE user_id = ?
                GROUP BY project_hash, command
            ''', (self.user_id,))
            stats = [dict(row) for row in stats_cursor.fetchall()]
            
            return {
                'export_timestamp': datetime.now().isoformat(),
                'pattern_success_rates': patterns,
                'usage_statistics': stats,
                'user_id': self.user_id  # 익명화된 ID
            }

# 전역 스토리지 인스턴스
_storage_instance = None

def get_learning_storage() -> LearningStorage:
    """전역 스토리지 인스턴스 가져오기"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = LearningStorage()
    return _storage_instance