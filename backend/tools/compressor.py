from PIL import Image
import os


def compress_image(input_path, target_size_kb=500):

    image = Image.open(input_path)

    filename = os.path.splitext(os.path.basename(input_path))[0]
    extension = os.path.splitext(input_path)[1].lower()

    output_path = os.path.join(
        "storage",
        "outputs",
        f"{filename}_compressed{extension}"
    )

    # PNG doesn't use JPEG quality compression
    if extension == ".png":
        image.save(
            output_path,
            optimize=True,
            compress_level=9
        )
        return output_path

    # Convert RGBA → RGB for JPEG
    if extension in [".jpg", ".jpeg"] and image.mode != "RGB":
        image = image.convert("RGB")

    quality = 95
    min_quality = 10

    while quality >= min_quality:

        image.save(
            output_path,
            optimize=True,
            quality=quality
        )

        size_kb = os.path.getsize(output_path) / 1024

        if size_kb <= target_size_kb:
            break

        quality -= 5

    return output_path