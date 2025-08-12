import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import filetype
from PIL import Image
import io

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "static/images"
THUMBNAIL_DIR = "static/images/thumbnails"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# Security settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'}

# Allowed file extensions (for filename validation)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".svg"}


# Pydantic response model for upload endpoint
class UploadResponse(BaseModel):
    """Response model for successful image uploads."""
    message: str = "تصویر با موفقیت آپلود شد"
    url: str
    filename: str
    thumbnail_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message": "تصویر با موفقیت آپلود شد",
                "url": "http://localhost:8000/static/images/550e8400-e29b-41d4-a716-446655440000.jpg",
                "thumbnail_url": "http://localhost:8000/static/images/thumbnails/550e8400-e29b-41d4-a716-446655440000.jpg",
                "filename": "550e8400-e29b-41d4-a716-446655440000.jpg"
            }
        }


router = APIRouter(tags=["Upload"])


def is_valid_image_extension(filename: str) -> bool:
    """Check if the file has a valid image extension."""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


def validate_mime_type(file_content: bytes) -> bool:
    """Validate the actual MIME type of the file content."""
    try:
        kind = filetype.guess(file_content)
        if kind is None:
            return False
        return kind.mime in ALLOWED_MIME_TYPES
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other security issues."""
    # Remove any path separators and dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limit filename length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename


def generate_thumbnail(image_content: bytes, thumbnail_path: str) -> bool:
    """
    Generate a 400x400 thumbnail from image content.
    
    Args:
        image_content: Raw image bytes
        thumbnail_path: Path where thumbnail should be saved
        
    Returns:
        bool: True if thumbnail was created successfully, False otherwise
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to RGB if necessary (handles RGBA, P, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create thumbnail (maintains aspect ratio)
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Save thumbnail as JPEG
        image.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
        
        print(f"✅ Thumbnail generated: {thumbnail_path}")
        return True
        
    except Exception as e:
        print(f"🔥 Thumbnail generation failed: {str(e)}")
        return False


@router.post(
    "/upload-image",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Image File",
    description="""
    Upload an image file and generate both original and thumbnail versions.
    
    ## Features
    - **File Validation**: Validates MIME type and file extension
    - **Size Limit**: Maximum 5MB file size
    - **Thumbnail Generation**: Auto-creates 400x400 optimized thumbnail
    - **Security**: Sanitizes filenames and prevents path traversal
    - **Multiple Formats**: Supports JPG, JPEG, PNG, and GIF
    
    ## Process
    1. Validates file extension and MIME type
    2. Checks file size (max 5MB)
    3. Sanitizes filename for security
    4. Saves original image to `/static/images/`
    5. Generates 400x400 thumbnail in `/static/images/thumbnails/`
    6. Returns URLs for both original and thumbnail
    
    ## Supported Formats
    - **Input**: JPG, JPEG, PNG, GIF
    - **Thumbnail Output**: JPEG (optimized, 85% quality)
    
    ## Security Features
    - MIME type validation using `filetype` library
    - Filename sanitization (removes dangerous characters)
    - Path traversal prevention
    - File size limits
    """,
    responses={
        201: {
            "description": "Image uploaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "تصویر با موفقیت آپلود شد",
                        "url": "http://localhost:8000/static/images/550e8400-e29b-41d4-a716-446655440000.jpg",
                        "thumbnail_url": "http://localhost:8000/static/images/thumbnails/550e8400-e29b-41d4-a716-446655440000.jpg",
                        "filename": "550e8400-e29b-41d4-a716-446655440000.jpg"
                    }
                }
            }
        },
        400: {
            "description": "Invalid file format or missing filename",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "فرمت فایل مجاز نیست"
                    }
                }
            }
        },
        413: {
            "description": "File too large (max 5MB)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "حجم فایل بیشتر از حد مجاز است"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error during upload",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "خطا در بارگذاری فایل"
                    }
                }
            }
        }
    }
)
async def upload_image(
    file: UploadFile = File(
        ...,
        description="Image file to upload (JPG, JPEG, PNG, GIF, max 5MB)",
        media_type="image/*"
    ),
    request: Request = None
):
    """
    Upload an image file with comprehensive validation and thumbnail generation.
    
    This endpoint performs the following operations:
    1. **Validation**: Checks file extension, MIME type, and size
    2. **Security**: Sanitizes filename to prevent path traversal
    3. **Storage**: Saves original image to static/images/
    4. **Thumbnail**: Generates 400x400 optimized JPEG thumbnail
    5. **Response**: Returns URLs for both original and thumbnail
    
    **Security Features:**
    - Uses `filetype` library for actual MIME type detection
    - Sanitizes filenames (removes dangerous characters)
    - Enforces 5MB file size limit
    - Prevents path traversal attacks
    
    **Thumbnail Generation:**
    - Creates 400x400 pixel thumbnails
    - Maintains aspect ratio
    - Converts all formats to optimized JPEG
    - Uses LANCZOS resampling for high quality
    
    Args:
        file: The image file to upload (multipart form data)
        request: FastAPI request object for generating absolute URLs
        
    Returns:
        UploadResponse: JSON object containing:
            - message: Success message in Persian
            - url: Absolute URL to the original image
            - thumbnail_url: Absolute URL to the 400x400 thumbnail
            - filename: Generated unique filename
            
    Raises:
        HTTPException 400: Invalid file format or missing filename
        HTTPException 413: File size exceeds 5MB limit
        HTTPException 500: Internal server error during processing
    """
    print("📥 File received:", file.filename)
    
    try:
        # Check if filename exists
        if not file.filename:
            print("🔥 Upload failed: No filename provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="نام فایل نامعتبر است."
            )
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(file.filename)
        print("🔧 Sanitized filename:", sanitized_filename)
        
        # Validate file extension
        if not is_valid_image_extension(sanitized_filename):
            print("🔥 Upload failed: Invalid file extension")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="فرمت فایل مجاز نیست. فقط فایل‌های jpg، jpeg، png و gif مجاز هستند."
            )
        
        # Read file content for size and MIME type validation
        print("🔧 Reading file content for validation...")
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            print(f"🔥 Upload failed: File too large ({len(file_content)} bytes)")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="حجم فایل بیشتر از حد مجاز است"
            )
        
        # Validate MIME type
        if not validate_mime_type(file_content):
            print("🔥 Upload failed: Invalid MIME type")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="فرمت فایل مجاز نیست"
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(sanitized_filename)[1].lower()
        print("🔍 File extension:", file_extension)
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        print("🔑 Generated filename:", unique_filename)
        
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        print(f"💾 Saving file to: {file_path}")
        
        # Reset file pointer and save to disk
        file.file.seek(0)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        print("✅ Original file saved successfully")
        
        # Generate thumbnail
        thumbnail_filename = f"{os.path.splitext(unique_filename)[0]}.jpg"
        thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)
        
        print("🔧 Generating thumbnail...")
        thumbnail_created = generate_thumbnail(file_content, thumbnail_path)
        
        print("✅ Upload completed successfully")
        
        # Generate dynamic base URL from request
        base_url = str(request.base_url).rstrip('/') if request else "http://localhost:8000"
        absolute_url = f"{base_url}/static/images/{unique_filename}"
        thumbnail_url = f"{base_url}/static/images/thumbnails/{thumbnail_filename}"
        
        # Create response using UploadResponse model
        response_data = {
            "message": "تصویر با موفقیت آپلود شد",
            "url": absolute_url,
            "filename": unique_filename,
            "thumbnail_url": thumbnail_url if thumbnail_created else None
        }
        
        return UploadResponse(**response_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions as they already have proper status codes
        raise
    except Exception as e:
        print("🔥 Upload failed:", str(e))
        # Clean up files if they were created
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        # Clean up thumbnail if it was created
        if 'thumbnail_path' in locals() and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در بارگذاری فایل"
        ) 