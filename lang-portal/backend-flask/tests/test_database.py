import unittest
from flask import Flask
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Word  # Ensure Word is imported
from db.seeds import seed_data


class TestDatabase(unittest.TestCase):

   def setUp(self):
    """Set up a fresh test database before each test."""
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory DB
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    
    self.app = app.test_client()
    
    with app.app_context():
        print("Creating all tables...")
        db.create_all()  # Ensure tables exist before running tests
        print("Tables created.")
        seed_data()  # Seed the database with initial data

    def tearDown(self):
        """Drop all tables after each test to start fresh."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_database_connection(self):
        """Check if database connection works."""
        with app.app_context():
            word_count = db.session.query(Word).count()
            self.assertGreater(word_count, 0, "Database connection failed!")

if __name__ == "__main__":
    unittest.main()
