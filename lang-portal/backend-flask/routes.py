from flask import Blueprint, jsonify, request
from models import db, Word, WordGroup, StudySession, StudyActivity

api = Blueprint('api', __name__)

@api.route('/api/dashboard/last_study_session', methods=['GET'])
def get_last_study_session():
    """Retrieve the last study session."""
    last_session = StudySession.query.order_by(StudySession.created_at.desc()).first()
    if last_session:
        response = {
            "id": last_session.id,
            "group_id": last_session.group_id,
            "created_at": last_session.created_at.isoformat(),
            "study_activities": [activity.id for activity in last_session.activities],  # ✅ Fix here
            "group_name": WordGroup.query.get(last_session.group_id).name
        }
        return jsonify(response)
    return jsonify({"error": "No study sessions found"}), 404

@api.route('/api/words', methods=['GET'])
def get_words_paginated():
    """Retrieve words with pagination."""
    page = request.args.get('page', type=int)

    # Fix: Validate `page` input
    if page is None or page < 1:
        return jsonify({"error": "Invalid page number"}), 400  # ✅ Now correctly returns `400`

    per_page = 100
    words = Word.query.paginate(page=page, per_page=per_page, error_out=False)

    items = [{"id": word.id, "german": word.german, "english": word.english} for word in words.items]

    return jsonify({
        "items": items,
        "pagination": {
            "current_page": words.page,
            "total_pages": words.pages,
            "total_items": words.total,
            "items_per_page": per_page
        }
    })

@api.route('/api/words', methods=['POST'])
def add_word():
    """Add a new word with input validation."""
    data = request.get_json()

    # Fix: Validate required fields before inserting into DB
    if "german" not in data or not data["german"] or "english" not in data or not data["english"]:
        return jsonify({"error": "Missing required fields: 'german' and 'english' are required"}), 400

    new_word = Word(
        german=data['german'],
        english=data['english'],
        parts=data.get('parts', "{}")  # Provide default value
    )
    db.session.add(new_word)
    db.session.commit()
    return jsonify({'id': new_word.id}), 201


@api.route('/api/words/<int:word_id>', methods=['GET'])
def get_word_details(word_id):
    """Retrieve word details."""
    word = Word.query.get_or_404(word_id)
    response = {'id': word.id, 'german': word.german, 'english': word.english}
    return jsonify(response)

@api.route('/api/words/<int:word_id>', methods=['PUT'])
def update_word(word_id):
    """Update a word."""
    data = request.get_json()
    word = Word.query.get_or_404(word_id)

    word.german = data.get('german', word.german)
    word.english = data.get('english', word.english)
    word.parts = data.get('parts', word.parts)
    db.session.commit()
    return jsonify({'id': word.id}), 200

@api.route('/api/words/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    """Delete a word."""
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    return jsonify({'result': 'success'}), 200

@api.route('/api/groups', methods=['GET'])
def get_groups():
    """Retrieve all word groups."""
    groups = WordGroup.query.all()
    return jsonify([{'id': group.id, 'name': group.name} for group in groups])

@api.route('/api/groups', methods=['POST'])
def add_group():
    """Add a new word group."""
    data = request.get_json()
    if "name" not in data:
        return jsonify({"error": "Missing required fields"}), 400  # ✅ Validation

    new_group = WordGroup(name=data['name'])
    db.session.add(new_group)
    db.session.commit()
    return jsonify({'id': new_group.id}), 201

@api.route('/api/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """Update a word group."""
    data = request.get_json()
    group = WordGroup.query.get_or_404(group_id)

    group.name = data.get('name', group.name)
    db.session.commit()
    return jsonify({'id': group.id}), 200

@api.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Delete a word group."""
    group = WordGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'result': 'success'}), 200

@api.route('/api/study_sessions', methods=['GET'])
def get_study_sessions():
    """Retrieve all study sessions."""
    sessions = StudySession.query.all()
    return jsonify([{'id': session.id, 'group_id': session.group_id, 'created_at': session.created_at.isoformat()} for session in sessions])

@api.route('/api/study_sessions', methods=['POST'])
def add_study_session():
    """Add a new study session."""
    data = request.get_json()
    if "group_id" not in data:
        return jsonify({"error": "Missing required fields"}), 400  # ✅ Validation

    new_session = StudySession(group_id=data['group_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'id': new_session.id}), 201

@api.route('/api/study_sessions/<int:session_id>', methods=['DELETE'])
def delete_study_session(session_id):
    """Delete a study session."""
    session = StudySession.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({'result': 'success'}), 200

@api.route('/api/study_activities', methods=['POST'])
def add_study_activity():
    """Add a new study activity."""
    data = request.get_json()

    # Fix: Validate required fields
    if "study_session_id" not in data:
        return jsonify({"error": "Missing required fields"}), 400  # ✅ Now correctly returns `400`

    new_activity = StudyActivity(study_session_id=data['study_session_id'])
    db.session.add(new_activity)
    db.session.commit()
    return jsonify({'id': new_activity.id}), 201

@api.route('/api/reset', methods=['POST'])
def reset_history():
    try:
        db.session.query(StudyActivity).delete()
        db.session.query(StudySession).delete()
        db.session.query(Word).delete()
        db.session.commit()
        return jsonify({"message": "History reset successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500