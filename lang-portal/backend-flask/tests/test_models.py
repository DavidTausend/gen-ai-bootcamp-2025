import unittest
from app import db, app
from models import Word

class TestModels(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_word_creation(self):
        """Ensure a Word can be created with valid input."""
        with app.app_context():
            word = Word(german="Apfel", english="Apple", parts="{}")  # ✅ Fix: Ensure `german` is set
            db.session.add(word)
            db.session.commit()

            # Ensure word exists in DB
            retrieved_word = Word.query.get(word.id)
            assert retrieved_word is not None
            assert retrieved_word.german == "Apfel"
            assert retrieved_word.english == "Apple"


if __name__ == '__main__':
    unittest.main()
