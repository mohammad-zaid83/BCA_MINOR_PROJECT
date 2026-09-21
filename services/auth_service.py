"""SQLite-backed authentication and student profile handling."""
import os
import sqlite3
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from config import DATABASE_PATH


# Demo student accounts (STU001..STU008)
DEMO_STUDENTS = [
    ("STU001", "Aarav Sharma",    "aarav@student.demo",    "BCA", "Semester 5", "stu001"),
    ("STU002", "Diya Patel",      "diya@student.demo",     "BCA", "Semester 5", "stu002"),
    ("STU003", "Rohan Verma",     "rohan@student.demo",    "BCA", "Semester 5", "stu003"),
    ("STU004", "Ananya Iyer",     "ananya@student.demo",   "BCA", "Semester 5", "stu004"),
    ("STU005", "Kabir Singh",     "kabir@student.demo",    "BCA", "Semester 5", "stu005"),
    ("STU006", "Meera Nair",      "meera@student.demo",    "BCA", "Semester 5", "stu006"),
    ("STU007", "Arjun Reddy",     "arjun@student.demo",    "BCA", "Semester 5", "stu007"),
    ("STU008", "Sara Khan",       "sara@student.demo",     "BCA", "Semester 5", "stu008"),
]


def _connect():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed demo students if not present."""
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            email        TEXT NOT NULL,
            course       TEXT NOT NULL,
            semester     TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id             TEXT NOT NULL,
            study_hours            REAL NOT NULL,
            attendance             REAL NOT NULL,
            previous_marks         REAL NOT NULL,
            assignments_completed  REAL NOT NULL,
            predicted_marks        REAL NOT NULL,
            grade                  TEXT NOT NULL,
            category               TEXT NOT NULL,
            created_at             TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    for sid, name, email, course, semester, pwd in DEMO_STUDENTS:
        cur.execute("SELECT 1 FROM students WHERE student_id = ?", (sid,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                (sid, name, email, course, semester, generate_password_hash(pwd)),
            )

    conn.commit()
    conn.close()


def authenticate(student_id: str, password: str):
    if not student_id or not password:
        return None
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id.strip().upper(),))
    row = cur.fetchone()
    conn.close()

    if row and check_password_hash(row["password_hash"], password):
        return {
            "student_id": row["student_id"],
            "name": row["name"],
            "email": row["email"],
            "course": row["course"],
            "semester": row["semester"],
        }
    return None


def get_student(student_id: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "student_id": row["student_id"],
        "name": row["name"],
        "email": row["email"],
        "course": row["course"],
        "semester": row["semester"],
    }