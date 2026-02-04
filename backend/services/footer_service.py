from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_footer(doc, text):
    section = doc.sections[0]
    footer = section.footer
    footer.paragraphs.clear()

    p = footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Texto izquierda
    run_text = p.add_run(text)

    # Tabulación para empujar el número a la derecha
    p.add_run("\t")

    # Campo número de página
    run_page = p.add_run()
    fldChar1 = run_page._r.add_fldChar("begin")
    instrText = run_page._r.add_instrText("PAGE")
    fldChar2 = run_page._r.add_fldChar("end")
