from PIL import Image
import os
import re

OUTPUT_FOLDER = "storage/outputs"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


def convert_image(input_path: str, output_format: str):

    image = Image.open(input_path)

    output_format = output_format.lower().strip()

    # ---------------------------------------------------------
    # SUPPORTED FORMATS
    # ---------------------------------------------------------

    extension_map = {
        "jpg": "jpg",
        "jpeg": "jpeg",
        "png": "png",
        "webp": "webp",
        "bmp": "bmp",
        "tiff": "tiff",
        "gif": "gif",
        "avif": "avif"
    }

    if output_format not in extension_map:

        raise ValueError(
            f"Unsupported output format: {output_format}"
        )

    extension = extension_map[output_format]

    # ---------------------------------------------------------
    # HANDLE JPEG / JPG TRANSPARENCY
    # ---------------------------------------------------------

    if output_format in ["jpg", "jpeg"]:

        if image.mode in ("RGBA", "LA", "P"):

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

            if image.mode == "P":
                image = image.convert("RGBA")

            if image.mode in ("RGBA", "LA"):

                background.paste(
                    image,
                    mask=image.getchannel("A")
                )

                image.close()
                image = background

            else:

                image = image.convert("RGB")

        else:

            image = image.convert("RGB")

    # ---------------------------------------------------------
    # HANDLE PNG
    # ---------------------------------------------------------

    elif output_format == "png":

        if image.mode not in ("RGB", "RGBA"):

            image = image.convert("RGBA")

    # ---------------------------------------------------------
    # GET CLEAN ORIGINAL NAME
    # ---------------------------------------------------------

    original_filename = os.path.basename(
        input_path
    )

    original_name = os.path.splitext(
        original_filename
    )[0]

    # Remove internal UUID
    # Example:
    # photo_a82f31c9 -> photo

    original_name = re.sub(
        r"_[a-fA-F0-9]{8}$",
        "",
        original_name
    )

    # Replace unsafe characters

    original_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        original_name
    )

    original_name = original_name.strip("_")

    if not original_name:

        original_name = "image"

    # ---------------------------------------------------------
    # CREATE BASE OUTPUT NAME
    # ---------------------------------------------------------

    base_filename = (
        f"{original_name}_converted"
    )

    output_filename = (
        f"{base_filename}.{extension}"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_filename
    )

    # ---------------------------------------------------------
    # PREVENT OUTPUT NAME COLLISION
    # ---------------------------------------------------------

    counter = 2

    while os.path.exists(output_path):

        output_filename = (
            f"{base_filename}_{counter}.{extension}"
        )

        output_path = os.path.join(
            OUTPUT_FOLDER,
            output_filename
        )

        counter += 1

    # ---------------------------------------------------------
    # SAVE FORMAT
    # ---------------------------------------------------------

    save_format = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "webp": "WEBP",
        "bmp": "BMP",
        "tiff": "TIFF",
        "gif": "GIF",
        "avif": "AVIF"
    }[output_format]

    image.save(
        output_path,
        format=save_format
    )

    image.close()

    return output_path