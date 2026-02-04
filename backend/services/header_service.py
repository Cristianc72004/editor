from docx.shared import Inches
from docx.oxml import OxmlElement, ns

def add_header(doc, logo_path, link):
    section = doc.sections[0]
    header = section.header
    header.paragraphs[0].clear()

    p = header.paragraphs[0]
    run = p.add_run()
    run.add_picture(logo_path, width=Inches(1.5))

    r = run._r
    rPr = r.get_or_add_rPr()
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(ns.qn('w:val'), 'Hyperlink')
    rPr.append(rStyle)
