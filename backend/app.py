from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.services.document_service import list_documents, process_document

app = FastAPI()

# Servir logos
app.mount(
    "/logos",
    StaticFiles(directory="backend/assets/logos"),
    name="logos"
)

# CORS
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
    link: str = Query(...),
    position: str = Query("left"),
    size: float = Query(1.5)
):
    output = process_document(
        filename, logo, footer_text, link, position, size
    )
    return {"status": "ok", "file": output}
