from datetime import timedelta
import os
from fastapi import APIRouter, UploadFile, HTTPException
from database.minioClient import minio_client, BUCKET
from uuid import uuid4

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload_image(file: UploadFile, uploadCollection):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    fileName = f"{uuid4()} - {file.filename}"

    doc = {
        "filename": fileName,
        "content_type": file.content_type,
        "path": path,
        "url": f"/uploads/{file.filename}"
    }

    uploadCollection.insert_one(doc)
    
    file.file.seek(0)
    minio_client.put_object(
        BUCKET,
        fileName,
        file.file,
        file.size,
        content_type=file.content_type
    )
    
    minio_url = minio_client.presigned_get_object(
        BUCKET,
        fileName,
        expires=timedelta(hours=1),
    )


    return {
        "filename": file.filename, 
        "local_url": f"/uploads/{file.filename}", 
        "minio_url": minio_url
    }

async def list_images(uploadCollection):
    return uploadCollection.find({}, {"_id": 0}).to_list(None)

async def get_image(filename: str, uploadCollection):
    img = uploadCollection.find_one({"filename": filename}, {"_id": 0})
    if not img:
        raise HTTPException(status_code=404, detail="Image not found!")
    else:
        return img