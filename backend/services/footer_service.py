def add_footer(doc, text):
    section = doc.sections[0]
    footer = section.footer
    footer.paragraphs[0].clear()
    footer.paragraphs[0].add_run(text)
