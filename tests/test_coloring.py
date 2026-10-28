import json
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from legacy_books.coloring import build_coloring_pdf


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def make_bw(path: Path, value: int = 255) -> None:
    Image.new("RGB", (1200, 1600), (value, value, value)).save(path)


def make_profile(tmp_path: Path) -> Path:
    path = tmp_path / "brand.json"
    write_json(path, {
        "brand": "Tik Tots",
        "canonical_url": "tiktotskids.com",
        "forbidden_text": ["www.tiktots.com"],
        "approved_characters": ["Tiko", "Buddy"],
        "interior": {
            "mode": "line_art",
            "max_color_fraction": 0.01,
            "min_width": 1000,
            "min_height": 1000,
            "trim_inches": [8.5, 11],
            "dpi": 300,
        },
    })
    return path


def make_book(tmp_path: Path, pages: list[dict]) -> Path:
    path = tmp_path / "book.json"
    write_json(path, {"title": "Book", "expected_pages": len(pages), "pages": pages})
    return path


def test_coloring_build_is_blocked_by_failed_preflight(tmp_path: Path):
    image = tmp_path / "page.png"
    make_bw(image)
    book = make_book(tmp_path, [{
        "id": "001", "asset": image.name, "kind": "coloring",
        "visible_text": ["www.tiktots.com"], "characters": ["Tiko"],
    }])
    with pytest.raises(ValueError, match="preflight failed"):
        build_coloring_pdf(book, make_profile(tmp_path), tmp_path / "out.pdf")


def test_coloring_build_writes_two_page_pdf(tmp_path: Path):
    first = tmp_path / "001.png"
    second = tmp_path / "002.png"
    make_bw(first, 255)
    make_bw(second, 245)
    pages = [
        {"id": "001", "asset": first.name, "kind": "coloring", "visible_text": ["tiktotskids.com"], "characters": ["Tiko"]},
        {"id": "002", "asset": second.name, "kind": "coloring", "visible_text": ["tiktotskids.com"], "characters": ["Buddy"]},
    ]
    output = tmp_path / "out.pdf"
    result = build_coloring_pdf(make_book(tmp_path, pages), make_profile(tmp_path), output)
    assert result == output
    assert output.exists()
    assert len(PdfReader(str(output)).pages) == 2


def test_fifty_page_build_stays_within_reasonable_memory(tmp_path: Path):
    import subprocess
    import sys
    script = r'''
import json, resource, sys
from pathlib import Path
from PIL import Image
from legacy_books.coloring import build_coloring_pdf
root = Path(sys.argv[1])
limit = 600 * 1024 * 1024
resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
profile = root / "brand.json"
profile.write_text(json.dumps({
    "brand":"Scale Test","canonical_url":"example.com","approved_characters":[],
    "interior":{"mode":"line_art","max_color_fraction":0.01,"min_width":1000,"min_height":1000,"trim_inches":[8.5,11],"dpi":300}
}))
pages=[]
for i in range(50):
    image = root / f"{i:03d}.png"
    page_image = Image.new("L", (1000, 1000), 255)
    page_image.putpixel((i, 0), 0)
    page_image.save(image)
    pages.append({"id":f"{i:03d}","asset":image.name,"kind":"coloring","visible_text":["example.com"],"characters":[]})
book=root / "book.json"
book.write_text(json.dumps({"title":"Fifty","expected_pages":50,"pages":pages}))
build_coloring_pdf(book, profile, root / "out.pdf")
'''
    result = subprocess.run([sys.executable, "-c", script, str(tmp_path)], text=True, capture_output=True, cwd=Path(__file__).parents[1])
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out.pdf").exists()
