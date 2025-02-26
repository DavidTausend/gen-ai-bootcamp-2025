from flask import Blueprint, jsonify, request
from models import db, Word, WordGroup, StudySession, StudyActivity
from services import grade_submission, generate_sentence, transcribe_image, generate_and_store_words

api = Blueprint('api', __name__)

# ----------------------------
# Dashboard Endpoint
# ----------------------------

@api.route('/api/dashboard/last_study_session', methods=['GET'])
def get_last_study_session():
    last_session = StudySession.query.order_by(StudySession.created_at.desc()).first()
    if last_session:
        response = {
            "id": last_session.id,
            "group_id": last_session.group_id,
            "created_at": last_session.created_at.isoformat(),
            "study_activities": [{
                "id": activity.id,
                "transcription": activity.transcription,
                "grade": activity.grade,
                "feedback": activity.feedback
            } for activity in last_session.activities],
            "group_name": WordGroup.query.get(last_session.group_id).name
        }
        return jsonify(response)
    return jsonify({"error": "No study sessions found"}), 404

# ----------------------------
# Study Sessions Endpoints
# ----------------------------

@api.route('/api/study_sessions', methods=['GET'])
def get_study_sessions():
    sessions = StudySession.query.all()
    return jsonify([{
        'id': session.id,
        'group_id': session.group_id,
        'created_at': session.created_at.isoformat()
    } for session in sessions])

@api.route('/api/study_sessions', methods=['POST'])
def add_study_session():
    data = request.get_json()
    if "group_id" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_session = StudySession(group_id=data['group_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'id': new_session.id}), 201

@api.route('/api/study_sessions/<int:session_id>', methods=['DELETE'])
def delete_study_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({'result': 'success'}), 200

# ----------------------------
# Study Activities Endpoints
# ----------------------------

@api.route('/api/study_activities', methods=['GET'])
def get_study_activities():
    activities = StudyActivity.query.all()
    response = []
    for activity in activities:
        response.append({
            "id": activity.id,
            "session_id": activity.session_id,
            "created_at": activity.created_at.isoformat(),
            "transcription": activity.transcription,
            "grade": activity.grade,
            "feedback": activity.feedback
        })
    return jsonify(response), 200

# ----------------------------
# Words Endpoints
# ----------------------------

@api.route('/api/words', methods=['GET'])
def get_words_paginated():
    page = request.args.get('page', type=int)
    if page is None or page < 1:
        return jsonify({"error": "Invalid page number"}), 400

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
    data = request.get_json()
    if "german" not in data or not data["german"] or "english" not in data or not data["english"]:
        return jsonify({"error": "Missing required fields: 'german' and 'english' are required"}), 400

    new_word = Word(
        german=data['german'],
        english=data['english'],
        parts=data.get('parts', "{}")
    )
    db.session.add(new_word)
    db.session.commit()
    return jsonify({'id': new_word.id}), 201

@api.route('/api/words/<int:word_id>', methods=['GET'])
def get_word_details(word_id):
    word = Word.query.get_or_404(word_id)
    return jsonify({'id': word.id, 'german': word.german, 'english': word.english})

@api.route('/api/words/<int:word_id>', methods=['PUT'])
def update_word(word_id):
    data = request.get_json()
    word = Word.query.get_or_404(word_id)

    word.german = data.get('german', word.german)
    word.english = data.get('english', word.english)
    word.parts = data.get('parts', word.parts)
    db.session.commit()
    return jsonify({'id': word.id}), 200

@api.route('/api/words/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    return jsonify({'result': 'success'}), 200

# ----------------------------
# Word Groups Endpoints
# ----------------------------

@api.route('/api/groups', methods=['GET'])
def get_groups():
    groups = WordGroup.query.all()
    return jsonify([{'id': group.id, 'name': group.name} for group in groups])

@api.route('/api/groups', methods=['POST'])
def add_group():
    data = request.get_json()
    if "name" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_group = WordGroup(name=data['name'])
    db.session.add(new_group)
    db.session.commit()
    return jsonify({'id': new_group.id}), 201

@api.route('/api/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    data = request.get_json()
    group = WordGroup.query.get_or_404(group_id)

    group.name = data.get('name', group.name)
    db.session.commit()
    return jsonify({'id': group.id}), 200

@api.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    group = WordGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify({'result': 'success'}), 200

# ----------------------------
# Sentence Generation & OCR Endpoints
# ----------------------------

@api.route('/api/generate_sentence', methods=['POST'])
def api_generate_sentence():
    data = request.get_json()
    word = data.get("word", "")
    response = generate_sentence(word)
    return jsonify(response)

@api.route('/api/transcribe_image', methods=['POST'])
def api_transcribe_image():
    data = request.get_json()
    image_data = data.get("image_data", "")
    response = transcribe_image(image_data)
    return jsonify(response)

# ----------------------------
# Grading and Submission Endpoints
# ----------------------------

@api.route('/api/grade_submission', methods=['POST'])
def grade_submission_route():
    try:
        data = request.get_json(force=True)
        target_sentence = data.get('target_sentence')
        transcription = data.get('transcription')
        session_id = data.get('session_id')

        if not target_sentence or not transcription or not session_id:
            return jsonify({"error": "Fields 'target_sentence', 'transcription', and 'session_id' are required"}), 400

        # Call grading service
        result = grade_submission(target_sentence, transcription)

        if 'error' in result:
            return jsonify({"error": result['error']}), 500

        # Save to StudyActivity
        new_activity = StudyActivity(
            session_id=session_id,
            transcription=transcription,
            grade=result.get('grade'),
            feedback=result.get('feedback')
        )
        db.session.add(new_activity)
        db.session.commit()

        return jsonify({
            "message": "Submission graded and saved.",
            "activity_id": new_activity.id,
            "grade": result.get('grade'),
            "feedback": result.get('feedback')
        }), 200

    except Exception as e:
        print(f"Error in grade_submission: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# ----------------------------
# Add Grade to Existing Session
# ----------------------------

@api.route('/api/sessions/<int:session_id>/add_grade', methods=['POST'])
def add_grade(session_id):
    data = request.get_json()
    grade = data.get('grade')

    session = StudySession.query.get_or_404(session_id)
    session.reviews += 1
    db.session.commit()

    return jsonify({"message": "Grade added successfully", "session_id": session_id})