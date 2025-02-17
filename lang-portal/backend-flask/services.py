from models import db, Word

def some_service_function():
    # Example service function that retrieves all words
    words = Word.query.all()
    return words
