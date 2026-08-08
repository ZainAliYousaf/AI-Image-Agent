from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import os

from ai.agent import run_agent

from tools.converter import convert_image
from tools.compressor import compress_image
from tools.pdf_generator import create_pdf

from utils.file_handler import save_uploaded_image


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AI Image Agent",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# FOLDERS
# =========================================================

UPLOAD_FOLDER = "storage/uploads"
OUTPUT_FOLDER = "storage/outputs"
TEMP_FOLDER = "storage/temp"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

os.makedirs(
    TEMP_FOLDER,
    exist_ok=True
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "AI Image Agent is Running 🚀"
    }


# =========================================================
# DOWNLOAD OUTPUT FILE
# =========================================================

@app.get("/download/{filename:path}")
async def download_file(filename: str):

    # Prevent access outside output folder
    safe_filename = os.path.basename(filename)

    file_path = os.path.join(
        OUTPUT_FOLDER,
        safe_filename
    )

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="Output file not found."
        )

    extension = os.path.splitext(
        safe_filename
    )[1].lower()

    if extension == ".pdf":

        media_type = "application/pdf"

    elif extension in [".jpg", ".jpeg"]:

        media_type = "image/jpeg"

    elif extension == ".png":

        media_type = "image/png"

    elif extension == ".webp":

        media_type = "image/webp"

    elif extension == ".avif":

        media_type = "image/avif"

    else:

        media_type = "application/octet-stream"

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=safe_filename
    )


# =========================================================
# CONVERT IMAGE
# =========================================================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    output_format: str = Form(...)
):

    input_path = await save_uploaded_image(
        file,
        UPLOAD_FOLDER
    )

    try:

        output_path = convert_image(
            input_path,
            output_format
        )

        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=os.path.basename(output_path)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image conversion failed: {str(e)}"
        )


# =========================================================
# COMPRESS IMAGE
# =========================================================

@app.post("/compress")
async def compress(
    file: UploadFile = File(...),
    target_size: str = Form(...)
):

    input_path = await save_uploaded_image(
        file,
        UPLOAD_FOLDER
    )

    target_map = {
        "100kb": 100,
        "200kb": 200,
        "500kb": 500,
        "1mb": 1024
    }

    target_size_kb = target_map.get(
        target_size.lower(),
        500
    )

    try:

        output_path = compress_image(
            input_path,
            target_size_kb
        )

        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=os.path.basename(output_path)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Image compression failed: {str(e)}"
        )


# =========================================================
# CREATE PDF
# =========================================================

@app.post("/create-pdf")
async def create_pdf_api(
    files: list[UploadFile] = File(...)
):

    if not files:

        raise HTTPException(
            status_code=400,
            detail="Please upload at least one image."
        )

    image_paths = []

    try:

        for file in files:

            input_path = await save_uploaded_image(
                file,
                UPLOAD_FOLDER
            )

            image_paths.append(
                input_path
            )

        pdf_path = create_pdf(
            image_paths
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="generated.pdf"
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF creation failed: {str(e)}"
        )


# =========================================================
# AI AGENT
# =========================================================

@app.post("/agent")
async def agent(
    prompt: str = Form(...),
    files: list[UploadFile] = File(...)
):

    # -----------------------------------------------------
    # Validate prompt
    # -----------------------------------------------------

    if not prompt.strip():

        raise HTTPException(
            status_code=400,
            detail="Please describe what you want to do."
        )


    # -----------------------------------------------------
    # Validate files
    # -----------------------------------------------------

    if not files:

        raise HTTPException(
            status_code=400,
            detail="Please upload at least one image."
        )


    image_paths = []

    try:

        # -------------------------------------------------
        # Save uploaded images
        # -------------------------------------------------

        for file in files:

            input_path = await save_uploaded_image(
                file,
                UPLOAD_FOLDER
            )

            image_paths.append(
                input_path
            )


        # -------------------------------------------------
        # Run AI agent
        # -------------------------------------------------

        result = run_agent(
            prompt,
            image_paths
        )


        # -------------------------------------------------
        # Check result
        # -------------------------------------------------

        result_files = result.get("files", [])

        if not result_files:

            raise HTTPException(
                status_code=500,
                detail=(
                    "The AI agent completed but "
                    "did not generate any output files."
                )
            )


        # -------------------------------------------------
        # Prepare individual downloadable files
        # -------------------------------------------------

        output_files = []

        for file_path in result_files:

            if not os.path.exists(file_path):

                continue

            filename = os.path.basename(
                file_path
            )

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension == ".pdf":

                media_type = "application/pdf"

            elif extension in [".jpg", ".jpeg"]:

                media_type = "image/jpeg"

            elif extension == ".png":

                media_type = "image/png"

            elif extension == ".webp":

                media_type = "image/webp"

            elif extension == ".avif":

                media_type = "image/avif"

            else:

                media_type = "application/octet-stream"


            output_files.append({
                "filename": filename,
                "download_url": f"/download/{filename}",
                "media_type": media_type
            })


        # -------------------------------------------------
        # Make sure files actually exist
        # -------------------------------------------------

        if not output_files:

            raise HTTPException(
                status_code=500,
                detail=(
                    "The agent generated output information, "
                    "but the files could not be found."
                )
            )


        # -------------------------------------------------
        # Return ALL files
        # -------------------------------------------------

        return {
            "success": True,
            "message": "Processing completed successfully.",
            "files": output_files
        }


    except HTTPException:
        raise


    except Exception as e:

        error_text = str(e)

        print(
            "AI Agent Error:",
            repr(e)
        )


        # -------------------------------------------------
        # Gemini quota
        # -------------------------------------------------

        if "GEMINI_QUOTA_EXCEEDED" in error_text:

            raise HTTPException(
                status_code=429,
                detail=(
                    "The AI service has reached its "
                    "current usage limit. "
                    "Please try again later."
                )
            )


        # -------------------------------------------------
        # Other errors
        # -------------------------------------------------

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI agent could not process "
                "your request."
            )
        )