"""Create the database and tables. Run from backend/:  python create_tables.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

with app.app_context():
    db.create_all()
    path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    print("Tables created at:", path)
