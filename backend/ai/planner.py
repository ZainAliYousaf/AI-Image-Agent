import json
from ai.llm import ask_llm


def create_plan(user_request: str):

    prompt = f"""
You are the planning brain of an AI image processing agent.

The agent has these tools:

1. convert
   - Converts an image from one format to another.
   - Parameters:
     format: jpg, jpeg, png, webp, avif, bmp, tiff, gif

2. compress
   - Compresses an image to a target maximum size.
   - Supported targets:
     100kb
     200kb
     500kb
     1mb

3. pdf
   - Combines multiple images into one PDF.

Your job is to understand the user's request and create a tool execution plan.

Return ONLY valid JSON.

The JSON must be an array.

Examples:

User:
"Convert my image to JPG"

Return:
[
    {{
        "tool": "convert",
        "format": "jpg"
    }}
]

User:
"Compress this image below 500 KB"

Return:
[
    {{
        "tool": "compress",
        "target": "500kb"
    }}
]

User:
"Convert the image to JPG and compress it below 1 MB"

Return:
[
    {{
        "tool": "convert",
        "format": "jpg"
    }},
    {{
        "tool": "compress",
        "target": "1mb"
    }}
]

User:
"Make a PDF from these images"

Return:
[
    {{
        "tool": "pdf"
    }}
]

User request:
{user_request}
"""

    response = ask_llm(prompt)

    # Remove markdown code fences if Gemini adds them
    response = response.strip()

    if response.startswith("```"):
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = response.strip()

    return json.loads(response)