import os
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"image/jpeg", "image/png"}

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def uploadFile(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path


def deleteFile(path: str):
    if os.path.exists(path):
        print(path)
        os.unlink(path)
