from PIL import Image
import os
import tempfile
import uuid


OUTPUT_FOLDER = "storage/outputs"
TEMP_FOLDER = "storage/temp"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

os.makedirs(
    TEMP_FOLDER,
    exist_ok=True
)


def create_pdf(image_paths):

    if not image_paths:
        raise ValueError("No images provided.")

    processed_images = []

    # Create a unique temporary folder for this PDF job
    temp_dir = tempfile.mkdtemp(
        dir=TEMP_FOLDER
    )

    try:

        # ==========================================
        # PREPARE IMAGES
        # ==========================================

        for index, image_path in enumerate(image_paths):

            if not os.path.isfile(image_path):

                raise FileNotFoundError(
                    f"Image file not found: {image_path}"
                )

            image = Image.open(image_path)

            # Make sure the image is fully loaded
            image.load()

            # ======================================
            # HANDLE TRANSPARENCY
            # ======================================

            if image.mode in ("RGBA", "LA", "P"):

                if image.mode == "P":
                    image = image.convert("RGBA")

                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                if image.mode in ("RGBA", "LA"):

                    background.paste(
                        image,
                        mask=image.getchannel("A")
                    )

                    image = background

                else:

                    image = image.convert("RGB")

            else:

                image = image.convert("RGB")

            # ======================================
            # RESIZE LARGE IMAGES
            # ======================================

            max_dimension = 2500

            if max(image.size) > max_dimension:

                ratio = (
                    max_dimension /
                    max(image.size)
                )

                new_size = (
                    int(image.width * ratio),
                    int(image.height * ratio)
                )

                image = image.resize(
                    new_size,
                    Image.Resampling.LANCZOS
                )

            # ======================================
            # TEMPORARY JPEG
            # ======================================

            temp_path = os.path.join(
                temp_dir,
                f"page_{index}.jpg"
            )

            image.save(
                temp_path,
                "JPEG",
                quality=85,
                optimize=True
            )

            processed_images.append(
                temp_path
            )

            image.close()

        # ==========================================
        # CREATE MEANINGFUL UNIQUE PDF NAME
        # ==========================================

        unique_id = uuid.uuid4().hex[:8]

        pdf_filename = (
            f"images_to_pdf_{unique_id}.pdf"
        )

        output_path = os.path.join(
            OUTPUT_FOLDER,
            pdf_filename
        )

        # ==========================================
        # OPEN PROCESSED IMAGES
        # ==========================================

        first_image = Image.open(
            processed_images[0]
        )

        remaining_images = []

        for path in processed_images[1:]:

            image = Image.open(path)

            remaining_images.append(
                image
            )

        # ==========================================
        # CREATE PDF
        # ==========================================

        first_image.save(
            output_path,
            "PDF",
            resolution=150.0,
            save_all=True,
            append_images=remaining_images
        )

        # ==========================================
        # CLOSE IMAGES
        # ==========================================

        first_image.close()

        for image in remaining_images:
            image.close()

        return output_path

    finally:

        # ==========================================
        # CLEAN TEMPORARY FILES
        # ==========================================

        for path in processed_images:

            try:
                os.remove(path)

            except OSError:
                pass

        try:
            os.rmdir(temp_dir)

        except OSError:
            pass