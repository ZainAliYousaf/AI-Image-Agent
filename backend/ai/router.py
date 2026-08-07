from ai.tool_registry import TOOLS


def execute_plan(plan, image_paths):

    current_files = image_paths

    for step in plan:

        tool_name = step.get("tool")

        if tool_name == "convert":

            output_format = step.get("format", "jpg")

            converted_files = []

            for image_path in current_files:

                output_path = TOOLS["convert"](
                    image_path,
                    output_format
                )

                converted_files.append(output_path)

            current_files = converted_files

        elif tool_name == "compress":

            target_size = step.get("target", "500kb")

            target_map = {
                "100kb": 100,
                "200kb": 200,
                "500kb": 500,
                "1mb": 1024
            }

            target_size_kb = target_map.get(
                target_size.lower(),
                500
            )

            compressed_files = []

            for image_path in current_files:

                output_path = TOOLS["compress"](
                    image_path,
                    target_size_kb
                )

                compressed_files.append(output_path)

            current_files = compressed_files

        elif tool_name == "pdf":

            pdf_path = TOOLS["pdf"](current_files)

            current_files = [pdf_path]

    return current_files