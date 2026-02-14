# backend/services/running_header_service.py

from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os, time

from .header_utils import (
    _ensure_generated_dir,
    _add_floating_picture,
    _build_bar_with_notch_png,
    _inline_to_anchor,
    GREEN_HEX,
    WHITE_RGB
)


def add_running_header(
    header,
    section,
    review,
    author,

    # posiciones cuadro review
    review_x,
    review_y,
    review_w,
    review_h,

    # posición nombre
    author_x,
    author_y,

    # franja inferior
    line_x,
    line_y,
    line_w,
    line_h
):

    # limpiar header
    while header.paragraphs:
        p = header.paragraphs[0]._p
        header._element.remove(p)

    out_dir = _ensure_generated_dir()
    ts = str(int(time.time() * 1000))

    # =============================
    # 1️⃣ CUADRO REVIEW
    # =============================

    review_png = os.path.join(out_dir, f"running_review_box_{ts}.png")

    _build_bar_with_notch_png(
        review_png,
        review_w,
        review_h,
        GREEN_HEX,
        f"  {review}  ",
        10,
        WHITE_RGB
    )

    p_box = header.add_paragraph()

    _add_floating_picture(
        p_box,
        review_png,
        review_w,
        review_x,
        review_y,
        h_ref="page",
        v_ref="page",
        z_index=2000,
        behind_doc=False
    )

    # =============================
    # 2️⃣ AUTOR (texto flotante)
    # =============================

    p_author = header.add_paragraph()
    r_author = p_author.add_run()
    r_author.add_text(author)

    inline = r_author._r.xpath(".//wp:inline")
    if inline:
        _inline_to_anchor(
            inline[-1],
            author_x,
            author_y,
            "page",
            "page",
            3000,
            False
        )

    # =============================
    # 3️⃣ LÍNEA INFERIOR
    # =============================

    line_png = os.path.join(out_dir, f"running_line_{ts}.png")

    _build_bar_with_notch_png(
        line_png,
        line_w,
        line_h,
        GREEN_HEX,
        "",
        1,
        WHITE_RGB
    )

    p_line = header.add_paragraph()

    _add_floating_picture(
        p_line,
        line_png,
        line_w,
        line_x,
        line_y,
        h_ref="page",
        v_ref="page",
        z_index=1000,
        behind_doc=True
    )
