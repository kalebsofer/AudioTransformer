
from minio import Minio
from minio.error import S3Error
from .config.settings import get_settings

settings = get_settings()

def initialize_minio():
    # Initialize MinIO client
    minio_client = Minio(
        settings.MINIO_URL,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )

    # Create a bucket if it doesn't exist
    bucket_name = "model"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")

    # Upload a sample file to the bucket (optional)
    # Replace 'path/to/your/model/file' with the actual path to your model file
    model_file_path = "path/to/your/model/file"
    model_file_name = "model_file_name"  # Replace with the actual model file name
    try:
        minio_client.fput_object(bucket_name, model_file_name, model_file_path)
        print(f"Uploaded '{model_file_name}' to bucket '{bucket_name}'.")
    except S3Error as e:
        print(f"Error uploading file: {e}")

if __name__ == "__main__":
    initialize_minio()