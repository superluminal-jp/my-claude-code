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
                          "examples": {"match": ["keep unrelated work."], "no_match": ["keep related work"]}}]},
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
            he.FIXTURE_DIR + "/tiny.sh": "#!/usr/bin/env bash\nset -euo pipefail\n" + he.FIXTURE_GUARD + "\necho hi > a.txt\n",
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
            self.assertTrue(has(Tree(tmp, cmap=m).violations(), "D-gap"))

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
            self.assertTrue(has(Tree(tmp, suite=s).violations(), "probe"))

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

    def test_a_fixture_that_uses_the_network_is_reported(self):
        extra = {he.FIXTURE_DIR + "/tiny.sh": "#!/usr/bin/env bash\ngit remote add origin x\n"}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, extra=extra).violations(), "tiny"))

    def test_a_fixture_without_the_empty_directory_guard_is_reported(self):
        extra = {he.FIXTURE_DIR + "/tiny.sh": "#!/usr/bin/env bash\nset -euo pipefail\necho hi > a.txt\n"}
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(has(Tree(tmp, extra=extra).violations(), "empty"))

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
        Tree(repo, suite=CheckScenarios().three_compound(), **kw)
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


if __name__ == "__main__":
    unittest.main()
