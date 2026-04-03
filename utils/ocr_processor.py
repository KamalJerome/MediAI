"""
OCR for prescription and document images using llama3.2-vision via Ollama.
Lazy-loads the Ollama client on first use to keep Streamlit startup fast.
"""

import os
import ollama


def extract_text_from_image(image_path: str) -> str:
    """
    Run OCR on an image file using llama3.2-vision via Ollama and return extracted text.

    Args:
        image_path: Path to a PNG, JPEG, WebP, BMP, etc.

    Returns:
        Extracted text (may be empty if nothing was detected).
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    response = ollama.chat(
        model='llama3.2-vision', #llama3.2-vision takes 44 secs; try these: qwen2.5vl:3b, moondream, deepseek-ocr
        messages=[{
            'role': 'user',
            'content': 'Extract all the text from this image. Return only the extracted text, nothing else.',
            'images': [image_path]
        }]
    )
    return response['message']['content'].strip()
