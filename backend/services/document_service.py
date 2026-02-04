import os
from docx import Document
from .header_service import add_header
from .footer_service import add_footer

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOC_ORIGINAL = os.path.join(BASE_DIR, "documents", "original")
DOC_PROCESSED = os.path.join(BASE_DIR, "documents", "processed")
LOGOS_DIR = os.path.join(BASE_DIR, "assets", "logos")

def list_documents():
    return [f for f in os.listdir(DOC_ORIGINAL) if f.endswith(".docx")]

def process_document(filename, logo, footer_text, link):
    input_path = os.path.join(DOC_ORIGINAL, filename)
    output_path = os.path.join(DOC_PROCESSED, f"editado_{filename}")
    logo_path = os.path.join(LOGOS_DIR, logo)

    doc = Document(input_path)
    add_header(doc, logo_path, link)
    add_footer(doc, footer_text)
    doc.save(output_path)

    return output_path
