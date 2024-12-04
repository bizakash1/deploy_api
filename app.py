from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
from gridfs import GridFS
import base64
import io

app = FastAPI()

# MongoDB Connection
client = MongoClient("mongodb+srv://Akash11:Pass123@cluster0.dqn6nis.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" , ssl = True)
db = client["mydatabase"]
fs = GridFS(db)

@app.post("/upload/")
async def upload_file(unique_id: str, file: UploadFile = File(...)):
    """
    API to upload a file with a unique identifier to MongoDB using GridFS.
    Args:
        unique_id (str): Unique identifier for the file.
        file (UploadFile): File to be uploaded.
    Returns:
        dict: Success message with the file's MongoDB ID.
    """
    # Read file content
    content = await file.read()
    
    # Store file in GridFS with metadata
    file_id = fs.put(content, filename=file.filename, metadata={"unique_id": unique_id})
    return {"message": f"File '{file.filename}' uploaded successfully.", "file_id": str(file_id)}

@app.get("/download/")
async def download_file(unique_id: str):
    """
    API to retrieve a file from MongoDB using unique ID and return it as a PDF.
    Args:
        unique_id (str): Unique identifier for the file.
    Returns:
        StreamingResponse: The PDF file returned as a downloadable file.
    """
    try:
        # Find the file by unique_id in the fs.files collection
        file_document = db.fs.files.find_one({"metadata.unique_id": unique_id})
        if not file_document:
            raise HTTPException(status_code=404, detail="File not found.")
        
        # Retrieve the file from GridFS
        file = fs.get(file_document["_id"])
        
        # Read the binary content of the file
        file_content = file.read()

        # Return the PDF as a downloadable file
        return StreamingResponse(io.BytesIO(file_content),
                                 media_type="application/pdf",  # Set the media type to PDF
                                 headers={"Content-Disposition": f"attachment; filename={file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
