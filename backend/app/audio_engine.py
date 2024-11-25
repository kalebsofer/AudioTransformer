# handle inference steps here
import os
import io
import torch
from PIL import Image
from minio import Minio
from transformers import BlipProcessor, BlipForConditionalGeneration
from .config.settings import get_settings

settings = get_settings()

class CaptionEngine:

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_dir = "local_model"
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

        self.processor = BlipProcessor.from_pretrained(
            self.model_dir, local_files_only=True
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            self.model_dir, local_files_only=True
        )
        self.model.to(self.device)
        self.model.eval()

    def get_caption(self, image_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            caption_ids = self.model.generate(**inputs)
            caption = self.processor.decode(caption_ids[0], skip_special_tokens=True)

        return caption