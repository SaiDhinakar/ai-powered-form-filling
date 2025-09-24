import os
import whisper
import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# Initialize FastAPI
app = FastAPI(title="Speech-to-Text API", description="Whisper + FastAPI", version="1.0")

# Load Whisper model (choose "small", "medium", or "large")
device = "cpu"
model = whisper.load_model("small", device=device)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_location = f"{file.filename}"
        with open(file_location, "wb+") as f:
            f.write(await file.read())

        # Transcribe using Whisper
        result = model.transcribe(file_location)

        # Cleanup (optional: delete file after processing)
        os.remove(file_location)

        return JSONResponse(content={"text": result["text"]})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
