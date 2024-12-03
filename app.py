from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

app = FastAPI()

# Directory to save files
UPLOAD_DIR = "uploaded_files"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@app.post("/upload/")
async def upload_file(unique_id: str, file: UploadFile = File(...)):
    """
    API to upload a file with a unique identifier.
    Args:
        unique_id (str): Unique identifier for the file.
        file (UploadFile): File to be uploaded.
    Returns:
        dict: Success message.
    """
    file_path = os.path.join(UPLOAD_DIR, unique_id + "_" + file.filename)
    
    # Save the file to disk
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"message": f"File '{file.filename}' uploaded successfully with unique_id '{unique_id}'."}

@app.get("/download/")
async def download_file(unique_id: str):
    """
    API to download a file associated with a unique identifier.
    Args:
        unique_id (str): Unique identifier for the file.
    Returns:
        FileResponse: File associated with the unique identifier.
    """
    # Search for the file with the unique_id prefix
    files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(unique_id + "_")]
    
    if not files:
        raise HTTPException(status_code=404, detail="File not found.")
    
    # Return the first matching file
    file_path = os.path.join(UPLOAD_DIR, files[0])
    return FileResponse(file_path, media_type="application/octet-stream", filename=files[0])
