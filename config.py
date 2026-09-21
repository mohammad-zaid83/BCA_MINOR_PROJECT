import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATASET_PATH   = os.path.join(BASE_DIR, "dataset", "students.csv")
MODEL_PATH     = os.path.join(BASE_DIR, "models", "student_model.pkl")
METRICS_PATH   = os.path.join(BASE_DIR, "models", "model_accuracy.json")
DATABASE_PATH  = os.path.join(BASE_DIR, "database", "students.db")

SECRET_KEY = "bca-minor-project-secret-key-change-in-production"

FEATURES = ["Study_Hours", "Attendance", "Previous_Marks", "Assignments_Completed"]
TARGET   = "Final_Marks"

TEST_SIZE    = 0.2
RANDOM_STATE = 42