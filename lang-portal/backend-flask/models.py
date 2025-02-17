from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    german = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(100), nullable=False)
    parts = db.Column(db.Text, nullable=True)

    def __init__(self, german, english, parts=None):
        if not german or not english:  # Ensure required fields are set
            raise ValueError("Both 'german' and 'english' are required fields")

        self.german = german
        self.english = english
        self.parts = json.dumps(parts) if isinstance(parts, dict) else parts

    def to_dict(self):
        return {
            "id": self.id,
            "german": self.german,
            "english": self.english,
            "parts": json.loads(self.parts) if self.parts else None  # Convert back to dict
        }

class WordGroup(db.Model):
    __tablename__ = 'word_group'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    
    # Relationship
    study_sessions = db.relationship('StudySession', backref='word_group', lazy=True)

class StudySession(db.Model):
    __tablename__ = 'study_session'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('word_group.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Fix: Change backref name to avoid duplicate conflicts
    activities = db.relationship('StudyActivity', backref='session', lazy=True)

class StudyActivity(db.Model):
    __tablename__ = 'study_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class StudyReviewItem(db.Model):
    __tablename__ = 'study_review_item'
    
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), primary_key=True)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'), primary_key=True)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
