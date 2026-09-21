"""
main.py — Entry point for the Student Academic Performance Prediction System.
Run: python main.py
"""
from functools import wraps

from flask import (
    Flask, flash, jsonify, redirect, render_template,
    request, session, url_for,
)

from config import DATASET_PATH, SECRET_KEY
from services.auth_service import authenticate, get_student, init_db
from services.model_service import ModelService, get_grade_and_category
from services.prediction_service import (
    clear_history, count_predictions, get_history, get_latest, save_prediction,
)

import pandas as pd

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize DB + load model once
init_db()
model_service = ModelService()


# ---------- Auth helpers ----------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_user():
    return {
        "current_student": session.get("student_name"),
        "current_student_id": session.get("student_id"),
    }


# ---------- Routes ----------
@app.route("/")
def index():
    return redirect(url_for("dashboard") if "student_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        sid = request.form.get("student_id", "").strip()
        pwd = request.form.get("password", "")

        if not sid or not pwd:
            flash("Please enter both Student ID and Password.", "error")
            return redirect(url_for("login"))

        student = authenticate(sid, pwd)
        if student:
            session["student_id"] = student["student_id"]
            session["student_name"] = student["name"]
            flash(f"Welcome back, {student['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Student ID or Password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    sid = session["student_id"]
    latest = get_latest(sid)
    total = count_predictions(sid)
    recent = get_history(sid, limit=5)
    return render_template(
        "dashboard.html",
        latest=latest,
        total_predictions=total,
        recent=recent,
    )


@app.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction():
    if request.method == "POST":
        try:
            study_hours = float(request.form.get("study_hours", "").strip())
            attendance = float(request.form.get("attendance", "").strip())
            previous_marks = float(request.form.get("previous_marks", "").strip())
            assignments = float(request.form.get("assignments_completed", "").strip())
        except (ValueError, TypeError):
            flash("Please enter valid numeric values in all fields.", "error")
            return redirect(url_for("prediction"))

        errors = []
        if study_hours < 0 or study_hours > 24:
            errors.append("Study Hours must be between 0 and 24.")
        if attendance < 0 or attendance > 100:
            errors.append("Attendance must be between 0 and 100.")
        if previous_marks < 0 or previous_marks > 100:
            errors.append("Previous Marks must be between 0 and 100.")
        if assignments < 0 or assignments > 50:
            errors.append("Assignments Completed must be between 0 and 50.")

        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("prediction"))

        predicted = model_service.predict(
            study_hours, attendance, previous_marks, assignments
        )
        grade, category = get_grade_and_category(predicted)

        save_prediction(
            session["student_id"], study_hours, attendance,
            previous_marks, assignments, predicted, grade, category,
        )

        return render_template(
            "result.html",
            study_hours=study_hours,
            attendance=attendance,
            previous_marks=previous_marks,
            assignments=assignments,
            predicted=round(predicted, 2),
            grade=grade,
            category=category,
        )

    return render_template("prediction.html")


@app.route("/analytics")
@login_required
def analytics():
    sid = session["student_id"]
    history = get_history(sid)

    # Dataset analytics (real values)
    try:
        df = pd.read_csv(DATASET_PATH)
        dataset_stats = {
            "count": int(len(df)),
            "study_vs_final": {
                "study": df["Study_Hours"].round(2).tolist(),
                "final": df["Final_Marks"].round(2).tolist(),
            },
            "attendance_vs_final": {
                "attendance": df["Attendance"].round(2).tolist(),
                "final": df["Final_Marks"].round(2).tolist(),
            },
            "previous_vs_final": {
                "previous": df["Previous_Marks"].round(2).tolist(),
                "final": df["Final_Marks"].round(2).tolist(),
            },
            "assignments_vs_final": {
                "assignments": df["Assignments_Completed"].round(2).tolist(),
                "final": df["Final_Marks"].round(2).tolist(),
            },
        }
    except Exception:
        dataset_stats = {"count": 0}

    return render_template(
        "analytics.html",
        history=history,
        dataset_stats=dataset_stats,
        metrics=model_service.get_metrics(),
    )


@app.route("/history")
@login_required
def history():
    history = get_history(session["student_id"])
    return render_template("history.html", history=history)


@app.route("/history/clear", methods=["POST"])
@login_required
def clear_history_route():
    clear_history(session["student_id"])
    flash("Your prediction history has been cleared.", "success")
    return redirect(url_for("history"))


@app.route("/profile")
@login_required
def profile():
    student = get_student(session["student_id"])
    total = count_predictions(session["student_id"])
    return render_template("profile.html", student=student, total_predictions=total)


@app.route("/model")
@login_required
def model_info():
    metrics = model_service.get_metrics()
    return render_template("model.html", metrics=metrics)


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# ---------- Error handlers ----------
@app.errorhandler(404)
def not_found(e):
    return render_template("login.html", not_found=True), 404


if __name__ == "__main__":
    print("=" * 55)
    print("  Student Academic Performance Prediction System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True)