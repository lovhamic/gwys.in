"""
Skill Library — SQLite storage for learned robot skills

Skills are recorded trajectories from teaching mode.
A skill = sequence of {time, joint_angles, gripper} frames.
"""

import sqlite3
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent / "skills.db"


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            trajectory_json TEXT NOT NULL,
            servo_types TEXT,
            created_at REAL NOT NULL,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            average_time REAL DEFAULT 0,
            last_used REAL
        )
    """)
    
    conn.commit()
    conn.close()


def save_skill(skill_id: str, name: str, trajectory: list, 
               servo_types: list = None, description: str = "", tags: list = None) -> bool:
    """Save a new skill or overwrite existing."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO skills 
        (skill_id, name, description, tags, trajectory_json, servo_types, created_at, last_used)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        skill_id, name, description,
        json.dumps(tags or []),
        json.dumps(trajectory),
        json.dumps(servo_types or [1, 0, 0, 1]),
        time.time(),
        time.time()
    ))
    
    conn.commit()
    conn.close()
    return True


def load_skill(skill_id: str) -> Optional[dict]:
    """Load a skill by ID. Returns dict or None."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM skills WHERE skill_id = ?", (skill_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    skill = dict(row)
    skill["trajectory"] = json.loads(skill["trajectory_json"])
    skill["tags"] = json.loads(skill["tags"])
    skill["servo_types"] = json.loads(skill["servo_types"])
    return skill


def list_skills() -> List[dict]:
    """List all skills with metadata."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT skill_id, name, description, tags, success_count, failure_count, created_at
        FROM skills ORDER BY last_used DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    skills = []
    for row in rows:
        skill = dict(row)
        skill["tags"] = json.loads(skill["tags"])
        skills.append(skill)
    return skills


def delete_skill(skill_id: str) -> bool:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM skills WHERE skill_id = ?", (skill_id,))
    conn.commit()
    conn.close()
    return True


def record_success(skill_id: str, execution_time: float):
    """Increment success count and update average time."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT success_count, average_time FROM skills WHERE skill_id = ?", (skill_id,))
    row = cursor.fetchone()
    if row:
        new_count = row[0] + 1
        new_avg = ((row[1] * row[0]) + execution_time) / new_count if row[0] > 0 else execution_time
        cursor.execute(
            "UPDATE skills SET success_count = ?, average_time = ?, last_used = ? WHERE skill_id = ?",
            (new_count, new_avg, time.time(), skill_id)
        )
        conn.commit()
    conn.close()


def record_failure(skill_id: str):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE skills SET failure_count = failure_count + 1 WHERE skill_id = ?",
        (skill_id,)
    )
    conn.commit()
    conn.close()


# Auto-init
init_db()
