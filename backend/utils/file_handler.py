import os
import uuid
import re
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image


# Maximum size of one uploaded image: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


# Extensions we officially support
ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
}


# Pillow format names
ALLOWED_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
    "AVIF",
}


async def save_uploaded_image(
    file: UploadFile,
    upload_folder: str
) -> str:

    # -----------------------------------------
    # Validate filename
    # -----------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

    original_name = Path(file.filename).name

    extension = Path(original_name).suffix.lower()

    # -----------------------------------------
    # Check extension
    # -----------------------------------------

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Allowed formats: JPG, JPEG, PNG, WEBP and AVIF."
            )
        )

    # -----------------------------------------
    # Read file
    # -----------------------------------------

    data = await file.read()

    if not data:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # -----------------------------------------
    # Check file size
    # -----------------------------------------

    if len(data) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail=(
                "File is too large. "
                "Maximum allowed size is 10 MB."
            )
        )

    # -----------------------------------------
    # Verify that it is actually an image
    # -----------------------------------------

    try:

        from io import BytesIO

        image = Image.open(
            BytesIO(data)
        )

        image_format = image.format

        if image_format not in ALLOWED_FORMATS:

            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file is "
                    "not a supported image."
                )
            )

        # Verify image integrity
        image.verify()

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file is corrupted "
                "or is not a valid image."
            )
        )

    # -----------------------------------------
    # Create safe original filename
    # -----------------------------------------

    filename_without_extension = Path(
        original_name
    ).stem

    # Replace unsafe characters
    safe_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        filename_without_extension
    )

    # Remove unnecessary underscores
    safe_name = safe_name.strip("_")

    # Fallback if filename becomes empty
    if not safe_name:

        safe_name = "image"

    # -----------------------------------------
    # Add unique ID
    # -----------------------------------------

    unique_id = uuid.uuid4().hex[:8]

    safe_filename = (
        f"{safe_name}_{unique_id}{extension}"
    )

    # -----------------------------------------
    # Create upload folder
    # -----------------------------------------

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_folder,
        safe_filename
    )

    # -----------------------------------------
    # Save file
    # -----------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as output_file:

            output_file.write(data)

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save the uploaded image."
            )
        )

    return file_path