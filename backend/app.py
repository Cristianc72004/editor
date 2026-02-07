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
    journal_name: str = Query("Green World Journal"),
    issn: str = Query("ISSN: 2737-6109"),

    # ====== PARÁMETROS =========
    # LOGO IZQ (coordenadas desde BORDE DE PÁGINA, en pulgadas)
    logo_left_x: float = Query(0.60),
    logo_left_y: float = Query(0.38),
    logo_left_w: float = Query(1.20),
    logo_left_h: float | None = Query(None),   # NUEVO (opcional)

    # LOGO DER (coordenadas y ancho)
    # Si no envías X, se alinea al borde derecho como antes.
    logo_right_x: float | None = Query(None),  # NUEVO (opcional)
    logo_right_y: float = Query(0.38),
    logo_right_w: float = Query(1.40),
    logo_right_h: float | None = Query(None),  # NUEVO (opcional)

    # TÍTULO + ISSN (PNG)
    title_x: float = Query(1.35),
    title_y: float = Query(0.45),
    title_w: float = Query(5.10),
    title_h: float = Query(0.70),

    # FRANJA (PNG con piquito)
    bar_x: float = Query(0.00),
    bar_y: float = Query(1.10),
    bar_w: float = Query(2.3622),  # 6 cm
    bar_h: float = Query(0.24)
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
        issn=issn,

        # posiciones
        logo_left_x=logo_left_x,
        logo_left_y=logo_left_y,
        logo_left_w=logo_left_w,
        logo_left_h=logo_left_h,

        logo_right_x=logo_right_x,
        logo_right_y=logo_right_y,
        logo_right_w=logo_right_w,
        logo_right_h=logo_right_h,

        title_x=title_x,
        title_y=title_y,
        title_w=title_w,
        title_h=title_h,
        bar_x=bar_x,
        bar_y=bar_y,
        bar_w=bar_w,
        bar_h=bar_h
    )
    return {"status": "ok", "file": output}