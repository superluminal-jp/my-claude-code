"""Acceptance tests for scripts/check_diagrams.py (Python standard library only).

Run from the skill folder:  python3 -B -m unittest discover -s tests -v
"""

import base64
import importlib.util
import io
import sys
import tempfile
import textwrap
import unittest
import urllib.parse
import zlib
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CHECKER = SKILL_DIR / "scripts" / "check_diagrams.py"
EXAMPLE = SKILL_DIR / "examples" / "library-reservation"

spec = importlib.util.spec_from_file_location("check_diagrams", CHECKER)
check_diagrams = importlib.util.module_from_spec(spec)
sys.modules["check_diagrams"] = check_diagrams  # dataclasses look their module up here
spec.loader.exec_module(check_diagrams)


def page(diagram, title="# システムコンテキスト図: 蔵書予約システム", lead="この図は、だれが蔵書予約システムを使うかを示す。",
         legend="## 凡例\n\n| 記号 | 意味 |\n|---|---|\n| 四角 | ソフトウェアシステム |\n"):
    parts = [title, "", lead, "", diagram, "", legend]
    return "\n".join(p for p in parts if p is not None)


GOOD_FLOWCHART = textwrap.dedent('''\
    ```mermaid
    flowchart LR
      accTitle: 蔵書予約システムのシステムコンテキスト図
      accDescr: 利用者が蔵書予約システムで本を予約し、システムがメール配信サービスで通知を送る。
      user(["利用者<br/>[Person]<br/>本を探して予約する"]):::person
      sys["蔵書予約システム<br/>[Software System]<br/>予約と貸出を管理する"]:::system
      mail["メール配信サービス<br/>[Software System: 外部]<br/>通知メールを送る"]:::external
      user -->|"本を検索し予約する"| sys
      sys -->|"予約完了を通知する<br/>[SMTP]"| mail
      classDef person fill:#CFE0F3,stroke:#1F4E79,color:#0B1F33
      classDef system fill:#DCE9F7,stroke:#1F4E79,color:#0B1F33
      classDef external fill:#EDEDED,stroke:#4D4D4D,stroke-dasharray:5 3,color:#0B1F33
    ```''')


def drawio_xml(cells, compressed=False):
    model = "<mxGraphModel><root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>" + cells + "</root></mxGraphModel>"
    if compressed:
        raw = urllib.parse.quote(model, safe="")
        deflater = zlib.compressobj(9, zlib.DEFLATED, -15)
        data = deflater.compress(raw.encode()) + deflater.flush()
        inner = base64.b64encode(data).decode()
    else:
        inner = model
    return f"<mxfile><diagram id=\"p1\" name=\"Context\">{inner}</diagram></mxfile>"


TITLE_CELL = '<mxCell id="title" value="システムコンテキスト図: 蔵書予約システム" style="text;" vertex="1" parent="1"><mxGeometry as="geometry"/></mxCell>'
LEGEND_CELL = ('<mxCell id="legend" value="凡例" style="swimlane;" vertex="1" parent="1"><mxGeometry as="geometry"/></mxCell>'
               '<mxCell id="legend-swatch" value="" style="rounded=1;" vertex="1" parent="legend"><mxGeometry as="geometry"/></mxCell>')
NODES = ('<mxCell id="a" value="利用者 [Person]" style="rounded=1;" vertex="1" parent="1"><mxGeometry as="geometry"/></mxCell>'
         '<mxCell id="b" value="蔵書予約システム [Software System]" style="rounded=1;" vertex="1" parent="1"><mxGeometry as="geometry"/></mxCell>')
LABELLED_EDGE = '<mxCell id="e1" value="予約する" edge="1" source="a" target="b" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>'

GOOD_DSL = textwrap.dedent('''\
    workspace "蔵書予約" "図書館の蔵書予約" {
        model {
            user = person "利用者" "本を探して予約する"
            sys = softwareSystem "蔵書予約システム" "予約と貸出を管理する" {
                web = container "Web アプリ" "画面を提供する" "React"
                api = container "API" "予約を受け付ける" "Python"
            }
            user -> web "本を検索し予約する" "HTTPS"
            web -> api "予約を登録する" "JSON/HTTPS"
        }
        views {
            systemContext sys "context" "蔵書予約システムのシステムコンテキスト図" {
                include *
                autoLayout lr
            }
            container sys "containers" "蔵書予約システムのコンテナ図" {
                include *
                autoLayout lr
            }
        }
    }
    ''')


class CheckerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def codes(self, *paths, **kwargs):
        findings = check_diagrams.check_paths([str(p) for p in paths], **kwargs)
        return {f.code for f in findings}, findings


class TestMarkdownPage(CheckerTestCase):
    def test_good_page_has_no_findings(self):
        p = self.write("context.md", page(GOOD_FLOWCHART))
        codes, findings = self.codes(p)
        self.assertEqual(set(), codes, findings)

    def test_missing_title(self):
        p = self.write("context.md", page(GOOD_FLOWCHART, title=None))
        self.assertIn("P1", self.codes(p)[0])

    def test_missing_lead_paragraph(self):
        p = self.write("context.md", page(GOOD_FLOWCHART, lead=None))
        self.assertIn("P2", self.codes(p)[0])

    def test_missing_legend(self):
        p = self.write("context.md", page(GOOD_FLOWCHART, legend=None))
        self.assertIn("P3", self.codes(p)[0])

    def test_english_legend_heading_counts(self):
        p = self.write("context.md", page(GOOD_FLOWCHART, legend="## Legend\n\n| Shape | Meaning |\n|---|---|\n| Box | System |\n"))
        self.assertNotIn("P3", self.codes(p)[0])

    def test_image_without_alt_text(self):
        p = self.write("deploy.md", page("![](deploy.drawio.svg)"))
        self.assertIn("P4", self.codes(p)[0])

    def test_image_with_alt_text_is_a_diagram(self):
        p = self.write("deploy.md", page("![本番環境のデプロイ図](deploy.drawio.svg)"))
        self.assertEqual(set(), self.codes(p)[0])

    def test_two_diagrams_on_one_page(self):
        p = self.write("context.md", page(GOOD_FLOWCHART + "\n\n" + GOOD_FLOWCHART))
        self.assertIn("P5", self.codes(p)[0])

    def test_page_without_diagram_is_not_a_view(self):
        p = self.write("notes.md", "メモだけのページ。\n")
        self.assertEqual(set(), self.codes(p)[0])


class TestMermaidFlowchart(CheckerTestCase):
    def check_block(self, block, **kwargs):
        p = self.write("view.md", page(block))
        return self.codes(p, **kwargs)[0]

    def test_missing_acc_title_and_description(self):
        block = GOOD_FLOWCHART.replace("  accTitle: 蔵書予約システムのシステムコンテキスト図\n", "")
        block = block.replace("  accDescr: 利用者が蔵書予約システムで本を予約し、システムがメール配信サービスで通知を送る。\n", "")
        codes = self.check_block(block)
        self.assertIn("M1", codes)
        self.assertIn("M2", codes)

    def test_multiline_acc_description_counts(self):
        block = GOOD_FLOWCHART.replace(
            "  accDescr: 利用者が蔵書予約システムで本を予約し、システムがメール配信サービスで通知を送る。\n",
            "  accDescr {\n    利用者が本を予約する。\n    システムが通知を送る。\n  }\n")
        self.assertEqual(set(), self.check_block(block))

    def test_unlabelled_relationship(self):
        block = GOOD_FLOWCHART.replace('user -->|"本を検索し予約する"| sys', "user --> sys")
        self.assertIn("M3", self.check_block(block))

    def test_empty_label_is_unlabelled(self):
        block = GOOD_FLOWCHART.replace('user -->|"本を検索し予約する"| sys', 'user -->|""| sys')
        self.assertIn("M3", self.check_block(block))

    def test_element_without_type(self):
        block = GOOD_FLOWCHART.replace("<br/>[Software System]<br/>予約と貸出を管理する", "<br/>予約と貸出を管理する")
        self.assertIn("M4", self.check_block(block))

    def test_element_used_without_definition(self):
        block = GOOD_FLOWCHART.replace('sys -->|"予約完了を通知する<br/>[SMTP]"| mail',
                                       'sys -->|"予約完了を通知する<br/>[SMTP]"| mail\n  sys -->|"記録を送る"| audit')
        self.assertIn("M5", self.check_block(block))

    def test_element_budget(self):
        self.assertIn("M6", self.check_block(GOOD_FLOWCHART, max_elements=2))
        self.assertNotIn("M6", self.check_block(GOOD_FLOWCHART, max_elements=3))

    def test_protocol_only_label(self):
        for label in ('"[SQL]"', '"SQL"', '"HTTP/JSON"', '"JSON over HTTPS"', '"ポート 3000"'):
            with self.subTest(label=label):
                block = GOOD_FLOWCHART.replace('|"本を検索し予約する"|', f"|{label}|")
                codes = self.check_block(block)
                self.assertIn("M10", codes)
                self.assertNotIn("M3", codes)

    def test_label_with_words_and_protocol_is_fine(self):
        block = GOOD_FLOWCHART.replace('|"本を検索し予約する"|', '|"予約を保存する<br/>[SQL/TLS]"|')
        self.assertNotIn("M10", self.check_block(block))

    def test_undirected_relationship(self):
        block = GOOD_FLOWCHART.replace('user -->|"本を検索し予約する"| sys', 'user ---|"本を検索し予約する"| sys')
        self.assertIn("M7", self.check_block(block))

    def test_chained_and_grouped_edges(self):
        block = GOOD_FLOWCHART.replace(
            'user -->|"本を検索し予約する"| sys',
            'user & mail -->|"問い合わせる"| sys')
        self.assertEqual(set(), self.check_block(block))

    def test_subgraph_is_a_boundary_not_an_element(self):
        block = GOOD_FLOWCHART.replace(
            '  sys["蔵書予約システム<br/>[Software System]<br/>予約と貸出を管理する"]:::system\n',
            '  subgraph lib["図書館 [Enterprise]"]\n'
            '    sys["蔵書予約システム<br/>[Software System]<br/>予約と貸出を管理する"]:::system\n'
            '  end\n'
            '  style lib fill:none,stroke:#808080,stroke-dasharray:6 4\n')
        codes = self.check_block(block, max_elements=3)
        self.assertEqual(set(), codes)

    def test_frontmatter_is_not_an_edge(self):
        block = GOOD_FLOWCHART.replace("```mermaid\n", "```mermaid\n---\ntitle: コンテキスト\n---\n")
        self.assertEqual(set(), self.check_block(block))

    def test_class_statement_assigns_no_label(self):
        block = GOOD_FLOWCHART + "\n"
        block = block.replace("      classDef person", "      class user person\n      classDef person")
        self.assertEqual(set(), self.check_block(block))

    def test_new_shape_syntax(self):
        block = GOOD_FLOWCHART.replace(
            '  sys["蔵書予約システム<br/>[Software System]<br/>予約と貸出を管理する"]:::system\n',
            '  sys["蔵書予約システム<br/>[Software System]<br/>予約と貸出を管理する"]:::system\n'
            '  db@{ shape: cyl, label: "予約データベース<br/>[Container: PostgreSQL]<br/>予約を保存する" }\n'
            '  sys -->|"予約を保存する<br/>[SQL]"| db\n')
        self.assertEqual(set(), self.check_block(block))

    def test_architecture_beta_is_rejected(self):
        block = textwrap.dedent('''\
            ```mermaid
            architecture-beta
              accTitle: 構成
              accDescr: API とデータベース
              service api(server)[API]
              service db(database)[DB]
              api:R --> L:db
            ```''')
        self.assertIn("M8", self.check_block(block))

    def test_unknown_diagram_type_is_reported(self):
        block = "```mermaid\npie\n  accTitle: x\n  accDescr: y\n  \"a\" : 1\n```"
        self.assertIn("M9", self.check_block(block))


class TestMermaidC4AndSequence(CheckerTestCase):
    def check_block(self, block, **kwargs):
        p = self.write("view.md", page(block))
        return self.codes(p, **kwargs)[0]

    C4 = textwrap.dedent('''\
        ```mermaid
        C4Context
          accTitle: 蔵書予約システムのシステムコンテキスト図
          accDescr: 利用者が蔵書予約システムで本を予約する。
          Person(user, "利用者", "本を探して予約する")
          System(sys, "蔵書予約システム", "予約と貸出を管理する")
          System_Ext(mail, "メール配信サービス", "通知メールを送る")
          Rel(user, sys, "本を検索し予約する")
          Rel(sys, mail, "予約完了を通知する", "SMTP")
        ```''')

    def test_good_c4_block(self):
        self.assertEqual(set(), self.check_block(self.C4))

    def test_c4_relationship_without_label(self):
        block = self.C4.replace('Rel(user, sys, "本を検索し予約する")', 'Rel(user, sys, "")')
        self.assertIn("M3", self.check_block(block))

    def test_c4_protocol_only_label(self):
        block = self.C4.replace('Rel(user, sys, "本を検索し予約する")', 'Rel(user, sys, "HTTPS")')
        self.assertIn("M10", self.check_block(block))

    def test_sequence_protocol_only_message(self):
        block = self.SEQ.replace("user->>api: 予約を送る [HTTPS]", "user->>api: [HTTPS]")
        self.assertIn("M10", self.check_block(block))

    def test_c4_element_budget(self):
        self.assertIn("M6", self.check_block(self.C4, max_elements=2))

    SEQ = textwrap.dedent('''\
        ```mermaid
        sequenceDiagram
          accTitle: 予約の流れ
          accDescr: 利用者が予約し、API がデータベースに保存する。
          autonumber
          actor user as 利用者 [Person]
          participant api as API [Container: Python]
          user->>api: 予約を送る [HTTPS]
          api-->>user: 予約番号を返す
        ```''')

    def test_good_sequence_block(self):
        self.assertEqual(set(), self.check_block(self.SEQ))

    def test_sequence_message_without_text(self):
        block = self.SEQ.replace("api-->>user: 予約番号を返す", "api-->>user:")
        self.assertIn("M3", self.check_block(block))

    def test_sequence_participant_without_type(self):
        block = self.SEQ.replace("participant api as API [Container: Python]", "participant api as API")
        self.assertIn("M4", self.check_block(block))


class TestDrawio(CheckerTestCase):
    def test_good_file(self):
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + LABELLED_EDGE))
        self.assertEqual(set(), self.codes(p)[0])

    def test_compressed_file_is_read(self):
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + LABELLED_EDGE, compressed=True))
        self.assertEqual(set(), self.codes(p)[0])

    def test_malformed_xml(self):
        p = self.write("context.drawio", "<mxfile><diagram>")
        self.assertIn("D1", self.codes(p)[0])

    def test_duplicate_id(self):
        dup = '<mxCell id="a" value="重複 [Person]" vertex="1" parent="1"><mxGeometry as="geometry"/></mxCell>'
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + dup + LABELLED_EDGE))
        self.assertIn("D2", self.codes(p)[0])

    def test_dangling_edge(self):
        edge = LABELLED_EDGE.replace('target="b"', 'target="zzz"')
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + edge))
        self.assertIn("D3", self.codes(p)[0])

    def test_protocol_only_edge(self):
        edge = LABELLED_EDGE.replace('value="予約する"', 'value="HTTPS"')
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + edge))
        self.assertIn("D9", self.codes(p)[0])

    def test_unlabelled_edge(self):
        edge = LABELLED_EDGE.replace('value="予約する"', 'value=""')
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + edge))
        self.assertIn("D4", self.codes(p)[0])

    def test_edge_label_child_counts(self):
        edge = LABELLED_EDGE.replace('value="予約する"', 'value=""')
        label = '<mxCell id="e1-label" value="予約する" style="edgeLabel;" vertex="1" connectable="0" parent="e1"><mxGeometry as="geometry"/></mxCell>'
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + edge + label))
        self.assertEqual(set(), self.codes(p)[0])

    def test_missing_title_and_legend(self):
        p = self.write("context.drawio", drawio_xml(NODES + LABELLED_EDGE))
        codes = self.codes(p)[0]
        self.assertIn("D5", codes)
        self.assertIn("D6", codes)

    def test_vertex_without_text(self):
        blank = '<mxCell id="c" value="" style="rounded=1;" vertex="1" parent="1"><mxGeometry as="geometry"/></mxCell>'
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + blank + LABELLED_EDGE))
        self.assertIn("D7", self.codes(p)[0])

    def test_element_budget(self):
        p = self.write("context.drawio", drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + LABELLED_EDGE))
        self.assertIn("D8", self.codes(p, max_elements=1)[0])

    def test_embedded_svg(self):
        xml = drawio_xml(TITLE_CELL + LEGEND_CELL + NODES + LABELLED_EDGE)
        import html
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" content="{html.escape(xml, quote=True)}"><g/></svg>'
        p = self.write("context.drawio.svg", svg)
        self.assertEqual(set(), self.codes(p)[0])
        p2 = self.write("broken.drawio.svg", svg.replace("予約する", ""))
        self.assertIn("D4", self.codes(p2)[0])


class TestStructurizr(CheckerTestCase):
    def test_good_workspace(self):
        p = self.write("workspace.dsl", GOOD_DSL)
        self.assertEqual(set(), self.codes(p)[0])

    def test_missing_views_block(self):
        text = GOOD_DSL.split("    views {")[0] + "}\n"
        self.assertNotIn("views", text)
        p = self.write("workspace.dsl", text)
        self.assertIn("S1", self.codes(p)[0])

    def test_relationship_described_only_by_protocol(self):
        p = self.write("workspace.dsl", GOOD_DSL.replace('user -> web "本を検索し予約する" "HTTPS"', 'user -> web "HTTPS"'))
        self.assertIn("S6", self.codes(p)[0])

    def test_relationship_without_description(self):
        p = self.write("workspace.dsl", GOOD_DSL.replace('user -> web "本を検索し予約する" "HTTPS"', "user -> web"))
        self.assertIn("S2", self.codes(p)[0])

    def test_element_without_description(self):
        p = self.write("workspace.dsl", GOOD_DSL.replace('person "利用者" "本を探して予約する"', 'person "利用者"'))
        self.assertIn("S3", self.codes(p)[0])

    def test_container_without_technology(self):
        p = self.write("workspace.dsl", GOOD_DSL.replace('"予約を受け付ける" "Python"', '"予約を受け付ける"'))
        self.assertIn("S4", self.codes(p)[0])

    def test_view_without_description(self):
        p = self.write("workspace.dsl", GOOD_DSL.replace('systemContext sys "context" "蔵書予約システムのシステムコンテキスト図"', 'systemContext sys "context"'))
        self.assertIn("S5", self.codes(p)[0])

    def test_view_title_child_counts_as_description(self):
        text = GOOD_DSL.replace('systemContext sys "context" "蔵書予約システムのシステムコンテキスト図" {',
                                'systemContext sys "context" {\n                title "蔵書予約システムのシステムコンテキスト図"')
        p = self.write("workspace.dsl", text)
        self.assertNotIn("S5", self.codes(p)[0])


class TestDiagramSet(CheckerTestCase):
    def test_directory_without_index(self):
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.assertIn("I1", self.codes(self.root / "set")[0])

    def test_view_not_linked_from_index(self):
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.write("set/containers.md", page(GOOD_FLOWCHART))
        self.write("set/README.md", "# 構成図の一覧\n\n- [システムコンテキスト図](context.md)\n")
        codes, findings = self.codes(self.root / "set")
        self.assertIn("I2", codes)
        self.assertTrue(any("containers.md" in f.path for f in findings if f.code == "I2"))

    def test_index_links_every_view(self):
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.write("set/views/containers.md", page(GOOD_FLOWCHART))
        self.write("set/README.md", "# 構成図の一覧\n\n- [システムコンテキスト図](./context.md)\n- [コンテナ図](views/containers.md#top)\n")
        self.assertEqual(set(), self.codes(self.root / "set")[0])

    def test_user_named_entry_file_is_the_index(self):
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.write("set/architecture.md", "# 構成図の一覧\n\n- [システムコンテキスト図](context.md)\n")
        self.assertEqual(set(), self.codes(self.root / "set")[0])

    def test_index_option_names_the_index(self):
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.write("set/overview.md", "# 一覧\n\n- [図](context.md)\n")
        self.write("set/notes.md", "# メモ\n\n[図の補足](context.md)\n")
        self.assertIn("I1", self.codes(self.root / "set")[0])  # two candidates: ambiguous
        codes = self.codes(self.root / "set", index="overview.md")[0]
        self.assertEqual(set(), codes)

    def test_backup_of_the_original_is_skipped_in_a_directory(self):
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.write("set/README.md", "# 一覧\n\n- [図](context.md)\n")
        self.write("set/architecture.original.md", "# 全体構成\n\n```mermaid\ngraph TD\n  A --> B\n```\n")
        self.assertEqual(set(), self.codes(self.root / "set")[0])
        # named explicitly, the backup is still checked
        self.assertIn("M1", self.codes(self.root / "set" / "architecture.original.md")[0])

    def test_same_id_with_different_names(self):
        other = GOOD_FLOWCHART.replace('sys["蔵書予約システム<br/>', 'sys["予約システム<br/>')
        self.write("set/context.md", page(GOOD_FLOWCHART))
        self.write("set/containers.md", page(other))
        self.write("set/README.md", "# 一覧\n\n- [a](context.md)\n- [b](containers.md)\n")
        self.assertIn("X1", self.codes(self.root / "set")[0])


class TestCommandLine(CheckerTestCase):
    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = check_diagrams.main(list(args))
        return status, out.getvalue(), err.getvalue()

    def test_exit_zero_when_only_warnings(self):
        p = self.write("view.md", page(GOOD_FLOWCHART))
        status, out, _ = self.run_main(str(p), "--max-elements", "1")
        self.assertEqual(0, status)
        self.assertIn("W M6", out)

    def test_exit_one_on_error(self):
        p = self.write("view.md", page(GOOD_FLOWCHART, legend=None))
        status, out, _ = self.run_main(str(p))
        self.assertEqual(1, status)
        self.assertIn("E P3", out)

    def test_exit_two_on_missing_path(self):
        status, _, err = self.run_main(str(self.root / "nope.md"))
        self.assertEqual(2, status)
        self.assertTrue(err)

    def test_bundled_example_passes_cleanly(self):
        status, out, _ = self.run_main(str(EXAMPLE))
        self.assertEqual(0, status, out)
        self.assertEqual("", out.strip().replace("ok", ""), out)


class TestBundledMaterial(CheckerTestCase):
    """What the skill tells the model to copy must itself pass the checker."""

    def test_templates_pass(self):
        templates = SKILL_DIR / "assets" / "templates"
        for name in ("view-page.md", "view.drawio", "workspace.dsl"):
            with self.subTest(template=name):
                findings = check_diagrams.check_paths([str(templates / name)])
                self.assertEqual([], findings)

    def test_reference_mermaid_examples_pass(self):
        text = (SKILL_DIR / "references" / "mermaid.md").read_text(encoding="utf-8")
        blocks = [body for _, info, body in check_diagrams.parse_markdown(text)[0] if info == "mermaid"]
        self.assertGreaterEqual(len(blocks), 4)
        for n, body in enumerate(blocks):
            with self.subTest(block=n):
                p = self.write(f"example-{n}.md", page("```mermaid\n" + "\n".join(body) + "\n```"))
                findings = check_diagrams.check_paths([str(p)])
                self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
