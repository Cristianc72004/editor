from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# ======================================================
# HEADER PRIMERA PÁGINA
# ======================================================
def add_first_page_header(header, section, logo_left, logo_right, review):
    header.paragraphs.clear()

    # ---------- TABLA LOGOS ----------
    table_logos = header.add_table(
        rows=1,
        cols=2,
        width=section.page_width
    )

    cell_left = table_logos.rows[0].cells[0]
    cell_right = table_logos.rows[0].cells[1]

    # Logo principal (revista)
    p_left = cell_left.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_left.add_run().add_picture(logo_left, width=Inches(2.8))

    # Logo editorial
    if logo_right:
        p_right = cell_right.paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_right.add_run().add_picture(logo_right, width=Inches(1.6))

    # ---------- FRANJA VERDE (TABLA REAL) ----------
    bar_table = header.add_table(
        rows=1,
        cols=1,
        width=section.page_width
    )

    bar_cell = bar_table.rows[0].cells[0]

    # Quitar márgenes internos
    tcPr = bar_cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for side in ["top", "left", "bottom", "right"]:
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), "0")
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)

    # Texto Review
    p = bar_cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(f" {review} ")
    run.bold = True

    # Fondo verde real
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "1F5C4D")
    bar_cell._tc.get_or_add_tcPr().append(shd)


# ======================================================
# HEADER PÁGINAS SIGUIENTES
# ======================================================
def add_running_header(header, review, author):
    header.paragraphs.clear()

    p = header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    p.add_run(review)
    p.add_run("\t")
    p.add_run(author)
