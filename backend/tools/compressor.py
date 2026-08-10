from PIL import Image
import os
import re
import tempfile

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

    # ---------------------------------------------------------
    # VALIDATE TARGET SIZE
    # ---------------------------------------------------------

    try:
        target_size_kb = float(target_size_kb)
    except (TypeError, ValueError):
        target_size_kb = 500

    target_size_kb = max(
        target_size_kb,
        1
    )

    target_size_bytes = (
        target_size_kb * 1024
    )

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
    # CREATE OUTPUT PATH
    # ---------------------------------------------------------

    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"{filename}_compressed{extension}"
    )

    # =========================================================
    # PNG COMPRESSION
    # =========================================================

    if extension == ".png":

        # -----------------------------------------------------
        # STEP 1: LOSSLESS PNG OPTIMIZATION
        # -----------------------------------------------------

        image.save(
            output_path,
            format="PNG",
            optimize=True,
            compress_level=9
        )

        current_size = os.path.getsize(
            output_path
        )

        # Already below requested target
        if current_size <= target_size_bytes:

            image.close()

            return output_path

        # -----------------------------------------------------
        # STEP 2: REDUCE COLORS
        # -----------------------------------------------------

        # Keep transparency when possible.
        if image.mode in ("RGBA", "LA"):

            working_image = image.convert(
                "RGBA"
            )

        elif image.mode == "P":

            working_image = image.convert(
                "RGBA"
            )

        else:

            working_image = image.convert(
                "RGB"
            )

        color_levels = [
            256,
            192,
            128,
            96,
            64,
            48,
            32,
            24,
            16
        ]

        for colors in color_levels:

            if working_image.mode == "RGBA":

                test_image = (
                    working_image.quantize(
                        colors=colors,
                        method=Image.Quantize.MEDIANCUT
                    )
                )

            else:

                test_image = (
                    working_image.quantize(
                        colors=colors
                    )
                )

            test_image.save(
                output_path,
                format="PNG",
                optimize=True,
                compress_level=9
            )

            test_image.close()

            current_size = os.path.getsize(
                output_path
            )

            if current_size <= target_size_bytes:

                working_image.close()
                image.close()

                return output_path

        # -----------------------------------------------------
        # STEP 3: REDUCE DIMENSIONS
        # -----------------------------------------------------

        # If palette reduction was not enough,
        # progressively reduce image dimensions.

        width, height = working_image.size

        scale = 0.90

        while (
            width > 100
            and height > 100
        ):

            width = max(
                int(width * scale),
                100
            )

            height = max(
                int(height * scale),
                100
            )

            resized = working_image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

            # Try several palette sizes on
            # the resized image.

            for colors in [
                256,
                128,
                64,
                32,
                16
            ]:

                if resized.mode == "RGBA":

                    test_image = (
                        resized.quantize(
                            colors=colors,
                            method=Image.Quantize.MEDIANCUT
                        )
                    )

                else:

                    test_image = (
                        resized.quantize(
                            colors=colors
                        )
                    )

                test_image.save(
                    output_path,
                    format="PNG",
                    optimize=True,
                    compress_level=9
                )

                test_image.close()

                current_size = os.path.getsize(
                    output_path
                )

                if current_size <= target_size_bytes:

                    resized.close()
                    working_image.close()
                    image.close()

                    return output_path

            resized.close()

            # Reduce dimensions further
            # if still above target.

            if width <= 100 or height <= 100:
                break

        # -----------------------------------------------------
        # FINAL PNG RESULT
        # -----------------------------------------------------

        # At this point we use the smallest practical
        # representation generated above.

        working_image.close()
        image.close()

        return output_path

    # =========================================================
    # JPEG COMPRESSION
    # =========================================================

    if extension in [".jpg", ".jpeg"]:

        if image.mode != "RGB":

            image = image.convert(
                "RGB"
            )

        quality = 95
        min_quality = 10

        while quality >= min_quality:

            image.save(
                output_path,
                format="JPEG",
                optimize=True,
                quality=quality
            )

            size_kb = (
                os.path.getsize(output_path)
                / 1024
            )

            if size_kb <= target_size_kb:

                break

            quality -= 5

        image.close()

        return output_path

    # =========================================================
    # OTHER FORMATS
    # =========================================================

    image.save(
        output_path,
        optimize=True
    )

    image.close()

    return output_path