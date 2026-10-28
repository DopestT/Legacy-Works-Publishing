from __future__ import annotations

import json
import math
from html import escape
from pathlib import Path

from .models import load_json


def _estimated_duration(text: str, words_per_minute: float) -> float:
    words = len(text.split())
    seconds = words / max(words_per_minute, 1.0) * 60.0
    return round(max(2.0, seconds), 3)


def build_voiceover_package(book_path: str | Path, profile_path: str | Path, output_dir: str | Path) -> dict[str, Path]:
    book = load_json(book_path)
    profile = load_json(profile_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    voice_cfg = profile.get("voiceover", {})
    voice = str(voice_cfg.get("voice", "narrator"))
    words_per_minute = float(voice_cfg.get("words_per_minute", 150))
    approved = set(profile.get("approved_characters", []))

    narration_lines: list[str] = []
    ssml_parts: list[str] = ["<speak>"]
    timeline_pages: list[dict] = []
    queue_items: list[dict] = []
    cursor = 0.0
    seen_ids: set[str] = set()

    for index, page in enumerate(book.get("pages", []), start=1):
        page_id = str(page.get("id", f"{index:03d}"))
        if page_id in seen_ids:
            raise ValueError(f"duplicate page id: {page_id}")
        seen_ids.add(page_id)
        text = str(page.get("narration", "")).strip()
        if not text:
            raise ValueError(f"empty narration on page {page_id}")
        unknown = [name for name in page.get("characters", []) if approved and name not in approved]
        if unknown:
            raise ValueError(f"unknown character on page {page_id}: {', '.join(unknown)}")

        raw_duration = page.get("duration_seconds")
        duration = float(raw_duration if raw_duration is not None else _estimated_duration(text, words_per_minute))
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError(f"duration must be positive on page {page_id}")
        duration = round(duration, 3)
        if duration <= 0:
            raise ValueError(f"duration must be positive on page {page_id}")
        start = round(cursor, 3)
        end = round(start + duration, 3)
        if not math.isfinite(end):
            raise ValueError(f"timeline duration must be finite on page {page_id}")
        cursor = end

        narration_lines.append(text)
        ssml_parts.append(f"  <p>{escape(text)}</p>")
        timeline_pages.append({
            "id": page_id,
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": duration,
        })
        queue_items.append({
            "id": page_id,
            "text": text,
            "voice": voice,
            "output": f"{page_id}.mp3",
        })

    if not timeline_pages:
        raise ValueError("empty narration: story has no pages")

    ssml_parts.append("</speak>")
    outputs = {
        "narration": output_dir / "narration.txt",
        "ssml": output_dir / "narration.ssml",
        "timeline": output_dir / "timeline.json",
        "render_queue": output_dir / "render_queue.json",
    }
    outputs["narration"].write_text("\n\n".join(narration_lines) + "\n", encoding="utf-8")
    outputs["ssml"].write_text("\n".join(ssml_parts) + "\n", encoding="utf-8")
    outputs["timeline"].write_text(json.dumps({
        "title": book.get("title", "Untitled"),
        "duration_seconds": round(cursor, 3),
        "pages": timeline_pages,
    }, indent=2) + "\n", encoding="utf-8")
    outputs["render_queue"].write_text(json.dumps({
        "title": book.get("title", "Untitled"),
        "voice": voice,
        "items": queue_items,
    }, indent=2) + "\n", encoding="utf-8")
    return outputs
