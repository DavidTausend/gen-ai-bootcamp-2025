from fastapi import FastAPI
from integrations.gptsovits import OpeaGptsovitsTts
from integrations.speecht5 import OpeaSpeecht5Tts
from fastapi.responses import StreamingResponse
import io

# Initialize FastAPI app
app = FastAPI()

gptsovits_tts = OpeaGptsovitsTts()
speecht5_tts = OpeaSpeecht5Tts()

@app.post("/synthesize/")
def synthesize_speech(text: str, model: str = "gptsovits"):
    """Generates speech from text using OPEA-supported TTS models."""
    try:
        if model == "gptsovits":
            audio_data = gptsovits_tts.synthesize(text)
        elif model == "speecht5":
            audio_data = speecht5_tts.synthesize(text)
        else:
            return {"error": "Invalid model selection. Choose 'gptsovits' or 'speecht5'."}

        audio_stream = io.BytesIO(audio_data)
        return StreamingResponse(audio_stream, media_type="audio/wav")
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
