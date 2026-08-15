# Quickstart: Scrum Guide 作成物・イベント テンプレート の検証

実装完了後、以下のコマンドで spec.md の成功基準（SC-001〜SC-005）と、リポジトリ横断の整合性を検証する。

## 前提条件

- リポジトリルートで実行する。
- `.claude/skills/scrum-master/references/templates/` が作成済みであること。

## SC-001: 7つのテンプレートファイルが存在する

```bash
ls .claude/skills/scrum-master/references/templates/*.md | wc -l
# 期待値: 7

for f in product-backlog sprint-backlog increment sprint-planning daily-scrum sprint-review sprint-retrospective; do
  test -f ".claude/skills/scrum-master/references/templates/${f}.md" && echo "OK: ${f}.md" || echo "MISSING: ${f}.md"
done
```

## SC-002: 開いてすぐ埋め始められる（手動確認）

自動化しない（見出し・記入欄の分かりやすさは主観的な品質基準のため）。実装者は各テンプレートを開き、追加の説明を読まずに「どこに何を書けばよいか」が分かるかを目視確認する。

## SC-003: 022番featureで削除した語彙が含まれない

```bash
grep -rniE 'スケーリング|フロー指標|アンチパターン|コーチングスタンス|Nexus|LeSS|SAFe|Scrum@Scale|Kanban|DORA|EBM|flow_metrics' \
  .claude/skills/scrum-master/references/templates/
# 期待値: 一致なし（終了コード1）
```

## SC-004: SKILL.mdから新規テンプレートへの導線が1回以内

```bash
grep -n 'templates/' .claude/skills/scrum-master/SKILL.md
# 期待値: 「参照ファイル」表に templates/ ディレクトリへのリンクが1行以上ある
```

## SC-005: 各テンプレートに[SG20, p.X]形式の出典がある

```bash
for f in .claude/skills/scrum-master/references/templates/*.md; do
  grep -q '\[SG20, p\.' "$f" && echo "OK: $f" || echo "MISSING CITATION: $f"
done
```

## デッドリンクの確認（FR-009相当、022番featureのパターンを踏襲）

```bash
grep -rnoE '\]\(\.\./[a-zA-Z0-9_.-]+\.md[^)]*\)|\]\([a-zA-Z0-9_.-]+\.md[^)]*\)' \
  .claude/skills/scrum-master/references/templates/ .claude/skills/scrum-master/SKILL.md \
  | sed -E 's/^([^:]+):.*\((\.\.\/)?([a-zA-Z0-9_.-]+\.md).*/\1 \3/' \
  | while read -r src target; do
      dir=$(dirname "$src")
      test -f "$dir/$target" -o -f "$(dirname "$dir")/$target" || echo "DEAD LINK in $src -> $target"
    done
```

## リポジトリ横断の整合性チェック

```bash
./scripts/check-mcp-consistency.sh
bash tests/run-codex-references.sh
bash tests/run-codex-drift.sh
bash tests/run-skill-routing.sh   # tests/skill-routing/007-scrum-facilitation.md を含む全件が通ること
```

## JSON妥当性（本featureでは`.claude/settings.json`を変更しないため、参考として記載しない）

該当なし — 022番featureとは異なり、本featureは`.claude/settings.json`を変更しない。
