import json
from pathlib import Path

from PIL import Image

from legacy_books.preflight import preflight


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def make_image(path: Path, *, color=(255, 255, 255), accent=None) -> None:
    image = Image.new("RGB", (1200, 1600), color)
    if accent:
        for x in range(100, 1100):
            for y in range(100, 300):
                image.putpixel((x, y), accent)
    image.save(path)


def profile(tmp_path: Path) -> Path:
    path = tmp_path / "brand.json"
    write_json(path, {
        "brand": "Tik Tots",
        "canonical_url": "tiktotskids.com",
        "forbidden_text": ["www.tiktots.com", "tiktoktskids.com", "tiktokotskids.com", "tik toks kids.com"],
        "approved_characters": ["Tiko", "Mia", "Jax", "Zee", "Lulu", "Buddy"],
        "interior": {"mode": "line_art", "max_color_fraction": 0.01, "min_width": 1000, "min_height": 1000},
    })
    return path


def book(tmp_path: Path, asset: Path, *, visible_text=None, characters=None) -> Path:
    path = tmp_path / "book.json"
    write_json(path, {
        "title": "Test Book",
        "expected_pages": 1,
        "pages": [{
            "id": "001",
            "asset": asset.name,
            "kind": "coloring",
            "visible_text": visible_text or ["tiktotskids.com"],
            "characters": characters or ["Tiko", "Buddy"],
        }],
    })
    return path


def test_tiktots_canonical_interior_passes(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image)
    report = preflight(book(tmp_path, image), profile(tmp_path))
    assert report.ok is True
    assert report.errors == []


def test_wrong_tiktots_url_blocks_interior(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image)
    report = preflight(book(tmp_path, image, visible_text=["www.tiktots.com"]), profile(tmp_path))
    assert report.ok is False
    assert any(issue.code == "forbidden_text" for issue in report.errors)
    assert any(issue.code == "missing_canonical_url" for issue in report.errors)


def test_unknown_character_blocks_interior(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image)
    report = preflight(book(tmp_path, image, characters=["Tiko", "Pierre"]), profile(tmp_path))
    assert report.ok is False
    assert any(issue.code == "unknown_character" for issue in report.errors)


def test_missing_asset_blocks_interior(tmp_path: Path):
    missing = tmp_path / "missing.png"
    report = preflight(book(tmp_path, missing), profile(tmp_path))
    assert report.ok is False
    assert any(issue.code == "missing_asset" for issue in report.errors)


def test_colored_page_blocks_line_art_interior(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image, accent=(255, 0, 0))
    report = preflight(book(tmp_path, image), profile(tmp_path))
    assert report.ok is False
    assert any(issue.code == "unexpected_color" for issue in report.errors)


def test_duplicate_asset_blocks_interior(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image)
    book_path = tmp_path / "book.json"
    write_json(book_path, {
        "title": "Test Book",
        "expected_pages": 2,
        "pages": [
            {"id": "001", "asset": image.name, "kind": "coloring", "visible_text": ["tiktotskids.com"], "characters": ["Tiko"]},
            {"id": "002", "asset": image.name, "kind": "coloring", "visible_text": ["tiktotskids.com"], "characters": ["Buddy"]},
        ],
    })
    report = preflight(book_path, profile(tmp_path))
    assert report.ok is False
    assert any(issue.code == "duplicate_asset" for issue in report.errors)


def test_duplicate_image_content_blocks_interior_even_with_different_filenames(tmp_path: Path):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    make_image(first)
    second.write_bytes(first.read_bytes())
    book_path = tmp_path / "book.json"
    write_json(book_path, {
        "title": "Test Book",
        "expected_pages": 2,
        "pages": [
            {"id": "001", "asset": first.name, "kind": "coloring", "visible_text": ["tiktotskids.com"], "characters": ["Tiko"]},
            {"id": "002", "asset": second.name, "kind": "coloring", "visible_text": ["tiktotskids.com"], "characters": ["Buddy"]},
        ],
    })
    report = preflight(book_path, profile(tmp_path))
    assert report.ok is False
    assert any(issue.code == "duplicate_content" for issue in report.errors)


def test_profile_can_require_explicit_page_review_approval(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image)
    profile_path = profile(tmp_path)
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    data["interior"]["require_review"] = True
    write_json(profile_path, data)
    report = preflight(book(tmp_path, image), profile_path)
    assert report.ok is False
    assert any(issue.code == "unapproved_page" for issue in report.errors)


def test_low_effective_dpi_blocks_print_interior(tmp_path: Path):
    image = tmp_path / "page.png"
    make_image(image)
    profile_path = profile(tmp_path)
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    data["interior"].update({"trim_inches": [8.5, 11], "min_effective_dpi": 300})
    write_json(profile_path, data)
    report = preflight(book(tmp_path, image), profile_path)
    assert report.ok is False
    assert any(issue.code == "low_effective_dpi" for issue in report.errors)
