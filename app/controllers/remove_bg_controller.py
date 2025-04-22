from fastapi import UploadFile, HTTPException, Request
from app.services.remove_bg_service import remove_background
from PIL import Image
from io import BytesIO

# Supported MIME types based on Pillow capabilities
SUPPORTED_IMAGE_TYPES = [
    "image/png",
    "image/jpeg",
    "image/bmp",
    "image/gif",
    "image/webp",
    "image/tiff",
    "image/x-portable-pixmap",      # .ppm
    "image/x-portable-graymap",     # .pgm
    "image/x-portable-bitmap",      # .pbm
    "image/x-icon",                 # .ico
    "image/x-tga",                  # .tga
    "image/vnd.ms-dds"              # .dds (used by some modern apps/games)
]

async def remove_bg_controller(file: UploadFile):
    if file.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={"success":False, "message":"Unsupported file type. Supported formats: PNG, JPEG, BMP, GIF, WEBP, TIFF, PPM, PGM, PBM, ICO, TGA, DDS."}
        )
    
    # Read image file bytes
    image_bytes = await file.read()

    # Open image using Pillow to check size
    try:
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size
        # print(f"Image size: {width}x{height}")
    except Exception as e:
        raise HTTPException(status_code=400, detail={"success":False, "message":"Invalid image file format."})
    


    # Check if image size exceeds 2800x2800
    if width > 2801 or height > 2801:
        raise HTTPException(
            status_code=400,
            detail={"success":False, "message":"Image size exceeds the maximum allowed dimensions of 2800x2800."}
        )

    # Perform background removal
    sd_img, sd_size, hd_img, hd_size = remove_background(image_bytes)

    return sd_img, sd_size, hd_img, hd_size
