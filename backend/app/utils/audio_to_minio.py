import io
from minio import Minio
from ..config.settings import get_settings

settings = get_settings()


def upload_audio_to_minio(
    audio_bytes: bytes, audio_id: str, file_extension: str
) -> None:
    if file_extension == "mp3":
        content_type = "audio/mpeg"
    elif file_extension == "wav":
        content_type = "audio/wav"
    else:
        raise ValueError("Unsupported audio format")

    try:
        minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE,
        )
        minio_client.put_object(
            "audio",
            f"{audio_id}.{file_extension}",
            io.BytesIO(audio_bytes),
            length=len(audio_bytes),
            content_type=content_type,
        )
    except Exception as e:
        raise Exception(f"Error uploading audio to MinIO: {str(e)}")
