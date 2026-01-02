from minio import Minio

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET = "uploads"

if not minio_client.bucket_exists(BUCKET):
    minio_client.make_bucket(BUCKET)
