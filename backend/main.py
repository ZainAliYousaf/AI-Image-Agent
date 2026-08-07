from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Annotated
import shutil
import os
from ai.agent import run_agent

from tools.converter import convert_image
from tools.compressor import compress_image
from tools.pdf_generator import create_pdf

app = FastAPI(title="AI Image Agent")

UPLOAD_FOLDER = "storage/uploads"
OUTPUT_FOLDER = "storage/outputs"
TEMP_FOLDER = "storage/temp"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "AI Image Agent is Running 🚀"
    }


# -------------------------------
# Convert Image
# -------------------------------
@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    output_format: str = Form(...)
):

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path = convert_image(input_path, output_format)

    return FileResponse(
        output_path,
        media_type="application/octet-stream",
        filename=os.path.basename(output_path)
    )


# -------------------------------
# Compress Image
# -------------------------------
@app.post("/compress")
async def compress(
    file: UploadFile = File(...),
    target_size: str = Form(...)
):

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    target_map = {
        "100kb": 100,
        "200kb": 200,
        "500kb": 500,
        "1mb": 1024
    }

    target_size_kb = target_map.get(target_size.lower(), 500)

    output_path = compress_image(input_path, target_size_kb)

    return FileResponse(
        output_path,
        media_type="application/octet-stream",
        filename=os.path.basename(output_path)
    )


# -------------------------------
# Create PDF
# -------------------------------
@app.post("/create-pdf")
async def create_pdf_api(
    files: list[UploadFile] = File(...)
):

    image_paths = []

    for file in files:
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_paths.append(input_path)

    pdf_path = create_pdf(image_paths)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="generated.pdf"
    )


# -------------------------------
# AI Agent
# -------------------------------
@app.post("/agent")
async def agent(
    prompt: str = Form(...),
    file: UploadFile = File(...)
):

    input_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = run_agent(
        prompt,
        [input_path]
    )

    files = result["files"]

    if not files:
        return {
            "message": "Agent completed but no output file was generated."
        }

    final_file = files[-1]

    return FileResponse(
        final_file,
        media_type="application/octet-stream",
        filename=os.path.basename(final_file)
    )