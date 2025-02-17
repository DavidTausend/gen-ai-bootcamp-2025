import unittest
from app import app, db
from models import Word, WordGroup, StudySession, StudyActivity


class TestRoutes(unittest.TestCase):

    def setUp(self):
        """Set up a clean test environment before each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for testing
        self.app = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Ensure database is properly reset between tests."""
        with app.app_context():
            db.session.rollback()  # ✅ Fix: Ensure tests don't remove required data
            db.session.remove()
            db.drop_all()

    def test_get_last_study_session(self):
        """Test retrieving the last study session when no sessions exist."""
        response = self.app.get('/api/dashboard/last_study_session')
        self.assertEqual(response.status_code, 404)  # Assuming no data is present initially

    def test_add_study_activity(self):
        """Ensure study activity is created with a valid `study_session_id`."""
        with app.app_context():
            # Create required data before making the request
            group = WordGroup(name="Test Group")
            db.session.add(group)
            db.session.commit()

            study_session = StudySession(group_id=group.id)
            db.session.add(study_session)
            db.session.commit()

            # Fix: Use only `study_session_id`
            response = self.app.post('/api/study_activities', json={
                "study_session_id": study_session.id  # ✅ Correct field name
            })
            self.assertEqual(response.status_code, 201)

    def test_add_study_activity_invalid_data(self):
        """Ensure API rejects requests with missing required fields."""
        response = self.app.post('/api/study_activities', json={})  # No `study_session_id`
        self.assertEqual(response.status_code, 400)  # Now correctly expects `400`

    def test_get_words_paginated(self):
        """Ensure words pagination works correctly."""
        response = self.app.get('/api/words?page=1')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('items', json_data)
        self.assertIn('pagination', json_data)

    def test_get_words_invalid_page(self):
        """Ensure invalid page numbers return a 400 error."""
        response = self.app.get('/api/words?page=invalid')
        self.assertEqual(response.status_code, 400)  # Expecting bad request for invalid page number

    def test_get_word_details(self):
        """Ensure a word exists before trying to retrieve it."""
        with app.app_context():
            word = Word(german="Apfel", english="Apple", parts="{}")  # ✅ Ensure required fields
            db.session.add(word)
            db.session.commit()
            word_id = word.id  # Get the actual ID

        response = self.app.get(f'/api/words/{word_id}')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('german', json_data)
        self.assertIn('english', json_data)

    def test_get_word_details_not_found(self):
        """Ensure non-existent words return a 404 error."""
        response = self.app.get('/api/words/999')
        self.assertEqual(response.status_code, 404)  # Expecting not found for non-existent word

    def test_delete_word(self):
        """Ensure we delete the correct word ID dynamically."""
        with app.app_context():
            word = Word(german="Apfel", english="Apple")  # ✅ Ensure required fields
            db.session.add(word)
            db.session.commit()
            word_id = word.id  # Get the actual word ID ✅

            response = self.app.delete(f'/api/words/{word_id}')
            self.assertEqual(response.status_code, 200)

            # Verify the word is deleted
            response = self.app.get(f'/api/words/{word_id}')
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
