import unittest
from app import app
from models import db, Word
from services import some_service_function  # Assuming a service function exists

class TestServices(unittest.TestCase):

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

    def test_service_function(self):
        with app.app_context():
            # Assuming some_service_function interacts with the database
            result = some_service_function()
            self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
