from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns

def add_header(doc, logo_path, link, position="left", size=1.5):
    section = doc.sections[0]
    header = section.header
    header.paragraphs[0].clear()

    p = header.paragraphs[0]

    # Alineación
    if position == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif position == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    run = p.add_run()
    run.add_picture(logo_path, width=Inches(size))

    # Estilo hipervínculo
    r = run._r
    rPr = r.get_or_add_rPr()
    rStyle = OxmlElement("w:rStyle")
    rStyle.set(ns.qn("w:val"), "Hyperlink")
    rPr.append(rStyle)
