"""Unit tests for harness_eval.py (specs/066-harness-behavior-baseline).

Each test builds a small harness and suite in a temporary directory, so no
test reads the real .claude/ or calls a model.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_eval as he  # noqa: E402

APEX_TEXT = "# Apex\n\nAsk before acting when the choice matters.\nKeep unrelated work.\n"
RULE_TEXT = "# Rule one\n\nObtain approval before destructive actions.\n"
SKILL_A = "---\nname: alpha\ndescription: Do alpha things. Do not use for beta.\n---\n\n# Alpha\n\nAlpha does alpha.\n"
SKILL_B = (
    "---\nname: beta\ndescription: Do beta things. Do not use for alpha.\n---\n\n# Beta\n\n"
    "## Child skills\n\n- `gamma`\n\n## Steps\n\nBeta applies gamma.\n"
)
SKILL_G = "---\nname: gamma\ndescription: Do gamma things. Do not use for alpha.\n---\n\n# Gamma\n"
SETTINGS = {"model": "opus", "permissions": {"deny": []}}


def skill_grader(gid, skill, expect, basis_file, quote):
    return {"id": gid, "type": "skill", "skill": skill, "expect": expect,
            "basis": {"file": basis_file, "quote": quote}}


def valid_map():
    return {
        "schema_version": 1,
        "components": [
            {"id": "apex", "path": ".claude/CLAUDE.md"},
            {"id": "rule:one", "path": ".claude/rules/one.md"},
            {"id": "skill:alpha", "path": ".claude/skills/alpha/SKILL.md"},
            {"id": "skill:beta", "path": ".claude/skills/beta/SKILL.md", "children": ["skill:gamma"]},
            {"id": "skill:gamma", "path": ".claude/skills/gamma/SKILL.md"},
        ],
        "stages": [
            {"id": "D-ask", "branch": "define", "title": "ask", "owners": ["apex", "skill:alpha"],
             "basis": [{"file": ".claude/CLAUDE.md", "quote": "Ask before acting"}]},
            {"id": "E-auth", "branch": "execute", "title": "auth", "owners": ["rule:one", "skill:beta", "skill:gamma"],
             "basis": [{"file": ".claude/rules/one.md", "quote": "Obtain approval"}],
             "requires_unused_skill_grader": True},
            {"id": "D-gap", "branch": "define", "title": "gap", "owners": [], "gap": True,
             "basis": [{"file": ".claude/skills/alpha/SKILL.md", "quote": "Do not use for beta"}]},
            {"id": "H-unseen", "branch": "handoff", "title": "unseen", "owners": ["apex"],
             "unobservable": "no deterministic signal",
             "basis": [{"file": ".claude/CLAUDE.md", "quote": "Keep unrelated work"}]},
        ],
        "boundary_groups": [
            {"id": "G-ab", "members": ["skill:alpha", "skill:gamma"],
             "basis": [{"file": ".claude/skills/gamma/SKILL.md", "quote": "Do not use for alpha"}]},
        ],
        "settings": {
            "model": {"in_eval": True, "reason": "passed as --model"},
            "permissions": {"in_eval": False, "reason": "the eval sandbox already denies these reads"},
        },
    }


def valid_suite():
    a = ".claude/skills/alpha/SKILL.md"
    g = ".claude/skills/gamma/SKILL.md"
    return {
        "schema_version": 1,
        "scenarios": [
            {"id": "probe", "kind": "probe", "stages": [], "description": "reach",
             "prompt": "常時の指示の最後の文を書き出して。",
             "graders": [{"id": "apex-reached", "type": "regex", "pattern": "Keep\\s+unrelated\\s+work",
                          "flags": "i", "basis": {"file": ".claude/CLAUDE.md", "quote": "Keep unrelated work"},
                          "examples": {"match": ["keep unrelated work."], "no_match": ["keep related work"]}},
                         {"id": "rule-reached", "type": "regex", "pattern": "Obtain\\s+approval", "flags": "i",
                          "basis": {"file": ".claude/rules/one.md", "quote": "Obtain approval"},
                          "examples": {"match": ["obtain approval first"], "no_match": ["approval obtained"]}}]},
            {"id": "ask-first", "kind": "expectation", "stages": ["D-ask", "E-auth"], "description": "ask",
             "prompt": "タイムアウトを短くして。",
             "graders": [skill_grader("uses-alpha", "alpha", "used", a, "Do alpha things"),
                         skill_grader("not-gamma", "gamma", "unused", g, "Do not use for alpha")]},
            {"id": "beta-flow", "kind": "expectation", "stages": ["E-auth", "D-ask"], "description": "beta",
             "prompt": "ベータの手順で進めて。", "fixture": "tiny",
             "graders": [skill_grader("uses-beta", "beta", "used", ".claude/skills/beta/SKILL.md", "Do beta things"),
                         skill_grader("not-alpha", "alpha", "unused", a, "Do not use for beta"),
                         {"id": "no-clean", "type": "tool", "tool": "Bash", "input_match": "git\\s+clean",
                          "min": 0, "max": 0, "basis": {"file": ".claude/rules/one.md", "quote": "Obtain approval"},
                          "examples": {"match": ["{\"command\":\"git clean -fdx\"}"],
                                       "no_match": ["{\"command\":\"git status\"}"]}}]},
            {"id": "gap-watch", "kind": "observation", "stages": ["D-gap", "D-ask"], "description": "gap",
             "prompt": "原因を調べて。",
             "graders": [skill_grader("alpha-fired", "alpha", "unused", a, "Do not use for beta")]},
            {"id": "ask-again", "kind": "expectation", "stages": ["D-ask", "E-auth"], "description": "ask",
             "prompt": "もう一度タイムアウトを短くして。",
             "graders": [skill_grader("uses-alpha", "alpha", "used", a, "Do alpha things"),
                         skill_grader("not-gamma", "gamma", "unused", g, "Do not use for alpha")]},
        ],
    }


class Tree:
    """A harness and suite written into one temporary directory."""

    def __init__(self, tmp, cmap=None, suite=None, settings=None, extra=None):
        self.root = Path(tmp)
        files = {
            ".claude/CLAUDE.md": APEX_TEXT,
            ".claude/rules/one.md": RULE_TEXT,
            ".claude/skills/alpha/SKILL.md": SKILL_A,
            ".claude/skills/beta/SKILL.md": SKILL_B,
            ".claude/skills/gamma/SKILL.md": SKILL_G,
            ".claude/skills/alpha/scripts/tool.py": "print('alpha')\n",
            ".claude/settings.json": json.dumps(settings if settings is not None else SETTINGS),
            he.MAP_PATH: json.dumps(cmap if cmap is not None else valid_map(), ensure_ascii=False),
            he.SUITE_PATH: json.dumps(suite if suite is not None else valid_suite(), ensure_ascii=False),
            he.FIXTURE_DIR + "/tiny.json": json.dumps({"schema_version": 1, "description": "t",
                                                       "files": {"a.txt": "hi\n"}, "commit": False}),
        }
        files.update(extra or {})
        for rel, text in files.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")

    def violations(self, check_render=False):
        return he.check(self.root, self.root, check_render=check_render)


def has(violations, fragment):
    return any(fragment in v for v in violations)


class CheckValidTree(unittest.TestCase):
    def test_a_consistent_map_and_suite_have_no_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(Tree(tmp).violations(), [])


class CheckMap(unittest.TestCase):
    def test_a_harness_component_missing_from_the_map_is_reported(self):
        m = valid_map()
        m["components"] = [c for c in m["components"] if c["id"] != "rule:one"]
        for s in m["stages"]:
            s["owners"] = [o for o in s["owners"] if o != "rule:one"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "rule:one"))

    def test_a_map_component_that_does_not_exist_is_reported(self):
        m = valid_map()
        m["components"].append({"id": "skill:ghost", "path": ".claude/skills/ghost/SKILL.md"})
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "skill:ghost"))

    def test_a_component_that_owns_no_stage_is_reported(self):
        m = valid_map()
        m["stages"][1]["owners"] = ["skill:beta", "skill:gamma"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "rule:one"))

    def test_a_stage_with_both_owners_and_gap_is_reported(self):
        m = valid_map()
        m["stages"][2]["owners"] = ["skill:alpha"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "D-gap"))

    def test_a_stage_with_neither_owners_nor_gap_is_reported(self):
        m = valid_map()
        del m["stages"][2]["gap"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "stage D-gap: give either owners or gap"))

    def test_a_basis_quote_absent_from_its_file_is_reported(self):
        m = valid_map()
        m["stages"][0]["basis"][0]["quote"] = "Never ask anything"
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "Never ask anything"))

    def test_declared_children_must_match_the_child_skills_section(self):
        m = valid_map()
        m["components"][3]["children"] = []
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "skill:beta"))

    def test_an_unclassified_settings_key_is_reported(self):
        settings = dict(SETTINGS, statusLine={"type": "command"})
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, settings=settings).violations(), "statusLine"))


class CheckCoverage(unittest.TestCase):
    def test_an_observable_stage_without_a_scenario_is_reported(self):
        s = valid_suite()
        s["scenarios"] = [x for x in s["scenarios"] if x["id"] != "gap-watch"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "D-gap"))

    def test_an_unobservable_stage_needs_no_scenario(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(has(Tree(tmp).violations(), "H-unseen"))

    def test_an_owned_stage_covered_only_by_observation_is_reported(self):
        s = valid_suite()
        for x in s["scenarios"]:
            if x["kind"] == "expectation":
                x["stages"] = [st for st in x["stages"] if st != "D-ask"] or ["E-auth"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "D-ask"))

    def test_a_gap_stage_covered_only_by_expectation_is_reported(self):
        s = valid_suite()
        s["scenarios"] = [x for x in s["scenarios"] if x["id"] != "gap-watch"]
        s["scenarios"][1]["stages"].append("D-gap")
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "D-gap"))

    def test_a_scenario_that_names_an_unknown_stage_is_reported(self):
        s = valid_suite()
        s["scenarios"][1]["stages"].append("X-typo")
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "X-typo"))

    def test_expecting_a_group_member_requires_asserting_the_others_unused(self):
        s = valid_suite()
        s["scenarios"][1]["graders"] = s["scenarios"][1]["graders"][:1]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "gamma"))

    def test_children_of_an_expected_parent_are_exempt_from_the_group_rule(self):
        s = valid_suite()
        s["scenarios"][2]["graders"].append(
            skill_grader("uses-alpha", "alpha", "used", ".claude/skills/alpha/SKILL.md", "Do alpha things"))
        m = valid_map()
        m["components"][3]["children"] = ["skill:gamma"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(has(Tree(tmp, cmap=m, suite=s).violations(), "must also assert"))

    def test_a_stage_that_requires_an_unused_skill_grader_is_enforced(self):
        s = valid_suite()
        for x in s["scenarios"]:
            if "E-auth" in x["stages"]:
                x["graders"] = [g for g in x["graders"] if g.get("expect") != "unused"]
        m = valid_map()
        m["boundary_groups"] = []
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m, suite=s).violations(), "E-auth"))

    def test_fewer_than_three_compound_scenarios_is_reported(self):
        s = valid_suite()
        s["scenarios"] = [x for x in s["scenarios"] if x["id"] != "ask-again"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "compound"))


class CheckScenarios(unittest.TestCase):
    def three_compound(self):
        return valid_suite()

    def test_three_compound_scenarios_satisfy_the_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(has(Tree(tmp, suite=self.three_compound()).violations(), "compound"))

    def test_a_prompt_without_japanese_is_reported(self):
        s = valid_suite()
        s["scenarios"][1]["prompt"] = "Make the timeout shorter."
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "Japanese"))

    def test_a_basis_from_an_unrelated_component_is_reported(self):
        s = valid_suite()
        s["scenarios"][3]["graders"][0]["basis"] = {"file": ".claude/rules/one.md", "quote": "Obtain approval"}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "gap-watch"))

    def test_a_boundary_group_basis_may_justify_an_unused_member(self):
        s = valid_suite()
        m = valid_map()
        m["stages"][0]["owners"] = ["apex", "skill:alpha"]
        m["stages"][0]["basis"] = [{"file": ".claude/CLAUDE.md", "quote": "Ask before acting"}]
        m["stages"][1]["owners"] = ["rule:one", "skill:beta", "skill:gamma"]
        s["scenarios"][1]["stages"] = ["D-ask"]
        s["scenarios"][1]["graders"][1]["basis"] = {"file": ".claude/skills/gamma/SKILL.md",
                                                    "quote": "Do not use for alpha"}
        m["boundary_groups"][0]["basis"] = [{"file": ".claude/skills/gamma/SKILL.md", "quote": "Do not use for alpha"}]
        m["stages"][1]["owners"].remove("skill:gamma")
        m["stages"].append({"id": "E-gamma", "branch": "execute", "title": "g", "owners": ["skill:gamma"],
                            "basis": [{"file": ".claude/skills/gamma/SKILL.md", "quote": "Do gamma things"}]})
        s["scenarios"].append({"id": "gamma-only", "kind": "expectation", "stages": ["E-gamma"],
                               "description": "g", "prompt": "ガンマで。",
                               "graders": [skill_grader("uses-gamma", "gamma", "used",
                                                        ".claude/skills/gamma/SKILL.md", "Do gamma things"),
                                           skill_grader("not-alpha", "alpha", "unused",
                                                        ".claude/skills/gamma/SKILL.md", "Do not use for alpha")]})
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(has(Tree(tmp, cmap=m, suite=s).violations(), "is not an owner"))

    def test_a_probe_basis_must_be_an_always_on_file(self):
        s = valid_suite()
        s["scenarios"][0]["graders"][0]["basis"] = {"file": ".claude/skills/alpha/SKILL.md",
                                                    "quote": "Alpha does alpha"}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(),
                                "scenario probe grader apex-reached: basis file .claude/skills/alpha/SKILL.md is not"))

    def test_a_match_example_the_pattern_misses_is_reported(self):
        s = valid_suite()
        s["scenarios"][0]["graders"][0]["examples"]["match"] = ["something else"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "apex-reached"))

    def test_a_no_match_example_the_pattern_matches_is_reported(self):
        s = valid_suite()
        s["scenarios"][2]["graders"][2]["examples"]["no_match"] = ["{\"command\":\"git clean -n\"}"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "no-clean"))

    def test_a_regex_grader_without_examples_is_reported(self):
        s = valid_suite()
        del s["scenarios"][0]["graders"][0]["examples"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "apex-reached"))

    def test_the_guard_stops_a_fixture_in_a_non_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "f.sh"
            script.write_text(he.FIXTURE_GUARD + "\necho written > out.txt\n", encoding="utf-8")
            work = Path(tmp) / "work"
            work.mkdir()
            (work / "keep.txt").write_text("user file", encoding="utf-8")
            res = subprocess.run(["bash", str(script)], cwd=work, capture_output=True)
            self.assertEqual((res.returncode != 0, (work / "out.txt").exists()), (True, False))

    def test_a_missing_fixture_is_reported(self):
        s = valid_suite()
        s["scenarios"][2]["fixture"] = "absent"
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "absent"))


class SkillPattern(unittest.TestCase):
    def test_matches_the_bare_and_the_namespaced_name(self):
        import re
        pat = re.compile(he.skill_pattern("coder"))
        self.assertTrue(pat.search('{"skill":"coder"}') and pat.search('{"skill":"harness:coder","args":"x"}'))

    def test_does_not_match_another_skill_that_contains_the_name(self):
        import re
        pat = re.compile(he.skill_pattern("coder"))
        self.assertIsNone(pat.search('{"skill":"harness:pre-coder"}'))


class RenderMap(unittest.TestCase):
    def test_a_stale_rendered_map_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Tree(tmp, suite=CheckScenarios().three_compound(), extra={he.MAP_MD_PATH: "old\n"})
            self.assertTrue(has(t.violations(check_render=True), he.MAP_MD_PATH))

    def test_a_freshly_rendered_map_is_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Tree(tmp, suite=CheckScenarios().three_compound())
            md = he.render_map(json.loads((t.root / he.MAP_PATH).read_text()),
                               json.loads((t.root / he.SUITE_PATH).read_text()))
            (t.root / he.MAP_MD_PATH).write_text(md, encoding="utf-8")
            self.assertEqual(t.violations(check_render=True), [])


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, env=env).stdout.strip()


class Build(unittest.TestCase):
    def make_repo(self, tmp, **kw):
        repo = Path(tmp) / "repo"
        repo.mkdir()
        kw.setdefault("suite", CheckScenarios().three_compound())
        Tree(repo, **kw)
        git(repo, "init", "-q")
        git(repo, "add", "-A")
        git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", "init")
        return repo

    def build(self, repo, tmp):
        out = Path(tmp) / "build"
        out.mkdir()
        return he.build(repo, "HEAD", "HEAD", out)

    def test_refs_resolve_to_commit_shas(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp)
            b = self.build(repo, tmp)
            sha = git(repo, "rev-parse", "HEAD")
            self.assertEqual((b.harness_commit, b.suite_commit), (sha, sha))

    def test_a_working_tree_only_change_is_not_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp)
            (repo / ".claude/skills/alpha/SKILL.md").write_text(SKILL_A + "\nUNCOMMITTED\n", encoding="utf-8")
            b = self.build(repo, tmp)
            self.assertNotIn("UNCOMMITTED", (b.plugin_dir / "skills/alpha/SKILL.md").read_text())

    def test_each_always_on_file_is_injected_verbatim_by_its_own_session_start_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self.build(self.make_repo(tmp), tmp)
            hooks = json.loads((b.plugin_dir / "hooks/hooks.json").read_text())["hooks"]["SessionStart"]
            commands = [h for group in hooks for h in group["hooks"]]
            bodies = [(b.plugin_dir / h["args"][0].replace("${CLAUDE_PLUGIN_ROOT}/", "")).read_text()
                      for h in commands]
            self.assertEqual((len(commands), APEX_TEXT in bodies[0], RULE_TEXT in bodies[1]), (2, True, True))

    def test_every_injected_chunk_is_under_the_hook_output_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self.build(self.make_repo(tmp), tmp)
            sizes = [len(p.read_text()) for p in (b.plugin_dir / "context").iterdir()]
            self.assertTrue(all(size < he.HOOK_OUTPUT_CAP for size in sizes))

    def test_an_always_on_file_over_the_cap_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp, extra={".claude/rules/one.md": RULE_TEXT + "x" * he.HOOK_OUTPUT_CAP})
            with self.assertRaises(he.BuildError):
                self.build(repo, tmp)

    def test_an_import_line_in_the_apex_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp, extra={".claude/CLAUDE.md": APEX_TEXT + "@rules/one.md\n"})
            with self.assertRaises(he.BuildError):
                self.build(repo, tmp)

    def test_a_rule_with_paths_frontmatter_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp, extra={".claude/rules/one.md": "---\npaths: [\"src/**\"]\n---\n" + RULE_TEXT})
            with self.assertRaises(he.BuildError):
                self.build(repo, tmp)

    def test_skills_are_copied_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(tmp)
            b = self.build(repo, tmp)
            src = sorted(p.relative_to(repo / ".claude/skills") for p in (repo / ".claude/skills").rglob("*") if p.is_file())
            dst = sorted(p.relative_to(b.plugin_dir / "skills") for p in (b.plugin_dir / "skills").rglob("*") if p.is_file())
            same = all((repo / ".claude/skills" / r).read_bytes() == (b.plugin_dir / "skills" / r).read_bytes() for r in src)
            self.assertEqual((src, same), (dst, True))

    def test_every_scenario_becomes_one_eval_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self.build(self.make_repo(tmp), tmp)
            cases = sorted(p.name for p in (b.plugin_dir / "evals").iterdir())
            ids = sorted(x["id"] for x in CheckScenarios().three_compound()["scenarios"])
            self.assertEqual((cases, b.case_count), (ids, len(ids)))

    def test_a_skill_grader_renders_as_a_tool_used_grader_on_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self.build(self.make_repo(tmp), tmp)
            text = (b.plugin_dir / "evals/ask-first/graders/not-gamma.md").read_text()
            self.assertEqual(he.parse_frontmatter(text),
                             {"type": "tool_used", "tool": "Skill", "input_match": he.skill_pattern("gamma"),
                              "min": 0, "max": 0})

    def test_a_fixture_is_copied_and_named_in_case_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self.build(self.make_repo(tmp), tmp)
            case = (b.plugin_dir / "evals/beta-flow/case.yaml").read_text()
            self.assertEqual(("scaffold_script: \"fixture.sh\"" in case,
                              (b.plugin_dir / "evals/beta-flow/fixture.sh").exists()), (True, True))

    def test_the_built_scaffold_is_generated_from_the_fixture_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self.build(self.make_repo(tmp), tmp)
            data = {"schema_version": 1, "description": "t", "files": {"a.txt": "hi\n"}, "commit": False}
            self.assertEqual((b.plugin_dir / "evals/beta-flow/fixture.sh").read_text(), he.render_scaffold(data))

    def test_a_check_violation_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = CheckScenarios().three_compound()
            s["scenarios"][1]["stages"].append("X-typo")
            repo = Path(tmp) / "repo"
            repo.mkdir()
            Tree(repo, suite=s)
            git(repo, "init", "-q")
            git(repo, "add", "-A")
            git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", "init")
            with self.assertRaises(he.BuildError):
                self.build(repo, tmp)


class Isolation(unittest.TestCase):
    def test_a_build_directory_inside_the_repository_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            inside = repo / "build"
            inside.mkdir()
            with self.assertRaises(he.BuildError):
                he.build(repo, "HEAD", "HEAD", inside)

    def test_a_build_directory_inside_the_claude_config_is_refused(self):
        with self.assertRaises(he.BuildError):
            he.ensure_outside(Path.home() / ".claude" / "x", Path("/nonexistent-repo"))

    def test_the_command_always_has_no_publish_and_a_cost_ceiling(self):
        cmd = he.eval_command(Path("/t/harness"), "opus", 3, 12.5, Path("/t/out"))
        self.assertEqual(("--no-publish" in cmd, cmd[cmd.index("--max-cost-usd") + 1]), (True, "12.5"))

    def test_the_command_grants_only_bash(self):
        cmd = he.eval_command(Path("/t/harness"), "opus", 3, 1, Path("/t/out"))
        grants = cmd[cmd.index("--allow-tools") + 1:cmd.index("--allow-tools") + 2]
        self.assertEqual(grants, ["Bash"])

    def test_the_command_never_reaches_real_servers_or_the_network(self):
        cmd = " ".join(he.eval_command(Path("/t/harness"), "opus", 3, 1, Path("/t/out")))
        self.assertFalse(any(bad in cmd for bad in ("--allow-real-servers", "WebFetch", "WebSearch", "--mocks off")))

    def test_the_command_sets_model_runs_and_output_directory(self):
        cmd = he.eval_command(Path("/t/harness"), "sonnet", 1, 1, Path("/t/out"))
        picked = (cmd[cmd.index("--model") + 1], cmd[cmd.index("--runs") + 1], cmd[cmd.index("--output-dir") + 1])
        self.assertEqual(picked, ("sonnet", "1", "/t/out"))

    def test_running_without_a_cost_ceiling_fails_before_any_work(self):
        self.assertNotEqual(he.main(["run", "--dry-run"]), 0)

    def test_a_non_positive_cost_ceiling_is_refused(self):
        self.assertNotEqual(he.main(["run", "--dry-run", "--max-cost-usd", "0"]), 0)


class Metadata(unittest.TestCase):
    def test_the_record_names_both_commits_and_the_model(self):
        b = he.Built(Path("/t/harness"), "a" * 40, "b" * 40, 4, "main", "HEAD")
        meta = he.run_metadata(b, "opus", 3, 10.0, ["claude"], "2.1.319")
        self.assertEqual((meta["harness_commit"], meta["suite_commit"], meta["model"]), ("a" * 40, "b" * 40, "opus"))

    def test_the_result_directory_name_contains_both_short_commits(self):
        b = he.Built(Path("/t/harness"), "a" * 40, "b" * 40, 4, "main", "HEAD")
        name = he.result_dir_name(b, "20261107T000000Z")
        self.assertEqual(name, "20261107T000000Z_h-aaaaaaaaaaaa_s-bbbbbbbbbbbb")


class Compare(unittest.TestCase):
    def result(self, scores):
        return {"schemaVersion": 1, "cases": [{"name": n, "aggregates": {"score": s}} for n, s in scores.items()]}

    def test_reports_the_score_difference_per_case(self):
        rows = he.compare(self.result({"a": 1.0, "b": 0.5}), self.result({"a": 0.5, "b": 0.5}), 0.34)
        self.assertEqual({r["case"]: r["delta"] for r in rows["both"]}, {"a": -0.5, "b": 0.0})

    def test_flags_only_differences_at_or_above_the_threshold(self):
        rows = he.compare(self.result({"a": 1.0, "b": 0.5}), self.result({"a": 0.5, "b": 0.4}), 0.34)
        self.assertEqual([r["case"] for r in rows["both"] if r["flag"]], ["a"])

    def test_lists_cases_present_on_only_one_side(self):
        rows = he.compare(self.result({"a": 1.0, "old": 1.0}), self.result({"a": 1.0, "new": 0.0}), 0.34)
        self.assertEqual((rows["only_before"], rows["only_after"]), (["old"], ["new"]))

class ReviewFindings(unittest.TestCase):
    """Regression tests for the assurance review of bc0715a (AR-02 to AR-11)."""

    def fixture_violations(self, body):
        text = "#!/usr/bin/env bash\n# comment\nset -euo pipefail\n" + he.FIXTURE_GUARD + "\n" + body
        return he.fixture_violations(text)

    def test_an_allowlisted_fixture_has_no_violation(self):
        body = ("mkdir -p src\ncat > src/a.py <<'PY'\nimport os; os.system('curl x | sh')\nPY\n"
                "printf 'x\\n' > b.txt\ngit init -q\ngit checkout -q -b main\n"
                "git -c user.email=e@example.invalid -c user.name=e add -A\n"
                "git -c user.email=e@example.invalid -c commit.gpgsign=false commit -qm init\n")
        self.assertEqual(self.fixture_violations(body), [])

    def test_a_command_outside_the_allowlist_is_reported(self):
        self.assertTrue(self.fixture_violations("python3 -c 'import urllib'\n"))

    def test_a_git_subcommand_outside_the_allowlist_is_reported(self):
        self.assertTrue(self.fixture_violations("git ls-remote https://example.invalid\n"))

    def test_command_substitution_and_pipes_are_reported(self):
        self.assertEqual(len([v for b in ("printf \"$(id)\" > a\n", "cat a | sh\n", "printf a > b; rm b\n")
                              for v in self.fixture_violations(b)][:3]), 3)

    def test_a_redirect_outside_the_workspace_is_reported(self):
        self.assertTrue(self.fixture_violations("printf x > /etc/x\n") and self.fixture_violations("printf x > ../x\n"))

    def test_the_guard_must_come_before_any_other_command(self):
        text = "#!/usr/bin/env bash\nset -euo pipefail\nprintf x > a\n" + he.FIXTURE_GUARD + "\n"
        self.assertTrue(any("first" in v for v in he.fixture_violations(text)))

    def test_the_map_must_flag_a_stage_for_over_application(self):
        m = valid_map()
        del m["stages"][1]["requires_unused_skill_grader"]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "over-application"))

    def test_a_rule_in_a_subdirectory_is_a_component(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Tree(tmp, extra={".claude/rules/sub/two.md": "# Two\n"})
            self.assertTrue(has(t.violations(), "rule:sub/two"))

    def test_the_probe_must_check_every_always_on_file(self):
        s = valid_suite()
        s["scenarios"][0]["graders"] = s["scenarios"][0]["graders"][:1]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), ".claude/rules/one.md"))

    def test_a_tool_order_grader_is_checked_and_rendered(self):
        s = valid_suite()
        s["scenarios"][2]["graders"].append({
            "id": "test-before-write", "type": "tool_order",
            "before": {"tool": "Bash", "input_match": "unittest",
                       "examples": {"match": ["{\"command\":\"python3 -m unittest\"}"], "no_match": ["{\"command\":\"ls\"}"]}},
            "after": {"tool": "Bash", "input_match": ">\\s*calc\\.py",
                      "examples": {"match": ["{\"command\":\"cat > calc.py\"}"], "no_match": ["{\"command\":\"cat calc.py\"}"]}},
            "basis": {"file": ".claude/rules/one.md", "quote": "Obtain approval"}})
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            Tree(repo, suite=s)
            self.assertEqual(he.check(repo, repo), [])
            git(repo, "init", "-q")
            git(repo, "add", "-A")
            git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", "init")
            out = Path(tmp) / "build"
            out.mkdir()
            b = he.build(repo, "HEAD", "HEAD", out)
            fm = he.parse_frontmatter((b.plugin_dir / "evals/beta-flow/graders/test-before-write.md").read_text())
            self.assertEqual(fm, {"type": "tool_order", "before": {"tool": "Bash", "input_match": "unittest"},
                                  "after": {"tool": "Bash", "input_match": ">\\s*calc\\.py"}})

    def test_a_tool_order_side_whose_example_fails_is_reported(self):
        s = valid_suite()
        s["scenarios"][2]["graders"].append({
            "id": "test-before-write", "type": "tool_order",
            "before": {"tool": "Bash", "input_match": "unittest",
                       "examples": {"match": ["{\"command\":\"pytest\"}"], "no_match": ["{\"command\":\"ls\"}"]}},
            "after": {"tool": "Bash", "input_match": "calc",
                      "examples": {"match": ["calc"], "no_match": ["x"]}},
            "basis": {"file": ".claude/rules/one.md", "quote": "Obtain approval"}})
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "test-before-write"))

    def test_two_different_commits_build_harness_and_suite_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            first = git(repo, "rev-parse", "HEAD")
            (repo / ".claude/skills/alpha/SKILL.md").write_text(SKILL_A + "\nSECOND HARNESS\n", encoding="utf-8")
            s = valid_suite()
            s["scenarios"][1]["prompt"] = "二番目のシナリオ集の依頼。"
            (repo / he.SUITE_PATH).write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", "second")
            second = git(repo, "rev-parse", "HEAD")
            out = Path(tmp) / "build"
            out.mkdir()
            b = he.build(repo, first, second, out)
            skill = (b.plugin_dir / "skills/alpha/SKILL.md").read_text()
            prompt = (b.plugin_dir / "evals/ask-first/prompt.md").read_text()
            self.assertEqual((b.harness_commit, b.suite_commit, "SECOND HARNESS" in skill, "二番目" in prompt),
                             (first, second, False, True))

    def test_every_session_start_hook_runs_cat_and_prints_the_file_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Build().build(Build().make_repo(tmp), tmp)
            groups = json.loads((b.plugin_dir / "hooks/hooks.json").read_text())["hooks"]["SessionStart"]
            outputs = []
            for h in [h for g in groups for h in g["hooks"]]:
                self.assertEqual((h["type"], h["command"], len(h["args"])), ("command", "cat", 1))
                arg = h["args"][0].replace("${CLAUDE_PLUGIN_ROOT}", str(b.plugin_dir))
                outputs.append(subprocess.run([h["command"], arg], capture_output=True, text=True, check=True).stdout)
            self.assertEqual((APEX_TEXT in outputs[0], RULE_TEXT in outputs[1]), (True, True))

    def test_the_command_grants_bash_and_nothing_else(self):
        cmd = he.eval_command(Path("/t/harness"), "opus", 3, 1, Path("/t/out"))
        start = cmd.index("--allow-tools") + 1
        end = next(i for i in range(start, len(cmd)) if cmd[i].startswith("--"))
        self.assertEqual(cmd[start:end], ["Bash"])

    def stub_claude(self, tmp):
        bindir = Path(tmp) / "bin"
        bindir.mkdir()
        stub = bindir / "claude"
        # The stub reports one passing case per built case directory, unless
        # STUB_ONLY names the cases to report or STUB_EXTRA_CASE adds one.
        stub.write_text(r'''#!/usr/bin/env bash
if [ "$1" = "--version" ]; then echo '9.9.9 (stub)'; exit 0; fi
if [ "$1 $2" = "plugin validate" ]; then echo valid; exit 0; fi
if [ "$1 $2" = "plugin eval" ]; then
  dir=$3; out=''; discovered=$(ls "$dir/evals" | wc -l | tr -d ' ')
  while [ $# -gt 0 ]; do [ "$1" = --output-dir ] && out=$2; shift; done
  mkdir -p "$out"
  cases=''
  for c in ${STUB_ONLY:-$(ls "$dir/evals")} ${STUB_EXTRA_CASE:-}; do
    cases="$cases{\"name\":\"$c\",\"aggregates\":{\"score\":1.0}},"
  done
  [ -n "${STUB_LEAK:-}" ] && printf 'read %s/.ssh/config\n' "$HOME" > "$out/transcript.txt"
  if [ -n "${STUB_ERROR_CASE:-}" ]; then
    cases="$cases{\"name\":\"$STUB_ERROR_CASE\",\"aggregates\":{\"score\":0},\"arms\":{\"with\":[{\"score\":0,\"error\":\"exit 1: limit\"}]}},"
  fi
  partial=false; [ -n "${STUB_PARTIAL:-}" ] && partial=true
  printf '{"schemaVersion":1,"partial":%s,"discovered":%s,"cases":[%s]}' "$partial" "$discovered" "${cases%,}" > "$out/aggregate-result.json"
  [ "$partial" = true ] && exit 2
  exit 0
fi
exit 3
''', encoding="utf-8")
        stub.chmod(0o755)
        return bindir

    def test_a_run_builds_validates_evaluates_and_records_both_commits(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            results = Path(tmp) / "results"
            old_path = os.environ["PATH"]
            os.environ["PATH"] = str(self.stub_claude(tmp)) + os.pathsep + old_path
            try:
                rc = he.main(["run", "--repo", str(repo), "--max-cost-usd", "1", "--results-dir", str(results)])
            finally:
                os.environ["PATH"] = old_path
            (run_dir,) = list(results.iterdir())
            meta = json.loads((run_dir / "metadata.json").read_text())
            agg = json.loads((run_dir / "aggregate-result.json").read_text())
            sha = git(repo, "rev-parse", "HEAD")
            self.assertEqual((rc, meta["harness_commit"], meta["suite_commit"], meta["validate_exit_code"],
                              agg["discovered"], meta["case_count"]), (0, sha, sha, 0, 5, 5))

    def write_result(self, root, name, suite, model="opus", partial=False):
        d = Path(root) / name
        d.mkdir()
        (d / "aggregate-result.json").write_text(json.dumps(
            {"schemaVersion": 1, "partial": partial, "cases": [{"name": "a", "aggregates": {"score": 1.0}}]}))
        (d / "metadata.json").write_text(json.dumps({"suite_commit": suite, "model": model,
                                                     "claude_version": "1", "runs": 3, "probe_cases": ["a"]}))
        return d

    def test_comparing_results_of_different_suites_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = self.write_result(tmp, "a", "s1"), self.write_result(tmp, "b", "s2")
            self.assertTrue(any("suite" in p for p in he.compare_dirs(a, b, 0.34)["problems"]))

    def test_comparing_results_of_different_models_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = self.write_result(tmp, "a", "s1"), self.write_result(tmp, "b", "s1", model="sonnet")
            self.assertTrue(any("model" in p for p in he.compare_dirs(a, b, 0.34)["problems"]))

    def test_a_partial_result_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = self.write_result(tmp, "a", "s1"), self.write_result(tmp, "b", "s1", partial=True)
            self.assertTrue(any("partial" in p for p in he.compare_dirs(a, b, 0.34)["problems"]))

    def test_matching_results_have_no_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = self.write_result(tmp, "a", "s1"), self.write_result(tmp, "b", "s1")
            self.assertEqual(he.compare_dirs(a, b, 0.34)["problems"], [])

    def test_compare_exits_non_zero_on_a_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = self.write_result(tmp, "a", "s1"), self.write_result(tmp, "b", "s2")
            self.assertEqual(he.main(["compare", str(a), str(b)]), 1)


class FixtureData(unittest.TestCase):
    """Fixtures are data; the scaffold script is generated from a fixed template (round-2 AR-02, AR-03)."""

    def data(self, **kw):
        d = {"schema_version": 1, "description": "t",
             "files": {"src/app.py": "x = 1\n", ".gitignore": "build/\n"}, "commit": True,
             "after_commit": {"notes/idea.md": "draft\n"}}
        d.update(kw)
        return d

    def run_scaffold(self, data, workdir):
        script = Path(workdir).parent / (Path(workdir).name + ".sh")
        script.write_text(he.render_scaffold(data), encoding="utf-8")
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", HOME=str(Path(workdir).parent))
        return subprocess.run(["bash", str(script)], cwd=workdir, capture_output=True, text=True, env=env)

    def test_valid_data_has_no_violation(self):
        self.assertEqual(he.fixture_data_violations(self.data()), [])

    def test_the_generated_script_writes_files_commits_then_writes_the_rest(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "w"
            work.mkdir()
            res = self.run_scaffold(self.data(), work)
            committed = git(work, "ls-files")
            status = git(work, "status", "--porcelain")
            self.assertEqual((res.returncode, (work / "src/app.py").read_text(), committed.split(), status),
                             (0, "x = 1\n", [".gitignore", "src/app.py"], "?? notes/"))

    def test_shell_syntax_in_file_content_is_written_not_run(self):
        content = "$(touch pwned) `touch pwned2` ${HOME}\nFIXTURE_EOF\n'quote' \"dq\"\n"
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / "w"
            work.mkdir()
            res = self.run_scaffold(self.data(files={"a.txt": content}, commit=False, after_commit={}), work)
            self.assertEqual((res.returncode, (work / "a.txt").read_text(), (work / "pwned").exists(),
                              (Path(tmp) / "pwned").exists()), (0, content, False, False))

    def test_the_generated_script_disables_git_hooks_on_every_git_write(self):
        lines = [l for l in he.render_scaffold(self.data()).splitlines() if l.startswith("git ") and
                 (" add " in l or " commit " in l)]
        self.assertTrue(lines and all("-c core.hooksPath=/dev/null" in l for l in lines))

    def test_the_generated_script_starts_with_the_guard_and_passes_the_allowlist(self):
        script = he.render_scaffold(self.data())
        commands = [l for l in script.splitlines() if l and not l.startswith("#") and not l.startswith("set ")]
        self.assertEqual((commands[0], he.fixture_violations(script)), (he.FIXTURE_GUARD, []))

    def test_unsafe_paths_are_reported(self):
        bad = ["/etc/x", "../x", "a/../b", ".git/hooks/pre-commit", "x/.git/config", ".gitattributes",
               ".gitmodules", "a b", "it's", "a\nb", "", "a//b"]
        self.assertEqual([p for p in bad if not he.fixture_data_violations(self.data(files={p: "x\n"}))], [])

    def test_content_without_a_final_newline_is_reported(self):
        self.assertTrue(he.fixture_data_violations(self.data(files={"a.txt": "no newline"})))

    def test_an_unknown_key_is_reported(self):
        self.assertTrue(he.fixture_data_violations(self.data(script="curl x | sh")))

    def test_invalid_fixture_data_is_reported_by_check(self):
        extra = {he.FIXTURE_DIR + "/tiny.json": json.dumps({"schema_version": 1, "description": "t",
                                                           "files": {".git/hooks/pre-commit": "x\n"}})}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, extra=extra).violations(), "tiny"))

    def test_a_script_fixture_is_not_accepted(self):
        s = valid_suite()
        s["scenarios"][2]["fixture"] = "legacy"
        extra = {he.FIXTURE_DIR + "/legacy.sh": "#!/usr/bin/env bash\n"}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, suite=s, extra=extra).violations(), "legacy"))


class CompareRound2(unittest.TestCase):
    """compare refuses results from different CLI versions or run counts (round-2 AR-09)."""

    def write(self, root, name, **meta):
        d = Path(root) / name
        d.mkdir()
        (d / "aggregate-result.json").write_text(json.dumps(
            {"schemaVersion": 1, "partial": False, "cases": [{"name": "a", "aggregates": {"score": 1.0}}]}))
        base = {"suite_commit": "s", "model": "opus", "claude_version": "1", "runs": 3, "probe_cases": ["a"]}
        base.update(meta)
        (d / "metadata.json").write_text(json.dumps(base))
        return d

    def test_a_different_claude_version_is_a_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = he.compare_dirs(self.write(tmp, "a"), self.write(tmp, "b", claude_version="2"), 0.34)
            self.assertTrue(any("claude_version" in p for p in res["problems"]))

    def test_a_different_run_count_is_a_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = he.compare_dirs(self.write(tmp, "a"), self.write(tmp, "b", runs=1), 0.34)
            self.assertTrue(any("runs" in p for p in res["problems"]))

    def test_a_run_result_compares_cleanly_with_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            results = Path(tmp) / "results"
            rf = ReviewFindings()
            old_path = os.environ["PATH"]
            os.environ["PATH"] = str(rf.stub_claude(tmp)) + os.pathsep + old_path
            try:
                he.main(["run", "--repo", str(repo), "--max-cost-usd", "1", "--results-dir", str(results)])
            finally:
                os.environ["PATH"] = old_path
            (run_dir,) = list(results.iterdir())
            self.assertEqual(he.compare_dirs(run_dir, run_dir, 0.34)["problems"], [])


class ReviewRound3(unittest.TestCase):
    """Regression tests for the assurance review of afb2a63 (round 3)."""

    def data(self, files):
        return {"schema_version": 1, "description": "t", "files": files, "commit": True}

    def test_git_paths_are_refused_in_any_letter_case(self):
        bad = [".GIT/config", ".Git/hooks/pre-commit", "x/.gIt/config", ".GITATTRIBUTES", ".GitModules"]
        self.assertEqual([p for p in bad if not he.fixture_data_violations(self.data({p: "x\n"}))], [])

    def test_every_git_command_in_the_scaffold_disables_hooks_and_templates(self):
        lines = [l for l in he.render_scaffold(self.data({"a.txt": "x\n"})).splitlines() if l.startswith("git ")]
        self.assertTrue(len(lines) == 4 and all("-c core.hooksPath=/dev/null" in l for l in lines)
                        and "-c init.templateDir=" in lines[0])

    def test_a_scenario_granting_a_tool_beyond_read_only_is_reported(self):
        for tool in ("Bash", "Write", "Edit", "WebFetch", "WebSearch", "Agent"):
            s = valid_suite()
            s["scenarios"][1]["allowed_tools"] = ["Read", tool]
            with tempfile.TemporaryDirectory() as tmp:
                self.assertTrue(has(Tree(tmp, suite=s).violations(), tool), tool)

    def test_a_skill_that_carries_its_own_hooks_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp, extra={".claude/skills/alpha/hooks/hooks.json": "{}"})
            with self.assertRaises(he.BuildError):
                Build().build(repo, tmp)

    def test_a_result_without_metadata_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = CompareRound2().write(tmp, "a")
            b = Path(tmp) / "b"
            b.mkdir()
            (b / "aggregate-result.json").write_text((a / "aggregate-result.json").read_text())
            self.assertTrue(any("metadata" in p for p in he.compare_dirs(a, b, 0.34)["problems"]))

    def test_metadata_missing_a_compared_key_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = CompareRound2().write(tmp, "a"), CompareRound2().write(tmp, "b")
            for d in (a, b):
                meta = json.loads((d / "metadata.json").read_text())
                del meta["runs"]
                (d / "metadata.json").write_text(json.dumps(meta))
            self.assertTrue(any("runs" in p for p in he.compare_dirs(a, b, 0.34)["problems"]))


class ReviewRound4(unittest.TestCase):
    """Regression tests for the assurance review of 44b6b8e (round 4)."""

    def excluded_map(self):
        m = valid_map()
        m["components"][4]["in_eval"] = False
        m["components"][4]["reason"] = "could change real data"
        return m

    def test_a_skill_marked_out_of_the_eval_is_not_built(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Build().build(Build().make_repo(tmp, cmap=self.excluded_map()), tmp)
            self.assertEqual(sorted(p.name for p in (b.plugin_dir / "skills").iterdir()), ["alpha", "beta"])

    def test_expecting_a_skill_left_out_of_the_eval_is_reported(self):
        m = self.excluded_map()
        s = valid_suite()
        s["scenarios"][2]["graders"].append(
            skill_grader("uses-gamma", "gamma", "used", ".claude/skills/gamma/SKILL.md", "Do gamma things"))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m, suite=s).violations(), "left out of the eval"))

    def test_leaving_a_skill_out_needs_a_reason(self):
        m = valid_map()
        m["components"][4]["in_eval"] = False
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "skill:gamma: in_eval false needs a reason"))

    def test_a_skill_whose_frontmatter_declares_hooks_stops_the_build(self):
        hooked = SKILL_A.replace("---\n\n# Alpha", "hooks:\n  Stop: []\n---\n\n# Alpha")
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp, extra={".claude/skills/alpha/SKILL.md": hooked})
            self.assertEqual(he.check(repo, repo), [])
            with self.assertRaisesRegex(he.BuildError, "hooks"):
                Build().build(repo, tmp)


SKILL_D = "---\nname: delta\ndescription: Do delta things.\n---\n\n# Delta\n"


class ReviewRound5(unittest.TestCase):
    """Regression tests for the assurance review of 112db91 (round 5)."""

    def commit(self, repo, message):
        git(repo, "add", "-A")
        git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", message)
        return git(repo, "rev-parse", "HEAD")

    def build_refs(self, repo, tmp, harness_ref, suite_ref):
        out = Path(tmp) / "build"
        out.mkdir()
        return he.build(repo, harness_ref, suite_ref, out)

    def add_delta(self, repo):
        """Add a skill and give it a stage, as adding an owner for a gap would."""
        (repo / ".claude/skills/delta").mkdir()
        (repo / ".claude/skills/delta/SKILL.md").write_text(SKILL_D, encoding="utf-8")
        m = valid_map()
        m["components"].append({"id": "skill:delta", "path": ".claude/skills/delta/SKILL.md"})
        m["stages"][0]["owners"].append("skill:delta")
        (repo / he.MAP_PATH).write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")

    # AR-03: one suite must run against an older and a newer harness.

    def test_a_suite_that_maps_a_component_the_older_harness_lacks_still_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            self.add_delta(repo)
            self.assertEqual(he.check(repo, repo), [])
            after = self.commit(repo, "add delta")
            b = self.build_refs(repo, tmp, before, after)
            self.assertEqual(((b.plugin_dir / "skills/delta").exists(), has(b.drift, "skill:delta")), (False, True))

    def test_a_quote_the_older_harness_lacks_is_recorded_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            (repo / ".claude/skills/alpha/SKILL.md").write_text(
                SKILL_A.replace("Do alpha things", "Do alpha work"), encoding="utf-8")
            suite = (repo / he.SUITE_PATH).read_text(encoding="utf-8").replace("Do alpha things", "Do alpha work")
            (repo / he.SUITE_PATH).write_text(suite, encoding="utf-8")
            self.assertEqual(he.check(repo, repo), [])
            after = self.commit(repo, "reword alpha")
            b = self.build_refs(repo, tmp, before, after)
            self.assertTrue(has(b.drift, "Do alpha work"))

    def test_the_same_commit_for_both_has_no_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(Build().build(Build().make_repo(tmp), tmp).drift, [])

    def test_a_harness_component_the_suite_does_not_map_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            self.add_delta(repo)
            after = self.commit(repo, "add delta")
            with self.assertRaisesRegex(he.BuildError, "skill:delta"):
                self.build_refs(repo, tmp, after, before)

    def test_a_suite_inconsistent_with_its_own_commit_stops_a_cross_commit_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            s = CheckScenarios().three_compound()
            s["scenarios"][1]["stages"].append("X-typo")
            (repo / he.SUITE_PATH).write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
            after = self.commit(repo, "typo")
            with self.assertRaisesRegex(he.BuildError, "X-typo"):
                self.build_refs(repo, tmp, before, after)

    def test_the_drift_and_the_probe_cases_are_recorded_in_the_run_metadata(self):
        b = he.Built(Path("/p"), "h" * 40, "s" * 40, 1, "a", "b",
                     drift=["x"], probe_cases=["probe"], case_ids=["probe"])
        meta = he.run_metadata(b, "opus", 1, 1.0, [], "v")
        self.assertEqual((meta["harness_drift"], meta["probe_cases"], meta["case_ids"]), (["x"], ["probe"], ["probe"]))

    # AR-05: eval material bundled inside a skill never enters the build.

    def test_a_skills_own_eval_suite_and_scaffold_are_not_built(self):
        extra = {".claude/skills/alpha/evals/x/case.yaml": 'schema_version: "1.1"\nname: "x"\n',
                 ".claude/skills/alpha/evals/x/prompt.md": "do x\n",
                 ".claude/skills/alpha/evals/x/fixture.sh": "git init\n"}
        with tempfile.TemporaryDirectory() as tmp:
            b = Build().build(Build().make_repo(tmp, extra=extra), tmp)
            evals = b.plugin_dir / "evals"
            stray = [p for p in b.plugin_dir.rglob("*") if p.is_file() and evals not in p.parents]
            stray = [p for p in stray if p.name in ("case.yaml", "fixture.sh")]
            self.assertEqual(((b.plugin_dir / "skills/alpha/evals").exists(), stray), (False, []))

    def test_the_skill_files_outside_evals_are_still_copied(self):
        extra = {".claude/skills/alpha/evals/x/case.yaml": 'schema_version: "1.1"\n'}
        with tempfile.TemporaryDirectory() as tmp:
            b = Build().build(Build().make_repo(tmp, extra=extra), tmp)
            self.assertEqual((b.plugin_dir / "skills/alpha/scripts/tool.py").read_text(), "print('alpha')\n")

    # AR-08: the plugin.json branch of the trusted-hook guard.

    def test_a_skill_plugin_json_that_declares_hooks_stops_the_build(self):
        extra = {".claude/skills/alpha/.claude-plugin/plugin.json": json.dumps({"name": "alpha", "hooks": "./h.json"})}
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp, extra=extra)
            self.assertEqual(he.check(repo, repo), [])
            with self.assertRaisesRegex(he.BuildError, r"plugin\.json declares hooks"):
                Build().build(repo, tmp)

    def test_a_skill_plugin_json_without_hooks_builds(self):
        extra = {".claude/skills/alpha/.claude-plugin/plugin.json": json.dumps({"name": "alpha"})}
        with tempfile.TemporaryDirectory() as tmp:
            b = Build().build(Build().make_repo(tmp, extra=extra), tmp)
            self.assertTrue((b.plugin_dir / "skills/alpha/.claude-plugin/plugin.json").is_file())

    # AR-06: a result whose probe did not pass measures no harness.

    def write(self, root, name, probe_score=1.0, cases=None, **meta):
        d = Path(root) / name
        d.mkdir()
        if cases is None:
            cases = [{"name": "probe", "aggregates": {"score": probe_score}}, {"name": "a", "aggregates": {"score": 1.0}}]
        (d / "aggregate-result.json").write_text(json.dumps({"schemaVersion": 1, "partial": False, "cases": cases}))
        base = {"suite_commit": "s", "model": "opus", "claude_version": "1", "runs": 3, "probe_cases": ["probe"]}
        base.update(meta)
        (d / "metadata.json").write_text(json.dumps({k: v for k, v in base.items() if v is not None}))
        return d

    def problems(self, tmp, **after):
        return he.compare_dirs(self.write(tmp, "a"), self.write(tmp, "b", **after), 0.34)["problems"]

    def test_a_result_whose_probe_did_not_pass_in_every_run_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(self.problems(tmp, probe_score=0.8333), "the probe probe did not pass"))

    def test_a_result_without_its_probe_case_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases = [{"name": "a", "aggregates": {"score": 1.0}}]
            self.assertTrue(has(self.problems(tmp, cases=cases), "the probe probe did not pass"))

    def test_metadata_without_the_probe_cases_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(self.problems(tmp, probe_cases=None), "probe_cases"))

    def test_a_suite_without_a_probe_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(self.problems(tmp, probe_cases=[]), "no probe"))

    def test_passing_probes_on_both_sides_are_no_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.problems(tmp), [])

    # AR-02: which aggregate-result.json a result directory means.

    def test_the_shallowest_aggregate_result_is_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "aggregate-result.json").write_text(json.dumps({"cases": [{"name": "top"}]}))
            (d / "a/b").mkdir(parents=True)
            (d / "a/b/aggregate-result.json").write_text(json.dumps({"cases": [{"name": "nested"}]}))
            self.assertEqual(he.load_result(d)["cases"][0]["name"], "top")

    def test_two_aggregate_results_at_the_same_depth_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for sub in ("a", "b"):
                (d / sub).mkdir()
                (d / sub / "aggregate-result.json").write_text(json.dumps({"cases": []}))
            with self.assertRaisesRegex(ValueError, "aggregate-result.json"):
                he.load_result(d)

    def test_compare_exits_2_on_an_ambiguous_result_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.write(tmp, "a")
            amb = Path(tmp) / "amb"
            for sub in ("x", "y"):
                (amb / sub).mkdir(parents=True)
                (amb / sub / "aggregate-result.json").write_text(json.dumps({"cases": []}))
            self.assertEqual(he.main(["compare", str(a), str(amb)]), 2)

    # AR-04: a run checks that the eval ran exactly the suite's cases.

    def run_with_stub(self, tmp, **env):
        repo = Build().make_repo(tmp)
        results = Path(tmp) / "results"
        bindir = ReviewFindings().stub_claude(tmp)
        patched = {"PATH": str(bindir) + os.pathsep + os.environ["PATH"], **env}
        with mock.patch.dict(os.environ, patched):
            rc = he.main(["run", "--repo", str(repo), "--max-cost-usd", "1", "--results-dir", str(results)])
        (run_dir,) = list(results.iterdir())
        return rc, json.loads((run_dir / "metadata.json").read_text())

    def test_a_run_whose_cases_match_the_suite_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, meta = self.run_with_stub(tmp)
            self.assertEqual((rc, meta["cases_missing"], meta["cases_unexpected"]), (0, [], []))

    def test_a_run_whose_result_has_a_case_outside_the_suite_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, meta = self.run_with_stub(tmp, STUB_EXTRA_CASE="stray")
            self.assertEqual((rc, meta["cases_unexpected"]), (1, ["stray"]))

    def test_a_complete_run_that_lacks_a_suite_case_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, meta = self.run_with_stub(tmp, STUB_ONLY="probe")
            self.assertEqual((rc, len(meta["cases_missing"])), (1, 4))

    def test_compare_refuses_a_result_whose_run_found_unexpected_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(self.problems(tmp, cases_unexpected=["stray"]), "stray"))


class ReviewRound6(unittest.TestCase):
    """Regression tests for the assurance review of 6897bff (round 6)."""

    r5 = ReviewRound5()

    def reword(self, repo, old, new, *rels):
        """Replace a phrase in harness files and in the map and suite that quote it."""
        for rel in (*rels, he.MAP_PATH, he.SUITE_PATH):
            p = repo / rel
            p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def run_refs(self, repo, tmp, results, harness_ref, suite_ref):
        bindir = Path(tmp) / "bin"
        if not bindir.exists():
            ReviewFindings().stub_claude(tmp)
        with mock.patch.dict(os.environ, {"PATH": str(bindir) + os.pathsep + os.environ["PATH"]}):
            rc = he.main(["run", "--repo", str(repo), "--max-cost-usd", "1", "--results-dir", str(results),
                          "--harness-ref", harness_ref, "--suite-ref", suite_ref])
        (run_dir,) = [p for p in results.iterdir() if f"_h-{harness_ref[:12]}_" in p.name]
        return rc, run_dir

    # AR-01: the composed path, two harness commits on one suite, then compare.

    def test_two_harness_commits_run_on_one_suite_and_compare_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            self.r5.add_delta(repo)
            after = self.r5.commit(repo, "add delta")
            results = Path(tmp) / "results"
            rc1, d1 = self.run_refs(repo, tmp, results, before, after)
            rc2, d2 = self.run_refs(repo, tmp, results, after, after)
            m1, m2 = (json.loads((d / "metadata.json").read_text()) for d in (d1, d2))
            res = he.compare_dirs(d1, d2, 0.34)
            self.assertEqual((rc1, rc2, m1["harness_commit"], m1["suite_commit"], m2["harness_commit"],
                              bool(m1["harness_drift"]), m2["harness_drift"], res["problems"]),
                             (0, 0, before, after, after, True, [], []))

    # AR-02: a probe grader whose phrase a harness commit lacks cannot show injection.

    def test_a_probe_grader_whose_phrase_the_older_harness_lacks_is_left_out_and_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            self.reword(repo, "unrelated", "spare", ".claude/CLAUDE.md")
            self.assertEqual(he.check(repo, repo), [])
            after = self.r5.commit(repo, "reword the apex ending")
            b = self.r5.build_refs(repo, tmp, before, after)
            graders = sorted(p.stem for p in (b.plugin_dir / "evals/probe/graders").iterdir())
            self.assertEqual((graders, b.probe_unchecked), (["rule-reached"], ["probe/apex-reached (.claude/CLAUDE.md)"]))

    def test_the_same_commit_leaves_no_probe_grader_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(Build().build(Build().make_repo(tmp), tmp).probe_unchecked, [])

    def test_a_build_where_no_probe_reach_grader_can_pass_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            self.reword(repo, "unrelated", "spare", ".claude/CLAUDE.md")
            self.reword(repo, "approval", "consent", ".claude/rules/one.md")
            self.assertEqual(he.check(repo, repo), [])
            after = self.r5.commit(repo, "reword both endings")
            with self.assertRaisesRegex(he.BuildError, "probe"):
                self.r5.build_refs(repo, tmp, before, after)

    def test_compare_notes_the_probe_graders_left_out_without_refusing(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.r5.write(tmp, "a", probe_unchecked=["probe/apex-reached (.claude/CLAUDE.md)"])
            res = he.compare_dirs(a, self.r5.write(tmp, "b"), 0.34)
            self.assertEqual((res["problems"], has(res["notes"], "apex-reached")), ([], True))

    # AR-03: the run record lists the skills that were built.

    def test_the_run_record_lists_the_built_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Build().build(Build().make_repo(tmp, cmap=ReviewRound4().excluded_map()), tmp)
            meta = he.run_metadata(b, "opus", 1, 1.0, [], "v")
            self.assertEqual((b.skills, meta["skills"]), (["alpha", "beta"], ["alpha", "beta"]))

    # AR-05: a settings key the map does not classify stops a cross-commit build.

    def test_a_harness_settings_key_the_map_does_not_classify_stops_the_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            before = git(repo, "rev-parse", "HEAD")
            (repo / ".claude/settings.json").write_text(json.dumps(dict(SETTINGS, env={"X": "1"})), encoding="utf-8")
            m = valid_map()
            m["settings"]["env"] = {"in_eval": False, "reason": "not applied by the eval"}
            (repo / he.MAP_PATH).write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(he.check(repo, repo), [])
            after = self.r5.commit(repo, "add env")
            with self.assertRaisesRegex(he.BuildError, "env"):
                self.r5.build_refs(repo, tmp, after, before)

    # AR-07: raw results stay out of git until a person chooses to add them.

    def test_the_results_directory_is_ignored_by_git(self):
        root = Path(__file__).resolve().parents[2]
        res = subprocess.run(["git", "-C", str(root), "check-ignore", "-q",
                              he.RESULTS_DIR + "/20261107T000000Z_h-x_s-y/report.html"])
        self.assertEqual(res.returncode, 0)


class ReviewRound7(unittest.TestCase):
    """Regression tests for the assurance review of 0ac8e15 (round 7)."""

    r5, r6 = ReviewRound5(), ReviewRound6()

    def mapped(self, cid, path):
        m = valid_map()
        m["components"].append({"id": cid, "path": path})
        m["stages"][0]["owners"].append(cid)
        return m

    # AR-02: install.sh also syncs agents/ and commands/.

    def test_an_agent_file_is_a_component_that_the_map_must_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Tree(tmp, extra={".claude/agents/reviewer.md": "---\nname: reviewer\n---\nReview.\n"})
            self.assertTrue(has(t.violations(), "component agent:reviewer.md (.claude/agents/reviewer.md) is missing"))

    def test_a_command_file_is_a_component_that_the_map_must_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Tree(tmp, extra={".claude/commands/ship.md": "Ship it.\n"})
            self.assertTrue(has(t.violations(), "component command:ship.md (.claude/commands/ship.md) is missing"))

    def test_a_harness_with_a_mapped_agent_stops_the_build(self):
        extra = {".claude/agents/reviewer.md": "---\nname: reviewer\n---\nReview.\n"}
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp, extra=extra, cmap=self.mapped("agent:reviewer.md", ".claude/agents/reviewer.md"))
            self.assertEqual(he.check(repo, repo), [])
            with self.assertRaisesRegex(he.BuildError, "agents and commands"):
                Build().build(repo, tmp)

    def test_a_harness_with_a_mapped_command_stops_the_build(self):
        extra = {".claude/commands/ship.md": "Ship it.\n"}
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp, extra=extra, cmap=self.mapped("command:ship.md", ".claude/commands/ship.md"))
            self.assertEqual(he.check(repo, repo), [])
            with self.assertRaisesRegex(he.BuildError, "agents and commands"):
                Build().build(repo, tmp)

    # AR-03: only reach graders depend on their phrase being present.

    def test_a_non_reach_probe_grader_is_kept_when_its_phrase_is_gone(self):
        s = valid_suite()
        s["scenarios"][0]["graders"].append(
            {"id": "no-tool-used", "type": "tool", "tool": "Bash", "input_match": "command", "min": 0, "max": 0,
             "basis": {"file": ".claude/CLAUDE.md", "quote": "Keep unrelated work"},
             "examples": {"match": ["{\"command\":\"cat x\"}"], "no_match": ["{}"]}})
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp, suite=s)
            before = git(repo, "rev-parse", "HEAD")
            self.r6.reword(repo, "unrelated", "spare", ".claude/CLAUDE.md")
            self.assertEqual(he.check(repo, repo), [])
            after = self.r5.commit(repo, "reword the apex ending")
            b = self.r5.build_refs(repo, tmp, before, after)
            graders = sorted(p.stem for p in (b.plugin_dir / "evals/probe/graders").iterdir())
            self.assertEqual((graders, b.probe_unchecked),
                             (["no-tool-used", "rule-reached"], ["probe/apex-reached (.claude/CLAUDE.md)"]))

    # AR-04: the missing-case branches of compare and run.

    def test_compare_refuses_a_complete_result_whose_run_missed_suite_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(self.r5.problems(tmp, cases_missing=["ask-first"]), "did not run these suite cases"))

    def test_a_partial_run_that_lacks_cases_records_them_and_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, meta = self.r5.run_with_stub(tmp, STUB_ONLY="probe", STUB_PARTIAL="1")
            self.assertEqual((rc, len(meta["cases_missing"]), meta["eval_exit_code"]), (0, 4, 2))


class ReviewRound8(unittest.TestCase):
    """Regression tests for the assurance review of 4e6b18e (round 8)."""

    # AR-02: fixture data must not write what Claude Code reads as configuration.

    def test_fixture_paths_that_claude_code_reads_as_configuration_are_refused(self):
        bad = [".claude/settings.json", ".Claude/hooks.json", "CLAUDE.md", "sub/claude.md", "CLAUDE.local.md",
               ".mcp.json", "x/.claude-plugin/plugin.json"]
        fd = FixtureData()
        self.assertEqual([p for p in bad if not has(he.fixture_data_violations(fd.data(files={p: "x\n"})), "unsafe path")], [])

    def test_ordinary_fixture_paths_are_still_accepted(self):
        fd = FixtureData()
        self.assertEqual(he.fixture_data_violations(fd.data(files={"docs/claude-notes.md": "x\n", "README.md": "x\n"})), [])

    # AR-03: the two untested guards of the build.

    def test_a_case_yaml_elsewhere_in_a_skill_stops_the_build(self):
        extra = {".claude/skills/alpha/extra/case.yaml": 'schema_version: "1.1"\n'}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(he.BuildError, "eval cases outside the generated evals/"):
                Build().build(Build().make_repo(tmp, extra=extra), tmp)

    def test_a_build_directory_outside_the_temporary_directory_is_refused(self):
        with self.assertRaisesRegex(he.BuildError, "not under the temporary directory"):
            he.ensure_outside(Path("/usr/share/harness-eval-check"), Path("/nonexistent-repo"))

    # AR-04: the scenario rules R2-A1 names.

    def suite_violations(self, edit):
        s = valid_suite()
        edit(s["scenarios"][1])
        with tempfile.TemporaryDirectory() as tmp:
            return Tree(tmp, suite=s).violations()

    def test_a_scenario_without_graders_is_reported(self):
        self.assertTrue(has(self.suite_violations(lambda sc: sc.update(graders=[])),
                            "scenario ask-first: needs at least one grader"))

    def test_a_non_probe_scenario_without_stages_is_reported(self):
        self.assertTrue(has(self.suite_violations(lambda sc: sc.update(stages=[])), "scenario ask-first: names no stage"))

    def test_a_grader_without_basis_is_reported(self):
        self.assertTrue(has(self.suite_violations(lambda sc: sc["graders"][0].pop("basis")),
                            "grader uses-alpha: needs a basis with file and quote"))

    def test_a_basis_with_an_empty_quote_is_reported(self):
        self.assertTrue(has(self.suite_violations(lambda sc: sc["graders"][0]["basis"].update(quote=" ")),
                            "grader uses-alpha: basis needs a file and a non-empty quote"))

    # AR-05: the map rules R1-A1 names for stages and boundary groups.

    def map_violations(self, edit):
        m = valid_map()
        edit(m)
        with tempfile.TemporaryDirectory() as tmp:
            return Tree(tmp, cmap=m).violations()

    def test_a_stage_without_basis_is_reported(self):
        self.assertTrue(has(self.map_violations(lambda m: m["stages"][0].update(basis=[])),
                            "stage D-ask: needs a basis with file and quote"))

    def test_a_boundary_group_without_basis_is_reported(self):
        self.assertTrue(has(self.map_violations(lambda m: m["boundary_groups"][0].update(basis=[])),
                            "boundary group G-ab: needs a basis with file and quote"))

    def test_a_boundary_group_quote_absent_from_its_file_is_reported(self):
        self.assertTrue(has(self.map_violations(lambda m: m["boundary_groups"][0]["basis"][0].update(quote="Not here")),
                            "boundary group G-ab: quote not found"))

    def test_a_boundary_group_with_one_member_is_reported(self):
        self.assertTrue(has(self.map_violations(lambda m: m["boundary_groups"][0].update(members=["skill:alpha"])),
                            "boundary group G-ab: needs two or more skill components"))

    def test_a_boundary_group_member_outside_the_map_is_reported(self):
        self.assertTrue(has(self.map_violations(
            lambda m: m["boundary_groups"][0].update(members=["skill:alpha", "skill:zeta"])),
            "boundary group G-ab: needs two or more skill components"))

    # AR-06: file tools run outside the OS sandbox, so a run records where the
    # real home directory's path shows up in its results.

    def test_a_run_records_result_files_that_mention_the_real_home_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, meta = ReviewRound5().run_with_stub(tmp, STUB_LEAK="1")
            self.assertEqual((rc, meta["home_path_files"]), (0, ["transcript.txt"]))

    def test_a_run_whose_results_do_not_mention_the_home_directory_records_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, meta = ReviewRound5().run_with_stub(tmp)
            self.assertEqual((rc, meta["home_path_files"]), (0, []))


class SmokeRunFindings(unittest.TestCase):
    """Regression tests for what the first real run (24 cases x 1 at 2822abe) showed."""

    def errored(self, name="probe"):
        return {"name": name, "aggregates": {"score": 0},
                "arms": {"with": [{"score": 0, "error": "exit 1: You've hit your 5-hour limit"}]}}

    def test_a_case_whose_run_ended_on_an_error_is_listed(self):
        result = {"cases": [self.errored("x"), {"name": "y", "aggregates": {"score": 1},
                                                "arms": {"with": [{"score": 1, "error": None}]}}]}
        self.assertEqual(he.errored_cases(result), ["x"])

    def test_compare_refuses_a_result_with_runs_that_ended_on_an_error(self):
        cases = [{"name": "probe", "aggregates": {"score": 1.0}}, self.errored("a")]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(ReviewRound5().problems(tmp, cases=cases), "ended on an error before grading"))

    def test_a_run_records_the_cases_whose_runs_ended_on_an_error_and_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            # The stub reports every built case, then one more errored run of the probe.
            rc, meta = ReviewRound5().run_with_stub(tmp, STUB_ONLY="ask-first beta-flow gap-watch ask-again",
                                                    STUB_ERROR_CASE="probe")
            self.assertEqual((rc, meta["errored_cases"]), (1, ["probe"]))


class ReviewRound9(unittest.TestCase):
    """Regression tests for the assurance review of 302e224 (round 9)."""

    # AR-03: an eval that exited on an error is refused even if no run carries an error field.

    def test_compare_refuses_a_result_whose_eval_exited_with_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(ReviewRound5().problems(tmp, eval_exit_code=1), "the eval exited with code 1"))

    def test_a_clean_or_partial_eval_exit_code_adds_no_such_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(has(ReviewRound5().problems(tmp, eval_exit_code=0), "the eval exited"))

    # AR-04: results go only where git ignores them, and never into ~/.claude.

    def run_into(self, tmp, results_dir):
        """`run` with the stub claude first on PATH, so no test can reach the real CLI."""
        repo = Build().make_repo(tmp)
        bindir = ReviewFindings().stub_claude(tmp)
        with mock.patch.dict(os.environ, {"PATH": str(bindir) + os.pathsep + os.environ["PATH"]}):
            return he.main(["run", "--repo", str(repo), "--max-cost-usd", "1", "--results-dir", str(results_dir)])

    def test_a_results_directory_inside_the_claude_config_is_refused(self):
        target = Path.home() / ".claude" / "harness-eval-results-check"
        with tempfile.TemporaryDirectory() as tmp:
            rc = self.run_into(tmp, target)
        self.assertEqual((rc, target.exists()), (2, False))

    def test_a_results_directory_inside_another_git_work_tree_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp) / "other"
            other.mkdir()
            git(other, "init", "-q")
            rc = self.run_into(tmp, other / "out")
            self.assertEqual((rc, (other / "out").exists()), (2, False))

    def test_the_repositorys_ignored_results_directory_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            he.ensure_results_dir(repo / he.RESULTS_DIR, repo)

    def test_a_results_directory_elsewhere_in_the_repository_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Build().make_repo(tmp)
            with self.assertRaisesRegex(he.BuildError, "git work tree"):
                he.ensure_results_dir(repo / "docs" / "results", repo)


if __name__ == "__main__":
    unittest.main()
