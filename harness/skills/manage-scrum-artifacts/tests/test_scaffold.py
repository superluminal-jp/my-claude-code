from __future__ import annotations

import os
import unittest
from pathlib import Path

from helpers import TEMPLATES, TempRepo, snapshot

PRODUCT_FILES = ["README.md", "definition-of-done.md", "product-backlog.md"]
SPRINT_FILES = [
    "increment.md", "sprint-backlog.md", "sprint-planning.md",
    "sprint-retrospective.md", "sprint-review.md",
]


class InitPlacesTheProductArtifacts(TempRepo):
    def test_init_at_the_root_places_exactly_the_three_product_files(self) -> None:
        result = self.scaffold("init")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.names(self.root / "scrum"), PRODUCT_FILES)

    def test_init_in_a_product_folder_places_them_there_and_not_at_the_root(self) -> None:
        (self.root / "products" / "a").mkdir(parents=True)
        result = self.scaffold("init", "--product", "products/a")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.names(self.root / "products" / "a" / "scrum"), PRODUCT_FILES)
        self.assertFalse((self.root / "scrum").exists())

    def test_placed_files_are_the_bundled_templates_byte_for_byte(self) -> None:
        self.scaffold("init")
        scrum = self.root / "scrum"
        pairs = {
            "product-backlog.md": "product-backlog.md",
            "definition-of-done.md": "definition-of-done.md",
            "README.md": "scrum-readme.md",
        }
        for placed, template in pairs.items():
            with self.subTest(placed=placed):
                self.assertEqual((scrum / placed).read_bytes(), (TEMPLATES / template).read_bytes())


class InitRefusesAProductOutsideTheRoot(TempRepo):
    def refused(self, *args: str) -> None:
        before = snapshot(self.root.parent)
        result = self.scaffold("init", *args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.root.parent), before)

    def test_a_parent_path_is_refused(self) -> None:
        (self.root.parent / "x").mkdir()
        self.refused("--product", "../x")

    def test_an_absolute_path_is_refused(self) -> None:
        outside = self.root.parent / "abs"
        outside.mkdir()
        self.refused("--product", str(outside))

    def test_a_symlink_that_leaves_the_root_is_refused(self) -> None:
        outside = self.root.parent / "outside"
        outside.mkdir()
        os.symlink(outside, self.root / "link")
        self.refused("--product", "link")

    def test_a_missing_folder_is_refused(self) -> None:
        self.refused("--product", "products/none")

    def test_a_scrum_symlink_that_leaves_the_root_is_refused(self) -> None:
        outside = self.root.parent / "elsewhere"
        outside.mkdir()
        os.symlink(outside, self.root / "scrum")
        self.refused()


class SprintAddsTheNextSprintFolder(TempRepo):
    def test_the_first_sprint_is_001_with_the_five_sprint_files(self) -> None:
        self.scaffold("init")
        result = self.scaffold("sprint", "--start", "2026-11-16")
        self.assertEqual(result.returncode, 0, result.stderr)
        sprints = self.root / "scrum" / "sprints"
        self.assertEqual(self.names(sprints), ["001-2026-11-16"])
        self.assertEqual(self.names(sprints / "001-2026-11-16"), SPRINT_FILES)

    def test_the_second_sprint_is_002_and_daily_adds_the_daily_scrum_file(self) -> None:
        self.scaffold("init")
        self.scaffold("sprint", "--start", "2026-11-16")
        result = self.scaffold("sprint", "--start", "2026-11-30", "--daily")
        self.assertEqual(result.returncode, 0, result.stderr)
        sprints = self.root / "scrum" / "sprints"
        self.assertEqual(self.names(sprints), ["001-2026-11-16", "002-2026-11-30"])
        self.assertEqual(self.names(sprints / "002-2026-11-30"), sorted(SPRINT_FILES + ["daily-scrum.md"]))


class SprintRefusesWhatItCannotPlace(TempRepo):
    def refused(self, *args: str) -> None:
        before = snapshot(self.root)
        result = self.scaffold("sprint", *args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_a_month_that_does_not_exist_is_refused(self) -> None:
        self.scaffold("init")
        self.refused("--start", "2026-13-01")

    def test_a_date_without_zero_padding_is_refused(self) -> None:
        self.scaffold("init")
        self.refused("--start", "2026-2-3")

    def test_a_start_not_after_the_latest_sprint_is_refused(self) -> None:
        self.scaffold("init")
        self.scaffold("sprint", "--start", "2026-11-16")
        self.refused("--start", "2026-11-16")
        self.refused("--start", "2026-11-02")

    def test_a_product_without_scrum_is_refused(self) -> None:
        self.refused("--start", "2026-11-16")


class ExistingFilesAreKept(TempRepo):
    def test_a_second_init_keeps_edited_files_and_restores_only_the_missing_one(self) -> None:
        self.scaffold("init")
        scrum = self.root / "scrum"
        (scrum / "product-backlog.md").write_text("edited backlog\n", encoding="utf-8")
        (scrum / "README.md").write_text("edited readme\n", encoding="utf-8")
        (scrum / "definition-of-done.md").unlink()

        result = self.scaffold("init")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((scrum / "product-backlog.md").read_text(encoding="utf-8"), "edited backlog\n")
        self.assertEqual((scrum / "README.md").read_text(encoding="utf-8"), "edited readme\n")
        self.assertEqual(
            (scrum / "definition-of-done.md").read_bytes(),
            (TEMPLATES / "definition-of-done.md").read_bytes(),
        )
        lines = result.stdout.splitlines()
        self.assertIn("created scrum/definition-of-done.md", lines)
        self.assertIn("kept scrum/product-backlog.md", lines)
        self.assertIn("kept scrum/README.md", lines)


if __name__ == "__main__":
    unittest.main()
