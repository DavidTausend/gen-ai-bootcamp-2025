# Create a Virtual Environment 

python -m venv venv
source venv/bin/activate 

pip install streamlit flask openai manga-ocr requests pillow

# Run Ollama

ollama serve

# Verify ollama serve is running

curl http://127.0.0.1:11434

#  Run the Backend (Flask)

python backend.py

# Run the Frontend (Streamlit)

streamlit run frontend.py