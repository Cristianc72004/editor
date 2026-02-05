from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def add_footer(doc, text):
    """
    Footer simple con texto a la izquierda y número de página a la derecha
    """

    section = doc.sections[-1]
    footer = section.footer

    footer.paragraphs.clear()

    p = footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Texto del footer
    p.add_run(text)
    p.add_run("\t")

    # Campo número de página
    run = p.add_run()

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")

    instr = OxmlElement("w:instrText")
    instr.text = "PAGE"

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")

    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
