from minio import Minio
import os
from pathlib import Path


def init_minio():
    """Initialize MinIO with data and audio buckets and required files."""

    client = Minio(
        "localhost:9000",
        access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )

    try:
        if not client.bucket_exists("model"):
            print("Creating bucket: model")
            client.make_bucket("model")
    except Exception as e:
        print(f"Error creating bucket model: {e}")

    try:
        if not client.bucket_exists("audio"):
            print("Creating bucket: audio")
            client.make_bucket("audio")
    except Exception as e:
        print(f"Error creating bucket audio: {e}")

    model_dir = Path("/model")
    for file_path in model_dir.glob("*"):
        if file_path.is_file():
            file_name = file_path.name
            try:
                client.stat_object("model", file_name)
                print(f"File {file_name} already exists in bucket")
            except:
                try:
                    print(f"Uploading {file_name} to bucket")
                    client.fput_object("model", file_name, str(file_path))
                    print(f"Successfully uploaded {file_name}")
                except Exception as e:
                    print(f"Error uploading {file_name}: {e}")


if __name__ == "__main__":
    init_minio()
