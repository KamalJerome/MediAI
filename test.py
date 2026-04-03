import argparse
import sys
import time
from utils.ocr_processor import extract_text_from_image


def main():
    parser = argparse.ArgumentParser(description="Quick test for VLM OCR via Ollama")
    parser.add_argument("image", help="Path to the image file (PNG/JPEG/etc.)")
    args = parser.parse_args()

    try:
        print(f"Running OCR on image: {args.image}")
        
        start = time.perf_counter()
        text = extract_text_from_image(args.image)
        elapsed = time.perf_counter() - start

        print("--- Extracted text ---")
        print(text or "<no text extracted>")
        print("----------------------")
        print(f"Elapsed time: {elapsed:.2f} seconds")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
