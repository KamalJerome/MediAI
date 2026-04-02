"""
PDF processing module for extracting text from uploaded documents.
"""

import os
import json
from typing import List, Tuple
import hashlib

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is not installed. Install it with: pip install PyPDF2")
    
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text.strip()


def get_file_hash(file_path: str) -> str:
    """Generate a hash of the file for deduplication."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def save_document_metadata(
    doc_name: str, 
    doc_path: str, 
    text_content: str, 
    embeddings_path: str
) -> dict:
    """
    Save document metadata for future reference.
    
    Args:
        doc_name: Name of the document
        doc_path: Path to the original document
        text_content: Extracted text content
        embeddings_path: Path where embeddings will be stored
        
    Returns:
        Metadata dictionary
    """
    metadata = {
        "name": doc_name,
        "original_path": doc_path,
        "hash": get_file_hash(doc_path),
        "content_length": len(text_content),
        "embeddings_path": embeddings_path
    }
    return metadata


def load_documents_metadata(metadata_file: str) -> dict:
    """Load existing document metadata."""
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_documents_metadata(metadata_file: str, metadata: dict):
    """Save document metadata to file."""
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
