from PIL import Image
import os


OUTPUT_FOLDER = "storage/outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def convert_image(input_path: str, output_format: str):

    image = Image.open(input_path)

    output_format = output_format.lower()

    extension_map = {
        "jpg": "jpg",
        "jpeg": "jpg",
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

    # JPEG doesn't support transparency
    if output_format in ["jpg", "jpeg"]:
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, "white")

            if image.mode == "P":
                image = image.convert("RGBA")

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

    elif output_format == "png":
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

    output_filename = (
        os.path.splitext(
            os.path.basename(input_path)
        )[0]
        + "."
        + extension
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_filename
    )

    save_format = {
        "jpg": "JPEG",
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

    return output_path