import os
from docx import Document

from .header_service import add_first_page_header, add_running_header
from .footer_service import add_footer
from .article_service import add_article_front

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOC_ORIGINAL = os.path.join(BASE_DIR, "documents", "original")
DOC_PROCESSED = os.path.join(BASE_DIR, "documents", "processed")
LOGOS_DIR = os.path.join(BASE_DIR, "assets", "logos")

REVIEW_TYPE = "Review"

def list_documents():
    return [f for f in os.listdir(DOC_ORIGINAL) if f.endswith(".docx")]

def process_document(
    filename,
    logo_left,
    logo_right,
    running_author,
    title,
    authors,
    footer_text
):
    input_path = os.path.join(DOC_ORIGINAL, filename)
    output_path = os.path.join(
        DOC_PROCESSED,
        f"{os.path.splitext(filename)[0]}_editado.docx"
    )

    os.makedirs(DOC_PROCESSED, exist_ok=True)

    doc = Document(input_path)
    section = doc.sections[0]

    section.different_first_page_header_footer = True

    add_first_page_header(
        header=section.first_page_header,
        section=section,
        logo_left=os.path.join(LOGOS_DIR, logo_left),
        logo_right=os.path.join(LOGOS_DIR, logo_right) if logo_right else None,
        review=REVIEW_TYPE
    )

    add_running_header(
        header=section.header,
        review=REVIEW_TYPE,
        author=running_author
    )

    add_article_front(
        doc=doc,
        title=title,
        authors=authors
    )

    add_footer(doc, footer_text)

    doc.save(output_path)
    return output_path
