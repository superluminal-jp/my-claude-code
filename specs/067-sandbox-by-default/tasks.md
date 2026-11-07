---
description: "Task list for 067: OS サンドボックスを既定で有効にし、日常作業に要る出口だけを最小限に開ける"
---

# Tasks: OS サンドボックスを既定で有効にし、日常作業に要る出口だけを最小限に開ける

背景と決めた事項 D1〜D10 は同じディレクトリの `spec.md`、実現の手段は `plan.md` にある。作業は、`main`(コミット 95668e3)から作ったブランチ `feat/sandbox-by-default` のワークツリー `.claude/worktrees/sandbox-by-default` で行った。push の前に、spec 066 をマージした `origin/main`(コミット 4b4d03e)に載せ直した。

## Red — 失敗するテストを先に書く

- [X] T001 [US1] [US2] [US3] [US6] `tests/run-sandbox-settings.sh` を作り、`.claude/settings.json` の不変条件(FR-001〜FR-006、FR-011、FR-014)を検査する。結果: 変更の前は HOOK-00 などが失敗した(61件のうち40件)
- [X] T002 [US2] [US3] [US4] [US5] 同じファイルに、SessionStart の3つのフックを `statusMessage` で取り出し、環境変数とスタブを与えて sh・bash・zsh で実行する検査(FR-008〜FR-010)を加える。結果: 変更の前は失敗した
- [X] T003 [P] [US2] `tests/assert_deck_units.py` に `chromium_args` の検査(UNIT-09〜11)を加える。結果: 変更の前は UNIT-09〜11 と、サンドボックスの中で Chromium を実際に起動する UNIT-08 が失敗した(`TargetClosedError`)
- [X] T004 [P] [US6] `tests/run-install.sh` に、マージの後も利用者のほかのプラグインのキーとサンドボックスの中の利用者のキーが残り、`github@claude-plugins-official` が `false` に、`sandbox` がリポジトリの値になる検査を加える(FR-012)。結果: 変更の前は失敗した。あわせて既存の `diff <(...)` の比較を文字列の比較に替えた(サンドボックスの中では `/usr/bin/diff` が `/dev/fd` を開けない)

## Green — 最小の変更で通す

- [X] T005 [US1] [US2] [US3] [US6] `.claude/settings.json` に `sandbox` と、MCP を止めるキーを加える
- [X] T006 [US2] [US3] [US4] [US5] `.claude/settings.json` の `hooks.SessionStart` に3つのフックを加える
- [X] T007 [US2] `deck.py` に `chromium_args` を加えて起動に使い、`references/deck-checks.md` に macOS のサンドボックスの原因を書く。結果: `tests/assert_deck_units.py` の11件が、サンドボックスの中で通った

## 文書

- [X] T008 `README.md` と `README.ja.md`(設定の説明、マージの注記、サンドボックスとフック、MCP、検証の手順、CI の本数)、`docs/mcp-servers.md`(棚卸しと止めたもの)、`docs/claude-config-design.md`(強制の手段と、フックで足す文脈)を書く
- [X] T009 [P] `docs/adr/0020-enable-sandbox-by-default.md` と `docs/adr/0021-block-mcp-servers-by-settings.md` を書く

## 検証

- [X] T010 `.github/workflows/ci.yml` に `tests/run-sandbox-settings.sh` を加え、`tests/run-*.sh` をすべて実行する。結果(2026-11-08、ワークツリーの設定のサンドボックスの中): run-sandbox-settings 61件、run-install、run-removed-guardrails 4件、run-readme-skill-index 33件、run-package-safety-bundle 21件、run-digital-agency-frontend-skill 74件、run-digital-agency-slides-skill 126件(E2E の1件は DADS の資産を取得できず skip)、run-requirements-decomposition-skill 5件、run-verified-delivery-skill 5件、run-note-write-guard 14件がすべて通った。run-config-pyramid(8件)と run-secure-logging-skill(PL-04)は、テンプレートを渡さない `mktemp -d` がサンドボックスの中で失敗して落ちた。サンドボックスの外では 60件と 40件がすべて通った。run-mcp-startup は uv のキャッシュ(`~/.cache/uv`)への書き込みが拒まれて落ちた。`.mcp.json` を変えていないので、外では再実行していない。要件の分解の判定(`check_graph.py --gate`)は ready(反証のレビューを記録済み)。載せ直した後は、spec 066 の `run-harness-eval.sh` が新しい設定のキー5つを未分類として落としたので、`docs/harness/capability-map.json` に分類と理由を加え(いずれも評価に含めない)、`docs/harness-eval.md` §4 に8点目の違い(SessionStart の注意が評価に届かない)を加えた。結果: run-harness-eval は 162件の単体テストと対応表の検査が通り、run-sandbox-settings 61件、run-install、run-removed-guardrails 4件、run-readme-skill-index 33件も通った
- [ ] T011 利用者の承認を得て、`install.sh` を実行し、`github` プラグインをアンインストールする。新しいセッションで SC-002〜SC-004 を確かめる(サンドボックスの中で Chromium を `--single-process` で起動する、Bedrock モードなら Bash の `AWS_PROFILE` が未設定であること、`aws … --profile X` が外で動くこと、止めた MCP のツールが無いこと)。SC-005 は GPG の鍵を持つマシンで確かめる
