from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_first_page_header(header, section, logo_left, logo_right, review):
    header.paragraphs.clear()

    table = header.add_table(
        rows=1,
        cols=2,
        width=section.page_width
    )

    # Logo izquierda
    p_left = table.rows[0].cells[0].paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_left.add_run().add_picture(logo_left, width=Inches(2.3))

    # Logo derecha
    if logo_right:
        p_right = table.rows[0].cells[1].paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_right.add_run().add_picture(logo_right, width=Inches(1.6))

    # Barra Review
    p = header.add_paragraph()
    run = p.add_run(f" {review} ")
    run.bold = True

    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "1F5C4D")
    pPr.append(shd)

def add_running_header(header, review, author):
    header.paragraphs.clear()
    p = header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(review)
    p.add_run("\t")
    p.add_run(author)
