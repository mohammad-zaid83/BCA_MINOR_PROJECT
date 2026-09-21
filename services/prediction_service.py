"""Handles prediction persistence and retrieval (scoped per student)."""
import os
import sqlite3
from datetime import datetime

from config import DATABASE_PATH


def _connect():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_prediction(student_id, study_hours, attendance, previous_marks,
                    assignments_completed, predicted_marks, grade, category):
    conn = _connect()
    conn.execute("""
        INSERT INTO predictions
        (student_id, study_hours, attendance, previous_marks,
         assignments_completed, predicted_marks, grade, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id, study_hours, attendance, previous_marks,
        assignments_completed, round(predicted_marks, 2), grade, category,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()


def get_history(student_id, limit=None):
    conn = _connect()
    sql = "SELECT * FROM predictions WHERE student_id = ? ORDER BY id DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    rows = conn.execute(sql, (student_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest(student_id):
    history = get_history(student_id, limit=1)
    return history[0] if history else None


def count_predictions(student_id):
    conn = _connect()
    n = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE student_id = ?", (student_id,)
    ).fetchone()[0]
    conn.close()
    return n


def clear_history(student_id):
    conn = _connect()
    conn.execute("DELETE FROM predictions WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()