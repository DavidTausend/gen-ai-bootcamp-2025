import requests
import sqlite3
import json
import os

# Database path
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'app_data.db')

# Helper function to connect to SQLite
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def some_service_function():
    """
    Example service function that retrieves all words from the SQLite database.
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM words")
    words = c.fetchall()
    conn.close()

    # Convert SQLite Row objects to dictionaries
    return [dict(word) for word in words]

def call_ollama_api(prompt):
    """
    Calls the Ollama API with the given prompt and handles JSON parsing errors.
    """
    url = 'http://localhost:11434/api/generate'
    payload = {
        "model": "llama2",
        "prompt": prompt
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        # Ensure response is valid JSON
        try:
            # Handle cases where multiple JSON objects might be returned
            response_json = json.loads(response.text.strip().split('\n')[0])
        except json.JSONDecodeError as json_err:
            print("JSON Decode Error:", json_err)
            print("Response Content:", response.text)
            return {"error": "Invalid JSON response from Ollama API"}

        return response_json

    except requests.exceptions.Timeout:
        print("Request to Ollama API timed out.")
        return {"error": "Request to Ollama API timed out."}

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"error": f"HTTP error occurred: {http_err}"}

    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error: {conn_err}")
        return {"error": f"Connection error: {conn_err}"}

    except requests.exceptions.RequestException as req_err:
        print(f"Request exception: {req_err}")
        return {"error": f"Request exception: {req_err}"}

def grade_submission(target_sentence, transcription):
    """
    Grades a user's submission by comparing the transcription to the target sentence using the Ollama API.
    """
    prompt = f"Grade the following transcription:\nTranscription: {transcription}\nTarget Sentence: {target_sentence}"

    api_response = call_ollama_api(prompt)

    if 'error' in api_response:
        return {"error": api_response['error']}

    # Assuming the API returns a JSON with a 'grade' field
    grade = api_response.get('grade', 'No grade returned')
    feedback = api_response.get('feedback', 'No feedback provided')

    # Save grading result to SQLite
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO sessions (sentence, grade, feedback) VALUES (?, ?, ?)",
                  (target_sentence, grade, feedback))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving grade to SQLite: {e}")

    return {
        "grade": grade,
        "feedback": feedback
    }

def get_sessions():
    """
    Retrieves all graded sessions from the SQLite database.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT sentence, grade, feedback FROM sessions")
        sessions = c.fetchall()
        conn.close()
        return [dict(s) for s in sessions]
    except Exception as e:
        print(f"Error retrieving sessions: {e}")
        return {"error": str(e)}

def generate_and_store_words(group_name, num_words=5):
    """
    Uses Ollama to generate German words and stores them in the SQLite database.
    """
    prompt = f"Generate a list of {num_words} basic German words, separated by commas."

    # Call Ollama API
    response = call_ollama_api(prompt)

    if 'error' in response:
        print(f"Ollama API Error: {response['error']}")
        return {"error": response['error']}

    # Parse generated words
    generated_text = response.get('response', "")
    if not generated_text:
        print("No response from Ollama.")
        return {"error": "No words generated from Ollama"}

    generated_words = [word.strip() for word in generated_text.split(",") if word.strip()]
    if not generated_words:
        print("Failed to parse words from Ollama response.")
        return {"error": "Failed to parse words"}

    # Insert word group and words into SQLite
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Create or get existing WordGroup
        c.execute("SELECT id FROM word_groups WHERE name = ?", (group_name,))
        group = c.fetchone()

        if not group:
            c.execute("INSERT INTO word_groups (name) VALUES (?)", (group_name,))
            group_id = c.lastrowid
            print(f"Created new word group '{group_name}' with ID {group_id}.")
        else:
            group_id = group['id']
            print(f"Using existing word group '{group_name}' with ID {group_id}.")

        # Insert generated words
        for word in generated_words:
            c.execute("INSERT INTO words (german, english, parts) VALUES (?, ?, ?)",
                      (word, "", "{}"))

        conn.commit()
        conn.close()

        print(f"Stored {len(generated_words)} words in the '{group_name}' group.")
        return {"message": f"Generated and stored {len(generated_words)} words in '{group_name}' group."}

    except Exception as e:
        print(f"Database error: {e}")
        return {"error": f"Database error: {e}"}