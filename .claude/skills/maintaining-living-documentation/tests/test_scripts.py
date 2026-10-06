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

@unittest.skipUnless(HAS_GIT, "git not installed")
class StopGateTests(TempDirTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.state_dir = self.root / "tmp"
        self.state_dir.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        init_repo(self.repo)
        write(self.repo, "app.py", "print('v1')\n")
        write(self.repo, "docs/guide.md", "# Guide\n")
        commit_all(self.repo, "initial")
        self.calls = 0

    def hook(self, payload: dict, *args: str, **env: str) -> dict | None:
        self.calls += 1
        full_env = dict(os.environ, TMPDIR=str(self.state_dir), CLAUDE_PROJECT_DIR=str(self.repo),
                        HOME=str(self.home), **env)
        if "LIVING_DOCS_GATE" not in env:
            full_env.pop("LIVING_DOCS_GATE", None)
        event = ("SessionStart" if "--session-start" in args
                 else "UserPromptSubmit" if "--turn-start" in args else "Stop")
        # turn_number makes otherwise identical calls distinct, as real consecutive events are.
        payload = {"session_id": "s1", "cwd": str(self.repo), "hook_event_name": event,
                   "stop_reason": "end_turn", "turn_number": self.calls, **payload}
        proc = subprocess.run([sys.executable, str(SCRIPTS / "stop_gate.py"), *args],
                              input=json.dumps(payload),
                              env=full_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout) if proc.stdout.strip() else None

    def test_session_start_injects_rule(self):
        out = self.hook({}, "--session-start")
        context = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("maintaining-living-documentation", context)
        self.assertIn("Documentation impact", context)
        self.assertIn(str(SCRIPTS), context)  # tells Claude where the scripts are

    def test_no_injection_when_rule_file_installed(self):
        write(self.repo, ".claude/rules/living-documentation.md", "# Living documentation (mandatory)\n")
        self.assertIsNone(self.hook({}, "--session-start"))

    def test_no_injection_outside_git(self):
        plain = self.root / "plain"
        plain.mkdir()
        env = dict(os.environ, TMPDIR=str(self.state_dir), CLAUDE_PROJECT_DIR=str(plain), HOME=str(self.home))
        proc = subprocess.run([sys.executable, str(SCRIPTS / "stop_gate.py"), "--session-start"],
                              input=json.dumps({"session_id": "s", "cwd": str(plain)}),
                              env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))

    def test_preexisting_changes_do_not_trigger(self):
        write(self.repo, "app.py", "print('dirty before session')\n")
        self.hook({}, "--session-start")
        self.assertIsNone(self.hook({"last_assistant_message": "Done."}))

    def test_changes_made_between_turns_do_not_trigger(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('edited by the user between turns')\n")
        self.assertIsNone(self.hook({}, "--turn-start"))
        self.assertIsNone(self.hook({"last_assistant_message": "Answered a question."}))

    def test_change_during_turn_is_still_blocked_after_turn_start(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('between turns')\n")
        self.hook({}, "--turn-start")
        write(self.repo, "app.py", "print('edited this turn')\n")
        out = self.hook({"last_assistant_message": "Implemented the feature."})
        self.assertEqual(out["decision"], "block")

    def test_code_change_without_report_is_blocked_once_per_turn_then_released(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('v2')\n")
        msg = {"last_assistant_message": "Implemented the feature."}
        out = self.hook(msg)
        self.assertEqual(out["decision"], "block")
        self.assertIn("Documentation impact", out["reason"])
        # The correction must not make Claude restate the answer it already gave.
        self.assertIn("do not repeat", out["reason"].lower())
        # Re-entry after our own block (stop_hook_active) never blocks again: warn instead of looping.
        out = self.hook({**msg, "stop_hook_active": True})
        self.assertNotIn("decision", out)
        self.assertIn("not blocking", out["systemMessage"])
        self.assertIsNone(self.hook(msg))  # same state is not reported again

    def test_block_budget_limits_blocks_across_turns(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('v2')\n")
        msg = {"last_assistant_message": "Implemented the feature."}
        self.assertEqual(self.hook(msg, LIVING_DOCS_GATE_MAX_BLOCKS="1")["decision"], "block")
        out = self.hook(msg, LIVING_DOCS_GATE_MAX_BLOCKS="1")
        self.assertNotIn("decision", out)
        self.assertIn("not blocking", out["systemMessage"])

    def test_report_satisfies_the_gate(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('v2')\n")
        out = self.hook({"last_assistant_message": "Done.\n\nDocumentation impact: none — internal refactor."})
        self.assertIsNone(out)

    def test_broken_link_in_changed_docs_is_blocked_even_with_report(self):
        self.hook({}, "--session-start")
        write(self.repo, "docs/guide.md", "# Guide\n\n[x](missing.md)\n")
        out = self.hook({"last_assistant_message": "Documentation impact\n- Updated: docs/guide.md"})
        self.assertEqual(out["decision"], "block")
        self.assertIn("missing.md", out["reason"])

    def test_docs_only_change_needs_no_report(self):
        self.hook({}, "--session-start")
        write(self.repo, "docs/guide.md", "# Guide\n\nMore text.\n")
        self.assertIsNone(self.hook({"last_assistant_message": "Edited the guide."}))

    def test_env_modes(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('v2')\n")
        out = self.hook({"last_assistant_message": "x"}, LIVING_DOCS_GATE="warn")
        self.assertIn("systemMessage", out)
        write(self.repo, "app.py", "print('v3')\n")
        self.assertIsNone(self.hook({"last_assistant_message": "x"}, LIVING_DOCS_GATE="off"))

    def test_project_config_modes(self):
        write(self.repo, ".living-documentation.json", json.dumps({"enforcement": "off"}))
        commit_all(self.repo)
        self.assertIsNone(self.hook({}, "--session-start"))  # no rule injection either
        write(self.repo, "app.py", "print('v2')\n")
        self.assertIsNone(self.hook({"last_assistant_message": "x"}))
        write(self.repo, ".living-documentation.json", json.dumps({"enforcement": "warn"}))
        self.assertIn("systemMessage", self.hook({"last_assistant_message": "x"}))
        # The environment variable overrides the project setting.
        write(self.repo, "app.py", "print('v3')\n")
        self.assertEqual(self.hook({"last_assistant_message": "x"}, LIVING_DOCS_GATE="block")["decision"], "block")

    def test_non_end_turn_stops_are_ignored(self):
        self.hook({}, "--session-start")
        write(self.repo, "app.py", "print('v2')\n")
        self.assertIsNone(self.hook({"stop_reason": "max_tokens", "last_assistant_message": "x"}))

    def test_outside_git_is_silent(self):
        plain = self.root / "plain"
        plain.mkdir()
        write(plain, "app.py", "x = 1\n")
        env = dict(os.environ, TMPDIR=str(self.state_dir), CLAUDE_PROJECT_DIR=str(plain))
        proc = subprocess.run([sys.executable, str(SCRIPTS / "stop_gate.py")],
                              input=json.dumps({"session_id": "s", "cwd": str(plain)}),
                              env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))


# ---------------------------------------------------------------------------
# Plugin packaging
# ---------------------------------------------------------------------------

class PluginPackagingTests(unittest.TestCase):
    def test_manifest(self):
        manifest = json.loads((SKILL_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], SKILL_ROOT.name)
        self.assertTrue(manifest["description"])

    def test_hook_scripts_exist(self):
        plugin = json.loads((SKILL_ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        for groups in plugin.values():
            for group in groups:
                for hook in group["hooks"]:
                    script = hook["args"][0].replace("${CLAUDE_PLUGIN_ROOT}", str(SKILL_ROOT))
                    self.assertTrue(Path(script).is_file(), script)

    @unittest.skipUnless(shutil.which("claude"), "Claude Code CLI not installed")
    def test_claude_plugin_validate(self):
        with tempfile.TemporaryDirectory() as td:
            # Validate the manifest, then the SKILL.md frontmatter as a skills directory.
            proc = subprocess.run(["claude", "plugin", "validate", "--strict", str(SKILL_ROOT)],
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            skills = Path(td) / "skills"
            shutil.copytree(SKILL_ROOT, skills / SKILL_ROOT.name,
                            ignore=shutil.ignore_patterns("__pycache__", ".claude-plugin"))
            proc = subprocess.run(["claude", "plugin", "validate", "--strict", "--json", str(skills)],
                                  text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertTrue(json.loads(proc.stdout)["success"])


# ---------------------------------------------------------------------------
# SKILL.md structure
# ---------------------------------------------------------------------------

class SkillDefinitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.frontmatter = self.text.split("---")[1]

    def field(self, name: str) -> str:
        import re
        return re.search(rf"^{name}: (.*)$", self.frontmatter, re.MULTILINE).group(1)

    def test_frontmatter_limits(self):
        import re
        name = self.field("name")
        self.assertRegex(name, r"^[a-z0-9-]{1,64}$")
        self.assertEqual(name, SKILL_ROOT.name)
        self.assertLessEqual(len(self.field("description")), 1024)
        self.assertLessEqual(len(self.field("compatibility")), 500)
        allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
        keys = set(re.findall(r"^([a-z-]+):", self.frontmatter, re.MULTILINE))
        self.assertLessEqual(keys, allowed)  # Agent Skills spec fields only, for portability

    def test_no_allowed_tools(self):
        # Declaring allowed-tools makes invoking the skill itself need approval (observed on
        # Claude Code 2.1.289): non-interactive runs then fail to load the skill at all.
        self.assertNotIn("allowed-tools:", self.frontmatter)

    def test_decision_record_rules(self):
        normative = self.text.split("## Normative basis", 1)[1].split("## For every change", 1)[0]
        self.assertIn("MUST NOT create or supersede a decision record unless the user explicitly asks", normative)
        self.assertIn("Proposed decision record:", self.text)
        rule = (SKILL_ROOT / "hooks/rule.md").read_text(encoding="utf-8")
        self.assertIn("only when the user explicitly asks", rule)

    def test_adr_template_follows_madr4(self):
        template = (SKILL_ROOT / "templates/adr.md").read_text(encoding="utf-8")
        self.assertIn("decision-makers:", template)
        self.assertNotIn("deciders:", template)
        self.assertEqual(common.record_status(template), "proposed")
        for heading in ("## Context and Problem Statement", "## Considered Options", "## Decision Outcome",
                        "### Consequences", "### Confirmation"):
            self.assertIn(heading, template)

    def test_body_is_concise(self):
        self.assertLess(self.text.count("\n"), 500)

    def test_rule_and_gate_agree_with_skill(self):
        rule = (SKILL_ROOT / "hooks/rule.md").read_text(encoding="utf-8")
        self.assertIn(self.field("name"), rule)
        self.assertIn("Documentation impact", rule)
        self.assertIn("Documentation impact", self.text)

    def test_normative_basis_names_each_standard(self):
        for ref in ("12207", "15289", "42010", "26514", "Docs-as-Code", "arc42", "C4", "ADR", "FAIR", "PROV", "RO-Crate"):
            with self.subTest(ref=ref):
                self.assertIn(ref, self.text.split("## Normative basis", 1)[1].split("## For every change", 1)[0])

if __name__ == "__main__":
    unittest.main()
