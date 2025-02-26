import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import nest_asyncio
import asyncio

# Apply nest_asyncio to allow nested loops
nest_asyncio.apply()

# Fix for Torch Event Loop Issue
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
from backend.chat import LocalChat
from backend.get_transcript import get_youtube_transcript
from gtts import gTTS  # Google Text-to-Speech
import base64

# Initialize LocalChat with RAG integration
local_chat = LocalChat(
    embedding_model_name='paraphrase-multilingual-MiniLM-L12-v2',
    text_gen_model_name='microsoft/DialoGPT-medium'
)

# Streamlit App
st.title("🇩🇪 German Language Learning Assistant")

# 🎬 YouTube Transcript Retrieval and RAG Storage
video_url = st.text_input("Enter YouTube Video URL for German Lessons:")
if video_url:
    transcript, error = get_youtube_transcript(video_url, language='de')
    if error:
        st.error(f"🚫 Error retrieving transcript: {error}")
    else:
        st.write("📄 Transcript:", transcript)

        # Process and Embed Transcript into RAG
        for idx, entry in enumerate(transcript):
            text = entry['text']
            doc_id = f"{video_url}_segment_{idx}"
            local_chat.add_to_rag(text, doc_id)
        st.success("✅ Transcript processed and stored in RAG.")

# 🔍 RAG Query Integration
query = st.text_input("💬 Ask a question about the German lesson:")
if query:
    # Query RAG for relevant documents
    rag_results = local_chat.query_rag(query)

    if rag_results and rag_results['documents'][0]:
        st.write("📚 Relevant Documents:")
        for doc, metadata in zip(rag_results['documents'][0], rag_results['metadatas'][0]):
            st.write(f"**Source:** {metadata['source']}")
            st.write(f"**Content:** {doc}")

        # 🧠 Generate Answer using DialoGPT
        combined_context = "\n".join(rag_results['documents'][0])
        response = local_chat.generate_response(f"{combined_context}\n\nUser: {query}")
        st.write("🤖 AI Response:", response)

        # 🔊 Generate Audio for Question
        tts_question = gTTS(text=query, lang="de")
        question_audio_path = "question_audio.mp3"
        tts_question.save(question_audio_path)

        # 🔊 Generate Audio for Answer
        tts_answer = gTTS(text=response, lang="de")
        answer_audio_path = "answer_audio.mp3"
        tts_answer.save(answer_audio_path)

        # Function to encode audio files for Streamlit playback
        def get_audio_base64(file_path):
            with open(file_path, "rb") as audio_file:
                encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")
            return f"data:audio/mp3;base64,{encoded_audio}"

        # Display audio buttons
        st.write("🎤 **Listen to the Question:**")
        st.audio(get_audio_base64(question_audio_path), format="audio/mp3")

        st.write("🎤 **Listen to the Answer:**")
        st.audio(get_audio_base64(answer_audio_path), format="audio/mp3")

    else:
        st.warning("⚠️ No relevant documents found in RAG.")