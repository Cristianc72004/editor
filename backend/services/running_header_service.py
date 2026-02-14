# backend/services/running_header_service.py

from docx.enum.text import WD_ALIGN_PARAGRAPH


def add_running_header(header, review, author):
    while header.paragraphs:
        p = header.paragraphs[0]._p
        header._element.remove(p)

    p = header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(review)
    p.add_run("\t")
    p.add_run(author)
