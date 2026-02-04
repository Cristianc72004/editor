from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.services.document_service import list_documents, process_document

app = FastAPI()

from fastapi.staticfiles import StaticFiles

app.mount(
    "/logos",
    StaticFiles(directory="backend/assets/logos"),
    name="logos"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/documents")
def get_documents():
    return list_documents()

@app.post("/process")
def process(
    filename: str = Query(...),
    logo: str = Query(...),
    footer_text: str = Query(...),
    link: str = Query(...)
):
    output = process_document(filename, logo, footer_text, link)
    return {"status": "ok", "file": output}

from fastapi.responses import FileResponse
import os
import uuid
from docx import Document
from backend.services.header_service import add_header
from backend.services.footer_service import add_footer
from docx2pdf import convert

@app.get("/preview")
def preview(
    filename: str,
    logo: str,
    footer_text: str,
    link: str
):

    temp_id = uuid.uuid4().hex[:8]

    base_dir = "backend"
    original = os.path.join(base_dir, "documents", "original", filename)

    temp_docx = os.path.join(
        base_dir, "documents", "processed", f"preview_{temp_id}.docx"
    )
    temp_pdf = os.path.join(
        base_dir, "documents", "processed", f"preview_{temp_id}.pdf"
    )

    doc = Document(original)
    add_header(doc, os.path.join(base_dir, "assets", "logos", logo), link)
    add_footer(doc, footer_text)
    doc.save(temp_docx)

    convert(temp_docx, temp_pdf)

    return FileResponse(
        temp_pdf,
        media_type="application/pdf",
        filename="preview.pdf"
    )
