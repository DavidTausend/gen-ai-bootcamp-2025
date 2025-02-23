import streamlit as st
import requests
import base64
import random

API_URL = "http://localhost:5000"

def fetch_word_group(group_id):
    try:
        response = requests.get(f"{API_URL}/api/groups/{group_id}/raw")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching word group: {e}")
        return {}

def generate_sentence(word):
    payload = {"word": word}
    try:
        response = requests.post(f"{API_URL}/api/generate_sentence", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("sentence", "No sentence generated.")
    except requests.exceptions.JSONDecodeError:
        st.error("Failed to parse backend response.")
        return ""
    except requests.RequestException as e:
        st.error(f"Error generating sentence: {e}")
        return ""

def grade_submission(image_data, target_sentence):
    payload = {"image_data": image_data, "target_sentence": target_sentence}
    try:
        response = requests.post(f"{API_URL}/api/grade_submission", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.JSONDecodeError:
        st.error("Failed to parse grading response.")
        return {}
    except requests.RequestException as e:
        st.error(f"Error grading submission: {e}")
        return {}

def save_study_session(sentence, grade, feedback):
    payload = {"sentence": sentence, "grade": grade, "feedback": feedback}
    try:
        response = requests.post(f"{API_URL}/api/save_session", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Error saving study session: {e}")

def main():
    st.title("Writing Practice")

    if "state" not in st.session_state:
        st.session_state.state = "setup"
        st.session_state.sentence = ""
        st.session_state.grade = ""
        st.session_state.feedback = ""

    if st.session_state.state == "setup":
        if st.button("Generate Sentence"):
            word_group = fetch_word_group("german_basics")
            words = word_group.get("words", [])
            if words:
                word = words[random.randint(0, len(words) - 1)]  # Randomly select a word
                st.session_state.sentence = generate_sentence(word)
                if st.session_state.sentence:
                    st.session_state.state = "practice"
            else:
                st.error("No words available in the word group.")

    elif st.session_state.state == "practice":
        st.write("### Write the following sentence in German:")
        st.write(f"**{st.session_state.sentence}**")
        uploaded_file = st.file_uploader("Upload your handwritten answer", type=["png", "jpg", "jpeg"])
        if uploaded_file and st.button("Submit for Review"):
            image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")
            result = grade_submission(image_data, st.session_state.sentence)
            if result:
                st.session_state.grade = result.get("grade", "N/A")
                st.session_state.feedback = result.get("feedback", "No feedback provided.")
                st.session_state.state = "review"

    elif st.session_state.state == "review":
        st.write("### Review Your Submission")
        st.write(f"**Grade:** {st.session_state.grade}")
        st.write(f"**Feedback:** {st.session_state.feedback}")
        save_study_session(st.session_state.sentence, st.session_state.grade, st.session_state.feedback)
        if st.button("Next Question"):
            st.session_state.state = "setup"
            st.session_state.sentence = ""
            st.session_state.grade = ""
            st.session_state.feedback = ""

if __name__ == "__main__":
    main()