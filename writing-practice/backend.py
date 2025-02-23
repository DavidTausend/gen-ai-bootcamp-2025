from flask import Flask, request, jsonify
import base64
import random
import sqlite3
from manga_ocr import MangaOcr
import requests
import json
from PIL import Image
import io

app = Flask(__name__)

# Initialize MangaOCR
ocr = MangaOcr()

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("study_sessions.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sentence TEXT, grade TEXT, feedback TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Mock word group database
word_groups = {
    "german_basics": {"words": ["Apfel", "Hund", "Haus", "Auto", "Buch"]}
}

@app.route("/api/groups/<group_id>/raw", methods=["GET"])
def get_word_group(group_id):
    return jsonify(word_groups.get(group_id, {}))

@app.route("/api/generate_sentence", methods=["POST"])
def generate_sentence():
    data = request.json
    word = data.get("word", "")
    prompt = f"Generate one simple English sentence that includes the German word '{word}'. Only return the sentence without any extra text or explanation."

    try:
        # Using Ollama for local LLM inference
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": prompt},
            stream=True
        )

        if response.status_code == 200:
            # Handle streamed response and parse JSON correctly
            json_lines = []
            for line in response.iter_lines():
                if line:
                    json_line = line.decode('utf-8').strip()
                    try:
                        parsed_line = json.loads(json_line)
                        json_lines.append(parsed_line)
                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON chunk: {e}")

            # Combine responses to form a single sentence
            generated_text = "".join([chunk.get("response", "") for chunk in json_lines]).strip()

            # Ensure only one sentence is returned
            generated_sentence = generated_text.split(".")[0] + "."

            return jsonify({"sentence": generated_sentence})
        else:
            error_message = response.json().get("error", "Unknown error")
            print(f"Ollama API error: {error_message}")
            return jsonify({"sentence": "Error generating response."})
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return jsonify({"error": f"JSON parsing error: {str(e)}"}), 500
    except Exception as e:
        print(f"Error in generate_sentence: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/grade_submission", methods=["POST"])
def grade_submission():
    data = request.json
    image_data = data.get("image_data", "")
    target_sentence = data.get("target_sentence", "")

    try:
        # Decode and transcribe image using MangaOCR
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        transcription = ocr(image)
        print(f"Transcription: {transcription}")

        # Use Ollama for translation
        translation_prompt = f"Translate this German text to English: {transcription}"
        translation_response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": translation_prompt}
        )

        translation_data = translation_response.json()
        translation = translation_data.get("response", "").strip()
        print(f"Translation: {translation}")

        # Use Ollama for grading
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

        # Parse grade and feedback
        grade_line = grading_output.split("\n")[0]
        grade = grade_line.split(":")[1].strip() if ":" in grade_line else "N/A"
        feedback = "\n".join(grading_output.split("\n")[1:]).strip()

        return jsonify({
            "transcription": transcription,
            "translation": translation,
            "grade": grade,
            "feedback": feedback
        })
    except Exception as e:
        print(f"Error in grade_submission: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/save_session", methods=["POST"])
def save_session():
    data = request.json
    sentence = data.get("sentence", "")
    grade = data.get("grade", "")
    feedback = data.get("feedback", "")

    try:
        conn = sqlite3.connect("study_sessions.db")
        c = conn.cursor()
        c.execute("INSERT INTO sessions (sentence, grade, feedback) VALUES (?, ?, ?)",
                  (sentence, grade, feedback))
        conn.commit()
        conn.close()
        return jsonify({"status": "saved"})
    except Exception as e:
        print(f"Error in save_session: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    try:
        conn = sqlite3.connect("study_sessions.db")
        c = conn.cursor()
        c.execute("SELECT sentence, grade, feedback FROM sessions")
        sessions = c.fetchall()
        conn.close()
        return jsonify([{"sentence": s[0], "grade": s[1], "feedback": s[2]} for s in sessions])
    except Exception as e:
        print(f"Error in get_sessions: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)