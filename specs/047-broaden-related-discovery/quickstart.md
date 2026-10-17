# Quickstart: 近接候補の発見を広げる(S2)

## 1. 単体テスト

```bash
python3 -B -m unittest discover -s .claude/skills/maintaining-living-documentation/tests -v
```

期待: 既存の 112 件と追加分がすべて通る。

## 2. 名前参照の手動確認

```bash
tmp=$(mktemp -d) && cd "$tmp"
git init -q && git config user.email t@example.invalid && git config user.name t
mkdir scripts docs && echo 'echo hi' > scripts/install.sh && echo 'Run scripts/install.sh first.' > docs/setup.md
git add -A && git commit -qm init && echo 'echo hi2' > scripts/install.sh
python3 "$OLDPWD/.claude/skills/maintaining-living-documentation/scripts/find_related.py" --root . --json
```

期待: `docs/setup.md` が `mention`・`P2`。`scripts/install.sh` 自身が `comment`・`P0`(助言)。

## 3. リンク検査

```bash
python3 .claude/skills/maintaining-living-documentation/scripts/check_links.py --root . --changed
```

期待: エラー 0。
