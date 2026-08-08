import os
import time


# Files older than this will be removed automatically.
# 1 hour = 3600 seconds
MAX_FILE_AGE = 60 * 60


def delete_file(file_path: str):
    """
    Safely delete one file.
    """

    if not file_path:
        return

    try:
        if os.path.isfile(file_path):
            os.remove(file_path)

    except OSError as e:
        print(
            f"Cleanup warning: could not delete {file_path}: {e}"
        )


def cleanup_old_files(folder: str):
    """
    Delete files older than MAX_FILE_AGE.
    """

    if not os.path.exists(folder):
        return

    current_time = time.time()

    for filename in os.listdir(folder):

        file_path = os.path.join(
            folder,
            filename
        )

        if not os.path.isfile(file_path):
            continue

        try:

            file_age = (
                current_time -
                os.path.getmtime(file_path)
            )

            if file_age > MAX_FILE_AGE:
                os.remove(file_path)

                print(
                    f"Cleaned old file: {file_path}"
                )

        except OSError as e:

            print(
                f"Cleanup warning: {e}"
            )