from __future__ import annotations

from pathlib import Path
import hashlib

from PIL import Image

from .models import Issue, PreflightReport, load_json


def _color_fraction(image: Image.Image) -> float:
    sample = image.convert("RGB")
    sample.thumbnail((300, 300))
    total = sample.width * sample.height
    if total == 0:
        return 0.0
    colored = 0
    pixel_data = sample.get_flattened_data() if hasattr(sample, "get_flattened_data") else sample.getdata()
    for r, g, b in pixel_data:
        if max(r, g, b) - min(r, g, b) > 18:
            colored += 1
    return colored / total


def preflight(book_path: str | Path, profile_path: str | Path) -> PreflightReport:
    book_path = Path(book_path)
    profile_path = Path(profile_path)
    book = load_json(book_path)
    profile = load_json(profile_path)
    errors: list[Issue] = []
    warnings: list[Issue] = []

    pages = book.get("pages", [])
    expected_pages = book.get("expected_pages")
    if expected_pages is not None and len(pages) != expected_pages:
        errors.append(Issue("page_count", f"Expected {expected_pages} pages, found {len(pages)}"))

    approved = set(profile.get("approved_characters", []))
    forbidden = [str(value).lower() for value in profile.get("forbidden_text", [])]
    canonical_url = str(profile.get("canonical_url", "")).lower().strip()
    interior = profile.get("interior", {})
    min_width = int(interior.get("min_width", 1))
    min_height = int(interior.get("min_height", 1))
    line_art = interior.get("mode") == "line_art"
    max_color_fraction = float(interior.get("max_color_fraction", 0.01))
    require_review = bool(interior.get("require_review", False))
    trim_inches = interior.get("trim_inches")
    min_effective_dpi = interior.get("min_effective_dpi")

    seen_ids: set[str] = set()
    seen_assets: set[str] = set()
    seen_hashes: dict[str, str] = {}
    for index, page in enumerate(pages, start=1):
        page_id = str(page.get("id", index))
        if page_id in seen_ids:
            errors.append(Issue("duplicate_page_id", f"Duplicate page id {page_id}", page_id))
        seen_ids.add(page_id)

        for character in page.get("characters", []):
            if approved and character not in approved:
                errors.append(Issue("unknown_character", f"Unapproved character: {character}", page_id))

        if require_review and page.get("review_status") != "approved":
            errors.append(Issue("unapproved_page", "Page has not passed required interior review", page_id))

        visible_text = " ".join(str(value) for value in page.get("visible_text", [])).lower()
        for token in forbidden:
            if token and token in visible_text:
                errors.append(Issue("forbidden_text", f"Forbidden brand text: {token}", page_id))
        if canonical_url and canonical_url not in visible_text:
            errors.append(Issue("missing_canonical_url", f"Missing canonical URL: {canonical_url}", page_id))

        asset_value = page.get("asset")
        if asset_value:
            normalized_asset = str((book_path.parent / asset_value).resolve())
            if normalized_asset in seen_assets:
                errors.append(Issue("duplicate_asset", f"Interior asset reused: {asset_value}", page_id))
            seen_assets.add(normalized_asset)
        if not asset_value:
            errors.append(Issue("missing_asset", "Page has no asset path", page_id))
            continue
        asset = (book_path.parent / asset_value).resolve()
        if not asset.exists():
            errors.append(Issue("missing_asset", f"Asset not found: {asset_value}", page_id))
            continue

        try:
            with Image.open(asset) as image:
                width, height = image.size
                pixels = image.convert("RGBA")
                digest = hashlib.sha256(
                    f"{width}x{height}:RGBA:".encode("ascii") + pixels.tobytes()
                ).hexdigest()
                if digest in seen_hashes:
                    errors.append(Issue("duplicate_content", f"Image content duplicates page {seen_hashes[digest]}", page_id))
                else:
                    seen_hashes[digest] = page_id
                if width < min_width or height < min_height:
                    errors.append(Issue("low_resolution", f"Page is {width}x{height}; minimum is {min_width}x{min_height}", page_id))
                if trim_inches and min_effective_dpi is not None:
                    trim_w, trim_h = float(trim_inches[0]), float(trim_inches[1])
                    if trim_w <= 0 or trim_h <= 0:
                        errors.append(Issue("invalid_trim", f"Invalid trim size: {trim_inches}", page_id))
                    else:
                        effective_dpi = max(width / trim_w, height / trim_h)
                        if effective_dpi < float(min_effective_dpi):
                            errors.append(Issue("low_effective_dpi", f"Effective resolution {effective_dpi:.1f} DPI is below {float(min_effective_dpi):.0f} DPI", page_id))
                if line_art and page.get("kind", "coloring") == "coloring":
                    fraction = _color_fraction(image)
                    if fraction > max_color_fraction:
                        errors.append(Issue("unexpected_color", f"Color fraction {fraction:.3f} exceeds {max_color_fraction:.3f}", page_id))
        except OSError as exc:
            errors.append(Issue("invalid_image", f"Could not open image: {exc}", page_id))

    return PreflightReport(errors=errors, warnings=warnings)
