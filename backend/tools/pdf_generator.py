import os
import img2pdf


def create_pdf(image_paths):

    output_path = os.path.join(
        "storage",
        "outputs",
        "generated.pdf"
    )

    with open(output_path, "wb") as pdf_file:
        pdf_file.write(
            img2pdf.convert(image_paths)
        )

    return output_path