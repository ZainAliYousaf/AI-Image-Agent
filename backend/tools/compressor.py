from PIL import Image
import os
import re


OUTPUT_FOLDER = "storage/outputs"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


def compress_image(
    input_path,
    target_size_kb=500
):

    image = Image.open(input_path)

    filename = os.path.splitext(
        os.path.basename(input_path)
    )[0]

    extension = os.path.splitext(
        input_path
    )[1].lower()

    # ---------------------------------------------------------
    # REMOVE INTERNAL UPLOAD UUID
    # ---------------------------------------------------------

    filename = re.sub(
        r"_[a-fA-F0-9]{8}$",
        "",
        filename
    )

    # ---------------------------------------------------------
    # CLEAN FILENAME
    # ---------------------------------------------------------

    filename = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        filename
    )

    filename = filename.strip("_")

    if not filename:
        filename = "image"

    # ---------------------------------------------------------
    # OUTPUT PATH
    # ---------------------------------------------------------

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"{filename}_compressed{extension}"
    )

    # ---------------------------------------------------------
    # PNG
    # ---------------------------------------------------------

    if extension == ".png":

        image.save(
            output_path,
            optimize=True,
            compress_level=9
        )

        image.close()

        return output_path

    # ---------------------------------------------------------
    # JPEG
    # ---------------------------------------------------------

    if extension in [".jpg", ".jpeg"]:

        if image.mode != "RGB":
            image = image.convert("RGB")

        quality = 95
        min_quality = 10

        while quality >= min_quality:

            image.save(
                output_path,
                optimize=True,
                quality=quality
            )

            size_kb = (
                os.path.getsize(output_path) / 1024
            )

            if size_kb <= target_size_kb:
                break

            quality -= 5

        image.close()

        return output_path

    # ---------------------------------------------------------
    # OTHER FORMATS
    # ---------------------------------------------------------

    image.save(
        output_path,
        optimize=True
    )

    image.close()

    return output_path