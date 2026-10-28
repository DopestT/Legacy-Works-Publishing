import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from legacy_books.preflight import preflight
from legacy_books.voiceover import build_voiceover_package


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile = self.root / "profile.json"
        self.profile.write_text("{}")

    def manifest(self, pages):
        path = self.root / "book.json"
        path.write_text(json.dumps({"pages": pages}))
        return path

    def test_reencoded_identical_pixels_are_duplicates(self):
        image = Image.new("RGB", (16, 16), "white")
        image.save(self.root / "first.png", compress_level=0)
        metadata = PngInfo()
        metadata.add_text("export", "another export")
        image.convert("RGBA").save(self.root / "second.png", compress_level=9, pnginfo=metadata)
        self.assertNotEqual((self.root / "first.png").read_bytes(), (self.root / "second.png").read_bytes())
        report = preflight(self.manifest([
            {"id": "1", "asset": "first.png"}, {"id": "2", "asset": "second.png"},
        ]), self.profile)
        self.assertIn("duplicate_content", [issue.code for issue in report.errors])

    def test_case_distinct_files_remain_distinct(self):
        Image.new("RGB", (16, 16), "white").save(self.root / "Page.png")
        if (self.root / "page.png").exists():
            self.skipTest("requires a case-sensitive filesystem")
        Image.new("RGB", (16, 16), "black").save(self.root / "page.png")
        report = preflight(self.manifest([
            {"id": "1", "asset": "Page.png"}, {"id": "2", "asset": "page.png"},
        ]), self.profile)
        self.assertTrue(report.ok, report.errors)

    def test_path_alias_is_reused_asset(self):
        Image.new("RGB", (16, 16), "white").save(self.root / "page.png")
        report = preflight(self.manifest([
            {"id": "1", "asset": "page.png"}, {"id": "2", "asset": "./page.png"},
        ]), self.profile)
        self.assertIn("duplicate_asset", [issue.code for issue in report.errors])

    def test_invalid_durations_do_not_write_outputs(self):
        for duration in [float("inf"), float("-inf"), float("nan"), 0.0001]:
            with self.subTest(duration=duration):
                story = self.manifest([{"narration": "Hello.", "duration_seconds": duration}])
                with self.assertRaises(ValueError):
                    build_voiceover_package(story, self.profile, self.root / "out")
                self.assertFalse((self.root / "out" / "timeline.json").exists())

    def test_cumulative_timeline_overflow_is_rejected(self):
        story = self.manifest([
            {"id": str(i), "narration": "Hello.", "duration_seconds": 1e308}
            for i in range(2)
        ])
        with self.assertRaises(ValueError):
            build_voiceover_package(story, self.profile, self.root / "out")

    def test_existing_preflight_suite(self):
        spec = importlib.util.spec_from_file_location("existing_preflight", Path(__file__).with_name("test_preflight.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in sorted(vars(module)):
            if name.startswith("test_"):
                with self.subTest(test=name), tempfile.TemporaryDirectory() as directory:
                    getattr(module, name)(Path(directory))
