from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from .transcription_engine import TranscriptionEngine
from .utils.audio_to_minio import upload_audio_to_minio
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transcription_engine = None

@app.on_event("startup")
async def startup_event():
    global transcription_engine
    start_time = time.time()
    transcription_engine = TranscriptionEngine()
    end_time = time.time()
    print(f"TranscriptionEngine initialized in {end_time - start_time:.4f} seconds")

@app.get("/health")
async def health_check():
    if transcription_engine is None:
        return {"status": "unhealthy", "message": "TranscriptionEngine not initialized"}
    return {"status": "healthy"}

@app.post("/generate-transcription")
async def generate_transcription(
    audio_file: UploadFile = File(...), audio_id: str = Form(...)
) -> dict:

    if not transcription_engine:
        print("TranscriptionEngine not initialized")
        raise HTTPException(
            status_code=500, detail="TranscriptionEngine not initialized"
        )

    try:
        start_time = time.time()
        audio_bytes = await audio_file.read()
        file_extension = audio_file.filename.split(".")[-1]

        upload_start_time = time.time()
        upload_audio_to_minio(audio_bytes, audio_id, file_extension)
        upload_end_time = time.time()
        print(
            f"Audio uploaded to MinIO in {upload_end_time - upload_start_time:.4f} seconds"
        )

        transcript_start_time = time.time()
        transcript = transcription_engine.get_transcript(audio_bytes)
        transcript_end_time = time.time()
        print(
            f"Transcription generated in {transcript_end_time - transcript_start_time:.4f} seconds"
        )

        end_time = time.time()
        print(f"Total request processing time: {end_time - start_time:.4f} seconds")

        return {"transcript": transcript}
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is reachable",
        "environment": {"host": "0.0.0.0", "port": 8051},
    }
