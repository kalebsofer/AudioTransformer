# handle back/front api here
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .audio_engine import TranscriptEngine
from .utils.img_to_minio import upload_image_to_minio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

transcript_engine = None

@app.on_event("startup")
async def startup_event():
    global transcript_engine
    transcript_engine = TranscriptEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-transcript")
async def generate_transcript(
    file: UploadFile = File(...), audio_id: str = Form(...)
) -> dict:
    if not transcript_engine:
        raise HTTPException(status_code=503, detail="Transcript engine not initialized")

    try:
        audio_bytes = await file.read()
        upload_image_to_minio(audio_bytes, audio_id)
        transcript = transcript_engine.get_caption(audio_bytes)
        return {
            "transcript": transcript,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is reachable",
        "environment": {"host": "0.0.0.0", "port": 8051},
    }