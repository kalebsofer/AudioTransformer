# handle back/front api here
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .caption_engine import CaptionEngine
from .utils.img_to_minio import upload_image_to_minio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

caption_engine = None

@app.on_event("startup")
async def startup_event():
    global caption_engine
    caption_engine = CaptionEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-caption")
async def generate_caption(
    file: UploadFile = File(...), image_id: str = Form(...)
) -> dict:
    if not caption_engine:
        raise HTTPException(status_code=503, detail="Caption engine not initialized")

    try:
        image_bytes = await file.read()
        upload_image_to_minio(image_bytes, image_id)
        caption = caption_engine.get_caption(image_bytes)
        return {
            "caption": caption,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is reachable",
        "environment": {"host": "0.0.0.0", "port": 8051},
    }