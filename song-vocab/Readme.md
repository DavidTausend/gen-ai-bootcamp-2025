# Donwload and Install Ollam for mac

https://ollama.com/download

# Download model

ollama run mistral

## Activate python environment

python3 -m venv venv

source venv/bin/activate 


## Install requirements

pip install -r requirements.txt

## Run the app

uvicorn main:app --host 0.0.0.0 --port 8000

## Get lycrics song

python3 serp-tool-test.py

Response:
[{'title': '99 Luftballons', 'url': 'https://westmusiker.de/wp-content/uploads/2020/08/Liedtext.pdf', 'snippet': '99 Luftballons. Nena. Hast Du etwas Zeit für mich. Dann singe ich ein Lied fuer Dich. Von 99 Luftballons. Auf ihrem Weg zum Horizont. Denkst Du vielleicht grad ...'}, {'title': '99 Luftballons Songtext von Nena', 'url': 'https://www.songtexte.com/songtext/nena/99-luftballons-63dcfa57.html', 'snippet': 'Hast du etwas Zeit für mich? Dann singe ich ein Lied für dich. Von neunundneunzig Luftballons Auf ihrem Weg zum Horizont Denkst du vielleicht grad an mich?'}, {'title': 'Nena – 99 Luftballons Lyrics', 'url': 'https://genius.com/Nena-99-luftballons-lyrics', 'snippet': '[Songtext zu „99 Luftballons“] [Strophe 1] Hast du etwas Zeit für mich? Dann singe ich ein Lied für dich. Von 99 Luftballons Auf ihrem Weg zum Horizont'}, {'title': 'NENA: 99 LUFTBALLONS', 'url': 'https://www.zebis.ch/sites/default/files/teaching_material/nena_99_luftballons.pdf', 'snippet': "Hast Du etwas Zeit für mich dann singe ich ein Lied für dich von 99 Luftballons auf ihrem Weg zum Horizont. Denkst Du vielleicht grad' an mich."}]