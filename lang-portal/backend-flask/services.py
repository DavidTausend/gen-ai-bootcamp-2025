import requests
from models import db, Word
import json

def some_service_function():
    # Example service function that retrieves all words
    words = Word.query.all()
    return words

def call_ollama_api(prompt):
    """
    Calls the Ollama API with the given prompt and handles JSON parsing errors.
    """
    url = 'http://localhost:11434/api/generate'
    payload = {
        "model": "your-model-name",  # Replace with your actual model name
        "prompt": prompt
    }

    try:
        response = requests.post(url, json=payload)

        # Check for HTTP errors
        response.raise_for_status()

        # Handle potential multiple JSON objects in the response
        try:
            response_json = json.loads(response.text.strip().split('\n')[0])  # Parse only the first JSON object
        except json.JSONDecodeError as json_err:
            print("JSON Decode Error:", json_err)
            print("Response Content:", response.text)
            return {"error": "Invalid JSON response from Ollama API"}

        return response_json

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"error": f"HTTP error occurred: {http_err}"}

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

    return {
        "grade": grade,
        "feedback": feedback
    }