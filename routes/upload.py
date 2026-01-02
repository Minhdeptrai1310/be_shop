from fastapi import APIRouter, UploadFile, File, Depends
from controllers.uploadController import upload_image, get_image, list_images
from database.collections import get_upload_collection

upload = APIRouter()

@upload.post('/upload-image')
async def uploadImage(file: UploadFile = File(...), uploadCollection=Depends(get_upload_collection)):
    return await upload_image(file, uploadCollection)

@upload.get("/images")
async def listImage(uploadCollection=Depends(get_upload_collection)):
    return await list_images(uploadCollection)

@upload.get("/images/{filename:path}")
async def getImage(filename: str, uploadCollection=Depends(get_upload_collection)):
    return await get_image(filename, uploadCollection)