import os

class Config:
    SECRET_KEY = "ABCDEF"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:root@localhost:5432/flask_dbms_project"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 