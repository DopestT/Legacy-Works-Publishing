from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .coloring import build_coloring_pdf
from .models import load_json
from .preflight import preflight
from .voiceover import build_voiceover_package


def _print_report(report) -> int:
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.ok else 2


def _init_book(profile_path: Path, destination: Path, title: str) -> int:
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(profile_path, destination / "brand.json")
    (destination / "assets").mkdir()
    (destination / "book.json").write_text(json.dumps({
        "title": title,
        "expected_pages": 0,
        "pages": [],
    }, indent=2) + "\n", encoding="utf-8")
    (destination / "story.json").write_text(json.dumps({
        "title": title,
        "pages": [],
    }, indent=2) + "\n", encoding="utf-8")
    print(destination)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="legacy-books", description="Reusable coloring-book and voiceover-book engines")
    sub = parser.add_subparsers(dest="command", required=True)

    pre = sub.add_parser("preflight", help="Validate a coloring-book interior")
    pre.add_argument("book")
    pre.add_argument("--profile", required=True)

    coloring = sub.add_parser("coloring", help="Build a validated coloring-book PDF")
    coloring.add_argument("book")
    coloring.add_argument("--profile", required=True)
    coloring.add_argument("--output", required=True)

    voice = sub.add_parser("voiceover", help="Build a narration/timeline package")
    voice.add_argument("story")
    voice.add_argument("--profile", required=True)
    voice.add_argument("--output-dir", required=True)

    init = sub.add_parser("init-book", help="Create a new book workspace from a reusable brand profile")
    init.add_argument("--profile", required=True)
    init.add_argument("--destination", required=True)
    init.add_argument("--title", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "preflight":
        return _print_report(preflight(args.book, args.profile))
    if args.command == "coloring":
        output = build_coloring_pdf(args.book, args.profile, args.output)
        print(output)
        return 0
    if args.command == "voiceover":
        outputs = build_voiceover_package(args.story, args.profile, args.output_dir)
        print(json.dumps({name: str(path) for name, path in outputs.items()}, indent=2))
        return 0
    if args.command == "init-book":
        return _init_book(Path(args.profile), Path(args.destination), args.title)
    raise AssertionError(args.command)
