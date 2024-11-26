from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .transcription_engine import TranscriptionEngine
from .utils.audio_to_minio import upload_audio_to_minio

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
    transcription_engine = TranscriptionEngine()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-transcription")
async def generate_transcription(
    file: UploadFile = File(...), audio_id: str = Form(...)
) -> dict:
    if not transcription_engine:
        raise HTTPException(
            status_code=503, detail="Transcription engine not initialized"
        )

    try:
        audio_bytes = await file.read()
        upload_audio_to_minio(audio_bytes, audio_id, file.filename.split(".")[-1])
        transcription = transcription_engine.get_transcript(audio_bytes)
        return {
            "transcription": transcription,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is reachable",
        "environment": {"host": "0.0.0.0", "port": 8051},
    }
