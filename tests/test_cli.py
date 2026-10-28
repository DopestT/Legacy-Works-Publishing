import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "legacy_books", *args], text=True, capture_output=True)


def test_cli_help_lists_core_commands():
    result = run_cli("--help")
    assert result.returncode == 0
    for command in ("preflight", "coloring", "voiceover", "init-book"):
        assert command in result.stdout


def test_init_book_creates_reusable_manifest_templates(tmp_path: Path):
    profile = tmp_path / "brand.json"
    profile.write_text(json.dumps({"brand": "Tik Tots"}), encoding="utf-8")
    destination = tmp_path / "new-book"
    result = run_cli("init-book", "--profile", str(profile), "--destination", str(destination), "--title", "Book Two")
    assert result.returncode == 0, result.stderr
    assert json.loads((destination / "book.json").read_text(encoding="utf-8"))["title"] == "Book Two"
    assert json.loads((destination / "story.json").read_text(encoding="utf-8"))["pages"] == []
    assert json.loads((destination / "brand.json").read_text(encoding="utf-8"))["brand"] == "Tik Tots"
