"""Behavior tests for scripts/check.py.

Run from the skill directory: python3 -B -m unittest discover -s tests -v
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import check  # noqa: E402


def codes(findings: list[check.Finding]) -> set[tuple[str, str]]:
    return {(f.sev, f.rule) for f in findings}


def rules(findings: list[check.Finding], rule: str) -> list[check.Finding]:
    return [f for f in findings if f.rule == rule]


GOOD_MD = """# 薬Aは血圧を下げる

答えの文。

## 設計は妥当である

設計の主張。

## 収縮期血圧が下がった

結果の主張。
"""

GOOD_ANSWER = """Bに移行すべきです。運用費が下がり、移行リスクは戻せる範囲に収まるためです。

- **運用費は年30%下がる。** 見積もりの内訳は次のとおり。
- **移行は段階的に戻せる。** 旧系を並行稼働させる。
"""


def node(nid: str, parent: str | None, kind: str = "claim", text: str = "X holds.", **kw: Any) -> dict[str, Any]:
    return {"id": nid, "parent": parent, "kind": kind, "text": text, **kw}


def tree(*nodes: dict[str, Any]) -> dict[str, Any]:
    return {"nodes": list(nodes)}


class HeadingChecks(unittest.TestCase):
    def test_well_formed_document_has_no_findings(self) -> None:
        self.assertEqual(check.check_md(GOOD_MD), [])

    def test_heading_level_skip_is_error(self) -> None:
        md = "# T\n\nlead\n\n### Deep\n\nbody\n\n### Deep2\n\nbody\n"
        self.assertIn(("E", "S1"), codes(check.check_md(md)))

    def test_single_child_section_is_warning(self) -> None:
        md = "# T\n\nlead\n\n## A\n\nbody\n\n### A1\n\nbody\n\n## B\n\nbody\n"
        self.assertIn(("W", "S2"), codes(check.check_md(md)))

    def test_parent_without_lead_text_is_warning(self) -> None:
        # A claim-sentence heading can carry the summary, so only judgment can decide.
        md = "# T\n\n## A\n\nbody\n\n## B\n\nbody\n"
        self.assertIn(("W", "S3"), codes(check.check_md(md)))

    def test_leaf_without_body_is_error(self) -> None:
        md = "# T\n\nlead\n\n## A\n\n## B\n\nbody\n"
        self.assertIn(("E", "S4"), codes(check.check_md(md)))

    def test_topic_label_heading_is_warning(self) -> None:
        md = "# T\n\nlead\n\n## 1. Results\n\nbody\n\n## 考察\n\nbody\n"
        self.assertEqual(len(rules(check.check_md(md), "S5")), 2)

    def test_template_heading_is_not_flagged_as_label(self) -> None:
        md = "# T\n\nlead\n\n## Methods\n\nbody\n\n## Results\n\nbody\n"
        found = check.check_md(md, template=frozenset({"methods", "results"}))
        self.assertNotIn(("W", "S5"), codes(found))

    def test_offtree_section_is_not_flagged_as_label(self) -> None:
        md = "# T\n\nlead\n\n## A claim\n\nbody\n\n## B claim\n\nbody\n\n## References\n\nbody\n"
        self.assertNotIn(("W", "S5"), codes(check.check_md(md)))

    def test_offtree_sections_do_not_count_toward_group_size(self) -> None:
        md = "# T\n\nlead\n\n## A\n\nx\n\n## B\n\nx\n\n## 出典\n\nx\n\n## Checklist\n\nx\n"
        self.assertIn(("W", "S6"), codes(check.check_md(md, max_group=2)))
        self.assertNotIn(("W", "S6"), codes(check.check_md(md, max_group=2, offtree=frozenset({"checklist"}))))

    def test_single_claim_child_beside_offtree_is_warning(self) -> None:
        md = "# T\n\nlead\n\n## A\n\nx\n\n## References\n\nx\n"
        self.assertIn(("W", "S2"), codes(check.check_md(md)))

    def test_group_larger_than_max_is_warning(self) -> None:
        md = "# T\n\nlead\n\n## A\n\nx\n\n## B\n\nx\n\n## C\n\nx\n"
        self.assertIn(("W", "S6"), codes(check.check_md(md, max_group=2)))
        self.assertNotIn(("W", "S6"), codes(check.check_md(md, max_group=3)))

    def test_missing_pair_counterpart_is_error(self) -> None:
        md = (
            "# T\n\nlead\n\n## M\n\nlead\n\n### M1 a\n\nx\n\n### M2 b\n\nx\n\n"
            "## R\n\nlead\n\n### R1 a\n\nx\n\n### R3 c\n\nx\n"
        )
        found = rules(check.check_md(md, pairs=[("M", "R")]), "S7")
        msgs = " ".join(f.msg for f in found)
        self.assertEqual(len(found), 2)
        self.assertIn("M2", msgs)
        self.assertIn("R3", msgs)

    def test_headings_inside_code_fence_are_ignored(self) -> None:
        md = "# T\n\nlead\n\n## A\n\n```\n#### not a heading\n```\n\n## B\n\nbody\n"
        self.assertEqual(check.check_md(md), [])


class AnswerChecks(unittest.TestCase):
    """Heading-less answers: lists form the tree, and the answer must come first."""

    def test_well_formed_answer_has_no_findings(self) -> None:
        self.assertEqual(check.check_md(GOOD_ANSWER), [])

    def test_answer_opening_with_list_is_warning(self) -> None:
        self.assertIn(("W", "S8"), codes(check.check_md("- a holds\n- b holds\n")))
        self.assertIn(("W", "S8"), codes(check.check_md("# T\n\n- a holds\n- b holds\n")))

    def test_answer_opening_with_table_is_warning(self) -> None:
        self.assertIn(("W", "S8"), codes(check.check_md("| a | b |\n|---|---|\n| 1 | 2 |\n")))

    def test_front_matter_is_skipped_for_opening_check(self) -> None:
        md = "---\ntitle: x\n---\nAnswer.\n\n- a holds\n- b holds\n"
        self.assertEqual(check.check_md(md), [])

    def test_list_item_with_single_subitem_is_warning(self) -> None:
        md = "Answer.\n\n- **A holds.**\n  - only evidence\n- **B holds.**\n  - e1\n  - e2\n"
        self.assertIn(("W", "S2"), codes(check.check_md(md)))

    def test_single_item_list_is_warning(self) -> None:
        self.assertIn(("W", "S2"), codes(check.check_md("Answer.\n\n- only point\n")))

    def test_label_lead_in_list_item_is_warning(self) -> None:
        md = "Answer.\n\n- **Reasons:** cost is low\n- リスク：移行が難しい\n"
        self.assertEqual(len(rules(check.check_md(md), "S5")), 2)

    def test_template_label_lead_in_list_item_is_not_flagged(self) -> None:
        md = "Answer.\n\n- Methods: the design is valid\n- Results: the difference holds\n"
        found = check.check_md(md, template=frozenset({"methods", "results"}))
        self.assertNotIn(("W", "S5"), codes(found))

    def test_claim_lead_in_list_item_is_not_label(self) -> None:
        md = "Answer.\n\n- **Cost falls by 30%.** evidence\n- **Risk is reversible.** evidence\n"
        self.assertNotIn(("W", "S5"), codes(check.check_md(md)))

    def test_list_group_larger_than_max_is_warning(self) -> None:
        md = "Answer.\n\n- a\n- b\n- c\n"
        self.assertIn(("W", "S6"), codes(check.check_md(md, max_group=2)))

    def test_lists_separated_by_paragraph_are_separate_groups(self) -> None:
        md = "Answer.\n\n- a\n- b\n\nMore.\n\n- c\n- d\n"
        self.assertNotIn(("W", "S6"), codes(check.check_md(md, max_group=3)))

    def test_bold_only_line_with_topic_label_is_warning(self) -> None:
        md = "Answer.\n\n**Reasons**\n\n- a holds\n- b holds\n"
        self.assertIn(("W", "S5"), codes(check.check_md(md)))

    def test_bold_only_line_with_claim_is_not_label(self) -> None:
        md = "Answer.\n\n**Cost falls by 30%.**\n\n- a holds\n- b holds\n"
        self.assertNotIn(("W", "S5"), codes(check.check_md(md)))

    def test_lists_under_offtree_sections_are_not_checked(self) -> None:
        md = "# T\n\nlead\n\n## A claim\n\nx\n\n## B claim\n\nx\n\n## References\n\n- Book\n  - link\n"
        self.assertEqual(check.check_md(md), [])

    def test_findings_are_sorted_by_line(self) -> None:
        md = "- x\n\n# T\n\n## A\n\n## B\n\nbody\n"
        lines = [int(f.loc[1:]) for f in check.check_md(md) if f.loc.startswith("L")]
        self.assertEqual(lines, sorted(lines))


class TreeChecks(unittest.TestCase):
    def test_duplicate_ids_is_schema_error(self) -> None:
        self.assertIn(("E", "T1"), codes(check.check_tree(tree(node("a", None), node("a", None)))))

    def test_unknown_kind_is_schema_error(self) -> None:
        self.assertIn(("E", "T1"), codes(check.check_tree(tree(node("a", None, kind="note")))))

    def test_multiple_roots_is_error(self) -> None:
        self.assertIn(("E", "T2"), codes(check.check_tree(tree(node("a", None), node("b", None)))))

    def test_cycle_is_error(self) -> None:
        t = tree(node("r", None), node("a", "b"), node("b", "a"))
        self.assertIn(("E", "T2"), codes(check.check_tree(t)))

    def test_single_claim_child_is_warning(self) -> None:
        self.assertIn(("W", "T3"), codes(check.check_tree(tree(node("r", None), node("a", "r")))))

    def test_group_without_order_is_error(self) -> None:
        t = tree(node("r", None), node("a", "r"), node("b", "r"))
        self.assertIn(("E", "T4"), codes(check.check_tree(t)))

    def test_deductive_group_over_four_is_error(self) -> None:
        kids = [node(f"c{i}", "r") for i in range(5)]
        t = tree(node("r", None, order="deductive", reason="skeptical reader"), *kids)
        self.assertIn(("E", "T5"), codes(check.check_tree(t)))

    def test_more_than_two_therefore_is_error(self) -> None:
        kids = [node(f"c{i}", "r", therefore=True) for i in range(3)]
        t = tree(node("r", None, order="deductive", reason="x"), node("p", "r"), *kids)
        self.assertIn(("E", "T6"), codes(check.check_tree(t)))

    def test_deductive_key_line_without_reason_is_warning(self) -> None:
        t = tree(node("r", None, order="deductive"), node("a", "r"), node("b", "r"))
        self.assertIn(("W", "T7"), codes(check.check_tree(t)))

    def test_valid_modus_ponens_passes_validity(self) -> None:
        t = tree(
            node("r", None, order="deductive", reason="x"),
            node("m", "r", prop="valid & diff -> effect"),
            node("p", "r", prop="valid & diff"),
            node("c", "r", prop="effect", therefore=True),
        )
        self.assertEqual(rules(check.check_tree(t), "T8"), [])

    def test_invalid_deduction_reports_countermodel(self) -> None:
        t = tree(
            node("r", None, order="deductive", reason="x"),
            node("m", "r", prop="p -> q"),
            node("c", "r", prop="p", therefore=True),
        )
        found = rules(check.check_tree(t), "T8")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].sev, "E")
        self.assertIn("p=0", found[0].msg)

    def test_missing_prop_reports_unchecked_info(self) -> None:
        t = tree(node("r", None, order="deductive", reason="x"), node("m", "r", prop="p -> q"), node("c", "r"))
        self.assertIn(("I", "T8"), codes(check.check_tree(t)))

    def test_bad_formula_is_error(self) -> None:
        t = tree(node("r", None, order="deductive", reason="x"), node("m", "r", prop="p ->"), node("c", "r", prop="q"))
        self.assertIn(("E", "T8"), codes(check.check_tree(t)))

    def test_context_over_two_sentences_is_warning(self) -> None:
        t = tree(node("r", None), node("x", "r", kind="context", text="一。二。三。"))
        self.assertIn(("W", "T9"), codes(check.check_tree(t)))

    def test_nonclaim_with_children_is_error(self) -> None:
        t = tree(node("r", None), node("x", "r", kind="record"), node("y", "x", kind="record"))
        self.assertIn(("E", "T10"), codes(check.check_tree(t)))

    def test_significance_off_root_is_warning(self) -> None:
        t = tree(
            node("r", None, order="structural"),
            node("a", "r"),
            node("b", "r"),
            node("s", "a", kind="significance"),
        )
        self.assertIn(("W", "T10"), codes(check.check_tree(t)))

    def test_overlapping_scopes_is_me_error(self) -> None:
        t = tree(
            node("r", None, order="structural", universe=["cost", "risk"]),
            node("a", "r", scope=["cost"]),
            node("b", "r", scope=["cost", "risk"]),
        )
        self.assertTrue(any("overlap" in f.msg for f in rules(check.check_tree(t), "T11")))

    def test_uncovered_universe_is_ce_error(self) -> None:
        t = tree(
            node("r", None, order="structural", universe=["cost", "risk", "time"]),
            node("a", "r", scope=["cost"]),
            node("b", "r", scope=["risk"]),
        )
        self.assertTrue(any("time" in f.msg for f in rules(check.check_tree(t), "T11")))

    def test_label_claim_is_error(self) -> None:
        t = tree(node("r", None, order="structural"), node("a", "r", text="Results"), node("b", "r"))
        self.assertIn(("E", "T12"), codes(check.check_tree(t)))


class FormulaEngine(unittest.TestCase):
    def test_parser_rejects_bad_syntax(self) -> None:
        for bad in ["p &", "(p", "p q", "p -> -> q", "1p"]:
            with self.subTest(bad=bad), self.assertRaises(check.FormulaError):
                check.entails([bad], "p")

    def test_entails_returns_none_when_valid(self) -> None:
        self.assertIsNone(check.entails(["p -> q", "p"], "q"))

    def test_entails_supports_biconditional_and_negation(self) -> None:
        self.assertIsNone(check.entails(["p <-> q", "!q"], "!p"))


class Cli(unittest.TestCase):
    def run_main(self, argv: list[str], stdin: str | None = None) -> tuple[int, str]:
        out = io.StringIO()
        old_stdin = sys.stdin
        try:
            if stdin is not None:
                sys.stdin = io.StringIO(stdin)
            with contextlib.redirect_stdout(out):
                code = check.main(argv)
        finally:
            sys.stdin = old_stdin
        return code, out.getvalue()

    def test_exit_code_is_1_on_error_and_0_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            bad, good = Path(d) / "bad.md", Path(d) / "good.md"
            bad.write_text("# T\n\nlead\n\n## A\n\n## B\n\nx\n", encoding="utf-8")
            good.write_text(GOOD_MD, encoding="utf-8")
            self.assertEqual(self.run_main(["md", str(bad)])[0], 1)
            code, out = self.run_main(["md", str(good)])
            self.assertEqual(code, 0)
            self.assertTrue(out.strip().endswith("ok"))

    def test_reads_stdin_when_file_is_dash(self) -> None:
        code, out = self.run_main(["md", "-"], stdin=GOOD_ANSWER)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "ok")

    def test_tree_reads_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "t.json"
            f.write_text(json.dumps(tree(node("a", None), node("b", None))), encoding="utf-8")
            self.assertEqual(self.run_main(["tree", str(f)])[0], 1)


if __name__ == "__main__":
    unittest.main()
