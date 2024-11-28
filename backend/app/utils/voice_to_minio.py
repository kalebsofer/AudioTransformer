import io
from minio import Minio
from ..config.settings import get_settings

settings = get_settings()


def upload_audio_to_minio(image_bytes: bytes, image_id: str) -> None:

    try:
        minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
        )
        minio_client.put_object(
            "images",
            f"{image_id}.jpg",
            io.BytesIO(image_bytes),
            length=len(image_bytes),
            content_type="image/jpeg",
        )
    except Exception as e:
        raise Exception(f"Error uploading image to MinIO: {str(e)}")