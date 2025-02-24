from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# ----------------------------
# Words & Groups Models
# ----------------------------

class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    german = db.Column(db.String(100), nullable=False)
    english = db.Column(db.String(100), nullable=False)
    parts = db.Column(db.Text, nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('word_groups.id'), nullable=True)

    def __init__(self, german, english, parts=None):
        if not german or not english:
            raise ValueError("Both 'german' and 'english' are required fields")
        self.german = german
        self.english = english
        self.parts = json.dumps(parts) if isinstance(parts, dict) else parts

    def to_dict(self):
        return {
            "id": self.id,
            "german": self.german,
            "english": self.english,
            "parts": json.loads(self.parts) if self.parts else None
        }


class WordGroup(db.Model):
    __tablename__ = 'word_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    words = db.relationship('Word', backref='group', lazy=True)
    study_sessions = db.relationship('StudySession', backref='word_group', lazy=True)


# ----------------------------
# Study Sessions & Activities
# ----------------------------

class StudySession(db.Model):
    __tablename__ = 'study_sessions'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('word_groups.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    activities = db.relationship('StudyActivity', backref='session', lazy=True)


class StudyActivity(db.Model):
    __tablename__ = 'study_activities'

    id = db.Column(db.Integer, primary_key=True)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class StudyReviewItem(db.Model):
    __tablename__ = 'study_review_items'

    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), primary_key=True)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), primary_key=True)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# ----------------------------
# Grading Result Model
# ----------------------------

class GradingResult(db.Model):
    __tablename__ = 'grading_results'

    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String(255), nullable=False)
    transcription = db.Column(db.String(255), nullable=False)
    translation = db.Column(db.String(255))
    grade = db.Column(db.String(5))
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "sentence": self.sentence,
            "transcription": self.transcription,
            "translation": self.translation,
            "grade": self.grade,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat()
        }