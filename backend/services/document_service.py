# backend/services/document_service.py
import os, time
from docx import Document
from docx.shared import Inches

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
    footer_text,
    journal_name,
    issn,
    # new
    logo_left_x, logo_left_y, logo_left_w,
    logo_right_y, logo_right_w,
    title_x, title_y, title_w, title_h,
    bar_x, bar_y, bar_w, bar_h
):
    input_path = os.path.join(DOC_ORIGINAL, filename)

    os.makedirs(DOC_PROCESSED, exist_ok=True)
    ts = int(time.time())
    output_path = os.path.join(
        DOC_PROCESSED,
        f"{os.path.splitext(filename)[0]}_editado_{ts}.docx"
    )

    original = Document(input_path)

    # Documento NUEVO + A4
    doc = Document()
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.header_distance = Inches(0.25)  # ↓ menos aire arriba

    # Copiar texto (sin estilos)
    for p in original.paragraphs:
        doc.add_paragraph(p.text)

    for index, section in enumerate(doc.sections):
        section.header.is_linked_to_previous = False
        section.first_page_header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False
        section.different_first_page_header_footer = True

        if index == 0:
            add_first_page_header(
                header=section.first_page_header,
                section=section,
                logo_left=os.path.join(LOGOS_DIR, logo_left),
                logo_right=os.path.join(LOGOS_DIR, logo_right) if logo_right else None,
                review=REVIEW_TYPE,
                journal_name=journal_name,
                issn=issn,
                # coords
                logo_left_x=logo_left_x, logo_left_y=logo_left_y, logo_left_w=logo_left_w,
                logo_right_y=logo_right_y, logo_right_w=logo_right_w,
                title_x=title_x, title_y=title_y, title_w=title_w, title_h=title_h,
                bar_x=bar_x, bar_y=bar_y, bar_w=bar_w, bar_h=bar_h
            )

        add_running_header(
            header=section.header,
            review=REVIEW_TYPE,
            author=running_author
        )

        add_footer(doc, footer_text)

    add_article_front(doc=doc, title=title, authors=authors)
    doc.save(output_path)
    return output_path