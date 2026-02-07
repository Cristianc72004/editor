# backend/services/header_service.py
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont, Image
import os, time

# ==========================
# Paleta / utilidades
# ==========================
GREEN_HEX = "1F5C4D"
GREY_ISSN_HEX = "557075"
WHITE_RGBA = (255, 255, 255, 255)
TRANSPARENT = (255, 255, 255, 0)
BLACK_RGB = (0, 0, 0)

# Word usa EMUs en wp:posOffset — 1" = 914400 EMUs
_EMUS_PER_INCH = 914400
def _emus(inches: float) -> int:
    return int(round(inches * _EMUS_PER_INCH))

def _ensure_dir(path: str): os.makedirs(path, exist_ok=True)

def _ensure_generated_dir():
    base = os.path.dirname(os.path.dirname(__file__))
    out = os.path.join(base, "assets", "generated")
    _ensure_dir(out)
    return out

def _pick_font(px: int, bold: bool = False):
    """
    Intenta Times New Roman (bold o regular); si no está, usa serif equivalentes.
    """
    try:
        candidates = []
        if bold:
            candidates += [
                "C:/Windows/Fonts/timesbd.ttf",  # Win Times New Roman Bold
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            ]
        else:
            candidates += [
                "C:/Windows/Fonts/times.ttf",  # Win Times New Roman Regular
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            ]
        # Fallback sans
        candidates += [
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for fp in candidates:
            if os.path.exists(fp):
                return ImageFont.truetype(fp, px)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    return r - l, b - t

def _hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# ==========================
# Inline -> Anchor (flotante, EMUs)
# ==========================
def _inline_to_anchor(
    inline_el,
    pos_x_in: float,
    pos_y_in: float,
    h_ref: str = "page",   # 'page' | 'margin'
    v_ref: str = "page",   # 'page' | 'margin'
    z_index: int = 2000,
    behind_doc: bool = False,  # True => detrás del documento
):
    """
    Convierte <wp:inline> en <wp:anchor>, posiciona con EMUs y setea la capa/z-order.
    """
    extent = inline_el.find(qn("wp:extent"))
    cx = extent.get("cx") if extent is not None else "0"
    cy = extent.get("cy") if extent is not None else "0"

    docPr = inline_el.find(qn("wp:docPr"))
    cNv = inline_el.find(qn("wp:cNvGraphicFramePr"))
    graphic = inline_el.find(qn("a:graphic"))

    anchor = OxmlElement("wp:anchor")
    for k, v in {
        "relativeHeight": str(z_index),
        "distT": "0", "distB": "0", "distL": "0", "distR": "0",
        "simplePos": "0",
        "behindDoc": "1" if behind_doc else "0",
        "locked": "0",
        "layoutInCell": "1",
        "allowOverlap": "1",
    }.items():
        anchor.set(k, v)

    simplePos = OxmlElement("wp:simplePos")
    simplePos.set("x", "0"); simplePos.set("y", "0")
    anchor.append(simplePos)

    positionH = OxmlElement("wp:positionH")
    positionH.set("relativeFrom", h_ref)
    posH = OxmlElement("wp:posOffset"); posH.text = str(_emus(pos_x_in))
    positionH.append(posH)
    anchor.append(positionH)

    positionV = OxmlElement("wp:positionV")
    positionV.set("relativeFrom", v_ref)
    posV = OxmlElement("wp:posOffset"); posV.text = str(_emus(pos_y_in))
    positionV.append(posV)
    anchor.append(positionV)

    new_extent = OxmlElement("wp:extent"); new_extent.set("cx", cx); new_extent.set("cy", cy)
    anchor.append(new_extent)

    effectExtent = OxmlElement("wp:effectExtent")
    for s in ["l", "t", "r", "b"]: effectExtent.set(s, "0")
    anchor.append(effectExtent)

    # Si está detrás del documento, usa wrapNone para no interferir el layout
    wrap = OxmlElement("wp:wrapNone") if behind_doc else OxmlElement("wp:wrapSquare")
    if not behind_doc:
        wrap.set("wrapText", "bothSides")
    anchor.append(wrap)

    if docPr is not None: anchor.append(docPr)
    if cNv   is not None: anchor.append(cNv)
    if graphic is not None: anchor.append(graphic)

    parent = inline_el.getparent(); idx = parent.index(inline_el)
    parent.remove(inline_el); parent.insert(idx, anchor)

def _add_floating_picture(paragraph, image_path, width_in, x_in, y_in,
                          h_ref="page", v_ref="page",
                          z_index=2000, behind_doc: bool = False):
    run = paragraph.add_run()
    run.add_picture(image_path, width=Inches(width_in))
    inl = run._r.xpath(".//wp:inline")
    if not inl: return
    _inline_to_anchor(inl[-1], x_in, y_in,
                      h_ref=h_ref, v_ref=v_ref,
                      z_index=z_index, behind_doc=behind_doc)

# ==========================
# PNGs: Título+ISSN y Franja  (width_in / height_in)
# ==========================
def _build_title_png(path_png, width_in, height_in, title, issn, title_pt, issn_pt, gap_px=18, dpi=140):
    """
    Renderiza:  [ TÍTULO (bold Times) ] + [ESP] + [ 'ISSN: ' + valor (regular) ]
    Centrado HORIZONTALMENTE dentro del PNG.
    """
    W = max(40, int(round(width_in  * dpi)))
    H = max(10, int(round(height_in * dpi)))
    img = Image.new("RGBA", (W, H), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    ft = _pick_font(int(title_pt * dpi / 72), bold=True)   # Título en negritas
    fi = _pick_font(int(issn_pt  * dpi / 72), bold=False)  # ISSN regular

    issn_val = issn.replace("ISSN", "").replace(":", "").strip()
    label = "ISSN: "

    tw, th = _text_size(draw, title, ft)
    lw, lh = _text_size(draw, label, fi)
    iw, ih = _text_size(draw, issn_val, fi)

    total_w = tw + gap_px + lw + iw
    if total_w > W - 8:
        # si no cabe, reduce un poco el gap
        gap_px = max(8, gap_px - 6)
        total_w = tw + gap_px + lw + iw

    # CENTRADO horizontal
    x = max(0, (W - total_w) // 2)
    yT = (H - th) // 2
    yI = (H - ih) // 2

    # Título (verde) en negritas
    draw.text((x, yT), title, fill=_hex_to_rgb(GREEN_HEX) + (255,), font=ft)
    x += tw + gap_px

    # ISSN (gris) regular
    grey = _hex_to_rgb(GREY_ISSN_HEX)
    draw.text((x, yI), label,    fill=grey + (255,), font=fi)
    x += lw
    draw.text((x, yI), issn_val, fill=grey + (255,), font=fi)

    img.save(path_png, format="PNG")

def _build_bar_with_notch_png(path_png, width_in, height_in, fill_hex, text, text_pt,
                              text_color=BLACK_RGB, notch_w_in=0.18, notch_h_in=0.18, dpi=140):
    W = max(20, int(round(width_in  * dpi)))
    H = max(10, int(round(height_in * dpi)))
    img = Image.new("RGBA", (W, H), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    fill = _hex_to_rgb(fill_hex)
    draw.rectangle([0, 0, W, H], fill=fill + (255,))

    # piquito sup. derecho
    nw = int(round(notch_w_in * dpi))
    nh = int(round(notch_h_in * dpi))
    tri = [(W - nw, 0), (W, 0), (W, nh)]
    draw.polygon(tri, fill=WHITE_RGBA)

    f = _pick_font(int(text_pt * dpi / 72))
    _, th = _text_size(draw, text, f)
    y = (H - th) // 2
    padL = max(10, int(H * 0.8))
    draw.text((padL, y), text, fill=text_color + (255,), font=f)

    img.save(path_png, format="PNG")

# ==========================
# Helpers: altura escalada de un logo (en pulgadas)
# ==========================
def _scaled_height_in(image_path: str, target_width_in: float) -> float:
    """
    Devuelve la altura (en pulgadas) con la que quedará una imagen
    cuando se inserta con ancho = target_width_in (manteniendo proporción).
    """
    try:
        with Image.open(image_path) as im:
            w, h = im.size  # px
            if w == 0:
                return 0.0
            ratio = h / float(w)
            return target_width_in * ratio
    except Exception:
        # Si algo falla, asumimos altura ~ 0.8 * ancho (aprox cuadrado)
        return target_width_in * 0.8

# ==========================
# Encabezado (primera página) — DOS FILAS
# ==========================
def add_first_page_header(
    header, section,
    logo_left, logo_right,
    review, journal_name, issn,
    # ===== coordenadas que envía document_service.py (pulgadas) =====
    logo_left_x, logo_left_y, logo_left_w,
    logo_right_y, logo_right_w,
    title_x, title_y, title_w, title_h,
    bar_x, bar_y, bar_w, bar_h
):
    """
    Dos filas:
      Fila 1: logos + título/ISSN
      Fila 2: franja debajo, y además detrás (behindDoc) para nunca tapar.

    Orden de inserción (importante para z-order en headers):
      1) FRANJA (z=500, behindDoc=True)
      2) LOGO IZQ (z=2000)
      3) LOGO DER (z=2000)
      4) TÍTULO (z=3000)
    """
    # Limpia header
    while header.paragraphs:
        p = header.paragraphs[0]._p
        header._element.remove(p)

    out_dir = _ensure_generated_dir()
    ts = str(int(time.time() * 1000))  # evita caché

    page_w_in = section.page_width.inches

    # --- Calculamos la altura real de la fila de arriba (fila 1) ---
    h_logo_left_in  = _scaled_height_in(logo_left, logo_left_w)
    h_logo_right_in = _scaled_height_in(logo_right, logo_right_w) if logo_right else 0.0

    # Fila 1: posición superior (mínimo y entre los 3 elementos)
    top_row_y = min(logo_left_y, logo_right_y if logo_right else logo_left_y, title_y)
    # Altura de la fila = max(alturas)
    row_height = max(h_logo_left_in, h_logo_right_in, title_h)

    # Gap vertical entre fila 1 y fila 2 (franja)
    GAP_IN = 0.10  # 2.54 mm aprox

    # Y final para la franja: SIEMPRE debajo de la fila 1
    bar_y_final = max(bar_y, top_row_y + row_height + GAP_IN)

    # ---------- (1) FRANJA primero — DETRÁS ----------
    bar_png = os.path.join(out_dir, f"bar_review_notch_{ts}.png")
    _build_bar_with_notch_png(
        path_png=bar_png,
        width_in=bar_w, height_in=bar_h,
        fill_hex=GREEN_HEX, text="  Review  ", text_pt=11, text_color=BLACK_RGB
    )
    p_bar = header.add_paragraph()
    _add_floating_picture(
        paragraph=p_bar,
        image_path=bar_png,
        width_in=bar_w,
        x_in=bar_x, y_in=bar_y_final,   # 👈 debajo de la fila 1
        h_ref="page", v_ref="page",
        z_index=500,
        behind_doc=True
    )

    # ---------- (2) LOGO IZQ — ENCIMA ----------
    p1 = header.add_paragraph(); p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rL = p1.add_run(); rL.add_picture(logo_left, width=Inches(logo_left_w))
    inlL = rL._r.xpath(".//wp:inline")
    if inlL:
        _inline_to_anchor(
            inline_el=inlL[-1],
            pos_x_in=logo_left_x,
            pos_y_in=logo_left_y,
            h_ref="page", v_ref="page",
            z_index=2000, behind_doc=False
        )

    # ---------- (3) LOGO DER — ENCIMA, a la DERECHA absoluta ----------
    RIGHT_PADDING_FROM_EDGE_IN = 0.10  # ajusta si lo quieres aún más al borde
    if logo_right:
        x_right = max(0.0, page_w_in - logo_right_w - RIGHT_PADDING_FROM_EDGE_IN)
        p2 = header.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        rR = p2.add_run(); rR.add_picture(logo_right, width=Inches(logo_right_w))
        inlR = rR._r.xpath(".//wp:inline")
        if inlR:
            _inline_to_anchor(
                inline_el=inlR[-1],
                pos_x_in=x_right,
                pos_y_in=logo_right_y,
                h_ref="page", v_ref="page",
                z_index=2000, behind_doc=False
            )

    # ---------- (4) TÍTULO + ISSN — ENCIMA DEL TODO ----------
    title_png = os.path.join(out_dir, f"title_box_{ts}.png")
    _build_title_png(
        path_png=title_png,
        width_in=title_w, height_in=title_h,
        title=journal_name, issn=issn,
        title_pt=24, issn_pt=12, gap_px=18
    )
    p3 = header.add_paragraph()
    _add_floating_picture(
        paragraph=p3,
        image_path=title_png,
        width_in=title_w,
        x_in=title_x, y_in=title_y,
        h_ref="page", v_ref="page",
        z_index=3000, behind_doc=False
    )

# ==========================
# Encabezado (páginas siguientes)
# ==========================
def add_running_header(header, review, author):
    while header.paragraphs:
        p = header.paragraphs[0]._p
        header._element.remove(p)
    p = header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(review)
    p.add_run("\t")
    p.add_run(author)