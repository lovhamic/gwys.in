"""
Memory Store — SQLite database for conversations, commands, and state history

Tables:
  conversations: id, timestamp, user_text, ai_response, mood
  commands: id, timestamp, command_text, commands_json, success, failure_reason
  states: id, timestamp, joint_angles, gripper, sensors, mood
"""

import sqlite3
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent / "memory.db"


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            user_text TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            mood TEXT DEFAULT 'curious',
            command_count INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            command_text TEXT NOT NULL,
            commands_json TEXT NOT NULL,
            success INTEGER DEFAULT 0,
            failure_reason TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            joint_angles TEXT NOT NULL,
            gripper REAL NOT NULL,
            distance REAL,
            current REAL,
            mood TEXT DEFAULT 'curious',
            status TEXT DEFAULT 'idle'
        )
    """)
    
    conn.commit()
    conn.close()


def log_conversation(user_text: str, ai_response: str, mood: str = "curious", command_count: int = 0):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (timestamp, user_text, ai_response, mood, command_count) VALUES (?, ?, ?, ?, ?)",
        (time.time(), user_text, ai_response, mood, command_count)
    )
    conn.commit()
    conn.close()


def log_command(command_text: str, commands_json: list, success: bool = False, failure_reason: str = None):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO commands (timestamp, command_text, commands_json, success, failure_reason) VALUES (?, ?, ?, ?, ?)",
        (time.time(), command_text, json.dumps(commands_json), int(success), failure_reason)
    )
    conn.commit()
    conn.close()


def log_state(joint_angles: list, gripper: float, distance: float, current: float, mood: str, status: str):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO states (timestamp, joint_angles, gripper, distance, current, mood, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (time.time(), json.dumps(joint_angles), gripper, distance, current, mood, status)
    )
    conn.commit()
    conn.close()


def get_conversation_history(limit: int = 10) -> List[dict]:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_states(limit: int = 5) -> List[dict]:
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM states ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_command_success(command_text: str):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE commands SET success = 1 WHERE command_text = ? ORDER BY timestamp DESC LIMIT 1",
        (command_text,)
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = _get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM commands")
    cmd_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM commands WHERE success = 1")
    success_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM states")
    state_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "conversations": conv_count,
        "commands": cmd_count,
        "successes": success_count,
        "states": state_count,
        "success_rate": (success_count / cmd_count * 100) if cmd_count > 0 else 0,
    }


# Auto-init on import
init_db()
