import sqlite3
import json
import os
from datetime import datetime

class RegistryManager:
    def __init__(self, db_path: str = "registry/soca.db"):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sutra_registry (
                    sutra_id TEXT PRIMARY KEY,
                    sutra_version TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    pramana TEXT NOT NULL,
                    pramana_confidence REAL DEFAULT 1.0,
                    confidence REAL DEFAULT 1.0,
                    module_path TEXT NOT NULL,
                    entry_point TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sutra_id TEXT NOT NULL,
                    test_input TEXT NOT NULL,
                    expected_output TEXT NOT NULL,
                    actual_output TEXT,
                    passed BOOLEAN,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sutra_id) REFERENCES sutra_registry(sutra_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trace_log (
                    trace_id TEXT PRIMARY KEY,
                    executed_sutras TEXT,
                    status TEXT,
                    total_execution_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def register_sutra(self, sutra_json: dict):
        pramana = sutra_json.get('pramana', 'anumana')
        pramana_confidence = {'pratyaksha': 1.0, 'anumana': 0.9, 'upamana': 0.8, 'shabda': 0.6}.get(pramana, 0.9)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sutra_registry (
                    sutra_id, sutra_version, name, category, pramana,
                    pramana_confidence, confidence,
                    module_path, entry_point, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sutra_json.get('sutra_id'),
                sutra_json.get('sutra_version', '1.0.0'),
                sutra_json.get('name'),
                sutra_json.get('category', 'core'),
                pramana,
                pramana_confidence,
                pramana_confidence,
                sutra_json.get('operation', {}).get('module'),
                sutra_json.get('operation', {}).get('entry_point', 'execute'),
                True
            ))
            conn.commit()
    
    def get_sutra(self, sutra_id: str) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sutra_id, sutra_version, name, category, pramana,
                       pramana_confidence, confidence,
                       module_path, entry_point
                FROM sutra_registry
                WHERE sutra_id = ? AND is_active = TRUE
            """, (sutra_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'sutra_id': row[0],
                    'sutra_version': row[1],
                    'name': row[2],
                    'category': row[3],
                    'pramana': row[4],
                    'pramana_confidence': row[5],
                    'confidence': row[6],
                    'module_path': row[7],
                    'entry_point': row[8]
                }
            return None
    
    def record_usage(self, sutra_id: str, success: bool):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if success:
                cursor.execute("""
                    UPDATE sutra_registry
                    SET usage_count = usage_count + 1,
                        success_count = success_count + 1,
                        confidence = MIN(1.0, confidence + 0.01),
                        last_used = CURRENT_TIMESTAMP
                    WHERE sutra_id = ?
                """, (sutra_id,))
            else:
                cursor.execute("""
                    UPDATE sutra_registry
                    SET usage_count = usage_count + 1,
                        failure_count = failure_count + 1,
                        confidence = MAX(0.1, confidence - 0.05),
                        last_used = CURRENT_TIMESTAMP
                    WHERE sutra_id = ?
                """, (sutra_id,))
            conn.commit()
    
    def log_trace(self, trace_data: dict):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trace_log (trace_id, executed_sutras, status, total_execution_time_ms)
                VALUES (?, ?, ?, ?)
            """, (
                trace_data.get('trace_id'),
                json.dumps(trace_data.get('executed_sutras', [])),
                trace_data.get('status', 'unknown'),
                trace_data.get('total_execution_time_ms', 0)
            ))
            conn.commit()
    
    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sutra_registry WHERE is_active = TRUE")
            total_sutras = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trace_log")
            total_traces = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(usage_count) FROM sutra_registry")
            total_usage = cursor.fetchone()[0] or 0
            return {
                'total_sutras': total_sutras,
                'total_traces': total_traces,
                'total_usage': total_usage
            }
