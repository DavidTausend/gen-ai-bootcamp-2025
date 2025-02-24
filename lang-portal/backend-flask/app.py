from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import base64
import requests
import json
from manga_ocr import MangaOcr
from PIL import Image
import io
import os

# Initialize MangaOCR globally
ocr = MangaOcr()

# ----------------------------
# Flask Application Factory
# ----------------------------

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Configure SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'app_data.db')
    app.config['DATABASE'] = db_path

    # Initialize the database
    init_db(db_path)

    # ----------------------------
    # Helper Functions
    # ----------------------------

    def get_db_connection():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ----------------------------
    # Routes
    # ----------------------------

    @app.route('/')
    def home():
        return "Welcome to the Unified SQLite Language Portal API!"

    # Generate Sentence Route
    @app.route("/api/generate_sentence", methods=["POST"])
    def generate_sentence():
        data = request.json
        word = data.get("word", "")
        prompt = f"Generate one simple English sentence that includes the German word '{word}'. Only return the sentence."
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": prompt},
                stream=True
            )
            if response.status_code == 200:
                generated_text = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            parsed_line = json.loads(line.decode('utf-8').strip())
                            generated_text += parsed_line.get("response", "")
                        except json.JSONDecodeError as e:
                            print(f"Skipping invalid JSON chunk: {e}")
                return jsonify({"sentence": generated_text.split('.')[0] + "."})
            else:
                error_message = response.json().get("error", "Unknown error")
                return jsonify({"error": error_message}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Grade Submission Route
    @app.route("/api/grade_submission", methods=["POST"])
    def grade_submission():
        data = request.json
        image_data = data.get("image_data", "")
        target_sentence = data.get("target_sentence", "")

        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            transcription = ocr(image)
            print(f"Transcription: {transcription}")

            translation_prompt = f"Translate this German text to English: {transcription}"
            translation_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": translation_prompt}
            )
            translation_data = translation_response.json()
            translation = translation_data.get("response", "").strip()
            print(f"Translation: {translation}")

            grading_prompt = (
                f"Grade this German writing sample:\n"
                f"Target English sentence: {target_sentence}\n"
                f"Student's German: {transcription}\n"
                f"Literal translation: {translation}\n"
                "Provide your assessment with a grade (S/A/B/C) and detailed feedback."
            )

            grading_response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": grading_prompt}
            )

            grading_data = grading_response.json()
            grading_output = grading_data.get("response", "").strip()
            grade_line = grading_output.split("\n")[0]
            grade = grade_line.split(":")[1].strip() if ":" in grade_line else "N/A"
            feedback = "\n".join(grading_output.split("\n")[1:]).strip()

            # Save grading result to SQLite
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO sessions (sentence, grade, feedback) VALUES (?, ?, ?)",
                      (target_sentence, grade, feedback))
            conn.commit()
            conn.close()

            return jsonify({
                "transcription": transcription,
                "translation": translation,
                "grade": grade,
                "feedback": feedback
            })

        except Exception as e:
            print(f"Error in grade_submission: {e}")
            return jsonify({"error": str(e)}), 500

    # Retrieve Saved Sessions
    @app.route("/api/sessions", methods=["GET"])
    def get_sessions():
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT sentence, grade, feedback FROM sessions")
            sessions = c.fetchall()
            conn.close()
            return jsonify([{"sentence": s["sentence"], "grade": s["grade"], "feedback": s["feedback"]} for s in sessions])
        except Exception as e:
            print(f"Error in get_sessions: {e}")
            return jsonify({"error": str(e)}), 500

    return app

# ----------------------------
# Database Initialization
# ----------------------------

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Create tables for words, study sessions, and grading
    c.execute('''CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    german TEXT NOT NULL,
                    english TEXT NOT NULL,
                    parts TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS word_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    created_at TEXT,
                    FOREIGN KEY(group_id) REFERENCES word_groups(id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    study_session_id INTEGER,
                    created_at TEXT,
                    FOREIGN KEY(study_session_id) REFERENCES study_sessions(id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sentence TEXT,
                    grade TEXT,
                    feedback TEXT
                )''')
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# ----------------------------
# Run the App
# ----------------------------

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)