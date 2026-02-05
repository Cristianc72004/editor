from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.document_service import list_documents, process_document

app = FastAPI()

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
    logo_left: str = Query(...),
    logo_right: str = Query(None),
    running_author: str = Query(""),
    title: str = Query(...),
    authors: str = Query(...),
    footer_text: str = Query(""),
    # 🔥 NUEVOS OPCIONALES
    journal_name: str = Query("Green World Journal"),
    issn: str = Query("ISSN: 2737-6109")
):
    output = process_document(
        filename=filename,
        logo_left=logo_left,
        logo_right=logo_right,
        running_author=running_author,
        title=title,
        authors=authors,
        footer_text=footer_text,
        journal_name=journal_name,
        issn=issn
    )
    return {"status": "ok", "file": output}