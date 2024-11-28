from minio import Minio
import os
from pathlib import Path


def init_minio():
    """Initialize MinIO with model and audio buckets and required files."""

    client = Minio(
        os.getenv("MINIO_URL"),
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False,
    )

    for bucket in ["model", "audio"]:
        try:
            if not client.bucket_exists(bucket):
                print(f"Creating bucket: {bucket}")
                client.make_bucket(bucket)
                print(f"Successfully created {bucket} bucket")
        except Exception as e:
            print(f"Error creating bucket {bucket}: {e}")

    model_dir = Path("/model")
    for file_path in model_dir.glob("*"):
        if file_path.is_file():
            file_name = file_path.name
            try:
                client.stat_object("model", file_name)
                print(f"File {file_name} already exists in bucket")
            except:
                try:
                    client.fput_object("model", file_name, str(file_path))
                except Exception as e:
                    print(f"Error uploading {file_name}: {e}")


if __name__ == "__main__":
    init_minio()
