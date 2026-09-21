"""
train_model.py
Trains the Linear Regression model on the student dataset.
- Features: Study_Hours, Attendance, Previous_Marks, Assignments_Completed
- Target:   Final_Marks
- Split:    80/20, random_state=42
"""
import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from config import (
    DATASET_PATH,
    FEATURES,
    METRICS_PATH,
    MODEL_PATH,
    RANDOM_STATE,
    TARGET,
    TEST_SIZE,
)


def train():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    data = pd.read_csv(DATASET_PATH)

    # Validate required columns
    missing = [c for c in FEATURES + [TARGET] if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    X = data[FEATURES]
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    r2   = r2_score(y_test, y_pred)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    metrics = {
        "algorithm": "Linear Regression",
        "features": FEATURES,
        "target": TARGET,
        "train_size": 1 - TEST_SIZE,
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "n_samples": int(len(data)),
        "r2_score": round(float(r2), 4),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "coefficients": {feat: round(float(coef), 4) for feat, coef in zip(FEATURES, model.coef_)},
        "intercept": round(float(model.intercept_), 4),
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print("=" * 55)
    print("  MODEL TRAINING COMPLETE")
    print("=" * 55)
    print(f"  Algorithm : Linear Regression")
    print(f"  Samples   : {len(data)}")
    print(f"  Train/Test: {int((1-TEST_SIZE)*100)}% / {int(TEST_SIZE*100)}%")
    print(f"  R2 Score  : {r2:.4f}")
    print(f"  MAE       : {mae:.4f}")
    print(f"  RMSE      : {rmse:.4f}")
    print("=" * 55)
    print(f"  Model saved to   : {MODEL_PATH}")
    print(f"  Metrics saved to : {METRICS_PATH}")


if __name__ == "__main__":
    train()