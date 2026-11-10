"""Tests for this Skill's bundled scripts (not for the target project)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))

import common  # noqa: E402
from common import classify, excluded  # noqa: E402

HAS_GIT = shutil.which("git") is not None


def run_script(name: str, *args: str, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def write(root: Path, rel: str, text: str = "") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def init_repo(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "user.name", "Skill Test")
    git(root, "config", "commit.gpgsign", "false")


def commit_all(root: Path, message: str = "commit") -> None:
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)


class TempDirTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name).resolve()

    def tearDown(self) -> None:
        self._td.cleanup()


# ---------------------------------------------------------------------------
# Exclusion and classification
# ---------------------------------------------------------------------------

class ExclusionTests(unittest.TestCase):
    def test_vcs_directories_are_excluded(self):
        self.assertTrue(excluded(".git", {}, is_dir=True))
        self.assertTrue(excluded(".git/config", {}))

    def test_dependency_trees_are_excluded_at_any_depth(self):
        self.assertTrue(excluded("packages/a/node_modules/x/README.md", {}))
        self.assertTrue(excluded("services/api/.venv", {}, is_dir=True))

    def test_build_dirs_only_excluded_at_top_level(self):
        self.assertTrue(excluded("build/out.txt", {}))
        self.assertFalse(excluded("src/build/rules.py", {}))

    def test_dot_prefixed_user_globs_work(self):
        config = {"exclude_globs": [".github/**"]}
        self.assertTrue(excluded(".github", config, is_dir=True))
        self.assertTrue(excluded(".github/workflows/ci.yml", config))

    def test_double_star_prefix_matches_top_level(self):
        config = {"exclude_globs": ["**/fixtures/**"]}
        self.assertTrue(excluded("fixtures/a.md", config))
        self.assertTrue(excluded("tests/fixtures/a.md", config))


class ClassificationTests(unittest.TestCase):
    CASES = {
        "src/api/handlers.py": {"implementation"},
        "requirements.txt": {"configuration"},
        "requirements-dev.txt": {"configuration"},
        "CMakeLists.txt": {"configuration"},
        "src/quadr-tree.c": {"implementation"},
        "docs/adr/0001-use-postgres.md": {"documentation", "decision"},
        "docs/decisions/0002-x.md": {"documentation", "decision"},
        "ADR-0003-queue.md": {"documentation", "decision"},
        ".github/workflows/ci.yml": {"infrastructure"},
        "Dockerfile": {"infrastructure"},
        "deploy/main.tf": {"infrastructure"},
        "openapi.yaml": {"specification"},
        "proto/service.proto": {"specification"},
        "tests/test_app.py": {"evidence"},
        "src/app.test.ts": {"evidence"},
        "src/main/java/FooTest.java": {"evidence"},
        "src/main/java/Latest.java": {"implementation"},
        "CHANGELOG.md": {"documentation"},
        "README": {"documentation"},
        "notes.txt": {"implementation"},
        "docs/notes.txt": {"documentation"},
        "api/service_pb2.py": {"generated"},
        "main.bicepparam": {"infrastructure"},
        ".github/actions/setup/action.yml": {"infrastructure"},
        "action.yaml": {"infrastructure"},
        "cdk.json": {"infrastructure"},
        "host.json": {"configuration"},
        "src/functions/http/function.json": {"configuration"},
        "vite.config.ts": {"configuration"},
        "next.config.mjs": {"configuration"},
    }

    def test_heuristics(self):
        for path, expected in self.CASES.items():
            with self.subTest(path=path):
                self.assertEqual(classify(path, {}), expected)

    def test_config_globs_override_heuristics(self):
        config = {"implementation_globs": ["spec/**"]}
        self.assertEqual(classify("spec/helpers.rb", config), {"implementation"})
        self.assertIn("evidence", classify("spec/helpers.rb", {}))

    def test_changelog_detection(self):
        for path in ("CHANGELOG.md", "HISTORY.rst", "changelog.d/123.feature.md", ".changeset/x.md"):
            with self.subTest(path=path):
                self.assertTrue(common.is_changelog(path))
        self.assertFalse(common.is_changelog("docs/history-of-the-project-team.png"))


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class ConfigTests(TempDirTestCase):
    def test_schema_key_is_accepted(self):
        write(self.root, ".living-documentation.json", json.dumps({"$schema": "x", "decision_globs": []}))
        self.assertEqual(common.load_config(self.root)["decision_globs"], [])

    def test_unknown_key_is_rejected(self):
        write(self.root, ".living-documentation.json", json.dumps({"docs_globs": []}))
        with self.assertRaises(common.ConfigError):
            common.load_config(self.root)

    def test_wrong_type_is_rejected(self):
        write(self.root, ".living-documentation.json", json.dumps({"exclude_globs": "docs/**"}))
        with self.assertRaises(common.ConfigError):
            common.load_config(self.root)

    def test_related_settings_are_validated(self):  # C1 (slice S2)
        write(self.root, ".living-documentation.json", json.dumps({"related": {"max_candidates": 3, "min_name_length": 4}}))
        self.assertEqual(common.load_config(self.root)["related"], {"max_candidates": 3, "min_name_length": 4})
        bad_settings = [("x", "related"), ({"max_candidates": 0}, "related.max_candidates"),
                        ({"max_candidates": True}, "related.max_candidates"),
                        ({"min_name_length": "6"}, "related.min_name_length"),
                        ({"min_name_length": 2.5}, "related.min_name_length"),
                        ({"unknown": 1}, "related.unknown")]
        for value, needle in bad_settings:
            with self.subTest(value=value):
                write(self.root, ".living-documentation.json", json.dumps({"related": value}))
                with self.assertRaises(common.ConfigError) as caught:
                    common.load_config(self.root)
                self.assertIn(needle, str(caught.exception))

    def test_loader_and_schema_agree(self):
        schema = json.loads(common.SCHEMA_PATH.read_text(encoding="utf-8"))
        glob_keys = {k for k in schema["properties"] if k.endswith("_globs") and k != "exclude_globs"}
        self.assertEqual(glob_keys, {f"{c}_globs" for c in common.CATEGORIES})

    def test_custom_classification_via_inspect(self):
        write(self.root, ".living-documentation.json", json.dumps({"decision_globs": ["records/*.txt"]}))
        write(self.root, "records/choice.txt", "decision")
        proc = run_script("inspect_project.py", "--root", str(self.root), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertGreaterEqual(json.loads(proc.stdout)["categories"].get("decision", 0), 1)


# ---------------------------------------------------------------------------
# inspect_project.py
# ---------------------------------------------------------------------------

class InspectTests(TempDirTestCase):
    def test_discovers_without_fixed_layout(self):
        write(self.root, "knowledge/overview.md", "# Overview\n")
        write(self.root, "contracts/service.proto", 'syntax = "proto3";\n')
        proc = run_script("inspect_project.py", "--root", str(self.root), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertGreaterEqual(data["categories"].get("documentation", 0), 1)
        self.assertGreaterEqual(data["categories"].get("specification", 0), 1)

    def test_filesystem_walk_skips_excluded_trees(self):
        write(self.root, ".git/HEAD", "ref: refs/heads/main\n")
        write(self.root, "pkg/node_modules/x/README.md", "# junk\n")
        write(self.root, "README.md", "# Real\n")
        proc = run_script("inspect_project.py", "--root", str(self.root), "--json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["files_scanned"], 1)
        self.assertNotIn(".git", data["top_directories"])

    @unittest.skipUnless(HAS_GIT, "git not installed")
    def test_git_listing_honors_gitignore(self):
        init_repo(self.root)
        write(self.root, ".gitignore", "secret-output/\n")
        write(self.root, "secret-output/report.md", "# generated\n")
        write(self.root, "README.md", "# Real\n")
        proc = run_script("inspect_project.py", "--root", str(self.root), "--json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["file_source"], "git")
        self.assertNotIn("secret-output/report.md", json.dumps(data["examples"]))

    def test_does_not_shadow_stdlib_inspect(self):
        proc = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import inspect; print(inspect.__file__)",
             str(SCRIPTS)],
            text=True, stdout=subprocess.PIPE,
        )
        self.assertNotIn(str(SCRIPTS), proc.stdout)


# ---------------------------------------------------------------------------
# audit.py
# ---------------------------------------------------------------------------

@unittest.skipUnless(HAS_GIT, "git not installed")
class AuditTests(TempDirTestCase):
    def setUp(self) -> None:
        super().setUp()
        init_repo(self.root)
        write(self.root, "app.py", "print('v1')\n")
        write(self.root, "CHANGELOG.md", "# Changelog\n")
        write(self.root, "docs/guide.md", "# Guide\n")
        commit_all(self.root, "initial")

    def audit(self, *args: str) -> dict:
        proc = run_script("audit.py", "--root", str(self.root), "--json", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_classifies_worktree_change(self):
        write(self.root, "app.py", "print('v2')\n")
        data = self.audit()
        self.assertEqual([c["path"] for c in data["changes"]], ["app.py"])
        self.assertIn("implementation", data["categories"])

    def test_hints_missing_changelog_and_docs(self):
        write(self.root, "app.py", "print('v2')\n")
        hints = " ".join(self.audit()["possible_impacts"])
        self.assertIn("CHANGELOG.md", hints)
        self.assertIn("No documentation file changed", hints)

    def test_reports_renames(self):
        git(self.root, "mv", "docs/guide.md", "docs/howto.md")
        data = self.audit()
        self.assertEqual(data["changes"][0]["old_path"], "docs/guide.md")
        self.assertIn("deleted or renamed", " ".join(data["possible_impacts"]))

    def test_includes_untracked_files(self):
        write(self.root, "new_module.py", "x = 1\n")
        self.assertIn("new_module.py", [c["path"] for c in self.audit()["changes"]])

    def test_base_includes_committed_and_uncommitted(self):
        git(self.root, "branch", "-M", "main")
        git(self.root, "checkout", "-qb", "feature")
        write(self.root, "committed.py", "x = 1\n")
        commit_all(self.root, "feature work")
        write(self.root, "app.py", "print('dirty')\n")
        paths = [c["path"] for c in self.audit("--base", "main")["changes"]]
        self.assertEqual(paths, ["app.py", "committed.py"])

    def test_root_may_be_a_subdirectory(self):
        write(self.root, "pkg/lib.py", "x = 1\n")
        commit_all(self.root)
        write(self.root, "pkg/lib.py", "x = 2\n")
        write(self.root, "app.py", "print('v2')\n")
        proc = run_script("audit.py", "--root", str(self.root / "pkg"), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual([c["path"] for c in json.loads(proc.stdout)["changes"]], ["lib.py"])

    def test_missing_git_binary_is_a_clean_error(self):
        env = dict(os.environ, PATH=str(self.root / "no-such-bin"))
        proc = run_script("audit.py", "--root", str(self.root), env=env)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("git is not installed", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


@unittest.skipUnless(HAS_GIT, "git not installed")
class DecisionRecordAuditTests(TempDirTestCase):
    ACCEPTED = ("---\nstatus: accepted\ndate: 2026-01-01\ndecision-makers: Team\n---\n\n"
                "# 0001. Use PostgreSQL\n\n## Context and Problem Statement\n\nWe need a datastore.\n\n"
                "## Decision Outcome\n\nChosen option: \"PostgreSQL\", because of transactions.\n")

    def setUp(self) -> None:
        super().setUp()
        init_repo(self.root)
        write(self.root, "docs/decisions/0001-use-postgresql.md", self.ACCEPTED)
        write(self.root, "docs/decisions/0002-draft.md", self.ACCEPTED.replace("accepted", "proposed"))
        commit_all(self.root)

    def modified(self, *args: str) -> list[str]:
        proc = run_script("audit.py", "--root", str(self.root), "--json", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)["accepted_records_modified"]

    def test_substance_edit_of_accepted_record_is_flagged(self):
        write(self.root, "docs/decisions/0001-use-postgresql.md",
              self.ACCEPTED.replace("because of transactions", "because it is popular"))
        self.assertEqual(self.modified(), ["docs/decisions/0001-use-postgresql.md"])

    def test_status_and_supersession_links_are_allowed(self):
        text = self.ACCEPTED.replace("status: accepted", "status: superseded by 0003").replace(
            "2026-01-01", "2026-02-01") + "\n## More Information\n\nSuperseded by [0003](0003-use-sqlite.md).\n"
        write(self.root, "docs/decisions/0001-use-postgresql.md", text)
        self.assertEqual(self.modified(), [])

    def test_deleting_accepted_record_is_flagged(self):
        (self.root / "docs/decisions/0001-use-postgresql.md").unlink()
        self.assertEqual(self.modified(), ["docs/decisions/0001-use-postgresql.md (deleted)"])

    def test_proposed_records_may_change(self):
        write(self.root, "docs/decisions/0002-draft.md", self.ACCEPTED.replace("accepted", "proposed") + "\nMore.\n")
        self.assertEqual(self.modified(), [])

    def test_bullet_status_format_and_base_mode(self):
        write(self.root, "adr/0003-queue.md", "# ADR-0003: Queue\n\n- Status: Accepted\n\n## Decision\n\nUse a queue.\n")
        commit_all(self.root)
        git(self.root, "branch", "-M", "main")
        git(self.root, "checkout", "-qb", "feature")
        write(self.root, "adr/0003-queue.md", "# ADR-0003: Queue\n\n- Status: Accepted\n\n## Decision\n\nUse a stream.\n")
        commit_all(self.root, "rewrite decision")
        self.assertEqual(self.modified("--base", "main"), ["adr/0003-queue.md"])

    def test_record_status_parsing(self):
        self.assertEqual(common.record_status("---\nstatus: \"Accepted\"\n---"), "accepted")
        self.assertEqual(common.record_status("# T\n\n## Status\n\nSuperseded by 0004\n"), "superseded")
        self.assertIsNone(common.record_status("# No status here\n"))


class AuditWithoutRepoTests(TempDirTestCase):
    def test_non_git_directory_is_a_clean_error(self):
        proc = run_script("audit.py", "--root", str(self.root))
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)


# ---------------------------------------------------------------------------
# check_links.py
# ---------------------------------------------------------------------------

class CheckLinksTests(TempDirTestCase):
    def check(self, *args: str) -> tuple[int, dict]:
        proc = run_script("check_links.py", "--root", str(self.root), "--json", *args)
        self.assertIn(proc.returncode, (0, 1), proc.stderr)
        return proc.returncode, json.loads(proc.stdout)

    def test_accepts_valid_relative_link(self):
        write(self.root, "docs/a.md", "[B](b.md)\n")
        write(self.root, "docs/b.md", "# B\n")
        self.assertEqual(self.check()[0], 0)

    def test_rejects_missing_relative_link(self):
        write(self.root, "note.md", "[Missing](nope.md)\n")
        rc, data = self.check()
        self.assertEqual(rc, 1)
        self.assertEqual(data["errors"][0]["message"], "missing local target")

    def test_ignores_code_blocks_inline_code_and_comments(self):
        write(self.root, "a.md",
              "```md\n[x](fake1.md)\n```\n\n~~~\n[x](fake2.md)\n~~~\n\nUse `[x](fake3.md)`.\n\n<!-- [x](fake4.md) -->\n")
        rc, data = self.check()
        self.assertEqual(rc, 0, data)

    def test_checks_reference_definitions_and_html(self):
        write(self.root, "a.md", "[ref]: missing-ref.md\n\n<img src=\"missing.png\">\n")
        rc, data = self.check()
        self.assertEqual({e["target"] for e in data["errors"]}, {"missing-ref.md", "missing.png"})

    def test_link_titles_and_angle_brackets(self):
        write(self.root, "b c.md", "# B\n")
        write(self.root, "a.md", '[t](<b c.md> "Title") [u](b%20c.md \'t\')\n')
        self.assertEqual(self.check()[0], 0)

    def test_root_relative_links_use_site_root(self):
        write(self.root, "site/guide.md", "# Guide\n")
        write(self.root, "README.md", "[g](/site/guide.md) [h](/guide.md)\n")
        rc, data = self.check()
        self.assertEqual(rc, 0)
        self.assertEqual(len(data["warnings"]), 1)  # /guide.md not under the project root
        rc, data = self.check("--site-root", "site")
        self.assertEqual(len(data["warnings"]), 1)  # now /site/guide.md is the unresolved one
        rc, data = self.check("--site-root", ".", "--site-root", "site")
        self.assertEqual(data["warnings"], [])

    def test_relative_link_escaping_root_is_an_error(self):
        write(self.root, "a.md", "[up](../outside.md)\n")
        rc, data = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("escapes", data["errors"][0]["message"])

    def test_anchor_checks(self):
        write(self.root, "b.md", "# Title\n\n## Section Two\n\n## Section Two\n\nSetext\n------\n\n### Custom {#custom-id}\n\n<a id=\"html-anchor\"></a>\n")
        write(self.root, "a.md",
              "[1](b.md#section-two) [2](b.md#section-two-1) [3](b.md#setext) [4](b.md#custom-id) "
              "[5](b.md#html-anchor) [6](#local)\n\n## Local\n")
        rc, data = self.check()
        self.assertEqual((rc, data["warnings"]), (0, []))
        write(self.root, "c.md", "[bad](b.md#nope)\n")
        rc, data = self.check()
        self.assertEqual((rc, len(data["warnings"])), (0, 1))
        rc, _ = self.check("--strict")
        self.assertEqual(rc, 1)

    def test_non_latin_heading_anchors(self):
        write(self.root, "b.md", "## 設計方針 (概要)\n\n## प्रोग्रामिंग भाषाएँ\n\n## Instana + Logz.io\n")
        write(self.root, "a.md", "[x](b.md#設計方針-概要) [y](b.md#प्रोग्रामिंग-भाषाएँ) [z](b.md#instana--logzio)\n")
        self.assertEqual(self.check()[1]["warnings"], [])

    @unittest.skipUnless(HAS_GIT, "git not installed")
    def test_changed_mode_ignores_preexisting_breakage(self):
        init_repo(self.root)
        write(self.root, "old.md", "[broken](missing.md)\n")
        write(self.root, "target.md", "# Target\n")
        write(self.root, "linker.md", "[t](target.md)\n")
        commit_all(self.root)
        write(self.root, "new.md", "[also broken](nope.md)\n")
        git(self.root, "rm", "-q", "target.md")
        rc, data = self.check("--changed")
        self.assertEqual(rc, 1)
        sources = sorted(e["source"] for e in data["errors"])
        self.assertEqual(sources, ["linker.md", "new.md"])  # not old.md

    def test_skill_own_documentation_passes(self):
        proc = run_script("check_links.py", "--root", str(SKILL_ROOT), "--strict")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


# ---------------------------------------------------------------------------
# stop_gate.py (Claude Code hook)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Plugin packaging
# ---------------------------------------------------------------------------

class FindRelatedTests(TempDirTestCase):
    """find_related.py lists the documents next to changed files (contract C1, proximity P1)."""

    def setUp(self) -> None:
        super().setUp()
        init_repo(self.root)
        write(self.root, "app.py", "print('v1')\n")
        write(self.root, "README.md", "# Project\n")
        write(self.root, "src/x.py", "print('x')\n")
        write(self.root, "src/README.md", "# src\n")
        write(self.root, "src/design.md", "# design\n")
        commit_all(self.root, "initial")

    def related(self, *args: str, root: Path | None = None) -> dict:
        proc = run_script("find_related.py", "--root", str(root or self.root), "--json", *args)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    @staticmethod
    def pairs(data: dict) -> list[tuple[str, str]]:
        """(source, path) of the document candidates; advisory comment records (P0) are left out."""
        return [(c["source"], c["path"]) for c in data["candidates"] if c["kind"] != "comment"]

    @staticmethod
    def of_kind(data: dict, kind: str) -> list[dict]:
        return [c for c in data["candidates"] if c["kind"] == kind]

    def commit_files(self, **files: str) -> None:
        """Write files (keyword names use '__' for '/' and '_dot_' for '.') and commit them."""
        for name, text in files.items():
            write(self.root, name.replace("__", "/").replace("_dot_", "."), text)
        commit_all(self.root, "fixture")

    def use_settings(self, **related: int) -> None:
        write(self.root, ".living-documentation.json", json.dumps({"related": related}))
        commit_all(self.root, "settings")

    def status(self) -> str:
        return subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=self.root,
                              text=True, stdout=subprocess.PIPE, check=True).stdout

    def test_lists_sibling_documents_of_a_changed_file(self):  # F1, SC-003
        write(self.root, "src/x.py", "print('x2')\n")
        before = self.status()
        data = self.related()
        self.assertEqual(set(data), {"changed", "candidates", "truncated"})
        self.assertEqual(data["changed"], ["src/x.py"])
        self.assertEqual(data["truncated"], 0)
        self.assertEqual(self.pairs(data), [("src/x.py", "src/README.md"), ("src/x.py", "src/design.md")])
        self.assertEqual({c["kind"] for c in data["candidates"]}, {"sibling", "comment"})  # comment: slice S2
        for candidate in self.of_kind(data, "sibling"):
            self.assertEqual(candidate["proximity"], "P1")
        for candidate in data["candidates"]:
            self.assertTrue(candidate["reason"])
        self.assertEqual(self.status(), before)  # read-only

    def test_changed_documents_are_not_candidates(self):  # F2
        write(self.root, "src/x.py", "print('x2')\n")
        write(self.root, "src/README.md", "# src, updated\n")
        data = self.related()
        self.assertEqual(data["changed"], ["src/README.md", "src/x.py"])
        self.assertEqual(self.pairs(data), [("src/x.py", "src/design.md")])

    def test_excluded_and_ignored_documents_are_not_candidates(self):  # F3
        write(self.root, ".living-documentation.json", json.dumps({"exclude_globs": ["src/design.md"]}))
        write(self.root, ".gitignore", "src/notes.md\n")
        write(self.root, "src/notes.md", "# ignored\n")
        commit_all(self.root, "config")
        write(self.root, "src/x.py", "print('x2')\n")
        self.assertEqual(self.pairs(self.related()), [("src/x.py", "src/README.md")])

    def test_document_only_change_has_no_candidates(self):  # F4
        write(self.root, "src/README.md", "# src, updated\n")
        data = self.related()
        self.assertEqual(data["changed"], ["src/README.md"])
        self.assertEqual(data["candidates"], [])

    def test_root_level_source_finds_root_readme(self):  # F5
        write(self.root, "app.py", "print('v2')\n")
        self.assertEqual(self.pairs(self.related()), [("app.py", "README.md")])

    def test_one_record_per_source_and_document_in_stable_order(self):  # F6
        write(self.root, "src/x.py", "print('x2')\n")
        write(self.root, "src/y.py", "print('y')\n")
        data = self.related()
        self.assertEqual(self.pairs(data), [
            ("src/x.py", "src/README.md"), ("src/y.py", "src/README.md"),
            ("src/x.py", "src/design.md"), ("src/y.py", "src/design.md"),
        ])
        first = run_script("find_related.py", "--root", str(self.root), "--json").stdout
        second = run_script("find_related.py", "--root", str(self.root), "--json").stdout
        self.assertEqual(first, second)

    def test_base_includes_committed_changes(self):  # F7
        git(self.root, "branch", "base")
        write(self.root, "src/x.py", "print('x2')\n")
        commit_all(self.root, "change x")
        self.assertEqual(self.related()["candidates"], [])
        self.assertEqual(self.pairs(self.related("--base", "base")),
                         [("src/x.py", "src/README.md"), ("src/x.py", "src/design.md")])

    def test_outside_git_is_a_clean_error_and_writes_nothing(self):  # F8
        with tempfile.TemporaryDirectory() as td:
            plain = Path(td).resolve()
            write(plain, "x.py", "print('x')\n")
            before = sorted((p.relative_to(plain).as_posix(), p.read_bytes()) for p in plain.rglob("*") if p.is_file())
            proc = run_script("find_related.py", "--root", str(plain))
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Git", proc.stderr)
            after = sorted((p.relative_to(plain).as_posix(), p.read_bytes()) for p in plain.rglob("*") if p.is_file())
            self.assertEqual(before, after)

    def test_deleted_source_still_finds_documents_but_deleted_documents_are_not_candidates(self):  # F9
        (self.root / "src/x.py").unlink()
        self.assertEqual(self.pairs(self.related()),
                         [("src/x.py", "src/README.md"), ("src/x.py", "src/design.md")])
        (self.root / "src/design.md").unlink()
        self.assertEqual(self.pairs(self.related()), [("src/x.py", "src/README.md")])

    def test_renamed_source_uses_its_new_directory(self):  # F9
        git(self.root, "mv", "src/x.py", "src/z.py")
        self.assertEqual(self.pairs(self.related()),
                         [("src/z.py", "src/README.md"), ("src/z.py", "src/design.md")])

    # --- Slice S2: mentions (P2), change history (P3), comments (P0), settings and cap ---

    def setup_install_script(self, doc_text: str = "Run scripts/install.sh first.\n") -> None:
        self.commit_files(scripts__install_dot_sh="echo hi\n", docs__setup_dot_md=doc_text)

    def change_install_script(self) -> dict:
        write(self.root, "scripts/install.sh", "echo hi2\n")
        return self.related()

    def test_document_naming_a_changed_path_is_a_mention(self):  # M1
        self.setup_install_script()
        mention = self.of_kind(self.change_install_script(), "mention")
        self.assertEqual([(c["source"], c["path"], c["proximity"]) for c in mention],
                         [("scripts/install.sh", "docs/setup.md", "P2")])
        self.assertIn("scripts/install.sh", mention[0]["reason"])

    def test_file_name_mentions_need_the_minimum_length(self):  # M2
        self.commit_files(docs__a_dot_md="This page uses x.py heavily.\n", docs__b_dot_md="See src/x.py for details.\n",
                          docs__c_dot_md="Run install.sh.\n", scripts__install_dot_sh="echo hi\n")
        write(self.root, "src/x.py", "print('x2')\n")
        write(self.root, "scripts/install.sh", "echo hi2\n")
        mentions = {(c["source"], c["path"]) for c in self.of_kind(self.related(), "mention")}
        self.assertEqual(mentions, {("src/x.py", "docs/b.md"), ("scripts/install.sh", "docs/c.md")})

    def test_partial_word_matches_are_not_mentions(self):  # M3
        self.setup_install_script("reinstall.sh and install.shx and my-install.sh are different.\n")
        self.assertEqual(self.of_kind(self.change_install_script(), "mention"), [])

    def test_a_sibling_that_also_names_the_file_is_listed_once(self):  # M4
        self.commit_files(scripts__install_dot_sh="echo hi\n", scripts__NOTES_dot_md="Edit scripts/install.sh.\n")
        data = self.change_install_script()
        records = [(c["kind"], c["path"]) for c in data["candidates"] if c["path"] == "scripts/NOTES.md"]
        self.assertEqual(records, [("sibling", "scripts/NOTES.md")])

    def test_changed_excluded_decision_and_history_documents_are_not_mentions(self):  # M5
        text = "Uses scripts/install.sh.\n"
        write(self.root, ".living-documentation.json", json.dumps({"exclude_globs": ["docs/private/*"]}))
        self.commit_files(scripts__install_dot_sh="echo hi\n", docs__changed_dot_md=text, docs__private__p_dot_md=text,
                          docs__adr__0001_x_dot_md=text, CHANGELOG_dot_md=text)
        write(self.root, "docs/changed.md", text + "More.\n")
        self.assertEqual(self.of_kind(self.change_install_script(), "mention"), [])

    def test_a_deleted_file_still_finds_documents_that_name_it(self):  # M6
        self.setup_install_script()
        (self.root / "scripts/install.sh").unlink()
        mention = self.of_kind(self.related(), "mention")
        self.assertEqual([c["path"] for c in mention], ["docs/setup.md"])

    def test_unreadable_and_huge_documents_are_skipped(self):  # M7
        self.setup_install_script()
        (self.root / "docs/bad.md").write_bytes(b"\xff\xfe scripts/install.sh \xff")
        (self.root / "docs/big.md").write_text("scripts/install.sh " + "x" * (1024 * 1024 + 1), encoding="utf-8")
        commit_all(self.root, "unreadable and huge")
        mention = self.of_kind(self.change_install_script(), "mention")
        self.assertEqual([c["path"] for c in mention], ["docs/setup.md"])

    def test_changelog_is_a_candidate_for_user_visible_changes(self):  # H1
        self.commit_files(CHANGELOG_dot_md="# Changelog\n")
        write(self.root, "src/x.py", "print('x2')\n")
        changelog = self.of_kind(self.related(), "changelog")
        self.assertEqual([(c["path"], c["source"], c["proximity"]) for c in changelog],
                         [("CHANGELOG.md", "src/x.py", "P3")])

    def test_no_changelog_candidate_when_history_changed_or_absent_or_not_user_visible(self):  # H1
        write(self.root, "src/x.py", "print('x2')\n")
        self.assertEqual(self.of_kind(self.related(), "changelog"), [])  # the project keeps no change history
        self.commit_files(CHANGELOG_dot_md="# Changelog\n")
        write(self.root, "CHANGELOG.md", "# Changelog\n\n- x\n")
        self.assertEqual(self.of_kind(self.related(), "changelog"), [])  # history already updated
        git(self.root, "checkout", "--", "CHANGELOG.md", "src/x.py")
        write(self.root, "tests/test_a.py", "def test_a(): pass\n")
        self.assertEqual(self.of_kind(self.related(), "changelog"), [])  # tests are not user-visible
        git(self.root, "stash", "-u", "-q")
        write(self.root, "src/design.md", "# design, updated\n")
        self.assertEqual(self.of_kind(self.related(), "changelog"), [])  # documentation only

    def test_only_a_project_level_changelog_counts_as_change_history(self):  # H3 (re-plan after the A1 measurement)
        self.commit_files(vendor__lib__changelog_dot_md="# vendored changelog\n")
        write(self.root, "src/x.py", "print('x2')\n")
        self.assertEqual(self.of_kind(self.related(), "changelog"), [])  # nested changelogs belong to vendored code
        git(self.root, "checkout", "--", "src/x.py")
        self.commit_files(CHANGELOG_dot_md="# Changelog\n")
        write(self.root, "src/x.py", "print('x3')\n")
        write(self.root, "vendor/lib/changelog.md", "# vendored changelog, updated\n")  # not the project's history
        self.assertEqual([c["path"] for c in self.of_kind(self.related(), "changelog")], ["CHANGELOG.md"])

    def test_changelog_candidate_is_one_per_file_with_a_count(self):  # H2
        self.commit_files(CHANGELOG_dot_md="# Changelog\n")
        write(self.root, "src/x.py", "print('x2')\n")
        write(self.root, "app.py", "print('v2')\n")
        changelog = self.of_kind(self.related(), "changelog")
        self.assertEqual(len(changelog), 1)
        self.assertEqual(changelog[0]["source"], "app.py")
        self.assertIn("2", changelog[0]["reason"])

    def test_comment_records_are_advisory_and_only_for_implementation_files(self):  # K1
        write(self.root, "src/x.py", "print('x2')\n")
        comments = self.of_kind(self.related(), "comment")
        self.assertEqual([(c["source"], c["path"], c["proximity"]) for c in comments], [("src/x.py", "src/x.py", "P0")])
        write(self.root, "pyproject.toml", "[project]\n")
        write(self.root, "tests/test_a.py", "def test_a(): pass\n")
        write(self.root, "src/design.md", "# design, updated\n")
        self.assertEqual([c["source"] for c in self.of_kind(self.related(), "comment")], ["src/x.py"])

    def cap_fixture(self, cap: int) -> dict:
        self.commit_files(docs__a_dot_md="Edit src/x.py.\n", docs__b_dot_md="Edit src/x.py.\n", CHANGELOG_dot_md="# Changelog\n")
        self.use_settings(max_candidates=cap)
        write(self.root, "src/x.py", "print('x2')\n")
        return self.related()

    def test_max_candidates_keeps_the_closest_documents_and_counts_the_rest(self):  # X1
        data = self.cap_fixture(2)
        self.assertEqual(self.pairs(data), [("src/x.py", "src/README.md"), ("src/x.py", "src/design.md")])
        self.assertEqual(data["truncated"], 3)  # docs/a.md, docs/b.md, CHANGELOG.md
        self.assertEqual(len(self.of_kind(data, "comment")), 1)  # advisory records are not counted

    def test_documents_beyond_the_cap_are_cut_by_proximity_then_path(self):  # X1
        data = self.cap_fixture(3)
        self.assertEqual([p for _, p in self.pairs(data)], ["src/README.md", "src/design.md", "docs/a.md"])
        self.assertEqual(data["truncated"], 2)

    def test_min_name_length_setting_changes_what_counts_as_a_mention(self):  # X2
        self.commit_files(docs__m_dot_md="Run install.sh.\n", scripts__install_dot_sh="echo hi\n")
        self.assertEqual(len(self.of_kind(self.change_install_script(), "mention")), 1)
        self.use_settings(min_name_length=11)
        self.assertEqual(self.of_kind(self.related(), "mention"), [])

    def test_text_output(self):  # F10
        write(self.root, "src/x.py", "print('x2')\n")
        proc = run_script("find_related.py", "--root", str(self.root))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("src/README.md", proc.stdout)
        self.assertIn("src/x.py", proc.stdout)




class PracticesDocumentTests(unittest.TestCase):
    """references/practices.md: layers, placement, and proximity (slice S5, contract C4)."""

    LAYERS = ("Project entry", "How-to", "Reference", "Architecture", "Decision records", "Change history",
              "Feature specification", "Code comments", "Research provenance")
    NEW_KEYS = ("GoogleSWE2020", "PEP8", "LinuxKernelStyle", "Diataxis")
    HEADING = "## Layers, placement, and proximity"

    def setUp(self) -> None:
        self.text = (SKILL_ROOT / "references/practices.md").read_text(encoding="utf-8")
        self.bib = (SKILL_ROOT / "references/bibliography.bib").read_text(encoding="utf-8")

    def section(self) -> str:
        self.assertIn(self.HEADING, self.text)
        return self.text.split(self.HEADING, 1)[1].split("\n## ", 1)[0]

    def test_layer_table_has_every_layer_with_a_basis(self):  # P1
        import re
        rows = [[c.strip() for c in line.strip().strip("|").split("|")]
                for line in self.section().splitlines() if line.startswith("|") and not set(line) <= set("|- ")]
        header, *body = rows
        self.assertEqual(header[0], "Layer")
        self.assertEqual(len(header), 5)
        for layer in self.LAYERS:
            with self.subTest(layer=layer):
                matching = [r for r in body if r[0].startswith(layer)]
                self.assertEqual(len(matching), 1)
                row = matching[0]
                self.assertEqual(len(row), 5)
                self.assertTrue(all(row), row)
                self.assertTrue(re.match(r"(Sourced|Design decision)", row[4]), row[4])

    def test_cited_bibliography_keys_exist(self):  # P2
        import re
        defined = set(re.findall(r"^@\w+\{([^,\s]+),", self.bib, re.MULTILINE))
        cited = set()
        for group in re.findall(r"\[([^\[\]]+)\](?!\()", self.text):
            parts = [p.strip() for p in group.split(";")]
            if all(re.fullmatch(r"[A-Z][A-Za-z0-9_]+", p) for p in parts):
                cited.update(parts)
        self.assertFalse(cited - defined, f"cited but not in bibliography.bib: {sorted(cited - defined)}")
        self.assertFalse(set(self.NEW_KEYS) - cited, "new sources must be cited in practices.md")
        self.assertFalse(set(self.NEW_KEYS) - defined)

    def test_proximity_scale_is_labelled_as_a_design_decision(self):  # P3
        section = self.section()
        for level in ("P0", "P1", "P2", "P3", "P4"):
            self.assertIn(level, section)
        self.assertRegex(section, r"(?i)proximity.*design decision|design decision.*proximity")
        self.assertRegex(section, r"(?i)per-directory README.*design decision|design decision.*per-directory README")
        self.assertIn("No source reviewed presents a single hierarchy", section)


class StackConventionsTests(unittest.TestCase):
    STACKS = ("Python", "TypeScript", "Terraform", "Bicep", "GitHub Actions")
    KEYS = ("PEP257", "TSDoc", "TFModuleStructure", "BicepParameters", "BicepLintDescription", "GHActionMetadata")
    HEADING = "## Stack conventions"

    def setUp(self) -> None:
        self.text = (SKILL_ROOT / "references/practices.md").read_text(encoding="utf-8")
        self.bib = (SKILL_ROOT / "references/bibliography.bib").read_text(encoding="utf-8")

    def section(self) -> str:
        self.assertIn(self.HEADING, self.text)
        return self.text.split(self.HEADING, 1)[1].split("\n## ", 1)[0]

    def test_every_stack_has_one_row_with_a_basis(self):
        import re
        rows = [[c.strip() for c in line.strip().strip("|").split("|")]
                for line in self.section().splitlines() if line.startswith("|") and not set(line) <= set("|- ")]
        header, *body = rows
        self.assertEqual(header[0], "Stack")
        for stack in self.STACKS:
            with self.subTest(stack=stack):
                matching = [r for r in body if r[0] == stack]
                self.assertEqual(len(matching), 1)
                self.assertEqual(len(matching[0]), len(header))
                self.assertTrue(re.match(r"(Sourced|Design decision)", matching[0][-1]), matching[0][-1])

    def test_stack_sources_are_cited_and_defined(self):
        import re
        defined = set(re.findall(r"^@\w+\{([^,\s]+),", self.bib, re.MULTILINE))
        cited = {part.strip() for group in re.findall(r"\[([^\[\]]+)\](?!\()", self.section())
                 for part in group.split(";")}
        for key in self.KEYS:
            with self.subTest(key=key):
                self.assertIn(key, cited)
                self.assertIn(key, defined)

    def test_skill_points_to_the_stack_conventions(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        step = skill.split("4. **Update together.**", 1)[1].split("5. **Check.**", 1)[0]
        self.assertIn("references/practices.md#stack-conventions", step)








# ---------------------------------------------------------------------------
# SKILL.md structure
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
