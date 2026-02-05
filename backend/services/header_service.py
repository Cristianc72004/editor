# backend/services/header_service.py
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont
import os, time

# ======================================
# CONFIGURACIÓN (A4 y layout final afinado)
# ======================================

GREEN_HEX = "1F5C4D"                 # #1f5c4d
GREEN_RGB = (0x1F, 0x5C, 0x4D)
GREY_ISSN_HEX = "557075"
WHITE_RGB = (255, 255, 255)
BLACK_RGB = (0, 0, 0)

# --- LOGO IZQUIERDO (desde borde de PÁGINA) ---
LOGO_LEFT_W_IN           = 1.20
LOGO_LEFT_X_FROM_PAGE_IN = 0.60
LOGO_LEFT_Y_FROM_PAGE_IN = 0.72   # 🔧 lo bajo un poco para dar respiro

# --- LOGO DERECHO (pegado a margen derecho) ---
LOGO_RIGHT_W_IN           = 1.40
LOGO_RIGHT_Y_FROM_PAGE_IN = 0.72   # 🔧 a la misma altura del izquierdo

# --- TÍTULO + ISSN como PNG (transparente, movible) ---
# Lo bajo y le doy un poco más de separación a la derecha del logo izq
TITLE_IMG_W_IN         = 5.00
TITLE_IMG_H_IN         = 0.72    # 🔧 un poco más bajo para que no choque
TITLE_X_FROM_PAGE_IN   = 2.30    # 🔧 antes 2.20; un poco más de espacio
TITLE_Y_FROM_PAGE_IN   = 0.68    # 🔧 más abajo para alinearlo a la fila
TITLE_PT               = 24
ISSN_PT                = 12
TITLE_GAP_PX           = 18

# --- FRANJA "Review" (PNG con piquito) 6 cm -> 2.3622 in ---
BAR_W_IN               = 2.3622
BAR_H_IN               = 0.24
BAR_X_FROM_PAGE_IN     = 0.00
BAR_Y_FROM_PAGE_IN     = 1.24    # 🔧 la bajo (antes 1.10) para que no toque el título
BAR_LABEL              = "  Review  "
BAR_LABEL_PT           = 11
BAR_COLOR_HEX          = GREEN_HEX
BAR_TEXT_COLOR         = BLACK_RGB

# Envolvente flotante
WRAP_STYLE_DEFAULT = "square"
ENABLE_FLOATING    = True

# ======================================
# HELPERS
# ======================================

_TWIPS_PER_INCH = 1440
_EMU_PER_INCH   = 914400

def _twips(inches: float) -> int:
    return int(round(inches * _TWIPS_PER_INCH))

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _ensure_generated_dir():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.join(base_dir, "assets", "generated")
    _ensure_dir(out_dir)
    return out_dir

def _pick_font(px: int):
    try:
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        for fp in candidates:
            if os.path.exists(fp):
                return ImageFont.truetype(fp, px)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top

def _hex_to_rgb(hex_str: str):
    h = hex_str.strip().lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# ========== inline -> anchor flotante con z-index ==========
def _inline_to_anchor(
    inline_el,
    pos_x_twips: int = 0,
    pos_y_twips: int = 0,
    h_ref: str = "page",     # 'page' | 'margin'
    v_ref: str = "page",     # 'page' | 'margin'
    align_right: bool = False,
    z_index: int = 0         # capa: mayor = más arriba
):
    extent = inline_el.find(qn('wp:extent'))
    cx = extent.get('cx') if extent is not None else "0"
    cy = extent.get('cy') if extent is not None else "0"

    docPr = inline_el.find(qn('wp:docPr'))
    cNv = inline_el.find(qn('wp:cNvGraphicFramePr'))
    graphic = inline_el.find(qn('a:graphic'))

    anchor = OxmlElement('wp:anchor')
    # relativeHeight controla z-order. Usa un número bajo/alto estable.
    for attr, val in {
        'distT': "0", 'distB': "0", 'distL': "0", 'distR': "0",
        'simplePos': "0",
        'relativeHeight': str(1000 + max(0, int(z_index))*1000),
        'behindDoc': "0", 'locked': "0", 'layoutInCell': "1",
        'allowOverlap': "1"
    }.items():
        anchor.set(attr, val)

    simplePos = OxmlElement('wp:simplePos'); simplePos.set('x', "0"); simplePos.set('y', "0")
    anchor.append(simplePos)

    # Horizontal
    positionH = OxmlElement('wp:positionH')
    positionH.set('relativeFrom', 'margin' if align_right else h_ref)
    if align_right:
        align = OxmlElement('wp:align'); align.text = 'right'
        positionH.append(align)
    else:
        posOffH = OxmlElement('wp:posOffset'); posOffH.text = str(int(pos_x_twips))
        positionH.append(posOffH)
    anchor.append(positionH)

    # Vertical
    positionV = OxmlElement('wp:positionV'); positionV.set('relativeFrom', v_ref)
    posOffV   = OxmlElement('wp:posOffset'); posOffV.text = str(int(pos_y_twips))
    positionV.append(posOffV); anchor.append(positionV)

    new_extent = OxmlElement('wp:extent'); new_extent.set('cx', cx); new_extent.set('cy', cy)
    anchor.append(new_extent)

    effectExtent = OxmlElement('wp:effectExtent')
    for side in ['l', 't', 'r', 'b']: effectExtent.set(side, "0")
    anchor.append(effectExtent)

    wrap = OxmlElement('wp:wrapSquare'); wrap.set('wrapText', 'bothSides')
    anchor.append(wrap)

    if docPr is not None: anchor.append(docPr)
    if cNv  is not None:  anchor.append(cNv)
    if graphic is not None: anchor.append(graphic)

    parent = inline_el.getparent()
    idx    = parent.index(inline_el)
    parent.remove(inline_el)
    parent.insert(idx, anchor)

def _add_floating_picture(paragraph, image_path,
                          width_inches: float,
                          pos_x_inches: float = 0.0,
                          pos_y_inches: float = 0.0,
                          h_ref: str = "page",
                          v_ref: str = "page",
                          align_right: bool = False,
                          z_index: int = 0):
    run = paragraph.add_run()
    run.add_picture(image_path, width=Inches(width_inches))
    if not ENABLE_FLOATING:
        return
    inline_list = run._r.xpath('.//wp:inline')
    if not inline_list:
        return
    _inline_to_anchor(
        inline_el=inline_list[-1],
        pos_x_twips=_twips(pos_x_inches),
        pos_y_twips=_twips(pos_y_inches),
        h_ref=h_ref,
        v_ref=v_ref,
        align_right=align_right,
        z_index=z_index
    )

# ========== Generación de PNGs ==========
def _pick_font_smart(pt: int, dpi: int = 140):
    return _pick_font(int(pt * dpi / 72))

def _build_title_png(path_png: str,
                     width_in: float,
                     height_in: float,
                     title: str,
                     issn: str,
                     title_pt: int,
                     issn_pt: int,
                     gap_px: int = TITLE_GAP_PX,
                     dpi: int = 140):
    width_px = max(40, int(round(width_in * dpi)))
    height_px = max(10, int(round(height_in * dpi)))
    img = Image.new("RGBA", (width_px, height_px), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    font_title = _pick_font_smart(title_pt, dpi)
    font_issn  = _pick_font_smart(issn_pt, dpi)

    issn_val = issn.replace("ISSN", "").replace(":", "").strip()
    label = "ISSN: "

    title_w, title_h = _text_size(draw, title, font_title)
    label_w, label_h = _text_size(draw, label, font_issn)
    issn_w,  issn_h  = _text_size(draw, issn_val, font_issn)

    total_w = title_w + gap_px + label_w + issn_w
    if total_w > width_px - 8:
        gap_px = max(10, gap_px - 6)
        font_issn  = _pick_font_smart(max(10, issn_pt - 1), dpi)
        label_w, label_h = _text_size(draw, label, font_issn)
        issn_w,  issn_h  = _text_size(draw, issn_val, font_issn)
        total_w = title_w + gap_px + label_w + issn_w

    y_title = int((height_px := height_px if (height_px := height_px) else height_px) or (height_px := height_px))
    # ^^ truco no necesario; hacemos normal:
    height_px = img.height
    y_title = int((height_px - title_h) / 2)
    y_issn  = int((height_px - issn_h) / 2)

    x = 0
    draw.text((x, y_title), title, fill=GREEN_RGB + (255,), font=font_title)
    x += title_w + gap_px
    issn_rgb = _hex_to_rgb(GREY_ISSN_HEX)
    draw.text((x, y_issn), label, fill=issn_rgb + (255,), font=font_issn)
    x += label_w
    draw.text((x, y_issn), issn_val, fill=issn_rgb + (255,), font=font_issn)

    img.save(path_png, format="PNG")

def _build_bar_with_notch_png(path_png: str,
                              width_in: float,
                              height_in: float,
                              fill_hex: str,
                              text: str,
                              text_pt: int,
                              text_color=BLACK_RGB,
                              notch_w_in: float = 0.18,
                              notch_h_in: float = 0.18,
                              dpi: int = 140):
    width_px  = max(20, int(round(width_in * dpi)))
    height_px = max(10, int(round(height_in * dpi)))
    img = Image.new("RGBA", (width_px, height_px), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    fill_rgb = _hex_to_rgb(fill_hex)
    draw.rectangle([0, 0, width_px, height_px], fill=fill_rgb + (255,))

    # piquito superior derecho
    notch_w_px = int(round(notch_w_in * dpi))
    notch_h_px = int(round(notch_h_in * dpi))
    tri = [(width_px - notch_w_px, 0), (width_px, 0), (width_px, notch_h_px)]
    draw.polygon(tri, fill=WHITE_RGB + (255,))

    font = _pick_font_smart(text_pt, dpi)
    pad_left = max(10, int(height_px * 0.8))
    _, text_h = _text_size(draw, text, font)
    y = int((height_px - text_h) / 2)
    draw.text((pad_left, y), text, fill=text_color + (255,), font=font)

    img.save(path_png, format="PNG")

# ==========================
# ENCABEZADOS
# ==========================

def add_first_page_header(header, section, logo_left, logo_right, review, journal_name, issn):
    """
    Layout:
    [LOGO IZQ] – [TÍTULO + ISSN] – [LOGO DER (pegado derecha)]
    [Franja Review (6 cm) con piquito, debajo del logo izquierdo]
    Todas las coordenadas desde BORDE DE PÁGINA para consistencia.
    Z-order: franja (0) < logos (1) < título (3).
    """
    # Limpia header
    while header.paragraphs:
        p = header.paragraphs[0]._p
        header._element.remove(p)

    # ---------- LOGO IZQUIERDO (z=1) ----------
    p1 = header.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    runL = p1.add_run()
    runL.add_picture(logo_left, width=Inches(LOGO_LEFT_W_IN))
    if ENABLE_FLOATING:
        inlineL = runL._r.xpath('.//wp:inline')
        if inlineL:
            _inline_to_anchor(
                inline_el=inlineL[-1],
                pos_x_twips=_twips(LOGO_LEFT_X_FROM_PAGE_IN),
                pos_y_twips=_twips(LOGO_LEFT_Y_FROM_PAGE_IN),
                h_ref="page",
                v_ref="page",
                align_right=False,
                z_index=1
            )

    # ---------- LOGO DERECHO (z=1, align right) ----------
    if logo_right:
        p2 = header.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        runR = p2.add_run()
        runR.add_picture(logo_right, width=Inches(LOGO_RIGHT_W_IN))
        if ENABLE_FLOATING:
            inlineR = runR._r.xpath('.//wp:inline')
            if inlineR:
                _inline_to_anchor(
                    inline_el=inlineR[-1],
                    pos_x_twips=0,
                    pos_y_twips=_twips(LOGO_RIGHT_Y_FROM_PAGE_IN),
                    h_ref="margin",    # horizontal = margen (para pegado derecha)
                    v_ref="page",      # vertical = página (consistente)
                    align_right=True,
                    z_index=1
                )

    # ---------- TÍTULO + ISSN (PNG, z=3) ----------
    out_dir = _ensure_generated_dir()
    ts = str(int(time.time() * 1000))
    title_png = os.path.join(out_dir, f"title_box_{ts}.png")
    _build_title_png(
        path_png=title_png,
        width_in=TITLE_IMG_W_IN,
        height_in=TITLE_IMG_H_IN,
        title=journal_name,
        issn=issn,
        title_pt=TITLE_PT,
        issn_pt=ISSN_PT,
        gap_px=TITLE_GAP_PX
    )
    p3 = header.add_paragraph()
    _add_floating_picture(
        paragraph=p3,
        image_path=title_png,
        width_inches=TITLE_IMG_W_IN,
        pos_x_inches=TITLE_X_FROM_PAGE_IN,
        pos_y_inches=TITLE_Y_FROM_PAGE_IN,
        h_ref="page",
        v_ref="page",
        align_right=False,
        z_index=3
    )

    # ---------- FRANJA (PNG con piquito, z=0) ----------
    bar_png = os.path.join(out_dir, f"bar_review_notch_{ts}.png")
    _build_bar_with_notch_png(
        path_png=bar_png,
        width_in=BAR_W_IN,
        height_in=BAR_H_IN,
        fill_hex=BAR_COLOR_HEX,
        text=BAR_LABEL,
        text_pt=BAR_LABEL_PT,
        text_color=BAR_TEXT_COLOR
    )
    p4 = header.add_paragraph()
    _add_floating_picture(
        paragraph=p4,
        image_path=bar_png,
        width_inches=BAR_W_IN,
        pos_x_inches=BAR_X_FROM_PAGE_IN,
        pos_y_inches=BAR_Y_FROM_PAGE_IN,
        h_ref="page",
        v_ref="page",
        align_right=False,
        z_index=0
    )

def add_running_header(header, review, author):
    # Encabezado simple para páginas siguientes
    while header.paragraphs:
        p = header.paragraphs[0]._p
        header._element.remove(p)
    p = header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(review)
    p.add_run("\t")
    p.add_run(author)