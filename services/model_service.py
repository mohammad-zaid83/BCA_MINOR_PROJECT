"""Loads the trained model and exposes prediction + metrics."""
import json
import os
import pickle

import numpy as np

from config import FEATURES, METRICS_PATH, MODEL_PATH


class ModelService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run `python train_model.py` first."
            )
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH) as f:
                self.metrics = json.load(f)
        else:
            self.metrics = {}

    def predict(self, study_hours, attendance, previous_marks, assignments):
        # Feature order MUST match training order
        X = np.array([[study_hours, attendance, previous_marks, assignments]])
        pred = float(self.model.predict(X)[0])
        # Clamp to valid marks range
        return max(0.0, min(100.0, pred))

    def get_metrics(self):
        return self.metrics

    def get_coefficients(self):
        return self.metrics.get("coefficients", {})

    def get_intercept(self):
        return self.metrics.get("intercept", 0.0)


def get_grade_and_category(marks: float):
    """
    Grading rule (kept separate from ML prediction):
      >= 90  -> A+  Excellent
      >= 80  -> A   Very Good
      >= 70  -> B+  Good
      >= 60  -> B   Above Average
      >= 50  -> C   Average
      >= 40  -> D   Pass
      <  40  -> F   Needs Improvement
    """
    if marks >= 90:
        return "A+", "Excellent"
    elif marks >= 80:
        return "A", "Very Good"
    elif marks >= 70:
        return "B+", "Good"
    elif marks >= 60:
        return "B", "Above Average"
    elif marks >= 50:
        return "C", "Average"
    elif marks >= 40:
        return "D", "Pass"
    else:
        return "F", "Needs Improvement"