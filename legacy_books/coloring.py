from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .models import load_json
from .preflight import preflight


def _fit_size(source: tuple[int, int], target: tuple[float, float]) -> tuple[float, float]:
    sw, sh = source
    tw, th = target
    scale = min(tw / sw, th / sh)
    return sw * scale, sh * scale


def build_coloring_pdf(book_path: str | Path, profile_path: str | Path, output_path: str | Path) -> Path:
    book_path = Path(book_path)
    profile_path = Path(profile_path)
    output_path = Path(output_path)

    report = preflight(book_path, profile_path)
    if not report.ok:
        codes = ", ".join(issue.code for issue in report.errors)
        raise ValueError(f"preflight failed: {codes}")

    book = load_json(book_path)
    profile = load_json(profile_path)
    interior = profile.get("interior", {})
    trim = interior.get("trim_inches", [8.5, 11])
    page_size = (float(trim[0]) * 72.0, float(trim[1]) * 72.0)

    pages = book.get("pages", [])
    if not pages:
        raise ValueError("preflight failed: no pages")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=page_size, pageCompression=1)
    for page in pages:
        asset = (book_path.parent / page["asset"]).resolve()
        with Image.open(asset) as image:
            draw_w, draw_h = _fit_size(image.size, page_size)
        x = (page_size[0] - draw_w) / 2.0
        y = (page_size[1] - draw_h) / 2.0
        pdf.drawImage(ImageReader(str(asset)), x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")
        pdf.showPage()
    pdf.save()
    return output_path
