from flask import Flask, request, jsonify
import base64
import random
import sqlite3
import pytesseract
from PIL import Image
import io
import requests
import json
import ast
import re

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("study_sessions.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sentence TEXT, grade TEXT, feedback TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Fetch word group from Ollama API
import re  # Import regex for cleaning

@app.route("/api/groups/<group_id>/raw", methods=["GET"])
def get_word_group(group_id):
    prompt = f"Generate a list of 5 basic German words suitable for beginners in the category '{group_id}'. Only return the list in JSON format."
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": prompt},
            stream=True
        )

        if response.status_code == 200:
            json_lines = []
            for line in response.iter_lines():
                if line:
                    json_line = line.decode('utf-8').strip()
                    try:
                        parsed_line = json.loads(json_line)
                        json_lines.append(parsed_line)
                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON chunk: {e}")

            generated_text = "".join([chunk.get("response", "") for chunk in json_lines]).strip()

            # Debug: Print the raw generated text
            print(f"Raw Generated Text: {generated_text}")

            # Clean the generated text
            cleaned_text = re.sub(r'//.*', '', generated_text)  # Remove comments
            cleaned_text = re.sub(r',\s*([\]}])', r'\1', cleaned_text)  # Remove trailing commas

            # Debug: Print the cleaned text
            print(f"Cleaned Generated Text: {cleaned_text}")

            # Safely parse cleaned text
            try:
                parsed_json = json.loads(cleaned_text)
                word_list = parsed_json.get(group_id, [])
                if not isinstance(word_list, list):
                    raise ValueError("Parsed word list is not a list")
            except (ValueError, SyntaxError, json.JSONDecodeError) as e:
                print(f"Error parsing cleaned word list: {e}")
                return jsonify({"words": [], "error": "Failed to parse cleaned word list."}), 500

            return jsonify({"words": word_list})
        else:
            error_message = response.json().get("error", "Unknown error")
            print(f"Ollama API error: {error_message}")
            return jsonify({"words": [], "error": error_message}), 500
    except Exception as e:
        print(f"Error in get_word_group: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate_sentence", methods=["POST"])
def generate_sentence():
    data = request.json
    word = data.get("word", "")
    prompt = f"Generate one simple English sentence that includes the German word '{word}'. Only return the sentence without any extra text or explanation."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": prompt},
            stream=True
        )

        if response.status_code == 200:
            json_lines = []
            for line in response.iter_lines():
                if line:
                    json_line = line.decode('utf-8').strip()
                    try:
                        parsed_line = json.loads(json_line)
                        json_lines.append(parsed_line)
                    except json.JSONDecodeError as e:
                        print(f"Skipping invalid JSON chunk: {e}")

            generated_text = "".join([chunk.get("response", "") for chunk in json_lines]).strip()
            generated_sentence = generated_text.split(".")[0] + "."
            return jsonify({"sentence": generated_sentence})
        else:
            error_message = response.json().get("error", "Unknown error")
            print(f"Ollama API error: {error_message}")
            return jsonify({"sentence": "Error generating response."}), 500
    except Exception as e:
        print(f"Error in generate_sentence: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/grade_submission", methods=["POST"])
def grade_submission():
    data = request.json
    image_data = data.get("image_data", "")
    target_sentence = data.get("target_sentence", "")

    try:
        # Transcribe the image using pytesseract
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        transcription = pytesseract.image_to_string(image, lang='eng').strip()
        print(f"Transcription: {transcription}")

        # Translate the transcription
        translation_prompt = f"Translate this German text to English: {transcription}"
        translation_response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": translation_prompt}
        )

        translation_text = ""
        for line in translation_response.iter_lines():
            if line:
                try:
                    parsed_line = json.loads(line.decode('utf-8').strip())
                    translation_text += parsed_line.get("response", "")
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON in translation: {e}")

        translation = translation_text.strip()
        print(f"Translation: {translation}")

        # Grade the submission
        grading_prompt = (
            f"Grade this German writing sample:\n"
            f"Target English sentence: {target_sentence}\n"
            f"Student's German: {transcription}\n"
            f"Literal translation: {translation}\n"
            "Provide your assessment with a grade (S/A/B/C) and detailed feedback."
        )

        grading_response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": grading_prompt},
            stream=True
        )

        grading_text = ""
        for line in grading_response.iter_lines():
            if line:
                try:
                    parsed_line = json.loads(line.decode('utf-8').strip())
                    grading_text += parsed_line.get("response", "")
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON in grading: {e}")

        grading_output = grading_text.strip()
        grade_line = grading_output.split("\n")[0]
        grade = grade_line.split(":")[1].strip() if ":" in grade_line else "N/A"
        feedback = "\n".join(grading_output.split("\n")[1:]).strip()

        # Save the graded session
        conn = sqlite3.connect("study_sessions.db")
        c = conn.cursor()
        c.execute("INSERT INTO sessions (sentence, grade, feedback) VALUES (?, ?, ?)",
                  (target_sentence, grade, feedback))
        conn.commit()
        conn.close()
        print("Session saved successfully.")

        # Return the response
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
        c.execute("SELECT id, sentence, grade, feedback FROM sessions ORDER BY id DESC")
        sessions = c.fetchall()
        conn.close()

        # Format sessions for frontend
        formatted_sessions = [{
            "id": s[0],
            "sentence": s[1],
            "grade": s[2],
            "feedback": s[3]
        } for s in sessions]

        return jsonify(formatted_sessions)
    except Exception as e:
        print(f"Error in get_sessions: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)