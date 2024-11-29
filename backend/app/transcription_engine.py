import os
import io
import time
import tracemalloc
import torch
import librosa
from minio import Minio
from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline
from .config.settings import get_settings

settings = get_settings()


class TranscriptionEngine:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = "/model"
        self._initialize_minio_client()
        self._initialize_resources()

    def _initialize_minio_client(self):
        start_time = time.time()
        tracemalloc.start()

        self.minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
        )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.time()

        print(
            f"_initialize_minio_client - Time: {end_time - start_time:.4f}s, "
            f"Current Memory: {current / 10**6:.2f}MB, Peak Memory: {peak / 10**6:.2f}MB"
        )

    def _download_files_from_minio(self, bucket: str, prefix: str, local_dir: str):
        start_time = time.time()
        tracemalloc.start()

        if not os.path.exists(local_dir) or not os.listdir(local_dir):
            objects = self.minio_client.list_objects(
                bucket, prefix=prefix, recursive=True
            )
            os.makedirs(local_dir, exist_ok=True)
            for obj in objects:
                if obj.object_name.startswith(".minio.sys") or "/" in obj.object_name:
                    continue
                file_path = os.path.join(local_dir, os.path.basename(obj.object_name))
                try:
                    response = self.minio_client.get_object(bucket, obj.object_name)
                    with open(file_path, "wb") as file_data:
                        for data in response.stream(32 * 1024):
                            file_data.write(data)
                except Exception as e:
                    raise Exception(f"Error downloading {obj.object_name}: {str(e)}")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.time()

        print(
            f"_download_files_from_minio - Time: {end_time - start_time:.4f}s, "
            f"Current Memory: {current / 10**6:.2f}MB, Peak Memory: {peak / 10**6:.2f}MB"
        )

    def _initialize_resources(self):
        start_time = time.time()
        tracemalloc.start()

        self._download_files_from_minio("model", "", self.model_dir)

        self.processor = WhisperProcessor.from_pretrained(
            self.model_dir, local_files_only=True
        )
        self.model = WhisperForConditionalGeneration.from_pretrained(
            self.model_dir, local_files_only=True
        )

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            device=self.device,
        )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.time()

        print(
            f"_initialize_resources - Time: {end_time - start_time:.4f}s, "
            f"Current Memory: {current / 10**6:.2f}MB, Peak Memory: {peak / 10**6:.2f}MB"
        )

    def get_transcript(self, audio_bytes: bytes) -> str:
        start_time = time.time()
        tracemalloc.start()

        try:
            audio_array, sampling_rate = librosa.load(io.BytesIO(audio_bytes), sr=16000)

            transcription = self.pipe(audio_array)["text"]

            return transcription

        except Exception as e:
            print(f"Error in get_transcript: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")

        finally:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            end_time = time.time()

            print(
                f"get_transcript - Time: {end_time - start_time:.4f}s, "
                f"Current Memory: {current / 10**6:.2f}MB, Peak Memory: {peak / 10**6:.2f}MB"
            )
