import json
from pathlib import Path

import pytest

from legacy_books.voiceover import build_voiceover_package


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def make_profile(tmp_path: Path) -> Path:
    path = tmp_path / "brand.json"
    write_json(path, {
        "brand": "Tik Tots",
        "approved_characters": ["Tiko", "Mia", "Jax", "Zee", "Lulu", "Buddy"],
        "voiceover": {"voice": "warm-kids-narrator", "words_per_minute": 150},
    })
    return path


def make_story(tmp_path: Path, pages: list[dict]) -> Path:
    path = tmp_path / "story.json"
    write_json(path, {"title": "The Endless Scroll", "pages": pages})
    return path


def test_voiceover_rejects_empty_narration(tmp_path: Path):
    story = make_story(tmp_path, [{"id": "001", "narration": "", "characters": ["Tiko"]}])
    with pytest.raises(ValueError, match="empty narration"):
        build_voiceover_package(story, make_profile(tmp_path), tmp_path / "out")


def test_voiceover_writes_deterministic_timeline_and_queue(tmp_path: Path):
    story = make_story(tmp_path, [
        {"id": "001", "narration": "Welcome to Tik Tots.", "duration_seconds": 4.0, "characters": ["Tiko"]},
        {"id": "002", "narration": "A mysterious door appears.", "duration_seconds": 5.5, "characters": ["Tiko", "Buddy"]},
    ])
    outputs = build_voiceover_package(story, make_profile(tmp_path), tmp_path / "out")
    timeline = json.loads(outputs["timeline"].read_text(encoding="utf-8"))
    queue = json.loads(outputs["render_queue"].read_text(encoding="utf-8"))
    assert timeline["duration_seconds"] == 9.5
    assert timeline["pages"] == [
        {"id": "001", "start_seconds": 0.0, "end_seconds": 4.0, "duration_seconds": 4.0},
        {"id": "002", "start_seconds": 4.0, "end_seconds": 9.5, "duration_seconds": 5.5},
    ]
    assert queue["voice"] == "warm-kids-narrator"
    assert queue["items"][0]["output"] == "001.mp3"
    assert outputs["narration"].read_text(encoding="utf-8").startswith("Welcome to Tik Tots.")
    assert "<speak>" in outputs["ssml"].read_text(encoding="utf-8")


def test_voiceover_rejects_duplicate_page_ids(tmp_path: Path):
    story = make_story(tmp_path, [
        {"id": "001", "narration": "First page.", "characters": ["Tiko"]},
        {"id": "001", "narration": "Second page.", "characters": ["Buddy"]},
    ])
    with pytest.raises(ValueError, match="duplicate page id"):
        build_voiceover_package(story, make_profile(tmp_path), tmp_path / "out")


def test_voiceover_rejects_nonpositive_duration(tmp_path: Path):
    story = make_story(tmp_path, [
        {"id": "001", "narration": "This page has bad timing.", "duration_seconds": -1, "characters": ["Tiko"]},
    ])
    with pytest.raises(ValueError, match="duration must be positive"):
        build_voiceover_package(story, make_profile(tmp_path), tmp_path / "out")
