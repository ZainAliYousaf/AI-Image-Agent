import re

from ai.llm import ask_llm


# =========================================================
# LOCAL PLANNER
# =========================================================

def local_plan(user_request):
    """
    Handle simple and deterministic image operations
    without using Gemini.
    """

    request = user_request.lower().strip()

    plan = []

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    wants_pdf = any(
        phrase in request
        for phrase in [
            "create pdf",
            "make pdf",
            "convert to pdf",
            "as pdf",
            "into pdf",
            "generate pdf",
            "pdf"
        ]
    )

    # -----------------------------------------------------
    # CONVERSION
    # -----------------------------------------------------

    format_patterns = {
        "jpg": [
            "jpg",
            "jpeg"
        ],
        "png": [
            "png"
        ],
        "webp": [
            "webp"
        ],
        "avif": [
            "avif"
        ]
    }

    output_format = None

    for fmt, keywords in format_patterns.items():

        for keyword in keywords:

            # Examples:
            # convert to png
            # convert these images into png
            # make them png
            # change to webp

            patterns = [
                rf"\bto\s+{keyword}\b",
                rf"\binto\s+{keyword}\b",
                rf"\b{keyword}\s+format\b",
                rf"\bmake.*\b{keyword}\b",
                rf"\bchange.*\b{keyword}\b",
                rf"\bconvert.*\b{keyword}\b"
            ]

            if any(
                re.search(
                    pattern,
                    request
                )
                for pattern in patterns
            ):

                output_format = fmt
                break

        if output_format:
            break

    # -----------------------------------------------------
    # COMPRESSION
    # -----------------------------------------------------

    wants_compression = any(
        phrase in request
        for phrase in [
            "compress",
            "compression",
            "reduce size",
            "reduce the size",
            "smaller size",
            "make smaller",
            "file size"
        ]
    )

    target_size = None

    if wants_compression:

        # -------------------------------------------------
        # Detect KB
        # -------------------------------------------------

        kb_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:kb|kB|kilobytes?)",
            request,
            re.IGNORECASE
        )

        if kb_match:

            value = float(
                kb_match.group(1)
            )

            target_size = f"{int(value)}kb"

        # -------------------------------------------------
        # Detect MB
        # -------------------------------------------------

        mb_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:mb|MB|megabytes?)",
            request,
            re.IGNORECASE
        )

        if mb_match:

            value = float(
                mb_match.group(1)
            )

            if value <= 1:
                target_size = "1mb"

            else:
                # Current compressor supports
                # targets up to 1 MB.
                target_size = "1mb"

        # -------------------------------------------------
        # Common predefined targets
        # -------------------------------------------------

        if not target_size:

            if "100 kb" in request:
                target_size = "100kb"

            elif "200 kb" in request:
                target_size = "200kb"

            elif "500 kb" in request:
                target_size = "500kb"

            elif "1 mb" in request:
                target_size = "1mb"

            elif "1mb" in request:
                target_size = "1mb"

        # -------------------------------------------------
        # Default compression target
        # -------------------------------------------------

        if not target_size:

            target_size = "500kb"

    # -----------------------------------------------------
    # BUILD LOCAL PLAN
    # -----------------------------------------------------

    # If we know exactly what the user wants,
    # there is no reason to call Gemini.
    if output_format or wants_compression or wants_pdf:

        # ---------------------------------------------
        # Conversion
        # ---------------------------------------------

        if output_format:

            plan.append({
                "tool": "convert",
                "format": output_format
            })

        # ---------------------------------------------
        # Compression
        # ---------------------------------------------

        if wants_compression:

            plan.append({
                "tool": "compress",
                "target": target_size
            })

        # ---------------------------------------------
        # PDF
        # ---------------------------------------------

        if wants_pdf:

            plan.append({
                "tool": "pdf"
            })

        if plan:

            return plan

    return None


# =========================================================
# AI PLANNER
# =========================================================

def ai_plan(user_request):
    """
    Use Gemini only when the request cannot be safely
    handled by the local planner.
    """

    prompt = f"""
You are the planning engine of an image-processing agent.

The available tools are:

1. convert
   Format values:
   jpg
   png
   webp
   avif

2. compress
   Target values:
   100kb
   200kb
   500kb
   1mb

3. pdf
   Creates one PDF from all current images.

Create a simple JSON execution plan.

Rules:

- Return ONLY a JSON array.
- Do not explain anything.
- Use the tools only when required.
- Preserve the order requested by the user.
- If the user asks to convert and then compress,
  conversion must come before compression.
- If the user asks to convert and create a PDF,
  conversion must come before PDF creation.
- If the user asks to compress and create a PDF,
  compression must come before PDF creation.

Examples:

User:
Convert these images to PNG

Output:
[
  {{
    "tool": "convert",
    "format": "png"
  }}
]

User:
Compress below 500 KB

Output:
[
  {{
    "tool": "compress",
    "target": "500kb"
  }}
]

User:
Convert to WebP and create a PDF

Output:
[
  {{
    "tool": "convert",
    "format": "webp"
  }},
  {{
    "tool": "pdf"
  }}
]

User request:
{user_request}
"""

    response = ask_llm(prompt)

    return response


# =========================================================
# MAIN PLANNER
# =========================================================

def create_plan(user_request):
    """
    First attempt deterministic local planning.

    Gemini is only called when the local planner
    cannot confidently understand the request.
    """

    # -----------------------------------------------------
    # Try local planner first
    # -----------------------------------------------------

    local_result = local_plan(
        user_request
    )

    if local_result:

        print(
            "Planner: Local plan used. "
            "Gemini was not called."
        )

        return local_result

    # -----------------------------------------------------
    # Fall back to Gemini
    # -----------------------------------------------------

    print(
        "Planner: Complex request. "
        "Using Gemini."
    )

    return ai_plan(
        user_request
    )