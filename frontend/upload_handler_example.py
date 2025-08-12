from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure static/images directory exists
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file and return an absolute URL.
    
    Returns:
        {
            "url": "http://localhost:8000/static/images/filename.jpg",
            "filename": "filename.jpg"
        }
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file to static/images directory
        file_path = IMAGES_DIR / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return absolute URLs (NOT relative)
        base_url = "http://localhost:8000"  # Change this to your actual domain in production
        absolute_url = f"{base_url}/static/images/{unique_filename}"
        thumbnail_url = f"{base_url}/static/images/thumbnails/{unique_filename}"
        
        print(f"✅ Image uploaded successfully: {absolute_url}")
        print(f"📱 Thumbnail URL: {thumbnail_url}")
        
        return JSONResponse({
            "url": absolute_url,
            "thumbnail_url": thumbnail_url,
            "filename": unique_filename,
            "message": "تصویر با موفقیت آپلود شد"
        })
        
    except Exception as e:
        print(f"❌ Image upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "images_dir": str(IMAGES_DIR)}

# Example of how your products endpoint should work
@app.get("/api/products")
async def get_products():
    """
    Example of how products should be returned with thumbnail URLs.
    """
    return [
        {
            "id": "1",
            "name": "Test Product",
            "description": "Test description",
            "price": 1000,
            "sizes": ["M", "L"],
            "image_url": "http://localhost:8000/static/images/thumbnails/product1.jpg",  # Thumbnail URL
            "createdAt": datetime.now().isoformat()
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 