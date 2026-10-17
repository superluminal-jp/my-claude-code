# Quickstart: 未処分の兄弟 README の検出(S1)

実装後に、端から端までの動作を確認する手順。作業は一時ディレクトリで行い、このリポジトリを書き換えない。

## 前提

- Python 3.9 以上、Git
- スキルのパス: `SKILL=.claude/skills/maintaining-living-documentation`

## 1. 単体テスト

```bash
python3 -B -m unittest discover -s .claude/skills/maintaining-living-documentation/tests -v
```

期待: 既存の 67 件と、追加した FindRelatedTests、StopGateTests、SkillDefinitionTests がすべて通る。

## 2. 候補の一覧(手動確認)

```bash
tmp=$(mktemp -d) && cd "$tmp"
git init -q && git config user.email t@example.invalid && git config user.name t
mkdir src && echo 'print(1)' > src/x.py && echo '# src' > src/README.md
git add -A && git commit -qm init
echo 'print(2)' > src/x.py
python3 "$OLDPWD/.claude/skills/maintaining-living-documentation/scripts/find_related.py" --root . --json
```

期待: `changed` が `["src/x.py"]`、`candidates` に `src/README.md`(`kind` が `sibling`、`proximity` が `P1`)。終了コード 0。

## 3. ゲートの動作(単体テストが自動化している)

- `src/README.md` を触らず言及もしない最終メッセージ → `block`(理由に `src/README.md`)
- README を更新、または最終メッセージにパスを書く → 通る
- `LIVING_DOCS_GATE=warn` → 警告のみ、`off` → 何もしない

## 4. 手順書

`SKILL.md` の手順 3 に `find_related.py` のコマンドと、処分の最小限の約束が載っていること。`SKILL.md` が 500 行未満であること。

## 5. リンク検査

```bash
python3 .claude/skills/maintaining-living-documentation/scripts/check_links.py --root . --changed
```

期待: エラー 0。
