import json
from models import db, Word, WordGroup, StudySession

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Load words
    for word_data in data.get('words', []):
        word = Word(german=word_data['german'], english=word_data['english'], parts=word_data.get('parts', {}))
        db.session.add(word)

    # Load word groups
    for group_data in data.get('groups', []):
        group = WordGroup(name=group_data['name'])
        db.session.add(group)

    # Load study sessions
    for session_data in data.get('study_sessions', []):
        session = StudySession(group_id=session_data['group_id'], created_at=session_data['created_at'])
        db.session.add(session)

    db.session.commit()
