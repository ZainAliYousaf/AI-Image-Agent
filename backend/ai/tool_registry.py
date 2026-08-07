from tools.converter import convert_image
from tools.compressor import compress_image
from tools.pdf_generator import create_pdf


TOOLS = {
    "convert": convert_image,
    "compress": compress_image,
    "pdf": create_pdf
}