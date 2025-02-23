from flask import Flask, request, jsonify
import base64
import random
import sqlite3
from manga_ocr import MangaOcr
import requests

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

# Function to interact with Ollama's REST API
def run_ollama(prompt, model="llama2"):
    try:
        url = "http://127.0.0.1:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Clean response to remove extra explanations or translations
        raw_response = data.get("response", "").strip()
        
        # Extract the first sentence or main output
        cleaned_response = raw_response.split("\n")[0]  # Get the first line only
        
        return cleaned_response
    except requests.exceptions.RequestException as e:
        print(f"Ollama API error: {e}")
        return "Error generating response."

@app.route("/api/groups/<group_id>/raw", methods=["GET"])
def get_word_group(group_id):
    return jsonify(word_groups.get(group_id, {}))

@app.route("/api/generate_sentence", methods=["POST"])
def generate_sentence():
    data = request.json
    word = data.get("word", "")
    prompt = f"Generate a simple German sentence using the word '{word}'."

    try:
        print(f"Generating sentence for word: {word}")

        # Use Ollama API to generate the sentence
        response = run_ollama(prompt)
        print(f"Generated sentence: {response}")
        return jsonify({"sentence": response})
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
        transcription = ocr(image_bytes)
        print(f"Transcription: {transcription}")

        # Use Ollama API for translation
        translation_prompt = f"Translate this German text to English: {transcription}"
        translation = run_ollama(translation_prompt)
        print(f"Translation: {translation}")

        # Use Ollama API for grading
        grading_prompt = (
            f"Grade this German writing sample:\n"
            f"Target English sentence: {target_sentence}\n"
            f"Student's German: {transcription}\n"
            f"Literal translation: {translation}\n"
            "Provide your assessment with a grade (S/A/B/C) and detailed feedback."
        )
        grading_response = run_ollama(grading_prompt)
        print(f"Grading Response: {grading_response}")

        # Simple parsing (improve with regex or structured output if needed)
        grade = "N/A"
        feedback = grading_response
        for line in grading_response.split("\n"):
            if "Grade:" in line:
                grade = line.split(":")[1].strip()

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