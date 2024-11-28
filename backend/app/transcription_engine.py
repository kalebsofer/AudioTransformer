import os
import io
import torch
from minio import Minio
from transformers import AutoModelForSpeechSeq2Seq, WhisperProcessor
from .config.settings import get_settings
import librosa


settings = get_settings()


class TranscriptionEngine:
    def __init__(self, use_minio=False):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = "local_model/benchmark"
        self.use_minio = use_minio
        if self.use_minio:
            self._initialize_minio_client()
        try:
            self._initialize_resources()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize resources: {str(e)}")

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
        try:
            # Check if model files exist locally
            if self.use_minio:
                if not os.path.exists(self.model_dir) or not os.listdir(self.model_dir):
                    self._download_files_from_minio("model", "", self.model_dir)

            self.processor = WhisperProcessor.from_pretrained(
                self.model_dir, local_files_only=True
            )
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_dir, local_files_only=True
            )
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"Error initializing resources: {str(e)}")

    def get_transcript(self, audio_bytes: bytes) -> str:
        try:
            audio_array, sampling_rate = librosa.load(io.BytesIO(audio_bytes), sr=16000)

            inputs = self.processor(
                audio_array, sampling_rate=sampling_rate, return_tensors="pt"
            ).to(self.device)

            with torch.no_grad(): 
                transcript_ids = self.model.generate(**inputs)
                transcript = self.processor.decode(
                    transcript_ids[0], skip_special_tokens=True
                )

            return transcript
        except Exception as e:
            raise RuntimeError(f"Error during transcription: {str(e)}")

    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """Transcribe an audio file and return the transcript."""
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        return self.get_transcript(audio_bytes)

if __name__ == "__main__":
    # Example usage
    try:
        engine = TranscriptionEngine(use_minio=False)  # Set use_minio to True when you want to use MinIO
        example_audio_path = "harvard.wav"
        transcript = engine.transcribe_audio_file(example_audio_path)
        print(f"Transcript: {transcript}")
    except Exception as e:
        print(f"Error: {str(e)}")

    # Simple test
    def test_transcription_engine():
        test_audio_path = "./AudioTransformer/harvard.wav"
        try:
            test_engine = TranscriptionEngine(use_minio=False)
            test_transcript = test_engine.transcribe_audio_file(test_audio_path)
            print(f"Test Transcript: {test_transcript}")
        except Exception as e:
            print(f"Test Error: {str(e)}")

    test_transcription_engine()