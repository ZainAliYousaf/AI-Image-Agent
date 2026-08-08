import os
import zipfile


OUTPUT_FOLDER = "storage/outputs"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


def create_zip(
    file_paths,
    zip_name="ai-image-agent-results.zip"
):
    """
    Create a ZIP archive containing multiple output files.
    """

    if not file_paths:
        raise ValueError(
            "No files provided for ZIP creation."
        )

    zip_path = os.path.join(
        OUTPUT_FOLDER,
        zip_name
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for file_path in file_paths:

            if not os.path.exists(file_path):
                continue

            zip_file.write(
                file_path,
                arcname=os.path.basename(file_path)
            )

    return zip_path