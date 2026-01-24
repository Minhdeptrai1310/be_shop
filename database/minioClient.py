from minio import Minio

minio_client = Minio(
    "127.0.0.1:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET = "uploads"

if not minio_client.bucket_exists(BUCKET):
    minio_client.make_bucket(BUCKET)
