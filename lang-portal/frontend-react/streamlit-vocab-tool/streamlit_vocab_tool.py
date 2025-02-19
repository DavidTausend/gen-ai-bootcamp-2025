import streamlit as st
import json
import requests
from io import StringIO
import os
import time
import re

# Read API Key from environment variable
LLM_API_KEY = os.getenv("LLM_API_KEY")

# Function to clean LLM response and extract JSON
def extract_json(text):
    try:
        # Attempt to parse JSON directly
        return json.loads(text)
    except json.JSONDecodeError as e:
        st.warning(f"Initial JSON Decode Error: {e}")

        # Clean up escape characters and attempt extraction
        cleaned_text = text.replace('\n', '').replace('\\', '').replace('\\"', '"')
        json_match = re.search(r'(\[.*\]|\{.*\})', cleaned_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e2:
                st.error(f"JSON Decode Error after cleaning: {e2}")
                return None
        return None

# Function to call LLM API for vocabulary generation with retry logic
def generate_vocab(category, retries=3, delay=2):
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Updated prompt to enforce clean, human-readable JSON
    prompt = (
        f"Generate a list of 4 German vocabulary words for the category '{category}' in the following JSON format:\n\n"
        "[\n"
        "  {\n"
        "    \"german\": \"Haus\",\n"
        "    \"pronunciation\": \"haus\",\n"
        "    \"english\": \"house\",\n"
        "    \"parts\": [\n"
        "      { \"letter\": \"H\", \"sound\": [\"h\"] },\n"
        "      { \"letter\": \"a\", \"sound\": [\"a\"] },\n"
        "      { \"letter\": \"u\", \"sound\": [\"u\"] },\n"
        "      { \"letter\": \"s\", \"sound\": [\"s\"] }\n"
        "    ]\n"
        "  }\n"
        "]\n\n"
        "ONLY return the JSON array without any escape characters or extra formatting. Make sure the JSON is clean, valid, and human-readable."
    )

    # Payload with the new prompt
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are an assistant that generates structured German vocabulary."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    # Log the payload for debugging
    st.write("Sending payload:", payload)

    for attempt in range(retries):
        try:
            response = requests.post(api_url, json=payload, headers=headers)

            # Log response for debugging
            st.write("API Response Status Code:", response.status_code)
            st.write("API Response Content:", response.text)

            if response.status_code == 200:
                # Extract and clean the response content
                response_json = response.json()
                generated_text = response_json["choices"][0]["message"]["content"]
                vocab_json = extract_json(generated_text)
                if vocab_json:
                    return vocab_json
                else:
                    st.error("Failed to extract valid JSON from the response.")
                    return []
            elif response.status_code == 503:
                st.warning(f"503 Service Unavailable. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                st.error(f"Failed to generate vocabulary. Status Code: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            st.error(f"Error during API request: {e}")
            return []

    st.error("Failed to generate vocabulary after multiple attempts.")
    return []

# Function to list available models from the Groq API
def list_models():
    api_url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        st.write("Models List Status Code:", response.status_code)
        if response.status_code == 200:
            models = response.json()
            st.subheader("Available Models")
            st.json(models)
        else:
            st.error(f"Failed to fetch model list. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching model list: {e}")

# Streamlit App
st.title("Vocabulary Language Importer")

# Section to list available models
if st.button("List Available Models"):
    list_models()

# Input for thematic category
category = st.text_input("Enter thematic category:")

if st.button("Generate Vocabulary"):
    if category:
        vocab = generate_vocab(category)
        if vocab:
            st.session_state["vocab"] = vocab
            st.success("Vocabulary generated successfully!")
        else:
            st.error("No vocabulary generated.")
    else:
        st.error("Please enter a category.")

# Display generated vocabulary
if "vocab" in st.session_state and st.session_state["vocab"]:
    st.subheader("Generated Vocabulary")
    st.json(st.session_state["vocab"])

    # Export to JSON
    vocab_json = json.dumps(st.session_state["vocab"], indent=2)
    st.download_button(
        label="Download Vocabulary as JSON",
        data=vocab_json,
        file_name="vocabulary.json",
        mime="application/json"
    )

# Import JSON file
st.subheader("Import Vocabulary JSON")
uploaded_file = st.file_uploader("Choose a JSON file", type="json")
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    imported_vocab = json.load(stringio)
    st.session_state["vocab"] = imported_vocab
    st.success("Vocabulary imported successfully!")
    st.json(imported_vocab)