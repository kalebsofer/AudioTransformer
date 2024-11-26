# handle inference steps here
import os
import io
import torch
from pydub import AudioSegment # replace with sounde equivalenet
from minio import Minio
from transformers import WhisperProcessor, WhisperForConditionalGeneration  # WhISPER like model replace with teh right models
from .config.settings import get_settings
from AudioTransformer.backend.app.config import settings #MinIo setup

settings = get_settings() MinIo settings

#benchmark_model_path = some_path 

class TranscriptEngine:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = "benchmark_model"
        self._initialize_minio_client()
        self._initialize_resources()

    def _initialize_minio_client(self):
        self.minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
        )

    def _download_files_from_minio(self, bucket: str, prefix: str, local_dir: str):
        """Download files from MinIO only if they do not exist locally."""
        if not os.path.exists(local_dir) or not os.listdir(local_dir):
            objects = self.minio_client.list_objects(
                bucket, prefix=prefix, recursive=True
            )
            os.makedirs(local_dir, exist_ok=True)
            for obj in objects:
                file_path = os.path.join(local_dir, os.path.basename(obj.object_name))
                try:
                    response = self.minio_client.get_object(bucket, obj.object_name)
                    with open(file_path, "wb") as file_data:
                        for data in response.stream(32 * 1024):
                            file_data.write(data)
                    print(f"Downloaded {obj.object_name} to {file_path}")
                except Exception as e:
                    raise Exception(f"Error downloading {obj.object_name}: {str(e)}")

    def _initialize_resources(self):
        self._download_files_from_minio("model", "", self.model_dir)

        self.processor = WhisperProcessor.from_pretrained(
            self.model_dir, local_files_only=True
        )
        self.model = WhisperForConditionalGeneration.from_pretrained(
            self.model_dir, local_files_only=True
        )
        self.model.to(self.device)
        self.model.eval()

    def get_tarnscript(self, audio_bytes: bytes) -> str:
        audio = AudioSegment.from_wav(io.BytesIO(audio_bytes)) # CHECK FILE TYPE
        audio = audio.set_channels(1).set_frame_rate(16000)
        inputs = self.processor(audio, return_tensors="pt").unputs.to(self.device)

        with torch.no_grad():
            logits = self.model(inputs),logits
            transcripts_ids = torch.argmax(logits, dim = 1)
            transcripts = self.processor.decode(transcripts_ids[0], skip_special_tokens=True)

        return transcripts