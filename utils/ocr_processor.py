"""
OCR for prescription and document images using llama3.2-vision via Ollama.
Lazy-loads the Ollama client on first use to keep Streamlit startup fast.
"""

import os
import threading

_ollama_lock = threading.Lock()
_ollama_imported = False


def _get_ollama():
    global _ollama_imported
    with _ollama_lock:
        if not _ollama_imported:
            try:
                import ollama
                _ollama_imported = True
            except ImportError as e:
                raise ImportError(
                    "Ollama is not installed. Install with:\n"
                    "  pip install ollama\n"
                    "Also ensure Ollama is running with llama3.2-vision model pulled."
                ) from e
        return ollama


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

    ollama_client = _get_ollama()
    response = ollama_client.chat(
        model='llama3.2-vision',
        messages=[{
            'role': 'user',
            'content': 'Extract all the text from this image. Return only the extracted text, nothing else.',
            'images': [image_path]
        }]
    )
    return response['message']['content'].strip()
