from flask import Blueprint, jsonify, request
from models import db, Word, WordGroup, StudySession, StudyActivity
from services import grade_submission, generate_sentence, transcribe_image, generate_and_store_words

api = Blueprint('api', __name__)

# ----------------------------
# Study Sessions Endpoints
# ----------------------------

@api.route('/api/dashboard/last_study_session', methods=['GET'])
def get_last_study_session():
    last_session = StudySession.query.order_by(StudySession.created_at.desc()).first()
    if last_session:
        response = {
            "id": last_session.id,
            "group_id": last_session.group_id,
            "created_at": last_session.created_at.isoformat(),
            "study_activities": [activity.id for activity in last_session.activities],
            "group_name": WordGroup.query.get(last_session.group_id).name
        }
        return jsonify(response)
    return jsonify({"error": "No study sessions found"}), 404

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
# Word Group Raw Data (NEW)
# ----------------------------

@api.route('/api/groups/<group_name>/raw', methods=['GET'])
def get_or_generate_word_group(group_name):
    from services import call_ollama_api, get_db_connection

    # Connect to the database
    conn = get_db_connection()
    c = conn.cursor()

    # Check if word group exists
    c.execute("SELECT id FROM word_groups WHERE name = ?", (group_name,))
    group = c.fetchone()

    if not group:
        # Word group not found, generate using Ollama
        print(f"Word group '{group_name}' not found. Generating using Ollama...")
        prompt = f"Generate a list of 100 basic German words."
        ollama_response = call_ollama_api(prompt)

        if 'error' in ollama_response:
            conn.close()
            return jsonify({"error": "Failed to generate words using Ollama"}), 500

        # Parse response and store in DB
        generated_words = ollama_response.get('response', "").split(",")
        # Create word group
        c.execute("INSERT INTO word_groups (name) VALUES (?)", (group_name,))
        group_id = c.lastrowid

        # Insert words into 'words' table
        for word in generated_words:
            clean_word = word.strip()
            c.execute("INSERT INTO words (german, english, parts) VALUES (?, ?, ?)",
                      (clean_word, "", "{}"))

        conn.commit()
        conn.close()

        return jsonify({"message": f"Generated and stored {len(generated_words)} words for '{group_name}'."})

    else:
        # Word group exists, fetch associated words
        group_id = group['id']
        c.execute("SELECT german, english FROM words WHERE group_id = ?", (group_id,))
        words = c.fetchall()
        conn.close()

        return jsonify([{"german": word["german"], "english": word["english"]} for word in words])

# ----------------------------
# Ollama Word Generation (NEW)
# ----------------------------

@api.route('/api/groups/<group_id>/generate_words', methods=['POST'])
def generate_words_for_group(group_id):
    """Generates words using Ollama and stores them in the database."""
    data = request.get_json()
    num_words = data.get("num_words", 100)  

    result = generate_and_store_words(group_id, num_words=num_words)

    if 'error' in result:
        return jsonify({"error": result['error']}), 500

    return jsonify(result), 200

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

        if not target_sentence or not transcription:
            return jsonify({"error": "Both 'target_sentence' and 'transcription' are required"}), 400

        result = grade_submission(target_sentence, transcription)

        if 'error' in result:
            return jsonify({"error": result['error']}), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in grade_submission: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@api.route('/api/sessions/<int:session_id>/add_grade', methods=['POST'])
def add_grade(session_id):
    data = request.get_json()
    grade = data.get('grade')

    session = StudySession.query.get_or_404(session_id)
    session.reviews += 1
    db.session.commit()

    return jsonify({"message": "Grade added successfully", "session_id": session_id})